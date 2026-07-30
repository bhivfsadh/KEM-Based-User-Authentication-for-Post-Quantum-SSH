# Malformed-Ciphertext Robustness and Timing Sanity Checks

The protocol-level security of KEMUAuth is established by the security analysis in the paper. Since this model does not capture implementation leakage, we also perform basic checks on the reference implementation when it processes attacker-chosen KEM ciphertexts. These checks are intended to detect obvious input-handling failures, crashes, inconsistent protocol behavior, and coarse timing differences that could provide an initial indication of implementation-level weaknesses. They do not establish constant-time execution or resistance to cache, power, electromagnetic, or fault-injection attacks. Production deployments therefore require additional assurance through formal implementation analysis, constant-time verification, independent code review, dynamic leakage testing, and platform-specific fault testing so that the implementation remains consistent with the analyzed design.

## Running the Tests

### One-Click Reproduction

```bash
# Build KEMSSH first (if not already built):
#   bash oqs-scripts/clone_liboqs.sh
#   bash oqs-scripts/build_liboqs.sh
#   bash oqs-scripts/build_openssh.sh

# Full reproduction (builds mutation sshd + runs both tables):
sudo bash testScripts/supp_ciphertext_robustness/run

# Protocol only (builds mutation sshd + runs Table 1):
sudo bash testScripts/supp_ciphertext_robustness/run --mode protocol

# Local decaps only (Table 2, no sudo needed):
bash testScripts/supp_ciphertext_robustness/run --mode local

# Quick smoke test (5 samples per class):
sudo bash testScripts/supp_ciphertext_robustness/run --same-len-tests 5 --diff-len-tests 5
```

### Custom Parameters

```bash
sudo bash testScripts/supp_ciphertext_robustness/run \
  --same-len-tests 100 \
  --diff-len-tests 50 \
  --decaps-warmup 5000 \
  --decaps-iterations 20000
```

### Manual Build (for debugging)

**Table 1 — Protocol-level test** (requires mutation-enabled sshd):

```bash
# Build mutation-enabled sshd:
bash testScripts/supp_ciphertext_robustness/run --mode build

# Then run protocol test:
sudo bash testScripts/supp_ciphertext_robustness/run --mode protocol

# Restore original sshd after testing:
git checkout -- auth2-kem.c
make clean && make -j4 sshd sshd-session sshd-auth ssh
```
```

**Table 2 — Local decapsulation microbenchmark** (no root required):

```bash
bash testScripts/supp_ciphertext_robustness/run --mode local

# Custom warmup/iterations:
bash testScripts/supp_ciphertext_robustness/run --mode local \
  --decaps-warmup 5000 --decaps-iterations 20000
```

### Tested Ciphertext Classes

| Class | Length | Construction |
|:---|:---|:---|
| `valid` | 1088 B | Normal ML-KEM-768 Encaps output |
| `onebit` | 1088 B | Flip 1 random bit in valid ciphertext |
| `multibit` | 1088 B | Flip ~1% of bits in valid ciphertext |
| `random` | 1088 B | Uniform random bytes |
| `allzero` | 1088 B | All bytes zeroed |
| `allff` | 1088 B | All bytes set to `0xff` |
| `truncated` | < 1088 B | Valid ciphertext truncated by 1 byte |
| `extended` | > 1088 B | Valid ciphertext extended by 1 byte |

## Results

The following results were obtained on an Ubuntu 24.04 VM (16 vCPU, Linux 6.8) with ML-KEM-768 running over the loopback interface. The implementation is based on liboqs and the KEMSSH reference implementation.

### Protocol-Level Malformed-Ciphertext Test

We tested a valid ML-KEM-768 ciphertext together with several malformed ciphertext classes. Each class was tested 50 times. The reported latency covers the interval from sending the challenge ciphertext to receiving the client's KEM response.

| Ciphertext class | Trials | Authentication outcome | Median latency (ms) | 95th percentile (ms) | Crashes |
|---|---:|---|---:|---:|---:|
| Valid | 50 | Success | 5.2 | 5.3 | 0 |
| One-bit flip | 50 | Rejected | 5.2 | 5.3 | 0 |
| Multi-bit flip | 50 | Rejected | 5.2 | 5.3 | 0 |
| Random | 50 | Rejected | 5.2 | 5.3 | 0 |
| All-zero | 50 | Rejected | 5.2 | 5.3 | 0 |
| All-`ff` | 50 | Rejected | 5.2 | 5.3 | 0 |
| Truncated | 50 | Rejected | 5.2 | 5.3 | 0 |
| Extended | 50 | Rejected | 5.2 | 5.3 | 0 |

All tested inputs followed the same protocol response path and produced a `KEM_RESPONSE`. Valid ciphertexts completed authentication, while malformed ciphertexts were ultimately rejected. We observed no crashes, and the median challenge-to-response latency varied by at most 0.04 ms across the tested classes.

### Local Decapsulation Timing Test

We separately benchmarked ML-KEM-768 decapsulation for fixed-length ciphertexts. The benchmark uses a ciphertext length of 1088 bytes and a shared-secret length of 32 bytes. It performs 100 warm-up operations followed by 500 measurements per ciphertext class, pins execution to one CPU core, and records time with `CLOCK_MONOTONIC_RAW`. Truncated and extended inputs are excluded because the local decapsulation interface accepts fixed-length ciphertext buffers.

| Ciphertext class | Samples | Median (ns) | 5th–95th percentile (ns) | Median difference |
|---|---:|---:|---:|---:|
| Valid | 500 | 8697 | 8551–9789 | — |
| One-bit flip | 500 | 8660 | 8552–9770 | −0.43% |
| Multi-bit flip | 500 | 8690 | 8550–9603 | −0.08% |
| Random | 500 | 8670 | 8554–9970 | −0.31% |
| All-zero | 500 | 8676 | 8551–9765 | −0.24% |
| All-`ff` | 500 | 8668 | 8556–9904 | −0.33% |

The median differences remain below 0.5%, and the measured percentile ranges overlap substantially. We therefore observed no coarse timing separation among these ciphertext classes in the tested environment. This result is only a timing sanity check and should not be interpreted as a constant-time or comprehensive side-channel evaluation.

## Output Files

| File | Description |
|:---|:---|
| `protocol_raw.csv` | Per-connection raw timing and results |
| `protocol_summary.csv` | Aggregated per-class statistics |
| `protocol_report.md` | Markdown report (Table 1) |
| `local_decaps_output.txt` | Local decapsulation microbenchmark output (Table 2) |

## Notes on Reproducibility

- The protocol-level test requires a mutation-enabled sshd, which is built automatically by `run --mode all`. The patch modifies `auth2-kem.c` to add a ciphertext mutation hook under `#ifdef KEM_TEST_MUTATION`.
- The local decapsulation benchmark requires liboqs. If liboqs is not found via `pkg-config`, set `LIBOQS_DIR` to the installation prefix.
- Timing measurements are environment-dependent. Absolute latencies will differ across platforms; the key signal is the absence of coarse timing separation between ciphertext classes.
- The protocol-level test starts a fresh sshd per connection to reset KEM state. This is intentional for correctness but increases total runtime.

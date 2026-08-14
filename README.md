# KEMUAuth: KEM-Based-User-Authentication-for-Post-Quantum-SSH (Anonymous Research Artifact)

This repository is an research artifact for evaluating KEM-based user authentication in SSH based on OQS-openSSHv10.

## Anonymous Statement

This artifact is prepared for anonymous review. Repository-specific personal identifiers are intentionally minimized in the project-owned scripts and documentation.

## Scope

This repository uses a full-source distribution approach so reviewers can build and run experiments directly.

Core contribution focus:
- KEM user-authentication workflow integration in the SSH stack.
- Reproducible experiment wrappers under [testScripts](testScripts) for paper-aligned evaluations.
- Controlled network emulation for RTT and TCP initcwnd experiments.

Non-core items are intentionally not expanded into separate benchmark suites if they are not central to the KEM user-authentication claim.

## Repository Layout

- Build helpers:
  - [oqs-scripts/clone_liboqs.sh](oqs-scripts/clone_liboqs.sh)
  - [oqs-scripts/build_liboqs.sh](oqs-scripts/build_liboqs.sh)
  - [oqs-scripts/build_openssh.sh](oqs-scripts/build_openssh.sh)
- Reviewer-facing experiments:
  - [testScripts/run_all](testScripts/run_all)
  - [testScripts/test1/test1](testScripts/test1/test1)
  - [testScripts/fig3_rerun/run](testScripts/fig3_rerun/run) — unified Figure-3 dataset (13 algorithms)
  - [testScripts/test2/test2](testScripts/test2/test2)
  - [testScripts/test3/test3](testScripts/test3/test3)
  - Backend runners in [testScripts/backends](testScripts/backends)
- Supplementary experiments (revision):
  - [testScripts/supp_concurrency/run](testScripts/supp_concurrency/run) — Server concurrency: throughput + pending memory
  - [testScripts/supp_ciphertext_robustness/run](testScripts/supp_ciphertext_robustness/run) — Ciphertext robustness
  - [testScripts/supp_rtt_loss/run](testScripts/supp_rtt_loss/run) — RTT dense scan + packet loss
  - Pre-computed results in each `reference_data.md`
- Experiment notes:
  - [testScripts/plan.md](testScripts/plan.md)

## Build


Recommended environment: Linux with sudo privileges for network shaping.

### Versions

- OpenSSH: 10.2p1 (OQS-OpenSSH 2025-12 fork)
- liboqs: 0.15.0 (AVX2-optimized ML-KEM, ML-DSA, SLH-DSA/FN-DSA, Falcon)
- OpenSSL: 3.0.2
- Build flow: `oqs-scripts/clone_liboqs.sh` → `oqs-scripts/build_liboqs.sh` → `oqs-scripts/build_openssh.sh`

### Quick Build (Recommended)

1. Build liboqs:
  ```bash
  bash oqs-scripts/clone_liboqs.sh
  bash oqs-scripts/build_liboqs.sh
  ```

2. Build OQS-OpenSSH:
  ```bash
  bash oqs-scripts/build_openssh.sh
  ```

After building, the ssh, sshd, ssh-keygen and related binaries will appear in the repository root or in the oqs-test/tmp directory.

---

### Manual Build (for custom configuration or debugging)

If you need to customize build parameters or wish to debug the build process manually, follow these steps:

1. Install dependencies (example for Ubuntu/Debian):
  ```bash
  sudo apt-get update
  sudo apt-get install -y autoconf automake libtool make gcc g++ pkg-config libssl-dev zlib1g-dev
  ```

2. In the repository root, generate the configure script (if not already present):
  ```bash
  autoreconf -i
  ```

3. Configure build parameters (adjust --prefix, --with-liboqs-dir, etc. as needed):
  ```bash
  ./configure --prefix="$PWD/oqs-test/tmp" --with-liboqs-dir="$PWD/oqs" --with-ssl-dir=/usr --with-cflags="-I$PWD/oqs-test/tmp/include"
  ```

4. Build and install:
  ```bash
  make -j
  make install
  ```

5. The resulting ssh/sshd/ssh-keygen binaries will be located in `$PWD/oqs-test/tmp`.

For more configure options, run `./configure --help`.

You may also refer to the `oqs-scripts/build_openssh.sh` script for an automated version of these steps.

## Experiments

> **Note:** All tests and pre-computed results in this repository are provided for reference and
> comparative evaluation only. Absolute latency, throughput, and resource figures depend on host
> hardware, kernel version, system load, and network conditions. They are not intended as
> strict performance guarantees across platforms.

Run all experiments in one command:

```bash
bash testScripts/run_all
```

### Test 1 (Figure-3 style, unified 13-algorithm dataset)

The unified Figure-3 dataset compares 13 client-authentication algorithms in one
campaign (RTT=67ms, initcwnd=10 MSS, server host-key Ed25519): Ed25519,
ML-DSA-44/65/87, Falcon-512/1024, SLH-DSA-SHA2-128f/192f/256f, ML-KEM-512/768/1024,
and Password (yescrypt). It replaces the earlier separate test1 (10 algorithms),
supp_falcon, and supp_password tables. Requires root (test account, tc, ip route,
initcwnd/offload setup).

```bash
sudo bash testScripts/fig3_rerun/run
```

Defaults:
- iterations=2000
- warmup=5
- RTT=67ms
- initcwnd=10

Quick smoke / overrides:

```bash
sudo env ITERATIONS=5 WARMUP=1 bash testScripts/fig3_rerun/run
```

Pre-computed results: [testScripts/test1/reference_data.md](testScripts/test1/reference_data.md)

A lightweight 10-algorithm variant (no Falcon/Password) remains at
`testScripts/test1/test1` for fast checks:

```bash
bash testScripts/test1/test1
```

### Test 2 (Figure-4 style, close/intermediate/long RTT)

```bash
bash testScripts/test2/test2
```

Defaults:
- rounds=1
- iterations=50
- warmup=5
- initcwnd=10
- profiles: all (close/intermediate/long)

Optional overrides:

```bash
bash testScripts/test2/test2 --profile intermediate --iterations 100 --rounds 2 --warmup 10
```

Supported profiles:
- all
- close
- intermediate
- long

### Test 3 (Figure-5 style, 11 initcwnd points)

```bash
bash testScripts/test3/test3
```

Defaults:
- rounds=1
- iterations=50
- warmup=5
- RTT=67ms
- initcwnd list: 3 5 7 10 15 20 25 30 35 40 50

Optional overrides:

```bash
bash testScripts/test3/test3 --iterations 100 --rounds 2 --warmup 10 --rtt 67 --initcwnd-list "3 5 7 10 15 20 25 30 35 40 50"
```

### Supplementary Experiments: Prerequisites

Some supplementary experiments require special build flags and system setup:

**Build with instrumentation flags:**

```bash
# For ciphertext robustness (Exp 3):
grep KEM_TEST_MUTATION config.h || echo '#define KEM_TEST_MUTATION 1' >> config.h
make -j4 ssh sshd sshd-session sshd-auth ssh-keygen

# For server concurrency (Exps 1 & 2):
grep KEM_TEST_INSTRUMENTATION config.h || echo '#define KEM_TEST_INSTRUMENTATION 1' >> config.h
make -j4 ssh sshd sshd-session sshd-auth ssh-keygen
```

> Building without these flags produces normal OpenSSH binaries; the flags only activate
> measurement hooks used by the experiments below.

**cgroup v2 (required by server concurrency experiments):**

```bash
# Check if cgroup v2 is available:
test -f /sys/fs/cgroup/cgroup.controllers && echo "cgroup v2 OK" || echo "cgroup v2 NOT available"
# If not, add "systemd.unified_cgroup_hierarchy=1" to kernel cmdline and reboot.
```

**Network interface (required by RTT/loss experiments):**

The RTT and loss experiments apply `tc netem` rules to the loopback interface (`lo`).
`ethtool` offload disable is attempted but non-fatal; if `lo` does not support `ethtool`,
the experiments still run correctly.

**KEM identities (required by all supplementary experiments):**

```bash
bash test/step1/gen_kem_identity_mlkem768.sh
```

**Runtime estimates (2-core VM, 67 ms RTT where applicable):**

| Experiment | Approx. Runtime |
|:---|:---|
| Test 1 (unified 13-alg, iterations=2000) | ~6.3 h |
| Test 2 (all 3 profiles) | ~15 min |
| Test 3 (11 initcwnd points) | ~10 min |
| Throughput cgroup | ~30 min |
| Pending memory | ~20 min |
| Ciphertext robustness | ~5 min |
| RTT dense scan | ~40 min |
| Packet loss | ~25 min |

---

### Supplementary: Server Concurrency (Revision)

Two experiments that measure server-side behaviour under controlled concurrency:
(1) full-SSH throughput at N = 1,8,16,32,64 concurrent clients with cgroup CPU/memory
accounting, and (2) per-connection memory cost of pending KEM challenges as a function of
concurrency P.

Requires `KEM_TEST_INSTRUMENTATION` build flag and cgroup v2 (see prerequisites above).

```bash
sudo bash testScripts/supp_concurrency/run
```

| Sub-experiment | Description | Pre-computed Results |
|:---|:---|:---|
| `throughput_cgroup/` | Full-SSH throughput with cgroup v2 CPU/memory isolation | [reference_data.md](testScripts/supp_concurrency/throughput_cgroup/reference_data.md) |
| `pending_memory/` | Pending KEM challenge memory growth: $M(P)=\alpha+\beta P$ | [reference_data.md](testScripts/supp_concurrency/pending_memory/reference_data.md) |

Run individually:
```bash
sudo bash testScripts/supp_concurrency/run --mode throughput
sudo bash testScripts/supp_concurrency/run --mode pending
```

### Supplementary: Ciphertext Robustness (Revision)

Malformed-ciphertext robustness and timing sanity checks for ML-KEM-768 KEM user
authentication. Two test modes:

- **Protocol-level** (`--mode protocol`): Sends mutated ciphertexts through a live
  SSH connection and records whether the server rejects them with consistent error
  codes (no distinguishable timing leak). Requires `sudo`.
- **Local decaps** (`--mode local`): Micro-benchmark that calls the ML-KEM-768
  decapsulation API directly with valid and mutated ciphertexts; measures whether
  decapsulation time differs between valid and invalid inputs. Runs without `sudo`.

Requires `KEM_TEST_MUTATION` build flag (see prerequisites above).

```bash
sudo bash testScripts/supp_ciphertext_robustness/run
```

| Table | Mode | Command |
|:---|:---|:---|
| Table 1 — Protocol-level | `--mode protocol` | `sudo bash testScripts/supp_ciphertext_robustness/run --mode protocol` |
| Table 2 — Local decaps | `--mode local` | `bash testScripts/supp_ciphertext_robustness/run --mode local` |

Pre-computed results: [reference_data.md](testScripts/supp_ciphertext_robustness/reference_data.md)

### Supplementary: RTT & Packet Loss (Revision)

Two experiments extending the latency evaluation: (1) a dense RTT scan across
9 points (0, 20, 40, 60, 80, 100, 120, 160, 200 ms) to verify smooth latency
trends, and (2) random packet-loss sensitivity at 5 loss levels (0, 0.1, 0.5,
1.0, 2.0%) with fixed 67 ms RTT. Both compare KEMUAuth (ML-KEM-768) vs ML-DSA-65.

Applies `tc netem` on `lo`; requires `sudo` and `ip`/`tc`/`ping` installed.

```bash
sudo bash testScripts/supp_rtt_loss/run
```

| Sub-experiment | Description | Pre-computed Results |
|:---|:---|:---|
| `rtt_scan/` | 9 RTT points, 500 iterations each | [reference_data.md](testScripts/supp_rtt_loss/rtt_scan/reference_data.md) |
| `loss/` | Random loss at 67 ms, 5 seeds × 200 iterations | [reference_data.md](testScripts/supp_rtt_loss/loss/reference_data.md) |

Run individually:
```bash
sudo bash testScripts/supp_rtt_loss/run --mode rtt
sudo bash testScripts/supp_rtt_loss/run --mode loss
```

## Outputs

Each test generates a reviewer-facing output set:
- raw_runs.csv
- round_means_append.csv
- summary.csv
- readable.md

See [testScripts/plan.md](testScripts/plan.md) for mapping.

## Notes on Reproducibility

- Network shaping depends on host load and scheduler behavior; small jitter is expected.
- Results are for reproducibility and comparative evaluation, not a strict absolute-latency guarantee across all platforms.
- If you publish results, align the environment with the paper setup for closest correspondence.

## License

This repository includes upstream OpenSSH/OQS components and follows their corresponding licenses.

Primary license references in this repository:
- [LICENCE](LICENCE)

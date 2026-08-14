# fig3_rerun — Unified Figure 3 rerun (13 algorithms, interleaved polling)

Standalone experiment script that does **not** modify the existing
`testScripts/test1/` implementation (`test1` / `supp_falcon` / `supp_password`).
Merge back into `testScripts/test1/` only after this has been validated.

## Goal

Rerun the paper Figure 3 experiment (end-to-end SSH handshake latency while
varying only the client-authentication algorithm) on the same machine and
software environment, combining the original `test1` (10 algorithms) +
`supp_falcon` (falcon512/1024) + `supp_password` (password) into a single
campaign, to fill in Falcon and Password results while preventing
environment drift.

## Settings (aligned with `plan/newTest/0814.md`)

- KEX: `mlkem768x25519-sha256`
- Server authentication: Ed25519
- RTT: ~ 67 ms (netem half-RTT on lo)
- TCP initial window: 10 MSS (loopback local route initcwnd)
- Measured range: from TCP SYN to successful user authentication
- Metrics: Mean / Median(P50) / P95
- ~200 samples per configuration by default (overridable)

## Algorithms (13)

| Auth mode | Algorithms |
|:---|:---|
| publickey | `ed25519` `md44` `md65` `md87` `falcon512` `falcon1024` `sd128f` `sd192f` `sd256f` |
| publickey-kem | `mk512` `mk768` `mk1024` |
| password (yescrypt) | `password` |

## Interleaved polling (drift amortization)

Each round `shuf`-fles the full algorithm list and runs each algorithm once
(test5 interleaved-polling style), so slow drift (temperature, CPU frequency,
background load) is evenly amortized across all algorithms.

## Usage

```bash
# Quick validation (small sample)
sudo env ITERATIONS=5 WARMUP=1 bash testScripts/fig3_rerun/run

# Full run (200 samples per algorithm, ~35-40 min)
sudo bash testScripts/fig3_rerun/run

# Custom
sudo env ITERATIONS=200 WARMUP=5 RTT_MS=67 INITCWND_MSS=10 bash testScripts/fig3_rerun/run
```

## Pre-computed Results

Unified 13-algorithm table: [test1/reference_data.md](../test1/reference_data.md)

## Output

- `results/raw_runs.csv` — per-connection samples (alg,round,phase,iter,latency_ms,success,retcode,auth_mode)
- `results/summary.csv` — Mean / P50 / P95 / failure rate per algorithm
- `results/readable.md` — readable table (0814.md format)
- `results/metadata.txt` — environment metadata

## Notes

- Requires root (test account creation, tc, ip route initcwnd, ethtool)
- Test account defaults to `ssh_fig3_test` (shared by password and pubkey/KEM), password `testpwd_12345`
- Restores initcwnd route, netem, lo offload and MTU on exit
- sshd cleanup uses a precise `$WORK_DIR/sshd.conf` match and never kills the system sshd

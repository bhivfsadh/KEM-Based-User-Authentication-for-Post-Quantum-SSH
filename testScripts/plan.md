# testScripts/plan.md

This directory contains the reviewer-facing experiment wrappers.

## One-click Entry
- Entry script: testScripts/run_all
- Usage: bash testScripts/run_all
- Behavior: runs test1, test2, and test3 in sequence with default reviewer settings.
- Default sampling: iterations=50, warmup=5 (rounds default to 1).
- Optional override: each test script supports CLI options for rounds/iterations/warmup and selected network parameters.

## Test Groups

### test1
- Goal: Figure-3 dataset generation (authentication algorithm comparison)
- Unified 13-algorithm runner: `testScripts/fig3_rerun/run`
  (Ed25519, ML-DSA-44/65/87, Falcon-512/1024, SLH-DSA-SHA2-128f/192f/256f,
  ML-KEM-512/768/1024, Password--yescrypt; interleaved polling)
- Lightweight variant (10 signature/KEM algorithms, no Falcon/Password):
  `testScripts/test1/test1`
- Outputs (unified run, in `testScripts/fig3_rerun/results/`):
  raw_runs.csv, summary.csv, readable.md, metadata.txt
- Pre-computed results: `testScripts/test1/reference_data.md` (unified table)

### test2-C / test2-I / test2-L
- Goal: Figure-4 dataset generation at close/intermediate/long latency
- Script: testScripts/test2/test2
- Outputs (per level): raw_runs.csv, round_means_append.csv, summary.csv, readable.md

### test3
- Goal: Figure-5 dataset generation (initcwnd scan)
- Script: testScripts/test3/test3
- Outputs: raw_runs.csv, round_means_append.csv, summary.csv, readable.md

## Supplementary Experiments

### supp_ciphertext_robustness
- Goal: Malformed-ciphertext robustness and timing sanity checks
- Script: testScripts/supp_ciphertext_robustness/run
- Two tables: (1) protocol-level observable behavior, (2) local decapsulation micro-benchmark
- Requires `KEM_TEST_MUTATION` build flag

### supp_concurrency
- Goal: Server-side concurrency stress tests
- Script: testScripts/supp_concurrency/run
- Sub-experiments:
  - `throughput_cgroup/`: Full-SSH throughput with cgroup v2 CPU/memory isolation
  - `pending_memory/`: Pending KEM challenge memory growth ($M(P)=\alpha+\beta P$)
- Requires `KEM_TEST_INSTRUMENTATION` build flag, cgroup v2

### supp_rtt_loss
- Goal: Dense RTT scan (9 points) and random packet loss sensitivity
- Script: testScripts/supp_rtt_loss/run (--mode rtt|loss|all)
- Sub-experiments:
  - `rtt_scan/`: 9 RTT points (0–200 ms), 500 iterations each
  - `loss/`: 5 loss levels (0–2%), 5 seeds × 200 iterations

## Rules
- Scripts are one-click runnable with fixed settings.
- Keep output naming stable and minimal.
- Keep all content in English for reviewer usability.
- Supplementary experiments use `supp_` prefix and `run` entry script.

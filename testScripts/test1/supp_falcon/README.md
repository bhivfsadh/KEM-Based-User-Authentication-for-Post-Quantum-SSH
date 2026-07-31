# supp_falcon — Falcon-512 / Falcon-1024 Baseline

Extends the paper's Fig.3 (Table III) authentication comparison by adding
Falcon-512 and Falcon-1024 under the same network conditions.

## Quick Start

```bash
# Full run (50 iterations, RTT=67ms, IW=10 MSS)
sudo bash testScripts/test1/supp_falcon/run

# Quick smoke test
sudo ITERATIONS=50 ROUNDS=1 \
  bash testScripts/test1/supp_falcon/run
```

## Fixed Conditions (matching Fig.3)

| Parameter | Value |
|:---|:---|
| Transport KEX | `mlkem768x25519-sha256` |
| Server hostkey | `ssh-ed25519` |
| RTT | 67 ms |
| TCP initcwnd | 10 MSS |
| Compared algorithms | falcon512, falcon1024 (+ existing Fig.3 algorithms for reference) |

## Output

| File | Content |
|:---|:---|
| `results/falcon_raw.csv` | Per-connection latency by algorithm |
| `results/falcon_summary.csv` | p50, p95, mean per algorithm |
| `results/auth_summary.csv` | Full Fig.3 comparison including Falcon |

## Requirements

- liboqs built with Falcon support (`ssh -Q key | grep falcon`)
- Root access (netem)

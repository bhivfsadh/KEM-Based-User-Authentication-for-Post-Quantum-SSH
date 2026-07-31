# supp_rtt_loss — RTT Sensitivity & Random Loss Experiments

Extends the paper's Fig.4 latency evaluation in two directions:
(1) a dense RTT scan (9 points from 0–200 ms) to verify that the three original
RTT points (37, 67, 163 ms) lie on a smooth trend, and (2) random packet loss at
fixed 67 ms RTT to compare KEMUAuth and ML-DSA-65 tail-latency degradation.

## Sub-experiments

| Directory | Description | Key Parameter |
|:---|:---|:---|
| `rtt_scan/` | Dense RTT scan: 9 points, 500 iterations each | RTT ∈ {0,20,40,60,80,100,120,160,200} ms |
| `loss/` | Random loss at RTT=67ms: 5 seeds × 200 iterations | Loss ∈ {0,0.1,0.5,1.0,2.0}% |

## Quick Start

```bash
# RTT scan only
sudo bash testScripts/supp_rtt_loss/rtt_scan/run

# Loss experiment only
sudo bash testScripts/supp_rtt_loss/loss/run

# Quick smoke test
sudo ITERATIONS=50 RTT_LIST="0 40 80 120" \
  bash testScripts/supp_rtt_loss/rtt_scan/run
sudo NUM_SEEDS=2 ITERATIONS_PER_SEED=50 \
  bash testScripts/supp_rtt_loss/loss/run
```

## Fixed Conditions

| Parameter | Value |
|:---|:---|
| Transport KEX | `mlkem768x25519-sha256` |
| Server hostkey | `ssh-ed25519` |
| TCP initcwnd | 10 MSS |
| Compared methods | KEMUAuth (ML-KEM-768) vs ML-DSA-65 |

## Output

### rtt_scan/
| File | Content |
|:---|:---|
| `results/rtt_raw.csv` | Per-connection latency by RTT and method |
| `results/rtt_summary.csv` | p50, p95, failure rate per (RTT, method) |

### loss/
| File | Content |
|:---|:---|
| `results/loss_raw.csv` | Per-connection latency by loss rate and method |
| `results/loss_summary.csv` | p50, p95, p99, TCP retransmits |
| `results/loss_retrans.csv` | Per-seed retransmission counts |

## Requirements

- Root access (netem on loopback or netns)
- `mlkem768x25519-sha256` KEX available
- ML-DSA-65 and ML-KEM-768 identities generated

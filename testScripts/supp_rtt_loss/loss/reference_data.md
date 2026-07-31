# loss — Pre-computed Results

> Host: toki-virtual-machine, Linux 6.8.0-136-generic  
> Transport KEX: mlkem768x25519-sha256, Server HostKey: ssh-ed25519  
> RTT: 67 ms, TCP initcwnd: 10 MSS  
> 5 seeds × 400 iterations = 2000 connections per loss level per method

## Random Packet Loss Sensitivity

| Loss (%) | Method | Successes | Failures (%) | p50 (ms) | p95 (ms) | p99 (ms) | TCP Retrans/conn |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | KEMUAuth | 2000 | 0.00 | 840.69 | 842.58 | 843.60 | 0.00 |
| 0 | ML-DSA-65 | 2000 | 0.00 | 841.68 | 843.63 | 844.63 | 0.00 |
| 0.1 | KEMUAuth | 2000 | 0.00 | 840.51 | 842.81 | 1115.33 | 0.07 |
| 0.1 | ML-DSA-65 | 2000 | 0.00 | 841.49 | 844.05 | 1119.90 | 0.09 |
| 0.5 | KEMUAuth | 2000 | 0.00 | 840.74 | 1116.64 | 1386.77 | 0.35 |
| 0.5 | ML-DSA-65 | 2000 | 0.00 | 841.71 | 1116.99 | 1844.37 | 0.35 |
| 1.0 | KEMUAuth | 2000 | 0.00 | 841.00 | 1184.91 | 1865.98 | 0.75 |
| 1.0 | ML-DSA-65 | 2000 | 0.00 | 841.93 | 1123.85 | 1876.07 | 0.78 |
| 2.0 | KEMUAuth | 2000 | 0.00 | 841.83 | 1774.46 | 2170.76 | 1.52 |
| 2.0 | ML-DSA-65 | 2000 | 0.00 | 842.77 | 1676.36 | 2140.88 | 1.52 |

## Key Observations

- Zero failures across all loss rates for both methods.
- p50 nearly identical between KEM and ML-DSA (~841 ms) regardless of loss rate; network RTT dominates median latency.
- p95 and p99 rise significantly with loss rate, but both methods degrade at the same rate.
- TCP retransmissions per connection are nearly identical — KEM's smaller authentication traffic does not confer a measurable advantage under random loss in this setup.

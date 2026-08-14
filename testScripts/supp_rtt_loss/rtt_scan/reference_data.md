# rtt_scan — Pre-computed Results

> Host: de-identified (Linux 6.8.0-136-generic)  
> Transport KEX: mlkem768x25519-sha256, Server HostKey: ssh-ed25519  
> TCP initcwnd: 10 MSS, 50 iterations per RTT point per method

## Dense RTT Scan (9 points, 0–200 ms)

| Target RTT (ms) | Measured RTT (ms) | KEM p50 (ms) | KEM p95 (ms) | ML-DSA p50 (ms) | ML-DSA p95 (ms) | KEM p50 Gain (%) | Failures (%) | p50 Δ (ms) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 0.025 | 74.23 | 76.59 | 77.57 | 79.15 | +4.31 | 0 | 3.34 |
| 20 | 20.117 | 329.97 | 331.81 | 331.51 | 333.88 | +0.46 | 0 | 1.54 |
| 40 | 40.106 | 550.86 | 553.20 | 552.14 | 555.19 | +0.23 | 0 | 1.28 |
| 60 | 60.108 | 770.96 | 772.55 | 772.16 | 773.85 | +0.16 | 0 | 1.20 |
| 80 | 80.065 | 990.83 | 993.33 | 992.01 | 994.50 | +0.12 | 0 | 1.18 |
| 100 | 100.110 | 1211.03 | 1212.57 | 1211.67 | 1214.08 | +0.05 | 0 | 0.64 |
| 120 | 120.135 | 1431.31 | 1433.31 | 1432.28 | 1434.27 | +0.07 | 0 | 0.97 |
| 160 | 160.136 | 1870.96 | 1872.57 | 1872.24 | 1874.26 | +0.07 | 0 | 1.28 |
| 200 | 200.120 | 2310.94 | 2313.86 | 2312.00 | 2314.49 | +0.05 | 0 | 1.06 |

## Key Observations

- At RTT=0, KEM is ~3.3 ms faster than ML-DSA (pure algorithm difference).
- As RTT increases, the absolute difference shrinks to ~1 ms; network latency dominates total handshake time.
- The paper's three original RTT points (37, 67, 163 ms) lie on a smooth, continuous trend with no missing inflection points.
- Zero failures across all 9 RTT points for both methods.

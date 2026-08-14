# throughput_cgroup — Pre-computed Results

> Host: de-identified (Linux 6.8.0-136-generic)  
> OpenSSH: 10.2-2025-12_p1 + liboqs 2025-12 + OpenSSL 3.0.2  
> Transport KEX: mlkem768x25519-sha256  
> Server HostKey: ssh-mldsa-65  
> 2-server-core cgroup v2 isolation, loopback, no artificial RTT or loss  
> 5 independent runs per concurrency level, medians reported  
> Each run: 5 s warm-up, 30 s measurement, 10 s cooldown  
> Throughput computed from successfully completed connections only

## Throughput & Resource Consumption

| N | Authentication method | Successful throughput (conn/s) | Gain vs. ML-DSA-65 | Server CPU utilization (%) | CPU per completed connection (ms) | p95 latency (ms) | Peak memory (MB) |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | KEMUAuth | 11.36 | 4.5% | 11.2 | 19.67 | 79 | 9.3 |
| 1 | ML-DSA-65 | 10.87 | — | 10.7 | 19.70 | 83 | 9.3 |
| 8 | KEMUAuth | 84.48 | 3.3% | 74.4 | 17.57 | 94 | 39.6 |
| 8 | ML-DSA-65 | 81.75 | — | 72.5 | 17.72 | 97 | 40.1 |
| 16 | KEMUAuth | 107.99 | 1.4% | 97.6 | 18.06 | 158 | 74.4 |
| 16 | ML-DSA-65 | 106.46 | — | 97.0 | 18.22 | 161 | 74.6 |
| 32 | KEMUAuth | 107.65 | 1.1% | 99.5 | 18.49 | 317 | 133.3 |
| 32 | ML-DSA-65 | 106.48 | — | 99.5 | 18.69 | 321 | 133.5 |
| 64 | KEMUAuth | 106.27 | 0.35% | 99.7 | 18.97 | 665 | 242.9 |
| 64 | ML-DSA-65 | 105.90 | — | 99.8 | 19.06 | 680 | 244.4 |

Throughput gain computed as:

```text
Gain(N) = (Throughput_KEMUAuth(N) − Throughput_ML-DSA-65(N))
          / Throughput_ML-DSA-65(N) × 100%
```

## Key Observations

- **N=1**: KEMUAuth achieves 4.5% higher throughput; single-connection algorithm advantage visible without concurrency pressure.
- **N=8**: KEMUAuth holds a 3.3% edge with both schemes around 75% CPU.
- **N=16–32**: CPU near saturation (~97–99.5%); throughput converges to ~106–108 conn/s; KEMUAuth advantage narrows to ~1%.
- **N=64**: Both schemes fully CPU-bound (~99.7%); throughput essentially equal (106.27 vs 105.90, +0.35%).
- **CPU/conn**: Both schemes stable at ~17–20 ms per completed connection across all N, confirming per-connection cost is independent of load.
- **Memory**: Near-identical peak memory between schemes; no memory-leak concern for either.
- This is a stress-test simulation. Failed attempts near CPU saturation are expected and do not indicate a protocol defect. Throughput is computed from successfully completed connections only.

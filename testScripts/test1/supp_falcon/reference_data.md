# supp_falcon — Pre-computed Results

> Host: toki-virtual-machine, Linux 6.8.0-136-generic  
> OpenSSH: 10.2-2025-12_p1 + liboqs 2025-12 + OpenSSL 3.0.2  
> Transport KEX: mlkem768x25519-sha256, Server HostKey: ssh-ed25519  
> RTT: 67 ms, TCP initcwnd: 10 MSS, loopback  
> Falcon uses AVX2-optimized liboqs Falcon implementation (Falcon baseline, not final FIPS 206 FN-DSA)

## Authentication Latency Comparison

| Client algorithm | Notation | Authentication category | Mean (ms) | p50 (ms) | p95 (ms) |
|---|---|---|---:|---:|---:|
| Ed25519 | `ed25519` | Classical signature | 850.06 | 849.96 | 851.49 |
| ML-KEM-768 KEMUAuth | `mk768` | PQ KEM | 848.81 | 848.87 | 850.22 |
| ML-DSA-65 | `md65` | PQ signature | 849.94 | 849.89 | 851.08 |
| Falcon-512 | `falcon512` | PQ signature | 848.91 | 848.89 | 850.84 |
| Falcon-1024 | `falcon1024` | PQ signature | 849.59 | 849.46 | 852.21 |

## Key Observations

- Falcon-512, Falcon-1024, KEMUAuth, ML-DSA-65, and Ed25519 all fall within a ~1 ms
  p50 band at IW10. Fixed protocol and network costs dominate; algorithmic signature
  or KEM differences are not visible at this RTT.
- This table uses the AVX2-optimized liboqs Falcon implementation as a Falcon baseline
  and should not be interpreted as final FIPS 206 FN-DSA results.

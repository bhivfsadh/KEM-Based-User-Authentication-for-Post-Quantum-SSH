# pending_memory — Pre-computed Results

> Host: toki-virtual-machine, Linux 6.8.0-136-generic  
> OpenSSH: 10.2-2025-12_p1 + liboqs 2025-12 + OpenSSL 3.0.2  
> Transport KEX: mlkem768x25519-sha256, Server HostKey: ssh-mldsa-65  
> RESPONSE_DELAY_MS=20000, HOLD_WINDOW_SEC=35, cgroup v2  
> Values are from linear fit across 5 independent runs per concurrency level

## Memory Growth: Linear Fit

Fitted models from measured peak memory at observed pending counts:

```text
M_KEMUAuth(P) ≈ 24.5413 + 3.10889·P   MiB
M_ML-DSA(P)   ≈ 20.2618 + 3.11238·P   MiB
```

| Normalized pending count P | Estimated peak memory: KEMUAuth (MiB) | Estimated peak memory: ML-DSA-65 (MiB) | Memory difference (MiB) | Explicit KEM state (MiB) |
|---:|---:|---:|---:|---:|
| 16 | 74.28 | 70.06 | 4.22 | 0.036 |
| 32 | 124.03 | 119.86 | 4.17 | 0.073 |
| 64 | 223.51 | 219.45 | 4.05 | 0.146 |
| 128 | 422.48 | 418.65 | 3.83 | 0.291 |
| 172 | 559.27 | 555.59 | 3.67 | 0.391 |

Both schemes share nearly identical per-connection slopes (~3.11 MiB/conn). This slope
is dominated by standard OpenSSH per-connection overhead (process, socket, transport state)
and should not be attributed to the KEM challenge itself.

## Explicit KEM Challenge State

The implementation retains **2,384 bytes per pending challenge** in explicitly
allocated KEMUAuth challenge context:

```text
M_explicit(P) = 2384·P / 2^20  MiB
M_explicit(172) = 2384·172 / 2^20 ≈ 0.391 MiB
```

## Key Observations

- Aggregate memory scaling is effectively identical for KEMUAuth and ML-DSA-65 (~3.11 MiB per pending connection).
- The fitted offset difference (~4 MiB) reflects implementation details (allocator, page granularity, minor fixed-size structures) and should not be interpreted as per-challenge cost.
- Explicit KEMUAuth-specific state is 2,384 bytes per pending challenge; at 172 pending challenges this contributes <0.4 MiB.
- Pending counter returns to 0 after authentication completes or connection terminates; no memory leak observed.

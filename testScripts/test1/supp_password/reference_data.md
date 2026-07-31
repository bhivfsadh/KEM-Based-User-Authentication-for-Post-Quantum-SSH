# supp_password — Pre-computed Results

> Host: toki-virtual-machine, Linux 6.8.0-136-generic  
> OpenSSH: 10.2-2025-12_p1 + liboqs 2025-12 + OpenSSL 3.0.2  
> Transport KEX: mlkem768x25519-sha256, Server HostKey: ssh-ed25519  
> RTT: 67 ms, TCP initcwnd: 10 MSS, loopback  
> Password test account: ssh_pwd_test, yescrypt ($y$j9T), PAM pam_unix

## Authentication Latency Comparison

| Client algorithm | Notation | Authentication category | Mean (ms) | p50 (ms) | p95 (ms) |
|---|---|---|---:|---:|---:|
| Ed25519 | `ed25519` | Classical signature | 850.06 | 849.96 | 851.49 |
| ML-KEM-768 KEMUAuth | `mk768` | PQ KEM | 848.81 | 848.87 | 850.22 |
| ML-DSA-65 | `md65` | PQ signature | 849.94 | 849.89 | 851.08 |
| Password (yescrypt) | `password` | Password | 792.69 | 792.45 | 794.56 |

## Key Observations

- Password authentication median latency is ~57 ms lower than cryptographic methods,
  primarily because it skips the public-key probe/KEM challenge round-trip required
  by signature and KEM-based authentication.
- This result should not be interpreted as password hashing being faster than KEM
  or signature operations; the protocol flows and credential models differ.
- This baseline is provided for deployment-context performance reference only.
  Password authentication relies on a low-entropy shared secret and does not share
  the security semantics of public-key or KEM-based proof-of-possession.

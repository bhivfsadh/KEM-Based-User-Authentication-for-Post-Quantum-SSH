# Exp 3 Table 1: Protocol-Level Observable Behavior

| Ciphertext Class | Tests | Client Returns Response? | Response Type | Response Length (B) | Auth Result | p50 Challenge-to-Response (ms) | p95 Challenge-to-Response (ms) | Crashes or Errors |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| valid | 50 | YES | KEM_RESPONSE | — | 50 success | 5.1 | 5.2 | 0 |
| onebit | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.2 | 0 |
| multibit | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.2 | 0 |
| random | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.3 | 0 |
| allzero | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.2 | 0 |
| allff | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.3 | 0 |
| truncated | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.4 | 0 |
| extended | 50 | YES | KEM_RESPONSE | — | 50 auth failure | 5.1 | 5.2 | 0 |

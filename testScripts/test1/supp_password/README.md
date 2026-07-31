# supp_password — Password Authentication Baseline

Adds a Password--yescrypt baseline to the paper's Fig.3 (Table III) authentication
comparison. Uses SSH password method with PAM `pam_unix` and yescrypt hashing
(`/etc/shadow`). This is a deployment reference only; it does not share the
security semantics of public-key or KEM-based authentication.

## Quick Start

```bash
# Full run (creates test account, runs 50 iterations)
sudo bash testScripts/test1/supp_password/run

# Use existing account
sudo SETUP_ACCOUNT=0 TEST_USER=myuser TEST_PASSWORD=mypass \
  bash testScripts/test1/supp_password/run
```

## Fixed Conditions (matching Fig.3)

| Parameter | Value |
|:---|:---|
| Transport KEX | `mlkem768x25519-sha256` |
| Server hostkey | `ssh-ed25519` |
| RTT | 67 ms |
| TCP initcwnd | 10 MSS |
| Auth method | `password` (PAM `pam_unix`, yescrypt `$y$j9T`) |

## Key Configuration

- `PasswordAuthentication yes`, `UsePAM yes`
- `KbdInteractiveAuthentication no` (prevents fallback)
- `PubkeyAuthentication no`, `KEMAuthentication no`
- Password supplied via `SSH_ASKPASS` (no human input in measurement)

## Output

| File | Content |
|:---|:---|
| `results/password_raw.csv` | Per-connection latency |
| `results/password_summary.csv` | p50, p95, mean vs KEM/ML-DSA/Ed25519 |

## Security Note

Password authentication relies on a low-entropy shared secret and allows the
server to obtain and verify the password. KEMUAuth and signature-based
authentication prove possession of a high-entropy long-term private key. This
baseline is provided for deployment-context performance comparison only.

## Requirements

- Root access (create test account, configure sshd)
- PAM and libxcrypt with yescrypt support
- No firewall on the test port

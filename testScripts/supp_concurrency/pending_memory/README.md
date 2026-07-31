# Pending KEM Challenge Memory Growth

Artificially delays the client after receiving a KEM challenge so that the server
accumulates a controlled number of pending challenge states. Measures peak server
memory, fits $M(P) = \alpha + \beta P$, and separates explicit challenge-state
size from per-connection SSH overhead.

## Quick Start

```bash
# Quick smoke test (P = 0, 16, 32, 3s delay)
sudo TEST2_ALLOW_FALLBACK=1 \
  bash testScripts/supp_concurrency/pending_memory/run

# Full run (P = 0, 16, 32, 64, 128, 256, 7 rounds, 20s delay)
sudo TARGET_CONCURRENCY="0 16 32 64 128 256" RUNS=7 \
  RESPONSE_DELAY_MS=20000 HOLD_WINDOW_SEC=35 \
  bash testScripts/supp_concurrency/pending_memory/run
```

## Environment Variables

| Variable | Default | Description |
|:---|:---|:---|
| `TARGET_CONCURRENCY` | `0 16 32 64 128 256` | Target concurrent connections |
| `RUNS` | `5` | Rounds per configuration |
| `RESPONSE_DELAY_MS` | `10000` | Client delay after challenge (ms) |
| `HOLD_WINDOW_SEC` | `15` | Sampling window duration |
| `SKIP_CLEANUP_TESTS` | `0` | Set to `1` to skip cleanup validation |

## How It Works

1. **KEM mode**: Client receives KEM challenge → pauses (`KEMUAUTH_RESPONSE_DELAY_MS` ms) → decrypts & responds. Server-side `KEM_PENDING_INC/DEC` events track active challenges.
2. **Baseline mode** (ML-DSA-65): Client receives `PK_OK` → pauses (`SIGAUTH_RESPONSE_DELAY_MS` ms) → signs & responds. `BASELINE_PAUSE_INC/DEC` events in client logs track active paused connections.

Both modes use barrier-synchronised client launch so that measured concurrency is comparable.

## Output

| File | Content |
|:---|:---|
| `results/summary.csv` | Per-(P, mode, run): peak memory, pending estimate, pids, cleanup status |
| `results/pending_events.csv` | Server-side KEM challenge create/destroy events |
| `results/metadata.txt` | Host info, parameters, commit hash |

## Build Requirements

`KEM_TEST_INSTRUMENTATION` must be defined in `config.h`. This enables:
- Server-side `kem_test_inc_pending()` / `kem_test_dec_pending()` → `KEM_PENDING_INC/DEC` in sshd log
- Client-side `KEMUAUTH_RESPONSE_DELAY_MS` → `usleep()` in `input_userauth_kem_info_req()`
- Client-side `SIGAUTH_RESPONSE_DELAY_MS` → `fprintf(stderr, "BASELINE_PAUSE_INC/DEC")` in `input_userauth_pk_ok()`

The instrumentation patch is at `patch/pending_counter.patch` for reference.

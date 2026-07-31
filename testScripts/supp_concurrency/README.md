# supp_concurrency — Server-Side Concurrency Experiments

Two supplementary experiments that measure server-side resource consumption under
controlled concurrency: (1) full-SSH throughput with cgroup CPU/memory accounting,
and (2) per-connection memory cost of pending KEM challenges.

## Sub-experiments

| Directory | Description | Paper Context |
|:---|:---|:---|
| `throughput_cgroup/` | Full-SSH concurrency throughput with cgroup v2 CPU and memory isolation (§1 of testInfo) | Complements Fig.3 by isolating server-side efficiency |
| `pending_memory/` | Pending KEM challenge memory growth under artificial client delay (§2 of testInfo) | Measures per-challenge state overhead separate from connection cost |

## Shared Requirements

- Root access (cgroup v2, CPU affinity)
- KEMSSH built with `KEM_TEST_INSTRUMENTATION` enabled in `config.h`
- `test/step1/gen_kem_identity_mlkem768.sh` must have been run

## Build

```bash
# Ensure KEM_TEST_INSTRUMENTATION is in config.h
grep KEM_TEST_INSTRUMENTATION config.h || \
  echo '#define KEM_TEST_INSTRUMENTATION 1' >> config.h
make -j4 ssh sshd sshd-session sshd-auth ssh-keygen
```

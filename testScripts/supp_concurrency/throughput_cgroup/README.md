# Throughput & Cgroup Resource Experiment

Compares ML-KEM-768 KEMUAuth against ML-DSA-65 signature authentication under
escalating SSH connection concurrency (N = 1, 8, 16, 32, 64, 128, 256). Measures
server-side connection throughput, CPU utilization, per-connection CPU cost,
peak memory, and p95 end-to-end latency via cgroup v2.

## Quick Start

```bash
# Pilot run (N = 1, 16, 64, 128, 256, 5 warmup + 30s measurement)
sudo bash testScripts/supp_concurrency/throughput_cgroup/run

# Full 5-round run
sudo CONCURRENCY_LIST="1 8 16 32 64 128 256" RUNS=5 \
  WARMUP_SECONDS=5 MEASURE_SECONDS=30 \
  bash testScripts/supp_concurrency/throughput_cgroup/run
```

## Environment Variables

| Variable | Default | Description |
|:---|:---|:---|
| `CONCURRENCY_LIST` | `1 8 16 32 64 128 256` | Concurrency levels |
| `RUNS` | `5` | Rounds per configuration |
| `WARMUP_SECONDS` | `5` | Warmup duration before measurement |
| `MEASURE_SECONDS` | `30` | Measurement window |
| `SERVER_CPUSET` | auto (2 cores) | Server CPU affinity |
| `CLIENT_CPUSET` | auto (remaining) | Client CPU affinity |
| `MAX_STARTUPS` | `1024` | sshd MaxStartups |

## Output

| File | Content |
|:---|:---|
| `results/raw_runs.csv` | Per-connection latency, retcode, error class |
| `results/summary.csv` | Aggregated throughput, CPU%, CPU/conn, peak memory, p95 |
| `results/metadata.txt` | Host info, commit hash, build options |

## Key Configuration

- Transport KEX: `mlkem768x25519-sha256`
- Server hostkey: `ssh-mldsa-65`
- Remote command: `true`
- cgroup v2 required (CPU + memory controllers)
- Server and client pinned to disjoint CPU sets

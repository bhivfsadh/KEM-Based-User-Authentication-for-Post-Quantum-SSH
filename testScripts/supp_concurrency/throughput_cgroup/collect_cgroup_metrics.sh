#!/usr/bin/env bash
# collect_cgroup_metrics.sh — continuous cgroup CPU and memory sampling
# Used for Exp 1 (concurrency throughput)
#
# Usage:
#   bash collect_cgroup_metrics.sh <cg_path> <output_csv> <interval_sec> <duration_sec>
#
# Output CSV: timestamp_epoch,memory_bytes,memory_mb,pids_current

set -euo pipefail

CG_PATH="$1"
OUTPUT_CSV="$2"
INTERVAL_SEC="${3:-0.1}"
DURATION_SEC="${4:-30}"

source "$(dirname "$0")/../common/cgroup_utils.sh"

echo "timestamp_epoch,memory_bytes,memory_mb,pids_current" > "$OUTPUT_CSV"

start_time="$(date +%s)"

while true; do
  current_time="$(date +%s)"
  elapsed=$((current_time - start_time))
  if [[ $elapsed -ge $DURATION_SEC ]]; then
    break
  fi

  local mem_val now pids_val
  now="$(date +%s.%N)"
  mem_val="$(read_memory_current "$CG_PATH")"
  pids_val="$(read_pids_current "$CG_PATH")"

  local mem_mb="NA"
  if [[ "$mem_val" != "NA" && "$mem_val" =~ ^[0-9]+$ ]]; then
    mem_mb="$(bytes_to_mb "$mem_val")"
  fi

  echo "$now,$mem_val,$mem_mb,$pids_val" >> "$OUTPUT_CSV"

  sleep "$INTERVAL_SEC"
done

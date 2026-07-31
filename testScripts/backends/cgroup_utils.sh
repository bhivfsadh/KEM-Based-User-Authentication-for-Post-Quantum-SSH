#!/usr/bin/env bash
# cgroup_utils.sh — cgroup v2 create/destroy/CPU/memory collection tools
# Used for Exp 1 (concurrency throughput + cgroup resources) and Exp 2 (Pending memory)
set -euo pipefail

# ---- Constants ----
CGROUP_V2_ROOT="${CGROUP_V2_ROOT:-/sys/fs/cgroup}"

# ---- Check cgroup v2 ----
check_cgroup_v2() {
  if [[ ! -f "$CGROUP_V2_ROOT/cgroup.controllers" ]]; then
    echo "[ERR] cgroup v2 not mounted at $CGROUP_V2_ROOT"
    echo "[HINT] ensure system boots with cgroup v2 (systemd.unified_cgroup_hierarchy=1)"
    return 1
  fi
  if ! grep -q cpu "$CGROUP_V2_ROOT/cgroup.controllers" 2>/dev/null; then
    echo "[ERR] cpu controller not available at $CGROUP_V2_ROOT"
    return 1
  fi
  return 0
}

# ---- Create cgroup and enable controllers ----
# Usage: create_cgroup <name>
# Returns: cgroup path (e.g. /sys/fs/cgroup/ssh-test-xxx)
create_cgroup() {
  local name="$1"
  local cg_path="$CGROUP_V2_ROOT/$name"

  if [[ -d "$cg_path" ]]; then
    echo "[WARN] cgroup $cg_path already exists; reusing" >&2
  else
    mkdir -p "$cg_path"
  fi

  # Enable cpu + memory controllers (recursively to leaf nodes)
  local controllers="+cpu +memory"
  echo "$controllers" > "$CGROUP_V2_ROOT/cgroup.subtree_control" 2>/dev/null || true

  echo "$cg_path"
}

# ---- Add process to cgroup ----
# Usage: add_pid_to_cgroup <cg_path> <pid>
add_pid_to_cgroup() {
  local cg_path="$1"
  local pid="$2"
  echo "$pid" >> "$cg_path/cgroup.procs" 2>/dev/null || {
    echo "[ERR] failed to add pid $pid to $cg_path" >&2
    return 1
  }
}

# ---- Add process and all descendants to cgroup (by process tree) ----
add_pid_tree_to_cgroup() {
  local cg_path="$1"
  local root_pid="$2"

  add_pid_to_cgroup "$cg_path" "$root_pid" || return 1

  # Recursively add all children
  local children
  children="$(pgrep -P "$root_pid" 2>/dev/null || true)"
  for child in $children; do
    add_pid_tree_to_cgroup "$cg_path" "$child" 2>/dev/null || true
  done
}

# ---- Continuously add sshd-related processes to cgroup (background task) ----
# Usage: start_cgroup_watcher <cg_path> [interval_sec]
# Output: watcher PID
start_cgroup_watcher() {
  local cg_path="$1"
  local interval="${2:-0.5}"

  (
    while true; do
      # Find all sshd-related processes
      for pid in $(pgrep -f "sshd" 2>/dev/null || true); do
        echo "$pid" >> "$cg_path/cgroup.procs" 2>/dev/null || true
      done
      sleep "$interval"
    done
  ) >/dev/null 2>&1 &
  echo $!
}

# ---- Read CPU usage_usec ----
read_cpu_usage_usec() {
  local cg_path="$1"
  if [[ -f "$cg_path/cpu.stat" ]]; then
    awk '$1=="usage_usec" {print $2; exit}' "$cg_path/cpu.stat"
  else
    echo "NA"
  fi
}

# ---- Read memory.current (bytes) ----
read_memory_current() {
  local cg_path="$1"
  if [[ -f "$cg_path/memory.current" ]]; then
    cat "$cg_path/memory.current"
  else
    echo "NA"
  fi
}

# ---- Read memory.peak (bytes, cgroup v2) ----
read_memory_peak() {
  local cg_path="$1"
  if [[ -f "$cg_path/memory.peak" ]]; then
    cat "$cg_path/memory.peak"
  else
    echo "NA"
  fi
}

# ---- Reset memory.peak (write to trigger refresh) ----
reset_memory_peak() {
  local cg_path="$1"
  if [[ -f "$cg_path/memory.peak" ]]; then
    # Cannot write memory.peak directly; use memory.max to reset state
    # Actual approach: record current value as baseline, compute delta manually
    echo "0" > "$cg_path/memory.peak" 2>/dev/null || true
  fi
}

# ---- Read pids.current ----
read_pids_current() {
  local cg_path="$1"
  if [[ -f "$cg_path/pids.current" ]]; then
    cat "$cg_path/pids.current"
  else
    echo "NA"
  fi
}

# ---- Destroy cgroup ----
destroy_cgroup() {
  local cg_path="$1"
  if [[ -d "$cg_path" ]]; then
    # Drain processes first
    echo "" > "$cg_path/cgroup.procs" 2>/dev/null || true
    sleep 0.2
    rmdir "$cg_path" 2>/dev/null || {
      echo "[WARN] could not remove cgroup $cg_path (may have lingering procs)" >&2
    }
  fi
}

# ---- CPU utilization calculation ----
# Usage: calc_cpu_util <delta_usec> <duration_sec> <cpu_cores>
# Output: percentage (0-100)
calc_cpu_util() {
  local delta_usec="$1"
  local duration_sec="$2"
  local cpu_cores="$3"

  if [[ "$delta_usec" == "NA" || -z "$delta_usec" ]]; then
    echo "NA"
    return
  fi

  # utilization_pct = delta_usec / (duration_sec * 1e6 * cores) * 100
  python3 -c "
du = float('$delta_usec')
ds = float('$duration_sec')
cc = float('$cpu_cores')
util = (du / (ds * 1_000_000 * cc)) * 100.0
print(f'{util:.2f}')
" 2>/dev/null || echo "NA"
}

# ---- CPU per connection calculation ----
# Usage: calc_cpu_per_conn <delta_usec> <success_count>
# Output: milliseconds per connection
calc_cpu_per_conn() {
  local delta_usec="$1"
  local success_count="$2"

  if [[ "$delta_usec" == "NA" || -z "$delta_usec" || "$success_count" -le 0 ]]; then
    echo "NA"
    return
  fi

  python3 -c "
du = float('$delta_usec')
sc = int('$success_count')
ms = (du / 1000.0) / sc
print(f'{ms:.3f}')
" 2>/dev/null || echo "NA"
}

# ---- Bytes to MB ----
bytes_to_mb() {
  local bytes="$1"
  if [[ "$bytes" == "NA" || -z "$bytes" ]]; then
    echo "NA"
    return
  fi
  python3 -c "print(f'{int($bytes) / (1024*1024):.2f}')" 2>/dev/null || echo "NA"
}

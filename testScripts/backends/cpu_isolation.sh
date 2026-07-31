#!/usr/bin/env bash
# cpu_isolation.sh — CPU affinity binding tools
# Used for Exp 1 and Exp 4
set -euo pipefail

# ---- Get logical CPU count ----
get_ncpu() {
  getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 1
}

# ---- Get CPU sibling mapping ----
# Output format: logical_id core_id socket_id
get_cpu_topology() {
  if command -v lscpu >/dev/null 2>&1; then
    lscpu -e=CPU,CORE,SOCKET,NODE 2>/dev/null | tail -n +2 || true
  fi
}

# ---- Generate cpuset range string ----
# Usage: mk_cpuset_range <start> <end>
mk_cpuset_range() {
  local a="$1"
  local b="$2"
  if (( a >= b )); then
    echo "$a"
  else
    echo "$a-$b"
  fi
}

# ---- Count cores in cpuset ----
count_cpuset_cpus() {
  local spec="$1"
  python3 -c "
spec = '$spec'
total = 0
for part in spec.split(','):
    part = part.strip()
    if '-' in part:
        lo, hi = part.split('-', 1)
        total += int(hi) - int(lo) + 1
    elif part.isdigit():
        total += 1
print(total)
" 2>/dev/null || echo 1
}

# ---- Check if two cpusets overlap ----
cpuset_overlap() {
  local a="$1"
  local b="$2"
  python3 -c "
def expand(s):
    cpus = set()
    for part in s.split(','):
        part = part.strip()
        if '-' in part:
            lo, hi = part.split('-', 1)
            cpus.update(range(int(lo), int(hi)+1))
        elif part.isdigit():
            cpus.add(int(part))
    return cpus

a_set = expand('$a')
b_set = expand('$b')
overlap = a_set & b_set
if overlap:
    print(f'OVERLAP: {sorted(overlap)}')
else:
    print('OK')
" 2>/dev/null
}

# ---- Bind process to CPUs ----
# Usage: bind_to_cpus <pid> <cpuset>
bind_to_cpus() {
  local pid="$1"
  local cpuset="$2"
  taskset -pc "$cpuset" "$pid" >/dev/null 2>&1 || {
    echo "[ERR] failed to bind pid $pid to cpuset $cpuset" >&2
    return 1
  }
}

# ---- Bind process tree to CPUs ----
bind_tree_to_cpus() {
  local root_pid="$1"
  local cpuset="$2"

  bind_to_cpus "$root_pid" "$cpuset" || return 1

  # Recursively bind children
  local children
  children="$(pgrep -P "$root_pid" 2>/dev/null || true)"
  for child in $children; do
    bind_tree_to_cpus "$child" "$cpuset" 2>/dev/null || true
  done
}

# ---- Auto-split server/client cpusets for experiments ----
# Usage: auto_split_cpusets <server_cores>
# Output: SERVER_CPUSET=... CLIENT_CPUSET=...
auto_split_cpusets() {
  local server_cores="${1:-2}"
  local ncpu
  ncpu="$(get_ncpu)"

  if (( ncpu < server_cores + 1 )); then
    echo "[ERR] not enough CPUs: have $ncpu, need at least $((server_cores + 1))" >&2
    return 1
  fi

  local server_start=0
  local server_end=$((server_cores - 1))
  local client_start=$server_cores
  local client_end=$((ncpu - 1))

  echo "SERVER_CPUSET=$(mk_cpuset_range $server_start $server_end)"
  echo "CLIENT_CPUSET=$(mk_cpuset_range $client_start $client_end)"
  echo "[INFO] auto split: server=$(mk_cpuset_range $server_start $server_end) client=$(mk_cpuset_range $client_start $client_end)" >&2
}

# ---- Bind current shell to CPUs ----
bind_self_to_cpus() {
  local cpuset="$1"
  taskset -cp "$cpuset" $$ >/dev/null 2>&1 || {
    echo "[ERR] failed to bind self to cpuset $cpuset" >&2
    return 1
  }
}

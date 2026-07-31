#!/usr/bin/env bash
# netem_setup.sh — netem (RTT/packet loss) setup and verification
# Used for Exp 4 (RTT dense scan + random packet loss)
set -euo pipefail

SUDO_BIN="${SUDO_BIN:-sudo}"

# ---- Check netem dependencies ----
check_netem_deps() {
  for cmd in tc ip ping; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "[ERR] missing: $cmd" >&2; return 1; }
  done
}

# ---- Set netem delay on interface (half RTT each direction) ----
# Usage: set_netem_delay <iface> <rtt_ms>
set_netem_delay() {
  local iface="$1"
  local rtt_ms="$2"
  local half_ms
  half_ms="$((rtt_ms / 2))"

  # Clear existing qdisc
  "$SUDO_BIN" tc qdisc del dev "$iface" root 2>/dev/null || true

  # Add netem delay (one-way delay = RTT/2)
  "$SUDO_BIN" tc qdisc add dev "$iface" root netem delay "${half_ms}ms"
  echo "[INFO] netem: $iface delay=${half_ms}ms (RTT=${rtt_ms}ms)"
}

# ---- Set netem delay + random packet loss on interface ----
# Usage: set_netem_delay_loss <iface> <rtt_ms> <loss_pct>
set_netem_delay_loss() {
  local iface="$1"
  local rtt_ms="$2"
  local loss_pct="$3"
  local half_ms
  half_ms="$((rtt_ms / 2))"

  "$SUDO_BIN" tc qdisc del dev "$iface" root 2>/dev/null || true
  "$SUDO_BIN" tc qdisc add dev "$iface" root netem delay "${half_ms}ms" loss random "${loss_pct}%"
  echo "[INFO] netem: $iface delay=${half_ms}ms loss=${loss_pct}% (RTT=${rtt_ms}ms)"
}

# ---- Clear netem ----
clear_netem() {
  local iface="$1"
  "$SUDO_BIN" tc qdisc del dev "$iface" root 2>/dev/null || true
}

# ---- Verify RTT ----
# Usage: verify_rtt <target_ip> <expected_rtt_ms>
verify_rtt() {
  local target_ip="$1"
  local expected_rtt="$2"

  local avg_rtt
  avg_rtt=$(ping -c 10 -q "$target_ip" 2>/dev/null | awk -F'/' 'END{print $5}' || echo "NA")

  if [[ "$avg_rtt" != "NA" ]]; then
    echo "[INFO] ping avg RTT: ${avg_rtt}ms (expected ~${expected_rtt}ms)"
  else
    echo "[WARN] cannot verify RTT via ping"
  fi
}

# ---- Show current qdisc ----
show_qdisc() {
  local iface="$1"
  "$SUDO_BIN" tc -s qdisc show dev "$iface" 2>/dev/null || true
}

# ---- Disable TSO/GSO/GRO on veth (avoid large-packet coalescing skewing netem) ----
disable_offload() {
  local iface="$1"
  "$SUDO_BIN" ethtool -K "$iface" tso off gso off gro off 2>/dev/null || true
}

# ---- Read TCP retransmission counter ----
read_tcp_retrans() {
  nstat -az TcpRetransSegs 2>/dev/null | awk '/TcpRetransSegs/ {print $2}' || echo "NA"
}

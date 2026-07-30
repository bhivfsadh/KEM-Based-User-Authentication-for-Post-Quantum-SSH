#!/usr/bin/env bash
# sshd_test_harness.sh — sshd start/stop/config/keygen common template
# Used across all new experiments
set -euo pipefail

ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../../.." && pwd)}"

# ---- Defaults ----
SSH_BIN="${SSH_BIN:-$ROOT_DIR/ssh}"
SSHD_BIN="${SSHD_BIN:-$ROOT_DIR/sshd}"
SSH_KEYGEN_BIN="${SSH_KEYGEN_BIN:-$ROOT_DIR/ssh-keygen}"
SSHD_SESSION_BIN="${SSHD_SESSION_BIN:-$ROOT_DIR/sshd-session}"
SSHD_AUTH_BIN="${SSHD_AUTH_BIN:-$ROOT_DIR/sshd-auth}"

TEST_USER="${TEST_USER:-$(id -un)}"
TEST_HOST="${TEST_HOST:-127.0.0.1}"
TEST_PORT="${TEST_PORT:-42222}"
MAX_STARTUPS="${MAX_STARTUPS:-1024}"
MAX_SESSIONS="${MAX_SESSIONS:-1}"
LOG_LEVEL="${LOG_LEVEL:-ERROR}"

# ---- Binary checks ----
check_ssh_binaries() {
  local missing=0
  for b in "$SSH_BIN" "$SSHD_BIN" "$SSH_KEYGEN_BIN" "$SSHD_SESSION_BIN" "$SSHD_AUTH_BIN"; do
    if [[ ! -x "$b" ]]; then
      echo "[ERR] missing binary: $b" >&2
      missing=1
    fi
  done
  return $missing
}

# ---- Command checks ----
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERR] missing command: $1" >&2; return 1; }
}

# ---- Generate Ed25519 host key ----
gen_host_key_ed25519() {
  local work_dir="$1"
  local key_file="$work_dir/ssh_host_ed25519_key"

  if [[ ! -f "$key_file" ]]; then
    "$SSH_KEYGEN_BIN" -q -t ed25519 -N "" -f "$key_file" >/dev/null
  fi
  echo "$key_file"
}

# ---- Generate ML-DSA-65 host key ----
gen_host_key_mldsa65() {
  local work_dir="$1"
  local key_file="$work_dir/ssh_host_mldsa65_key"

  if [[ ! -f "$key_file" ]]; then
    "$SSH_KEYGEN_BIN" -q -t ssh-mldsa-65 -N "" -f "$key_file" >/dev/null
  fi
  echo "$key_file"
}

# ---- Generate Ed25519 user key ----
gen_user_key_ed25519() {
  local work_dir="$1"
  local key_file="$work_dir/id_ed25519"

  if [[ ! -f "$key_file" ]]; then
    "$SSH_KEYGEN_BIN" -q -t ed25519 -N "" -f "$key_file" >/dev/null
    chown "$TEST_USER" "$key_file" "$key_file.pub" 2>/dev/null || true
  fi
  echo "$key_file"
}

# ---- Generate ML-DSA-65 user key ----
gen_user_key_mldsa65() {
  local work_dir="$1"
  local key_file="$work_dir/id_mldsa65"

  if [[ ! -f "$key_file" ]]; then
    "$SSH_KEYGEN_BIN" -q -t ssh-mldsa-65 -N "" -f "$key_file" >/dev/null
    chown "$TEST_USER" "$key_file" "$key_file.pub" 2>/dev/null || true
  fi
  echo "$key_file"
}

# ---- Generate known_hosts ----
gen_known_hosts() {
  local work_dir="$1"
  local host_key_pub="$2"
  local known_hosts="$work_dir/known_hosts"

  if [[ -f "$host_key_pub" ]]; then
    local key_line
    key_line="$TEST_HOST $(cat "$host_key_pub")"
    echo "$key_line" > "$known_hosts"
  fi
  echo "$known_hosts"
}

# ---- Write standard sshd_config ----
# Usage: write_sshd_config <cfg_file> <host_key_file> <authorized_keys_file> [authorized_kem_keys_file]
write_sshd_config() {
  local cfg="$1"
  local host_key="$2"
  local auth_keys="$3"
  local auth_kem_keys="${4:-}"

  cat > "$cfg" <<EOF
Port $TEST_PORT
ListenAddress $TEST_HOST
PidFile $(dirname "$cfg")/sshd.pid
HostKey $host_key
HostKeyAlgorithms $HOST_KEY_ALGS
KexAlgorithms mlkem768x25519-sha256
LogLevel $LOG_LEVEL
SshdSessionPath $SSHD_SESSION_BIN
SshdAuthPath $SSHD_AUTH_BIN

# Disable non-test authentication
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin no

# Public-key authentication (signature)
PubkeyAuthentication yes
PubkeyAcceptedAlgorithms ssh-ed25519,ssh-mldsa-65
AuthorizedKeysFile $auth_keys

# KEM authentication
KEMAuthentication yes
KEMAuthAlgorithms ML-KEM-768
EOF

  if [[ -n "$auth_kem_keys" && -f "$auth_kem_keys" ]]; then
    echo "AuthorizedKEMKeysFile $auth_kem_keys" >> "$cfg"
  fi

  cat >> "$cfg" <<EOF

# Concurrency protection
MaxStartups $MAX_STARTUPS
PerSourceMaxStartups none
MaxSessions $MAX_SESSIONS
LoginGraceTime 120
StrictModes no

# Disable extra features
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PrintMotd no
Banner none
EOF
}

# ---- Write KEM-only sshd_config ----
write_sshd_config_kem_only() {
  local cfg="$1"
  local host_key="$2"
  local auth_kem_keys="$3"

  cat > "$cfg" <<EOF
Port $TEST_PORT
ListenAddress $TEST_HOST
PidFile $(dirname "$cfg")/sshd.pid
HostKey $host_key
HostKeyAlgorithms $HOST_KEY_ALGS
KexAlgorithms mlkem768x25519-sha256
LogLevel $LOG_LEVEL
SshdSessionPath $SSHD_SESSION_BIN
SshdAuthPath $SSHD_AUTH_BIN

# Disable non-test authentication
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin no

# KEM-only authentication
PubkeyAuthentication no
KEMAuthentication yes
KEMAuthAlgorithms ML-KEM-768
AuthenticationMethods publickey-kem
AuthorizedKEMKeysFile $auth_kem_keys

# Concurrency protection
MaxStartups $MAX_STARTUPS
PerSourceMaxStartups none
MaxSessions $MAX_SESSIONS
LoginGraceTime 120
StrictModes no

# Disable extra features
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PrintMotd no
Banner none
EOF
}

# ---- Write signature-only sshd_config ----
write_sshd_config_sig_only() {
  local cfg="$1"
  local host_key="$2"
  local auth_keys="$3"

  cat > "$cfg" <<EOF
Port $TEST_PORT
ListenAddress $TEST_HOST
PidFile $(dirname "$cfg")/sshd.pid
HostKey $host_key
HostKeyAlgorithms $HOST_KEY_ALGS
KexAlgorithms mlkem768x25519-sha256
LogLevel $LOG_LEVEL
SshdSessionPath $SSHD_SESSION_BIN
SshdAuthPath $SSHD_AUTH_BIN

# Disable non-test authentication
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin no

# Signature-only authentication
PubkeyAuthentication yes
PubkeyAcceptedAlgorithms ssh-mldsa-65
AuthorizedKeysFile $auth_keys
KEMAuthentication no
AuthenticationMethods publickey

# Concurrency protection
MaxStartups $MAX_STARTUPS
PerSourceMaxStartups none
MaxSessions $MAX_SESSIONS
LoginGraceTime 120
StrictModes no

# Disable extra features
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PrintMotd no
Banner none
EOF
}

# ---- Start sshd ----
start_sshd() {
  local cfg="$1"
  local log_file="${2:-/dev/null}"
  local extra_opts="${3:-}"

  # shellcheck disable=SC2086
  "$SSHD_BIN" -D -f "$cfg" -E "$log_file" $extra_opts &
  local pid=$!

    # Wait for sshd to be ready
  local waited=0
  while [[ $waited -lt 10 ]]; do
    if "$SSH_BIN" -p "$TEST_PORT" -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null -o BatchMode=yes \
      -o ConnectTimeout=2 "$TEST_USER@$TEST_HOST" \
      -o PasswordAuthentication=no 2>/dev/null exit 0 2>/dev/null; then
            # TCP connectable means ready (auth will fail, that is expected)
      :
    fi
    if kill -0 "$pid" 2>/dev/null; then
      sleep 0.5
      waited=$((waited + 1))
    else
      echo "[ERR] sshd died during startup" >&2
      return 1
    fi
  done

    # Return PID
  echo "$pid"
}

# ---- Stop sshd ----
stop_sshd() {
  local pid="$1"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}

# ---- Verify algorithm negotiation ----
# Verify negotiated transport KEX, hostkey, and userauth match expectations
verify_algorithm_negotiation() {
  local ssh_opts=("$@")
  local log_file
  log_file="$(mktemp /tmp/ssh_verify_neg_XXXXXX)"

  "$SSH_BIN" -vvv "${ssh_opts[@]}" "$TEST_USER@$TEST_HOST" true >"$log_file" 2>&1 || true

  echo "=== Algorithm negotiation debug ==="
  echo "--- KEX ---"
  grep -i "kex: " "$log_file" 2>/dev/null | head -5 || echo "(not found)"
  echo "--- Host key ---"
  grep -i "host key: " "$log_file" 2>/dev/null | head -3 || echo "(not found)"
  echo "--- Userauth ---"
  grep -i "userauth" "$log_file" 2>/dev/null | grep -i "method\|succeed\|fail" | head -10 || echo "(not found)"
  echo "--- Connection reuse ---"
  grep -i "control\|multiplex\|mux" "$log_file" 2>/dev/null | head -3 || echo "(none)"

  rm -f "$log_file"
}

# ---- Build CLIENT_COMMON_OPTS array ----
build_client_opts() {
  local known_hosts="$1"
  local identity_file="${2:-}"
  local kem_identity_file="${3:-}"
  local kem_auth="${4:-yes}"
  local kem_algs="${5:-ML-KEM-768}"

  if [[ "$kem_auth" == "yes" ]]; then
  # KEM mode: align with step3 KEM worker
    cat <<OPTS
-o StrictHostKeyChecking=no -o UserKnownHostsFile=$known_hosts -o BatchMode=yes -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o ConnectTimeout=5 -o KexAlgorithms=mlkem768x25519-sha256 -o HostKeyAlgorithms=$HOST_KEY_ALGS -o PreferredAuthentications=publickey-kem -o PubkeyAuthentication=no -o KEMAuthentication=yes -o KEMAuthAlgorithms=$kem_algs -o IdentityKEMFile=$kem_identity_file -o LogLevel=ERROR -p $TEST_PORT
OPTS
  else
    # Signature mode: align with step3 signature worker
    cat <<OPTS
-o StrictHostKeyChecking=no -o UserKnownHostsFile=$known_hosts -o BatchMode=yes -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o ConnectTimeout=5 -o KexAlgorithms=mlkem768x25519-sha256 -o HostKeyAlgorithms=$HOST_KEY_ALGS -o PreferredAuthentications=publickey -o PubkeyAcceptedAlgorithms=ssh-mldsa-65 -o IdentityFile=$identity_file -o KEMAuthentication=no -o LogLevel=ERROR -p $TEST_PORT
OPTS
  fi
}

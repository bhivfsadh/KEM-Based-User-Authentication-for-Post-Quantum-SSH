#!/usr/bin/env bash
# sshd_test_harness.sh — thin wrapper; canonical version is in backends/
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SRC_DIR/../backends/sshd_test_harness.sh"

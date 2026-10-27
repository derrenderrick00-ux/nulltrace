#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is missing. On Ubuntu: sudo apt update && sudo apt install python3 python3-venv python3-pip" >&2
  exit 1
fi
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Python venv is missing. On Ubuntu: sudo apt install python3-venv" >&2
  exit 1
fi
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
if ! PIP_DISABLE_PIP_VERSION_CHECK=1 .venv/bin/python -m pip install --retries 1 --timeout 15 -e '.[dev]'; then
  echo 'Dependency download/install failed. Verify Internet/DNS and retry this script; no global Python changes were made.' >&2
  exit 1
fi
.venv/bin/python -m nulltrace --strict
.venv/bin/python -m pytest -q

echo
echo "NULLTRACE v1.5.0-rc1 environment ready (GUI acceptance still pending)."
echo "Activate with: source .venv/bin/activate"
echo "Start the game with: python -m nulltrace
Check later with: bash scripts/verify_cinematics_v15.sh"

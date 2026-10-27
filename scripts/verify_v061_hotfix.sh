#!/usr/bin/env bash
# No Nmap scans, packet captures or John audits are run by this automated gate.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  echo "Missing virtual environment. Run: bash scripts/setup_ubuntu.sh" >&2
  exit 2
fi
printf '\n[1/5] Environment diagnostic\n'
"$PY" -m nulltrace --strict
printf '\n[2/5] Syntax checks\n'
"$PY" -m compileall -q src tests
printf '\n[3/5] Automated regression tests\n'
"$PY" -m pytest -q
printf '\n[4/5] Mission catalog\n'
"$PY" -m nulltrace --list-missions | awk 'END { print "Mission records:", NR; if (NR!=100) exit 1 }'
printf '\n[5/5] Offscreen graphical smoke\n'
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PY" -m nulltrace --headless-smoke
printf '\nAUTOMATED GATE PASSED. Perform manual animation and real-tool tests (see docs).\n'

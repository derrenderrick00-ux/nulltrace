#!/usr/bin/env bash
# Non-destructive verification: no live scans or hash audits run automatically.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  echo "Missing .venv Python. First run: bash scripts/setup_ubuntu.sh" >&2
  exit 2
fi
printf '\n[1/4] Phase 0 diagnostic\n'
"$PYTHON" -m nulltrace --strict
printf '\n[2/4] All automated tests\n'
"$PYTHON" -m pytest -q
printf '\n[3/4] Mission catalog count\n'
"$PYTHON" -m nulltrace --list-missions | awk 'END { print "Mission records:", NR; if (NR!=100) exit 1 }'
printf '\n[4/4] Offscreen Pygame smoke (no window)\n'
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PYTHON" -m nulltrace --headless-smoke
printf '\nNON-GRAPHICAL GATE PASSED. Also perform the manual on-device test matrix.\n'

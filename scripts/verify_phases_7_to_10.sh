#!/usr/bin/env bash
# SAFE RELEASE GATE: does not launch scanners, John, TShark, Burp or live HTTP labs.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  echo "Virtual environment missing: bash scripts/setup_ubuntu.sh" >&2
  exit 2
fi
printf '\n[1/6] Environment diagnostic\n'
"$PY" -m nulltrace --strict
printf '\n[2/6] Compile Python sources and tests\n'
"$PY" -m compileall -q src tests
printf '\n[3/6] Unit and integration regression suite\n'
"$PY" -m pytest -q
printf '\n[4/6] Mission catalog\n'
"$PY" -m nulltrace --list-missions | awk 'END { print "Mission records:", NR; if (NR!=100) exit 1 }'
printf '\n[5/6] Offline incident fixture\n'
"$PY" -m nulltrace --lab incident
printf '\n[6/6] Pygame offscreen smoke\n'
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PY" -m nulltrace --headless-smoke
printf '\nAUTOMATED GATE PASSED. Complete on-device Burp and GUI manual tests before acceptance.\n'

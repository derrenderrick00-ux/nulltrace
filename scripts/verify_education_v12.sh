#!/usr/bin/env bash
# No live scanners, packet captures, password audits, or HTTP labs are launched here.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  echo "Python virtual environment not found. Activate and install dependencies first." >&2
  exit 2
fi
printf '\n[1/5] Environment and dependency diagnostic\n'
"$PY" -m nulltrace --strict
printf '\n[2/5] Compile updated source and all tests\n'
"$PY" -m compileall -q src tests
printf '\n[3/5] Original + education regression tests\n'
"$PY" -m pytest -q
printf '\n[4/5] Validate 100 lessons x nine stages\n'
"$PY" - <<'PY'
from nulltrace.core.content import Curriculum
from nulltrace.education.lessons import LessonLibrary
curr=Curriculum(); lessons=LessonLibrary(curriculum=curr)
assert len(curr.missions)==100 and len(lessons.lessons)==100
assert sum(len(l.stages) for l in lessons.lessons.values())==900
print('Catalog: 100 missions; Academy: 100 lessons / 900 stages (PASS)')
PY
printf '\n[5/5] Offscreen Pygame rendering\n'
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PY" -m nulltrace --headless-smoke
printf '\nEDUCATION V1.2 AUTOMATED GATE PASSED. Complete manual GUI and save-compatibility tests before approving release.\n'

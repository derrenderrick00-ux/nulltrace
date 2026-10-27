#!/usr/bin/env bash
# Offline-safe v1.5 gate: no Burp, network scans, packet capture or John subprocesses.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  echo 'Missing .venv Python. Run: bash scripts/setup_ubuntu.sh' >&2
  exit 2
fi
printf '\n[1/6] Environment diagnostic\n'
"$PY" -m nulltrace --strict
printf '\n[2/6] Source compilation\n'
"$PY" -m compileall -q src tests
printf '\n[3/6] Legacy + cinematic + casework regression\n'
"$PY" -m pytest -q
printf '\n[4/6] Content and design contracts\n'
"$PY" - <<'PY'
from nulltrace.core.content import Curriculum
from nulltrace.education.lessons import LessonLibrary
from nulltrace.cinematics.timeline import CinematicLibrary
from nulltrace.investigations.casebook import Casebook
from nulltrace.network.journey import PacketJourney
curr=Curriculum();lessons=LessonLibrary(curriculum=curr)
cinema=CinematicLibrary();cases=Casebook()
assert len(curr.active)==len(lessons.lessons)==100
assert sum(len(l.stages) for l in lessons.lessons.values())==900
assert len(cinema.sequences)==10
assert sum(len(s.beats) for s in cinema.sequences.values())==50
assert len(cases.cases)==10
assert all(PacketJourney(ch).hops for ch in range(1,11))
print('PASS: 100 missions / 900 stages / 10 cinematic sequences / 50 beats / 10 cases / 10 network scenarios')
PY
printf '\n[5/6] Legacy offline synthetic incident fixture\n'
"$PY" -m nulltrace --lab incident
printf '\n[6/6] Pygame 3-frame SDL offscreen smoke\n'
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PY" -m nulltrace --headless-smoke
printf '\nV1.5 AUTOMATED GATE PASSED. On-device manual UI, case-save, cinematics, and real lab regression required before release approval.\n'

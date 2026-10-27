# NULLTRACE Phase 0 — Validation Report

**Date:** 2026-10-26  
**Location:** Isolated build environment (not the user's Ubuntu laptop)

## Passed

- `bash -n scripts/setup_ubuntu.sh` — syntax valid.
- `python3 -m compileall -q src tests scripts/window_smoke_test.py` — Python files compile.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 3/3 passed.
- `PYTHONPATH=src python3 -m pytest -q` — 3/3 passed.
- `PYTHONPATH=src python3 -m nulltrace` — read-only diagnostic executed.
- Catalog integrity: exactly 100 mission records, unique IDs, valid prerequisite links and references in master Markdown.
- Master document: 28 numbered major sections.

## Not validated here

- Full `pip install -e '.[dev]'` including Pygame-CE download, because the isolated build environment cannot resolve the Python package index DNS. The installer now uses bounded retries and provides a clear failure message.
- Pygame GUI smoke test because Pygame-CE is not installed in this build environment.
- Installation on the user's own Ubuntu/Windows machines. This must be verified locally.
- Any actual game, lab adapter or story scene execution: none has been implemented in Phase 0.

## Expected user-local verification

```bash
cd ~/Documents/nulltrace
bash scripts/setup_ubuntu.sh
source .venv/bin/activate
python -m nulltrace --strict
python -m pytest -q
python scripts/window_smoke_test.py
```

**Acceptance:** diagnostics find pygame-ce, the three current starter tests pass, and the optional smoke window renders successfully in an active desktop session.

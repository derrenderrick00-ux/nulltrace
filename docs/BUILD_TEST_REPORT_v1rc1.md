# NULLTRACE 1.0.0-rc1 — Build & Integration Test Report

**Scope:** Phases 7–10 development candidate. **Not** approval of stable production v1.0.

## Validation performed in build environment

- Python source compilation: passed.
- Bash syntax (`bash -n`) for installer/verification scripts: passed.
- `pytest`: **51 passed, 3 skipped**. Skips are graphical Pygame tests because this build environment does not have pygame-ce installed. All three must be rerun on Ubuntu where pygame-ce is installed.
- Full campaign integrity: **100 catalog records, 100 individually graded assessments**, and complete prerequisite progression when the designated synthetic lab fixtures and Chapter 10 disclosure choice are supplied.
- Retained content: original 70 assessments unchanged in meaning/data.
- Stage 7: A real local **127.0.0.1** HTTP server was started during tests; basic requests, manual completion header, 404, 405, receipt confirmation, malformed/expired receipt and clean shutdown passed. **Burp Suite GUI itself was not tested in build environment.**
- Stages 8–10: offline dossier hash, timeline order, contradiction, tamper rejection, choice gate, ending outcomes, Markdown report, save and idempotent progression passed.
- `python -m nulltrace --lab incident`: returned `offline (pass)`.
- `python -m nulltrace --lab web` with no manual request: correctly returned `pending (failed)`; this is expected before the localhost exercise is completed.
- Runtime Nmap, TShark, John have not been rerun in this isolated environment; the prior v0.6.1 adapters are retained as verified by the user's Ubuntu command output.

## Pending before release acceptance

1. Graphical/UI tests on Ubuntu: `bash scripts/verify_phases_7_to_10.sh` — all tests should run with pygame-ce and no skipped cases.
2. On-device manual use of Burp Suite Community Proxy/Repeater against the printed local portal URL, with request receipt and Chapter 8 grading.
3. Manual examination of Chapters 9–10 briefing screens, completion of normal-mode progression, and confirmation of all three endings using isolated test profiles.
4. User-saved progress restart and migration check (SQLite schema unchanged).
5. Resource use/accessibility and Windows source/binary release QA.
6. Design-fidelity gap review: 100 complete nine-stage interactive lessons, cinematics, artwork, and other production features remain outside this RC scope.

**Gate:** Automated source-code acceptance *candidate*. Mark Phases 7–10 complete only after the specified on-device checks, and do not claim full production v1.0 until major outstanding master-design items are implemented and tested.

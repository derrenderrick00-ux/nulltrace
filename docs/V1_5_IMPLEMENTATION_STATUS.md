# NULLTRACE v1.5.0-rc1 — Implementation and Gap Audit

| Feature | Delivered in this package | Remaining limitations |
|---|---|---|
| v1.3 timeline engine | Yes; deterministic pause/next/prev/restart/tick | No camera postprocessing or voice acting |
| v1.3 procedural environments | Yes; 5 themed 2D environments | Not commissioned illustrated backgrounds |
| v1.4 campaign cinematics | Yes; 10 chapters × 5 captioned beats = 50 beats | Short scenes, not full feature-film cutscenes |
| v1.4 customizable protagonist | Yes; name/codename substituted, appearance drawn | Only existing 3 procedural outfits; no speech audio |
| v1.5 interactive evidence cases | Yes; 10 independent synthetic cases requiring supporting records | Not a free-form graph case board or 100 custom cases |
| v1.5 trace simulator | Yes; 10 deterministic scenario labels, gateway fault/recovery, manual/auto navigation | Conceptual transit, not real PCAP replay or full TCP state machine |
| v1.5 SQLite compatibility | Yes; additive `case_reviews` table; per-player idempotent records | Existing legacy saves need user acceptance |
| Prior 100 missions and 900 Academy stages | Preserved | Existing mini-projects remain partly reflective/quiz based |
| Prior security tool labs | Unmodified | Manual real-tool regressions recommended on Ubuntu |
| Desktop packaging | Python source ZIP and setup scripts | Standalone executable packaging and Windows acceptance outstanding |
| Automated regression | 98 passed / 6 Pygame skips in authoring runner | 6 GUI checks still require owner Ubuntu run |

**Release classification:** Functional educational + cinematic prototype candidate; not a finished high-budget cinematic game.

# NULLTRACE — Developer & Maintainer Manual

**Version:** v1.5.0-rc1  
**Primary audience:** Python contributors, QA maintainers, educators and future port developers  
**Canonical design:** `docs/NULLTRACE_Master_System_Design_v1.5.md`  
**Current delivery:** Full-source release candidate, not signed native binaries.

## 1. Clone / download, prerequisites, and local development

- The project repository is `https://github.com/derrenderrick00-ux/nulltrace.git` (project owner's GitHub). Checkout the v1.5 feature branch **only after it has been pushed**; otherwise start from the verified v1.2 branch.
- Alternatively download the full-source `NULLTRACE_v1.3-v1.5_Cinematic_Investigations_Upgrade.zip` and extract it directly into a project root. The ZIP does not contain `.git`, `.venv`, user data or generated caches.
- Requirements: Python 3.10–3.15 per `pyproject.toml` (owner uses 3.14.4), working Pygame-CE 2.5.8, `pytest>=8,<10`, Git and system's Python virtual environment support. Desktop GUI/SDL2 needed for visible testing; Ubuntu first, Windows secondary.

Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git unzip
cd ~/Documents/nulltrace
bash scripts/setup_ubuntu.sh
source .venv/bin/activate
bash scripts/verify_cinematics_v15.sh
python -m nulltrace
```

Windows PowerShell:

```powershell
Set-Location "$HOME\Documents\nulltrace"
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m nulltrace
```

A more targeted developer loop is `python -m pytest -q tests/test_cinematic_investigations_v15.py` followed by GUI interaction testing.

## 2. Source layout and ownership

```text
nulltrace/
├── src/nulltrace/
│   ├── core/                 # Mission catalog / session
│   ├── education/            # 100 nine-stage lesson records and validation
│   ├── cinematics/           # v1.3 timeline state and 2D environment drawings
│   │   ├── timeline.py
│   │   └── sets.py
│   ├── investigations/       # Dossier and v1.5 evidence-case grader
│   │   ├── casebook.py
│   │   └── report.py
│   ├── network/              # v1.5 offline packet-journey state + legacy simulator
│   ├── persistence/          # SQLite migrations and per-player state
│   ├── labs/                 # Existing bounded real-tool adapters
│   ├── story/                # Chapter summaries / endings
│   ├── ui/                   # Pygame Game, scene routing, sprite animation
│   └── launcher.py           # CLI entry point
├── content/
│   ├── cinematics/chapter_beats.json     # 10 x 5 = 50 beats
│   ├── investigations/casebook.json     # 10 cases
│   ├── lessons/lesson_stages_01_10.json  # 100 x 9 = 900 stages
│   └── missions/                      # Original 100 stable mission IDs and assessments
├── lab_assets/                   # Synthetic lab data (never private credentials)
├── scripts/                      # Setup, verification, fixture generation
├── tests/                        # Regression and optional SDL smoke tests
└── docs/                         # Master, user/dev manuals, acceptance
```

The **modular-monolith boundary** is deliberate: cinematic content does not execute shell commands, network simulations never contact devices, and lab adapters are only invoked by explicit lab commands or user interactions. `src/nulltrace/ui/app.py` is currently a large orchestration module; future refactors should move page rendering into scoped controllers without changing campaign IDs or persistence APIs.

## 3. Runtime data flow

1. `launcher.main()` parses explicit CLI flags; default starts `ui.app.run_game()`.
2. `Game` constructs `Store`, `Curriculum`, `LessonLibrary`, `CinematicLibrary`, `Casebook`, and state controllers.
3. `Game` selects an existing player or opens character creation; `Session` handles mission progress.
4. `Game.navigate()` changes screen; `render()` calls the corresponding `draw_<screen>()` method; `handle()` dispatches user input; `update()` advances animation timers.
5. Original mission assessments and real tool checks retain their pre-v1.3 semantics. The new casework has a **separate** per-player completion table.

No web backend, cache server or arbitrary executable mission scripts are required. Contents under `content/` are declarative JSON only.

## 4. Cinematic module (v1.3/v1.4)

`CinematicLibrary` reads and validates `content/cinematics/chapter_beats.json`:

```json
{
  "schema_version": 1,
  "chapter": 1,
  "location": "Meridian apartment",
  "environment": "apartment",
  "beats": [
    {"speaker": "SYSTEM", "shot": "establish", "duration_ms": 3500,
     "text": "YEAR 2038 // A fictional opening line long enough for a scene."}
  ]
}
```

The **actual chapter records contain at least four beats**; the snippet above is illustrative, not a valid entire sequence. Exactly ten sequences are required, chapter 1–10. Allowed environments: `apartment`, `operations`, `archive`, `datacenter`, `mirror`; allowed shots: `establish`, `dialogue`, `close`, `console`, `reveal`; fixed uppercase speaker identities are validated. Each beat duration must be between 1000 and 20000 ms. Only `{name}` and `{codename}` replacement tokens are permitted. **Do not add Python expressions or Python eval to scene content.**

`Timeline` tracks `index`, `elapsed_ms`, `playing`; time step `tick(dt)` clamps dt to .25 s and advances at most one beat each time. Supports `advance()`, `previous()`, `restart()`, auto play and manual subtitle controls. `cinematics.sets.draw_set()` draws procedural, bounded Pygame scenery for five reusable environments; no external images or network requests. `Game.draw_cinematic()` draws selected player appearance using the existing operator sprite.

A story beat does **not** automatically award a mission, change relationships, or execute tool commands. Future scene triggers must use a reviewed, explicit event schema and regressions.

## 5. Evidence investigation module (v1.5)

`Casebook` loads `content/investigations/casebook.json` into ten frozen `Case` records. Each case contains `id` (`CASE-CH01` through `CASE-CH10`), chapter, title, briefing, 3–8 evidence artifacts, three conclusions, `correct_index`, and at least two required supporting evidence IDs.

`CaseSession` manages temporary `selected` evidence and a `conclusion`. `assess()` rejects a missing conclusion, a wrong conclusion, or a correct conclusion submitted without required evidence. Only when the session returns success does `Game._submit_case()` call `Store.record_case()` outside QA mode. **Do not call the store method directly from unvalidated imported content.**

Casework is an additional formative practice system. It does not change original assessment unlock rules and must not claim that a completed case constitutes professional incident-response competence. Distinguish `observation`, `claim` and `limitation` explicitly.

## 6. Network packet-journey simulator (v1.5)

`network.journey.PacketJourney` defines ten fixed chapter scenarios and uses `network.simulator.HOSTS`, all synthetic RFC1918 example addresses. `hops` expose `label`, `address` and a note; `step()`, `tick(dt)`, `reset()`, and `toggle_gateway()` support manual and timed advancement.

Turning the gateway off stops the displayed route at gateway; it does not disable an actual computer's connection. `journey.py` MUST remain free of `subprocess`, `socket`, and packet-sniffing calls. If later adding PCAP playback, keep it distinct from simulation and explicitly label capture provenance.

## 7. Persistence and migration

`Store` uses SQLite (`~/.local/share/nulltrace/campaign.sqlite3` by default, overridden by `NULLTRACE_SAVE_DIR`). It stores players, mission attempts/completion, story decisions, evidence, lesson stages and field notes. v1.5 adds:

```sql
CREATE TABLE IF NOT EXISTS case_reviews (
  player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  case_id TEXT NOT NULL,
  conclusion INTEGER NOT NULL CHECK(conclusion BETWEEN 0 AND 2),
  evidence_json TEXT NOT NULL,
  recorded_at INTEGER NOT NULL,
  PRIMARY KEY(player_id, case_id)
);
```

Migration is additive, old tables are neither dropped nor rewritten. Writes use transactions and `INSERT OR IGNORE` so case completion is idempotent. QA case completion is held in memory and not written. Regression `test_case_progress_additive_migration_and_profile_isolation` exercises two independent profiles and a reopen.

Before altering persistence, back up existing saves, write tests on an old-schema fixture, and avoid destructive migrations.

## 8. Security boundaries

- Terminal UI is explicitly simulated and does not pass commands to a system shell.
- Nmap only targets its game-created `127.0.0.1` listener under bounded execution.
- TShark reads an offline supplied capture using standard input where needed; no automatic sniffing.
- John audits generated synthetic training hashes in an isolated temporary home.
- Burp exercises use a local loopback training portal with fictional records.
- Scene content and case JSON are read-only data; no arbitrary scripts or command templates.
- Malformed content is rejected at load time. Never merge a content loader that interprets arbitrary Python.
- User saves, `.venv`, `.env` and local backups are excluded from source archives and Git.

Verify optional labs separately on the actual Ubuntu computer before accepting changes to adapters. Do not run real-tool integrations in ordinary unit-test CI.

## 9. Tests and release gates

Run:

```bash
python -m compileall -q src tests
python -m pytest -q
bash scripts/verify_cinematics_v15.sh
```

**Build-environment result at authoring:** 98 passing tests, six skips requiring Pygame. **Expected on a working Pygame Ubuntu host:** 104 tests passed, 0 skipped *if all new GUI tests pass*. This is an expectation, not a verified Ubuntu result.

The verifier executes strict environment diagnostics, Python compilation, regression tests, catalog/cinematic/casebook/journey coverage, and a 3-frame SDL dummy driver smoke test. The developer still must perform real GUI acceptance (all screens, controls, long text, save migrations, QA isolation, scene navigation, reduced motion). Full checklist: `docs/V1_3_TO_V1_5_ACCEPTANCE.md`.

Release gates:

| Release | Required demonstration |
|---|---|
| v1.3 | Timeline + five scene sets, manual controls, reduced motion |
| v1.4 | Chapter-specific cinematic content in Chapters 1–10, profile substitution |
| v1.5 | Ten casework tasks, ten packet-journey scenarios, migration, manual GUI acceptance |

Only tag `v1.5.0` after the owner approves release acceptance; the ZIP itself is `v1.5.0-rc1`.

## 10. Git workflow for user-owned repository

The user has pushed `feature/education-v1.2` at commit `d4a67db`. Build on top of it rather than assuming it has merged to `main`:

```bash
cd ~/Documents/nulltrace
git switch feature/education-v1.2
git status --short
git switch -c feature/cinematics-v1.5
# Extract approved upgrade ZIP, then test.
git add README.md CHANGELOG.md pyproject.toml \
  content/cinematics content/investigations \
  src/nulltrace/cinematics src/nulltrace/investigations/casebook.py \
  src/nulltrace/network/journey.py src/nulltrace/persistence/store.py \
  src/nulltrace/ui/app.py tests/test_cinematic_investigations_v15.py \
  scripts/verify_cinematics_v15.sh docs/USER_MANUAL_v1.5.md \
  docs/DEVELOPER_MANUAL_v1.5.md docs/NULLTRACE_Master_System_Design_v1.5.md \
  docs/V1_3_TO_V1_5_ACCEPTANCE.md docs/V1_5_IMPLEMENTATION_STATUS.md

git diff --cached --check
git commit -m "feat: add cinematic scenes and evidence investigations (v1.5 rc1)"
git push -u origin feature/cinematics-v1.5
```

If `git status` shows a stray untracked file with a confusing name, inspect it and leave it out of the explicit `git add` command. Never force-push or run `git clean -fdx` to fix a typo. GitHub PR should target whichever parent branch currently includes v1.2; review PR diff and automated results before merging to `main`.

## 11. Adding content safely

**New cinematic scene:** Validate speaker/shot/environment/duration; write concise dialogue with only supported tokens; add tests; keep scene count or update contract only in a versioned release.  
**New case:** Add synthetic evidence, distinguish observation from inference, provide one defensible conclusion and two directly supporting records; extend schema and automated tests first.  
**New packet scenario:** Extend `SCENARIOS` without adding socket/network calls; demonstrate appropriate protocols and routing limitations.  
**New Pygame screen:** Add `draw_<page>` and a navigation entry from an existing screen; include button coordinates within the 1180 × 720 logical canvas; provide keyboard alternatives and offscreen smoke tests.  
**New save state:** Use additive SQLite migration + two-player isolation tests; preserve old saves.

## 12. Coding-quality concerns and future refactors

`ui/app.py` remains large and uses direct button callbacks. Before a major refactor, introduce scene presenters and layout components gradually with snapshots and behavioral tests. Educator-authored lesson stages reuse a mission knowledge-check rather than independent mastery evaluation; the grading and lab-success distinction should be preserved. Keep animations scalable and expose reduced-motion options. Avoid copyrighted movie assets or claims that film characters are licensed.

## 13. Future modification roadmap

See the updated Master System Design v1.5 for versioned scope. High-priority next areas are unique simulations beyond chapter-level packet journeys, fully assessed nine-stage mini-projects, sprite sheets and professional art, voice accessibility, detailed interactive case boards, more UI accessibility, robust Windows packaging, and eventually instructor authoring. Multiplayer, AI mentors, cloud accounts and 3D environments remain optional later-stage designs requiring independent security reviews.

---
**Maintenance rule:** The master specification describes intended behavior; tests and implementation inventory distinguish what has actually shipped. Never mark a requested feature complete solely because a quiz, placeholder animation or smoke test exists.

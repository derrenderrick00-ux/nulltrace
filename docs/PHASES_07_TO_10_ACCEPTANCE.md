# NULLTRACE Phases 7–10 — Acceptance Test Matrix (v1.0.0-rc1)

**Acceptance principle:** Automated tests passing ≠ the game release being production-complete. These are *developer release gates*. Do not mark a phase finished until its manual tests pass on Ubuntu. The core Pygame app is offline and saves locally; the Burp teaching lab is an explicitly started **local** web server. Keep v0.6.1 backups until acceptance is complete.

## A. Back up and install

```bash
cd ~/Documents
mkdir -p nulltrace-backups
tar --exclude='nulltrace/.venv' -czf nulltrace-backups/source_before_v1rc1.tar.gz nulltrace
if [ -f ~/.local/share/nulltrace/campaign.sqlite3 ]; then
  cp -a ~/.local/share/nulltrace/campaign.sqlite3 nulltrace-backups/campaign_before_v1rc1.sqlite3
fi
unzip -o ~/Downloads/NULLTRACE_Phases_7_to_10_v1.0.0-rc1.zip -d ~/Documents/nulltrace
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

**Expected:** `Successfully installed nulltrace-game-1.0.0rc1`. Do not delete `.venv`, old SQLite save files or the existing project. If you use `NULLTRACE_SAVE_DIR`, back up that directory instead of assuming the default location.

## B. Automated regression gate (safe)

```bash
bash scripts/verify_phases_7_to_10.sh
```

Expected in Ubuntu:

- `--strict` reports Python/Pygame/pytest installed.
- Python compilation passes.
- All tests pass with **0 skipped** when pygame-ce is installed.
- Mission list says **100 records**.
- Offline incident lab returns `Synthetic NEXUS incident review: offline (pass)`.
- Offscreen Pygame smoke says `PASS (3 frames)`.
- The script does **not** run Nmap, John, TShark, Burp or live HTTP labs.

**Failure response:** Save the complete terminal traceback. If it is dependency-related, activate the project `.venv` and rerun `python -m pip install -e '.[dev]'`. If it is a game test failure, do not approve the release or reset campaign saves.

## C. Phase 7 — Web security (v0.7 scope)

- [ ] **C7-01:** `python -m nulltrace --web-lab` prints a `127.0.0.1:<random-port>` URL; visiting `/` shows the synthetic training portal. It must not bind to `0.0.0.0`.
- [ ] **C7-02:** A normal request to `/training/case?case=alpha` returns `case=alpha`, `owner=analyst-a`. Unknown cases return HTTP 404. POST returns 405.
- [ ] **C7-03:** In Burp Suite Community, use the local browser/Proxy then Repeater to change `case=alpha` to `case=mirror`; add `X-Nulltrace-Review: authorized`. The controlled fixture returns the alternate synthetic case.
- [ ] **C7-04:** `python -m nulltrace --lab web` before the modified request reports **pending**; afterward reports **local-http (pass)**, explicitly stating Burp itself is not verifiable.
- [ ] **C7-05:** Use `python -m nulltrace --qa`; access each Chapter 8 mission and check all ten teaching notes/knowledge checks render. Four marked web-lab missions must not pass until the local receipt exists.
- [ ] **C7-06:** Stop the web server with `Ctrl+C`. Verify the game still launches without the server. Mission progress remains intact after restart.

**Phase 7 acceptance:** C7-01 through C7-06 pass. Success from `--lab web` alone is insufficient to claim the manual Burp exercise was completed.

## D. Phase 8 — Final chapters and story (v0.8 scope)

- [ ] **C8-01:** Chapter chooser shows Chapters **1–10** and missions **CH08-M01 through CH10-M10** with stable IDs. Locked missions cannot be completed before prerequisites in normal mode.
- [ ] **C8-02:** Chapters 9 and 10 open their story briefings without errors. All 20 assessments have correct/incorrect feedback, and all 20 teaching notes render.
- [ ] **C8-03:** `python -m nulltrace --lab incident` reports **offline (pass)**, a synthetic timeline and a conflict involving `MI-07` and `IS-21`; it does **not** prove intent.
- [ ] **C8-04:** In Chapter 10's Story Archive, choose a disclosure route. Attempting CH10-M10 without a route must refuse final completion; after a route is selected, it can be completed with prerequisite and lab conditions satisfied.
- [ ] **C8-05:** After completing the final mission, click **NEXT MISSION** and observe a story ending. Oversight route with all 10 chapter evidence items → `THE RECKONING`; broad → `THE BLACKOUT`; restricted → `THE SILENT PROTOCOL`.
- [ ] **C8-06:** From the Evidence Board, use **EXPORT TRAINING DOSSIER** and inspect the generated Markdown. It should contain source identifiers, SHA-256, findings and limitations, not unqualified claims of real wrongdoing.
- [ ] **C8-07:** Restart the game. Confirm the chosen ending, evidence and campaign progress are preserved.

**Developer shortcut:** `python -m nulltrace --qa` unlocks chapter previews and all assessments without saving mission completions or story decisions. It cannot be used to certify persisted final-campaign progress; complete normal-mode progression for that gate, or use an isolated test database via `NULLTRACE_SAVE_DIR`.

**Phase 8 acceptance:** All C8 tests pass. Full cinematic art and voice work are deferred features, not implicitly accepted.

## E. Phase 9 — Stabilization

- [ ] **C9-01:** All automated tests pass on Ubuntu (`python -m pytest -q`); note the exact count and any skips.
- [ ] **C9-02:** Legacy v0.6.1 player profile and Chapter 1–7 mission completions load unchanged (no new SQLite schema columns or migrations).
- [ ] **C9-03:** Changing profiles does not mix evidence, endings or mission completions.
- [ ] **C9-04:** Invalid answer input never unlocks missions; repeat valid completion does not grant duplicate completion rows.
- [ ] **C9-05:** `--lab packet`, `--lab nmap`, `--lab john` still work in the user's environment; record whether each runs in real or simulated mode. These integrations previously passed on Ubuntu, but this upgrade must not regress them.
- [ ] **C9-06:** Start/stop the web server several times. It releases its ephemeral port; game remains responsive and no external targets are accessed.
- [ ] **C9-07:** Exercise the UI at 1180×720 and a smaller window, mission navigation, animated hoodie character and the new ending screens. No crashes, severe overlaps, or illegible key controls.
- [ ] **C9-08:** Test failed/missing tools, invalid evidence files, and tampered or expired local receipt; failures must not be reported as real successful exercises.
- [ ] **C9-09:** Test app close and reopen after completing a chapter; campaign progress survives.

**Phase 9 acceptance:** All critical issues fixed or documented with explicit sign-off. This build still has a content-quality gap versus the full nine-step teaching method; stabilization does not erase it.

## F. Phase 10 — Release engineering

- [ ] **C10-01:** Check `python -m pip show nulltrace-game` shows `1.0.0rc1`, app boots from `.venv` and `--list-missions` prints 100.
- [ ] **C10-02:** Verify the release ZIP has no `.venv`, `__pycache__`, personal SQLite saves, environment files, secrets or OS-only temporary data.
- [ ] **C10-03:** Source installation on Ubuntu, documented tests, and troubleshooting steps are reproducible from a fresh project copy.
- [ ] **C10-04:** Run equivalent smoke tests on Windows before advertising Windows support. Build Windows binaries on Windows, not on Linux.
- [ ] **C10-05:** Assess the master-design gap audit. Features not yet implemented—full cinematic story, complete nine-step lessons, advanced accessibility—must remain **open**, and the label stays `release candidate`.

**Phase 10 acceptance:** Source release candidate can be signed off after source tests and manual checks; a **stable v1.0 production release is NOT accepted** while major master-design requirements remain incomplete.

## G. Simple acceptance record

| Gate | Automated | Manual Ubuntu | Status |
|---|---|---|---|
| Phase 7 local web lab | Unit/integration tests | C7-01…06 | PENDING |
| Phase 8 final campaign | 100-mission regression | C8-01…07 | PENDING |
| Phase 9 stabilization | Regression + app smoke | C9-01…09 | PENDING |
| Phase 10 source release | ZIP manifest + documentation | C10-01…05 | PENDING |

When sharing results, report *which steps passed*, the precise failing command or screen, and tool execution mode. A simulated fallback is not the same as a passed real-tool integration.

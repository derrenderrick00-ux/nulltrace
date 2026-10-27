# NULLTRACE v1.3–v1.5 — Ubuntu Acceptance Matrix

**Build:** v1.5.0-rc1 • **Status:** Awaiting user verification.  
**Prior approved baseline:** v1.2.0-rc1, 62 passing Ubuntu automated tests.  
**Authoring-environment validation:** 98 tests passed and 6 Pygame-dependent tests skipped.  
**Expected on your Ubuntu Pygame environment:** 104 passing tests if all graphical checks succeed.

## Phase A — Automated verification

- [ ] `bash scripts/verify_cinematics_v15.sh` exits zero.
- [ ] `python -m pytest -q` reports 104 passed, no skips (count may increase with subsequent tests).
- [ ] `python -m nulltrace --strict` reports Python 3.14.4, Pygame and pytest importable.
- [ ] `python -m nulltrace --headless-smoke` passes on SDL dummy driver.
- [ ] Content counts: 100 missions, 100 lessons, 900 Academy stages, 10 cinematic sequences/50 beats, 10 evidence cases, 10 packet-journey scenarios.

## Phase B — Existing save and training safety

- [ ] Backup source and `~/.local/share/nulltrace/campaign.sqlite3` before installing.
- [ ] Open the existing Alex/Ghost operator and verify completed missions and Academy stages remain.
- [ ] Launch Chapter 1 and Chapter 10 Academy lessons; original assessment and labs still open.
- [ ] Run existing Nmap, TShark, John and Burp labs as needed after code changes; do not claim simulation fallback as real integration success.
- [ ] `--qa` runs without storing new mission completions, Academy stages, or case completions.

## Phase C — v1.3 Cinematic engine

- [ ] Story Archive → WATCH CINEMATIC opens a scene, no exception.
- [ ] NEXT changes speaker/subtitle; PREV reverses a beat; RESTART returns to first beat.
- [ ] AUTO PLAY advances one beat at a time; PAUSE stops; last beat stops automatically.
- [ ] Press Space to advance, R to restart, M to toggle reduced motion.
- [ ] Alex/Ghost custom codename is substituted in operator dialogue; a second name also works.
- [ ] At least one five-location procedural environment draws correctly and title text remains readable.

## Phase D — v1.4 All-chapter narrative integration

- [ ] Repeat cinematic test for chapters 1, 5, 8 and 10.
- [ ] Use QA to inspect all ten chapters without altering normal saves.
- [ ] Scene content is distinct for all chapters (not identical placeholders).
- [ ] Return to Story Archive after cinematic playback without losing chapter selection.
- [ ] Existing Story Archive choices and final ending options still work.

## Phase E — v1.5 Interactive evidence cases

- [ ] Story Archive → OPEN CHAPTER CASE opens the selected chapter's case.
- [ ] Trying VERIFY without a conclusion gives feedback, no completion.
- [ ] Selecting a correct conclusion without the supporting evidence fails with a request for records.
- [ ] Selecting a false allegation fails even when records are selected.
- [ ] Selecting the correct conclusion and required records yields PASS.
- [ ] Restart the game: the case remains verified only on that operator profile.
- [ ] Select a second operator: its case progress stays independent.
- [ ] Chapter mission completion counts do not change when only casework is completed.

## Phase F — v1.5 Packet Journey

- [ ] Network Map → PACKET JOURNEY opens the illustrative animated route.
- [ ] STEP highlights the next hop; RESET returns to the source.
- [ ] AUTO PLAY proceeds to endpoint and stops; pause works.
- [ ] GATEWAY ON/OFF demonstrates simulated route disruption and restoration.
- [ ] Journey labels clearly state the visualization is simulated (not live traffic).
- [ ] Test Chapters 3, 5 and 10 with different scenario labels.

## Phase G — Layout, accessibility and shipping

- [ ] No text or button is unintentionally clipped at 1180 × 720 logical size.
- [ ] Windows can be resized without losing mouse click accuracy.
- [ ] Buttons and subtitles remain readable; cinematic view does not block mission navigation.
- [ ] Reduced-motion choices prevent time-based cinematic autoplay when enabled.
- [ ] No user database, `.venv`, `.env` or `.git` bundled in the distributable ZIP.
- [ ] The User Manual and Developer Manual match actual commands and limitations.
- [ ] Commit and push to **`feature/cinematics-v1.5`** only after acceptance.

## Release decision

Approve v1.3 / v1.4 / v1.5 **individually** based on the relevant sections above. A passing automated suite alone is insufficient. Document failures by screen, chapter, command and terminal traceback. Defer the native Windows binary, voice-over, licensed art assets and 100 distinct interactive mini-projects to future milestones instead of claiming them as delivered.

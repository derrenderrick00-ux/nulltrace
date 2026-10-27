# NULLTRACE — Phases 1–6 Test and Acceptance Matrix

**Build:** v0.6.0 development release (user acceptance pending)  
**Target:** Ubuntu 26.04, Python 3.14.4, pygame-ce 2.5.8, ThinkPad X280 (8 GB)  
**Scope:** 70 assessment-backed missions in Chapters 1–7; core 2D desktop UI, simulation, offline packet fixture, localhost Nmap, synthetic John exercise.

**Approval rule:** NO phase is marked accepted merely because a Python test passes. Run both automatic tests and the relevant manual tests on the target laptop, report failures, and then approve each phase. The eventual Master System Design remains the scope authority. This release is a functional learning/gameplay **prototype**; richer scenes, animated packet movement, detailed command-by-command tasks, full cinematic sequences and all 100 fully authored lessons are not in this build.

## A. Automated gate (must pass before manual tests)

From `~/Documents/nulltrace` with the virtual environment installed:

```bash
source .venv/bin/activate
bash scripts/verify_phases_1_to_6.sh
```

**Expected:**
- `--strict` environment diagnostic succeeds, Pygame and pytest available.
- At least 29 pure-Python tests pass; graphical tests are NOT skipped on your machine (Pygame installed).
- 100 mission records reported; exactly 70 are available in v0.6.
- Headless Pygame three-frame check passes.
- No real Nmap/John exercise is launched by the automated gate.

Also run:

```bash
python -m compileall -q src
python -m nulltrace --list-missions | grep -c PLAYABLE  # expected 70
python -m nulltrace --list-missions | grep -c PLANNED   # expected 30
```

## B. Manual test procedure

Record PASS / FAIL / BLOCKED and attach a short log or screenshot for each failed case. Use a fresh player, **Alex** / **Ghost**, appearance **hoodie**, as the example. You may also create a second profile with other names to verify customization.

### Phase 1 — Foundation and first playable game (`v0.1`)
- [ ] **P1-01 Start:** `python -m nulltrace` opens a resizable game window without tracebacks; controls remain visible at your screen resolution.
- [ ] **P1-02 Create:** Create Alex / Ghost / hoodie. The screen advances to a Chapter 1 story briefing.
- [ ] **P1-03 Customize:** Create another player with different name, codename and outfit. Names display correctly in the header.
- [ ] **P1-04 Invalid input:** Clear either name and try to create a player. Game refuses cleanly; existing saves remain intact.
- [ ] **P1-05 Save/restart:** Exit with window close or Esc; relaunch and select the earlier profile. Its identity survives.
- [ ] **P1-06 First mission:** Complete `CH01-M01` with the correct answer. It records completion and unlocks M02.
- [ ] **P1-07 Wrong answer:** Choose an incorrect option on `CH01-M02`. Feedback appears; M03 remains locked. Retry with the correct answer.
- [ ] **P1-08 Window/control:** Resize, navigate by clicking and Esc, then quit. Game should not freeze or close unexpectedly.
- [ ] **P1-09 Branch:** On the Chapter 1 briefing choose 'Verify evidence first', then restart; the choice is still shown.

**Approval evidence:** Screenshot of opening, saved profile and first mission completed; game restarted successfully.

### Phase 2 — Chapter 1 curriculum (`v0.2`)
- [ ] **P2-01 Beginner order:** Use Recruit guidance; all 10 Chapter 1 lessons, questions and feedback are accessible in progression order.
- [ ] **P2-02 Shell:** In Safe Terminal execute `help`, `pwd`, `ls`, `cd reports`, `cat incident-07.txt`.
- [ ] **P2-03 Shell safety:** Try `rm -rf /` in Safe Terminal. It must be rejected as unsupported; system files remain unaffected.
- [ ] **P2-04 Logs:** `cat /var/log/network.log` shows only fictional event data.
- [ ] **P2-05 Chapter operation:** Complete CH01-M10, verify M02–M10 progress and `mirror07` in Evidence Board.
- [ ] **P2-06 Separate players:** Check a newly created player has **zero** completed missions and no inherited evidence.

**Approval evidence:** 10/10 Chapter 1, terminal log observations, evidence board entry.

### Phase 3 — Chapters 2–4 networking (`v0.3`)
- [ ] **P3-01 Interactive topology:** Open Network Map; select workstation, switch, gateway, fileserver and DNS. Different device IPs display.
- [ ] **P3-02 Route simulation:** Toggle gateway unavailable and restore it. Shown path changes to `GATEWAY_UNREACHABLE` then returns.
- [ ] **P3-03 Terminal:** Run simulated `ip`, `ping fileserver`, `traceroute fileserver`, `dig mirror.training.invalid`.
- [ ] **P3-04 No live traffic:** Verify this screen sends no real packets and is explicitly labeled simulated.
- [ ] **P3-05 Curriculum:** Check Chapters 2, 3 and 4 each contain 10 distinct playable assessments, with clear explanations after answers.
- [ ] **P3-06 Unlock chain:** CH04-M01 stays locked until CH03-M10 is complete in normal mode.
- [ ] **P3-07 Evidence:** After chapter capstones, the Evidence Board reflects the three related observations.

**Approval evidence:** screenshots of both route states, Chapters 2–4 progress, evidence entries.

### Phase 4 — Wireshark / packet analysis (`v0.4`)
- [ ] **P4-01 Bundled capture:** `lab_assets/pcaps/ghost_dns.pcap` opens in Wireshark (or with TShark) and contains 3 packets.
- [ ] **P4-02 Manual query:** Wireshark display filter `dns` reveals `mirror.training.invalid` requests and a synthetic response.
- [ ] **P4-03 Tool command:** `python -m nulltrace --lab packet` displays `real` when TShark exists, including synthetic query names.
- [ ] **P4-04 No sniffing:** Tool runs with `-r` bundled fixture, not a capture interface; doesn't prompt for elevated privileges.
- [ ] **P4-05 Required lab:** In QA mode choose `CH05-M05`, answer first **without** running the lab; mission must reject grading. Click Run Lab, then submit the answer.
- [ ] **P4-06 Report:** Complete the chapter operation in normal progression, then verify packet evidence appears on the board.

**Approval evidence:** TShark output, Wireshark screenshot, in-game lab indicator.

### Phase 5 — Nmap (`v0.5`)
- [ ] **P5-01 Tool command:** `python -m nulltrace --lab nmap` returns `real`, state `open`, target **only** `127.0.0.1`, and a temporary local TCP port.
- [ ] **P5-02 No network scan:** Review that output and confirm no LAN/external IP is targeted. The game must not scan Wi-Fi peers.
- [ ] **P5-03 Repeat:** Repeat the loopback test; it terminates cleanly and doesn't leave a listening process behind.
- [ ] **P5-04 Tool unavailable:** If using a test environment without Nmap, result must clearly state **simulated**, not 'real'.
- [ ] **P5-05 Mandatory lab:** `CH06-M10` requires a successful lab run before its quiz can be completed.
- [ ] **P5-06 Evidence:** Complete Chapter 6; Evidence Board records the controlled management-port observation.

**Approval evidence:** Output confirming 127.0.0.1 / open, progression after lab.

### Phase 6 — John the Ripper (`v0.6`)
- [ ] **P6-01 Synthetic only:** Verify lab uses temporary generated training hashes and a tiny built-in wordlist—not `/etc/shadow` or private files.
- [ ] **P6-02 Tool command:** `python -m nulltrace --lab john` completes in bounded time. Look for `real` when installed John supports `md5crypt`; otherwise review the explicitly marked simulation fallback.
- [ ] **P6-03 Honest mode:** Distinguish **real** versus **simulated** output. A simulation pass is NOT evidence that John integration is verified.
- [ ] **P6-04 Cleanup:** Repeated lab runs leave no training hash/pot files in your personal project or home folder.
- [ ] **P6-05 Mission gate:** `CH07-M07` requires a lab run before the question can pass.
- [ ] **P6-06 Final chapter:** All Chapter 7 assessments are playable; completing CH07-M10 produces weak-training-key evidence.
- [ ] **P6-07 Save/restart:** Quit and relaunch after Chapter 7; all mission completions persist; chapter 8 is labelled PLANNED.

**Approval evidence:** John/simulation output, case board, last mission progress.

## C. Testing advanced content quickly without losing campaign progress

Use the explicit developer/QA mode:

```bash
python -m nulltrace --qa
```

Select or create an operator, open Chapters, select a Chapter 5–7 mission, and test. QA mode unlocks all **existing** Chapters 1–7, but **does not save mission completions or story choices**. Tool labs are still explicit and require pressing **Run Lab**. **Do not** use QA mode to validate normal unlock/save progression; use a regular profile for that.

## D. Negative test matrix

- [ ] **NEG-01:** No shell metacharacters typed in Safe Terminal can execute a system command.
- [ ] **NEG-02:** Unknown simulated devices/paths are rejected without exceptions.
- [ ] **NEG-03:** Missing optional security tools cause truthful fallbacks, not crashes.
- [ ] **NEG-04:** Missing/corrupt PCAP fails clearly and does not change saved progression.
- [ ] **NEG-05:** A wrong answer never awards a mission completion.
- [ ] **NEG-06:** Repeated correct answers never award duplicate completions or evidence.
- [ ] **NEG-07:** Closing a graphical screen then reopening the save does not corrupt SQLite.
- [ ] **NEG-08:** No network target other than 127.0.0.1 appears in actual Nmap process arguments.
- [ ] **NEG-09:** No real private credentials are read for password labs.

## E. Result template

```text
NULLTRACE v0.6 acceptance — Ubuntu
Python:
Pygame:
Automated tests: ___ passed, ___ failed, ___ skipped
Phase 1: PASS / FAIL / BLOCKED — details:
Phase 2: PASS / FAIL / BLOCKED — details:
Phase 3: PASS / FAIL / BLOCKED — details:
Phase 4: PASS / FAIL / BLOCKED — details:
Phase 5: PASS / FAIL / BLOCKED — details:
Phase 6: PASS / FAIL / BLOCKED — details:
Critical errors and tracebacks:
Screenshots / logs:
```

### Acceptance status on delivery

- Automated course, save, network, packet and tool safety tests: **passed in this execution environment**.
- Real Nmap, TShark and John tools: **not installed in the packaging environment**; real runs are **not verified here**.
- Pygame graphical tests: **not installed in packaging environment**; must pass on the user's Ubuntu machine.
- All six phases: **candidate for user testing, not approved or marked complete**.

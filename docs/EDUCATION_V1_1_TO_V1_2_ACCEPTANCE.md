# NULLTRACE v1.1–v1.2 — Educational expansion: acceptance test matrix

**Release:** `1.2.0rc1` (educational enhancement candidate)
**Baseline:** working `1.0.0rc1` 100-mission campaign
**Environment:** Ubuntu, Python 3.14.4, pygame-ce 2.5.8 as used in prior release
**Status:** automated tests verified in build environment; Ubuntu graphical tests and manual acceptance **NOT YET VERIFIED**.

## Implementation and scope

- v1.1 foundation: a declarative, validated nine-stage lesson schema; staged lesson navigation, mission-specific explanations, glossary term, worked example, everyday application, chapter flow model and a **separate** completion record.
- v1.2 expansion: structured nine-stage material for **all 100 missions (900 stage records)**; practice question, interactive hop-by-hop chapter diagram, learner-written field note, cross-mission operation prompt; Academy stage counter by chapter.
- Both releases are packaged together as v1.2.0-rc1. Existing mission assessments, the four earlier lab integrations, story choices and mission IDs have been retained.

### Important learning limitations

This is an **educational content and UI expansion**, not yet a complete animated, hands-on simulation for every lesson. The diagram is a conceptual **chapter-level** data-flow model, not a faithful packet-capture playback or an executable physical network. Many mini-projects use an ungraded reflection/field-note form with optional existing tool labs. Stage 7 practice uses the previously authored mission question, so passing it is practice—not independent verification of mastery. Some topics require further examples, animations, independent practice questions, and richer simulation mechanics in later iterations. The existing final mission assessment and real-lab gates remain authoritative for mission credit. Scene cinematics are still planned for v1.3–v1.5.

## A. Automated tests

```bash
cd ~/Documents/nulltrace
source .venv/bin/activate
bash scripts/verify_education_v12.sh
```

**Accept only if:** strict diagnostic passes; Python compiles; all regression tests pass; 100 missions / 100 lessons / 900 stages are reported; Pygame smoke test passes. On Ubuntu where Pygame is installed, no Pygame tests should be skipped. The build environment independently ran `58 passed, 4 skipped` (Pygame unavailable there); the **expected** on-device count is 62 passed and 0 skipped, subject to actual verification.

## B. Manual Academy UI tests (new profile)

1. Start `python -m nulltrace`. Select or create an operator, e.g. **Alex / Ghost / hoodie**.
2. Open **ACADEMY**. Confirm Chapters 1–10 show counters `0/90` for a newly created profile and global total `0/900`.
3. Open **Chapter 1 → CH01-M01**. The lesson should open at Stage 1, with nine numbered tabs across the top.
4. Use **MARK STAGE COMPLETE** on Stage 1. Confirm the next stage opens and the Academy total becomes `1/900` after returning to Academy.
5. Visit Stages 2 and 3, check the definitions and explanations. For long text, use wheel or **Page Up / Page Down** to scroll.
6. Stage 4: press **NEXT HOP** to highlight the entire illustrated flow, then **RECORD FLOW REVIEW**. Confirm Stage 4 is marked complete.
7. Stage 5: confirm the worked example and the stated interpretive limitation appear. Do **not** expect the examples to run as shell commands.
8. Stage 6: confirm the topic-specific application appears.
9. Stage 7: deliberately select a wrong practice answer; expected feedback without mission credit. Then select the correct answer; expected feedback, recorded Stage 7, no mission credit. Keyboard **1–3** should work here.
10. Stage 8: type fewer than 20 characters and press **SAVE FIELD NOTE**; expect a clear validation error. Type an evidence note such as `Observed an authorized host; uncertainty remains about its service owner.` and save; stage should be marked done.
11. Stage 9: mark complete, then click **MISSION ASSESSMENT**. The existing assessment must open and its original grading and lab requirements must work.
12. Restart the game; reopen the same profile/mission. Stage counter and field note must persist. Repeat with a second profile; the second profile must not inherit the first player's lesson stage progress.
13. In **ACADEMY**, check chapter and global progress counters are correct and do not count completed stage retries twice.
14. Resize the window (e.g. 1024x768) and confirm controls remain clickable, fonts legible, and mouse coordinates scale correctly.

## C. Compatibility: existing v1.0 player

1. Back up `~/.local/share/nulltrace/campaign.sqlite3` (or custom save location) **before installing**.
2. Reopen the pre-existing player after upgrading. Name, codename, appearance, existing completed missions, laboratory records, chapter evidence and story choices must be unchanged.
3. Previously completed missions must still display as completed and remain replayable; their new lesson stages begin unrecorded, rather than auto-awarding 9 stages.
4. Complete one lesson stage, restart, and verify it persists. Complete a real mission assessment; it must not discard the lesson stage progress.
5. Corrupt/too-short field-note inputs should be rejected, not crash the program.

## D. QA mode / course breadth

1. `python -m nulltrace --qa`, select an operator and open CH03-M06, CH05-M04, CH06-M04, CH07-M07, CH08-M08 and CH10-M10.
2. All nine teaching stages should render for each. Diagram and technical examples should match the mission theme; final assessments must still exist.
3. Mark some stages in QA mode; close and launch normal game. The changes must **not** persist in SQLite.
4. For safety, real Nmap operations remain localhost-only; PCAP inspection remains offline; John fixtures remain synthetic; Burp portal remains loopback-only. The education verification script itself must never launch these tools.

## E. Regression gate

- [ ] All automated tests pass with Pygame installed (0 skipped).
- [ ] 100 unique lesson records; nine ordered stages each.
- [ ] Reading lesson stages doesn't award original mission completion.
- [ ] Original Chapter 1–10 assessments still function.
- [ ] Stage 7 wrong/correct feedback works.
- [ ] Stage 8 self-reported note validates and persists.
- [ ] Diagram replay and stage recording work.
- [ ] Existing save/achievements/choices remain unchanged.
- [ ] QA mode never writes lesson progress or notes.
- [ ] No new non-local network or unbounded shell access.
- [ ] GUI displays correctly at normal and resized window sizes.

### Approval decision

`v1.2.0-rc1` remains **candidate/unapproved** until on-device verification is complete. Proceed to design/build v1.3–v1.5 only after this gate passes. Do not tag this build as a stable v1.2 release prematurely.

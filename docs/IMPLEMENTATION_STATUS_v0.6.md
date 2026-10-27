# NULLTRACE — Phase 1–6 Implementation and Gap Audit

**Revision:** v0.6.0 development candidate (2026-10-26)  
**Canonical scope source:** `NULLTRACE_Master_System_Design_v1.0.md`  
**Approval state:** **Not accepted**; target-machine tests outstanding.

## Features delivered in this codebase

| Phase | Implemented and testable | Still requires further implementation / polish |
|---|---|---|
| 1: Foundation | Pygame app shell, home/menu/navigation, custom identity (name/codename/appearance), Chapter 1 prologue summary, first playable assessment, SQLite profiles and progress, screen scaling | Full character sprites, cinematic opening cutscene, advanced focus/accessibility review |
| 2: Chapter 1 | Ten graded mission records, guided lesson/objective screen, retries, prerequisites, terminal grammar, chapter capstone evidence, save/reload | Fully distinct applied exercises for each mission, advanced pedagogical hints, richer narrative investigation |
| 3: Networking Ch2–4 | Thirty graded missions, selectable topology nodes, router-failure toggle, simulated ping/traceroute/DNS, chapter summaries | Animated protocol visualizations and distinct technical validators for every challenge |
| 4: Wireshark Ch5 | Ten graded missions, shipped 3-packet DNS fixture, TShark adapter (read-only PCAP), lab gating on 5 missions, evidence on capstone | Rich TCP/ARP fixtures, guided per-packet UI inspection and varied capture datasets |
| 5: Nmap Ch6 | Ten graded missions, loopback-only temporary TCP service, explicit opt-in `-sT -Pn -p PORT -oX - 127.0.0.1`, XML parser, controlled lab gating on 4 missions | Distinct service inventory scenarios, additional Nmap output interpretation validation |
| 6: John Ch7 | Ten graded missions, temporary synthetic `md5crypt` fixture and tiny wordlist, optional John adapter, explicit simulated fallback, gated lab checks on 4 missions | Cross-build John verification, more password policy labs, deeper format explanations |

## Core rules and interfaces

- Content loader validates 100 IDs, 70 assessments, prerequisites, answer ranges, unique choices and objectives.
- Session enforces chapter sequence and lab-before-assessment gates where defined.
- Store uses SQLite foreign keys, duplicate-safe mission completions and evidence, attempt history, distinct profiles and persisted early story decisions.
- Network simulator uses documentation-only private addresses and does not send packets.
- Safe terminal uses a bounded parser and entirely synthetic filesystem; never sends strings to a shell.
- Nmap and TShark subprocess calls use constant, internally built arguments. Nmap's sole address is 127.0.0.1.
- John runs use temporary files containing fictional credentials and a bounded wordlist.
- The application provides a developer-only QA flag which cannot record progress or story choices.

## What 'playable' means here

For Chapters 1–7 each mission has a learner-facing objective, a separate activity description, one manually authored multiple-choice assessment, correction feedback, and an unlock condition. Some missions additionally require a controlled laboratory run. This is a genuinely navigable and persistent **curriculum prototype**, but it does **not** yet implement every distinct simulator, forensic investigation, evidence-writing exercise, or cinematic scene specified in the GDD. Do not claim it does.

## Safety and authenticity

- A lab reports one of `real`, `simulated` or `unavailable`.
- A simulated run can be sufficient to progress through the current game's conceptual exercises for accessibility, but does **not** demonstrate skill with the actual tool.
- Lab method is stored with mission completion, permitting a later learning-progress audit and replay for real-tool mastery.
- The archive has no real user password dumps, no copied private captures, and no scanner targets outside loopback.
- No software security tool is automatically started during app startup or automated tests.

## Test status on delivery

- 31 Python unit/integration tests pass in packaging environment.
- Two Pygame graphical tests skipped **there** because Pygame is not installed in that isolated environment.
- Real TShark, Nmap, and John weren't installed **there**, so real adapters require Ubuntu user validation.
- The user's Phase 0 Ubuntu logs confirm that Python 3.14.4, pygame-ce 2.5.8, Nmap, TShark, and John are present, but **they have not yet executed this v0.6 code**.

## Future work and acceptance gate

Before production-grade Phase 1–6 completion, replace remaining placeholder-style assessments with deeper mission-specific interactive tasks, fully implement instructional content for every mission, add rich 2D narrative/visual effects, verify external adapters and performance, and demonstrate the entire manual test matrix. These improvements can be delivered as v0.6.x increments. Phase 7 (Burp Suite) and Phases 8–10 remain separate future milestones.

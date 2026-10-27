# NULLTRACE: The Cybersecurity Chronicles
## Master System Design, Architecture & Implementation Specification

| Document control | Value |
|---|---|
| Specification | `NT-SYS-001` |
| Baseline version | `1.0.0` |
| Date | 2026-10-26 |
| Status | **Phase 0 design baseline approved; implementation not started** |
| Product | Offline-first cinematic cybersecurity investigation RPG |
| Initial platform | Ubuntu desktop; Windows compatibility target |
| Engine | Python + pygame-ce |
| Release target | v1.0 complete base game, ten chapters and 100 missions |
| Reference protagonist | Alex / Ghost / street-technician hoodie (**example, never mandatory**) |
| Audience | Absolute beginner through intermediate practitioner |

> **Source of truth.** This file is the primary design reference for all NULLTRACE phases. Its examples specify proposed interfaces and behavior, not delivered software. The companion `content/missions/catalog.json` is the initial structured index of all 100 missions. Implementation may start only after the applicable feature's requirements and tests are understood. Changes to this baseline require a recorded design decision.

---

## Contents

1. Product vision, learning outcomes and success metrics
2. Product boundaries, operating assumptions and non-goals
3. Canonical story universe and truth model
4. Characters, factions and customization
5. Three-act campaign, ten chapters and branching endings
6. Scene system and opening playable vertical slice
7. Learning framework, diagnostics, curriculum and grading
8. Gameplay loops, player UX, accessibility and UI
9. Complete 100-mission implementation catalog
10. Software architecture and component boundaries
11. Data contracts, schemas and versioning
12. Database schema, save semantics and migrations
13. Runtime mission, scene and laboratory state machines
14. Simulation engine and networking model
15. Real security-tool integration strategy
16. Threat model, scope authorization and sandboxing
17. Assets, audiovisual pipeline and content authoring
18. Repository structure and dependency policy
19. Environment setup for Ubuntu and Windows
20. Implementation plan: Phases 0–10
21. Testing matrix, release gates and definition of done
22. Performance budgets, observability and failure recovery
23. Git workflow, maintenance and change control
24. Future expansion architecture and compatibility
25. Risks, limitations and assumptions
26. Phase 0 completion inventory and immediate next steps
27. Acceptance scenarios and example interfaces
28. References and glossary

---

# 1. Product vision and success criteria

### 1.1 Product vision

A player begins as a junior network technician and develops genuine cybersecurity investigative competence by completing an original techno-thriller. Technical understanding is a prerequisite for meaningful progress: players must reason about networks, analyze packet evidence, perform explicitly authorized service inventories, evaluate synthetic password-audit results, and assess controlled web applications. The narrative supplies motivation; the exercises supply transferable knowledge.

**Tagline:** *Every connection leaves a trace. The truth requires evidence.*

### 1.2 Product pillars

1. **Learning first.** A learner can start with no Linux, networking, or security experience.
2. **Evidence over fantasy.** A discovered port is not proof of exploitation; an IP address is not an exact physical location; encrypted TLS application content is not readable without suitable keys or endpoint access.
3. **Narrative integration.** Technical lessons explain the next meaningful investigative decision.
4. **Offline-first.** The campaign, local progress, simulation and mandatory supplied fixtures work without Internet connectivity.
5. **Controlled realism.** The four real tools are used on supplied evidence or laboratory systems; arbitrary networks and real credentials are never scanned or harvested automatically.
6. **Extensibility.** Add content and tool adapters through declared, versioned interfaces.
7. **Low-resource compatibility.** Target an 8 GB RAM dual-boot development laptop; sophisticated visuals must not be required for educational correctness.

### 1.3 Learner capabilities on completion

A graduate of the in-game curriculum should be able to:

- Navigate basic Linux commands, files, permissions and logs.
- Explain Ethernet, IPv4/IPv6, subnetting, DHCP, DNS, ARP, TCP, UDP, NAT, routing, ICMP, HTTP and TLS at an introductory practical level.
- Troubleshoot fictional and controlled network connectivity failures.
- Read supplied `.pcapng` captures with Wireshark and TShark; correlate endpoints, filters, timestamps and protocol behaviors.
- Read and, on a bounded local target, generate authorized Nmap results; distinguish observed exposure from a verified vulnerability.
- Explain salted password hashing; safely use John the Ripper on purpose-generated weak test hashes; articulate defensive controls.
- Use Burp Suite Community Proxy and Repeater with an intentionally vulnerable local training app; distinguish authentication from authorization.
- Build incident timelines and reports that cite the evidence, uncertainty, scope, and recommended mitigations.
- Make reasoned decisions concerning privacy, disclosure, infrastructure continuity and ethical authorization.

NULLTRACE's completion award is **an in-game achievement**, **not professional accreditation**.

### 1.4 Product success metrics (acceptance targets)

| Metric | Target / test |
|---|---|
| Educational completion | 100/100 catalogued missions have a passing golden-path test before v1.0 |
| Curriculum breadth | Every required competency assessed in a new applied scenario |
| Save durability | Resume and repeat do not corrupt or double-award progression |
| Offline | Main story and supplied lab artifacts remain usable without Internet |
| Safety | The app never starts a live scan absent player initiation; default targets remain contained |
| Accessibility | Keyboard-operable critical UI, subtitles, scalable text, reduced-motion mode |
| Runtime | Aim for 60 FPS in normal scenes, offer 30 FPS mode; performance measured on target laptop |
| Base memory | Aim below 1.5 GB for ordinary gameplay **excluding external tools** |
| Cross-platform | Linux and Windows tested before stable release, with per-OS packaging |
| Reliability | No unresolved severity-1 defects at release gate |

---

# 2. Scope, constraints and non-goals

### 2.1 Included in the v1.0 base game

- Single-player, customizable protagonist (name, codename, appearance, pronouns and selected portrait).
- Ten chapters; 100 primary missions, with one chapter capstone each.
- Three-act original storyline, named factions, meaningful choices and three principal endings.
- Recruit/Operator/Specialist assistance presets; diagnostic placement assessment.
- Academy, simulated terminal, network simulator, evidence/case board and competence tracker.
- Local `.pcapng`, Nmap XML, John synthetic audit, and Burp-controlled local web exercises.
- Per-profile local saves, backups, migrations, progress export/import, achievements and replay.
- Inclusive controls and multiple quality/audio settings.
- Linux and Windows desktop build with separate platform release verification.

### 2.2 Explicit v1.0 non-goals

- Public Internet scanning, unrestricted shell execution or autonomous penetration testing.
- A real-world surveillance platform, proxy infrastructure, attacker tooling or live malware execution.
- Multiplayer, social matchmaking, cloud synchronization, user accounts, online leaderboard or payments.
- Generative AI dependence, paid Burp features, photorealistic 3D or an open-world map.
- Live credential harvesting, automatic access to Wi-Fi/router management or user personal files.
- Professional cybersecurity certification or guarantees of employability.

### 2.3 Assumptions

- Python >=3.10 is available; Python 3.13 is the first proposed compatibility target, not an absolute requirement.
- Internet is available for initial package installation; it is not needed for the mandatory gameplay content after setup.
- External tools are optional dependencies until their chapter is implemented.
- Local service labs should run without root when feasible, using unprivileged ports bound to loopback.
- External educational targets, if later supported, require explicit independent scope approval and a stronger threat model.

---

# 3. Story world, technical plausibility and canonical truth

### 3.1 Setting

Year **2038**. **NEXUS** is a federated digital infrastructure platform intended to help participating institutions coordinate networking reliability, emergency communications and cyber incident response. Its operations contractor is **Meridian Network Operations**, where the player begins as a junior technician.

**MIRROR** is an analytics subsystem. It correlates observations supplied by consenting/contracted endpoints and participating organizations (e.g. logs, traffic metadata and organizational records). A covert unit within the **Directorate** expanded its scope well beyond public expectations, manipulating incident reporting to justify ever-broader observation powers.

**Technical truth rule:** MIRROR cannot read arbitrary TLS content by magic, identify exact geography from any IP, or monitor devices without a technically plausible collection path. Each serious capability must be explained through realistic sensors, logging, permitted access, compromised controls, or probabilistic inference. Its inferences have documented uncertainty and may be false.

### 3.2 The factions

| Faction | Public role | Internal tension |
|---|---|---|
| Meridian Network Operations | Keeps NEXUS connected | Operational duty vs secrecy of customers |
| The Directorate | Defends critical systems | Legitimate response vs abusive surveillance expansion |
| The Unseen | Investigates hidden abuses | Responsible disclosure vs indiscriminate exposure |
| Independent Investigators | Establish defensible facts | Their neutrality is challenged by both sides |
| SPECTER | Appears to be one unknown intruder | Actually an operational label used by multiple actors |

### 3.3 Canonical reveals

- **CH03:** Existence and expanded observation scope of MIRROR discovered; evidence of intent still incomplete.
- **CH05:** Incident reports present materially incomplete network evidence; omission alone does not establish motive.
- **CH07:** SPECTER is an operational identity used by multiple people, not a single mysterious attacker.
- **CH09:** Evidence links a covert Directorate unit to manipulated incident narratives; an Unseen splinter faction has also endangered innocent parties.
- **CH10:** A defensible evidence chain can be assembled. Player chooses a disclosure or containment strategy, with consequences for privacy, accountability and uptime.

### 3.4 Canonical restrictions

- The central mystery's factual resolution remains consistent across branches.
- Choice branches may reveal different supporting clues, change relationships, alter access to optional scenes, and determine ending; they do not remove mandatory learning opportunities.
- Technical errors produce feedback or retries, never irreversible story damage.
- On-screen computer output is either generated by the lab or a clearly labeled fictional screenshot; real-looking random text is not treated as evidence.
- Evidence provenance matters. Contradictory reports remain unresolved until tested against independent sources.

---

# 4. Protagonist, characters and relationships

### 4.1 Customizable protagonist

The player is always a new junior network technician at Meridian; their biography and technical career entry point are shared for story coherence. The player may choose display name, codename, pronouns, portrait, outfit preset, accessibility preferences and assistance difficulty.

**Reference demonstration preset:** `name=Alex`, `codename=Ghost`, `appearance=street_hoodie`. This is a screenshot/testing profile only; never hardcode it as the sole playable character. Sample pronouns in configuration are placeholders, not identity assumptions.

Appearance has no stat benefits. Difficulty changes hints and assistance, not base content availability. Diagnostic placement may mark basic lessons as recognized but mandatory ethics orientation and capstones still apply.

### 4.2 Key cast

| Character | Role | Arc |
|---|---|---|
| Jonah Vale | Meridian senior engineer and first mentor | Network pragmatist who must decide whether silence is complicity |
| Mara Voss | Unseen coordinator | Learns how to balance truth-seeking with collateral risk |
| Dr. Imani Kade | Former NEXUS architect | Confronts responsibility for MIRROR's misuse |
| Elias Rook | Directorate security chief | Seeks stability but resists external oversight |
| SPECTER | Collective operational label | Players untangle distinct actors and false attributions |
| The player | Customizable operator | Develops technical skill and independent judgment |

### 4.3 Relationship variables and state

Use **named bounded values plus explicit decision flags**, not a one-dimensional morality bar. Proposed tracks: `directorate_trust` (0..100), `unseen_trust` (0..100), `evidence_integrity` (0..100), `disclosure_risk` (0..100); initialization and clamping must be documented and unit-tested. State flags such as `preserved_original_logs`, `verified_specter_aliases`, `protected_subject_data`, and `authorized_final_report` have greater ending significance than minor score changes.

Narrative state changes happen only via defined story events; replaying a learning mission cannot repeatedly influence relationship scores. The player can remain distrustful of both factions and still obtain a credible conclusion.

---

# 5. Three-act campaign and endings

| Chapter | Act | Story beat | Education and achievement | Ending-relevant evidence |
|---|---|---|---|---|
| CH01 The Awakening | I | Repair workstation 07; see `MIRROR-07` in a log | Linux basics, ethics, intro networking | Preserve original log reference |
| CH02 The Invisible Network | I | Discover unlisted network segment | LAN, IPv4, CIDR, topology | Reconcile diagram and physical inventory |
| CH03 The Language of Machines | I | Protocol correlation points to MIRROR | TCP/IP, DNS, DHCP, ARP | Verify multiple protocol observations |
| CH04 Ghost Routes | II | Recorded path and report disagree | gateways, routing, NAT, traceroute | Distinguish observation from inferred route |
| CH05 The Packet Files | II | Omitted traffic found in capture | Wireshark, offline captures | Trace frames with immutable fixture hashes |
| CH06 The Open Doors | II | Scope-approved audit uncovers service exposure | Nmap and reports | Separate exposure from proven compromise |
| CH07 The Forgotten Keys | II | Synthetic audit reveals weakness in modeled access path; SPECTER is collective | John and credential defense | Identify what weak passwords can and cannot explain |
| CH08 Behind the Browser | III | Local portal model uncovers broken authorization | Burp, HTTP, session reasoning | Verify access-control flaw on training app |
| CH09 The Shadow Network | III | Coordinated incident reveals evidence tampering and faction abuses | incident response and forensics | Independent timestamp/source correlation |
| CH10 The NEXUS Protocol | III | Assemble complete case and choose disclosure approach | integrated capstone | Final evidence dossier and player decision |

### 5.1 Branching strategy

Use a **foldback branching model**. Each chapter has a required spine plus optional scenes and dialogue variant nodes. The technical mission sequence is not forked into incompatible curricula. At the end of each act, narrative branches reconverge after updating well-defined state flags. This bounds content cost and preserves learning coverage.

### 5.2 Ending predicates (design requirements)

There are exactly three primary ending families in v1.0:

1. **The Reckoning:** player chooses independent accountable disclosure; sufficient verified sources and explicit safeguards (`protected_subject_data`, `preserved_original_logs` and completed evidence dossier) exist.
2. **The Blackout:** player chooses indiscriminate release in the last decision, with narrative harm acknowledged. This is a fictional consequence, not an exercise to actually disrupt infrastructure.
3. **The Silent Protocol:** player opts for restricted containment/reporting; immediate exposure is constrained, systemic accountability remains incomplete.

**Precedence:** first resolve the player's final explicit strategy; then validate evidence/safeguard gates; if required safeguards are insufficient, show a corrective investigative scene or truthful fallback consequence rather than secretly changing the player's choice. A final ending resolver must be deterministic and covered by a complete test matrix for each decision/flag permutation boundary.

---

# 6. Scene graph and v0.1 vertical slice

### 6.1 Scene definitions

A scene is a versioned data object with: ID, background, optional characters/portrait variants, text and audio assets, entry conditions, allowed actions, exit event(s), accessibility transcript and next-scene references. Scene content never contains raw Python code. Expressions are restricted to a typed, well-documented condition language or simple declarative predicates.

### 6.2 Canonical narrative scene anchors

| Scene ID | Event | Trigger |
|---|---|---|
| `S00_BOOT` | Title, logo, accessibility choice | launch |
| `S01_CREATE` | Profile and optional Alex/Ghost demo preset | new game |
| `S02_APARTMENT` | First day assignment | profile committed |
| `S03_MERIDIAN_NOC` | Jonah introduces workstation 07 | CH01 progression |
| `S04_TUTORIAL_TERMINAL` | Player checks system identity and routing | tutorial mission |
| `S05_CONNECTIVITY_FIX` | Repair simulated gateway mismatch | CH01-M10 operation |
| `S06_MIRROR_LOG` | Unexpected `MIRROR-07` event | complete repair |
| `S07_UNKNOWN_MESSAGE` | Anonymous question about monitoring | debrief complete |
| `S08_REPORT_CHOICE` | Report, preserve permitted evidence or ask Jonah | narrative choice |
| `S09_ACT1_REVEAL` | MIRROR existence supported by multiple observations | CH03-M10 |
| `S10_ROUTE_CONTRADICTION` | Path logs conflict with official report | CH04-M10 |
| `S11_PACKET_REVEAL` | Independent packet evidence proves omission | CH05-M10 |
| `S12_SCOPE_MEETING` | Scope-approved local test authorized | CH06 opening |
| `S13_SPECTER_MULTIPLE` | SPECTER alias attribution revised | CH07-M10 |
| `S14_PORTAL_CLUE` | Local portal training case supports web lesson | CH08-M10 |
| `S15_TAMPERED_REPORT` | Evidence manipulation established | CH09-M10 |
| `S16_FINAL_BRIEF` | Final investigation assigned | CH10-M01 |
| `S17_DECISION` | Disclosure options and safeguards | CH10-M09 |
| `S18_RECKONING` | Accountability outcome | ending resolver |
| `S19_BLACKOUT` | Harmful disclosure outcome | ending resolver |
| `S20_SILENT` | Containment outcome | ending resolver |
| `S21_CREDITS` | Results, skills, replay and accessibility recap | ending finished |

Support optional scene bundles per chapter, but all core scene anchors need golden-path and branch tests.

### 6.3 The exact Phase 1 playable loop

1. Start a Pygame window and open main menu (keyboard and pointer operable).
2. Create a player; choose Alex/Ghost example or customize identity.
3. View S02 opening scene with captions and skip/replay control.
4. Talk to Jonah; receive a simple bounded terminal/network diagnostic case.
5. Inspect a simulated IP/gateway configuration, identify the misconfiguration, and apply a correct fix.
6. Receive structured feedback explaining why the fix works; record one competence outcome.
7. View the MIRROR log and mysterious transmission. Record an explicit story choice.
8. Checkpoint safely into SQLite. Quit and reopen; all state resumes without duplicate rewards.

**Phase 1 acceptance:** complete this loop on a fresh profile with keyboard-only navigation, mouse navigation, invalid name handling, empty save handling, and restart recovery. No real Nmap/Wireshark tools are required.

### 6.4 Opening sample dialogue (illustrative, editable)

- Jonah: “Workstation seven can reach its neighbors, but not the application server. Start with the addressing information.”
- Player tutorial prompt: “A default gateway forwards traffic outside the local subnet. Does this machine have the right next hop?”
- System after repair: `CONNECTIVITY RESTORED — EVENT REF: MIRROR-07 (RESTRICTED)`.
- Unknown message: “You repaired the connection. Why was MIRROR observing it?”

---

# 7. Learning, diagnostic placement and grading

### 7.1 Mandatory nine-stage lesson pattern

1. State the topic and learning objectives.
2. Define unfamiliar terms.
3. Explain mechanisms step by step.
4. Present a diagram, animation or labeled visualization.
5. Explain a worked example or legitimate command output.
6. Relate the concept to a real-life system or defensive task.
7. Provide exercises with explanation after submission.
8. Complete a mini-investigation that applies the skill.
9. Integrate multiple concepts in a chapter operation.

A typical 30-minute non-capstone mission allocates about 4 minutes briefing, 8 minutes concept/demo, 12 minutes practice and 6 minutes debrief. This is a content pacing target, not a timer that penalizes slow learners. Capstones may be longer and require mid-mission checkpoints.

### 7.2 Difficulty presets

- **Recruit:** explicit explanations, contextual visual aids, three-tier hints and beginner-friendly feedback.
- **Operator:** reduced scaffolding; key facts and tools available on demand.
- **Specialist:** fewer prompts and more independent hypothesis formation.

Difficulty does not alter network facts or change which targets are authorized. It cannot turn a prohibited action into an allowed one. Players can change assistance difficulty at checkpoints without losing completed work.

### 7.3 Diagnostic placement

The optional beginning diagnostic tests Linux navigation, network models, IP/CIDR, protocol interpretation and ethical scope. It generates a **recommendation and optional lesson waivers**, not skill mastery. Safety orientation and chapter capstones cannot be bypassed. Repeating a diagnostic does not grant story rewards or overwrite existing assessment evidence.

### 7.4 Competency rubric

- `practiced`: guided exercise completed.
- `competent`: goal achieved with limited/no hints and a defensible interpretation.
- `mastered`: same skill transferred to a new fixture or scenario without answer memorization.

Each competency has a stable ID (`NET.IPV4.ADDRESS`, `PCAP.DNS.CORRELATE`, `NMAP.XML.INTERPRET`, etc.), required prerequisite IDs and assessment evidence IDs. Passing thresholds are mission-defined, documented, and tested, not arbitrary based on time or number of clicks.

### 7.5 Feedback and replays

Wrong submissions disclose *why* the conclusion is unsupported and which concept to revisit. Hints escalate from conceptual to directional to guided. Capstone grading requires independent evidence and rejects answers with no support even when final guesses happen to match. Replaying a mission can improve mastery, but rewards and irreversible story actions are processed once.

### 7.6 Learning asset requirements

Each published mission must have a written explanation, novice glossary, diagram description/transcript, one tested example, at least one applied activity, a validator/rubric, expected result(s), common misconceptions, citations for external technical claims, accessibility alternatives, and a debrief linking back to the story.

---

# 8. Gameplay and UI/UX specification

### 8.1 Main modes

| Mode | Description | Typical outputs |
|---|---|---|
| Story | Conversations, cutscenes, ethical choices | narrative flags and scene transitions |
| Academy | Lessons, visualization, worked examples | conceptual progress |
| Simulation | Mock terminal, switches, routes and packets | synthetic state and expected results |
| Laboratory | Player uses real tools on owned fixtures/local apps | local verified artifacts |
| Investigation | Evidence board, hypothesis and report writing | evidence citations and findings |
| Operations | Multi-domain capstones and debriefs | mastery, completion and story events |

### 8.2 Main screens

Main Menu; Character Creator; Operations Hub; Chapter Select; Mission Briefing; Dialogue/Cinematic View; Academy; Simulated Terminal; Network View; Laboratory Instructions; Evidence Locker; Investigation Board; Skill Tree; Knowledge Database; Settings/Accessibility; Save/Profile Manager; Results/Debrief.

UI layout consists of a central scene canvas plus optional contextual panels. All critical controls have keyboard focus, visible labels, hover-independent activation and touch-friendly pointer targets where relevant. Player progress never depends on an animation completing.

### 8.3 Presentation rules

- Cinematic **2D**, not open-world or full 3D; scene artwork with parallax layers where performant.
- Dark techno-thriller palette with readable contrast. Terminal output must wrap or scroll; no green-text-only accessibility assumption.
- Resolution-independent layout (logical UI coordinates + dynamic scaling); recommended minimum window approximately 1024×576 where feasible, with text-scale handling and graceful reflow.
- Distinct audio buses (master, music, ambience, effects, optional narration).
- All voiced story content has subtitles; captions represent meaningful non-speech audio. Skip/replay controls supported.
- Reduced motion and a static-illustration fallback for network animations.
- No requirement to type complex commands during the first tutorial; accept guided UI input and later graduate to real terminal syntax.

### 8.4 Evidence model

An evidence item is not merely an inventory collectible. It specifies `source_type`, `original_fixture_sha256`, `observation`, `timestamp_or_range`, `provenance`, `scope`, `confidence`, and source references (e.g. frame number, XML element, log line). The player distinguishes:

- **Observation:** directly found in an artifact.
- **Hypothesis:** unconfirmed possible explanation.
- **Finding:** conclusion supported by sufficient evidence.
- **Recommendation:** protective or investigative action derived from findings.

The case board supports connections between evidence and hypotheses. The system must reject unsupported conclusions and explain what stronger evidence would look like.

---

# 9. Complete 100-mission catalog

**Contract for every row:** ID, title, learning objective, applied activity, verifiable outcome and preferred mode. `content/missions/catalog.json` contains all fields plus chapter references and initial prerequisite chains. These are **design records**, not runnable mission content or completed tests; individual lesson prose, JSON validators, assets and golden fixtures are authored during the corresponding build phase.


## CH01: The Awakening

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH01-M01` | **Welcome to Meridian** | Cybersecurity ethics and authorization | Categorize authorized versus prohibited actions in a guided briefing. **Pass:** Scenario classification rubric. |
| `CH01-M02` | **Assets Under Threat** | Assets, threats, vulnerabilities, risk, CIA triad | Annotate incident cards with asset, threat and consequence. **Pass:** At least four correctly justified identifications. |
| `CH01-M03` | **Inside the Machine** | Hardware, OS, processes and services | Inspect a simulated workstation and process list. **Pass:** Locate operating system, network adapter and service role. |
| `CH01-M04` | **The Linux Filesystem** | Paths, files, directories and permissions | Navigate a mock filesystem in the game terminal. **Pass:** Reach specified file without privileged commands. |
| `CH01-M05` | **The Black Terminal** | pwd, ls, cd, cat, help, command structure | Execute bounded simulated shell commands. **Pass:** Correct commands and descriptions of output. |
| `CH01-M06` | **Who Has Access?** | Accounts, file permissions, least privilege | Adjust fictional read permissions on training files. **Pass:** Reach intended access policy without overgranting. |
| `CH01-M07` | **The System Remembers** | Log timestamps, severity, provenance | Inspect synthetic diagnostic logs. **Pass:** Order events correctly with explicit uncertainty. |
| `CH01-M08` | **Connected Machines** | LAN basics, clients, servers, switches and routers | Connect labeled devices in a topology exercise. **Pass:** Produce valid client-to-server path. |
| `CH01-M09` | **First Contact** | IP addresses, interfaces, ping and troubleshooting | Check configured addresses and simulated ping results. **Pass:** Correctly diagnose a reachability issue. |
| `CH01-M10` | **The Unknown Transmission** | Integrate Linux, logs and connectivity reasoning | Repair workstation 07 and examine MIRROR-07 log reference. **Pass:** Demonstrate stable simulated connectivity and support report. |

## CH02: The Invisible Network

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH02-M01` | **Networks Everywhere** | LAN, WAN, Internet and addressing domains | Classify sample network diagrams. **Pass:** Correctly distinguish network boundaries. |
| `CH02-M02` | **Signals and Cables** | Copper, fiber, radio, latency and noise | Compare fictional physical links. **Pass:** Explain medium tradeoffs accurately. |
| `CH02-M03` | **The Switching Room** | Switching, broadcast domains, topologies | Wire a simulated switch fabric. **Pass:** Frames reach correct local devices. |
| `CH02-M04` | **Machine Identities** | Ethernet frames and MAC addressing | Trace destination MAC decisions. **Pass:** Select destination or gateway MAC correctly. |
| `CH02-M05` | **Address Required** | IPv4, prefixes and host addressing | Assign IPv4 addresses in an isolated network. **Pass:** No collisions and valid host prefixes. |
| `CH02-M06` | **The Network Mask** | CIDR prefixes and netmasks | Solve subnet membership exercises. **Pass:** Correct network and broadcast boundaries. |
| `CH02-M07` | **Divide the Network** | Subnet allocation and address planning | Partition a fictional office network. **Pass:** Subnets are nonoverlapping and sized correctly. |
| `CH02-M08` | **Beyond IPv4** | IPv6 notation and address scopes | Label example IPv6 addresses. **Pass:** Correctly classify sample address scopes. |
| `CH02-M09` | **Mapping Meridian** | Topology documentation and endpoint inventory | Produce device-node and link map. **Pass:** Map conforms to given inventory. |
| `CH02-M10` | **The Hidden Segment** | Combined layer-2 and IP investigation | Find incorrectly placed simulated network endpoint. **Pass:** Identify and correct segment misconfiguration. |

## CH03: The Language of Machines

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH03-M01` | **Seven Layers** | OSI and TCP-IP mapping | Match packet functions to layers. **Pass:** Accurate conceptual layer mapping. |
| `CH03-M02` | **Encapsulation** | Frames, packets, segments and headers | Animate source-to-destination encapsulation. **Pass:** Arrange wrappers in correct order. |
| `CH03-M03` | **The Port Number** | Sockets and service port concepts | Match service sessions to endpoints. **Pass:** Correct five-tuple interpretation. |
| `CH03-M04` | **Two Messengers** | TCP and UDP characteristics | Select transport characteristics for cases. **Pass:** Justified choices, not rote keywords. |
| `CH03-M05` | **The Handshake** | SYN, SYN-ACK, ACK and sequence logic | Reassemble simulated TCP establishment. **Pass:** Correct message and endpoint order. |
| `CH03-M06` | **What's in a Name?** | DNS query/answer types and caching | Trace a synthetic domain lookup. **Pass:** Identify question, answer and caching role. |
| `CH03-M07` | **Automatic Addressing** | DHCP lifecycle and lease basics | Investigate a simulated lease exchange. **Pass:** Correctly identify assignment failure. |
| `CH03-M08` | **Who Owns This IP?** | ARP request/response on local segments | Diagnose a simulated ARP mapping issue. **Pass:** Correct local resolution explanation. |
| `CH03-M09` | **The Web Connection** | HTTP, HTTPS and TLS overview | Compare visible metadata across two sessions. **Pass:** Do not claim encrypted content is readable. |
| `CH03-M10` | **Protocol Anomaly** | Correlate DNS, ARP, TCP and DHCP records | Reconstruct a synthetic protocol timeline. **Pass:** Supported finding and MIRROR clue recovered. |

## CH04: Ghost Routes

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH04-M01` | **The Default Gateway** | Local versus off-subnet forwarding | Route packets through a gateway exercise. **Pass:** Correct next-hop selection. |
| `CH04-M02` | **Routing Decisions** | Longest-prefix-match and routing tables | Select routes from a synthetic table. **Pass:** Choose most specific matching route. |
| `CH04-M03` | **Translated Identities** | NAT and address translation | Trace a simulated translated flow. **Pass:** Correct internal/external tuple mapping. |
| `CH04-M04` | **Following the Route** | TTL, traceroute, path uncertainty | Read supplied traceroute outputs. **Pass:** Distinguish a hop from physical geography. |
| `CH04-M05` | **Control Messages** | ICMP error and diagnostic purposes | Explain synthetic ICMP results. **Pass:** Accurate interpretation without assuming reachability. |
| `CH04-M06` | **The Slow Connection** | Latency, jitter, loss and measurement limits | Inspect controlled trace metrics. **Pass:** Separate latency from throughput conclusions. |
| `CH04-M07` | **The Broken Route** | Routing mistakes and recovery | Repair a misconfigured route in simulation. **Pass:** Target path restored using minimal change. |
| `CH04-M08` | **Names Versus Paths** | DNS versus routing fault isolation | Investigate two failure reports. **Pass:** Accurately attribute each root cause. |
| `CH04-M09` | **Tracing Evidence** | Correlating independent route observations | Compare several synthetic paths. **Pass:** Support hypothesis with multiple observations. |
| `CH04-M10` | **Ghost Route** | Integrated diagnostics and time correlation | Resolve a deceptive route incident case. **Pass:** Evidence-backed report with uncertainty noted. |

## CH05: The Packet Files

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH05-M01` | **Inside a Packet** | Capture ethics, payload versus metadata | Inspect simulated protocol layers. **Pass:** Identify observation scope and privacy constraints. |
| `CH05-M02` | **The Capture File** | PCAP and PCAPNG navigation | Open the supplied offline capture. **Pass:** Correct packet count and timeframe. |
| `CH05-M03` | **Packet Anatomy** | Ethernet, IP, TCP/UDP header fields | Find fields in an annotated capture. **Pass:** Correct source, destination and fields. |
| `CH05-M04` | **Filtering the Noise** | Wireshark display filter fundamentals | Filter a provided synthetic capture. **Pass:** Submit qualifying frame number and rationale. |
| `CH05-M05` | **DNS Evidence** | DNS records and transaction matching | Find DNS request-response pair. **Pass:** Correct query, response and client endpoint. |
| `CH05-M06` | **Address Discovery** | ARP analysis and mapping | Identify ARP exchange in sample capture. **Pass:** Supported mapping with frame references. |
| `CH05-M07` | **Following TCP** | Connection setup, retransmissions | Trace a supplied TCP conversation. **Pass:** Correct handshake and loss inference limits. |
| `CH05-M08` | **Encrypted Conversations** | TLS and HTTP observability | Compare synthetic plaintext and encrypted flows. **Pass:** Only infer details visible in capture. |
| `CH05-M09` | **Reconstruct the Flow** | Correlating packet timestamps and streams | Create traffic timeline from fixture. **Pass:** Coherent flow timeline with citations. |
| `CH05-M10` | **The Missing Packet** | Formal analysis of omitted capture evidence | Write packet-based case report. **Pass:** Cited frames, defensible finding, preserved fixture hash. |

## CH06: The Open Doors

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH06-M01` | **Reconnaissance** | Discovery versus exploitation | Interpret safe host/service inventory. **Pass:** Identify reconnaissance scope and purpose. |
| `CH06-M02` | **Rules of Engagement** | Permission, lab range, prohibited targets | Review signed fictional assessment scope. **Pass:** Select approved loopback-only target. |
| `CH06-M03` | **Is Anybody There?** | Nmap host discovery concepts | Review or run lab-approved discovery. **Pass:** Correctly interpret responsive local asset. |
| `CH06-M04` | **Checking the Ports** | TCP connect-scanning concepts | Run bounded approved TCP connect assessment. **Pass:** Identify lab service port from XML evidence. |
| `CH06-M05` | **Open or Filtered?** | Nmap state semantics and uncertainty | Classify supplied scan outputs. **Pass:** Correct open, closed, filtered interpretation. |
| `CH06-M06` | **Identifying Services** | Banners and service uncertainty | Analyze controlled service-identification output. **Pass:** Distinguish identification from proof of vulnerability. |
| `CH06-M07` | **UDP Investigations** | UDP ambiguity and closed/filtered uncertainty | Inspect supplied UDP result examples. **Pass:** State limits accurately. |
| `CH06-M08` | **Reading the Scan** | Nmap XML schema and evidence handling | Parse a provided XML scan report. **Pass:** Correct endpoints, ports and state extraction. |
| `CH06-M09` | **Exposure Versus Vulnerability** | Risk triage and verification | Classify observations from approved service scan. **Pass:** Avoid unjustified compromise claims. |
| `CH06-M10` | **The Open Doors** | Scoped service-exposure assessment | Produce bounded local asset/security inventory. **Pass:** Valid scope, supported findings and remediation. |

## CH07: The Forgotten Keys

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH07-M01` | **Identity and Trust** | Authentication, authorization and sessions | Compare account access scenarios. **Pass:** Correctly distinguish identity from permission. |
| `CH07-M02` | **The Weak Password** | Entropy misconceptions and common patterns | Evaluate fictitious password examples. **Pass:** Explain unpredictability and reuse risk. |
| `CH07-M03` | **The Hash** | Hashing versus encryption and verification | Match sample hash verification steps. **Pass:** Accurate nonreversible-hash explanation. |
| `CH07-M04` | **Salt and Cost** | Salting, KDF work factors and password storage | Inspect synthetic hash metadata. **Pass:** Recognize unique salt and work factor properties. |
| `CH07-M05` | **The Training Vault** | Synthetic training hashes and scope | Load provided fictional hashes. **Pass:** Confirm only provided examples are used. |
| `CH07-M06` | **Meet John** | John interface and safe audit workflows | Read tool help and supplied synthetic fixture. **Pass:** Identify audit scope and input format. |
| `CH07-M07` | **Wordlist Audit** | Dictionary-based weak-password auditing | Audit pre-generated weak local hashes with supplied wordlist. **Pass:** Recover only expected synthetic training strings. |
| `CH07-M08` | **Reading the Results** | What successful or unsuccessful audit proves | Interpret controlled run output. **Pass:** Accurate limitations and evidence references. |
| `CH07-M09` | **Defending Credentials** | Long unique passwords, MFA, rate limits, secure hashing | Propose mitigations for fictional system. **Pass:** Concrete layered defense measures. |
| `CH07-M10` | **The Forgotten Keys** | Credential security incident reconstruction | Complete permitted synthetic audit report. **Pass:** Support weakness claims without real credentials. |

## CH08: Behind the Browser

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH08-M01` | **How the Web Works** | Client-server HTTP roles and TLS | Trace browser to service request flow. **Pass:** Correct endpoint, transport and trust model. |
| `CH08-M02` | **Request and Response** | HTTP methods, statuses, URLs and bodies | Inspect saved HTTP exchanges. **Pass:** Correct method, path and status explanation. |
| `CH08-M03` | **Hidden in the Headers** | Headers, content types and origin boundaries | Compare safe local request headers. **Pass:** Identify relevant headers accurately. |
| `CH08-M04` | **Sessions and Cookies** | Session identifiers, cookies, cookie attributes | Investigate a simulated session lifecycle. **Pass:** Explain login continuity and expiry. |
| `CH08-M05` | **The Intermediary** | HTTP proxy mechanics and scoping | Trace request via local proxy. **Pass:** Correct proxy role and restrictions. |
| `CH08-M06` | **Meet Burp Suite** | Burp Community proxy setup | Intercept request to own loopback training app. **Pass:** Show bounded local request in HTTP history. |
| `CH08-M07` | **Repeating a Request** | Manual safe HTTP Repeater analysis | Change harmless test parameter in local app. **Pass:** Interpret response differences accurately. |
| `CH08-M08` | **Access Boundaries** | Object-level authorization fundamentals | Identify a deliberate local training weakness. **Pass:** Explain ownership check failure with safe fixture. |
| `CH08-M09` | **Securing the Portal** | Authorization validation and session hardening | Patch or select mitigations in simulated server. **Pass:** Regression scenario denies unintended access. |
| `CH08-M10` | **Behind the Browser** | End-to-end local web security assessment | Write web investigation report with requests/responses. **Pass:** Findings reproducible on controlled training app. |

## CH09: The Shadow Network

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH09-M01` | **An Incident Begins** | Preparation, detection, containment, lessons learned | Sequence an incident-response plan. **Pass:** Correct stage and tradeoff reasoning. |
| `CH09-M02` | **Following the Logs** | Events and logs across systems | Review provided multi-system logs. **Pass:** Identify relevant event references. |
| `CH09-M03` | **Preserving Evidence** | Hashes, chain of custody, minimal handling | Record fixture identity and provenance. **Pass:** Exact fixture hashes and handling note. |
| `CH09-M04` | **Building a Timeline** | Time zones, ordering, clock drift | Normalize event timestamps in supplied logs. **Pass:** Chronology cites sources and uncertainty. |
| `CH09-M05` | **Network and Host** | Correlating PCAP and host events | Link capture with host process events. **Pass:** Valid cross-source attribution caveats. |
| `CH09-M06` | **Exposure Analysis** | Inventory versus actual compromise | Compare Nmap XML with incident artifacts. **Pass:** Appropriate conclusion about service exposure. |
| `CH09-M07` | **Web Evidence** | HTTP logs, session metadata and sequence | Correlate sanitized request logs. **Pass:** Document observations and limits. |
| `CH09-M08` | **True or False Alert?** | False positives, plausible alternatives | Evaluate two evidence-supported hypotheses. **Pass:** Select best-supported interpretation. |
| `CH09-M09` | **Analyst's Report** | Writing structured incident reports | Produce executive summary plus technical evidence. **Pass:** Meets rubric for evidence, uncertainty, mitigation. |
| `CH09-M10` | **The Shadow Network** | Integrated full-case response | Reconstruct case and identify manipulated records. **Pass:** Complete multi-evidence findings with citations. |

## CH10: The NEXUS Protocol

| ID | Mission | Objective | Activity and assessment |
|---|---|---|---|
| `CH10-M01` | **The Final Briefing** | Investigation authorization and plan | Scope the final evidence review. **Pass:** Valid plan and protected data handling. |
| `CH10-M02` | **Mapping NEXUS** | Multi-layer infrastructure topology | Reconstruct relevant infrastructure model. **Pass:** Topology supported by fixtures. |
| `CH10-M03` | **The Traffic Archive** | Independent traffic analysis | Analyze supplied PCAPNG artifacts. **Pass:** Correct packet-level findings and caveats. |
| `CH10-M04` | **The Service Register** | Interpreting recorded authorized scans | Analyze synthetic Nmap XML findings. **Pass:** Accurate service inventory and exposure discussion. |
| `CH10-M05` | **Credential Audit** | Password-security conclusions | Interpret synthetic John audit evidence. **Pass:** Evidence-backed credential policy recommendations. |
| `CH10-M06` | **The MIRROR Portal** | Session and access-control evaluation | Inspect local test app with Burp Community. **Pass:** Correctly identify and document lab issue. |
| `CH10-M07` | **Conflicting Records** | Cross-source evidence validation | Compare logs, packets and reports. **Pass:** Detect tampered or omitted evidence. |
| `CH10-M08` | **Chain of Truth** | Final evidence and incident timeline | Produce comprehensive structured case record. **Pass:** Provenance-complete findings with limitations. |
| `CH10-M09` | **The Disclosure Decision** | Ethics, privacy, public interest, continuity | Choose disclosure route and justify safeguards. **Pass:** Consistent explicit narrative flags and reasoning. |
| `CH10-M10` | **NULLTRACE** | All competency domains, integrated capstone | Complete final integrated case and ending. **Pass:** All required competencies and ending conditions satisfied. |

### 9.1 Mission execution standard

Each milestone must expand catalog stubs into fully validated mission documents. A mission is **not finished** until the required content, sample inputs, safe environment policy, known solution, tests, UI transitions and save/replay semantics exist. Chapter ten operations are multi-competency assessments. Chapter ten's final mission uses all four tool families in controlled form.

### 9.2 Prerequisite design

The starter catalog currently uses a simple *linear prerequisite chain* within each chapter and from prior chapter capstone to the next chapter. During implementation, the curriculum engine will support a DAG with separate `required` and `recommended` competency edges. Allow diagnostic waivers only for designated lessons. Reject cycles at content-build time; use stable IDs instead of list positions. An accessibility mode must not change whether a learner satisfies a technical prerequisite.

---
# 10. Software architecture and module boundaries

### 10.1 Architecture style

**Modular monolith**: a single offline-first desktop Python process hosting logically separate engines, with carefully controlled out-of-process security tools. The first release does **not** use microservices, Redis, web accounts, background daemons, or Internet APIs.

```text
Pygame Application / Presentation
    ├── Scene Manager        → dialogue, UI navigation, cutscenes
    ├── Story Engine         → flags, branches, NPC relationships
    ├── Curriculum Engine    → prerequisite graph, lessons, competencies
    ├── Mission Engine       → state machine, objectives, capstones
    ├── Assessment Engine    → pure validation of claims / evidence
    ├── Investigation Engine → evidence and report graph
    ├── Progression Engine   → unlocks, achievements
    └── Internal Event Bus   → domain events, no network broker
            │
            ├── Content Repository → versioned JSON / assets
            ├── Persistence        → SQLite / atomic transactions
            └── Lab Controller     → policy → adapters → bounded subprocesses
                                       ├── synthetic network simulation
                                       ├── TShark / Wireshark fixtures
                                       ├── approved Nmap localhost service
                                       ├── John synthetic hashes
                                       └── Burp local training app
```

### 10.2 Core boundaries and allowed dependencies

- `core`: application lifecycle, dependency wiring, configuration, clock and event dispatch. May import interfaces from feature packages; should not contain chapter-specific rules.
- `ui`: Pygame rendering and input only. UI may issue typed commands to mission/story services and display returned view models; it cannot directly modify database rows or grant awards.
- `story`: deterministic branching and relationship effects. Consumes mission completion signals; knows no tool-specific CLI invocation details.
- `learning`: glossary, prerequisites, lesson progress, skill taxonomy, hints and diagnostics. Independent of scene graphics.
- `missions`: mission lifecycle, objectives, transition rules and permission checks; cannot spawn shell processes directly.
- `assessment`: pure/domain validation from normalized evidence; deterministic and testable without launching Pygame or a security tool.
- `investigations`: evidence graph, source provenance, confidence, report format and case validation.
- `labs`: controller, simulated fixtures, adapter registry, execution policy, data normalization; adapter implementations know nothing about Pygame.
- `progression`: competency awards, unlock decisions, achievement idempotency.
- `persistence`: SQLite transactions, repositories, migrations and backups. No Pygame or subprocess dependencies.
- `content`: schema validation, version resolution, localization, asset manifests and integrity checking. **Data only, no scripts embedded in mission packages.**

### 10.3 Command versus event

A **command** expresses player intent (`StartMission`, `SubmitEvidence`, `RecordChoice`, `LaunchLab`) and is validated synchronously at a service boundary. An **event** expresses a completed state transition (`mission.completed`, `evidence.accepted`, `story.choice_recorded`). Events do not replace database transactions. Persistent effects happen in one atomic transaction; the event is then emitted from an outbox or replay-safe state transition to avoid loss and duplicate awards.

Representative event names:

```text
profile.created
mission.started
lesson.completed
lab.requested
lab.started
lab.completed
lab.failed
evidence.submitted
assessment.completed
mission.completed
story.choice_recorded
chapter.unlocked
save.migrated
```

### 10.4 Dependency injection and service interfaces

The application composition root instantiates services once, passes interfaces into owning systems, and shuts down external lab resources on exit. Prefer structural typing with `typing.Protocol` for ports; implementations may be swapped with fake repositories/adapters for testing.

Illustrative interface signatures (**design contract, not Phase 0 implemented code**):

```python
from typing import Protocol

class MissionRepository(Protocol):
    def load(self, mission_id: str) -> "MissionDefinition": ...
    def list_for_chapter(self, chapter_id: str) -> list["MissionDefinition"]: ...

class AssessmentEngine(Protocol):
    def evaluate(self, assessment_id: str, answer: "Submission", evidence: list["Evidence"]):
        "AssessmentResult": ...

class SaveRepository(Protocol):
    def save_checkpoint(self, campaign_id: str, expected_revision: int, state: "Checkpoint"):
        "SaveResult": ...
    def load_checkpoint(self, campaign_id: str) -> "Checkpoint": ...

class LabAdapter(Protocol):
    def check_available(self) -> "AvailabilityReport": ...
    def validate(self, lab: "ApprovedLab", request: "LabRequest") -> "ValidationResult": ...
    def start(self, lab: "ApprovedLab", request: "LabRequest") -> "LabSession": ...
    def collect(self, session: "LabSession") -> "NormalizedLabResults": ...
    def stop(self, session: "LabSession") -> None: ...
    def cleanup(self, session: "LabSession") -> None: ...
```

### 10.5 Source tree after implementation

```text
nulltrace/
├── pyproject.toml
├── README.md
├── docs/
│   ├── NULLTRACE_Master_System_Design_v1.0.md
│   ├── adr/                   # architecture decision records
│   ├── runbooks/              # troubleshooting & release process
│   └── references/            # research, permissions, licenses
├── src/nulltrace/
│   ├── __main__.py            # currently environment diagnostic only
│   ├── core/
│   ├── ui/
│   ├── story/
│   ├── learning/
│   ├── missions/
│   ├── assessment/
│   ├── investigations/
│   ├── labs/
│   │   ├── controller.py
│   │   ├── simulation/
│   │   ├── adapters/
│   │   ├── policy/
│   │   └── normalized/
│   ├── progression/
│   ├── persistence/
│   └── content/
├── content/
│   ├── characters/
│   ├── chapters/
│   ├── scenes/
│   ├── lessons/
│   ├── missions/catalog.json
│   ├── competencies/
│   └── translations/
├── assets/
│   ├── backgrounds/
│   ├── portraits/
│   ├── ui/
│   ├── sound/
│   └── captions/
├── lab_assets/
│   ├── pcaps/
│   ├── scan_reports/
│   ├── synthetic_hashes/
│   ├── training_web/
│   └── manifests/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── content/
│   ├── safety/
│   ├── migration/
│   └── golden/
├── scripts/
│   ├── setup_ubuntu.sh
│   ├── setup_windows.ps1
│   ├── validate_content.py
│   └── build_release.py
└── .github/workflows/          # optional CI in implementation
```

Only Phase 0 paths in the shipped starter exist now; other paths are target structure, not a claim of delivery.

---

# 11. Data contracts, content format and schema evolution

### 11.1 ID conventions

- Chapter: `CH01` ... `CH10`.
- Mission: `CH05-M04` (immutable).
- Scene: `S11_PACKET_REVEAL` or similarly stable slug.
- Competency: `PCAP.DNS.CORRELATE`.
- Assessment: `CH05-M04-ASSESS`.
- Evidence: generated UUID plus immutable provenance fields.
- Lab: `LAB-PCAP-CH05-M04-V1`.

IDs are content-independent and never reassigned. `content_version` uses semantic versioning where contract changes matter.

### 11.2 Canonical mission definition (illustrative JSON)

```json
{
  "schema_version": 1,
  "id": "CH05-M04",
  "content_version": "1.0.0",
  "chapter_id": "CH05",
  "title_key": "mission.ch05.m04.title",
  "kind": "laboratory",
  "prerequisite_missions": ["CH05-M03"],
  "competency_ids": ["PCAP.FILTERS.BASIC"],
  "required": true,
  "entry_scene_id": "S_CH05_M04_BRIEF",
  "exit_scene_id": "S_CH05_M04_DEBRIEF",
  "lesson_id": "LESSON-PCAP-FILTERS-V1",
  "lab_id": "LAB-PCAP-CH05-M04-V1",
  "assessment_id": "CH05-M04-ASSESS",
  "hints": ["HINT_1", "HINT_2", "HINT_3"],
  "retry_policy": "unlimited",
  "replayable": true,
  "estimated_minutes": 30
}
```

### 11.3 Assessment definition (illustrative)

```json
{
  "schema_version": 1,
  "id": "CH05-M04-ASSESS",
  "validator_type": "pcap_display_filter_evidence",
  "required_evidence_fields": ["fixture_sha256", "frame_number", "protocol"],
  "max_submissions": null,
  "minimum_competency": "competent",
  "rubric": [
    {"id": "correct_fixture", "weight": 25},
    {"id": "correct_protocol", "weight": 25},
    {"id": "correct_frame", "weight": 25},
    {"id": "defensible_explanation", "weight": 25}
  ]
}
```

Rubric weights and thresholds must be explicitly declared. `validator_type` maps to **pre-registered in-process code**, never imports a module specified by user-controlled content. Prefer evidence-keyed grading over requiring players to copy exact sentences.

### 11.4 Lab declaration (illustrative)

```json
{
  "schema_version": 1,
  "id": "LAB-PCAP-CH05-M04-V1",
  "mode": "offline_fixture",
  "adapter": "tshark",
  "allowed_operations": ["read_capture", "display_filter"],
  "fixtures": [{"path": "lab_assets/pcaps/example.pcapng", "sha256": "<generated at asset build time>"}],
  "time_limit_seconds": 30,
  "max_output_bytes": 1048576,
  "network_allowed": false,
  "root_required": false
}
```

The `example.pcapng` path above is a **placeholder**. Phase 0 does not provide genuine packet-capture files. The lab controller must reject missing files, mismatched hashes and disallowed operations.

### 11.5 Character config (illustrative)

```json
{
  "schema_version": 1,
  "profile_id": "example-alex-ghost",
  "display_name": "Alex",
  "codename": "Ghost",
  "appearance_id": "street_hoodie",
  "pronouns": "they/them",
  "campaign_id": "example-campaign-001",
  "assistance_preset": "recruit"
}
```

This example is **not** a mandatory gender/pronoun identity. Every property that represents player identity remains user-editable under specified bounds; escape player strings before drawing or logging them.

### 11.6 Authoring and validation rules

- JSON must pass declared structural validation; required fields cannot be omitted and extra executable instructions are forbidden.
- Validate IDs, uniqueness, path containment, referenced assets, competency DAG acyclicity, scene reachability and ending determinism at build time.
- Chapter content may introduce new asset IDs but never silently alter the meaning of existing mission IDs.
- Version schema changes via migration and add regression tests before release.
- Limit size and depth of imported JSON; never dynamically evaluate string expressions from a mission file.
- Localized text uses message IDs and safe variable interpolation (`operator_name`) with proper escaping.

---

# 12. Database, saves and migrations

### 12.1 Design decisions

SQLite remains the authority for campaign progress. JSON files are authored content, imports/exports or debug snapshots. Player data is stored in a user-data directory, **not inside installed package assets**. Exact platform directories will be defined during Phase 1; separate portable mode may come later.

Use WAL where suitable, foreign keys enabled, prepared statements, unique constraints, and transactions for mission completion/awards. Provide explicit checkpoints and backup before migration. Do not store raw personal network captures or real credentials in the save database.

### 12.2 Logical schema

| Table | Primary responsibility | Integrity concern |
|---|---|---|
| `players` | profile identity and presentation preferences | controlled text lengths and unique profile ID |
| `campaigns` | current active campaign and content version | ownership, revision and checkpoint |
| `mission_progress` | attempt state and progress per campaign | unique `(campaign_id, mission_id)` |
| `mission_attempts` | submitted evidence, retry/outcome history | bounded metadata only |
| `competency_progress` | skill and mastery evidence | unique `(campaign_id, competency_id)` |
| `story_flags` | boolean/string narrative flags | explicit allowed flag namespace |
| `relationships` | bounded score state | ranges checked |
| `cases` | case status, report references | case ID/version compatibility |
| `evidence` | provenance, original content hash, source pointer | immutable source identity |
| `assessment_results` | scoring rubric and reproducible outcomes | idempotent attempt IDs |
| `achievements` | one-time awards | unique per award/campaign |
| `settings` | UI, audio and accessibility options | schema-validated defaults |
| `event_outbox` | durable domain events awaiting dispatch | replay-safe event IDs |
| `schema_migrations` | applied database migrations | sequential controlled versioning |

### 12.3 Selected SQL shape (design example)

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL CHECK(length(display_name) BETWEEN 1 AND 40),
    codename TEXT NOT NULL CHECK(length(codename) BETWEEN 1 AND 40),
    appearance_id TEXT NOT NULL,
    pronouns TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    current_mission_id TEXT,
    save_revision INTEGER NOT NULL DEFAULT 0 CHECK(save_revision >= 0),
    content_version TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mission_progress (
    campaign_id TEXT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    mission_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN
        ('locked','available','in_progress','evaluating','recoverable','completed')),
    best_competency TEXT,
    completed_at TEXT,
    PRIMARY KEY (campaign_id, mission_id)
);

CREATE TABLE IF NOT EXISTS achievements (
    campaign_id TEXT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    achievement_id TEXT NOT NULL,
    awarded_at TEXT NOT NULL,
    PRIMARY KEY (campaign_id, achievement_id)
);
```

The final DDL will be expanded and versioned during Phase 1. The above is executable example syntax but is **not an already installed DB**.

### 12.4 Atomic mission completion

Within a single transaction: verify expected campaign revision; verify mission and assessment; set completion state; record best skill evidence; award each unique achievement once; record permissible story effects; increment save revision; write outbox events. Commit only after all required writes succeed. After commit, dispatch events. On crash, resume from the committed revision and process pending outbox events idempotently.

### 12.5 Export/import and recovery

- Export profiles in a versioned archive containing `manifest.json`, save data and hashes; exclude transient caches, external tool binaries and personal packet captures.
- Verify archive size, member paths, CRC/content hash and schema version before import; never extract an untrusted archive without path traversal checks.
- Back up the database before migration. On migration failure, retain the prior copy and surface a useful recovery message.
- If content dependencies disappear, preserve historical completion records, label unavailable scenes clearly and offer a safe recovery route.
- Restore `in_progress` lab activities to `recoverable` after process termination; don't claim an interrupted real tool completed successfully.

---

# 13. State machines and transactional boundaries

### 13.1 Mission states

`LOCKED → AVAILABLE → IN_PROGRESS → EVALUATING → COMPLETED`; incorrect submissions return to `IN_PROGRESS` with feedback. Crashes or closed labs may enter `RECOVERABLE`, from which the player can restart the lab or resume a safe checkpoint. `REPLAYABLE` is a **UI capability** of completed missions, not a second durable completion state.

Transition conditions:

| Transition | Guard | Persistent effect |
|---|---|---|
| locked→available | prerequisite competencies fulfilled or eligible diagnostic waiver | unlock record |
| available→in_progress | player selects mission and save exists | attempt open |
| in_progress→evaluating | submission structurally valid | assessment attempt |
| evaluating→in_progress | insufficient evidence | feedback / no award |
| evaluating→completed | validator passes and safety checks hold | transaction: progress + award + event |
| in_progress→recoverable | interrupted, lab stopped or application reopened | cleanup metadata only |
| completed→replay | deliberate player action | separate practice attempt; no duplicate award |

### 13.2 Lab states

`NOT_READY → AVAILABLE → VALIDATED → STARTING → RUNNING → COLLECTING → COMPLETED`; errors lead to `FAILED` or `INTERRUPTED`, then `CLEANUP`. An adapter must never leave a started process orphaned during normal cancellation. A lab with missing dependencies is `NOT_READY`, but its simulation equivalent remains playable if provided.

### 13.3 UI / story transitions

Scene navigation is controlled by the Scene Manager. Story Engine returns a permitted next-scene ID based on stored flags and completion state. UI animation and dialog skipping are presentation-only; they cannot award skills. Each chapter ending sets one stable `chapter_completed` flag after capstone verification.

---

# 14. Simulated networking and terminal model

### 14.1 Simulation principles

The simulation is an educational discrete-event model, **not a complete TCP/IP implementation**. Every supported behavior must be accurate for its declared scope and limitations. Deterministic seeds make golden tests reproducible. Use a virtual event clock and bounded queues; avoid real wall-clock sleeps to grade simulated packet transport.

### 14.2 Device model

`Host`, `Switch`, `Router`, `Server`, `Interface`, `Link`, `Frame`, `Packet`, `Route`, `ARPCache`, `DNSRecord`, `DHCPLease`, `Service`. Device IDs separate labels from actual addresses; changing topology does not invalidate references. A topology manifest declares nodes, interfaces, links, prefixes, routes, and expected reachability.

### 14.3 Required simulation behaviors by chapter

- CH01: static IP/netmask/gateway, basic simulated ping, permissions and safe terminal navigation.
- CH02: MAC learning, forwarding, prefix membership, subnet math and IPv4/IPv6 identity examples.
- CH03: encapsulation, TCP handshake, DNS requests/responses, DHCP lease assignment, ARP mapping and protocol timelines.
- CH04: longest-prefix route selection, gateway errors, NAT mapping, TTL/ICMP/traceroute model and latency explanation.
- CH05+: visualize flows in fixtures or from the internal simulator, never fabricate packet facts for a real capture.

### 14.4 Simulated terminal grammar

Use a fixed parser/dispatcher for documented commands (`help`, `pwd`, `ls`, `cd`, `cat`, `ip addr`, `ip route`, `ping` in controlled simulation, `clear`). Arguments are parsed by our grammar and never handed to an OS shell. Unexpected commands receive informative feedback, not system execution. No `eval`, `exec`, or shell passthrough. A `sudo` teaching example may be simulated but must not request a real admin password.

### 14.5 Accuracy tests

For each simulated protocol, include reference examples and tests for normal, failed, boundary and misleading cases (e.g. no default route, conflicting IPv4 subnet masks, DNS response with no route, ICMP blocked, TCP retransmission not necessarily compromise). Display packet source/destination and timeline in consistent units.

---

# 15. Real tool integrations and chapter lab contracts

### 15.1 Adapter architecture

Each tool adapter implements:

1. `check_available()` — inspect executable availability/version; no side effects.
2. `validate(ApprovedLab, request)` — verify signed/packaged fixture manifest, intended operation and permissions.
3. `start()` — bounded, explicitly player-approved action on controlled target/input.
4. `collect()` — parse normalized facts with input/evidence provenance.
5. `stop()` — cancel only the process/resources the adapter created.
6. `cleanup()` — remove bounded temporary lab artifacts and restore known state.

Tool adapters are independently tested with **fake executables** and offline fixtures. They expose structured results, not arbitrary stdout to be interpreted as proof. Tool versions are recorded for reproducibility.

### 15.2 Nmap (CH06, CH09/CH10)

- Primary workflow: conceptual scanning simulation; then a local service lab under player control.
- Allowed default target: loopback service `127.0.0.1` with explicit permitted port list, not a LAN CIDR or default gateway.
- Prefer normal user TCP connect methods where feasible; no implicit raw-socket permissions.
- Prefer generated XML results (`-oX`) or provided fixture XML; parse with a hardened parser and bounded file size.
- Whitelist fixed option sets and target exact validated endpoint; arguments passed as an array; **never** construct `shell=True` commands.
- Normalize host state, port, protocol, service label and uncertainty; do not claim a service vulnerability merely because a port is open.
- If Nmap absent, guided simulation remains accessible; mandatory real-tool requirements will clearly show the dependency.

### 15.3 Wireshark / TShark (CH05, CH09/CH10)

- Provide original synthetic `.pcapng` fixtures with SHA-256 checksums and expected analysis assertions.
- Player can open the capture in Wireshark; programmatic grader uses TShark `-r <approved-file>` on saved evidence, not live capture.
- Lab controller fixes file path, permissible filter syntax and resource limits; output normalized by frame number, timestamp, protocol and relevant selected fields.
- Default game cannot initiate interface capture or require membership in `wireshark` group. Live capture remains optional and outside mandatory core progression.
- Capture interpretation explicitly distinguishes plaintext content, packet headers, TLS-visible metadata and information not observed.

### 15.4 John the Ripper (CH07, CH10)

- Only synthetic, purpose-generated weak hashes embedded in lab fixtures; no import of real passwords or protected credential stores for graded core missions.
- Supplied small wordlist and bounded work factors; avoid GPU-accelerated or unbounded cracking tasks in default labs.
- Adapter records fixture ID, John version, allowed mode and elapsed/result summary; plaintext training examples need not persist in normal saves.
- Teach hashing versus encryption, salt uniqueness, key stretching and why failed small-wordlist results do not prove that a password is strong.

### 15.5 Burp Suite Community Edition (CH08, CH10)

- Launch a deliberately vulnerable test web application on `127.0.0.1` with a random unprivileged port and a generated nonsecret session token.
- Player configures Burp's local proxy for only this lab (or uses Burp's browser); capture/repeat harmless training requests.
- Server stores rubric-relevant lab state so the game can grade without scraping Burp's UI or assuming paid scanner APIs.
- Local app must be isolated from real user data, expose no public interface, and reset between attempts. Potential CSRF and authorization lessons remain within fixture account identities.
- Use only Community features: manual Proxy/History, Repeater, Decoder/Comparer where relevant. Do **not** require Professional's automated vulnerability scanner.

### 15.6 Optional tools later

Scapy may help generate fixtures or simulate packet structure; it is *not* required in the Phase 0 development environment. Suricata, Zeek and other defensive tools can be added later via adapters. Avoid all-in-one install scripts for heavy cybersecurity packages before their chapter.

---

# 16. Security policy, threat model and containment

### 16.1 Trust boundaries

| Input or boundary | Threats | Mitigations |
|---|---|---|
| Mission JSON / mod pack | disguised executable payload, traversal, massive inputs | structural schema, path roots, size limits, no code execution |
| External tools | command injection, process runaway, unauthorized scan | fixed argv, option allowlist, restricted targets, timeouts, output caps |
| Local lab services | accidental external exposure, unsafe state leakage | loopback bind, ephemeral isolated state, server timeout, reset |
| Uploaded PCAP/XML/archive | malformed parser input, resource exhaustion | content/type checks, size ceilings, hardened parser, no privileged parsing |
| Save/import data | corruption, malformed state, path traversal | schema versions, migration, checksum/CRC, atomic backups |
| Player-entered strings | unsafe formatting, log injection | length limits, rendering escapes, normalized storage |
| Future third-party content | untrusted dependencies or executable mods | signed/verified manifests where applicable, no arbitrary Python plugin execution |

### 16.2 Allowlisting is necessary but not sufficient

A validated target string alone cannot guarantee isolation. For network-active lab actions, enforce an independent technical boundary such as a loopback-only process with controlled listening services, and review container/network namespace isolation before adding multi-host labs. Re-check the resolved target immediately before launching tools. Do not accept user-supplied command fragments or shell metacharacter interpretations. **Never perform background scans without express player action.**

### 16.3 Technical safeguards

- Strict `subprocess.Popen`/`run` with argument arrays and `shell=False`.
- Non-root runtime by default; no automatic `sudo`, Wi-Fi scanning, route changes, firewall edits or arbitrary filesystem inspection.
- Approved fixtures included in verified install trees; normalize and confine paths with a canonical root check.
- Timeouts, memory/output limits where supported, and controlled process termination.
- Restrict unexpected DNS resolution and network egress for offline exercises through environment isolation rather than only UI text.
- Logs record selected lab operation, fixture hash and result code; omit secrets and data that would reveal unrelated user traffic.
- Clearly distinguish simulated commands from actual OS commands in UI.
- Security regression tests attempt prohibited targets and malformed command arguments to verify refusal **without actually scanning them**.

### 16.4 Ethics and disclosure content

Students learn informed authorization, scope boundaries, least privilege, responsible disclosure, privacy-aware evidence preservation and limitations of inference. The player does not gain story rewards for attacking real networks. Narrative choices involving indiscriminate exposure are presented as fiction with consequences; labs never execute them.

---

# 17. Content, graphics, audio and localization pipeline

### 17.1 Visual direction

Original, grounded techno-thriller art: dark blue/teal infrastructure rooms, readable console monitors, stylized portraits, subtle network diagrams and limited motion. Image references are *mood boards*, not source assets. Build or license every distributable asset with attribution and reuse rights.

### 17.2 Sprite / scene requirements

- Scene backgrounds, character portrait layers, expression variants, UI panels, icons and network nodes use stable asset IDs.
- Asset packs include pixel dimensions, license, attribution, fallback text and original source location.
- Avoid embedding critical text inside images; keep it localizable and scalable.
- All information-bearing animations have a static or step-through alternative.
- Subtitle/caption transcripts for dialogue, effects indicating security-relevant events and voiceovers.

### 17.3 Asset organization

Store source design files separately from runtime compressed assets when practical. Build tools validate references, optimize resolution and create a per-release asset manifest with hashes. UI resources use a theme token system and accessible contrast validation.

### 17.4 Audio roadmap

v0.1 needs basic effects and optional background ambiance only; full voice acting is not required. v0.2+ may introduce narration in chapter anchors. Speech is never the sole source of essential evidence. Allow subtitles, independent volume, mute, and caption replay.

### 17.5 Localization

Player-facing text uses stable `text_key` IDs and safe interpolation placeholders. Initial language English; localization can be added after core UI text layout is ready. Keep command syntax, IP addresses and protocol names unmodified while translating instructional explanations. Player naming is rendered as untrusted text.

---
# 18. Repository, dependencies and release packaging

### 18.1 Phase 0 starter repository

The companion ZIP is a **scaffold and diagnostic**, not a game. It contains this master document, the 100-entry catalog, install scripts, `pyproject.toml`, a read-only `python -m nulltrace` environment doctor, an optional Pygame graphical smoke test and starter tests. Phase 1 creates the actual scene/game engines. The repository's version is `0.0.0` until the first vertical-slice release (`0.1.0`).

### 18.2 Dependency policy

- Use the per-project `.venv`; never `sudo pip install` application dependencies or override OS-managed Python's safety controls.
- Main Phase 0 pin: `pygame-ce==2.5.8`; pytest is a dev extra. Python package name is `pygame-ce`, but import name is `pygame`.
- Keep transitive versions in a release lock/constraints file once Phase 1 dependency resolution succeeds on the two target platforms.
- Avoid installing `pygame` alongside `pygame-ce` in the same environment, which can lead to package conflicts.
- Audit dependencies and record source/license before distribution.
- External system utilities are not installed via pip. Install at the phase where needed; document platform-specific detection and permission requirements.

### 18.3 Release artifacts

For each release: source tag, changelog, content manifest, schema migration list, golden tests, checksums, Linux release artifact, Windows release artifact, troubleshooting guide and known issues. Build Windows packages on Windows and Linux packages on Linux; PyInstaller is not a general-purpose cross-compiler.

---

# 19. Development environment: Ubuntu and Windows

### 19.1 Target machine and installation strategy

Primary: Ubuntu Linux dual boot, modest 8 GB RAM hardware. Keep each security tool optional to avoid installing a heavy suite on day one. The Phase 0 environment installs **Python dev tooling and Pygame only**, plus pytest. Git and VS Code can be reused if already installed.

### 19.2 Ubuntu: one-time prerequisites

Run these in Ubuntu Terminal (network access required for package installation):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 --version
git --version
```

If `python3 -m venv` fails despite installation, inspect the error and verify `python3-venv` was installed for the active system Python version. Do not add third-party PPAs unless a later documented requirement genuinely demands one.

### 19.3 Extract project and run Phase 0 installer

Download the supplied `NULLTRACE_Phase0_Starter.zip` and extract it to `~/Documents/nulltrace`. If the ZIP extracts as `NULLTRACE_Phase0`, rename that folder to `nulltrace`. Then:

```bash
cd ~/Documents/nulltrace
bash scripts/setup_ubuntu.sh
source .venv/bin/activate
python -m nulltrace --strict
python -m pytest -q
python scripts/window_smoke_test.py
```

The installer does the following in order: checks Python and venv; creates a `.venv` only if absent; installs editable package with `[dev]` and bounded download retries; runs strict diagnostics and tests. It does **not** run scans, change network settings, install Nmap, or prompt for admin privileges. Pygame graphical smoke test displays a simple static window for up to eight seconds and may be run separately once a desktop session is active.

If running from a fresh shell without activating the venv:

```bash
cd ~/Documents/nulltrace
.venv/bin/python -m nulltrace --strict
.venv/bin/python -m pytest -q
```

### 19.4 Manual setup equivalent (Ubuntu)

```bash
cd ~/Documents/nulltrace
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m nulltrace --strict
python -m pytest -q
```

**Common mistake:** `python -m pip install -e .[dev]` without quotes can be expanded unexpectedly in some shells. Use `'.[dev]'` as shown.

### 19.5 Optional tool readiness (do not install as Phase 0 requirement)

```bash
command -v nmap || true
command -v tshark || true
command -v john || true
```

- **Phase 4 (packet analysis):** Install Wireshark/TShark using Ubuntu packages after reviewing packet-capture privileges. Offline PCAP analysis does not require permission to capture on a live network. Default labs never activate live capture.
- **Phase 5 (scanning):** Install Nmap from Ubuntu packages; game labs use only approved local services by default.
- **Phase 6 (password security):** Install John the Ripper from trusted distributions when required; use supplied synthetic hashes only.
- **Phase 7 (web security):** Install Burp Community from PortSwigger's official download; the trainer works with a loopback-only local web app. Do not rely on Burp Professional.

Installation options and package names may change, so re-check official instructions at implementation time rather than embedding arbitrary download URLs and scripts.

### 19.6 Windows environment

Use a recent compatible Python installation from python.org, Git, and VS Code. Extract to `Documents\\nulltrace`, then PowerShell:

```powershell
cd $HOME\Documents\nulltrace
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
.\.venv\Scripts\python.exe -m nulltrace --strict
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\window_smoke_test.py
```

This uses a session-scoped process invocation of the setup script and does not require permanently weakening PowerShell's execution policy. If your machine blocks script execution under organizational policy, perform manual `py -m venv .venv` and invoke `.venv\Scripts\python.exe` directly. Build Windows executables on the Windows operating system.

### 19.7 Troubleshooting matrix

| Symptom | Likely cause | Safe response |
|---|---|---|
| `No module named venv/ensurepip` | missing venv OS package | install `python3-venv` from Ubuntu repository |
| `externally-managed-environment` | trying global pip install | activate `.venv`, use `.venv/bin/python -m pip` |
| `No module named pygame` | dependencies not installed in active env | run setup; verify `which python` |
| `pip` SSL/network error | unavailable Internet/cert issue | repair connectivity; do not disable TLS verification |
| `display not initialized` | no graphical session/SDL issue | test inside Ubuntu desktop session, examine display logs |
| command `nmap` missing | optional tool not installed | expected before its phase |
| `Permission denied` during scan/capture | system privilege boundary | do not auto-elevate; use offline fixture or safe unprivileged lab |
| pytest cannot import `nulltrace` | not installed editable / PYTHONPATH missing | run setup or `PYTHONPATH=src python3 -m pytest -q` |
| process hung in external lab | tool timeout/cleanup bug | cancel owned lab; report log and return to last checkpoint |

---

# 20. Phased implementation plan and work packages

**Versioning:** `v0.1` is the first playable vertical slice, **not** a full first chapter. `v1.0` is the complete base game. Phase completion is gated by tests, not dates.

### Phase 0 — Architecture and environment (this deliverable)

- [x] Approve product vision, original story, customizable protagonist and narrative restrictions.
- [x] Define 10 chapters and 100 stable mission catalog records.
- [x] Choose modular architecture, core data contracts, safety policy and version strategy.
- [x] Specify release gates, test strategy and future modification policy.
- [x] Create master system specification and local environment scaffold.
- [ ] **User-local:** extract scaffold, install dependencies into `.venv`, run diagnostics and tests on Ubuntu.
- [ ] **User-local:** verify Pygame video smoke test displays correctly.

**Exit:** document and catalog exist; scaffold tests pass in verification environment; local Ubuntu installation is confirmed by user diagnostic output. No playable game exists yet.

### Phase 1 — v0.1 first vertical slice

**Work packages:**

1. Initialize scene manager, fixed-update clock, input mapping, responsive window, main menu.
2. Implement profile creator with validation, Alex/Ghost example preset and accessibility settings.
3. Create story engine with declarative S02–S08 sequence and dialogue renderer.
4. Implement constrained terminal commands and elementary network connectivity simulation.
5. Implement a mission state machine with assessment feedback and Chapter 1 opening loop.
6. Create initial SQLite schema, transaction wrapper, save/checkpoint and restart recovery.
7. Write automated golden-path tests and manual UI walkthrough scripts.

**Gate G1:** user can create character → investigate → fix route → discover log → record choice → quit → restart → resume; no double-awards or critical crashes. Keyboard and mouse paths pass.

### Phase 2 — v0.2 first chapter

**Work packages:**

1. Nine-stage lesson UI and progress/skill view.
2. Recruit/Operator/Specialist assistance settings and hint levels.
3. Complete CH01-M01 through CH01-M10 with verified quiz/simulation assets.
4. Introductory diagnostic with skip recommendations (but no capstone/ethics waiver).
5. Content validator for missions, lessons, scenes and rubric assets.

**Gate G2:** fresh beginner can finish all ten missions, receive feedback, resume correctly and progress into CH02; diagnostic cannot bypass ethics or capstone.

### Phase 3 — v0.3 networking and protocols

**Work packages:**

1. Topology renderer and discrete-event network model.
2. Addressing/subnetting, Ethernet/switching, IPv6 intro, protocol animations.
3. DNS/DHCP/ARP/TCP/UDP and application/TLS demonstration.
4. Routing-table/gateway/NAT/traceroute/ICMP and performance case engine.
5. Implement CH02–CH04 with correctness fixtures and visual explanations.

**Gate G3:** all route/protocol examples are technically reviewed, deterministic, and pass edge-case tests; simulator and visuals agree about the same state.

### Phase 4 — v0.4 packet analysis

**Work packages:**

1. Source/licensing workflow for synthetic PCAPNG captures and SHA-256 manifest.
2. TShark adapter with offline only, input bounds, field parsing and failures.
3. Player launch help for Wireshark UI, packet filters and known-answer grader.
4. Evidence locker and source frame references.
5. Implement CH05 and PCAP-based portions of later capstones.

**Gate G4:** mandatory exercises pass with supplied capture only, no live capture or elevated privileges; incomplete/corrupt captures fail safely.

### Phase 5 — v0.5 Nmap

**Work packages:**

1. Scope/policy file + loopback-only training service.
2. Nmap adapter with approved arguments, timeout, XML parsing and evidence normalization.
3. Simulated scan output for new learners and missing dependencies.
4. CH06 approved-reconnaissance missions and findings report.
5. Abuse-case tests for arbitrary endpoints/flags and malformed XML.

**Gate G5:** scanner cannot launch outside controlled default lab and every submitted finding correctly distinguishes exposure from compromise.

### Phase 6 — v0.6 authentication audit

**Work packages:**

1. Generate synthetic weak hash fixtures with known passwords and small test wordlists.
2. Safe John adapter with bounded resource usage and results normalization.
3. Security explanation UI for salts, key derivation, MFA and defense.
4. Implement CH07 and related capstone evidence.

**Gate G6:** all mandatory audits reproduce results with only game-owned fixture files and no real credentials; runtime remains bounded.

### Phase 7 — v0.7 web security

**Work packages:**

1. Local loopback web trainer with deliberately flawed access-control case and reset fixtures.
2. Instructional setup for Burp Community Proxy, HTTP History and Repeater.
3. Server-state validators, failure recovery and cross-platform process cleanup.
4. Complete CH08 and related capstone evidence.

**Gate G7:** Burp Community is sufficient, no Pro feature needed; training service never binds to external interfaces.

### Phase 8 — v0.8 integrated campaign

**Work packages:**

1. Incident case engine, timeline correlation, uncertainty rubric and report export.
2. Complete CH09, CH10 and their laboratory fixture subsets.
3. Implement relationships, branch foldback and three endings.
4. End-to-end story reachability and save/replay tests.

**Gate G8:** all 100 missions and all endings reachable under documented conditions; every compulsory capstone assessed using real evidence or controlled fixture outputs.

### Phase 9 — v0.9 release candidate

**Work packages:** performance/accessibility audit, data migration tests, integrity check, packaging proof, localization readiness, Windows/Linux QA, end-user documentation, bug triage, copyright/licensing review, regression tests and offline test matrix.

**Gate G9:** zero unresolved severity-1 issues; stable fresh installation and upgrades on both platforms; package manifests and documentation accurate.

### Phase 10 — v1.0 stable release

Publish tagged source + Linux/Windows builds and checksums, changelog, beginner guide, security limitations, troubleshooting and content credits. Gate requires sign-off for story completion, learning correctness, safe labs, portability and tested migrations.

---

# 21. Testing strategy, quality gates and definition of done

### 21.1 Test pyramid

| Layer | Representative tests | When |
|---|---|---|
| Pure unit | CIDR calculations, state machine transitions, ending resolver, rubric scoring | every change |
| Content schema | 100 IDs unique, DAG acyclic, referenced lessons/scenes/assets exist | every content update |
| Integration | lab fake executable, SQLite transaction/rollback, event outbox delivery | each relevant phase |
| Golden fixture | expected frame numbers, XML results, hash audits, HTTP trainer state | each tool phase |
| End-to-end | create profile → CH01 → save → resume; final capstone | release candidate |
| Security | reject unauthorized endpoint, shell args, oversized archives, traversal, malformed XML | any lab/content update |
| Accessibility | keyboard focus, caption parity, text scale, reduced-motion | each visual release |
| Performance | target laptop FPS, memory, process termination | before tagged release |
| Platform | Ubuntu and Windows install/uninstall, build, runtime and save paths | before tagged release |

### 21.2 Test data policy

Fixtures are non-sensitive, owned/generated for the game, reproducible from scripts where practical, and checksummed. No real passwords, private captures or third-party copyrighted screenshots in committed test fixtures. A fake adapter must support all failure codes so tests do not need actual port scans or password cracking.

### 21.3 Minimum gate checklist for each feature

- [ ] Requirements, acceptance criteria and safety classification exist.
- [ ] Code implements only documented responsibilities and interfaces.
- [ ] Unit and content tests pass; negative cases tested.
- [ ] Manual usability walkthrough completed.
- [ ] Settings, accessibility and error feedback are handled.
- [ ] Save/replay behavior checked; old saves unchanged unless migrated.
- [ ] External tool absent case handled explicitly.
- [ ] Security policy enforces scope and resource limits.
- [ ] Release notes identify what works and what remains unimplemented.

### 21.4 Priority severity model

- **Severity 1:** data loss, unauthorized network action, uncontrolled process, privilege escalation, game-blocking crash in mandatory storyline.
- **Severity 2:** reproducible broken required lesson, incorrect assessment, corrupted evidence, inaccessible critical control.
- **Severity 3:** minor visual issue, noncritical performance regression or optional-scene bug.

A release is blocked by unresolved severity 1 defects. Severity 2 requires explicit disposition before stable release.

### 21.5 Phase 0 tests provided

`tests/test_phase0.py` verifies exactly 100 mission records with unique IDs, required catalog fields, a complete project manifest and a read-only environment report. These are **scaffold** checks only. They do not validate teaching correctness or gameplay because the game has not been built.

---
# 22. Performance, observability and failure recovery

### 22.1 Performance policy

Aiming for an 8 GB RAM laptop:

- Fixed-timestep simulation or bounded update loop separated from render interpolation; target 60 FPS normal, optional 30 FPS mode.
- Preload only assets required for current scene and upcoming transition; release unused textures and audio resources.
- Avoid decoding large captures on the Pygame render thread; bounded workers and progress feedback for expensive reads.
- Normal core game target under ~1.5 GB RAM excluding separate external tools (measurement target, not verified capability).
- Cap evidence items shown per page, per-mission event queue length, tool output size, replay history and imported archive size.
- Do not run a VM, Burp, John and packet parsers simultaneously by default; lab manager limits active sessions.

### 22.2 Observability

Record time-stamped application logs by severity, active scene/mission IDs, error codes, adapter availability and elapsed process duration. Never log actual entered passwords, large imported captures or private user documents. Add opt-in diagnostic export with path redaction. Maintain basic non-identifying crash reproduction metadata (OS, app version, Python version, mission ID and error traceback).

### 22.3 Fail-safe behavior

| Failure | Response |
|---|---|
| Missing Pygame assets | substitute placeholder art + readable transcript where possible; dev build emits error |
| Missing external tool | lab marked unavailable; show install guidance and compatible simulation |
| Malformed mission content | validator rejects mission prior to play; release build never silently grants completion |
| Corrupt PCAP/XML | reject with specific fixture error; do not treat as empty valid evidence |
| Tool hang | terminate owned process tree within bounded timeout, clean temporary directory |
| Crash during save | retain last committed revision and retry outbox dispatch after restart |
| SQLite migration failure | restore prior backup and display recovery instructions |
| Lost Internet | core game continues; no remote dependency for mandatory content |
| Lab service port already in use | select validated available loopback port, then verify bound address |
| Accessibility setting unsupported in scene | fall back to static/transcript variant and record test failure |

---

# 23. Git, project governance and change control

### 23.1 Branch strategy

- `main` must remain installable and pass baseline tests.
- Short-lived branches named `feature/<module>`, `content/<chapter>`, `fix/<issue>`.
- Commits describe one coherent change; include test additions as relevant.
- Every release has an annotated tag (`v0.1.0`, `v0.2.0`, etc.) and notes.
- Never commit `.venv`, database saves, `.env` secrets, generated local logs or private real-world capture data.

### 23.2 Recommended starting Git steps (local computer)

```bash
cd ~/Documents/nulltrace
git init
git branch -M main
git add .
git commit -m "docs: establish NULLTRACE phase 0 specification and Python scaffold"
```

**Do not blindly add a GitHub remote:** first create or select the correct repository, verify no sensitive files are tracked, then add its actual URL. No remote is required for local Phase 0 checks.

### 23.3 Architecture decision records (ADR)

Capture a short note in `docs/adr/NNNN-title.md` when a decision materially changes interfaces, saved data, mission semantics or the threat model. Template:

```text
# ADR-NNN: Title
Status: Proposed / Accepted / Superseded
Context: Why the change is necessary
Decision: What changes and what remains stable
Alternatives: Options considered
Consequences: Testing, migration, risk, backward compatibility
Acceptance: Approval and date
```

### 23.4 Initial approved architecture decisions

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Python modular monolith, Pygame-CE for desktop | baseline |
| ADR-002 | JSON-authored missions + SQLite persisted progress | baseline |
| ADR-003 | Control and validate all real labs via adapters | baseline |
| ADR-004 | Offline-first, independent of cloud/AI | baseline |
| ADR-005 | Fixed central narrative truth, foldback branches | baseline |
| ADR-006 | Customizable protagonist, Alex/Ghost only demo preset | baseline |
| ADR-007 | Build vertical slice before 100 mission implementations | baseline |
| ADR-008 | Content IDs stable and saves migrated across releases | baseline |

### 23.5 Modification rule

Feature requests go into backlog, not directly into the current milestone. Any change to the mission IDs, lab safety model, base save schema or release scope requires an ADR and regression plan. Build a tested small system instead of merging unrelated projects into this codebase.

---

# 24. Future modifications and expansion roadmap

### 24.1 Compatibility promises

Public content ID formats, story flag namespaces, normalized lab results and save schema versioning should survive patch updates. Deprecate rather than silently remove fields. Breaking changes require a major content/runtime version, a migration path, and communication to users.

### 24.2 Planned optional expansions

| Horizon | Candidate addition | Architectural prerequisite |
|---|---|---|
| v1.x | additional defensive-networking and forensic case packs | mission/content schema and asset manager |
| v1.x | advanced network visualization and customizable practice | simulation API, performance budget |
| v2.x | optional adaptive AI study mentor | consent, privacy policy, human-readable offline fallback |
| v2.x | bounded custom mission editor | validator, versioned authoring format, no arbitrary code |
| v2.x | accessibility/voice narration content packs | localization and caption pipeline |
| v3.x | cooperative investigations | identity, synchronized case state, security review and dedicated server architecture |
| v3.x | instructor-managed assignments | permissions, isolation, moderation and content review |
| v4.x | optional 3D scenes and advanced simulation | presentation abstraction and independent assets |
| future | Android companion | separate UI/runtime/mobile security design; not a trivial Pygame desktop port |

These are options, **not promised release dates**. Their exact versions may change after experience with v1.0.

### 24.3 AI-mentor restrictions

If later introduced, an AI mentor may explain theory, suggest lessons, translate approved hints and help interpret evidence, but it must not silently start real tools, bypass authorization, generate graded results without verification or upload a user's private packet captures by default. Original offline instructional content remains authoritative for assessments.

### 24.4 Third-party mission packs

Mission packs contain declarative JSON/text/assets with size, source and license manifests. Require safe path resolution and content validation. No loading arbitrary `.py` scripts from community content. Tool adapters remain built-in and reviewed until a stronger permission and signature system is explicitly designed.

---

# 25. Risk register and limitations

| Risk | Probability | Impact | Planned mitigation |
|---|---|---|---|
| 100 missions exceed sustainable content workload | High | High | chapter-by-chapter gates, reusable lesson/rubric templates |
| Story repeats simplistic hacker tropes | Medium | High | evidence model, contradictory reports, nuanced factions |
| Technical inaccuracies teach wrong skills | Medium | High | protocol reference tests and peer review against authoritative docs |
| Real tools can reach unintended endpoints | Medium | Critical | simulation by default, loopback isolation, explicit approval, safety tests |
| Tool/OS updates break labs | High | Medium | adapter version checks and offline golden fixtures |
| Save migrations corrupt progress | Medium | High | transactions, backups, migration test suite |
| Cross-platform process differences | High | Medium | adapter separation and testing on both target OSes |
| Lower-end laptop struggles with simultaneous tools | High | Medium | tool scheduling, resource limits and lightweight default labs |
| Mission answers leak through fixture filenames | Medium | Medium | asset packaging review and varied evidence-based questions |
| Screens exclude keyboard-only users | Medium | High | accessibility acceptance from Phase 1 |
| Security content misunderstood as approval to scan networks | Medium | High | authorization orientation, owned targets and default-deny policy |
| Third-party artwork/license uncertainty | Medium | High | original or properly licensed art and attribution manifest |

### 25.1 Explicit unknowns carried into implementation

1. Final pixel art style and full licensed asset set are not created in Phase 0.
2. Full voice scripts and acted recordings are not created in Phase 0.
3. Exact tool version compatibility across Ubuntu/Windows will be verified at tool phases.
4. Individual mission sample packet captures, Nmap XML, hash fixtures and training web app have not been generated yet.
5. Full scene dialogue beyond core anchors will be authored and reviewed alongside chapters.
6. Detailed typed Python and JSON schemas here are implementation contracts, not completed APIs.
7. Local installation and graphics performance must be verified by the user on their machine.

These are **intentional planned tasks**, not hidden delivered features.

---

# 26. Phase 0 completion inventory and next actions

### 26.1 Deliverables included with starter

| Path | Delivered in Phase 0? | Purpose |
|---|---|---|
| `docs/NULLTRACE_Master_System_Design_v1.0.md` | Yes | authoritative specification |
| `content/missions/catalog.json` | Yes | 100 design-only mission records |
| `pyproject.toml` | Yes | Python package metadata, Pygame and test dependencies |
| `src/nulltrace/doctor.py` | Yes | read-only environment diagnosis |
| `scripts/setup_ubuntu.sh` | Yes | local Ubuntu venv installer |
| `scripts/setup_windows.ps1` | Yes | local Windows venv installer |
| `scripts/window_smoke_test.py` | Yes | separate optional Pygame graphics check |
| `tests/test_phase0.py` | Yes | manifest/catalog consistency checks |
| Pygame game scenes or actual playable mission | **No** | Phase 1 |
| Nmap/Wireshark/John/Burp integrations | **No** | Phases 4–7 |
| Real networking and content labs | **No** | future phases |

### 26.2 Completion criteria

**Design freeze** is complete when the master document and catalog are internally consistent, reviewable and checked into Git. **Local environment setup** is complete only after the extracted project installs on Ubuntu and the player's terminal returns successful diagnostics and tests. **Phase 1 is not started** until an actual playable mission is being implemented.

### 26.3 First 30-minute local setup session

1. Extract ZIP to `~/Documents/nulltrace`; open Terminal there.
2. Run `bash scripts/setup_ubuntu.sh`.
3. Activate venv: `source .venv/bin/activate`.
4. Run `python -m nulltrace --strict` and `python -m pytest -q`.
5. Optional: `python scripts/window_smoke_test.py` to verify graphical output.
6. Initialize Git and commit the Phase 0 baseline; record any error output in an issue/notes file.

**Do not install every cybersecurity tool at once; do not change live network settings to “verify” Phase 0.**

---

# 27. Acceptance scenarios and architecture examples

### 27.1 AT-01: create and resume a profile

**Given** no saves exist, **when** a player creates a character with a valid name and codename, **then** one profile and campaign is committed, the next scene appears, and relaunching the application restores identity and story position. Empty or excessively long names receive feedback; the application cannot crash or store invalid records.

### 27.2 AT-02: complete a mission exactly once

**Given** a passing validated submission for a currently active mission, **when** the completion command is submitted twice, **then** one completed state and one achievement award exist. The second request returns the existing result without duplicate rewards or repeating irreversible narrative consequences.

### 27.3 AT-03: refuse an unauthorized lab request

**Given** a player or mod supplies an unauthorized target or an unexpected Nmap option, **when** the adapter is asked to validate, **then** it rejects the request before creating any external process. A fake subprocess test must prove no command was launched; it must not attempt to scan the actual target.

### 27.4 AT-04: analyze a local PCAP offline

**Given** a provided hash-verified fixture and offline TShark installation, **when** a player submits supported frame and protocol observations, **then** the grader returns structured evidence with fixture hash and frame references, without accessing live interfaces.

### 27.5 AT-05: recover interrupted lab

**Given** a lab was running during abnormal termination, **when** the game restarts, **then** it marks the attempt recoverable, cleans orphaned resources it owns where possible, and offers a new safe run. It does not fabricate a passing result.

### 27.6 AT-06: branch the ending reproducibly

**Given** a complete dossier and final disclosure strategy, **when** the ending resolver runs repeatedly against the same save state, **then** it returns the same ending ID every time. All narrative branch choices remain consistent with saved evidence and explicit guard conditions.

### 27.7 AT-07: migrate saves without losing competency history

**Given** a v0.x save before a compatible schema revision, **when** the migration runs successfully, **then** every previously earned mission completion, competence and story choice is preserved, and the backup remains available. A deliberately failing migration must roll back or restore prior data.

### 27.8 AT-08: teach real technical limitations

**Given** an open port observed by Nmap, **when** a learner claims the host is compromised, **then** the rubric identifies insufficient evidence and explains what the result supports. Given TLS-protected traffic without endpoint keys, the grader must not reward unsupported plaintext claims.

### 27.9 AT-09: no installed security tools in Phase 1

**Given** Nmap, TShark, John and Burp are missing, **when** the player completes the opening chapter, **then** the main storyline and simulations function correctly. Tool dependencies are introduced only when their lab chapters are reached.

### 27.10 AT-10: Phase 0 environment doctor is safe

**Given** only a Python installation, **when** `python -m nulltrace` is run with the package import path configured, **then** it checks versions and executable paths without network requests, subprocess execution, privilege elevation or mutation of system files.

---

# 28. References and terminology

### 28.1 Authoritative technical references (retrieved/reviewed 2026-10-26)

- Python standard `venv` documentation: https://docs.python.org/3/library/venv.html
- Pygame Community Edition: https://github.com/pygame-community/pygame-ce
- Pygame-CE release list (v2.5.8, 2026-08): https://github.com/pygame-community/pygame-ce/releases
- Pygame-CE PyPI package (Python 3.10+): https://pypi.org/project/pygame-ce/
- pytest getting started: https://docs.pytest.org/en/stable/getting-started.html
- Nmap output format guide: https://nmap.org/book/man-output.html
- Nmap reference manual: https://nmap.org/book/man.html
- TShark manual: https://www.wireshark.org/docs/man-pages/tshark.html
- Wireshark User's Guide: https://www.wireshark.org/docs/wsug_html_chunked/
- John the Ripper official site and documentation: https://www.openwall.com/john/
- Burp Suite Community Edition scope/features: https://portswigger.net/burp/communitydownload
- Burp Suite getting started: https://portswigger.net/burp/documentation/desktop/getting-started
- OWASP Web Security Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

### 28.2 Key vocabulary

- **Adapter:** a safe, versioned wrapper normalizing a specific tool's operations/results.
- **Assessment:** deterministic evaluation of an answer, evidence or laboratory state.
- **Capstone:** integrated chapter operation demonstrating multiple competencies.
- **Content contract:** schema and validation rules governing missions, scenes, labs and lessons.
- **Evidence provenance:** origin and integrity information required to interpret an artifact.
- **Event outbox:** durable record of completed domain changes awaiting safe event dispatch.
- **Golden fixture:** intentionally prepared, checksummed lab input with a known expected result.
- **Mission DAG:** directed acyclic graph of mission/competency prerequisites.
- **Modular monolith:** a single deployed application with independent internal modules.
- **Phase gate:** measurable condition that must pass before declaring a release ready.
- **Recruit / Operator / Specialist:** levels of instructional support, not moral roles.
- **Synthetic hash:** deliberately generated training credential hash, not a user credential.
- **Vertical slice:** smallest fully functioning end-to-end portion proving the overall product workflow.

---

## Appendix A — Phase 0 engineering acceptance checklist

- [x] Product scope, non-goals and safety posture documented.
- [x] Core narrative, cast, canon, ending families and scene anchors specified.
- [x] Customizable protagonist and Alex/Ghost illustrative profile documented.
- [x] All 100 missions identified with objectives, activities and expected verification.
- [x] Application component boundaries, data contracts and state machines specified.
- [x] SQL sketch, migration, replay and transaction requirements specified.
- [x] Four tool adapter strategies and containment limits specified.
- [x] Ten staged release phases and acceptance gates defined.
- [x] Initial Ubuntu/Windows setup scripts and read-only diagnostic provided.
- [x] Content catalog and project integrity unit tests provided.
- [ ] Ubuntu environment installed **on player's laptop** and checks passed (requires local execution).
- [ ] Optional Pygame graphics smoke test passed **on player's laptop** (requires local execution).
- [ ] All 100 missions implemented or tested as gameplay (**future work, not Phase 0**).

## Appendix B — Controlled change log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-10-26 | Initial formal design baseline and Phase 0 environment scaffold |

**END OF MASTER SYSTEM DESIGN v1.0.0**

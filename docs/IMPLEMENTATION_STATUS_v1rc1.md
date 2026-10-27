# NULLTRACE v1.0.0-rc1 — Requirement coverage / gap audit

## What is implemented

- **Mission IDs:** 100 stable catalog entries, 100 distinct assessment items, all fully validated for question structure.
- **New learning:** 30 additional beginner-facing topic notes for Chapters 8–10, and access to the original 70 Chapter 1–7 activities.
- **Core UI:** Main menu, customizable player profile and operator animation, Story Archive, mission browser, knowledge checks, simulated terminal/network, case evidence board, tool labs, three ending scenes.
- **Story:** Full chapter 1–10 summaries, existing choices in Chapters 1, 5, 9 and a Chapter 10 disclosure selection. Three deterministic endings based on final choice and number of chapter evidence items.
- **Offline labs:** Bundled synthetic PCAP and NEXUS case JSON, TShark streaming adapter and case integrity validator; existing controlled Nmap and John integrations.
- **Web lab:** Only on explicit launch, synthetic local data, HTTP inspection and deliberate missing object-level authorization on the training server. A local receipt records request completion, not Burp itself.
- **Local saves:** Existing v0.6.1 SQLite schema unchanged, mission progression and story choices persist.
- **Report:** Opt-in Markdown synthetic dossier, with timeline provenance and uncertainty.
- **Quality controls:** 100-mission regression, target restriction tests, receipt expiry/corruption, preservation of pre-existing 70 mission content, QA-mode nonpersistent decisions, source build tests.

## Gaps versus Phase 0 master system design

| Requirement | Current state | Planned remedy |
|---|---|---|
| Nine-step lessons for every mission | New chapters have concise teaching notes and individual MCQs; not full nine stages | Author complete lessons, demos, exercises, mini-projects and capstones |
| Cinematic story scenes | Prose briefings and illustrated/animated player, not fully staged scenes | 2D environments, scene direction, sound and character dialogue assets |
| Burp workflow proof | Local HTTP request receipt; cannot verify which client was used | Instructor-reviewed or structured local request transcripts, without overclaiming tool provenance |
| Web security depth | One deliberately flawed synthetic object retrieval; no large vulnerable app | Expand supervised local labs covering sessions, mitigation and diverse HTTP cases |
| Incident investigation depth | One fixed offline dossier with five events and a reproducible discrepancy | Independent multi-artifact cases, editable analyst claims, report rubric and timeline builder |
| Advanced tool labs | Selected missions use opt-in adapters; many missions rely on assessment questions | Multiple progressive real-tool exercises and stronger evidence-based grading |
| Character customization | Name/codename and 3 basic outfits; procedural idle/walk/blink | Portrait/appearance editor, localization and accessibility options |
| Original visual/audio content | Basic functional HUD and code-drawn sprite | Illustrations, animation transitions, soundtrack, voiced optional dialogue |
| Windows binary / Linux executable | Editable Python source only | Build/test on each target OS with PyInstaller; signed release artifacts if applicable |
| Accessibility/UX | Basic GUI and keyboard answer controls | Formal font-scaling, contrast, reduced-motion, subtitles, navigation and responsive tests |
| Performance targets | Not benchmarked on target ThinkPad with full labs | Frame-time and memory profiling on user's hardware |
| Security architecture | Loopback and synthetic fixture boundaries; not container sandbox | Container/network namespace sandboxing where later labs require stronger isolation |

## Acceptance conclusion

Phases 7–10 are **implemented as an integration/release candidate**, not automatically completed production phases. Phase 7 is dependent on a real manual Burp Community exercise on the user's machine; graphical tests and cross-OS performance must also pass locally. The game remains a meaningful, evolving cybersecurity course prototype rather than the fully realized cinematic educational RPG described in the master system design.

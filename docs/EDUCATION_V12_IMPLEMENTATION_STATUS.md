# NULLTRACE Education v1.1–v1.2 — Implementation inventory

| System | Delivered | Notes |
|---|---|---|
| Nine-stage lesson library | Yes | Strictly validated schema; 100 unique IDs, ordered stages |
| Lesson content | Yes | 100 topic-specific lesson objects, 900 stages; narrative, definitions, explanations, examples, applications, exercise and mini-project prompts |
| Lesson visualizations | Partial | Interactive hop-by-hop **chapter-level** schematic; not packet replay |
| Real-tool teaching | Existing | Previously tested Nmap, TShark, John and local HTTP/Burp labs unchanged |
| Academy UI | Yes | Mission lesson stage navigation and per-chapter progress tracker |
| Practice quiz | Yes | Reuses mission question; not an independent final assessment |
| Topic mini-project | Partial | Typed field note with input checks; content isn't independently evaluated |
| Integrated operation | Existing + text | Legacy assessed mission and lab gates remain in place |
| Stage persistence | Yes | SQLite schema 2, additive tables only, idempotent entries |
| QA isolation | Yes | QA lesson progress kept in memory, not SQLite |
| Production cinematics | No | Planned v1.3–v1.5 |
| Native binaries | No | Existing source release; Windows packaging later |

This document differentiates working features from planned features to prevent incorrectly claiming full master-design parity.

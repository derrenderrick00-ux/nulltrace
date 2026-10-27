# NULLTRACE — v1.0.0-rc1 (Phases 7–10 integration candidate)

**Status:** Python/Pygame desktop **100-mission campaign prototype**, pending local Ubuntu acceptance and richer production content. This is **not** a claim of completed feature parity with `docs/NULLTRACE_Master_System_Design_v1.0.md`. Do not call this the stable v1.0 release until the full manual, content, performance and accessibility gates are met.

The upgrade builds on your existing **v0.6.1**, preserving previous Nmap, TShark, John and operator-animation changes. Adds:

- **Phase 7:** 10 Chapter 8 web-security missions, 10 brief teaching cards, synthetic loopback training web application and manual Burp Community exercises.
- **Phase 8:** Chapters 9–10 (20 more assessed missions and teaching cards), synthetic incident dossier, story choices, three endings and Markdown report export.
- **Phase 9:** Regression tests, secure loopback lab validation, old-save compatibility and a release acceptance matrix.
- **Phase 10:** Versioned `v1.0.0-rc1` source release and automated verification script; stable cross-platform binary packaging is **not complete**.

## Ubuntu upgrade from v0.6.1 (preserves player saves)

Download the upgrade ZIP into `~/Downloads`. Back up first:

```bash
cd ~/Documents
mkdir -p nulltrace-backups
# Back up code but exclude virtual environment and local temporary files.
tar --exclude='nulltrace/.venv' --exclude='nulltrace/__pycache__' \
  -czf nulltrace-backups/source_before_v1rc1.tar.gz nulltrace
if test -f ~/.local/share/nulltrace/campaign.sqlite3; then
  cp -a ~/.local/share/nulltrace/campaign.sqlite3 \
    nulltrace-backups/campaign_before_v1rc1.sqlite3
fi
```

Upgrade **into the existing root** (no new nested project directory):

```bash
unzip -o ~/Downloads/NULLTRACE_Phases_7_to_10_v1.0.0-rc1.zip -d ~/Documents/nulltrace
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m pip install -e '.[dev]'
bash scripts/verify_phases_7_to_10.sh
python -m nulltrace
```

If you keep saves at a custom location (`NULLTRACE_SAVE_DIR` or `XDG_DATA_HOME`), back up that location too. The ZIP contains **no** user SQLite save file; the SQLite schema is unchanged. Existing completed missions retain their original IDs.

## Runtime / controls

```bash
python -m nulltrace               # Normal campaign (prerequisites enforced)
python -m nulltrace --qa          # Developer mode; missions/decisions not saved
python -m nulltrace --strict      # Environment diagnostic
python -m nulltrace --list-missions
python -m nulltrace --lab incident # Offline synthetic evidence case review
python -m nulltrace --lab packet # Existing offline TShark integration
python -m nulltrace --lab nmap   # Existing loopback-only Nmap exercise
python -m nulltrace --lab john   # Existing generated-hash exercise
python -m nulltrace --lab web    # Check web-training receipt; does NOT launch server
python -m nulltrace --web-lab    # Start bounded 127.0.0.1 training HTTP portal, Ctrl+C stops
python -m nulltrace --export-dossier ~/Documents/nulltrace_case.md
```

Controls: mouse click; keyboard `1`–`3` for assessment answers; `Esc` for navigation; on Operations Floor, `WASD`/arrows move the character and `M` toggles reduced motion. Alex/Ghost/hoodie is a customizable sample, not mandatory.

## Chapter 8 manual Burp Suite Community exercise

1. Open **Terminal A**, activate `.venv`, and run `python -m nulltrace --web-lab`. It prints the assigned local URL, e.g. `http://127.0.0.1:NNNN/` (the port varies). Keep it running.
2. Use a **Burp Suite Community** browser/proxy configured for the **printed local URL only**. Review the synthetic `case=alpha` request. Send it to Repeater.
3. In Repeater, change the query parameter to `case=mirror` and add header `X-Nulltrace-Review: authorized`. Submit; observe the different synthetic case record. This demonstrates the intentionally missing case-owner authorization control.
4. Open **Terminal B**, activate `.venv`, and run `python -m nulltrace --lab web`. Expected mode: `local-http (pass)`; the receipt proves only that the loopback request was made, **not which HTTP client was used**.
5. Start the game and attempt CH08-M06/M07/M08/M10, or the later CH10-M06. Press **RUN CONTROLLED WEB LAB** in each relevant assessment to verify the receipt. Submit the assessment separately.
6. Press `Ctrl+C` in Terminal A to stop the portal. The receipt is valid for seven days and can be repeated at any time.

Only fictional records exist. The HTTP server binds to **127.0.0.1**; do not change it to `0.0.0.0` or forward its port to other hosts. This is a **deliberately vulnerable lab**, not a production application. For a detailed guide, read `docs/WEB_BURP_LAB_GUIDE.md`.

## New storyline and final mission

Chapters 8–10 cover web sessions and object authorization, incident investigation, and final cross-source correlation. In the **Chapter 10 Story Archive**, choose a **disclosure route** (independent oversight, broad release, or restricted review). This is required before completing CH10-M10. The final story scene shows one of three outcomes, determined by the selected route and collected chapter evidence. An optional **EXPORT TRAINING DOSSIER** button in the Case Board saves a Markdown report to the local user-data directory. It never automatically contacts a server.

## Automated and manual acceptance

```bash
bash scripts/verify_phases_7_to_10.sh
```

Read **`docs/PHASES_07_TO_10_ACCEPTANCE.md`**. The automated gate does not exercise the real Burp GUI or verify Windows builds; the user must conduct those manually. Our packaging environment ran the non-Pygame tests only and did **not** perform your local Burp interaction.

## Project layout

- `content/missions/catalog.json`: unchanged 100 stable IDs with updated content status.
- `content/missions/assessments_01_07.json`: original 70 preserved assessments.
- `content/missions/assessments_08_10.json`: 30 new individual assessments.
- `content/chapters/lesson_notes_08_10.json`: 30 concise topic explanations for newer chapters.
- `src/nulltrace/labs/web_training.py`: explicit loopback synthetic web training portal.
- `src/nulltrace/labs/incident.py`: offline forensic-training fixture validator.
- `src/nulltrace/investigations/report.py`: Markdown evidence report export.
- `src/nulltrace/story/endings.py`: deterministic branching narrative outcomes.
- `tests/`: legacy and current regression tests.
- `docs/`: full original master design and explicit release gap reports.

## Honest scope limitations

The campaign has 100 individually graded questions and some controlled tool labs. It **does not yet** provide 100 cinematic scenes, full nine-stage interactive lessons for each mission, deeply interactive real-world tool exercises in every chapter, voice acting, rich original art, or a finished accessibility review. The web lab checks a self-reported localhost request; it cannot prove Burp was used. The incident correlation is performed on a bundled **fictional** case dossier. Python source and tests are packaged; Linux/Windows standalone executables remain future release engineering work. See `docs/IMPLEMENTATION_STATUS_v1rc1.md`.

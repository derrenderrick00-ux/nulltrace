# NULLTRACE — The Cybersecurity Chronicles

**v1.2.0-rc1 | Education expansion candidate (v1.1–v1.2)**

NULLTRACE is a Python/Pygame single-player, offline-first cybersecurity learning-game prototype set in the fictional NEXUS universe. It contains 100 existing assessed missions plus a new **nine-stage Academy for each mission** (900 study stages). The Academy is intentionally separate from the graded missions: reading text or saving a reflection does **not** certify cybersecurity competence.

## Install or upgrade on Ubuntu

Back up your existing SQLite save and source first. Extract the release **into the existing project root**, retaining `.venv`, then:

```bash
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m pip install -e '.[dev]'
bash scripts/verify_education_v12.sh
python -m nulltrace
```

Detailed user acceptance and migration instructions: `docs/EDUCATION_V1_1_TO_V1_2_ACCEPTANCE.md`.

## Gameplay

1. Create an operator (Alex/Ghost/hoodie is an editable example) or select an existing profile.
2. Open **ACADEMY**, choose a chapter and a mission.
3. Navigate **Objectives → Terms → Step by step → Visual model → Worked example → Real-life application → Practice → Mini-project → Integrated operation**.
4. Mark stages after studying; inspect the chapter-level hop diagram; answer the practice check; write your own short evidence note.
5. Use **MISSION ASSESSMENT** for the original separately graded challenge. Applicable external tool labs remain explicitly user-triggered.

Stage progress persists per player in SQLite, separate from mission completions. Previously completed missions stay completed after the additive database migration. In `--qa` mode, no progress is persisted.

## Commands

```bash
python -m nulltrace                 # Pygame campaign
python -m nulltrace --qa            # QA mode, does not save educational progress
python -m nulltrace --strict        # Environment check
bash scripts/verify_education_v12.sh # Automated regression + GUI smoke
python -m nulltrace --lab packet    # Offline synthetic TShark lab
python -m nulltrace --lab nmap      # Game-owned 127.0.0.1 TCP scan
python -m nulltrace --lab john      # Generated training hash
python -m nulltrace --web-lab       # Local HTTP training server for Burp
python -m nulltrace --lab web       # Checks manual local HTTP receipt
python -m nulltrace --lab incident  # Synthetic evidence dossier
```

## Safety boundaries

No automatic home-network scanning or credential collection. The virtual terminal never launches shell commands; Nmap is restricted to a temporary localhost listener, TShark reads a bundled synthetic PCAP, John uses synthetic hashes, and Burp interacts only with a user-launched localhost training server. The v1.2 verification script does not launch any real security tools.

## Engineering notes

- Python >=3.10, pygame-ce 2.5.8, pytest; tested on Ubuntu by user in prior version with Python 3.14.4.
- Mission catalog: `content/missions/catalog.json`; assessments unchanged.
- Nine-stage declarative lesson content: `content/lessons/lesson_stages_01_10.json`.
- Lesson library validation: `src/nulltrace/education/lessons.py`.
- UI: `src/nulltrace/ui/app.py`.
- New saved stage and note tables: `src/nulltrace/persistence/store.py`.
- Acceptance: `docs/EDUCATION_V1_1_TO_V1_2_ACCEPTANCE.md`.
- Original GDD: `docs/NULLTRACE_Master_System_Design_v1.0.md`.

## Known gaps

The lesson experience includes explanatory content, a chapter-level flow visualization, one practice check and an ungraded mini-project reflection. It does **not** yet provide bespoke simulations for each of the 100 missions, distinct independent mastery tests, fully staged cinematics, original animated environments, professional voice performances, or standalone multi-platform installers. These are subjects for subsequent design/release stages. **Do not claim v1.2 is production-complete before manual acceptance.**

# NULLTRACE — The Cybersecurity Chronicles

**v1.5.0-rc1 • v1.3–v1.5 Cinematic and Interactive Investigation Candidate**

Offline-first Python/Pygame cybersecurity learning thriller. **100 assessed missions, 900 Academy stages, 10 captioned five-beat cinematics, 10 synthetic evidence investigations, and ten offline network-journey scenarios.**

## Installation on Ubuntu

Requirements: Python 3.10–3.15 declared (owner-tested Python 3.14.4 on Ubuntu in prior releases), Python venv, Python package download access, Pygame-CE 2.5.8 (installed automatically), and optional security tools for practical labs. 8 GB RAM recommended.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git unzip
cd ~/Documents/nulltrace
bash scripts/setup_ubuntu.sh
source .venv/bin/activate
bash scripts/verify_cinematics_v15.sh
python -m nulltrace
```

**If upgrading from v1.2:** back up `~/.local/share/nulltrace/campaign.sqlite3`, create `feature/cinematics-v1.5` from `feature/education-v1.2`, and unzip the full-source upgrade over the existing project root while preserving `.venv` and Git. This update uses an **additive SQLite table**. Full steps and fresh ZIP/GitHub download instructions in [`docs/USER_MANUAL_v1.5.md`](docs/USER_MANUAL_v1.5.md).

## Where to play

- **Story Archive:** `WATCH CINEMATIC` (manual/replay/auto), `OPEN CHAPTER CASE` (gather supporting records), `PACKET JOURNEY` (step-through simulation).
- **Academy:** 100 nine-stage lessons; mission assessment remains a separate knowledge check.
- **Evidence Board / Network Map:** report and trace entry points.
- **Operations Floor:** WASD/arrow keys and procedural operator sprites.
- **Tool Labs:** optional user-started, controlled TShark, loopback Nmap, synthetic John, and local Burp exercises.

## Essential commands

```bash
python -m nulltrace                 # Play the game
python -m nulltrace --qa            # Developer QA (no game progress saved)
python -m nulltrace --strict        # Environment diagnostics
bash scripts/verify_cinematics_v15.sh
python -m nulltrace --lab incident  # Safe offline synthetic report
```

## Documentation

- **Player installation and controls:** `docs/USER_MANUAL_v1.5.md`
- **Code architecture and extension guide:** `docs/DEVELOPER_MANUAL_v1.5.md`
- **Full master design and future modification roadmap:** `docs/NULLTRACE_Master_System_Design_v1.5.md`
- **Release tests:** `docs/V1_3_TO_V1_5_ACCEPTANCE.md`
- **Implemented versus future gaps:** `docs/V1_5_IMPLEMENTATION_STATUS.md`
- **Historical Phase 0 design:** `docs/NULLTRACE_Master_System_Design_v1.0.md`

This is **a functional cinematic educational prototype**, not a fully voiced 3D hacker game, not a professional certification, and not a sandbox for unapproved real networks. The authoring environment passed non-GUI tests; Ubuntu acceptance is required before calling v1.5 stable.

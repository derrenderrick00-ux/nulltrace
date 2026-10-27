# NULLTRACE — User Manual

**Version:** v1.5.0-rc1 (v1.3–v1.5 gameplay enhancement candidate)  
**Audience:** New players, instructors, and testers  
**Platforms:** Ubuntu Linux primary; Windows source installation supported but requires local testing  
**Status:** Release candidate. Do not confuse a passing test suite with full cinematic production completion.

## 1. What NULLTRACE is

NULLTRACE is an offline-first, 2D educational cybersecurity thriller built with Python and Pygame-CE. The current campaign includes **100 assessed missions**, **100 Academy lessons with nine stages each (900 total)**, **10 chapter cutscenes with five dialogue beats each**, **10 synthetic evidence investigations**, and an **offline animated packet-journey simulator**. Four optional real-tool lab integrations teach analysis with TShark/Wireshark, Nmap, John the Ripper and Burp Suite Community Edition. Those tools are controlled/authorized and are not required to open the game.

An illustrative operator is **Alex / Ghost / hoodie**. You can create a different identity. This is an instructional game, not an externally accredited certification or a production penetration-testing system.

## 2. System requirements

| Item | Requirement / recommendation |
|---|---|
| Operating system | Ubuntu 26.04 x86-64 tested by project owner on previous releases; modern Linux distributions with working SDL2, or Windows 10/11 |
| Python | Python **3.10–3.15**, according to the declared project range. **3.14.4** is the owner-tested runtime; other versions require verification |
| Pygame | `pygame-ce==2.5.8`, installed by the setup script |
| RAM | **8 GB recommended**, especially if Burp, Wireshark and the game run together |
| Disk | Allow at least **1 GB free** for source, virtual environment and downloaded Python packages; extra disk for optional security tools |
| Display | Desktop display capable of **1180 × 720** logical rendering, scaled for smaller/larger windows |
| Keyboard/mouse | Both recommended; mouse is necessary for some controls |
| Network | Needed to download Python packages or clone from GitHub; **not required** for the campaign or simulated exercises |

Optional security tools: `tshark`, `nmap`, `john` and Burp Suite Community. These are **not** installation prerequisites for ordinary gameplay. Burp/Java and Wireshark may need separate installation through their official sources. Live sniffing is not used by compulsory lessons.

## 3. Downloading the source files

### Option A — Upgrade an existing v1.2 installation (recommended for current players)

1. Download **`NULLTRACE_v1.3-v1.5_Cinematic_Investigations_Upgrade.zip`** from the conversation.
2. Place it in `~/Downloads` (Ubuntu) or Downloads (Windows).
3. Back up the existing source and private campaign save using the instructions below.
4. Extract into the existing NULLTRACE directory. **Do not delete `.venv` or your user saves.**

### Option B — New installation from the ZIP

Download the same complete-source ZIP, extract it into a new `nulltrace` folder, and run the setup script for your operating system. The ZIP contains the whole source tree; **you do not need earlier update ZIPs**.

### Option C — GitHub source checkout

Repository: `https://github.com/derrenderrick00-ux/nulltrace.git`. Clone it with:

```bash
git clone https://github.com/derrenderrick00-ux/nulltrace.git
cd nulltrace
```

Use the appropriate release tag or feature branch **once the new v1.5 code has actually been pushed**. The remote may currently contain only v1.2, so cloning `main` does not necessarily give you v1.5 until it is merged or released. Check `git branch -a` and `git tag -l` rather than assuming a branch exists.

## 4. Installation on Ubuntu (fresh source)

Install prerequisites:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git unzip
```

If installing from the downloaded ZIP into a new folder:

```bash
mkdir -p ~/Documents/nulltrace
unzip ~/Downloads/NULLTRACE_v1.3-v1.5_Cinematic_Investigations_Upgrade.zip -d ~/Documents/nulltrace
cd ~/Documents/nulltrace
bash scripts/setup_ubuntu.sh
source .venv/bin/activate
```

**Important:** Don't pre-create an additional nested `NULLTRACE_Phase0` directory or run `mv` into an existing target folder. Verify `ls scripts/setup_ubuntu.sh` exists under the current `nulltrace` root.

Run the v1.5 verification and launch:

```bash
bash scripts/verify_cinematics_v15.sh
python -m nulltrace
```

Quit the Pygame window normally to return to the terminal. In a later shell session, activate the same environment again:

```bash
cd ~/Documents/nulltrace
source .venv/bin/activate
python -m nulltrace
```

## 5. Upgrading safely from v1.2 on Ubuntu

Before extraction, **close the game and local training-web server**, then run:

```bash
cd ~/Documents/nulltrace
mkdir -p ~/Documents/nulltrace-backups
tar --exclude=.venv --exclude=.git -czf ~/Documents/nulltrace-backups/before_v15_source.tar.gz .
if [ -f ~/.local/share/nulltrace/campaign.sqlite3 ]; then
  cp -a ~/.local/share/nulltrace/campaign.sqlite3 \
    ~/Documents/nulltrace-backups/campaign_before_v15.sqlite3
fi
```

Ensure you are working on the v1.2 branch and commit it first if necessary. Create a new feature branch (`git switch -c feature/cinematics-v1.5`) rather than modifying `main` directly. Then:

```bash
unzip -o ~/Downloads/NULLTRACE_v1.3-v1.5_Cinematic_Investigations_Upgrade.zip -d ~/Documents/nulltrace
source .venv/bin/activate
python -m pip install -e '.[dev]'
bash scripts/verify_cinematics_v15.sh
python -m nulltrace
```

The v1.5 case-history table is **additive**: existing operators, completed missions, Academy stages, field notes, and story decisions are not reset. Exporting a separate copy of your SQLite save first remains strongly recommended.

## 6. Installation on Windows (PowerShell)

Install Python with `py` or `python` available, then install Git if you plan to clone from GitHub. Extract the ZIP into a directory such as `C:\Users\<you>\Documents\nulltrace` and run PowerShell **in that directory**:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m nulltrace
```

If PowerShell script execution is restricted, you can perform the script actions manually: `py -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`. Do not globally disable security policies. Windows packaging and GUI acceptance for this release have not been confirmed.

## 7. Navigation and controls

**Main Menu / Command Center:** select or create a profile, continue a mission, access the Operations Floor.  
**Chapters:** choose one of ten chapters; normal mission prerequisites still apply.  
**Academy:** review objectives, terminology, explanations, visual diagrams, examples, applications, exercises, field-note practice, and integrated assessments.  
**Story Archive:** choose a chapter, then `WATCH CINEMATIC`, `OPEN CHAPTER CASE`, or `PACKET JOURNEY`.  
**Evidence Board:** inspect previously earned evidence and launch the active chapter case.  
**Network Map:** inspect simulated IP addresses and routes; select `PACKET JOURNEY` for a step-by-step animation.  
**Tool Labs:** user-triggered security demonstrations; real operations only in approved offline/loopback environments.

**Controls:** Click buttons. `ESC` returns to a previous menu; `WASD` or arrow keys move the operator in the Operations Floor; `M` toggles reduced character motion in that room. Cutscene controls: click **NEXT**, **PREV**, **AUTO PLAY**, **RESTART**, or press `SPACE` (next), `R` (restart), `M` (reduced motion). Packet journey: **STEP**, **AUTO PLAY**, **RESET**, **GATEWAY ON/OFF**; also `SPACE` and `R`. Page Up/Page Down and the mouse wheel scroll longer Academy explanations.

The cinemas have captions and manual navigation; there is no recorded voice acting. Some long buttons shorten their display text rather than enlarging the window.

## 8. How to complete an investigation

1. In Story Archive, select a chapter and click **OPEN CHAPTER CASE**.
2. Read the fictional case briefing and the evidence statements.
3. Click relevant records to select them. The evidence kind distinguishes observation, limitation and claim.
4. Select the conclusion best supported by those observations.
5. Click **VERIFY CASE**. If a required record is missing, the engine explains that additional support is required. If the conclusion overstates the record, retry.
6. A successful, non-QA submission writes an idempotent case-completion record for that player. **It does not automatically complete a numbered mission**.

Ten case files are available—one per chapter. They use entirely synthetic, authored data. A correct click sequence verifies reasoning about the supplied fixture, not a professional incident investigation.

## 9. Controlled tools and CLI

From an activated environment:

```bash
python -m nulltrace --strict
python -m nulltrace --list-missions
python -m nulltrace --qa
python -m nulltrace --lab packet
python -m nulltrace --lab nmap
python -m nulltrace --lab john
python -m nulltrace --lab incident
```

`--qa` bypasses normal mission unlocking for review and does not save mission completions, Academy stages, or case completions. A successful simulated fallback is **not** proof of real-tool integration.

For the Burp web laboratory, start `python -m nulltrace --web-lab` in Terminal 1, leave it running, follow `docs/WEB_BURP_LAB_GUIDE.md` with Burp Repeater, and then execute `python -m nulltrace --lab web` in Terminal 2. Stop the local server with Ctrl+C. This is a synthetic `127.0.0.1` exercise.

Dossier export (uses the first stored profile):

```bash
python -m nulltrace --export-dossier ~/Documents/nulltrace_case.md
```

## 10. Saves, privacy and recovery

Normal campaign database: `~/.local/share/nulltrace/campaign.sqlite3` on default Linux XDG configuration (or a path under `NULLTRACE_SAVE_DIR` if set). Stores profile identity, progress, story choices, evidence and the new chapter-case review records. No Google account or GitHub login is required to play. **Never push this file or a `.env` secret into a public Git repository.** The repository's `.gitignore` excludes standard save files, venv files and logs.

If a new update crashes, preserve the failing logs and revert the source via Git or restore the backup archive. Restore the backed-up database only if necessary; doing so replaces newer progress. Do not delete the working `.venv` as a first troubleshooting step.

## 11. Verifying the v1.5 candidate

```bash
bash scripts/verify_cinematics_v15.sh
python -m nulltrace
python -m nulltrace --qa
```

Manually test the cinematic viewer in Chapters 1, 5, 8 and 10; toggle autoplay, navigate backward, change reduction settings; complete at least one chapter case with wrong and right answers; step packet journey through a gateway failure and restore; restart the game and verify your completed case remains in the original profile and absent in a new profile. See `docs/V1_3_TO_V1_5_ACCEPTANCE.md` for the acceptance matrix.

## 12. Known limitations

- Scenes use procedural 2D environments and captioned dialogue, **not** fully illustrated cinematic sprite sheets, voice performances or rich soundtracks.
- Packet motion is a deterministic illustrative graph, **not** Wireshark packet replay, IP geolocation, or a live network trace.
- Casework contains ten case files, not 100 independently graded practical investigations; the original 100 mission assessments remain.
- Existing nine-stage lesson mini-projects include written reflection and do not all have separate practical validators.
- Linux GUI/Windows execution for **v1.5** remains subject to your acceptance testing; the authoring environment cannot run Pygame tests.

## 13. Troubleshooting

| Symptom | Check |
|---|---|
| `No module named nulltrace` | Verify you are inside the project and installed `pip install -e '.[dev]'` in the active venv. |
| `No module named pygame` | Re-run `bash scripts/setup_ubuntu.sh` and activate `.venv`. |
| Window does not open | Test `python scripts/window_smoke_test.py`; verify desktop GUI and video driver. |
| `src refspec main does not match any` | Commit to the local branch before pushing; never force-push reflexively. |
| Web lab reports pending | Leave the local server running while sending the intended Burp request and checking the receipt. |
| Existing progress missing | Check that `NULLTRACE_SAVE_DIR` and home directory are unchanged before restoring backups. |

---
*NULLTRACE is a training tool. Practice only on systems and targets for which you have explicit authorization.*

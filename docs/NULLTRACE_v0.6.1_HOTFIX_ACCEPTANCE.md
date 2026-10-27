# NULLTRACE v0.6.1 — TShark / John / operator animation hotfix

**Scope:** targeted compatibility + animated prototype. Phases 4 and 6 are **not accepted** until real-tool tests pass on Ubuntu. Does not implement full cinematic sprites, a movie-like cutscene system, or Chapters 8–10.

## Why these fixes are needed

1. Your PCAP was readable to the regular user (`-rw-r--r--`), but TShark reported it could not read it. A restrictive Ubuntu **AppArmor profile** is a plausible explanation: filesystem permissions alone are not enough. The new adapter pipes the already-verified 337-byte synthetic capture to TShark via `-r -`, so TShark does **not** open a file from your Documents directory. This does **not** change AppArmor or require `sudo`.
2. Ubuntu's basic/core John build does not recognize `--help` or the jumbo-only `--pot=...` option. The new adapter uses `--format=md5crypt`, `--wordlist=...` and `--show`; isolates `HOME` / `XDG_CONFIG_HOME` / `XDG_DATA_HOME` to a temporary directory; and removes those temporary artifacts after use. John tests use only a synthetically generated training hash.
3. The game previously contained a character-name/appearance picker but **no rendered character sprite**. The new procedural 2D operator has idle breathing, brief blinks, and walking gait; selectable `hoodie`, `analyst`, and `technician` designs. Walk around the **Operations Floor** using WASD or arrow keys. Press **M** to toggle reduced motion. Animation is a **placeholder**, not final commissioned sprite art.

## Safe installation (preserve saves)

You must first download `NULLTRACE_v0.6.1_Hotfix.zip` to `~/Downloads`.

```bash
cd ~/Documents/nulltrace
mkdir -p ~/Documents/nulltrace-backups
# Your campaign database is outside the repository; preserve it independently.
if [ -f ~/.local/share/nulltrace/campaign.sqlite3 ]; then
  cp -a ~/.local/share/nulltrace/campaign.sqlite3 \
      ~/Documents/nulltrace-backups/campaign_before_v061.sqlite3
fi
# Back up the source files being replaced:
cp -a src/nulltrace/labs/practical.py ~/Documents/nulltrace-backups/practical_v060.py
cp -a src/nulltrace/ui/app.py ~/Documents/nulltrace-backups/app_v060.py
unzip -o ~/Downloads/NULLTRACE_v0.6.1_Hotfix.zip -d ~/Documents/nulltrace
source .venv/bin/activate
python -m pip install -e '.[dev]'
bash scripts/verify_v061_hotfix.sh
```

**No `sudo` is required** and the hotfix contains no SQLite schema migration.

## Automated acceptance criteria

- The environment diagnostic must report Pygame-CE installed.
- All Python tests must pass; with Pygame-CE available, graphical tests must not be skipped. Baseline for this patch: **39 tests passed** in the packaging environment, with **2 Pygame tests skipped** because the packaging environment lacks Pygame. Target Ubuntu should show **41 passed, 0 skipped** (dependent on the unchanged older tests).
- `Mission records: 100`.
- `NULLTRACE Pygame UI smoke: PASS (3 frames)`.

## Real packet tool verification (Phase 4)

```bash
python -m nulltrace --lab packet
```

Expected after patch:

```text
TShark offline packet inspection: real (pass)
 - Frames: 3
 - Trusted capture piped via stdin (no live sniffing):
 - 192.0.2.10 ... mirror.training.invalid
```

Verify the same stdin approach independently (it does not initiate a live capture):

```bash
cat lab_assets/pcaps/ghost_dns.pcap | tshark -n -r - -Y dns \
  -T fields -e ip.src -e ip.dst -e dns.qry.name
```

Three lines are expected, including two requests and a response involving `mirror.training.invalid`. If the command still fails, copy the **full** output and run `tshark --version | head -8` and `sudo aa-status | grep -i tshark` to check which security policy is applied. Do **not** disable AppArmor or run TShark with sudo.

## Real John verification (Phase 6)

```bash
python -m nulltrace --lab john
```

Expected when Ubuntu's installed John accepts MD5-crypt:

```text
John: synthetic credential audit: real (pass)
 - Fixture: generated MD5-crypt hash for training only ...
 - The five-word local training dictionary identified ...
```

If it still reports `simulated`, inspect available options by simply running `john` with **no flags**; use `john --test=1` to check formats, if desired. Ubuntu's core John build does not necessarily support `john --help`. Report the exact fallback diagnostic. No real credentials are used.

## Character animation acceptance (UI)

```bash
python -m nulltrace
```

- [ ] Select Alex / Ghost / hoodie, open the **Command Center**: a small animated hoodie operator appears on the right.
- [ ] Open **Story Archive**: a larger operator sprite appears at the right side of the dialogue scene.
- [ ] Open **OPERATOR** (profile screen): hoodie/analyst/technician choices change the small preview.
- [ ] Click **OPERATIONS FLOOR** on Command Center: avatar appears and idly breathes/blinks.
- [ ] Press **W A S D** and the arrow keys: the sprite moves, walks, and stays within the room boundary.
- [ ] Press **M** in Operations Floor: animation is suppressed as a reduced-motion option; press M again to restore.
- [ ] Exit and relaunch: your **name, codename, outfit, mission progress** remain unchanged.
- [ ] Resize the window and navigate back; no crash or control loss.

### Definition of done

- Packet real lab passes → the previously blocked **Phase 4 tool-integration** test may be accepted (other manual Phase 4 checklist items still apply).
- John real lab passes → the previously blocked **Phase 6 tool-integration** test may be accepted (other manual Phase 6 checklist items still apply).
- Animation UI tests pass → v0.6.1 procedural avatar implementation accepted, **not** a final cinematic animation system.

If any test fails, record its exact output and keep that item **pending**, even when the game launches.

"""Explicitly exported Markdown training dossier, never an automated incident accusation."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from nulltrace.persistence.store import Store, default_path
from nulltrace.labs.incident import inspect_case
from nulltrace.story.endings import resolve_ending


def render_dossier(store: Store, player_id: int) -> str:
    player=store.player(player_id)
    completed=store.completed(player_id)
    evidence=store.evidence(player_id)
    choices=store.choices(player_id)
    case=inspect_case()
    fully_completed='CH10-M10' in completed
    ending=resolve_ending(choices,{key for key,_ in evidence}) if fully_completed else None
    items='\n'.join(f'- **{code}** — {desc}' for code,desc in evidence) or '- No findings collected.'
    return f'''# NULLTRACE — Synthetic Incident Dossier

**Status:** {'Completed campaign' if fully_completed else 'Draft — mission progression incomplete'}
**Operator:** {player['name']} / {player['codename']}
**Completed mission assessments:** {len(completed)}/100
**Fixture:** NEXUS-FINAL-01 (entirely fictional)
**File integrity (SHA-256):** `{case['sha256']}`
**Evidence event count:** {case['events']}

## Preserved case observations

{items}

## Evidence assessment

- **Observed discrepancy:** {case['discrepancy']}.
- **Uncertainty:** {case['qualification']}.
- **Scope:** Training artifacts only. No real people, accounts, or institutions are implicated.
- **Interpretation:** A discrepancy is a finding to investigate, not automatic proof of intent.

## Story decision

- Disclosure route: {choices.get('disclosure_route','not selected')}
- Outcome: {ending.title if ending else 'not yet available'}

## Recommended next steps

1. Preserve originals and compare integrity digests.
2. Correlate records in a common time zone and document uncertainty.
3. Seek independent review before drawing conclusions about intent.
4. Minimize unrelated data in any disclosure.

*Automatically generated local training report. It does not certify professional competence or authenticate external evidence.*
'''


def export_dossier(store: Store, player_id: int, path: Path | None = None) -> Path:
    if path is None:
        root=default_path().parent / 'dossiers'
        path=root / f'operator_{player_id}_dossier.md'
    path=Path(path).expanduser()
    path.parent.mkdir(parents=True,exist_ok=True)
    body=render_dossier(store,player_id)
    path.write_text(body,encoding='utf-8')
    return path

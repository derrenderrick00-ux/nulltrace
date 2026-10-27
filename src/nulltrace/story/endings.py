"""Deterministic ending outcomes. No AI, remote data, or hidden dice rolls."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Ending:
    code: str
    title: str
    summary: str
    epilogue: str
    evidence_count: int


def resolve_ending(choices: dict[str,str], evidence_ids: set[str]) -> Ending:
    count = len(evidence_ids)
    route = choices.get('disclosure_route', 'restricted')
    if route == 'broad':
        return Ending('blackout','THE BLACKOUT',
            'A broad release exposes the surveillance programme, but puts uninvolved people and services at risk.',
            'The Unseen fractures. Your dossier endures; the damage to bystanders cannot be undone.',count)
    if route == 'oversight' and count >= 9:
        return Ending('reckoning','THE RECKONING',
            'A documented, independently reviewed disclosure enables accountability while protecting sensitive details.',
            'MIRROR is placed under oversight. The investigation becomes a model for responsible evidence handling.',count)
    return Ending('silent','THE SILENT PROTOCOL',
        'The evidence is preserved under restricted review; immediate disruption is limited but broad accountability is uncertain.',
        'The network keeps operating. Public confidence remains unsettled and independent review is not complete.',count)

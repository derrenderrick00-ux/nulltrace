"""Offline, reproducible synthetic incident evidence dossier; no networking."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from nulltrace.core.content import ROOT

CASE_FILE = ROOT / 'lab_assets/cases/nexus_case.json'

def inspect_case(path: Path = CASE_FILE) -> dict:
    data = path.read_bytes()
    if len(data) > 100_000:
        raise ValueError('Case file exceeds expected training size')
    case = json.loads(data)
    if case.get('case_id') != 'NEXUS-FINAL-01' or case.get('schema_version') != 1:
        raise ValueError('Invalid or incompatible training case')
    records = case['timeline']
    if len(records) < 5 or len(records) > 20 or any('timestamp_utc' not in event or 'reference' not in event for event in records):
        raise ValueError('Case event schema invalid')
    times = [datetime.fromisoformat(e['timestamp_utc'].replace('Z','+00:00')).astimezone(timezone.utc) for e in records]
    if times != sorted(times):
        raise ValueError('Timeline not in UTC order')
    references = {e['reference'] for e in records}
    if not {'MI-07', 'IS-21', 'AU-18'}.issubset(references):
        raise ValueError('Missing records needed to corroborate the conflict')
    if case['official_summary']['claim'] != case['observed_conflict']['contradicted_claim']:
        raise ValueError('Conflict chain incomplete')
    return {'events':len(records),'sha256':hashlib.sha256(data).hexdigest(),
            'discrepancy':'IS-21 denies MIRROR metadata; MI-07 records it',
            'qualification':'Discrepancy alone does not establish intentional manipulation',
            'source_ids':tuple(e['reference'] for e in records)}

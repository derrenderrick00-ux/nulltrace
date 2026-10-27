"""Read-only, schema-checked curriculum catalog. No executable mission content."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os
import re

ROOT = Path(__file__).resolve().parents[3]
MISSION_RE = re.compile(r"^CH(\d\d)-M(\d\d)$")

class ContentError(ValueError):
    pass

@dataclass(frozen=True)
class Mission:
    id: str
    chapter_id: str
    title: str
    objective: str
    activity: str
    verification: str
    prerequisites: tuple[str, ...]
    mode: str
    assessment: dict | None
    lesson_note: str = ''


class Curriculum:
    def __init__(self, root: Path = ROOT):
        self.root = Path(root)
        catalog = json.loads((root / 'content/missions/catalog.json').read_text(encoding='utf-8'))
        assessments = []
        for filename in ('assessments_01_07.json', 'assessments_08_10.json'):
            assessments.extend(json.loads((root / 'content/missions' / filename).read_text(encoding='utf-8')))
        exam = {x['mission_id']: x for x in assessments}
        notes = json.loads((root / 'content/chapters/lesson_notes_08_10.json').read_text(encoding='utf-8'))
        if len(notes) != 30 or not all(isinstance(v,str) and 35 <= len(v) <= 400 for v in notes.values()):
            raise ContentError('Expected 30 nonempty advanced instructional notes')
        if len(exam) != 100 or len(assessments) != 100:
            raise ContentError('Expected 100 unique active assessments')
        ids = [m['id'] for m in catalog]
        if len(ids) != 100 or len(set(ids)) != 100:
            raise ContentError('Expected 100 unique mission catalog IDs')
        self.missions = {}
        for entry in catalog:
            ident = entry['id']
            match = MISSION_RE.fullmatch(ident)
            if not match or entry['chapter_id'] != f'CH{match.group(1)}':
                raise ContentError(f'Invalid mission identifier: {ident}')
            if (ident in exam) != (int(match.group(1)) <= 10):
                raise ContentError(f'Unexpected assessment coverage: {ident}')
            for prerequisite in entry['prerequisites']:
                if prerequisite not in ids or ids.index(prerequisite) >= ids.index(ident):
                    raise ContentError(f'Invalid prerequisite for {ident}: {prerequisite}')
            a = exam.get(ident)
            if a:
                if len(a['choices']) != 3 or len(set(a['choices'])) != 3 or not 0 <= a['answer_index'] < 3:
                    raise ContentError(f'Invalid assessment choices: {ident}')
                if a['objective'] != entry['learning_objective']:
                    raise ContentError(f'Assessment mismatch: {ident}')
            self.missions[ident] = Mission(ident, entry['chapter_id'], entry['title'], entry['learning_objective'], entry['activity'], entry['verification'], tuple(entry['prerequisites']), entry['mode'], a, notes.get(ident,''))
        self.active = [x for x in self.missions.values() if x.assessment is not None]

    def unlocked(self, mission: Mission, completed: set[str], qa: bool = False) -> bool:
        return bool(mission.assessment) and (qa or all(x in completed for x in mission.prerequisites))

    def get(self, mid: str) -> Mission:
        return self.missions[mid]

    def chapter(self, n: int) -> list[Mission]:
        return [self.missions[f'CH{n:02d}-M{i:02d}'] for i in range(1, 11)]

    @staticmethod
    def checked_response(mission: Mission, answer: int) -> tuple[bool, str]:
        a = mission.assessment
        if a is None:
            raise ContentError('Mission is not playable yet')
        if not isinstance(answer, int) or not 0 <= answer < 3:
            raise ContentError('Invalid answer index')
        return answer == a['answer_index'], a['explanation']

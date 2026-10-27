"""Versioned, declarative nine-stage lessons. No executable instructions in data."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from nulltrace.core.content import ROOT, Curriculum, ContentError

STAGE_KEYS = ('objectives','terms','explain','visual','example','application','exercise','project','integrate')

@dataclass(frozen=True)
class Lesson:
    mission_id: str
    focus: str
    diagram: tuple[str, ...]
    example_label: str
    stages: tuple[dict, ...]

class LessonLibrary:
    def __init__(self, root: Path = ROOT, curriculum: Curriculum | None = None):
        root = Path(root)
        content = root / 'content/lessons/lesson_stages_01_10.json'
        try:
            raw = json.loads(content.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ContentError('Lesson content unreadable') from exc
        if not isinstance(raw,list) or len(raw)!=100:
            raise ContentError('Expected exactly 100 lessons')
        curriculum = curriculum or Curriculum(root)
        known = set(curriculum.missions)
        self.lessons: dict[str,Lesson] = {}
        for item in raw:
            if not isinstance(item,dict) or item.get('schema_version') != 1:
                raise ContentError('Unsupported lesson record')
            mid=item.get('mission_id')
            if not isinstance(mid,str) or mid not in known or mid in self.lessons:
                raise ContentError(f'Invalid/duplicate lesson: {mid}')
            stages=item.get('stages')
            if not isinstance(stages,list) or len(stages)!=9 or tuple(s.get('key') for s in stages if isinstance(s,dict))!=STAGE_KEYS:
                raise ContentError(f'Invalid stages: {mid}')
            for s in stages:
                if any(not isinstance(s.get(k),str) or not 12<=len(s[k])<=3000 for k in ('title','body','action')):
                    raise ContentError(f'Incomplete lesson stage: {mid}')
            diagram=item.get('diagram')
            if not isinstance(diagram,list) or not 2<=len(diagram)<=6 or not all(isinstance(t,str) and 1<=len(t)<=35 for t in diagram):
                raise ContentError(f'Invalid diagram: {mid}')
            focus=item.get('focus')
            ex=item.get('example_label')
            if not isinstance(focus,str) or not focus.strip() or not isinstance(ex,str) or not ex.strip():
                raise ContentError(f'Missing lesson metadata: {mid}')
            self.lessons[mid]=Lesson(mid,focus,tuple(diagram),ex,tuple(stages))
        if set(self.lessons)!=known:
            raise ContentError('Lesson coverage does not match campaign')

    def get(self, mid: str) -> Lesson:
        return self.lessons[mid]

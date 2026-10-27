"""Synthetic interactive casework with explicit evidence requirements."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from nulltrace.core.content import ROOT, ContentError

@dataclass(frozen=True)
class Evidence:
    id: str
    label: str
    kind: str

@dataclass(frozen=True)
class Case:
    id: str
    chapter: int
    title: str
    briefing: str
    evidence: tuple[Evidence,...]
    conclusions: tuple[str,...]
    correct_index: int
    required_evidence: frozenset[str]
    feedback: str

class Casebook:
    def __init__(self, root:Path=ROOT):
        try:rows=json.loads((Path(root)/'content/investigations/casebook.json').read_text(encoding='utf8'))
        except (OSError,UnicodeError,json.JSONDecodeError) as exc:raise ContentError('Casebook unavailable') from exc
        if not isinstance(rows,list) or len(rows)!=10:raise ContentError('Exactly ten cases required')
        self.cases={}
        for r in rows:
            if not isinstance(r,dict) or r.get('schema_version')!=1:raise ContentError('Invalid case schema')
            n=r.get('chapter');ident=r.get('id')
            if type(n)!=int or not 1<=n<=10 or ident!=f'CASE-CH{n:02d}' or n in self.cases:raise ContentError('Invalid case identity')
            raw=r.get('evidence');options=r.get('conclusions');correct=r.get('correct_index');req=r.get('required_evidence')
            if not isinstance(raw,list) or len(raw)<3 or len(raw)>8 or not isinstance(options,list) or len(options)!=3:
                raise ContentError('Invalid case content lengths')
            items=[]
            for row in raw:
                if not isinstance(row,dict) or row.get('kind') not in ('observation','claim','limitation') or not isinstance(row.get('id'),str) or not isinstance(row.get('label'),str) or not 10<=len(row['label'])<=400:raise ContentError('Invalid evidence')
                items.append(Evidence(row['id'],row['label'],row['kind']))
            ids={i.id for i in items}
            if len(ids)!=len(items) or not isinstance(req,list) or len(req)<2 or not set(req)<=ids or type(correct)!=int or not 0<=correct<3:raise ContentError('Invalid expected finding')
            if not all(isinstance(x,str) and 25<=len(x)<=300 for x in options):raise ContentError('Invalid conclusion')
            if not isinstance(r.get('feedback'),str) or len(r['feedback'])<25:raise ContentError('Invalid feedback')
            if not isinstance(r.get('briefing'),str) or not isinstance(r.get('title'),str):raise ContentError('Invalid narrative')
            self.cases[n]=Case(ident,n,r['title'],r['briefing'],tuple(items),tuple(options),correct,frozenset(req),r['feedback'])
        if set(self.cases)!=set(range(1,11)):raise ContentError('Case coverage mismatch')

    def get(self,chapter:int)->Case:return self.cases[chapter]

class CaseSession:
    def __init__(self,case:Case):
        self.case=case;self.selected=set();self.conclusion=None

    def toggle(self,evidence_id:str):
        if evidence_id not in {item.id for item in self.case.evidence}:raise ValueError('Unknown case evidence')
        if evidence_id in self.selected:self.selected.remove(evidence_id)
        else:self.selected.add(evidence_id)

    def choose(self,index:int):
        if type(index)!=int or not 0<=index<3:raise ValueError('Invalid conclusion')
        self.conclusion=index

    def assess(self)->tuple[bool,str]:
        missing=self.case.required_evidence-self.selected
        if self.conclusion is None:return False,'Choose a conclusion before submitting.'
        if self.conclusion!=self.case.correct_index:return False,'This conclusion overstates or contradicts the evidence. '+self.case.feedback
        if missing:return False,f'Select the {len(missing)} required supporting record(s). Look for direct observations, not rumors.'
        unsupported={e.id for e in self.case.evidence if e.kind=='claim'} & self.selected
        if unsupported:return False,'Deselect unverified claims; support the conclusion using documented observations.'
        return True,self.case.feedback

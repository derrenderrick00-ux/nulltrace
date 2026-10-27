"""Declarative, repeatable offline cutscenes. Data has no executable callbacks."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from nulltrace.core.content import ROOT, ContentError

ENVIRONMENTS = {'apartment','operations','archive','datacenter','mirror'}
SHOTS = {'establish','dialogue','close','console','reveal'}
SPEAKERS = {'SYSTEM','OPERATOR','JONAH','MARA','IMANI','ROOK','UNKNOWN'}

@dataclass(frozen=True)
class Beat:
    speaker: str
    text: str
    shot: str
    duration_ms: int

@dataclass(frozen=True)
class Sequence:
    chapter: int
    location: str
    environment: str
    beats: tuple[Beat,...]

class CinematicLibrary:
    def __init__(self, root: Path = ROOT):
        try:
            data = json.loads((Path(root)/'content/cinematics/chapter_beats.json').read_text(encoding='utf8'))
        except (OSError,UnicodeError,json.JSONDecodeError) as exc:
            raise ContentError('Cinematic content is unreadable') from exc
        if not isinstance(data,list) or len(data)!=10:raise ContentError('Expected ten cinematic sequences')
        sequences={}
        for item in data:
            if not isinstance(item,dict) or item.get('schema_version')!=1:raise ContentError('Invalid cinematic schema')
            chapter=item.get('chapter')
            if type(chapter)!=int or not 1<=chapter<=10 or chapter in sequences:raise ContentError('Invalid chapter')
            location=item.get('location');environment=item.get('environment');raw=item.get('beats')
            if not isinstance(location,str) or not location.strip() or environment not in ENVIRONMENTS:raise ContentError('Invalid environment')
            if not isinstance(raw,list) or not 4<=len(raw)<=12:raise ContentError('Bad beat count')
            beats=[]
            for b in raw:
                if not isinstance(b,dict) or b.get('speaker') not in SPEAKERS or b.get('shot') not in SHOTS:raise ContentError('Invalid cinematic beat')
                duration=b.get('duration_ms');msg=b.get('text')
                if type(duration)!=int or not 1000<=duration<=20000 or not isinstance(msg,str) or not 20<=len(msg)<=500:
                    raise ContentError('Invalid cinematic text or duration')
                # Two safe tokens only. Refuse arbitrary or malformed template placeholders.
                if '{' in msg.replace('{name}','').replace('{codename}','') or '}' in msg.replace('{name}','').replace('{codename}',''):
                    raise ContentError('Unsupported interpolation token')
                beats.append(Beat(b['speaker'],msg,b['shot'],duration))
            sequences[chapter]=Sequence(chapter,location,environment,tuple(beats))
        if set(sequences)!=set(range(1,11)):raise ContentError('Cinematic chapter coverage mismatch')
        self.sequences=sequences

    def get(self,chapter:int)->Sequence:return self.sequences[chapter]

    @staticmethod
    def substitute(text:str,name:str,codename:str)->str:
        # Replacement instead of str.format protects braces in user-entered names.
        return text.replace('{name}',name).replace('{codename}',codename)

class Timeline:
    """Deterministic, time-based playback; skip/step remains available to reduced-motion users."""
    def __init__(self,sequence:Sequence):
        self.sequence=sequence;self.index=0;self.elapsed_ms=0.;self.playing=False

    @property
    def beat(self)->Beat:return self.sequence.beats[self.index]

    @property
    def done(self)->bool:return self.index==len(self.sequence.beats)-1

    def advance(self)->bool:
        if self.done:self.playing=False;return False
        self.index+=1;self.elapsed_ms=0.;return True

    def previous(self):
        self.index=max(0,self.index-1);self.elapsed_ms=0.;self.playing=False

    def restart(self):self.index=0;self.elapsed_ms=0.;self.playing=False

    def tick(self,dt:float):
        if not self.playing:return
        dt=max(0.,min(float(dt),.25));self.elapsed_ms+=dt*1000
        if self.elapsed_ms>=self.beat.duration_ms:
            self.advance()  # one beat per frame avoids accidental scene skips

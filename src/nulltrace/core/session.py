"""Rules engine: mission progression and evidence; no display or tool spawning."""
from __future__ import annotations
from nulltrace.core.content import Curriculum
from nulltrace.persistence.store import Store
from nulltrace.labs.practical import LAB_MISSIONS,LabResult

CHAPTER_EVIDENCE={
    'CH01-M10':('mirror07','MIRROR-07 appeared in Meridian monitoring logs after a gateway configuration failure.'),
    'CH02-M10':('network_segment','The discovered NEXUS-linked network segment was missing from the published diagram.'),
    'CH03-M10':('protocol_anomaly','An observed DNS request used the training name associated with MIRROR records.'),
    'CH04-M10':('route_discrepancy','Official path descriptions do not match the training route evidence.'),
    'CH05-M10':('pcap_record','The supplied packet capture supports a narrower claim than the official incident summary.'),
    'CH06-M10':('management_port','A scoped loopback audit identified an unexpected reachable service in the exercise.'),
    'CH07-M10':('weak_training_key','Synthetic credential audit demonstrated risk from predictable password choices.'),
    'CH08-M10':('portal_weakness','Local synthetic HTTP portal demonstrates missing object-level authorization.'),
    'CH09-M10':('shadow_discrepancy','Bundled evidence files reveal a conflict between MIRROR records and the official summary.'),
    'CH10-M10':('nexus_dossier','The final synthetic evidence report documents findings and uncertainty.'),
}

class Session:
    def __init__(self, curriculum: Curriculum,store: Store,player_id: int,qa:bool=False):
        self.curriculum=curriculum;self.store=store;self.player_id=player_id;self.qa=qa
        self.lab_results:dict[str,LabResult]={}

    @property
    def completed(self)->set[str]:return self.store.completed(self.player_id)

    def can_start(self,mid:str)->bool:
        return self.curriculum.unlocked(self.curriculum.get(mid),self.completed, self.qa)

    def attach_lab(self,mid:str,result:LabResult):
        if not self.can_start(mid):raise ValueError('Mission locked')
        if mid not in LAB_MISSIONS:raise ValueError('No lab required for this mission')
        self.lab_results[mid]=result

    def submit(self,mid:str,choice:int)->tuple[bool,str]:
        if not self.can_start(mid):raise ValueError('Mission locked')
        mission=self.curriculum.get(mid)
        if mid == 'CH10-M10' and not self.qa and 'disclosure_route' not in self.store.choices(self.player_id):
            return False,'Choose your disclosure route in the Chapter 10 Story Archive before final submission.'
        if mid in LAB_MISSIONS and not (mid in self.lab_results and self.lab_results[mid].success):
            return False,'Complete this mission’s controlled laboratory first, then answer the question.'
        correct, explanation=self.curriculum.checked_response(mission,choice)
        if correct and self.qa:
            return True,'QA mode: result is not saved. '+explanation
        method = self.lab_results[mid].mode if mid in LAB_MISSIONS else 'concept'
        self.store.submit(self.player_id,mid,correct,method)
        if correct and mid in CHAPTER_EVIDENCE:
            code,desc=CHAPTER_EVIDENCE[mid]
            self.store.add_evidence(self.player_id,code,desc)
        return correct,explanation

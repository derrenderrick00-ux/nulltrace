"""Offline network journey: deterministic illustrative frames, never live packet capture."""
from __future__ import annotations
from dataclasses import dataclass
from nulltrace.network.simulator import route,HOSTS

@dataclass(frozen=True)
class Hop:
    label:str
    address:str
    note:str

SCENARIOS={
1:('TCP to service',('workstation-07','switch-01','gateway','fileserver')),
2:('LAN to gateway',('workstation-07','switch-01','gateway')),
3:('DNS query',('workstation-07','switch-01','gateway','dns')),
4:('Gateway trace',('workstation-07','switch-01','gateway','fileserver')),
5:('Captured DNS',('workstation-07','switch-01','gateway','dns')),
6:('Approved inventory',('workstation-07','switch-01','gateway')),
7:('Secure archive',('workstation-07','switch-01','gateway','fileserver')),
8:('HTTP portal',('workstation-07','switch-01','gateway','fileserver')),
9:('Incident timeline',('workstation-07','switch-01','gateway','fileserver')),
10:('NEXUS review',('workstation-07','switch-01','gateway','fileserver')),
}

class PacketJourney:
    def __init__(self,chapter:int=1):
        if type(chapter)!=int or chapter not in SCENARIOS:raise ValueError('Invalid chapter')
        self.chapter=chapter;self.name,self.nodes=SCENARIOS[chapter];self.index=0;self.playing=False;self.elapsed=0.;self.gateway_online=True

    def reset(self):self.index=0;self.elapsed=0.;self.playing=False

    @property
    def hops(self)->tuple[Hop,...]:
        result=[]
        for label in self.nodes:
            if label=='gateway' and not self.gateway_online:
                result.append(Hop('gateway','192.168.10.1','Gateway unavailable: simulated traffic stops here.'))
                break
            result.append(Hop(label,HOSTS.get(label,'training-only'),'Illustrative logical transit; not an observed packet capture.'))
        return tuple(result)

    @property
    def current(self)->Hop:return self.hops[self.index]

    @property
    def at_end(self)->bool:return self.index==len(self.hops)-1

    def step(self):
        if self.at_end:self.playing=False;return False
        self.index+=1;self.elapsed=0.;return True

    def toggle_gateway(self):
        self.gateway_online=not self.gateway_online;self.reset()

    def tick(self,dt:float):
        if not self.playing:return
        self.elapsed+=max(0.,min(float(dt),.25))
        if self.elapsed>=1.0:self.elapsed=0.;self.step()

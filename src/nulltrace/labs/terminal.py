"""Bounded, fictional terminal grammar. No subprocess, shell or real filesystem access."""
from __future__ import annotations
import shlex
from nulltrace.network.simulator import explain

FILES = {
  '/home/alex': ('reports','notes.txt'),
  '/home/alex/reports': ('incident-07.txt',),
  '/var/log': ('network.log',),
}
TEXT = {
  '/home/alex/notes.txt': 'Meridian shift 03:17: Review workstation-07. Scope: authorized simulation only.',
  '/home/alex/reports/incident-07.txt': 'Host: 192.168.10.17\nGateway: 192.168.10.1\nRemote file server: 192.168.20.20\nFinding: check route to services subnet.',
  '/var/log/network.log': '03:17:08 LINK OK\n03:17:09 MIRROR-07 RESTRICTED REFERENCE\n03:18:02 GATEWAY MISCONFIGURATION RECORDED'
}

class VirtualTerminal:
    def __init__(self): self.cwd='/home/alex';self.history=[]
    def execute(self, line: str) -> str:
        if len(line)>160: return 'Command too long (160-character limit).'
        try: args=shlex.split(line)
        except ValueError:return 'Unterminated quote; check your input.'
        if not args:return ''
        cmd=args[0]
        if cmd=='help':return 'SAFE SIMULATION: help, pwd, ls, cd, cat, ip, ping, traceroute, dig, clear\nNothing here executes an operating-system command.'
        if cmd=='pwd':return self.cwd
        if cmd=='ls':
            path=self._path(args[1]) if len(args)==2 else self.cwd
            return '   '.join(FILES[path]) if path in FILES else 'Not a training directory.'
        if cmd=='cd':
            path=self._path(args[1]) if len(args)==2 else '/home/alex'
            if path in FILES:self.cwd=path;return f'Entered {path}'
            return 'Directory not found in simulated filesystem.'
        if cmd=='cat':
            if len(args)!=2:return 'Usage: cat <training-file>'
            return TEXT.get(self._path(args[1]),'Training file not found.')
        if cmd=='ip':return 'SIMULATED: workstation-07 192.168.10.17/24 via gateway 192.168.10.1'
        if cmd=='ping':
            if len(args)!=2:return 'Usage: ping fileserver'
            return 'SIMULATED: ICMP echo reply from 192.168.20.20 (routing available)' if args[1] in ('fileserver','192.168.20.20') else 'Unknown simulation target; try fileserver.'
        if cmd=='traceroute':return explain('workstation-07','fileserver')
        if cmd=='dig':return 'SIMULATED: mirror.training.invalid A 203.0.113.77 (documentation IP)'
        if cmd=='clear':return '\f'
        return 'Command unavailable. This is not a real shell; type help.'
    def _path(self, input_path: str) -> str:
        from posixpath import normpath,join
        return normpath(input_path if input_path.startswith('/') else join(self.cwd,input_path))

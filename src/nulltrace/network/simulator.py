"""Deterministic, offline, illustrative network simulator; NEVER touches real network."""
from __future__ import annotations
from ipaddress import ip_address, ip_network

HOSTS = {'workstation-07':'192.168.10.17', 'switch-01':'192.168.10.2', 'gateway':'192.168.10.1', 'fileserver':'192.168.20.20','dns':'192.168.20.53'}
NETWORKS = {'office':'192.168.10.0/24','services':'192.168.20.0/24'}

def same_subnet(a: str,b: str,prefix: int =24) -> bool:
    return ip_address(b) in ip_network(f'{a}/{prefix}',strict=False)

def route(source='workstation-07', destination='fileserver', gateway_online: bool=True) -> list[str]:
    if source not in HOSTS or destination not in HOSTS: raise ValueError('Unknown simulated host')
    if same_subnet(HOSTS[source], HOSTS[destination]):return [source,'switch-01',destination]
    if not gateway_online:return [source,'switch-01','GATEWAY_UNREACHABLE']
    return [source,'switch-01','gateway',destination]

def explain(source: str,destination: str) -> str:
    path=route(source,destination)
    detail = 'Local frame forwarding' if len(path)==3 else 'Router forwards between subnets'
    return f'{" → ".join(path)}\n{detail}. Illustration: not an actual packet trace.'

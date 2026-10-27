"""Rebuild the tiny synthetic, non-sensitive offline PCAP. No capture device used."""
import socket
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'lab_assets/pcaps/ghost_dns.pcap'

def checksum(data:bytes)->int:
    if len(data)%2:data+=b'\x00'
    w=struct.unpack('!%dH'%(len(data)//2),data)
    total=sum(w)
    while total>>16:total=(total&0xffff)+(total>>16)
    return (~total)&0xffff

def iphdr(source,dest,payload,proto,ident):
    a=socket.inet_aton(source);b=socket.inet_aton(dest)
    h=struct.pack('!BBHHHBBH4s4s',0x45,0,len(payload)+20,ident,0,64,proto,0,a,b)
    h=h[:10]+struct.pack('!H',checksum(h))+h[12:]
    return h

def udp(sport,dport,data):
    # UDP checksum 0 is permitted in IPv4; here all addresses are documentation ranges.
    return struct.pack('!HHHH',sport,dport,8+len(data),0)+data

def name(s):return b''.join(bytes([len(part)])+part.encode() for part in s.split('.'))+b'\x00'
qname=name('mirror.training.invalid')
query=struct.pack('!HHHHHH',0x1234,0x0100,1,0,0,0)+qname+struct.pack('!HH',1,1)
response=struct.pack('!HHHHHH',0x1234,0x8180,1,1,0,0)+qname+struct.pack('!HH',1,1)+b'\xc0\x0c'+struct.pack('!HHIH',1,1,60,4)+socket.inet_aton('203.0.113.77')
packets=[]
for i,(src,dst,sport,dport,data) in enumerate([
    ('192.0.2.10','198.51.100.53',50500,53,query),
    ('198.51.100.53','192.0.2.10',53,50500,response),
    ('192.0.2.10','198.51.100.53',50501,53,query),
]):
    payload=udp(sport,dport,data)
    frame=b'\x02\x00\x00\x00\x00\x02'+b'\x02\x00\x00\x00\x00\x01'+b'\x08\x00'+iphdr(src,dst,payload,17,440+i)+payload
    packets.append(frame)
with TARGET.open('wb') as out:
    out.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
    for i,frame in enumerate(packets):
        out.write(struct.pack('<IIII',1730000000+i,0,len(frame),len(frame)))
        out.write(frame)
print('Wrote',TARGET,'frames',len(packets))

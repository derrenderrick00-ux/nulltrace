"""Non-networked release regression tests. All external tool usage is mocked."""
import importlib.util
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
from unittest.mock import patch
import pytest

from nulltrace.core.content import Curriculum,ContentError,ROOT
from nulltrace.core.session import Session,CHAPTER_EVIDENCE
from nulltrace.persistence.store import Store
from nulltrace.labs.terminal import VirtualTerminal
from nulltrace.network.simulator import same_subnet,route,explain
from nulltrace.labs.practical import (
    LAB_MISSIONS,PCAP,TRAINING_DOMAIN,TEST_PASSWORD,packet_file_sanity,packet_lab,
    nmap_lab,parse_nmap_xml,john_lab,run_lab
)

@pytest.fixture
def course():return Curriculum()

@pytest.fixture
def db(tmp_path):
    store=Store(tmp_path/'saves'/'test.db')
    yield store
    store.close()

def test_phase_count_and_stable_ids(course):
    assert len(course.missions)==100
    assert len(course.active)==100
    assert [x.id for x in course.active]==[f'CH{c:02d}-M{m:02d}' for c in range(1,11) for m in range(1,11)]
    assert all(course.get(f'CH{ch:02d}-M01').assessment for ch in (8,9,10))

def test_all_70_items_have_unique_questions_and_valid_answers(course):
    assert len({m.assessment['question'] for m in course.active})==100
    for m in course.active:
        assert m.assessment['objective']==m.objective
        assert len(set(m.assessment['choices']))==3
        success,reason=course.checked_response(m,m.assessment['answer_index'])
        assert success and reason
        for i in range(3):
            if i!=m.assessment['answer_index']:
                assert not course.checked_response(m,i)[0]

def test_mission_order_and_chapter_prerequisites(course):
    completed=set()
    for m in course.active:
        assert course.unlocked(m,completed)
        completed.add(m.id)
    assert course.unlocked(course.get('CH08-M01'),completed,True)

def test_invalid_assessment_index(course):
    with pytest.raises(ContentError):course.checked_response(course.get('CH01-M01'),4)

def test_create_profile_and_persist(db,tmp_path):
    pid=db.create_player(' Alex ',' Ghost ','hoodie')
    assert db.player(pid)['name']=='Alex'
    assert db.player(pid)['codename']=='Ghost'
    path=db.path
    db.con.commit()
    second=Store(path)
    try:assert second.player(pid)['appearance']=='hoodie'
    finally:second.close()

def test_profile_rejects_invalid_input(db):
    for n,c,a in [('', 'Ghost','hoodie'),('Alex','','hoodie'),('Alex\nOh','Ghost','hoodie'),('Alex','Ghost','root')]:
        with pytest.raises(ValueError):db.create_player(n,c,a)

def test_progression_locked_before_prerequisite(course,db):
    pid=db.create_player('Alex','Ghost','hoodie')
    session=Session(course,db,pid)
    assert session.can_start('CH01-M01')
    assert not session.can_start('CH01-M02')
    with pytest.raises(ValueError):session.submit('CH01-M02',0)
    ok,_=session.submit('CH01-M01',course.get('CH01-M01').assessment['answer_index'])
    assert ok and session.can_start('CH01-M02')

def test_wrong_answer_does_not_unlock(course,db):
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid)
    right=course.get('CH01-M01').assessment['answer_index']
    assert not s.submit('CH01-M01',(right+1)%3)[0]
    assert not s.can_start('CH01-M02')
    assert db.con.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]==1

def test_repeat_completion_is_idempotent(course,db):
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid)
    right=course.get('CH01-M01').assessment['answer_index']
    assert s.submit('CH01-M01',right)[0]
    assert s.submit('CH01-M01',right)[0]
    assert db.con.execute('SELECT COUNT(*) FROM mission_progress').fetchone()[0]==1

def test_capstone_creates_evidence_once(course,db):
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid)
    for mission in course.chapter(1):
        assert s.submit(mission.id,mission.assessment['answer_index'])[0]
    assert len(db.evidence(pid))==1
    assert db.evidence(pid)[0][0]=='mirror07'
    s.submit('CH01-M10',course.get('CH01-M10').assessment['answer_index'])
    assert len(db.evidence(pid))==1

def test_qa_mode_bypasses_unlock_but_does_not_save(course,db):
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid,qa=True)
    assert s.can_start('CH07-M10')
    # Requires lab; deliberate simulation (no external tool)
    from nulltrace.labs.practical import LabResult
    s.attach_lab('CH07-M10',LabResult(True,'simulated','Test',('fixture',)))
    assert s.submit('CH07-M10',course.get('CH07-M10').assessment['answer_index'])[0]
    assert not db.completed(pid)
    assert not db.evidence(pid)

def test_lab_required_before_grading(course,db):
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid,qa=True)
    m=course.get('CH05-M05')
    good,message=s.submit(m.id,m.assessment['answer_index'])
    assert not good and 'laboratory' in message
    from nulltrace.labs.practical import LabResult
    s.attach_lab(m.id,LabResult(True,'simulated','Synthetic',('works',)))
    assert s.submit(m.id,m.assessment['answer_index'])[0]

def test_lab_cannot_attach_to_wrong_mission(course,db):
    from nulltrace.labs.practical import LabResult
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid,qa=True)
    with pytest.raises(ValueError):s.attach_lab('CH01-M01',LabResult(True,'real','oops',()))

def test_terminal_no_real_shell_and_bounds(tmp_path):
    t=VirtualTerminal()
    assert '/home/alex'==t.execute('pwd')
    assert 'incident-07.txt' in t.execute('ls reports')
    assert 'MIRROR-07' in t.execute('cat /var/log/network.log')
    assert 'not a real shell' in t.execute('rm -rf /').lower()
    assert t.execute('x'*161).startswith('Command too long')
    assert 'Unterminated' in t.execute('cat "')

def test_virtual_terminal_navigation():
    t=VirtualTerminal()
    assert t.execute('cd reports')=='Entered /home/alex/reports'
    assert t.execute('pwd')=='/home/alex/reports'
    assert 'Gateway' in t.execute('cat incident-07.txt')
    assert 'training directory' in t.execute('ls /etc')
    assert 'unknown simulation' in t.execute('ping 1.1.1.1').lower()

def test_network_determinism():
    assert same_subnet('192.168.1.10','192.168.1.12')
    assert not same_subnet('192.168.1.10','192.168.2.12')
    assert route() == ['workstation-07','switch-01','gateway','fileserver']
    assert route(gateway_online=False)[-1]=='GATEWAY_UNREACHABLE'
    assert 'Illustration' in explain('workstation-07','fileserver')
    with pytest.raises(ValueError):route(destination='hostile-public-server')

def test_packet_fixture_is_valid_and_stable():
    r=packet_file_sanity()
    assert r['frames']==3
    assert len(r['sha256'])==64
    assert PCAP.exists()

def test_packet_fixture_rejects_corruption(tmp_path):
    f=tmp_path/'bad.pcap';f.write_bytes(b'nothing')
    with pytest.raises(ValueError):packet_file_sanity(f)

def test_packet_fallback_is_honestly_labeled():
    with patch('nulltrace.labs.practical.shutil.which',return_value=None):
        r=packet_lab()
    assert r.success and r.mode=='simulated'
    assert '192.0.2.10' in ' '.join(r.details)

def test_packet_real_adapter_has_only_read_only_flags():
    def fake_run(args,**kwargs):
        assert args[1:3]==['-n','-r']
        assert args[3]=='-'
        assert kwargs['input']==PCAP.read_bytes()
        assert '-i' not in args and '-w' not in args
        return subprocess.CompletedProcess(args,0,stdout=f'192.0.2.10\t198.51.100.53\t{TRAINING_DOMAIN}\n'.encode(),stderr=b'')
    with patch('nulltrace.labs.practical.shutil.which',return_value='/usr/bin/tshark'),patch('nulltrace.labs.practical.subprocess.run',side_effect=fake_run):
        r=packet_lab()
    assert r.mode=='real' and r.success

def test_nmap_parser_accepts_only_loopback():
    xml='<nmaprun><host><addresses><address addr="127.0.0.1" addrtype="ipv4"/></addresses><ports><port protocol="tcp" portid="43123"><state state="open"/></port></ports></host></nmaprun>'
    assert parse_nmap_xml(xml,43123)=='open'
    assert parse_nmap_xml(xml.replace('127.0.0.1','192.0.2.10'),43123)=='not-found'
    with pytest.raises(ValueError):parse_nmap_xml('x'*300001,43123)

def test_nmap_unavailable_fallback():
    with patch('nulltrace.labs.practical.shutil.which',return_value=None):
        r=nmap_lab()
    assert r.success and r.mode=='simulated'

def test_nmap_real_adapter_never_scans_nonloopback():
    def fake_run(args,**kwargs):
        assert args[-1]=='127.0.0.1'
        assert args[1:4]==['-sT','-Pn','-p']
        assert '-oX' in args
        p=args[4]
        xml=f'<nmaprun><host><addresses><address addr="127.0.0.1"/></addresses><ports><port protocol="tcp" portid="{p}"><state state="open"/></port></ports></host></nmaprun>'
        return subprocess.CompletedProcess(args,0,xml,'')
    with patch('nulltrace.labs.practical.shutil.which',return_value='/usr/bin/nmap'),patch('nulltrace.labs.practical.subprocess.run',side_effect=fake_run):
        result=nmap_lab()
    assert result.success and result.mode=='real'

def test_john_unavailable_uses_simulation_not_real():
    with patch('nulltrace.labs.practical.shutil.which',return_value=None):
        r=john_lab()
    assert r.success and r.mode=='simulated'
    assert 'No real credentials' in ' '.join(r.details)

def test_unknown_lab_cannot_start():
    with pytest.raises(ValueError):run_lab('arbitrary_command')

def test_chapter_progression_reaches_phase_six_without_external_tools(course,db):
    """Integrates 100 missions with opt-in training lab result fixtures, never uses tools."""
    from nulltrace.labs.practical import LabResult
    pid=db.create_player('Alex','Ghost','hoodie');s=Session(course,db,pid)
    db.set_choice(pid,'disclosure_route','oversight')
    for m in course.active:
        assert s.can_start(m.id),m.id
        if m.id in LAB_MISSIONS:
            s.attach_lab(m.id,LabResult(True,'simulated','Fixture',('synthetic evidence',)))
        ok,msg=s.submit(m.id,m.assessment['answer_index'])
        assert ok,(m.id,msg)
    assert len(db.completed(pid))==100
    assert len(db.evidence(pid))==10
    assert s.can_start('CH10-M10')

@pytest.mark.skipif(importlib.util.find_spec('pygame') is None,reason='Pygame not installed in test runner; Ubuntu graphical validation required')
def test_pygame_headless_frames(monkeypatch,tmp_path):
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    monkeypatch.setenv('NULLTRACE_SAVE_DIR',str(tmp_path))
    from nulltrace.ui.app import smoke_test
    assert smoke_test()==0

@pytest.mark.skipif(importlib.util.find_spec('pygame') is None,reason='Pygame unavailable in test runner; must run on target Ubuntu')
def test_pygame_every_screen_and_quiz(monkeypatch,tmp_path):
    """Render all scene types with a real SDL dummy display, including intro and exams."""
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    import pygame
    from nulltrace.ui.app import Game
    db=Store(tmp_path/'ui.db')
    g=Game(pygame,qa=True,store=db)
    try:
        assert g.page=='home'
        g.render()
        g.page='profile';g.render()
        g.new_profile()
        assert g.page=='story'
        for chapter in range(1,11):
            g.chapter=chapter;g.page='story';g.render()
            g._open_chapter(chapter);g.render()
            g.open_mission(f'CH{chapter:02d}-M01')
            assert g.page=='lesson'
            g.render()
            g.page='assessment';g.render()
        for page in ('chapters','terminal','network','evidence','tools','operator_room','home'):
            g.page=page;g.render()
        g.page='terminal';g.command='help';g.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        assert 'SAFE SIMULATION' in '\n'.join(g.term_lines)
    finally:g.close()

def test_parse_realistic_nmap_direct_address():
    """Nmap's actual XML has host/address as a direct child of host."""
    sample='''<?xml version="1.0"?><nmaprun><host><status state="up"/>
    <address addr="127.0.0.1" addrtype="ipv4"/>
    <ports><port protocol="tcp" portid="38080"><state state="open"/></port></ports>
    </host></nmaprun>'''
    assert parse_nmap_xml(sample,38080)=='open'

def test_story_choice_persistence(db):
    pid=db.create_player('Alex','Ghost','hoodie')
    db.set_choice(pid,'chapter01_decision','verify')
    assert db.choices(pid)['chapter01_decision']=='verify'
    db.set_choice(pid,'chapter01_decision','report')
    assert db.choices(pid)['chapter01_decision']=='report'

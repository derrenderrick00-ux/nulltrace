"""New campaign, story, and safe local-lab acceptance tests.

Networking is strictly a temporary 127.0.0.1 HTTP server owned by this test.
No scanners, external targets, credentials, or live packet captures are used.
"""
import json
from pathlib import Path
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from nulltrace.core.content import Curriculum, ContentError, ROOT
from nulltrace.core.session import Session
from nulltrace.labs.practical import LabResult, LAB_MISSIONS, web_lab, incident_lab, run_lab
from nulltrace.labs.web_training import receipt_file, receipt_status, start_server
from nulltrace.labs.incident import CASE_FILE, inspect_case
from nulltrace.persistence.store import Store
from nulltrace.story.endings import resolve_ending
from nulltrace.story.scenes import CHAPTERS


def test_one_hundred_assessments_and_notes():
    c=Curriculum()
    assert len(c.missions)==len(c.active)==100
    assert len({m.assessment['question'] for m in c.active})==100
    assert all(c.get(f'CH{ch:02d}-M{i:02d}').lesson_note for ch in (8,9,10) for i in range(1,11))
    assert all(not c.get(f'CH{ch:02d}-M{i:02d}').lesson_note for ch in (1,2) for i in (1,2))
    assert sorted(CHAPTERS)==list(range(1,11))


def test_first_seventy_still_match_baseline():
    original=json.loads((ROOT/'content/missions/assessments_01_07.json').read_text())
    c=Curriculum()
    for item in original:
        assert c.get(item['mission_id']).assessment==item


def test_later_wrong_answers_and_unlocks(tmp_path):
    c=Curriculum();db=Store(tmp_path/'save.db');pid=db.create_player('Alex','Ghost','hoodie')
    try:
        s=Session(c,db,pid,qa=True)
        m=c.get('CH08-M01')
        bad=(m.assessment['answer_index']+1)%3
        assert not s.submit(m.id,bad)[0]
        assert s.submit(m.id,m.assessment['answer_index'])[0]
        assert not db.completed(pid), 'QA must not write progress'
    finally:db.close()


def test_final_choice_is_required_but_does_not_change_prior_save(tmp_path):
    c=Curriculum();db=Store(tmp_path/'campaign.db');pid=db.create_player('Alex','Ghost','hoodie')
    try:
        s=Session(c,db,pid)
        # Complete all but last mission using fixtures; never execute real tools.
        for m in c.active[:-1]:
            if m.id in LAB_MISSIONS:
                s.attach_lab(m.id,LabResult(True,'simulated','Fixture',('synthetic',)))
            assert s.submit(m.id,m.assessment['answer_index'])[0],m.id
        m=c.get('CH10-M10')
        s.attach_lab(m.id,LabResult(True,'offline','Fixture',('synthetic',)))
        ok,why=s.submit(m.id,m.assessment['answer_index'])
        assert not ok and 'disclosure route' in why
        assert len(db.completed(pid))==99
        assert len(db.evidence(pid))==9
        db.set_choice(pid,'disclosure_route','oversight')
        assert s.submit(m.id,m.assessment['answer_index'])[0]
        assert len(db.completed(pid))==100
        assert len(db.evidence(pid))==10
        assert resolve_ending(db.choices(pid),{x for x,_ in db.evidence(pid)}).code=='reckoning'
        assert s.submit(m.id,m.assessment['answer_index'])[0]
        assert len(db.completed(pid))==100
    finally:db.close()


def test_endings_all_branches():
    facts={f'e{i}' for i in range(10)}
    assert resolve_ending({'disclosure_route':'oversight'}, facts).code=='reckoning'
    assert resolve_ending({'disclosure_route':'oversight'}, {'one'}).code=='silent'
    assert resolve_ending({'disclosure_route':'broad'}, facts).code=='blackout'
    assert resolve_ending({'disclosure_route':'restricted'}, facts).code=='silent'
    assert resolve_ending({},facts).code=='silent'


def test_web_lab_requires_manually_triggered_receipt(monkeypatch,tmp_path):
    monkeypatch.setenv('NULLTRACE_SAVE_DIR',str(tmp_path))
    assert not receipt_file().exists()
    assert receipt_status()[0] is False
    assert web_lab().success is False
    server=start_server(receipt_path=receipt_file())
    assert server.server_address[0]=='127.0.0.1'
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        url=f'http://127.0.0.1:{server.server_port}/training/case?case=alpha'
        with urlopen(url,timeout=3) as response:
            assert json.loads(response.read())['owner']=='analyst-a'
        assert not receipt_file().exists()
        # A manual HTTP client switches synthetic case ID, demonstrating missing object-level authorization.
        with urlopen(url.replace('alpha','mirror'),timeout=3) as response:
            assert json.loads(response.read())['owner']=='analyst-b'
        assert not receipt_file().exists(), 'Reading a case without review header is not completion'
        req=Request(url.replace('alpha','mirror'),headers={'X-Nulltrace-Review':'authorized'})
        with urlopen(req,timeout=3) as response:
            assert response.status==200
        assert receipt_status()[0]
        result=run_lab('web')
        assert result.success and result.mode=='local-http'
        assert 'not independently verifiable' in ' '.join(result.details)
        try:
            urlopen(f'http://127.0.0.1:{server.server_port}/does-not-exist',timeout=3)
        except HTTPError as exc:assert exc.code==404
        else:raise AssertionError('Unexpected missing-resource success')
    finally:
        server.shutdown();thread.join(timeout=4);server.server_close()


def test_receipt_expiration_and_malformed(monkeypatch,tmp_path):
    monkeypatch.setenv('NULLTRACE_SAVE_DIR',str(tmp_path))
    path=receipt_file()
    path.write_text('not-json',encoding='utf-8')
    assert not receipt_status()[0]
    path.write_text(json.dumps({'schema_version':1,'case':'mirror','review':'authorized','completed_at':1}),encoding='utf-8')
    assert not receipt_status()[0]
    path.write_text(json.dumps({'schema_version':1,'case':'mirror','review':'unauthorized','completed_at':9999999999}),encoding='utf-8')
    assert not receipt_status()[0]


def test_training_portal_method_restrictions(tmp_path):
    server=start_server(receipt_path=tmp_path/'receipt.json')
    th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
    try:
        req=Request(f'http://127.0.0.1:{server.server_port}/training/case?case=alpha',data=b'no',method='POST')
        with pytest.raises(HTTPError) as e:urlopen(req,timeout=3)
        assert e.value.code==405
        assert not (tmp_path/'receipt.json').exists()
    finally:server.shutdown();th.join(timeout=4);server.server_close()


def test_local_lab_refuses_bad_port():
    for port in (-1,65536,'random'):
        with pytest.raises(ValueError):start_server(port)


def test_incident_dossier_integrity_and_limits(tmp_path):
    finding=inspect_case()
    assert finding['events']==5
    assert 'MI-07' in finding['source_ids'] and 'IS-21' in finding['source_ids']
    assert len(finding['sha256'])==64
    assert run_lab('incident').mode=='offline'
    blob=json.loads(CASE_FILE.read_text())
    blob['timeline'][0]['timestamp_utc']='2038-06-17T04:15:00Z'
    path=tmp_path/'corrupt.json';path.write_text(json.dumps(blob))
    with pytest.raises(ValueError,match='UTC order'):inspect_case(path)
    path.write_text('{bad')
    with pytest.raises(ValueError):inspect_case(path)


def test_external_lab_independent_from_virtual_terminal():
    from nulltrace.labs.terminal import VirtualTerminal
    t=VirtualTerminal()
    assert 'not a real shell' in t.execute('nmap -sT 192.168.1.1').lower()
    assert 'not a real shell' in t.execute('python -m nulltrace --web-lab').lower()

def test_export_dossier_preserves_training_claim_limits(tmp_path):
    from nulltrace.investigations.report import export_dossier
    store=Store(tmp_path/'save.sqlite3')
    try:
        pid=store.create_player('Alex','Ghost','hoodie')
        store.add_evidence(pid,'shadow_discrepancy','Fictional conflicting log summary')
        output=export_dossier(store,pid,tmp_path/'reports'/'case.md')
        text=output.read_text(encoding='utf-8')
        assert 'Alex / Ghost' in text
        assert 'SHA-256' in text
        assert 'Draft' in text
        assert 'not automatic proof' in text
        assert output.exists()
    finally:store.close()

@pytest.mark.skipif(__import__('importlib').util.find_spec('pygame') is None,reason='Pygame only available on target Ubuntu')
def test_pygame_new_pages_and_final_story(monkeypatch,tmp_path):
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    import pygame
    from nulltrace.ui.app import Game
    store=Store(tmp_path/'gui.sqlite3')
    g=Game(pygame,qa=True,store=store)
    try:
        g.new_profile()
        assert g.session is not None
        for page in ('home','chapters','tools','evidence','disclosure','ending'):
            g.page=page;g.render()
        for chapter in (8,9,10):
            g.chapter=chapter;g.page='story';g.render()
            g.page='missions';g.render()
            g.open_mission(f'CH{chapter:02d}-M01')
            g.render()
            g.page='assessment';g.render()
        g._record_disclosure('oversight')
        assert g.qa_story_choices['disclosure_route']=='oversight'
        assert not store.choices(g.profile_id)
    finally:g.close()

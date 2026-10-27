"""v1.3–1.5 regression tests. Never trigger a real security tool."""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import json
import pytest
from nulltrace.core.content import Curriculum,ContentError
from nulltrace.cinematics.timeline import CinematicLibrary, Timeline
from nulltrace.investigations.casebook import Casebook,CaseSession
from nulltrace.network.journey import PacketJourney
from nulltrace.persistence.store import Store
from nulltrace.education.lessons import LessonLibrary

@pytest.fixture(scope='module')
def cinematic():return CinematicLibrary()
@pytest.fixture(scope='module')
def cases():return Casebook()

def test_legacy_campaign_retained():
    curriculum=Curriculum();library=LessonLibrary(curriculum=curriculum)
    assert len(curriculum.active)==len(library.lessons)==100
    assert sum(len(x.stages) for x in library.lessons.values())==900

def test_cinematic_chapters_and_50_beats(cinematic):
    assert len(cinematic.sequences)==10
    assert sum(len(x.beats) for x in cinematic.sequences.values())==50
    assert len({c.environment for c in cinematic.sequences.values()})==5

@pytest.mark.parametrize('chapter',range(1,11))
def test_chapter_cinematic_timeline(cinematic,chapter):
    timeline=Timeline(cinematic.get(chapter));assert timeline.beat.shot=='establish'
    timeline.playing=True
    for _ in range(5):timeline.tick(.25)
    assert timeline.index==0
    while not timeline.done:assert timeline.advance()
    assert not timeline.advance()
    timeline.previous();assert timeline.index==3
    timeline.restart();assert timeline.index==0 and timeline.playing is False


def test_cinematic_safe_interpolation(cinematic):
    actual=cinematic.substitute('{codename} greets {name}','{x}', 'Ghost')
    assert actual=='Ghost greets {x}'


def test_cinematic_loader_rejects_unsupported_interpolation(tmp_path,cinematic):
    root=tmp_path/'content/cinematics';root.mkdir(parents=True)
    rows=json.loads((Path(__file__).resolve().parents[1]/'content/cinematics/chapter_beats.json').read_text())
    rows[0]['beats'][1]['text']='Bad arbitrary token {phone} and some text here'
    (root/'chapter_beats.json').write_text(json.dumps(rows))
    with pytest.raises(ContentError):CinematicLibrary(tmp_path)

@pytest.mark.parametrize('chapter',range(1,11))
def test_cases_require_evidence_not_just_guessing(cases,chapter):
    case=cases.get(chapter);s=CaseSession(case)
    assert s.assess()[0] is False
    s.choose(case.correct_index);assert s.assess()[0] is False
    for evid in case.required_evidence:s.toggle(evid)
    assert s.assess()[0] is True
    s.choose((case.correct_index+1)%3)
    assert s.assess()[0] is False


def test_unverified_claims_cannot_be_used_as_proof(cases):
    c=cases.get(1);s=CaseSession(c)
    s.choose(c.correct_index)
    for key in c.required_evidence:s.toggle(key)
    claim=next(x.id for x in c.evidence if x.kind=='claim')
    s.toggle(claim)
    assert s.assess()[0] is False
    s.toggle(claim)
    assert s.assess()[0] is True


def test_case_evidence_validation(cases):
    s=CaseSession(cases.get(1))
    with pytest.raises(ValueError):s.toggle('random-real-world-evidence')
    with pytest.raises(ValueError):s.choose(5)
    evid=next(iter(s.case.required_evidence))
    s.toggle(evid);assert evid in s.selected
    s.toggle(evid);assert evid not in s.selected


def test_casebook_rejects_duplicated_evidence(tmp_path):
    r=tmp_path/'content/investigations';r.mkdir(parents=True)
    records=json.loads((Path(__file__).resolve().parents[1]/'content/investigations/casebook.json').read_text())
    records[0]['evidence'][1]['id']=records[0]['evidence'][0]['id']
    (r/'casebook.json').write_text(json.dumps(records))
    with pytest.raises(ContentError):Casebook(tmp_path)

@pytest.mark.parametrize('chapter',range(1,11))
def test_network_journey_10_scenarios(chapter):
    j=PacketJourney(chapter)
    assert len(j.hops)>=3
    assert j.hops[0].label=='workstation-07'
    j.playing=True;j.tick(.25);assert j.index==0
    while not j.at_end:assert j.step()
    assert not j.step()
    j.reset();assert j.index==0
    j.toggle_gateway();assert not j.gateway_online
    assert j.hops[-1].label=='gateway'
    assert j.at_end is False
    while not j.at_end:j.step()
    assert 'unavailable' in j.current.note.lower()


def test_no_real_packet_io():
    import inspect
    from nulltrace.network import journey
    text=inspect.getsource(journey)
    assert 'subprocess' not in text and 'socket.' not in text and 'scapy.' not in text


def test_case_progress_additive_migration_and_profile_isolation(tmp_path,cases):
    file=tmp_path/'old_campaign.sqlite3'
    db=Store(file)
    a=db.create_player('Alex','Ghost','hoodie')
    b=db.create_player('Pat','Wave','technician')
    db.submit(a,'CH01-M01',True)
    db.mark_stage(a,'CH01-M01',0)
    case=cases.get(1)
    assert db.record_case(a,case.id,case.correct_index,set(case.required_evidence))
    assert db.record_case(a,case.id,case.correct_index,set(case.required_evidence)) is False
    assert db.solved_cases(a)=={'CASE-CH01'}
    assert db.solved_cases(b)==set()
    assert db.completed(a)=={'CH01-M01'}
    assert db.stages_done(a,'CH01-M01')=={0}
    report=db.case_report(a,case.id)
    assert set(report['evidence'])==set(case.required_evidence)
    assert db.case_report(b,case.id) is None
    db.close()
    db=Store(file)
    assert db.solved_cases(a)=={'CASE-CH01'}
    assert db.completed(a)=={'CH01-M01'}
    assert db.stages_done(a,'CH01-M01')=={0}
    db.close()


def test_case_progress_rejects_bad_data(tmp_path):
    db=Store(tmp_path/'s.db');a=db.create_player('Alex','Ghost','hoodie')
    with pytest.raises(ValueError):db.record_case(a,'BAD',0,set())
    with pytest.raises(ValueError):db.record_case(a,'CASE-CH01',9,set())
    with pytest.raises(ValueError):db.record_case(a,'CASE-CH01',0,{'x'*71})
    with pytest.raises(ValueError):db.record_case(999,'CASE-CH01',0,set())
    db.close()


def test_graphical_cinematic_and_case_smoke(tmp_path,monkeypatch):
    pg=pytest.importorskip('pygame',reason='Pygame graphical acceptance runs on Ubuntu')
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy');monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    from nulltrace.ui.app import Game
    db=Store(tmp_path/'test.sqlite3');game=None
    try:
        db.create_player('Alex','Ghost','hoodie')
        game=Game(pg,store=db,qa=True)
        for page in ('cinematic','casework','journey'):
            if page=='cinematic':game._start_cinematic()
            if page=='casework':game._start_case()
            if page=='journey':game._start_journey()
            assert game.page==page
            game.update(.016);game.render()
        assert game.qa
    finally:
        if game:game.close()
        else:db.close()


def test_graphical_multi_chapter_smoke(tmp_path,monkeypatch):
    pg=pytest.importorskip('pygame',reason='Pygame graphical acceptance runs on Ubuntu')
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy');monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    from nulltrace.ui.app import Game
    db=Store(tmp_path/'test.sqlite3');game=None
    try:
        db.create_player('Alex','Ghost','hoodie')
        game=Game(pg,store=db,qa=True)
        for chapter in (1,5,8,10):
            game.chapter=chapter
            for start in (game._start_cinematic,game._start_case,game._start_journey):
                start();game.update(.016);game.render()
        assert db.solved_cases(game.profile_id)==set()
    finally:
        if game:game.close()
        else:db.close()

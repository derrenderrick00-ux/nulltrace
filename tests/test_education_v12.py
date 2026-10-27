"""Nine-stage lesson coverage, integrity, schema migration and QA isolation.
No external tools, network scans, live captures or subprocesses are launched.
"""
import json
import sqlite3
import importlib.util
from pathlib import Path
import pytest
from nulltrace.core.content import Curriculum, ContentError, ROOT
from nulltrace.education.lessons import LessonLibrary, STAGE_KEYS
from nulltrace.persistence.store import Store


def test_full_nine_stage_coverage():
    lib=LessonLibrary();curriculum=Curriculum()
    assert len(lib.lessons)==len(curriculum.active)==100
    assert sum(len(x.stages) for x in lib.lessons.values())==900
    assert all(tuple(s['key'] for s in lesson.stages)==STAGE_KEYS for lesson in lib.lessons.values())
    assert all('training' in str(lesson.stages).lower() or 'evidence' in str(lesson.stages).lower()
               for lesson in lib.lessons.values())


def test_mission_specific_lessons_and_long_form_explanations():
    lib=LessonLibrary()
    assert len({x.focus for x in lib.lessons.values()})==100
    assert len({x.stages[2]['body'] for x in lib.lessons.values()})==100
    assert len({x.stages[4]['body'] for x in lib.lessons.values()})==100
    for mid in ('CH01-M01','CH03-M06','CH05-M04','CH07-M07','CH08-M08','CH10-M10'):
        lesson=lib.get(mid)
        assert len(lesson.stages[2]['body'])>350
        assert len(lesson.diagram) >= 3
        assert 'PRACTICE QUESTION' in lesson.stages[6]['body']
        assert 'YOUR TRAINING TASK' in lesson.stages[7]['body']
        assert 'mission' in lesson.stages[8]['body'].lower() or 'chapter' in lesson.stages[8]['body'].lower()


def test_content_rejects_corruption(tmp_path):
    content=json.loads((ROOT/'content/lessons/lesson_stages_01_10.json').read_text())
    folder=tmp_path/'content/lessons'; folder.mkdir(parents=True)
    def try_bad(modify):
        dirty=json.loads(json.dumps(content))
        modify(dirty)
        (folder/'lesson_stages_01_10.json').write_text(json.dumps(dirty))
        with pytest.raises(ContentError):LessonLibrary(root=tmp_path,curriculum=Curriculum())
    try_bad(lambda d:d.pop())
    try_bad(lambda d:d[1].update(mission_id=d[0]['mission_id']))
    try_bad(lambda d:d[0]['stages'][4].update(key='bad'))
    try_bad(lambda d:d[0].update(diagram=['alone']))
    try_bad(lambda d:d[0]['stages'][0].update(body='x'*3001))


def test_additive_migration_preserves_player_missions_evidence(tmp_path):
    path=tmp_path/'campaign.sqlite3'
    # Deliberately create save from current release then simulate old metadata.
    db=Store(path)
    pid=db.create_player('Alex','Ghost','hoodie')
    db.submit(pid,'CH01-M01',True)
    db.add_evidence(pid,'test','Synthetic proof')
    db.set_choice(pid,'chapter01_decision','verify')
    db.con.execute('UPDATE schema_meta SET version=1');db.con.commit()
    db.close()
    db=Store(path)
    try:
        assert db.con.execute('SELECT version FROM schema_meta').fetchone()[0]==2
        assert db.player(pid)['codename']=='Ghost'
        assert 'CH01-M01' in db.completed(pid)
        assert db.evidence(pid)==[('test','Synthetic proof')]
        assert db.choices(pid)['chapter01_decision']=='verify'
        assert db.stages_done(pid,'CH01-M01')==set()
        db.mark_stage(pid,'CH01-M01',0)
        db.mark_stage(pid,'CH01-M01',0)
        assert db.stages_done(pid,'CH01-M01')=={0}
    finally:db.close()


def test_stage_progress_separate_from_mission_completion(tmp_path):
    db=Store(tmp_path/'save.db');pid=db.create_player('Operator','Ghost','analyst')
    try:
        for idx in range(9):db.mark_stage(pid,'CH02-M05',idx)
        assert db.stages_done(pid,'CH02-M05')==set(range(9))
        assert not db.completed(pid)
        with pytest.raises(ValueError):db.mark_stage(pid,'CH02-M05',9)
        with pytest.raises(ValueError):db.mark_stage(pid,'../../../etc',0)
        db.save_lesson_note(pid,'CH02-M05','Observed subnet mismatch; gateway configuration requires verification.')
        assert 'gateway' in db.lesson_note(pid,'CH02-M05')
        with pytest.raises(ValueError):db.save_lesson_note(pid,'CH02-M05','too short')
        with pytest.raises(ValueError):db.save_lesson_note(pid,'CH02-M05','x'*1201)
    finally:db.close()


def test_isolation_between_players(tmp_path):
    db=Store(tmp_path/'a.db')
    try:
        a=db.create_player('Alex','Ghost','hoodie')
        b=db.create_player('Taylor','Trace','technician')
        db.mark_stage(a,'CH01-M01',2)
        db.save_lesson_note(a,'CH01-M01','Found an allowed training device; unknown external hosts excluded.')
        assert db.stages_done(b,'CH01-M01')==set()
        assert db.lesson_note(b,'CH01-M01')==''
    finally:db.close()


@pytest.mark.skipif(importlib.util.find_spec('pygame') is None,reason='Pygame GUI verified on Ubuntu laptop')
def test_gui_nine_stages_all_views_in_qa(monkeypatch,tmp_path):
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    import pygame
    from nulltrace.ui.app import Game
    db=Store(tmp_path/'ui.db')
    game=Game(pygame,qa=True,store=db)
    try:
        game.new_profile()
        game.open_mission('CH01-M01')
        assert game.stage==0
        for i in range(9):
            game._go_stage(i)
            game.render()
        game._go_stage(3)
        for _ in range(len(game.lessons.get(game.mid).diagram)-1):game._advance_diagram()
        game._complete_stage()
        game._go_stage(6)
        game._practice_answer(game.curriculum.get(game.mid).assessment['answer_index'])
        assert game.practice_ok
        game._go_stage(7)
        game.field_note='Synthetic evidence identified; cause remains unknown until corroborated.'
        game._save_field_note()
        assert game.field_note
        assert db.stages_done(game.profile_id,'CH01-M01')==set()
        assert not db.lesson_note(game.profile_id,'CH01-M01')
        game._go_stage(8);game.render()
    finally:game.close()

def test_summary_counts_are_per_profile_and_idempotent(tmp_path):
    db=Store(tmp_path/'save.db')
    try:
        p=db.create_player('Alex','Ghost','hoodie')
        q=db.create_player('Nova','Trace','analyst')
        for stage in (0,1,1,7):db.mark_stage(p,'CH03-M06',stage)
        db.mark_stage(p,'CH03-M07',0)
        assert db.lesson_summary(p)[3]==4
        assert sum(db.lesson_summary(q).values())==0
    finally:db.close()

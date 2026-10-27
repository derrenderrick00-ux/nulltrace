"""Local SQLite save store with explicit transactions and idempotent rewards."""
from __future__ import annotations
from pathlib import Path
import os
import sqlite3
import re
import time


def default_path() -> Path:
    override = os.environ.get('NULLTRACE_SAVE_DIR')
    base = Path(override).expanduser() if override else Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'nulltrace'
    base.mkdir(parents=True, exist_ok=True)
    return base / 'campaign.sqlite3'

class Store:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path is not None else default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(self.path), timeout=5)
        self.con.row_factory = sqlite3.Row
        self.con.execute('PRAGMA foreign_keys = ON')
        self.con.executescript('''
            CREATE TABLE IF NOT EXISTS schema_meta(version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS players(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 32),
                codename TEXT NOT NULL CHECK(length(codename) BETWEEN 1 AND 32),
                appearance TEXT NOT NULL,
                created_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS mission_progress(
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                mission_id TEXT NOT NULL,
                completed_at INTEGER NOT NULL,
                lab_method TEXT NOT NULL DEFAULT 'concept',
                PRIMARY KEY(player_id, mission_id));
            CREATE TABLE IF NOT EXISTS attempts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                mission_id TEXT NOT NULL,
                correct INTEGER NOT NULL,
                created_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS evidence(
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                evidence_id TEXT NOT NULL,
                description TEXT NOT NULL,
                PRIMARY KEY(player_id,evidence_id));
            CREATE TABLE IF NOT EXISTS story_choices(
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                choice_id TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY(player_id, choice_id));
        ''')
        # v1.2 additive migration: keeps existing profile, mission and evidence rows.
        self.con.executescript('''
            CREATE TABLE IF NOT EXISTS lesson_stage_progress(
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                mission_id TEXT NOT NULL,
                stage_index INTEGER NOT NULL CHECK(stage_index BETWEEN 0 AND 8),
                recorded_at INTEGER NOT NULL,
                PRIMARY KEY(player_id,mission_id,stage_index));
            CREATE TABLE IF NOT EXISTS lesson_field_notes(
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                mission_id TEXT NOT NULL,
                note TEXT NOT NULL CHECK(length(note)<=1200),
                PRIMARY KEY(player_id,mission_id));
        ''')
        if self.con.execute('SELECT COUNT(*) FROM schema_meta').fetchone()[0] == 0:
            self.con.execute('INSERT INTO schema_meta VALUES(1)')
        with self.con:
            self.con.execute('UPDATE schema_meta SET version=2 WHERE version<2')
        self.con.commit()

    def lesson_summary(self, player_id: int) -> dict[int,int]:
        """Return count of recorded stages by chapter without changing mission completion."""
        rows=self.con.execute('SELECT mission_id,COUNT(*) FROM lesson_stage_progress '
                              'WHERE player_id=? GROUP BY mission_id',(player_id,)).fetchall()
        result={i:0 for i in range(1,11)}
        for mid,total in rows:
            if re.fullmatch(r'CH\d{2}-M\d{2}',mid):
                chapter=int(mid[2:4])
                if chapter in result:result[chapter]+=total
        return result

    def stages_done(self, player_id: int, mission_id: str) -> set[int]:
        return {row[0] for row in self.con.execute(
            'SELECT stage_index FROM lesson_stage_progress WHERE player_id=? AND mission_id=?',
            (player_id,mission_id))}

    def mark_stage(self, player_id: int, mission_id: str, stage_index: int):
        if not isinstance(stage_index,int) or not 0 <= stage_index <= 8:
            raise ValueError('Invalid lesson stage')
        if not isinstance(mission_id,str) or not re.fullmatch(r'CH\d{2}-M\d{2}',mission_id):
            raise ValueError('Invalid lesson identifier')
        with self.con:
            self.con.execute('INSERT OR IGNORE INTO lesson_stage_progress VALUES(?,?,?,?)',
                             (player_id,mission_id,stage_index,int(time.time())))

    def save_lesson_note(self, player_id: int, mission_id: str, note: str):
        if not isinstance(note,str) or len(note.strip())<20 or len(note)>1200:
            raise ValueError('Write an evidence note between 20 and 1200 characters')
        with self.con:
            self.con.execute('INSERT INTO lesson_field_notes VALUES(?,?,?) '
                             'ON CONFLICT(player_id,mission_id) DO UPDATE SET note=excluded.note',
                             (player_id,mission_id,note.strip()))

    def lesson_note(self, player_id: int, mission_id: str) -> str:
        r=self.con.execute('SELECT note FROM lesson_field_notes WHERE player_id=? AND mission_id=?',
                           (player_id,mission_id)).fetchone()
        return r[0] if r else ''

    def close(self):
        self.con.close()

    def create_player(self, name: str, codename: str, appearance: str) -> int:
        name, codename = name.strip(), codename.strip()
        if not (1 <= len(name) <= 32 and 1 <= len(codename) <= 32):
            raise ValueError('Name and codename must contain 1–32 characters')
        if any(ord(c) < 32 for c in name + codename):
            raise ValueError('Control characters are not allowed')
        if appearance not in ('hoodie', 'analyst', 'technician'):
            raise ValueError('Unknown appearance')
        with self.con:
            cur = self.con.execute('INSERT INTO players(name,codename,appearance,created_at) VALUES(?,?,?,?)',(name,codename,appearance,int(time.time())))
        return cur.lastrowid

    def players(self):
        return self.con.execute('SELECT * FROM players ORDER BY id DESC').fetchall()

    def player(self, ident: int):
        row = self.con.execute('SELECT * FROM players WHERE id=?',(ident,)).fetchone()
        if row is None: raise ValueError('Player not found')
        return row

    def completed(self, player_id: int) -> set[str]:
        return {r[0] for r in self.con.execute('SELECT mission_id FROM mission_progress WHERE player_id=?',(player_id,))}

    def submit(self, player_id: int, mission_id: str, correct: bool, lab_method='concept') -> bool:
        """Record attempt, complete once only; returns True only on first completion."""
        with self.con:
            self.con.execute('INSERT INTO attempts(player_id,mission_id,correct,created_at) VALUES(?,?,?,?)',(player_id,mission_id,int(correct),int(time.time())))
            if not correct:
                return False
            cur = self.con.execute('INSERT OR IGNORE INTO mission_progress(player_id,mission_id,completed_at,lab_method) VALUES(?,?,?,?)',(player_id,mission_id,int(time.time()),lab_method))
            return bool(cur.rowcount)

    def add_evidence(self, player_id: int, evid: str, description: str):
        with self.con:
            self.con.execute('INSERT OR IGNORE INTO evidence(player_id,evidence_id,description) VALUES(?,?,?)',(player_id,evid,description))

    def evidence(self, player_id: int) -> list[tuple[str,str]]:
        return [(r[0],r[1]) for r in self.con.execute('SELECT evidence_id,description FROM evidence WHERE player_id=? ORDER BY evidence_id',(player_id,))]

    def set_choice(self, player_id: int, ident: str, value: str):
        with self.con:
            self.con.execute('INSERT INTO story_choices(player_id,choice_id,value) VALUES(?,?,?) ON CONFLICT(player_id,choice_id) DO UPDATE SET value=excluded.value',(player_id,ident,value))

    def choices(self, player_id: int) -> dict[str,str]:
        return {r[0]:r[1] for r in self.con.execute('SELECT choice_id,value FROM story_choices WHERE player_id=?',(player_id,))}

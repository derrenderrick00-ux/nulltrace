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
        if self.con.execute('SELECT COUNT(*) FROM schema_meta').fetchone()[0] == 0:
            self.con.execute('INSERT INTO schema_meta VALUES(1)')
        self.con.commit()

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

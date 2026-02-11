import os
import sqlite3
from datetime import datetime


DB_FILENAME = 'lifeos.sqlite'


def _data_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data')


def db_path():
    return os.path.join(_data_dir(), DB_FILENAME)


def connect():
    path = db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS inbox ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'text TEXT, '
        'created_at TEXT'
        ')'
    )
    cur.execute(
        'CREATE TABLE IF NOT EXISTS tasks ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'title TEXT, '
        'kind TEXT, '
        'status TEXT, '
        'created_at TEXT, '
        'last_seen_at TEXT, '
        'days_skipped INTEGER, '
        'snooze_until TEXT, '
        'snooze_count INTEGER, '
        'leverage INTEGER, '
        'resistance INTEGER, '
        'est_minutes INTEGER'
        ')'
    )
    conn.commit()
    conn.close()


def insert_inbox(text):
    conn = connect()
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute(
        'INSERT INTO inbox (text, created_at) VALUES (?, ?)',
        (text, created_at),
    )
    conn.commit()
    conn.close()


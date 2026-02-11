import os
import sqlite3
from datetime import datetime, timedelta

from . import log


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
    cur.execute(
        'CREATE TABLE IF NOT EXISTS reference ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'text TEXT, '
        'created_at TEXT'
        ')'
    )
    conn.commit()
    conn.close()


def utc_now_iso():
    return datetime.utcnow().isoformat()


def today_str():
    return datetime.now().date().isoformat()


def tomorrow_str():
    return (datetime.now().date() + timedelta(days=1)).isoformat()


def insert_inbox(text):
    conn = connect()
    cur = conn.cursor()
    created_at = utc_now_iso()
    cur.execute(
        'INSERT INTO inbox (text, created_at) VALUES (?, ?)',
        (text, created_at),
    )
    conn.commit()
    conn.close()
    log('Captured inbox item: {}'.format(text))


def list_inbox_items():
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT id, text, created_at FROM inbox ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows


def get_inbox_item(item_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, text, created_at FROM inbox WHERE id = ?',
        (item_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def delete_inbox_item(item_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute('DELETE FROM inbox WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    log('Deleted inbox item {}'.format(item_id))


def insert_reference_from_inbox(inbox_item):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO reference (text, created_at) VALUES (?, ?)',
        (inbox_item['text'], utc_now_iso()),
    )
    cur.execute('DELETE FROM inbox WHERE id = ?', (inbox_item['id'],))
    conn.commit()
    conn.close()
    log('Moved inbox {} to reference'.format(inbox_item['id']))


def insert_task_from_inbox(inbox_item, kind, est_minutes):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO tasks ('
        'title, kind, status, created_at, last_seen_at, '
        'days_skipped, snooze_until, snooze_count, leverage, resistance, est_minutes'
        ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            inbox_item['text'],
            kind,
            'open',
            utc_now_iso(),
            None,
            0,
            None,
            0,
            0,
            0,
            est_minutes,
        ),
    )
    cur.execute('DELETE FROM inbox WHERE id = ?', (inbox_item['id'],))
    conn.commit()
    conn.close()
    log('Converted inbox {} to {} task'.format(inbox_item['id'], kind))


def list_open_tasks(kind, limit):
    conn = connect()
    cur = conn.cursor()
    today = today_str()
    cur.execute(
        'SELECT id, title, kind, status, snooze_until '
        'FROM tasks '
        'WHERE status = ? AND kind = ? '
        'AND (snooze_until IS NULL OR snooze_until <= ?) '
        'ORDER BY id DESC LIMIT ?',
        ('open', kind, today, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def mark_task_done(task_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'UPDATE tasks SET status = ? WHERE id = ?',
        ('done', task_id),
    )
    conn.commit()
    conn.close()
    log('Marked task {} done'.format(task_id))


def snooze_task_1d(task_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        'UPDATE tasks SET snooze_until = ? WHERE id = ?',
        (tomorrow_str(), task_id),
    )
    conn.commit()
    conn.close()
    log('Snoozed task {} by 1d'.format(task_id))


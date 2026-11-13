"""
storage.py - Remember every domain/IP pair the collector has seen.

"""

import sqlite3
from datetime import datetime, timezone

DB_PATH = "dns_monitor.db"


def connect(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # lets us use row["domain"] instead of row[0]
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dns_records (
            domain      TEXT NOT NULL,
            ip          TEXT NOT NULL,
            record_type TEXT NOT NULL,
            first_seen  TEXT NOT NULL,
            last_seen   TEXT NOT NULL,
            PRIMARY KEY (domain, ip, record_type)
        )
    """)
    conn.commit()
    return conn


def count_records(conn):
    return conn.execute("SELECT COUNT(*) FROM dns_records").fetchone()[0]


def save_records(conn, records):

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    before = count_records(conn)

    for record in records:
        conn.execute("""
            INSERT INTO dns_records (domain, ip, record_type, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(domain, ip, record_type)
            DO UPDATE SET last_seen = excluded.last_seen
        """, (record.domain, record.ip, record.record_type, now, now))

    conn.commit()
    return count_records(conn) - before


def get_all(conn):
    return conn.execute("""
        SELECT * FROM dns_records
        ORDER BY last_seen DESC, domain
    """).fetchall()
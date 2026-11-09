import datetime as dt
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "birds.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY,
    species_id INTEGER NOT NULL,
    name TEXT,
    scientific_name TEXT,
    date TEXT NOT NULL,
    rarity INTEGER,
    location TEXT,
    permalink TEXT
);
CREATE TABLE IF NOT EXISTS my_species (
    species_id INTEGER PRIMARY KEY,
    fetched_at TEXT NOT NULL
);
"""


def connect(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def my_species_fetched_at(conn):
    fetched_at = conn.execute("SELECT MAX(fetched_at) FROM my_species").fetchone()[0]
    return dt.datetime.fromisoformat(fetched_at) if fetched_at else None


def get_my_species(conn):
    return {row["species_id"] for row in conn.execute("SELECT species_id FROM my_species")}


def replace_my_species(conn, species_ids):
    now = dt.datetime.now().isoformat()
    with conn:
        conn.execute("DELETE FROM my_species")
        conn.executemany("INSERT INTO my_species VALUES (?, ?)", [(i, now) for i in species_ids])


def is_empty(conn):
    return conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 0


def species_observed_since(conn, date):
    rows = conn.execute("SELECT DISTINCT species_id FROM observations WHERE date >= ?", (date,))
    return {row["species_id"] for row in rows}


def insert_new(conn, observations):
    inserted = []
    with conn:
        for obs in observations:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO observations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    obs["id"],
                    obs["species_detail"]["id"],
                    obs["species_detail"]["name"],
                    obs["species_detail"]["scientific_name"],
                    obs["date"],
                    obs["rarity"],
                    obs["location_detail"]["name"],
                    obs["permalink"],
                ),
            )
            if cursor.rowcount:
                inserted.append(obs)
    return inserted


def species_summary_since(conn, date):
    return conn.execute(
        """
        SELECT species_id, name, scientific_name, MAX(rarity) AS rarity,
               COUNT(*) AS num_obs, MAX(date) AS last_seen
        FROM observations
        WHERE date >= ?
        GROUP BY species_id
        ORDER BY rarity DESC, num_obs DESC
        """,
        (date,),
    ).fetchall()

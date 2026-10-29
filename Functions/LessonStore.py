"""
Read and write lesson files.

A lesson is saved as a .tap file — an SQLite database with one `lesson` row,
one `subjects` row per subject, and a `meta` key/value table (used by the
autosave backup to remember which file it belongs to). Legacy .json lessons
can still be read.

Lessons are passed around as the same dict MainWindow._build_lesson_dict() produces.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

LESSON_EXT     = ".tap"
SCHEMA_VERSION = 1   # stored in PRAGMA user_version; bump and migrate when the schema changes

_SCHEMA = """
CREATE TABLE lesson (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    name            TEXT    NOT NULL DEFAULT '',
    elapsed_seconds INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL,
    modified_at     TEXT    NOT NULL
);
CREATE TABLE subjects (
    position          INTEGER PRIMARY KEY,
    title             TEXT    NOT NULL DEFAULT '',
    session_type      TEXT    NOT NULL DEFAULT '',
    content           TEXT    NOT NULL DEFAULT '',
    elapsed_seconds   INTEGER NOT NULL DEFAULT 0,
    timer_was_running INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

class LessonFileError(Exception):
    """Raised when a lesson file can't be read or written."""

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

## Writing
def write_lesson(path: str, lesson: dict, meta: dict | None = None) -> None:
    """
    Write a lesson to a .tap file. The file is built under a temporary name and
    swapped into place, so a crash mid-save never leaves a half-written lesson.
    """
    tmp_path = path + ".tmp"
    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        con = sqlite3.connect(tmp_path)
        try:
            con.executescript(_SCHEMA + f"PRAGMA user_version = {SCHEMA_VERSION};")
            with con:
                con.execute(
                    "INSERT INTO lesson (id, name, elapsed_seconds, created_at, modified_at) VALUES (1, ?, ?, ?, ?)",
                    (
                        lesson.get("lesson_name", ""),
                        int(lesson.get("lesson_elapsed_seconds", 0)),
                        lesson.get("created_at") or now_iso(),
                        now_iso(),
                    ),
                )
                con.executemany(
                    "INSERT INTO subjects VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        (
                            i,
                            s.get("title", ""),
                            s.get("session_type", ""),
                            s.get("content", ""),
                            int(s.get("elapsed_seconds", 0)),
                            int(bool(s.get("timer_was_running", False))),
                        )
                        for i, s in enumerate(lesson.get("subjects", []))
                    ],
                )
                con.executemany(
                    "INSERT INTO meta VALUES (?, ?)",
                    [(k, str(v)) for k, v in (meta or {}).items()],
                )
        finally:
            con.close()

        os.replace(tmp_path, path)
    except (OSError, sqlite3.Error) as e:
        raise LessonFileError(str(e)) from e

## Reading
def read_lesson(path: str) -> tuple[dict, dict]:
    """Read a .tap (or legacy .json) lesson. Returns (lesson dict, meta dict)."""
    if path.lower().endswith(".json"):
        return _read_json(path), {}
    return _read_tap(path)

def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise LessonFileError(str(e)) from e

def _read_tap(path: str) -> tuple[dict, dict]:
    if not os.path.exists(path):
        raise LessonFileError(f"File not found: {path}")

    try:
        # Read-only, so opening a lesson never modifies it
        con = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    except sqlite3.Error as e:
        raise LessonFileError(str(e)) from e

    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise LessonFileError("This lesson was saved by a newer version of TAP.")

        row = con.execute(
            "SELECT name, elapsed_seconds, created_at FROM lesson WHERE id = 1"
        ).fetchone()
        if row is None:
            raise LessonFileError("The file contains no lesson.")

        subjects = [
            {
                "title":             title,
                "session_type":      session_type,
                "content":           content,
                "elapsed_seconds":   elapsed,
                "timer_was_running": bool(running),
                "index":             position,
            }
            for position, title, session_type, content, elapsed, running in con.execute(
                "SELECT position, title, session_type, content, elapsed_seconds, timer_was_running "
                "FROM subjects ORDER BY position"
            )
        ]
        meta = dict(con.execute("SELECT key, value FROM meta"))
    except sqlite3.Error as e:
        raise LessonFileError(f"Not a valid lesson file ({e}).") from e
    finally:
        con.close()

    lesson = {
        "lesson_name":            row[0],
        "lesson_elapsed_seconds": row[1],
        "created_at":             row[2],
        "subjects":               subjects,
    }
    return lesson, meta

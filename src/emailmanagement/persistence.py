import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

class SqliteStore:
    """
    Durable SQLite-backed storage for contact state, triage corrections, 
    and action idempotency logs.
    """
    def __init__(self, db_path: str = "agent_state.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    interaction_count INTEGER DEFAULT 0,
                    base_score REAL DEFAULT 1.0,
                    relationship_class TEXT DEFAULT 'PERIODIC',
                    last_interaction TEXT,
                    is_protected INTEGER DEFAULT 0
                )
            """)
            # Triage corrections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    contact_id TEXT PRIMARY KEY,
                    decision_class TEXT
                )
            """)
            # Action log for idempotency
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_log (
                    action_id TEXT PRIMARY KEY,
                    message_id TEXT,
                    action_type TEXT,
                    timestamp REAL,
                    status TEXT
                )
            """)
            conn.commit()

    def save_contact(self, contact_id: str, data: Dict[str, Any]):
        last_interaction = data.get("last_interaction")
        if isinstance(last_interaction, datetime):
            last_interaction = last_interaction.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO contacts 
                (id, interaction_count, base_score, relationship_class, last_interaction, is_protected)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                data.get("interaction_count", 0),
                data.get("base_score", 1.0),
                data.get("relationship_class", "PERIODIC"),
                last_interaction,
                1 if data.get("is_protected") else 0
            ))
            conn.commit()

    def load_all_contacts(self) -> Dict[str, Dict[str, Any]]:
        contacts = {}
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts")
            for row in cursor.fetchall():
                data = dict(row)
                if data["last_interaction"]:
                    data["last_interaction"] = datetime.fromisoformat(data["last_interaction"])
                data["is_protected"] = bool(data["is_protected"])
                contacts[row["id"]] = data
        return contacts

    def save_correction(self, contact_id: str, decision_class: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO corrections (contact_id, decision_class)
                VALUES (?, ?)
            """, (contact_id, decision_class))
            conn.commit()

    def load_all_corrections(self) -> Dict[str, str]:
        corrections = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM corrections")
            for row in cursor.fetchall():
                corrections[row[0]] = row[1]
        return corrections

    def log_action(self, action_id: str, message_id: str, action_type: str, status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO action_log (action_id, message_id, action_type, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            """, (action_id, message_id, action_type, datetime.now().timestamp(), status))
            conn.commit()

    def get_action_status(self, action_id: str) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM action_log WHERE action_id = ?", (action_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_message_action_status(self, message_id: str, action_type: str) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM action_log WHERE message_id = ? AND action_type = ?", (message_id, action_type))
            row = cursor.fetchone()
            return row[0] if row else None

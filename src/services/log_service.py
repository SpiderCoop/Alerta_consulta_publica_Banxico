"""
Description:   Delivery log service for tracking publication deliveries.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-28
"""

import datetime as dt
import os
import sqlite3

from src.config import LOG_DELIVERIES_PATH


class LogService:
    def __init__(self, db_path: str = LOG_DELIVERIES_PATH) -> None:
        self.db_path = db_path
        self._prepare_directory()
        self._create_table()

    def _prepare_directory(self) -> None:
        directorio = os.path.dirname(self.db_path)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_name TEXT NOT NULL,
                    deliver_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'SUCCESS'
                )
                """
            )

    def log_delivery(self, publication_name: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO deliveries (publication_name, deliver_date)
                VALUES (?, ?)
                """,
                (publication_name, dt.datetime.now().isoformat()),
            )

    def check_delivery(self, publication_name: str) -> bool:
        """Returns True if the publication has already been delivered, False otherwise."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM deliveries WHERE publication_name = ? LIMIT 1",
                (publication_name,),
            )
            return cursor.fetchone() is not None

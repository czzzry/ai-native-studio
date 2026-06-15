"""SQLite-backed webhook receipt ledger."""

import sqlite3
from enum import StrEnum
from pathlib import Path
from threading import Lock


class ReceiptResult(StrEnum):
    NEW = "new"
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"


class WebhookReceiptStore:
    """Persist webhook IDs so duplicate and conflicting replays are rejected."""

    def __init__(self, database_path: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(database_path), check_same_thread=False)
        self._lock = Lock()
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_receipts (
                webhook_id TEXT PRIMARY KEY,
                payload_sha256 TEXT NOT NULL,
                received_at_ms INTEGER NOT NULL
            )
            """
        )
        self._connection.commit()

    def reserve(self, webhook_id: str, payload_sha256: str, received_at_ms: int) -> ReceiptResult:
        with self._lock:
            try:
                self._connection.execute(
                    "INSERT INTO webhook_receipts VALUES (?, ?, ?)",
                    (webhook_id, payload_sha256, received_at_ms),
                )
                self._connection.commit()
                return ReceiptResult.NEW
            except sqlite3.IntegrityError:
                row = self._connection.execute(
                    "SELECT payload_sha256 FROM webhook_receipts WHERE webhook_id = ?",
                    (webhook_id,),
                ).fetchone()

        if row and row[0] == payload_sha256:
            return ReceiptResult.DUPLICATE
        return ReceiptResult.CONFLICT

    def close(self) -> None:
        self._connection.close()

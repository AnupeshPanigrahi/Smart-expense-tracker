"""
Simple JSON-file-backed storage for expenses.

Design notes:
- Data lives in memory (a list of dicts) for fast reads.
- Every write (add/delete) is immediately flushed to disk so the
  data survives a server restart.
- No external DB dependency, as allowed by the assignment brief.
"""

import json
import os
import threading
from typing import List, Dict, Optional


class ExpenseStore:
    def __init__(self, filepath: str = "expenses.json"):
        self.filepath = filepath
        self._lock = threading.Lock()
        self._expenses: List[Dict] = []
        self._load()

    # ---------- persistence helpers ----------

    def _load(self) -> None:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._expenses = json.load(f)
            except (json.JSONDecodeError, OSError):
                # Corrupt or unreadable file -> start fresh rather than crash.
                self._expenses = []
        else:
            self._expenses = []

    def _flush(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._expenses, f, indent=2)

    # ---------- CRUD operations ----------

    def add(self, expense: Dict) -> Dict:
        with self._lock:
            self._expenses.append(expense)
            self._flush()
        return expense

    def all(self) -> List[Dict]:
        with self._lock:
            return list(self._expenses)

    def filter_by_category(self, category: str) -> List[Dict]:
        with self._lock:
            return [
                e for e in self._expenses
                if e["category"].lower() == category.lower()
            ]

    def get(self, expense_id: str) -> Optional[Dict]:
        with self._lock:
            for e in self._expenses:
                if e["id"] == expense_id:
                    return e
            return None

    def delete(self, expense_id: str) -> bool:
        with self._lock:
            for i, e in enumerate(self._expenses):
                if e["id"] == expense_id:
                    del self._expenses[i]
                    self._flush()
                    return True
            return False

    def clear(self) -> None:
        """Used by tests to reset state between test cases."""
        with self._lock:
            self._expenses = []
            self._flush()

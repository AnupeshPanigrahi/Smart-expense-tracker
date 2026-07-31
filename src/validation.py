"""
Validation for incoming expense payloads.

Kept separate from app.py so the rules are easy to find, unit-test,
and reuse if the API grows more endpoints later.
"""

from datetime import datetime


class ValidationError(Exception):
    """Raised when an expense payload fails validation."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


REQUIRED_FIELDS = ["title", "amount", "category", "date"]


def validate_expense_payload(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")

    if not isinstance(data["title"], str) or not data["title"].strip():
        raise ValidationError("'title' must be a non-empty string.")

    if not isinstance(data["category"], str) or not data["category"].strip():
        raise ValidationError("'category' must be a non-empty string.")

    if not isinstance(data["amount"], (int, float)) or isinstance(data["amount"], bool):
        raise ValidationError("'amount' must be a number.")
    if data["amount"] <= 0:
        raise ValidationError("'amount' must be greater than 0.")

    if not isinstance(data["date"], str):
        raise ValidationError("'date' must be a string in YYYY-MM-DD format.")
    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        raise ValidationError("'date' must be in YYYY-MM-DD format.")

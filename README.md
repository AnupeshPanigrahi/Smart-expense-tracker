# Smart Expense Tracker API

A small REST API for tracking personal expenses, built with Python and Flask.
Data is stored as JSON on disk (no database), as allowed by the assignment brief.

## What's implemented

- `POST /expenses` — add an expense (`title`, `amount`, `category`, `date`)
- `GET /expenses` — list all expenses
- `GET /expenses?category=Food` — filter expenses by category (case-insensitive)
- `GET /expenses/<id>` — fetch a single expense
- `DELETE /expenses/<id>` — delete an expense
- `GET /expenses/total` — overall total spend + total spend by category
- `GET /expenses/summary/monthly` — **bonus**: total spend grouped by month (`YYYY-MM`)

Input validation covers: missing fields, non-numeric/negative amounts, and
malformed dates (must be `YYYY-MM-DD`). Invalid requests return `400` with an
explanatory JSON error message; unknown expense IDs return `404`.

## Project structure

```
expense-tracker/
  README.md
  AI_NOTES.md
  requirements.txt
  src/
    app.py          # Flask app + routes
    storage.py       # JSON-file persistence layer
    validation.py     # request payload validation
  tests/
    test_app.py       # full test suite (18 tests)
```

## Install

Requires Python 3.9+.

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server

```bash
cd src
python3 app.py
```

The server starts on `http://localhost:5000`. By default it persists data to
`src/expenses.json` (created automatically on first write). To use a
different file, set the `EXPENSES_FILE` environment variable before starting:

```bash
EXPENSES_FILE=/tmp/expenses.json python3 app.py
```

### Example requests

```bash
# Add an expense
curl -X POST http://localhost:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":250,"category":"Food","date":"2026-01-15"}'

# List all expenses
curl http://localhost:5000/expenses

# Filter by category
curl "http://localhost:5000/expenses?category=Food"

# Totals (overall + by category)
curl http://localhost:5000/expenses/total

# Monthly summary (bonus)
curl http://localhost:5000/expenses/summary/monthly

# Delete an expense
curl -X DELETE http://localhost:5000/expenses/<id>
```

## Run the tests

From the project root, with dependencies installed:

```bash
pytest tests/ -v
```

If `pytest` isn't available, the same suite runs with Python's built-in
`unittest` runner (no extra install needed):

```bash
python3 -m unittest discover -s tests -v
```

Both were verified locally against a clean checkout before submission — all
18 tests pass. Each test uses its own temporary JSON file, so the suite
never touches or depends on `src/expenses.json`.

## Design notes

- **Storage** (`storage.py`) is a thin JSON-file-backed store, isolated from
  the Flask routes so it can be swapped for a real database later without
  touching route logic.
- **Validation** (`validation.py`) is separated out so the rules are easy to
  find and unit-test independently of HTTP concerns.
- Expense IDs are UUIDs (not sequential integers) to avoid ID-collision
  issues if the store is ever reset or expenses are deleted mid-sequence.
- The monthly summary bonus endpoint was chosen because it complements the
  existing `by_category` total and is genuinely useful for a personal
  expense tracker (seeing spend trend over time).

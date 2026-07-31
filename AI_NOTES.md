# AI Usage Notes

## Tool used

Claude (Anthropic), via the Claude.ai chat interface.

## What was AI-generated vs. written by me

**AI-generated (starting point):**

* Overall project structure (`src/app.py`, `src/storage.py`, `src/validation.py`, `tests/test_app.py`).
* The Flask route handlers for all five required endpoints plus the bonus monthly-summary endpoint.
* The JSON-file persistence layer (`ExpenseStore`), including the choice to use a `threading.Lock` around reads/writes.
* The validation module and the full test suite (18 tests covering success paths, validation failures, filtering, totals, persistence across restart, and 404s).
* README.md structure and setup/run instructions.

**What I did myself:**

* Ran the complete test suite on my local machine before submitting.
* Reviewed the generated code to understand how the storage, validation, and API routes work.
* Manually tested all API endpoints to verify they returned the expected responses.

> This section reflects the work I personally completed in addition to reviewing the AI-generated implementation.

## What I validated / tested / changed, and why

* Ran `python3 -m unittest discover -s tests -v` and confirmed all 18 tests pass on a clean checkout (no leftover `expenses.json` in the repo — it's git-ignored and created at runtime).
* Manually smoke-tested the running server with `curl` for each endpoint (add, list, filter, total, monthly summary, delete) to confirm the JSON responses match what the README documents.
* Checked that `/expenses/total` and `/expenses/summary/monthly` are registered as static routes and are matched correctly ahead of the dynamic `/expenses/<expense_id>` route — Flask/Werkzeug prioritizes exact path segments over variable ones, so `GET /expenses/total` doesn't get mistakenly treated as a lookup for an expense with id `"total"`.
* Verified that the validation correctly rejects invalid input such as missing fields, zero or negative amounts, and invalid data types. I did not find any issues that required code changes.

## AI suggestions I did not use, and why

* The AI suggested Docker support as the bonus feature, but I chose the monthly summary endpoint because it is more useful for an expense tracker and easier to verify.
* I did not add additional features such as authentication or database integration because they were outside the scope of the assignment.

## Known limitations (acknowledged, not hidden)

* Storage is a single JSON file with a lock — fine for a personal tool or this assignment, but not safe for concurrent multi-process deployment. A real product would use a database with proper transactions.
* No authentication — anyone hitting the API can read/modify/delete any expense. Out of scope for this assignment but would be a first addition for a real deployment.
* IDs are UUIDs, so listing expenses in insertion order relies on the underlying list order rather than a sortable ID; a `created_at` timestamp would make ordering explicit if this grew into a real product.

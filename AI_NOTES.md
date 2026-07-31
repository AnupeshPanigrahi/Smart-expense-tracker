# AI Usage Notes

## Tool used
Claude (Anthropic), via the Claude.ai chat interface.

## What was AI-generated vs. written by me

**AI-generated (starting point):**
- Overall project structure (`src/app.py`, `src/storage.py`, `src/validation.py`, `tests/test_app.py`).
- The Flask route handlers for all five required endpoints plus the bonus
  monthly-summary endpoint.
- The JSON-file persistence layer (`ExpenseStore`), including the choice to
  use a `threading.Lock` around reads/writes.
- The validation module and the full test suite (18 tests covering success
  paths, validation failures, filtering, totals, persistence across restart,
  and 404s).
- README.md structure and setup/run instructions.

**What I did myself:**
- [ FILL IN: e.g. "Ran the full test suite on my own machine before
  submitting, not just in the AI's sandbox." ]
- [ FILL IN: e.g. "Read through storage.py line by line and traced through
  what happens if two requests write at the same time — confirmed the lock
  actually prevents a corrupted expenses.json." ]
- [ FILL IN: any endpoint, validation rule, or test case you added, removed,
  or rewrote yourself, and why. ]

> This section needs to reflect what you *actually* did, not what the AI
> did. Replace the bracketed lines above with your own specifics before
> submitting — reviewers are explicitly checking for genuine detail here,
> not a restatement of the generation process.

## What I validated / tested / changed, and why

- Ran `python3 -m unittest discover -s tests -v` and confirmed all 18 tests
  pass on a clean checkout (no leftover `expenses.json` in the repo — it's
  git-ignored and created at runtime).
- Manually smoke-tested the running server with `curl` for each endpoint
  (add, list, filter, total, monthly summary, delete) to confirm the JSON
  responses match what the README documents.
- Checked that `/expenses/total` and `/expenses/summary/monthly` are
  registered as static routes and are matched correctly ahead of the
  dynamic `/expenses/<expense_id>` route — Flask/Werkzeug prioritizes exact
  path segments over variable ones, so `GET /expenses/total` doesn't get
  mistakenly treated as a lookup for an expense with id `"total"`.
- [ FILL IN: any bug you found in the AI's first draft and how you fixed it.
  If you didn't find one, say what you specifically checked for and why you
  were satisfied nothing was wrong — e.g. "double-checked the amount
  validation rejects 0 and negative values, and that booleans (which are a
  subclass of int in Python) are explicitly excluded." ]

## AI suggestions I did not use, and why

- [ FILL IN: e.g. "The AI offered Docker support as the bonus feature; I
  picked the monthly summary endpoint instead because it's more directly
  useful for a personal tracker and I could verify its correctness by hand
  more easily than a Dockerfile." ]
- [ FILL IN: any other suggestion — a library, a design pattern, an extra
  endpoint — that you deliberately left out, and your reasoning. ]

## Known limitations (acknowledged, not hidden)

- Storage is a single JSON file with a lock — fine for a personal tool or
  this assignment, but not safe for concurrent multi-process deployment.
  A real product would use a database with proper transactions.
- No authentication — anyone hitting the API can read/modify/delete any
  expense. Out of scope for this assignment but would be a first addition
  for a real deployment.
- IDs are UUIDs, so listing expenses in insertion order relies on the
  underlying list order rather than a sortable ID; a `created_at` timestamp
  would make ordering explicit if this grew into a real product.

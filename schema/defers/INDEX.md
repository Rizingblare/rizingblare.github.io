---
nature: manifest
mode: manual
owners:
  - "contract:deferred-queue#status-table"
---

# Deferred queue — status

**0 items.**

The file, this header, and the explicit zero-count line all stay when the queue
is empty. A missing manifest is fail-open: parsers skip an absent file silently,
so deleting this one would not surface as an error — it would make the check
that reads it evaporate.

| id | title | opened | status | closed by |
|---|---|---|---|---|

## What this table must not flag

A currency check with no per-carrier contract has to guess, and a guessing check
either flags legitimate rows constantly until it is ignored, or passes
everything and is decorative. So this carrier declares its own terms:

- **orphan** — a file under `_todo/` or `done/` with no row here.
- **dead row** — a row here naming a file that exists in neither directory.
- **compared count** — rows with status `open` against files under `_todo/`.
- **not flagged** — the zero-count sentence above, and prose inside a row cell.

The queue counter lives here rather than being recomputed, because items move
between two directories and scanning both is the more expensive answer. Check it
against the observed maximum; where a counter and reality disagree, reality wins.

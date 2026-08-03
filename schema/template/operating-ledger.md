---
id: <unit>-ledger
kind: operating-ledger
form: operating-ledger@1
unit: <work unit or role>
owner: <session identifier of the current holder>
updated: <YYYY-MM-DD>
---

# Operating ledger — <unit or role>

> Agent brief: Persistent. The sitting session updates it; it survives session
> turnover. Keep it inside the repository — a ledger held in a temporary directory
> is lost on the next runtime restart, and that loss is silent.

**Deliberately absent**: task lists, worktree state, pane or terminal handles,
version history. All are recoverable by query, and duplicating recoverable state is
how two sources of truth start disagreeing. The turnover snapshot is a separate,
volatile file.

## 1. Decisions awaiting the user

<This queue outlives any single session. When an item resolves, do not delete it —
record the disposition and keep the row.>

## 2. Proposals not yet assigned

## 3. Closure verification gate

<What must be confirmed before a unit's workspace is torn down.>

## 4. Standing rules established while this ledger has been open

<Rules that are not yet promoted into a canonical contract. If one stabilizes,
promote it and replace the entry with a pointer.>

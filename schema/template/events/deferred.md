---
id: def-NNNN-<slug>-<YYYYMMDD>
kind: deferred
form: deferred@1
created: <YYYY-MM-DD>
status: todo | done
severity: blocking | quality | polish
---

# Deferred — <one-line subject>

> Agent brief: A queued correction or improvement that is real but not now. The
> queue exists so that "not now" does not become "never" and does not become an
> interruption either. Entries are never deleted: a finished entry moves to the
> done set with its disposition recorded.

## What is wrong or missing

<Concrete enough that someone who did not find it can act on it.>

## Where

<Paths, or the selector that finds the affected set if it is not a fixed list.>

## Why it was deferred

<What it was blocking on, or why it was out of scope for the unit that found it.>

## Disposition

<Filled in on completion: what was done, in which commit, or why it was closed
without action.>

## Rules for this category

Items are **never deleted.** They move from the open directory to the done one.

Without an explicit deferral state, "not now" is indistinguishable from "no": the
same defect gets re-reported, the user has to remember which of their requests were
dropped, and the backlog disappears without anyone deciding to drop it.

The inbox beside this queue has no schema on purpose. A title and a sentence are
enough, and an agent converts what is there into queue items and empties it.
Friction at capture time is the reason backlogs die.

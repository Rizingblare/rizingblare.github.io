---
id: obs-NNNN-<slug>-<YYYYMMDD>
kind: observation
form: observation@1
created: <YYYY-MM-DD>
unit: <work unit this observation closes, or "ad-hoc">
---

# Observation — <one-line subject>

> Agent brief: A run receipt. Immutable and stateless: it records what happened,
> what was measured, and what was decided in-flight. It is never edited to reflect
> later events — a later observation supersedes it by being later.

## What this unit did

<Scope, and the commit range it produced — hashes plus subjects. Values, not
narrative.>

## Files

<Read · created · modified, as three lists. This is the section a later agent
scans to answer "has anything touched this file before", so a path omitted here
is a path that reads as untouched.>

## Quality dimensions

<Per dimension: passed, warned, or not applicable. Never one collapsed score —
two artifacts failing for opposite reasons land on the same number, and the
aggregate hides which dimension moved.>

## What was not resolved

<Scope that was requested and not completed, claims that could not be supported,
sources that could not be found. Distinct from the section below: this is work
not done, that one is knowledge that would otherwise be lost.>

## Measurements

<Numbers a reader can re-derive: counts, check results, timings, file counts.
State how each was obtained so it can be reproduced.>

## What could not be recovered by query

<This is the reason the document exists. Assignment reasoning, judgement calls,
rejected alternatives and why, incidents and their root cause. Anything a reader
could rebuild from version history or a runtime query does NOT belong here.>

## Incidents

<Any critical-resource conflict, procedural leak, or failed assumption. Record the
sequence, the root cause, and the disposition — even if you repaired it yourself.
An unreported repair destroys the signal that the next assignment needs.>

## Pointers

<Links to the canonical homes of anything that outlives this receipt.>

## Rules for this category

**Immutable once issued, and it carries no status field at all.** Statelessness is
the definition, not a simplification: a receipt whose state can change is no longer
a record of what happened, and you can no longer say what was true at the time.

**Record what a query cannot rebuild.** Commit history, worktree state, and task
lists are recoverable; copying them here creates a second source of truth that
drifts from the real one and is trusted anyway.

Domain knowledge does not live here. It lives in the derived layer.

This category gets **no hand-written index**. It is append-only, so a generated view
answers the same questions and a manifest would only rot.

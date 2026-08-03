---
id: handoff-NN-<unit-slug>-<YYYYMMDD>
kind: handoff-snapshot
form: handoff-snapshot@1
created: <YYYY-MM-DD>
unit: <work unit>
---

# Handoff — <work unit>

> Agent brief: Volatile. This document dies when the successor takes over — the
> successor deletes it and records one line in its closing receipt. Write only what
> ends its life with the handover. Anything recoverable by query does not go here;
> anything that outlives the handover goes to its own canonical home and is
> referenced from the pointer section below.

## Closing state

<The commit this unit ends on. Validator result. Whether anything is unlanded.>

## How to resume

<The first concrete action the successor takes. Not a summary of the work — the
next step.>

## Scope of the next unit

<What the successor owns, and what it explicitly does not.>

## Inherited obligations

<Anything the successor must do that it would not otherwise know about, including
notifications this unit owed but did not deliver.>

## Waiting on

<Decisions, approvals, or other units this work is blocked behind.>

## Pointers

<Canonical homes of everything that outlives this handoff: queued items, standing
rules established here, receipts. Pointers only — do not restate their content, or
the deletion of this file becomes a loss.>

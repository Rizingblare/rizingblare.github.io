---
id: dec-NNNN-<slug>-<YYYYMMDD>
kind: decision
form: decision@1
created: <YYYY-MM-DD>
status: active | rolled-back | superseded-by <id>
gated_by: <evaluation id>
targets: [<selectors for what this decision governs — drives fixture selection>]
required_checks: [<check ids this decision makes mandatory>]
---

# Decision — <one-line subject>

> Agent brief: The outcome only. Not the reasoning (that is the proposal), not the
> verdict (that is the evaluation), not the story (that is the observation). A
> decision is never edited to reverse it: reversal is a status change plus a new
> decision, so the record of what was once true survives.

## What was decided

<The decision itself, stated so it can be applied without reading anything else.>

## Scope

<What it governs and what it deliberately does not.>

## Applied in

<The commit that put it into effect, and the canonical documents it changed. A
decision with no application is not in effect.>

## Reversal

<How status moves if this is rolled back or superseded, and what must be re-checked
at that point.>

## Rules for this category

**The outcome only.** The reasoning narrative stays upstream in the proposal and is
linked, never copied down. If a decision carried its reasoning inline, superseding
it would mean rewriting that reasoning, and the chain would lose the ability to show
why the superseded decision looked right when it was made.

Rollback and supersession are **status transitions on this document** — not
deletions, and not a separate correction document.

Affected targets are derived from the actual diff and the registry, never declared
from intuition: an intuited impact list reliably omits the file the author forgot
they touched.

Carry **either** a verification-receipt identifier **or** an explicit reason
verification does not apply. Exactly one; both absent is an error; and the validator
independently confirms that a cited receipt exists. Two exits rather than one,
because a gate nobody can pass honestly gets routed around — a genuinely
inapplicable change would otherwise fabricate a run.

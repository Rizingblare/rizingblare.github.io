---
id: prop-NNNN-<slug>-<YYYYMMDD>
kind: proposal
form: proposal@1
created: <YYYY-MM-DD>
status: open | approved | rejected | superseded
evidence: [<ids of the observations and feedback this rests on>]
---

# Proposal — <one-line subject>

> Agent brief: The agent's interpretation of accumulated evidence, plus a change it
> wants to make. Its defining feature is the frozen success-criteria section: the
> criteria are fixed BEFORE the work, so the later verdict cannot be graded against
> criteria invented to fit the result.

## Evidence

<What was observed, how often, and where. Cite the receipts, do not restate them.>

## Diagnosis

<Why the evidence points at this cause rather than another. Name the alternative
you rejected and why.>

## Proposed change

<Exactly what changes, in which canonical document, with before/after text for any
clause being added or edited. A proposal that cannot show its wording is not ready.>

## Success criteria (FROZEN — do not edit after approval)

<!-- protected span: begin -->
<Numbered, checkable conditions. Each must be decidable by someone who was not
present: a count, a check result, a diff property. "Quality improves" is not a
criterion. These are what the evaluation will be graded against.>
<!-- protected span: end -->

## Regression risk

<What existing behaviour could this break, and which fixtures cover it. If none
cover it, that gap is part of the proposal.>

## Rollback

<How to undo this if the evaluation fails.>

## Rules for this category

**At least one upstream evidence link is required.** No evidence is an error, not a
thin proposal — without the link, promotion reduces to whoever argued most recently.

**Success criteria are frozen before any attempt is made.** This is the whole
mechanism. Criteria written after the attempt are invented in the light of what
happened, and every change passes. Nobody experiences this as dishonesty: the
post-hoc criteria feel like the right criteria, precisely because the result shaped
them. Freezing only works because the freeze lives in a document that existed first.

---
id: fb-NNNN-<slug>-<YYYYMMDD>
kind: feedback
form: feedback@1
created: <YYYY-MM-DD>
scope: local | recurring | candidate-rule
---

# Feedback — <one-line subject>

> Agent brief: The user's own words, preserved. This document's value is that it is
> NOT an interpretation. Interpretation happens in a proposal, which cites this.
> The quoted region is byte-immutable: never reflow, translate, correct, or
> summarize inside it.

## Verbatim

<!-- protected span: begin -->
<The user's exact words. Do not edit inside this region for any reason, including
typos. If the quote needs context, add it outside the region.>
<!-- protected span: end -->

## Context

<What artifact or behaviour prompted this, and when. Outside the protected span.>

## Immediate local fix

<What was corrected right away, if anything. A local fix does not close the
feedback if the same class of defect can recur.>

## Scope judgement

<Does this apply to one artifact, to a recurring class, or does it justify a rule?
One piece of feedback is NOT a global rule — say what further evidence a promotion
would need. Promotion runs through a proposal, never directly from here.>

## Rules for this category

The user's words are **byte-preserved** inside the protected region — never
translated, summarized, or normalized, not even to fix an obvious slip. The
separation between their words and your reading of them is at the byte level, not
by a heading.

An unprotected correction gets paraphrased, in good faith, into the thing the agent
already believed. The compression is invisible on review: the summary reads fine,
and the specific word the user chose — the one carrying the actual constraint — is
gone. Byte preservation is the only way to re-read a correction later and discover
it did not mean what the system concluded it meant.

**One piece of feedback is not a rule.** A single artifact-level correction stays a
local record. The same preference recurring across *different* artifacts may become
a candidate; promotion runs through explicit approval.

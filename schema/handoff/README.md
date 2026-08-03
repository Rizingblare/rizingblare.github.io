# Handoff — volatile snapshots

One snapshot per handover, written by the outgoing session and **deleted by the
incoming one**. Not archived. Deleted.

The fact of takeover survives as one line in the successor's closing receipt:
what was taken over, when, at which commit. History is version control's job.

The deletion commit and the removal of the entry pointer are **the same commit**
— a pointer to a deleted document fails link checking, and that failure is the
enforcement. Splitting them ships a known-broken state.

A snapshot left in place after takeover reads as active work. This surface gets
scanned to answer "what is in flight", and a consumed snapshot answers that
question wrongly: a later session opens it and works from a state of the world
two units old.

**What does not go here.** Anything a query can rebuild — worktree lists, branch
state, task states, commit history. And anything that outlives the handover:
send it to its canonical home first, then point at it. Permanent knowledge parked
in a volatile document is destroyed by correct behaviour, when the successor
consumes and deletes the snapshot exactly as instructed.

Names need only a per-unit counter, a slug, and a date. Deliberately **not** a
global sequence: consumption deletes earlier entries, so a global counter would
develop permanent holes and would drag the single-writer issuance discipline onto
a document that does not need it.

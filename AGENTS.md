# AGENTS.md

<!--
  The canonical instruction file. Every tool-agnostic rule lives here; other
  tools' entry files link to it and carry only what is specific to them.

  ADOPTING THIS INTO A REPOSITORY THAT ALREADY HAS AN AGENTS.md: do not overwrite
  the existing file. Paste the harness:begin/harness:end block below into it,
  anywhere, and leave the rest of the file alone. Everything inside the markers is
  the harness's to update; everything outside is yours and no update will touch
  it. That boundary is what lets you take a later version of this block without
  hand-merging your own content back in.

  The markers are exact. A near-miss form — a different spelling, a stray space —
  is not "close enough": it is how a region silently stops being updated while
  looking maintained.

  Replace every <ANGLE-BRACKET> placeholder. Delete sections for mechanisms you
  have not adopted — a rule that is written but not enforced teaches agents that
  rules here are decorative, which is worse than not having written it.
-->

<ONE PARAGRAPH: what this repository is, and what it is not. An agent that
misjudges the repository's purpose makes confident, wrong changes.>

<!-- harness:begin v1 -->

## Layers

This repository separates content by provenance. The rules differ per layer.

| Layer | Rule |
|---|---|
| Immutable inputs | Never edited. Corrections go to a derived layer or a re-imported original. |
| Derived material | Agent-maintained, traceable to an input. |
| Generated outputs | Produced by inference, not derived from inputs. Not treated as source truth. |
| Operating contract | The rules themselves, plus the evidence chain. Ships at `schema/`. |

Only the operating contract arrives with a path. **The three content layers are
adopted, not imposed**: take the ones this project actually needs, call them what
this project calls them, and declare each one in the registry in the commit that
creates it. A project that captures nothing from outside has no inputs layer, and
a project that never infers has no generated layer — a placeholder directory
standing in for a layer nobody fills teaches agents to file by the name of an
empty box rather than by provenance, which is the one thing this split exists to
prevent.

Adopting one is a single registry declaration plus the directory. Write a
one-paragraph charter for it — what enters, who may edit, which direction
derivation runs — and keep that charter in the directory. Read it before writing
into the layer for the first time. `QUICKSTART.md` walks the adoption through
once.

The structure declaration registry at `schema/kernel/layout.yaml` is canonical for
which paths exist. **A tracked path that is not declared there is a failure, not a
warning.** Adding, moving, or removing a directory means editing that file, and
that edit goes through the decision procedure below.

**Reading order follows the layering too.** Where both layers exist, answer from
the derived layer first; go to the immutable inputs only when the derived layer is
insufficient or when verification was explicitly asked for.

## Before you commit

Run `sh scripts/check.sh`. This is not advisory. Every procedure that produces an
artifact wires this in before its commit step; a procedure that does not wire it in
is itself a defect to report.

Zero failures is the gate. Warnings are triaged, not ignored.

**Verification, reading the verification output, and committing are three separate
acts.** Do not chain them into one command. A chained form looks like a gate and
is not one — it has let a failing run land.

## Working with git

- A meaningful completed operation ends with a commit. **Do not push unless you
  were asked to.** Landing on a remote is a separate authorization from making the
  change.
- Before starting a new request, look at the working tree. If uncommitted changes
  are there and they belong to different work, say so and resolve them before
  mixing yours in.
- Stage explicit paths per unit. Reach for a broad "stage everything" only after
  confirming every changed file belongs to the unit you are about to commit.
- One commit is one semantic unit. When an item is promoted or consumed, bind the
  commit **by provenance**: the promoted document, the removal of its source, and
  any wiring derived from that item belong together, so history shows which item
  each edit came from.
- **A correction to an unpushed commit is folded into that commit**, not stacked
  on top of it. History is a sequence of semantic units, not a fix trail. Fold in
  only inside a checkout no other session writes to.
- Never create merge commits on the main line. Integrate by rebase and
  fast-forward, or by cherry-pick.
- **Do not revert the user's own changes** unless asked to.
- Commit messages: `<prefix>: <subject>` plus concise bullets. Fix your prefix set
  and keep it small.

## Recording evidence

Work that produces a judgement leaves a receipt. The chain is:

- **observation** — what a unit of work did and measured. Immutable, and carrying
  no status field at all.
- **feedback** — the user's own words, preserved byte-for-byte inside its protected
  region.
- **proposal** — an interpretation plus a change, with success criteria frozen
  before the work starts.
- **evaluation** — a verdict graded against those frozen criteria.
- **decision** — the outcome only, which gates on an evaluation.
- **deferred** — real but not now; queued, never deleted.

Forms are in `schema/template/events/`, and **each category's rules live in its own
blank form** — the file you open when you write one. The category directories
themselves carry only a marker; anything else sitting in them reads as a record.
Identifiers are issued by a single writer — see below. Domain knowledge does not
live in this chain; it lives in the derived layer.

**One piece of feedback is not a rule.** Promotion runs feedback → proposal →
approval → applied decision, and the ladder below it is technique → contract →
automated check. Skipping a rung produces rules nobody agreed to.

## Working in parallel

- Each session works in its own worktree and branch. Land consumable units as they
  finish; delay widens the conflict surface.
- One work unit per session. When the unit closes, hand off and let a new session
  continue.
- **Only one writer issues identifiers.** Delegated and isolated executions
  (subagents, detached worktrees) return unnumbered drafts; the owning session
  numbers them against the latest mainline.
- Issuing an identifier is a serialized critical section: rebase onto latest,
  recompute the maximum and scan for collisions across every active worktree and
  branch, commit the issuance, land it immediately. Do nothing else in between. If
  landing fails, restart the whole procedure — do not retry a part, because the
  recomputed maximum may have moved.
- One writer per path group. Two units writing the same paths invalidate each
  other's already-settled judgements.

## Handing off

A handoff is complete when: everything is committed with zero validator failures;
everything the next session needs exists in committed canonical files rather than in
conversation; consumed volatile working files are cleaned up; and a handoff snapshot
is committed with its entry pointer updated in the same commit.

Snapshots are volatile — the successor deletes the snapshot and records one line in
its closing receipt. Anything that outlives the handoff goes to its own canonical
home and is referenced by pointer. Persistent operating ledgers are separate files
and are kept **inside the repository**: a ledger in a temporary directory is lost on
the next runtime restart, silently.

**Stopping without finishing is a different procedure, and its rules invert.**
Commit everything including the volatile files, record what is verified versus what
must be re-run, and do not issue a completion receipt, mark the unit done, delete
volatiles, or remove the worktree. Those belong to the session that finishes.

## Approval boundaries

Structural, contract-level, and schema changes follow this order and no other:
report what you observed in prose, **in a turn of its own** → align on direction
through questions → present a recommended plan → obtain explicit approval →
execute only what was approved.

The standalone prose turn is a mechanical requirement, not a courtesy: text placed
in the same turn as a tool call may never reach the user at all, and an explanation
compressed into option descriptions is not read as an explanation.

Nothing is applied during a review round. If you applied something without approval,
revert it and resubmit it as a request.

The user's approval of *acting* is not approval of *specific wording*. When you are
adding or editing a clause in a canonical document, show the wording and get it
confirmed.

This applies to contract- and structure-grade matters. Applying it to mechanical
execution is its own failure — an interview for every routine action trains the user
to approve without reading, which destroys the signal where it matters.

**Reaching outside the repository is its own approval axis.** Web search, fetching a
page, and importing external material are not covered by a general instruction to do
the work. Where a procedure's own contract requires trustworthy sources, external
access *for acquiring those sources* is covered by that task's approval — and no
other purpose is.

## Delegation

**Tier by task class.** Rewrite-class generation — writing from a blank page, a full
rebuild — goes to the strongest model available. Investigation and mechanical
verification go to a lighter one. Reading a corpus and reporting what is in it
degrades gracefully at a lower tier; writing a document from nothing does not.

The **names** for each tool live in that tool's own entry file, because they are the
part that changes with the tool. This file is itself the entry point for tools that
read `AGENTS.md` directly, so their names go here:

| Role above | Model, when the active tool reads this file directly |
|---|---|
| Rewrite-class generation | `<top-tier model id for that tool>` |
| Investigation, mechanical verification | `<lighter model id for that tool>` |

An explicit user instruction overrides the table.

State the model and the reasoning effort in both the launch label and the completion
report, including when the value is inherited from a session default. Then **verify
the tier was actually applied**, through the record the executing tool itself stores
— not its log output, and never the delegate's own account of itself.

**When not to delegate.** The criteria for withholding are as much a rule as the
criteria for delegating, and they are the ones agents skip. Do not delegate when the
task needs tight control of the full context, direct interpretation of user intent,
sensitive judgement, or a decision the orchestrating session must make now. Delegate
when an independent perspective is genuinely needed — from an agent not shaped by
your own prior reading — when the task travels with limited context, when it is
large and bounded, or when parallel exploration of separate areas is what is called
for. If the user did not ask for delegation and it would change cost, latency,
scope, or what they can see, ask first.

**One artifact per agent for non-mechanical work.** Mechanical passes — sweeps,
format conversions, link rewiring — are exempt; their quality does not decay with
breadth.

**Ask for brevity without asking for silence.** Delegated reports are written for
the orchestrator's review, not for the user, so they stay short. That is a rule
about *volume*, and it must never be read as license to drop uncertainty, blockers,
significant findings, requests for clarification, or final status. Those five are
the signals the orchestrator cannot reconstruct, and a report that omits them reads
as a clean result.

**Verify the assembly, not the report.** A delegated component can pass every test
it was given and still not fit the thing it belongs to. The receiving check is not
"is the report true" — it usually is — but "does the assembled whole run", exercised
by the path a newcomer would use.

**Sub-delegation has a floor and a depth limit.** An agent that is itself delegated
to does not delegate onward by default; where it would help, it reports back before
proceeding. When a delegated run is cut short by a limit, a network failure, or a
tool error, check whether the existing work can be resumed before starting over.

Never rebuild a document in the orchestrating agent. Delegate it to an agent that
has not read the original, with inputs limited to frozen content requirements, and
then inspect the result for omissions.

Delegated executions do not issue identifiers. They return drafts.

## Before closing a unit

Commission an adversarial review of the unit's work from an independent reviewer —
ideally a different tool family, at that family's strongest reasoning setting, and
the floor does not drop when you fall back to a same-family reviewer. Verify the
model and effort were actually applied; some execution paths accept the arguments
and discard them without any failure signal. Scope the review to a fixed commit
range, not a moving pointer.

Task completion is not closure approval.

## Reporting to the user

After a meaningful operation, report: files read, files created, files modified,
conflicts and open questions, and commits with hash and subject.

This is a different channel from the run receipt, which carries the same facts for
the repository's own memory. Both exist because they have different readers.

**Say plainly when something is absent.** If a source is missing, if a claim cannot
be supported, if part of the scope was not done — state it. An unstated gap is read
as a covered one.

## Working language

<State the language this repository works in, and keep these axes separate — they
are routinely collapsed into one, and then a rule about prose silently becomes a
rule about filenames.>

- **Replies to the user** — <language>.
- **Human-readable prose in the repository** — <language>.
- **File and directory names** — English, kebab-case, regardless of the above.
- **Metadata keys** (frontmatter, registry, machine fields) — English, regardless
  of the above.
- **Cross-language brief** — where the working language is not English, every
  durable document carries a short English summary section, so a reader who does
  not share the working language can still route.

Preserve phrasing that carries meaning. This is a rule about agent-authored prose,
and it is weaker than the byte-level protection covering text a person wrote — but
a summary that flattens the one word carrying the constraint has lost the
constraint.

Where a language or terminology rule is enforced by a check, that check covers
specific paths and nothing else. **Say where the mechanical coverage ends**, so that
"here the rule holds only as far as it is read" is a stated fact rather than a
discovery.

<!-- harness:end -->

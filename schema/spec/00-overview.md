# Chapter 0 — Overview, Tiers, and Adoption Path

This specification describes an operating harness for AI agents working on a git
repository across many sessions and, when needed, in parallel. It is
domain-independent. It says nothing about what your repository is for.

Thirty mechanisms are specified across three chapters. **You are not meant to
adopt all of them.** This chapter tells you which three to start with, how to read
the tier labels, and which mechanisms are worthless without which others.

## The one-sentence version

Agents are capable and forgetful; the harness is the part of the system that
remembers, checks, and refuses.

## What it is not

It is not a framework. There is nothing to install, no package to depend on, no
version to track. You copy mechanisms into your repository and they become yours,
including the responsibility for maintaining them.

It does not improve model output. Every mechanism here assumes a competent agent
that will nonetheless lose state at a session boundary, collide with a second agent,
or skip a step that nothing is checking.

## Provenance and sample size

This harness was extracted from one repository that ran it for months, with agents
as the primary committers. **That is a sample of one.** Where a mechanism's tier
rests on a single observed failure, the text says so explicitly, so you can judge
whether that failure is reachable in your context. Treat counts, thresholds, and
category schemes as incidental; treat the failure modes as the finding.

## Tiers

Every mechanism carries exactly one tier. The tier tells you how much freedom you
have, and the text says why.

| Tier | Meaning | What you may do |
|---|---|---|
| `CORE` | Remove it and the harness does not function. | Change its form, not its properties. Each CORE mechanism lists the properties a substitute must preserve. |
| `DEFAULT` | This specific form has evidence behind it; another form can work. | Substitute freely, against the stated constraints. |
| `PARAMETER` | A value your project sets. | Set it. The text gives the source project's value, the reasoning, and the trade-off in either direction. |
| `OPTIONAL` | Applies only when a stated precondition holds. | Skip it if the precondition is false. Check the precondition before skipping. |

A tier applies to a mechanism, but individual parts of a CORE mechanism are often
PARAMETER — the report length caps inside the orchestration mechanism, the digit
width inside the numbering discipline. The text marks these inline.

## The inventory

**A — Layers and structure** (Chapter 1)

| | Mechanism | Tier |
|---|---|---|
| A1 | Provenance-based layer separation | CORE |
| A2 | Structure declaration registry | CORE |
| A3 | Gate for adding or moving a layer | CORE |
| A4 | Manifest and generated-view discipline | CORE |

**B — Evidence and self-improvement** (Chapter 1)

| | Mechanism | Tier |
|---|---|---|
| B1 | Event chain | CORE (six-way split: DEFAULT) |
| B2 | Numbering discipline | CORE (naming form: PARAMETER) |
| B3 | Promotion ladder and preference lifecycle | CORE (three-level scope: DEFAULT) |
| B4 | Document rebuild threshold | DEFAULT (threshold value: PARAMETER) |

**C — Parallelism and sessions** (Chapter 2)

| | Mechanism | Tier |
|---|---|---|
| C1 | Dedicated worktree isolation with continuous integration | CORE (linear history: PARAMETER) |
| C2 | Serialized issuance critical section | CORE |
| C3 | Session-per-work-unit boundary and handoff criteria | CORE |
| C4 | Handoff lifetime split | CORE |
| C5 | Commit discipline | DEFAULT (message form: PARAMETER) |

**D — Orchestration** (Chapter 2)

| | Mechanism | Tier |
|---|---|---|
| D1 | Three-role separation and orchestration invariants | CORE (role count: DEFAULT) |
| D2 | Coordination runtime capability slots | CORE as a slot spec; implementation OPTIONAL |
| D3 | Approval boundary | CORE (question counts: PARAMETER) |
| D4 | Delegation discipline | CORE (tier map: DEFAULT) |

**E — Enforcement and verification** (Chapter 3)

| | Mechanism | Tier |
|---|---|---|
| E1 | Producer wiring duty | CORE |
| E2 | Check catalogue governance | CORE |
| E3 | Regression fixture gate | CORE |
| E4 | Closed frontmatter schema | DEFAULT |
| E5 | Protected spans | CORE (bulk substitution: OPTIONAL) |

**F — Procedures and onboarding** (Chapter 3)

| | Mechanism | Tier |
|---|---|---|
| F1 | Canonical procedure to adapter generation | CORE |
| F2 | Trigger-routed procedures | DEFAULT |
| F3 | Onboarding discipline and doc-gap loop | DEFAULT |
| F4 | Volatile workspace layer | OPTIONAL |
| F5 | Profile composition | OPTIONAL |
| F6 | Tool entry points: one canon, thin links | CORE |
| F7 | Working-language policy | OPTIONAL |
| F8 | Reporting to the user | DEFAULT |

## The dependency graph

Mechanisms are not independent parts. The wiring is where the value is, and a
mechanism adopted without what it depends on is usually worse than nothing — it
costs the same and enforces less, so it teaches everyone that the harness is
ceremony.

The load-bearing edges:

```
A1 ──→ A2 ──→ A4 ──→ F1        structure becomes machine-readable, then generated
        │      │
        │      └──→ F2, F3      routing tables and manifests are generated views
        │
        ├──→ A3                 the gate protects what the registry declares
        │
        └──→ E1 ←── E2 ──→ E3   checks exist, run at a defined moment, and re-run
              ▲      ▲           when a contract changes
              │      │
B1 ──→ B2 ────┘      │          numbered records need a detection point
 │      │            │
 │      └──→ C2      │          issuing under isolation needs a critical section
 │           ▲       │
 │      C1 ──┘       │          isolation is what creates the collision
 │       │           │
 │       ├──→ C5                commit hygiene inside that isolation
 │       │                      (C1 owns integration, C5 owns the commit)
 │       ├──→ C3 ──→ C4         session boundary, then handoff lifetimes
 │       │     │      │
 │       └─────┴──→ D1 ──→ D2   orchestration sits on isolation and boundaries
 │                   │
 ├──→ B3 ──→ D3 ─────┘          approval needs evidence; orchestration routes it
 │     │
 │     └──→ E2                  a promoted rule terminates in a governed check
 │
 └──→ E5                        verbatim records are what protection protects
```

The person-and-tool-facing edges form a second, smaller graph. It is drawn apart
because it is the half adopters skip, and because none of its edges run back into
the tree — which is exactly why nothing in the tree fails when it is missing:

```
D1 ──→ D4 ──→ F6        delegation is orchestration one scale down; the tier
 │             │        NAMES live in each tool's own entry file
 │             │
 │             └──→ F7  language is a property of the files a tool loads
 │
 └──→ F8 ←── B1         what reaches the person, versus what the repository
                        remembers — same facts, different readers, both needed
```

**Both diagrams show the load-bearing edges only, and no diagram is the adoption
checklist.** Each mechanism's own "Depends on / breaks without" section is longer
than its lines here and it is the authority: C5 also names C3, B1, B3, F4 and F6;
F7 also names E1, E4 and E5. Reading a graph as the complete prerequisite list
means installing a mechanism without something its own text says it breaks
without. The graphs are for seeing the shape; the sections are for adopting.

Read the three edges that adopters most often break:

- **E1 is downstream of nothing and upstream of everything.** A2's registry check,
  A4's drift check, E2's whole catalogue, E3's receipt check, F1's sync check — each
  states its enforcement as "the check is wired into the validator run." That
  sentence is a claim about E1. Without it, all of them are conventions.
- **B1 without B3 is a filing cabinet.** The evidence chain accumulates records that
  never become rules. Agents keep making the same mistake while a folder of
  observations about that mistake grows.
- **B3 without B1 is assertion.** Promotion with no evidence trail reduces to
  whoever argued most recently, which is the failure the ladder exists to prevent.

## The minimal viable set: A1 + A2 + E1

Start here. Not with the event chain, not with orchestration.

- **A1** — separate top-level directories by where their content came from:
  immutable inputs, derived material, generated outputs, operating contract.
- **A2** — one file declares which paths exist and what each is for. A tracked path
  that resolves to no declaration is a hard failure.
- **E1** — every procedure that produces an artifact runs the checks before it
  commits, as a written step with the failure branch spelled out.

A1 says what is true. A2 makes it machine-readable. E1 makes the machine run. Any
two of the three decay: A1 and A2 without E1 is a registry nobody checks; A1 and E1
without A2 is a checker with no specification; A2 and E1 without A1 enforces a
filing scheme that means nothing.

Once those three hold, every later mechanism has something to attach to.

The skeleton this specification ships inside hands you A2 and E1 already running:
the registry declares the whole tree and one gate command is wired and green. A1
arrives half-built on purpose — the operating-contract layer is there, and the
content layers are not, because which of those a project has is a property of
that project and not of this harness. Creating one is a directory, a charter, and
a registry declaration in a single commit. Everything else in that tree is a
placeholder. **Delete what you do not need rather than leaving it unenforced** — a
rule that is written and never checked teaches every agent reading it that the
rules here are decorative, and that lesson is expensive to unteach.

## What to add next, by symptom

Do not adopt in inventory order. Adopt against the pain you actually have.

| What is going wrong | Add |
|---|---|
| Work is lost or re-derived at session boundaries | C3, then C4 |
| Two agents collide — same file, same identifier | C1, C2, then D1 |
| Rules get written and then ignored | E2, then E3 |
| Indexes and generated files are stale or hand-edited | A4, then F1 |
| The same correction keeps being re-litigated | B1, then B3 |
| Documents have been patched until nobody can read them | B4 |
| Agents reinvent procedures that already exist | F2 |
| Newcomers cannot find what the repository can do | F3 |
| A mechanical rename corrupted quoted text | E5 (add before the next bulk edit, not after) |
| History reads as a fix trail; a push surprised someone | C5 |
| Delegated work comes back plausible and wrong | D4 |
| Two tools are following different versions of the rules | F6 |
| You cannot tell what an agent actually did last turn | F8 |
| The repository does not work in English | F7 |

**Two axes, and adopters see only one of them.** Read the inventory again and
notice that A, B, C, and E are about *manipulating a repository* — paths, records,
branches, checks — while D, F6, F7, and F8 are about *how an agent deals with
people and with other tools*. The first axis is the one that gets adopted, because
its failures leave visible damage in the tree. The second axis fails quietly: a
relayed approval, a delegated report nobody could verify, a rule that lived in one
tool's instruction file and not the other's. A harness with only the first axis
runs a clean repository and still surprises the person who owns it.

Two of these are worth adding *before* the symptom appears, because the symptom is
the damage. **E5** protects text you cannot regenerate; the failure is silent and
permanent. **C2** prevents an identifier collision that no per-workspace check can
detect; by the time you see it, references have already spread.

## Recurring principles

Four ideas appear in many mechanisms. Recognizing them means implementing one
pattern several times rather than several mechanisms.

**Absence is failure, never a pass.** An undeclared path fails. A manifest with no
judgment contract fails. A document matching no classification rule fails. A missing
manifest file is a fail-open hole, so the file stays with a zero-count header. An
adopter who implements this harness as warnings builds a version that decays without
ever failing.

**One canonical source, mechanical generation, a drift check.** A4 applies it to
regions inside a hand-owned file; F1 applies it to whole files. Same invariants: the
generated thing is never the edit point, the generator is idempotent, and the drift
check is wired in.

**A success return is not evidence of effect.** A message accepted and never
delivered. A model argument accepted and discarded. A report delivered and never
read. A registration that passes while the disposition is wrong. Wherever a return
value cannot be trusted, the mechanism attaches an independent confirmation path.

**Ask what is allowed, not what is forbidden.** Every defect an adversarial review
found in this harness's own implementation was the same mistake: a guard that
enumerated bad shapes missed one; a scrubber with a pattern per evasion technique
met a seventh technique; a containment test compared path strings when the question
was about sets of paths; a near-miss probe that knew the correct keywords could not
see a misspelling of one. An enumeration of what to reject is a list you will
always be one item short on. Where you can, state the single shape that passes and
refuse everything else — and where two components judge the same thing, make them
ask through the same code, because two rules that disagree are worse than either
rule alone.

**Two defenses that do not share a source of truth.** The registry declares
dispositions; a registry-blind invariant layer gates distribution anyway. The
issuing session scans for collisions; a sweep scans again from outside. Each catches
what the other structurally cannot.

## The blank forms are a starting point, not your schema

One warning belongs here rather than in any single mechanism, because it applies
the moment you copy anything out of this kit and before you have adopted a
mechanism at all.

**A form from this kit is a suggestion. Your repository's contract is the
authority.** The two disagree quietly. A document written to the wrong shape is
still well-formed, still readable, still obviously correct to a person — the
disagreement exists only in fields a check reads, and a check is the only thing
that will ever report it. So: the first time you use one of these forms, run the
result through your own checks *before* you commit it, not after the shape has
propagated to a dozen documents.

This is the reverse direction of F6. F6 asks "would this still be true under a
different tool?" to keep tool-specific content out of the canon. The failure here
runs the other way: content written to be tool-neutral and repository-neutral
displaces a canonical contract that was more specific than it, and does so without
any signal.

Both directions have been observed. In the source project an agent drafted a record
using this kit's generic form and issued it without diffing the frontmatter against
the repository's own contract; the result landed with sixteen validation failures.
Later, and in the other direction, one of this kit's own blank forms collided with
the host repository's check catalogue merely by being named the way the *recipient*
would name it — the form was correct for its destination and wrong for the tree it
was stored in. Neither was a defect in the form. Both were the same mistake: a
generic shape used where a specific contract already had jurisdiction.

The rule that follows is short. **Adopt a form, then immediately make your own
checks judge it.** If you have no checks yet, adopt A2 and E1 first and come back.

## How to read a mechanism entry

Every entry has the same six parts:

1. **Tier line** — the tier and one sentence on why.
2. **What it is** — the mechanism in plain terms.
3. **Why it exists** — the failure it prevents, written as something that happens
   rather than something that happened. This is the part to read first if you are
   deciding whether a mechanism applies to you.
4. **How to adopt** — concrete steps.
5. **Depends on / breaks without** — the edges, by mechanism id.
6. **If you change it** — what a substitute must preserve.

If you are skimming, read the tier lines and the "why it exists" sections. The rest
is implementation detail you will need only for the mechanisms you adopt.

# Chapter 1 — Layers, Structure, and Evidence

## A1 — Provenance-based layer separation

**Tier: CORE.** Remove it and there is no principled answer to "where does this file belong," so every other mechanism in the harness loses its addressing scheme and its notion of what may edit what.

### What it is

Top-level directories are separated by **where their content came from**, not by what the content is about. The harness uses four provenance classes:

- **Immutable inputs** — material captured from outside the project (fetched pages, uploaded documents, transcripts, exported data). Byte-preserved. Never edited in place.
- **Derived knowledge** — agent-maintained content in which every claim traces back to an immutable input, with a locator.
- **Generated outputs** — content the agent produced by inference. No captured input backs it; it rests on model capability.
- **Operating contract** — the rules, procedures, forms, and evidence records by which agents work on the repository.

Subject matter is orthogonal to this split. Two documents about the same topic sit in different layers when their provenance differs, and a single layer routinely spans every topic the project touches.

Three boundary rules make the split load-bearing. **Derivation is one-way**: derived content points at inputs, never the reverse. **Corrections never edit an input** — even when the correction is obviously right, even when a user asks for it directly; the fix is recorded in the derived layer, or a corrected original is captured as a new input and the old one is removed only on explicit instruction. There is no per-case exception path; changing the rule itself travels the change-control chain (B1, D3). **Inference-generated output is not filed under derived knowledge** even though both are agent-written, because the two have different warrants and different failure behavior.

Two rules govern how the layers are *read*, and they are as much a part of the mechanism as the writing rules.

**The layering is a reading order.** A question is answered from the derived layer first; the immutable inputs are consulted when the derived layer is insufficient or when verification was explicitly asked for. Without a stated order, every question re-reads the sources, the derived layer's whole reason for existing goes unused, and — worse — nobody notices the derived layer has gone stale, because nothing depends on it.

**A new claim that contradicts a recorded one does not silently replace it.** Both stay, and the conflict is visible. The instinct to overwrite is strong and feels like tidying: the newer information is usually the better information. But the two records disagreeing is itself a finding, and the *reason* the older claim was recorded — a source that said something different — does not stop existing because a newer source disagrees. Claims whose support is thin are marked with a confidence grade rather than stated flat, so that a later reader can tell an uncertain claim from a settled one without re-deriving both. (B3 applies the same shape to *preferences*, where the contradiction is between two things the user said; this rule is about content, and the two are separate carriers of one principle.)

### Why it exists

Without input immutability, an agent "fixes an obvious typo" in a captured source. Months later the derived claim and the source agree perfectly, and nothing in the repository can tell you whether they agree because the derivation was faithful or because the source was edited to match the derivation. The evidentiary value of every input collapses at once, and no check fires, because a clean edit to a text file is indistinguishable from a correct one.

Without separating inference-generated output from source-derived knowledge, an agent's own inference is read back in a later session as an established fact and re-cited. Each round trip raises apparent confidence while the underlying evidence stays at zero. This is invisible in review: the later document is well-sourced, and its source is the earlier document.

Without separating the operating contract from content, rule changes and content edits arrive in the same commits, and the question "which rule was in force when this artifact was produced" has no answer. Regression checking (E3) becomes guesswork, because you cannot identify which contract version a given output was produced under.

### How to adopt

1. Choose one top-level directory per provenance class **your project actually has**, which is usually three to five. A project that captures nothing from outside has no immutable-inputs layer, and standing an empty directory there because a list said four is worse than its absence: content gets filed by the name of the empty box rather than by where it came from, which is the one thing this split exists to stop. Write a one-paragraph charter for each layer you do create, stating what enters it, who may edit it, and which direction derivation runs.
2. Make immutability mechanical, not aspirational: forbid content edits under the inputs directory; allow renames only as path normalization that updates every reference in the same change; make the check that enforces this a build failure (E1, E5).
3. Require every derived document to record the input path and an in-document locator for its claims. A derived document that cannot name its input is either misfiled or unsupported.
4. If your project produces inference-generated content at all, give that layer its own root, and state explicitly in its charter that its contents are not evidence and are never cited as sources by the derived layer. If it does not, do not create the root — an empty one invites the merge back into derived that this rule exists to prevent.
5. Declare the whole set in the structure registry in the same change (A2). Until that happens, the layering exists only in prose.

### Depends on / breaks without

- **A2** — layering by convention enforces nothing. The registry is where the boundary becomes a machine check; without it the split degrades to convention and drifts within weeks, because every misfiling is individually reasonable.
- **A3** — without a gate on adding or moving a layer, the set erodes by accretion and the provenance criterion stops discriminating.
- **E1** — the immutability and attribution checks only run if a procedure wires them before commit.
- **E5** — without byte-level protection of captured original text, immutability is a policy any agent can violate with an ordinary edit, and nothing afterwards distinguishes a corrected input from a faithful one.

### If you change it

CORE. The number of classes and their names are yours; the criterion is not. If you split by topic, by team, or by file type instead of by provenance, you get a taxonomy rather than a contract — nothing follows from membership, and none of A2's checks have anything to enforce.

## A2 — Structure declaration registry

**Tier: CORE.** This is the file that converts A1's boundaries from prose into a machine check; without it every structural rule in the harness is advisory.

### What it is

One declaration file owns the answer to "which paths exist in this repository and what is each one for." Every tracked path must resolve to **exactly one** declaration, or to an explicit exclusion entry. No match is a hard failure. Two equally specific matches is a hard failure. Neither is a warning.

The concrete shape that makes this work:

- **A closed top-level key set.** An unrecognized key is a load error, not ignored data. The registry cannot grow undocumented dimensions.
- **One declaration per path group**, carrying at minimum: a stable identifier, one path selector, a role (content root, support, and so on), and a **disposition** — what a downstream process does with the path, most importantly whether it is shipped in a public distribution. One disposition per declaration is the shape the reference engine implements. If you run two distributions with different rules, do not overload the single field: give each process its own key and say in the registry's own comment which key belongs to which process, because a disposition whose owning process is ambiguous is read by both and honoured by neither.
- **A frozen minimal selector grammar.** The set used here is: exact file; direct children of a directory; recursive subtree; root-level files; single path segment; a named directory at any depth. Anything outside this set is a load error. Extending the grammar is itself a registry change that travels the decision gate — it is not a code change someone makes while fixing a selector.
- **Deterministic specificity.** Exact beats longer literal prefix beats fewer wildcards. An equal-specificity double match is an error, never a coin flip, because a coin flip means attribution silently depends on declaration order.
- **Overrides that must be strictly more specific than, and contained within, their parent declaration.** A violating override is a load error; otherwise an override quietly becomes a second, competing declaration.
- **A non-empty exclusions list** — the explicit untracked axis (build output, dependency directories, tool caches), each with a stated reason. Exclusion is a declared decision, not a gap.
- **A fail-closed loader.** Any parse or schema violation raises, and **nothing is partially loaded**. The loader accepts a deliberately strict subset of its file format: no anchors, aliases, merge keys, duplicate keys, type tags, block scalars, or tabs, and a bounded nesting depth. Every construct outside the subset is an error rather than an interpretation. The loader also validates enum membership, required-key presence, and structural invariants (exactly N categories, path-to-category bijection) in the same pass.
- **Attribution that never reads file contents.** A path's declaration is determined by its path alone. Consequence: a file cannot declare its own exemption. Only the registry can exempt it.

The registry also carries the inventory of manifests (A4) and, when a large structural migration is under way, a topology state with a frozen mapping table — so that "we are mid-move" is a machine-visible fact and downstream processes such as distribution can be blocked for the duration.

Changes to the registry are made by one writer only, through the decision gate (B2, C2).

**State the through-line here, because it recurs through this whole chapter: the absence of a declaration is a failure, never a pass.** An undeclared path fails the build. A hand-written index with no judgment contract is an error, not a silent pass (A4). A document that matches no classification rule is an error, not "unclassified." A missing manifest file is not "nothing to check" — it is a fail-open hole, so the file stays in place with a zero-count header. Adopters who implement this harness as warnings build a version that decays without ever failing.

### Why it exists

**Undeclared-as-warning rots.** A warning that fires on every run stops being read within a week. Attribution coverage then degrades toward zero without a single failing build, and the first time anyone notices is when a downstream process needs to know a path's disposition and finds none. As a hard failure, coverage stays at 100% by construction: you cannot add a path without saying what it is.

**Registration is not the same as intent, and the registry cannot tell the difference.** Measured once, in the single project this harness ran in: a path is declared, every registry check passes, and the disposition is wrong — content that must never ship is assembled into the public bundle, and the only thing that stops it is a second check that never reads the registry. The registry has no complaint, because the declaration is well-formed. This is the one failure mode adopters most reliably underestimate, so build for it explicitly: the disposition belongs on the registry as the single source of truth (assembled into the distribution allowlist, undeclared = fail), **and** an independent invariant layer that never reads the registry must gate distribution — a short hardcoded list of things that must never ship under any disposition, plus a canary that fails when a new top-level private-looking path appears. One source of truth for *what the disposition is*; a second, registry-blind defense for *what must never leave*.

**Wildcard declarations are fail-open.** A root-level "all files at the repository root" selector silently adopts every new root file into whatever disposition the wildcard carries. Someone drops a personal scratch file at the root; the next distribution ships it, with no signal at any point. The repair is to enumerate root-level files and tool-config files exactly, and to accept that adding a root file now requires a registry edit. That friction is the mechanism working.

**Inference hides drift.** If the registry derives directory names from category names by rule (pluralizing, appending a suffix), a directory rename cannot be detected as drift, because the inference regenerates whatever is there. Declare each mapping exactly, even when the pattern is obvious.

**Self-declared exemption is void by construction.** If attribution consulted file contents, any file could add a line claiming to be out of scope, and the check would agree with it. Path-only attribution makes that impossible without touching the registry, which is single-writer and gated.

### How to adopt

1. Create one registry file under your operating-contract layer. Give it a schema version and a closed key set.
2. Enumerate every tracked path group. Run the unregistered-path check; it will fail; fix by declaring, not by widening selectors. Resist the urge to add a catch-all — a catch-all is the failure mode, not the fix.
3. Freeze the selector grammar to the smallest set that covers your declarations. Write the specificity ordering down and make ambiguity an error.
4. Write the loader fail-closed and give it its own check id. Do not reuse a general-purpose parser for the registry: a permissive parser will accept a merge key or a duplicate key and hand you a plausible-looking document that is not what the author wrote.
5. Add the disposition field to every declaration, with undeclared = fail. Then build the second, registry-blind privacy defense separately, and test it by deliberately mis-declaring a private path in a fixture and confirming the second layer still refuses.
6. Wire the registry checks into every procedure that produces or moves files (E1), and register their ids in the check catalogue at error level (E2).
7. Make registry edits owner-only and gated by a decision record (B2, C2).

### Depends on / breaks without

- **A1** supplies the categories the registry declares. Without it the registry is a file list with no semantics.
- **A3** gates the changes; without it declarations accumulate as fast as directories do.
- **A4** consumes the registry's manifest inventory and cross-checks against it in both directions.
- **E1** guarantees the checks actually run before a commit. Without that wiring, the registry is correct only when someone remembers to look.
- **E2** governs the check ids. If the unregistered-path check can be downgraded to a warning, or if its id is not a closed-set member bound to the catalogue, A2's guarantee is advisory — this is the single most common way an adopted registry becomes decorative.
- **B2/C2** keep registry edits serialized; concurrent registry edits from isolated workspaces produce the same class of silent divergence as duplicate numbering.

**The minimal viable set for this whole harness is A1 + A2 + E1.** Layer separation says what the boundaries are, the registry makes them machine-readable, and producer wiring makes the machine actually run. Without all three, everything else in this specification is paperwork that never executes.

### If you change it

CORE. The file format, the selector syntax, the role vocabulary, and the disposition vocabulary are all yours. Four properties are not substitutable: exactly-one-declaration resolution; hard failure on both no-match and ambiguity; a loader that loads nothing on error; and attribution that never reads file contents. Drop any one and the registry becomes a document that describes the repository rather than a mechanism that constrains it.

## A3 — Gate for adding or moving a layer

**Tier: CORE.** Without a gate, the layer set that A1 and A2 depend on erodes by accretion until membership stops implying anything.

### What it is

Adding a top-level layer, moving one, or changing a boundary between two requires **all** of the following, conjunctively:

1. **A distinct provenance or epistemic category** — an artifact kind that genuinely belongs to none of the existing layers. The proposal must name the layer it most resembles and say why the resemblance is insufficient.
2. **A durable, plural artifact family** — content that accumulates and is reused, not a one-off deliverable that happens to need a home this week.
3. **Passage through the evidence chain to explicit human approval** (B1, D3), with the registry declaration and the validator's recognition of the new root landing in the **same change** as the approval, not as a follow-up.

If the character overlaps an existing layer, the answer is a subtree of that layer, not a new root.

**Moving a layer or shifting a boundary is the same gate with different operative requirements.** Condition 1 does not apply — no new category is being minted — so the gate instead demands that meaning, commit history, and inbound links survive the relocation, and that the registry declaration change and the file move land in the **same commit**. No commit may exist in which a path is attributed to its old layer while physically living in the new one. Approval and a decision record are still required, because a boundary shift changes which rules apply to content that already exists.

### Why it exists

A relocation done as file-move-now, registry-later leaves a window in which attribution is simply wrong and every check still passes, because the registry is internally self-consistent — it is faithfully describing a repository that no longer exists. Nothing fails, the window closes when someone gets around to the second commit, and if they never do, the mis-attribution becomes the new normal.

Without the gate, every new output kind gets a top-level directory because that is the path of least resistance in the moment. After a year the top level has a dozen entries whose distinctions are purely historical, "which layer does this belong to" no longer has a determinate answer, and mechanical attribution (A2) degenerates into a catch-all that classifies everything and discriminates nothing.

The mirror failure is just as damaging: with no procedure for adding a layer, an artifact family with genuinely different provenance gets crammed into an existing layer, and that layer's rules — immutability, one-way derivation, citation requirements — are then wrong for it. The rules get quietly violated for that subtree, and once a layer has an unenforced region, its checks stop being trusted anywhere.

### How to adopt

Write the three conditions into your kernel document as a checklist, not as prose. Require the proposal to state the closest existing layer and the specific property that makes it unsuitable. Require the registry declaration, the layer charter, and any validator recognition to be part of the approving change. Record the outcome as a decision (B1) so that a later "why is this a root?" has an answer.

### Depends on / breaks without

- **A1** defines what a layer is; **A2** is what a new layer must be declared into.
- **D3** supplies the approval sequence — prose first, then structured questions, then explicit approval, then execution.
- **B1** carries the evidence and the decision record; without it the gate has no memory and the same argument is re-litigated.

### If you change it

CORE. The wording of the three conditions is yours. Their conjunctive character is not: a gate where any one condition suffices is not a gate, because "this is a durable family" is true of nearly everything anyone proposes.

## A4 — Manifest and generated-view discipline

**Tier: CORE.** An index with no named owner becomes confident misinformation, which is strictly worse than having no index.

### What it is

An index is a **manifest**: it enumerates the items its directory owns, their state, and pointers outward. It is created and retained only when **all three** conditions hold:

1. **A real consumer reads the enumeration** — a procedure step, a machine parse, or a human browsing path. Measured, not assumed.
2. **A named update owner exists.** Owners are typed strings with exactly three kinds: a procedure (`workflow:<name>`), a script (`script:<path>#<anchor>`), or a contract clause (`contract:<id>#<anchor>`). Multiple owners are normal. A validator-only owner is allowed only when the acting updater is additionally named in a layer contract or profile clause — a check that reads a file is not a party that updates it.
3. **Auto-discovery cannot provide the same value.** If a directory listing, a metadata scan, or an on-demand generated view gives the same answer, no manifest is created.

Path is the manifest's identity, so manifests carry no id or version field. Frontmatter declares nature, mode, and owners.

**Modes and markers.** Three modes: *manual*, *generated* (whole file), *mixed*. A generated file carries a top-of-file sentinel naming the generator and forbidding hand edits. A mixed file wraps each generated region in an exact **paired marker**, with four exclusivity rules: (a) inside the markers is generator-exclusive — a hand edit there is a lint error revealed by the regeneration diff; (b) outside the markers is generator-untouchable — a generator that writes there is defective; (c) the markers themselves are hand-owned, and adding, removing, or moving one travels the inventory/design-change procedure; (d) no nesting. Drift is detected by regenerating and diffing. A marker-*like* line that is not the exact form is an error, not something to ignore — near-miss markers are how a generated region silently stops being regenerated. Probe for the token followed by *any* keyword, not by the three correct spellings: a typo in the keyword itself reads as ordinary prose under the narrow probe, which is precisely the case the rule exists to catch. And whatever the checker treats as out of scope — fenced examples, typically — every writer must treat the same way, which in practice means they locate markers through the same scan rather than through their own search. A checker that ignores fenced markers while a generator rewrites them reports a clean document and edits an example.

**Per-carrier judgment contracts.** Each hand-written manifest declares its own currency contract: what counts as an *orphan* (an owned item exists with no row), what counts as a *dead row* (a row exists with no item), which structured counts are compared, and — critically — what the check must **not** flag: series lines that compress bulk items into one row, single pointer rows to another manifest, explicit zero-count sentences, and prose inside a row capsule. A hand-written manifest with no such contract is an **error**, not a silent pass.

**Empty state.** At zero items, the file, its header, and an explicit "0 items" statement all remain. A generator that emits nothing for empty input is defective.

**Registry cross-check.** Existence, mode, and path come from the registry; owners and detail come from the manifest's own frontmatter; a check compares the two in both directions. Neither side restates the other: the registry never enumerates item instances, and manifests never restate structure or paths — they link to the registry instead.

### Why it exists

**Ownerless enumerations decay, and the presence of a named owner predicts decay better than any other property.** An index nobody is obliged to update is still read as current, so it produces confident wrong answers rather than visible gaps. This is why owner wiring must land in the **same commit** that creates the manifest: a repository state in which an ownerless index exists is a state in which decay has already started.

**A missing file is fail-open.** Parsers skip absent files silently, so deleting a manifest does not surface as an error — it makes the check that read it evaporate. Hence the empty-state rule, and hence abolition order: record the loss of a retention condition, amend the inventory, re-wire the consumers, and only then remove the file. Deleting first, while a consumer still reads it, converts an enforced rule into an unenforced one with no signal.

**Hand edits inside generated regions vanish.** The edit survives until the next regeneration and then disappears, leaving no trace — the author believes the fix landed and the reviewer saw it land. Only marker discipline plus a regeneration-diff check makes this detectable.

**A currency check with no per-carrier contract has to guess**, and a guessing check either flags legitimate compressed rows constantly (so it gets ignored) or passes everything (so it is decorative). Making an undeclared carrier an error forces the contract to exist before the check is asked to judge.

**Counterexample worth keeping.** Append-only record categories deliberately get **no** hand-written index in this harness: an on-demand generated view answers the same questions, so the third retention condition fails and no manifest is created. The discipline is as much about not creating manifests as about maintaining them.

### How to adopt

1. List every existing index. For each, test the three conditions honestly. Delete the ones that fail — after re-wiring consumers.
2. Add typed owner strings to frontmatter for the survivors. Where you cannot name an owner, that is the answer: the index should not exist.
3. Declare the surviving set in the registry (A2) as the inventory canon, with mode and disposition, and add the bidirectional cross-check.
4. Implement the generator with exact paired markers and a drift check that regenerates and diffs, defaulting to error (E2).
5. Write a per-carrier judgment contract for each hand-written manifest, including its exclusion list. Make an undeclared carrier fail.
6. Make manifest creation and abolition travel the decision gate, with owner wiring in the same commit.

### Depends on / breaks without

- **A2** — the registry holds the manifest inventory and the disposition; without it there is no canonical answer to which manifests should exist, and the cross-check has nothing to compare against.
- **E1** — the drift and currency checks must be wired into producing procedures.
- **E2** — the drift check must default to error and belong to the closed check set.
- **F1** — without a shared marker grammar and one drift check covering both generated manifests and generated procedure adapters, each generator grows its own marker form, and a near-miss form in one of them stops being regenerated without any check noticing.
- **B1** — recording the loss of a retention condition, and the decision to abolish, uses the evidence chain. Without it, an index is deleted with no record of why, and the next agent re-creates it.

### If you change it

CORE. Marker syntax, owner-string grammar, and the mode names are free. The three retention conditions, the same-commit owner wiring, the four marker exclusivity rules, the fail-closed empty state, and "undeclared carrier = error" are the mechanism.

## B1 — Event chain

**Tier: CORE** (the six-way split and its category names are **DEFAULT**). Without a durable evidence chain, every rule in the repository is a rule someone remembers, and self-improvement becomes indistinguishable from drift.

### What it is

Five kinds of record plus a queue, each an individual immutable-or-status-bearing file, named `{category}-{number}-{slug}-{date}` with the filename equal to the identifier.

- **Run receipt** — what a run read, created, modified; which quality dimensions passed or warned; what the agent could not resolve. **Immutable once issued, and it carries no status field at all** — statelessness is its definition. A receipt whose state can change is no longer a record of what happened. Quality is recorded **per dimension and never collapsed into one score**: a single number is unactionable, because two artifacts failing for opposite reasons land on the same value and the aggregate hides which dimension moved. The pressure to collapse is real — one number sorts and charts — and the cost is that the receipt stops telling you what to fix.
- **Verbatim feedback** — the user's own words, byte-preserved in a protected span (E5). Never translated, summarized, or normalized. Around the protected span sit the agent's classification: scope, feedback type, status, and an optional interpretation note explicitly marked as the agent's.
- **Interpretation / proposal** — the agent's reading of what should change, carrying at least one upstream evidence link (no evidence is an error) and a **success-criteria section frozen before any attempt is made**.
- **Evaluation** — a verdict bound *by reference* to pre-registered criteria: the proposal's frozen section, or a regression fixture identifier. Status is running or concluded; a verdict exists only when concluded.
- **Decision** — the outcome only: what was decided and what it affects. Not the reasoning narrative, which stays upstream and is linked. Rollback and supersession are **status transitions on the original decision**, not deletions and not a separate correction document. Machine fields: affected targets derived from the actual diff and the registry (never declared from intuition), the check identifiers the decision requires, and either a verification-receipt identifier or an explicit not-applicable reason — exactly one of the two, with a validator independently confirming that a cited receipt exists.
- **Deferred queue** — items acknowledged but not acted on now, with status and a low-friction inbox a user can write into freely; an agent converts inbox entries into queue items, backfilling classification, and empties the inbox. Items are never deleted; they move to a done state.

Common metadata across all six: identifier equal to filename stem, date synchronized with the date in the filename, layer and domain tags drawn from controlled vocabularies, the producing procedure, and the form version the document was written against.

### Why it exists

**Criteria frozen before the result exists.** If success criteria are written after the attempt, the evaluator grades against criteria invented in the light of what happened, and every change passes. Nobody experiences this as dishonesty — the post-hoc criteria feel like the right criteria, precisely because the result shaped them. Freezing is the only defense, and it only works if the freeze is in a separate document written earlier.

**Verbatim protection.** An unprotected correction gets paraphrased, in good faith, into the thing the agent already believed. The compression is invisible on review: the summary reads fine, and the specific word the user chose — the one carrying the actual constraint — is gone. Byte preservation is not ceremony; it is the only way to re-read a correction later and discover that it did not mean what the system concluded it meant.

**Receipt separated from state.** A mutable receipt stops being evidence, because you can no longer say what was true at the time. Conversely, if a decision carries its full reasoning inline, superseding it means rewriting the reasoning, and the chain loses the ability to show why the superseded decision looked right when it was made.

**Machine fields derived from the diff.** Impact lists declared from intuition systematically omit the file the author forgot they touched. Deriving affected targets from the actual change and the registry closes the gap that regression selection (E3) depends on.

**A queue for "not now."** Without an explicit deferral state, "not now" is indistinguishable from "no." The same defect gets re-reported, the user has to remember which of their requests were dropped, and the system quietly loses its backlog.

### How to adopt

1. Create one directory per category (six, or fewer — see below) directly under your operating-contract layer, as siblings. Do not nest them under a shared parent; the flat sibling arrangement keeps each category's path a single exact declaration in the registry.
2. Write one blank form per category, and version the forms. Records declare which form version they were written against, so a form change does not retroactively invalidate old records.
3. Make the frozen-criteria section a required body section for proposals, and make an evaluation's criteria reference required and non-editable after the verdict lands.
4. Forbid a status field on the run receipt. This is a schema rule, enforced by the frontmatter check (E4).
5. Make each producing procedure emit its receipt as part of the procedure, not as an afterthought (E1).
6. Give the deferred queue a plain-text inbox with no schema. Friction at capture time is the reason backlogs die.

### Depends on / breaks without

- **B2** — every record is a numbered resource; without single-writer numbering, the chain accumulates duplicate identifiers and its links become ambiguous.
- **E1** — the chain records what happened only if the procedures that act are wired to write records.
- **E4** — a closed frontmatter schema is what keeps the per-category rules (status forbidden here, required there) enforceable.
- **E5** — verbatim protection is what makes the feedback record evidence rather than a paraphrase.
- **B3** — the promotion ladder consumes this chain; with no chain, promotion has no evidence and collapses into whoever argued last.
- **A2** — each category's directory is an exact declaration; inferring directory names from category names hides renames.

### If you change it

The six-way split and the category names are **DEFAULT**. You may merge documents — folding evaluation into decision, or interpretation into a proposal that later carries its own verdict — provided five boundaries survive:

1. The user's words and the agent's reading are separated at the byte level, not by a heading.
2. Success criteria are frozen in a record that exists before the attempt.
3. The verdict against those criteria is distinguishable from the decision to act on it; at minimum, the criteria reference is immutable once the verdict lands.
4. An immutable, stateless run receipt is distinguishable from a mutable state carrier.
5. Deferral is an explicit state, not an absence.

Boundaries 1 and 2 are the two a single merged document cannot preserve, because both depend on one part being written and sealed before another part exists. Everything else in the split is filing convenience. The evidence here comes from one project, and the six-way shape was arrived at by successive splitting rather than designed up front — treat the count as incidental and the five boundaries as the finding.

## B2 — Numbering discipline

**Tier: CORE** (digit width, date syntax, and per-category versus single global sequence are **PARAMETER**). Duplicate identifiers in an evidence chain corrupt the links that every other mechanism reads.

### What it is

The universal core is exactly three things: **a single global writer for numbered resources, a duplicate-issuance recovery procedure, and guaranteed detection timing.**

**Single global writer.** Only the owner session issues new numbers. Delegated and isolated executions — subagents, isolated workspaces, side branches — **never issue**. They return unnumbered drafts; the owner session assigns the identifier on the latest mainline snapshot, after scanning for collisions across active isolated workspaces and branches, not merely against mainline. The one exception is the owner session working in its own isolated workspace, and even then issuance may only happen inside the serialized critical section described in C2.

**Derived next number.** The next identifier is the category's current maximum plus one, computed at issuance time. No counter field is maintained, because a counter drifts from reality the moment an issuance is rolled back or an identifier is recovered by hand. (A queue whose items move between directories is the reasonable exception: there, a counter in the queue's manifest is cheaper than scanning two directories, and the counter is checked against the observed maximum.)

**Immutable identifiers.** Filename stem equals the frontmatter identifier. Once issued, the whole identifier — number, slug, and date — is immutable. A typo in a slug stays. The sole exception is a renumbering forced by duplicate recovery, which records what the document was previously called, when it was renumbered, and why.

**Recovery.** When a duplicate is detected, the **later** issuance is renumbered to the next free number. Precedence is decided by first-add commit time, with ambiguity resolved by reading context. The earlier issuance and all references to it are untouched.

**Provenance-bounded reference rewiring.** This is the part adopters get wrong. The old stem is shared by the legitimate first issuance and the duplicate, so a repository-wide substitution of that stem silently re-points references that correctly pointed at the first issuance. Therefore: candidate references are limited to those added at or after the duplicate's first commit — anything written before that commit necessarily referred to the first issuance. Each candidate is confirmed against history individually. **If even one candidate cannot be distinguished, automatic rewiring stops and the case goes to manual judgment.** Stopping beats mis-pointing, because a stopped migration is visible and a mis-pointed reference is not.

**Detection timing.** A global uniqueness check exists, and its run before commit is guaranteed by producer wiring (E1) — not by anyone remembering. Detection before references spread is what keeps the recovery candidate set down to a commit or two.

**Naming form (parameters).** `{category}-{zero-padded number}-{slug}-{date}`, with the date synchronized to a frontmatter field and a mismatch treated as an error.

### Why it exists

**The collision that isolated validation cannot see.** Two isolated working copies each compute "current maximum plus one" and issue the same number under different slugs. Each copy's validator passes, because neither copy can see the other. Nothing fails until the two are integrated — by which point both documents have been referenced by other documents written in their own workspace, so the merge produces two valid-looking records with one identifier and a set of links that no longer resolve to a unique target. This was measured once, in the one project this harness ran in, but it is structural rather than incidental: any maximum-plus-one scheme evaluated over a partitioned view has it, and no amount of per-workspace validation detects it.

**Mutable identifiers make every reference a dangling risk.** If a slug typo can be fixed, then any reference written before the fix is stale, and there is no way to distinguish "this link is stale because of a rename" from "this link was always wrong." Freezing the identifier costs one ugly slug and buys referential stability forever.

**Counters lie.** A stored counter and the observed maximum diverge on the first abandoned issuance, and the divergence is silent until someone reuses a number.

### How to adopt

1. Pick the naming form and freeze it. Write the anchored regular expression that recognizes it, including the rule that the slug's last token may not itself look like a date (otherwise the date segment is ambiguous).
2. Write the rule that only the owner session issues, and the rule that delegated executions return unnumbered drafts. State them in the delegation instructions, not only in the policy — a subagent reads its prompt, not your contract tree.
3. Implement the uniqueness check and wire it into every procedure that issues (E1). Register it at error level in the check catalogue (E2).
4. Write the recovery procedure down before you need it, including the provenance bound and the stop-on-ambiguity rule. During an incident nobody derives the provenance bound from first principles; they run a global substitution.
5. Add the "renumbered from" field to your record schema so a recovered document explains itself.

### Depends on / breaks without

- **C2** — the serialized issuance critical section is the only safe way an owner working in an isolated workspace can issue; without it, single-writer discipline is defeated by the owner's own isolation.
- **C1** — isolation is what creates the partitioned view in the first place; the two mechanisms are designed together.
- **E1** — detection timing is guaranteed by wiring, not by hope. Without it, duplicates are found after references spread and recovery becomes expensive.
- **B1** — the chain is the thing being numbered; **A2** declares each category's path exactly, so a category directory cannot be renamed silently.

### If you change it

**Parameters.** *Digit width*: four was used here; widen by appending digits rather than re-padding, so previously issued identifiers stay valid. Narrower widths save nothing and force an early migration. *Date syntax*: including a creation date in the identifier makes records self-sorting and makes slug collisions rare, at the cost of one more field that must stay synchronized (mismatch = error). Drop it and you lose chronological readability but remove a synchronization surface. *Per-category versus one global sequence*: per-category keeps numbers small and lets a reader infer the category's volume, but multiplies the number of sequences you must serialize; one global sequence has a single critical section and a single maximum to compute, but numbers grow quickly and the category is no longer readable from the number alone.

**What a substitute must preserve**: exactly one issuing authority at any moment; a recovery procedure that renames the *later* issuance and bounds reference rewiring by provenance; and a detection point that is wired into producing procedures rather than run when someone thinks of it.

A legitimate alternative removes the problem class entirely: content-hash or random identifiers need no writer, no critical section, and no recovery procedure, at the cost of human-readable ordering and of ever being able to say "the next one is 43." If you take that route, take it fully — drop the maximum-plus-one rule rather than keeping both, because a hybrid reintroduces the collision without the benefit.

## B3 — Promotion ladder and preference lifecycle

**Tier: CORE** (the three-level scope split is **DEFAULT**). Without a promotion path, verified knowledge either never becomes binding or becomes binding everywhere the moment it is first noticed.

### What it is

Two ladders, both three-runged, and they are different ladders.

**Promotion ladder — how knowledge becomes enforcement.**
1. **Non-binding technique note** — knowledge for which "violation" is not a meaningful concept. Craft, heuristics, patterns that helped once. Stored, versionless, never checked.
2. **Profile or contract** — a rule whose violation is a failure. Versioned, with an identified scope of application.
3. **Automated check** — the rule enforced by the validator, with an identifier in the closed check catalogue (E2).

**Rung 2 needs a worked-example ledger beside it, and this is the part adopters skip.** A rule about judgement — what counts as clear prose, what counts as an adequate summary — is not transmissible as a rule sentence alone. Two readers apply the same sentence to opposite verdicts and both believe they complied. The fix is a ledger of matched pairs: the rejected form, the accepted form, and one line on what distinguishes them, grown from actual corrections rather than invented. It is consulted **before** writing, not during review, because at review time the artifact already exists and the reviewer is arguing against sunk work. The ledger is append-by-design, so it is exempt from the rebuild counter (B4) and its entries are never pruned for tidiness — a pair that looks obvious now is obvious *because* the ledger taught it.

Where a rule classifies rather than judges — a controlled vocabulary of domains, kinds, statuses — the corresponding discipline is that **the vocabulary is closed and extending it travels the gate**. An agent that may add a term when none fits will always find that none fits, and within months the vocabulary has one value per author. Refusing to classify is the correct outcome and it is the signal that the vocabulary needs a decision, not a new string.

Knowledge climbs a rung when it has been verified repeatedly; the verification itself is the evidence chain's job (proposal → evaluation), and the storage layer is only a shelf.

**Preference lifecycle — how a user's stated wish becomes a rule.** One file per preference, carrying a statement, a scope, evidence links into the event chain, and a status: candidate → active → superseded, plus **conflict** for unresolved contradictions. Five rules govern transitions:

1. An explicit user request for a global rule creates a **candidate**; the agent explains the effects and side effects; the user confirms; only then does it become active.
2. A single artifact-level correction stays a local record. It is **never** promoted to a global rule on its own.
3. The same preference recurring across *different* artifacts may be promoted to candidate.
4. Contradicting feedback **splits by scope** — the older preference is not deleted. If the contradiction cannot be resolved, the preference is held in `conflict` status rather than resolved by whoever spoke most recently.
5. An explicit change leaves the old file `superseded` and linked from the new one.

Scope has three levels: this artifact, a class of artifacts (a profile or document type), and global.

### Why it exists

**Premature globalization is the failure this mechanism exists to prevent, and its shape is specific.** One correction — genuinely right in its context — becomes a rule applied to everything. Some weeks later contradicting feedback arrives from a different context, and it is also right. With only two scope levels, local and global, there is nowhere to put "true for this class, not everywhere," so someone deletes the older rule to make room. The case the older rule was right about is now lost, and nothing records that it was ever right. The system then oscillates: each new correction overwrites the previous one, and neither the user nor the agent can see that the two were never actually in conflict — they were about different classes of artifact. The middle scope tier is the entire fix.

**No middle rung on the promotion ladder** produces the same pathology in the other direction: every observation is either a rule (so trivia gets enforced and the rule set becomes unusable) or a note (so verified findings stay advisory). A rule that never reaches the machine rung is followed exactly as often as it is read, which after a few months is rarely.

**A prose aggregate ledger cannot carry per-item status.** If preferences live as bullet points in one document, superseding a single entry means editing a shared file: status transitions get lost in the edit, evidence links get pruned during cleanups, and the conflict state has nowhere to live. One file per preference is what makes status and evidence survivable.

**Conflict as a status, not as a resolution.** Deleting the loser of a contradiction destroys the evidence that would let a later review notice the two were scoped differently. Holding the contradiction visibly is uncomfortable and correct.

### How to adopt

1. Create a storage location for non-binding technique notes, and state in its charter that nothing there is enforced. This is what stops premature rule-making: there is somewhere else to put a finding.
2. Store preferences as one file each, with statement, scope, evidence links, and status. Make the status enum include an explicit conflict value.
3. Wire the three consumers: the feedback-recording procedure creates candidates; the periodic review procedure is the promotion and supersession gate, running through explicit user approval (D3); the validator enforces the file shape and requires evidence links on anything active.
4. Write the never-globalize-a-single-correction rule into the approval boundaries as a standing prohibition — "do not promote a single feedback event into a global rule" — because it is the rule an agent will most naturally violate while being helpful.
5. When a rule reaches the third rung, register its check in the closed catalogue at error level and bind its regression fixtures (E2, E3).

### Depends on / breaks without

- **B1** — evidence links point into the event chain; without it, promotion has no substantiation and reduces to assertion.
- **D3** — promotion crosses the approval boundary; without the approval sequence the agent promotes its own interpretations.
- **E2** — the top rung only exists if checks are governed; an ungoverned check can be downgraded to a warning and the promotion silently reverses.
- **E3** — when a promoted rule later changes, the fixtures that must re-run are selected by binding, not by memory.

### If you change it

The **three-level scope split is DEFAULT**. A substitute needs at least one tier between "this document" and "everything"; a two-level local/global split forces exactly the oscillation described above, and it forces it reliably, not occasionally. Whether the middle tier is a document type, a profile, a directory, or a task class is yours to choose.

The number and names of the promotion rungs are also flexible. What a substitute must preserve: a place for knowledge that cannot fail, an explicit transition where knowledge becomes binding and versioned, a terminal rung where a machine enforces it, and one status carrier per preference regardless of storage format. The evidence base is one project, but the failure it prevents is reported by anyone who has watched a style guide accumulate contradictory rules.

## B4 — Document rebuild threshold

**Tier: DEFAULT** (the threshold value is **PARAMETER**). The counter-and-threshold form has evidence from one project; a different trigger can work, but something must convert accumulated patching into a rebuild, because nothing in normal review ever does.

### What it is

Every document under the policy carries an integer counter of **semantic partial edits since its last full rebuild**.

**Transitions.** New document: 0. Semantic partial edit (a surgical fix, a section added): +1, and for versioned contracts the version also increments. Mechanical work — sweeps, moves, renames, link rewiring, regeneration, metadata backfill — leaves the counter unchanged. A full rebuild resets it to 0. A rollback leaves it unchanged. When first touching a document that predates the policy, set the counter to the measured value if it can be measured, otherwise saturate it at the threshold and record why.

**The gate.** At the threshold (3 in the source project), the default response to the *next* modification request is a **rebuild proposal**, not another patch. A user may override — "just patch it this once" — which records a one-to-one **exception receipt** (date plus the gist of the instruction). Past the threshold, having fewer receipts than (level − threshold) is a **validator failure**. Receipts never reset the counter; only a rebuild does.

**Exemption.** Documents whose normal behavior is appending rows — logs, manifests, glossaries, inventories, queues, example ledgers, entry documents — declare themselves exempt with a literal boolean field that is mutually exclusive with the counter. A filename pattern is a first-pass classifier; the self-declaration is canonical, because a pattern cannot see that a technique note is append-by-design.

**Excluded by class.** Immutable inputs, event records, and generated artifacts are outside the policy — the first two have no concept of surgical edit, and the third is counted on its canonical source instead.

**The rebuild protocol**, which is where the actual risk lives:

- The **rewriter is an independent agent that has not read the original**, nor any discarded candidate. Its only inputs are the frozen content requirements and the applicable contracts.
- The **orchestrating agent never writes the rebuild**. Its job is to check the candidate for omissions against a **union inventory** extracted independently by two other agents from the original.
- The candidate is staged at a temporary path and compared before it replaces the live document. Each inventory item is marked satisfied, repaired, or deliberately dropped; deliberate drops are stated as such.
- A **baseline content hash** of the live document is recorded when the rebuild starts and re-compared immediately before landing. Mismatch = automatic stop. A real modification that arrived during the rebuild pre-empts it; the stale candidate and its inventories are discarded or re-run against the new snapshot. No arbitrary merge.
- The receipt records baseline and candidate hashes, both inventories, per-item disposition, the independent review verdict, and the re-verification result. Machine-regenerable parts may be recorded as counts and classification rather than in full. In a multi-document campaign, each document's receipt is committed together with that document's change, so an interrupted campaign resumes from committed evidence.

For knowledge documents whose claims must trace to sources, the inventory is extracted **per claim**, each item binding its supporting reference, its attribution class (source claim, agent inference, user statement), and its confidence — because claim/source separation and silent confidence inflation are the first-class losses a rebuild causes, and a reference list that merely still exists does not detect either.

### Why it exists

**Patch-on-patch decay is invisible to per-edit review.** Every individual edit is locally correct, so nothing ever fails. What degrades is the whole: sections drift apart in tone and level of detail, an early paragraph and a late one state the same rule differently, and the reader cannot tell which one is current. The next agent then patches *around* the confusion rather than through it, because resolving it is out of scope for the request. Without a trigger that fires on accumulation rather than on any single edit, this never surfaces.

**A rewriter who read the original inherits it.** Given the old document, an agent restructures rather than rebuilds: it preserves section order, reuses phrasings, and reproduces the very defect that motivated the rebuild — while honestly reporting that it rewrote the document. Withholding the original is the only reliable way to get a blank-slate reconstruction.

**A single inventory extractor misses what the rewriter also misses.** Two independent extractions, unioned, catch the items that one reader's attention skipped; the disagreement between them is itself the signal.

**A rebuild landing on a stale snapshot clobbers a real edit.** Somebody fixes an error in the live document while the rebuild is in flight; the rebuild lands and the fix is gone. The rebuild reports success, and the loss is invisible until the error is re-reported. Baseline-hash re-comparison immediately before landing is what makes the collision loud.

### How to adopt

1. Add the counter, the receipt list, and the exemption boolean to your metadata schema, with mutual exclusion between the exemption and the counter enforced by the schema check (E4).
2. Define which changes are semantic and which are mechanical, explicitly. This boundary is where the counter becomes gameable if left vague.
3. Implement the aggregate warning at the threshold and the hard failure past it. Do not implement only the warning; the warning is the reminder, the failure is the mechanism.
4. Backfill existing documents at the threshold rather than trying to reconstruct history. This turns the counter into a work queue instead of a retroactive accusation, and it is the only affordable option in a repository of any age.
5. Write the rebuild protocol as a procedure, with the role split explicit, and make it impossible to run without the staging step and the baseline comparison.

### Depends on / breaks without

- **D1** — the role split (rewriter, inspector, two inventory extractors) is an orchestration pattern; without a director/worker separation the orchestrating agent will simply write the rebuild itself, which defeats the protocol's core.
- **C1** — the rebuild runs in isolation while the live document remains available for real edits; that is exactly what makes the baseline gate necessary and possible.
- **B1** — the receipt is an event record; without the chain there is nowhere durable to put it.
- **E1**, **E4** — the counter gate is a metadata check that must actually run.

### If you change it

**Threshold (PARAMETER).** Three was chosen because below three the coherence damage is usually still local and a patch is genuinely cheaper, while at three the edits begin interacting with each other. Raising it delays detection until the decay is expensive to reverse and the rebuild is correspondingly larger. Lowering it spends the protocol's real cost — three or four agents per document — on documents that did not need it, and the predictable result is that people stop honoring the gate. Note that the threshold interacts with the exemption rule: if too many documents are append-by-design in practice and the exemption is not used, a low threshold generates constant false triggers.

**Mechanism (DEFAULT).** A substitute may use a different trigger — size growth, edit recency clustering, a periodic review sweep, a reviewer's judgment call — but it must preserve three properties: the trigger fires **automatically**, without depending on anyone noticing decay; the exception path is **machine-checked** rather than informal, so "just this once" cannot become the standing practice; and the content-preservation protocol has an **extractor who is not the rewriter**. Drop the third and rebuilds become an efficient way to lose content while producing a cleaner-looking document.

# Chapter 2 — Parallelism, Sessions, and Orchestration

This chapter covers the mechanisms that let more than one agent session work on the same repository at the same time without corrupting each other's work, and that let a long effort survive being carried across many sessions.

Throughout, the running example is a documentation site repository with path groups `docs/reference/`, `docs/guides/`, and `docs/api/`, plus an operating-contract directory `ops/`. Substitute your own layout.

The example deliberately uses different directory names from the skeleton this specification ships inside, which calls its operating-contract layer something else again. That is not an oversight and it is worth one sentence: if the example and the skeleton agreed, every name in both would read as prescribed. They are placeholders in both places. What the mechanisms constrain is the *relationship* between layers, never their names.

A note on evidence: this harness ran in exactly one project. Where a rule's tier rests on a single observed failure, that is stated inline so you can judge whether the failure mode is reachable in your context.

---

## C1 — Dedicated worktree isolation with continuous integration of consumable units

**Tier: CORE** — parallel sessions sharing one checkout corrupt each other's in-flight history and staging state, and no downstream discipline can repair that after the fact.

### What it is

Every session works in its own git worktree on its own branch, created from the latest mainline snapshot at session start. All writes happen inside that worktree. No session writes into another session's worktree, and no two sessions share a checkout.

Against that isolation sits a counter-pressure: **the moment a semantic unit becomes consumable — a finished document, a completed generated artifact, a closed sub-task — it lands on mainline immediately.** The default landing path is to rebase the working branch onto the current mainline tip and then fast-forward mainline onto it. Selective landing of a subset of commits uses cherry-pick. The two forces are deliberate: isolation prevents interference, immediate landing prevents divergence. A session that holds ten days of work in its worktree is isolated and useless — every other session is building on a mainline that does not contain its work, and the merge surface grows with every hour.

Teardown is gated on a **zero-residue check**, and the check differs by landing path. If everything landed by fast-forward, verify that the working branch is an ancestor of mainline. If any cherry-picks were used, verify patch-equivalence instead — cherry-picked commits have different hashes, so counting commits or comparing tips silently reports "nothing left" while unlanded work is still sitting on the branch. Only after residue is confirmed zero do you remove the worktree and delete the branch.

### Why it exists

Two sessions sharing one checkout interleave on the index and on in-flight history rewriting. A session that rewrites its most recent commit to fold in a correction picks up whatever another session committed into the same checkout in between, silently absorbing unrelated work into a commit that claims to be one semantic unit. The rewrite reports success. The contamination is discovered later, when someone reads the commit and finds changes that have nothing to do with its subject.

Deferred integration converts a small conflict into a large one. Every unlanded consumable unit is a divergence that every other session will eventually have to reconcile, and the reconciliation cost is superlinear in the delay.

A worktree removed while it still holds unlanded commits destroys work with no error. The naive check — "the branch and mainline have the same number of commits" — passes after a cherry-pick landing even when patches are missing, because cherry-picking rewrites hashes. The check that would have caught it is a patch-equivalence comparison, and the reason to specify it explicitly is that the intuitive check is the wrong one.

### How to adopt

1. **Session start**: create the worktree and branch from the mainline tip in one step, using a branch name derived from the work unit (`wt/api-reference-rebuild`). Record nothing about this in a document — it is recoverable by querying the worktree list (see C4).
2. **During the session**: after each consumable semantic unit is committed and validated, rebase onto the current mainline tip and fast-forward mainline. Treat this as part of finishing the unit, not as a separate chore.
3. **Never create merge commits on mainline.** Integration is rebase + fast-forward, or cherry-pick.
4. **Session end**: run the residue check appropriate to the landing path used. If residue is nonzero, land it before cleaning up — cleanup never comes first.
5. **Never rewrite history in a shared checkout.** If a correction must be folded into an existing commit, do it in a worktree that only this session writes to.

### Depends on / breaks without

- **E1 (producer wiring duty)** — without a validator run wired into the procedure that produces each unit, continuous landing propagates unverified commits into the shared line *faster* than batched integration would. Continuous integration amplifies whatever quality gate you have, including its absence.
- **Enables C2** — the serialized issuance critical section is defined in terms of rebase-onto-latest and immediate landing, which only exist if this mechanism does.
- **Enables C3 and D1** — session boundaries and multi-agent orchestration both assume each session has an isolated workspace whose contents are its own.

### If you change it

The linear, merge-free history is a **PARAMETER**. The source project chose it so that "has everything landed?" is answerable by a single ancestry test, and so that a commit reads as one semantic unit rather than as a point on a braid. A project that prefers merge commits can keep the rest of this mechanism, but a substitute must preserve two properties: (a) a cheap, reliable residue check before any workspace is destroyed, and (b) the prohibition on history rewriting in a checkout that more than one session writes to. Moving toward merges costs you the one-line ancestry check and buys you fewer rebase conflicts in long-lived branches — a trade that gets better the longer your branches live, which is itself an argument for landing more often rather than merging.

---

## C2 — The serialized issuance critical section

**Tier: CORE** — any globally sequential resource issued from isolated workspaces will collide, and isolated validation cannot detect the collision.

### What it is

Some resources are numbered from a single global sequence: event records, decision records, migration steps, anything whose identifier is "current maximum + 1". Issuing one of those from an isolated workspace requires an unbroken four-step procedure:

1. **Rebase** the working branch onto the current mainline tip.
2. **Recompute** the category's current maximum, and run a **global collision scan** that covers every active worktree and branch — including their uncommitted working directories.
3. **Commit** the issuance.
4. **Land it immediately** by fast-forward.

Between step 1 and step 4 the session does no other work: no second issuance, no unrelated commits, no long-running delegation. The window between "I computed the maximum" and "my number is on mainline" is the exposure window, and the procedure exists to make it as small as a human-supervised process can make it.

Two adjacent rules complete the mechanism.

**Delegated and isolated executions do not issue at all.** A subagent, a delegated worktree, a branch handed to another agent — none of these issue numbered resources. They return **unnumbered drafts**. The session that owns the sequence assigns the number on the latest mainline snapshot. The sole exception is the owner's own worktree, and only through the four-step procedure above; issuing outside the procedure violates the rule even for the owner.

**On landing failure, restart the whole procedure — never retry the landing alone.** This is the part adopters drop first, so the argument is spelled out below.

### Why it exists

Two isolated working copies each compute "current maximum + 1" and issue the same number. Each copy's validator passes, because neither copy can see the other. The duplicate surfaces only after both land, by which time references to the ambiguous identifier have already been written in both tracks.

A reference-based scan does not see uncommitted files. A scan that walks branch refs reports a clean sequence while another worktree holds an uncommitted file claiming the same number. The scan must walk the working directories of active worktrees, not only their refs.

**The no-partial-retry rule**: steps 2 and 4 are coupled. The maximum computed in step 2 is valid *only for the mainline snapshot that step 1 produced*. A fast-forward failure is proof that mainline moved, which is proof that step 2's input is now stale — and the commit that moved mainline may itself have issued a number in the same category. Retrying only the landing means publishing a number computed against a snapshot already known to be obsolete, while skipping the exact step that would have detected the conflict. What you discard on restart is not the issuance commit; it is the *validity of the number*. Rebase, recompute, and renumber only if the recomputed maximum moved.

The final piece is **duplicate recovery**, because prevention by convention is not prevention by construction:

- The **later** issuance is renumbered; the earlier one and all references to it are immutable. Precedence is decided by first-add commit time.
- The renumbered document records what it was renumbered from and why.
- **Reference rewriting is provenance-bounded and fail-closed.** The old identifier is shared by the legitimate earlier issuance and the duplicate, so a repository-wide substitution silently redirects the earlier one's references to the later document. Candidates for rewriting are therefore limited to references added *after* the duplicate's first commit — references written before that necessarily point at the earlier document. Each candidate is confirmed against history individually. If even one candidate cannot be distinguished, **automatic rewriting stops and the case goes to manual judgment**: stopping is safer than mis-pointing.
- Closure requires re-running the uniqueness check to zero and updating any manifest rows carrying the identifier, in the same commit.

### How to adopt

1. Enumerate which resources in your repository are globally sequential. If none are, you do not need this mechanism — but check for implicit ones (migration numbers, ordered decision logs, fixture ids).
2. Designate a **single writer** for each sequence. The source project treats "one active session at a time" as the operating default and escalates to the user when a parallel situation actually requires an issuance, rather than carrying a writer-designation field in a document (which would need its own single-writer discipline to update — a bootstrap loop).
3. Write the four steps as one atomic procedure in the runbook that produces the resource, with the no-other-work-in-between constraint stated as part of the procedure.
4. Implement the collision scan over **both** refs and active working directories. Compare on the numeric prefix only — the observed collision form is the same number with a different descriptive suffix, which a whole-filename comparison misses.
5. Implement a uniqueness check in the repository validator as the recovery net, and write the duplicate-recovery procedure above before you need it.
6. State explicitly that delegated executions return unnumbered drafts.

### Depends on / breaks without

- **B2 (numbering discipline)** — this mechanism is the parallel-execution half of B2. Without B2's single-global-writer rule and recovery procedure, the critical section has nothing to protect.
- **C1 (worktree isolation)** — steps 1 and 4 are defined in terms of rebase-onto-latest and fast-forward landing.
- **E1 (producer wiring duty)** — the uniqueness check is a recovery net whose value depends entirely on *when* it runs. Detection before references spread is guaranteed by the check being wired into every procedure that produces one of these resources, not by anyone remembering to run it. Without E1 the duplicate is found after propagation, when fail-closed reference rewriting will refuse to proceed and the cleanup becomes manual.
- This is one of several places where the minimal viable set **A1 + A2 + E1** shows through: without wired enforcement, the rest is paperwork that never executes.

### If you change it

The mechanism is CORE, but its *implementation* is not fixed. The source project deliberately chose clause-level discipline over mechanization (no commit hooks, no compare-and-swap on a counter), because the sequence is issued a handful of times per session and a lock adds a failure mode of its own. A project issuing numbers hundreds of times per day should mechanize.

A mechanized substitute must preserve four properties: the maximum is computed against the same snapshot the issuance lands on; the computation sees every isolated workspace, including uncommitted state; the window between computation and landing is minimal; and a failure anywhere in the sequence restarts the whole sequence rather than resuming inside it. A naive lock preserves the first three and quietly breaks the fourth, because a lock that survives a landing failure invites exactly the partial retry this rule forbids.

---

## C3 — Session-per-work-unit boundary and handoff completion criteria

**Tier: CORE** — without a defined unit boundary, sessions run until context degrades and the successor must reconstruct state that was never written down.

### What it is

**One implementation unit equals one session.** When a unit completes — a wave of a multi-part effort, a large standalone work item — that session performs a handoff and ends. The next unit starts in a new session. Continuing into the next unit in the same session happens only on explicit user instruction.

A handoff is complete only when all of the following hold:

1. **Everything produced is committed**, the working tree is clean, and the repository validator reports zero failures.
2. **Everything the successor needs to start without re-investigating is in committed, canonical artifacts** — receipts, records, manifests, queue state. *State that exists only in the conversation is not a handoff basis.* Decisions and observations still living in the conversation are promoted to durable artifacts now, as part of the handoff.
3. **Consumed volatile working files are deleted.** Intermediate inventories, candidate lists, throwaway scripts. Durable evidence is the job of the artifacts in (2); only originals the next unit will inherit are explicitly retained.
4. **A handoff snapshot is committed, and the entry-point pointer is updated in the same commit.** The pointer is the link from wherever a new session actually starts reading to the snapshot. Deferring the pointer to a later commit is forbidden: a snapshot nobody links to is not discovered on the resume path.
5. **Conversation preservation** is mandatory when the user explicitly asks for a handoff and when ending a long session in which reasoning accumulated. It is a separate axis from state handoff, not a substitute for it.

There is a **second path for interrupted handoffs**, and its rules invert. When the unit cannot be completed — context limit, forced stop — you do not follow the completion path. Instead:

- **Freeze by committing everything, including the volatile working files.** The completion path's cleanup rule does not apply. The completion condition for freezing is dirty-and-untracked equals zero.
- **Listing files is not a substitute for committing them.** If something genuinely cannot be committed, produce a patch or artifact that preserves its content and commit its hash and recovery location into a durable carrier. If even that is impossible, **do not declare the handoff complete** — report it as an unfinished stop.
- The interrupted snapshot records: the last known-good commit, an explicit split of what is finished-and-verified versus what must be re-run, known validator state including any outstanding failures, which worktrees and branches must be kept and why, and the first command on resume.
- **Forbidden on this path**: issuing a unit-completion receipt, marking the unit complete, deleting volatile files, removing the worktree. All of those belong to the session that finishes the unit.

### Why it exists

A session that carries three units accumulates enough context that its later judgments degrade, and the degradation is invisible from inside the session. The boundary is a forcing function for context hygiene.

The dominant handoff failure is the successor re-deriving state that the predecessor knew. It happens because the predecessor's knowledge lived in the conversation, and conversations do not transfer. The completion criterion "durable or it does not exist" is the whole defence.

A snapshot written without updating the entry pointer is never found. The successor starts reading at the resume canon, follows a pointer that still names the previous handoff, and works from stale state — while a correct, current snapshot sits in the repository unreferenced.

An interrupted session that follows the completion path deletes its own in-progress work, because the completion path says to clean up volatiles. That is why the interrupted path is written separately rather than as an exception clause: the rules genuinely invert, and an exception clause invites applying the wrong default.

### How to adopt

1. Define what counts as a unit in your project. It should be something a competent session can finish, verify, and land in one sitting.
2. Write the completion checklist as a runbook with the five criteria above, in order, and make the validator run in step 1 an explicit named command.
3. Provide a snapshot form (see C4) with mandatory sections: how a new session starts reading, the closing state of the world, the next unit's scope and any obligations inherited from this unit's lessons, the open and waiting list, and a pointers section.
4. Write the interrupted path as a separate procedure, not as a footnote.
5. Add a closing rule to the effect that no session is handed over on the strength of commit messages alone — commit messages are history, not a starting surface.

### Depends on / breaks without

- **C1** — the unit boundary and the worktree lifecycle are the same lifecycle. Without isolation, "the unit is done" has no clean workspace-teardown meaning.
- **C4** — the handoff artifact's lifetime rules. Without them the snapshot accumulates content that should live elsewhere, and the handoff surface becomes a second, drifting copy of the repository's state.
- **E1** — completion criterion (1) requires a validator that actually runs. Without wired validation, "zero failures" is an assertion.
- **C5 (complement, not prerequisite)** — criterion (1) says everything is committed; C5 is what makes those commits individually readable. A handoff can satisfy the letter of criterion (1) with a single commit containing three units, and the successor inherits a clean tree and unreadable history.
- **B1 (event chain)** — the successor's one-line takeover receipt, and the promotion of conversation-only decisions into durable records, both land in the evidence chain.

### If you change it

CORE, but the granularity is yours. What a substitute must preserve: a defined boundary at which state is forced into durable form; an explicit "conversation state does not transfer" rule; a discovery path from the successor's actual entry point to the handoff artifact, updated atomically with the artifact; and a separate procedure for stopping without finishing, whose defaults invert the finishing procedure's cleanup rules.

---

## C4 — Handoff lifetime split

**Tier: CORE** — without a lifetime rule, handoff surfaces either lose permanent knowledge when they are cleaned up or accumulate stale state that later sessions read as current.

### What it is

The mechanism is a **classification test applied to every piece of state** before it is written anywhere. Run it in this order:

1. **Can a query rebuild it?** Task lists, worktree state, terminal or pane handles, branch state, commit history, anything the version-control system or the coordination runtime can enumerate on demand. → **Never write it down.** A written copy is a second source of truth that drifts from the real one and is trusted anyway.
2. **Does its lifetime end when the successor takes over?** Where the work currently stands, what the successor touches first, what has not been reported yet. → **The volatile handoff snapshot.**
3. **Does it outlive the session but belong to this ongoing unit?** The backlog of decisions awaiting the user, assignment rationale, unfulfilled notification duties, incident history that informs the next assignment. → **A persistent operating ledger**, updated by whoever currently holds the role, never deleted.
4. **Does it outlive the unit entirely?** Standing discipline, deferred work items, recorded judgment failures. → **Its own canonical home**, and the snapshot references it with a **pointer only**.

That produces two compartments with different lifetimes under one handoff surface — say `ops/handoff/` for snapshots and `ops/handoff/ledgers/` for ledgers.

Three operational rules follow.

**The snapshot is deleted once the successor has taken over.** Not archived, deleted. The fact of takeover survives as one line in the successor's closing receipt — what was taken over, when, at which commit. History is git's job. The deletion commit and the removal of the entry pointer are **the same commit**, because a pointer to a deleted document fails link checking — that failure is the enforcement mechanism, and splitting the two commits means shipping a known-broken state.

**The snapshot's pointers section is a mandatory form field**, not a convention. Its absence is what makes people inline permanent knowledge into a volatile document.

**Both compartments live inside the repository.** A path outside the repository is not a persistence mechanism.

Because the volatile compartment's contents legitimately vanish, the structure registry must declare the series *and* an explicit persistence exception for it — otherwise routine deletion trips the undeclared-or-missing-path failure that the registry exists to raise.

Snapshot filenames need only a per-unit counter, a slug, and a date (`handoff-02-api-reference-rebuild-YYYYMMDD.md` is one workable shape). The counter is deliberately **not** a global sequence: consumption deletes earlier entries, so a global counter would develop permanent holes and would drag the whole single-writer issuance discipline (C2) onto a document that does not need it. Ordering canon is the date plus history.

### Why it exists

**An operating ledger placed in a temporary directory disappears wholesale.** A runtime restart, or the system's cleanup of its scratch area, takes the entire handoff record with it. In the source project this happened twice, to the same class of document, before the rule was written. The reasoning that led there is seductive: in-progress state is not repository content, so it seemed to belong outside the repository. The correction is that *durability requirement*, not *content type*, decides the home — and a ledger the next session must read is a durability requirement.

**A snapshot left in place after takeover reads as active work.** The handoff surface is scanned to answer "what is in flight," and a consumed snapshot answers that question wrongly. A later session opens it and works from a state of the world that is two units old. This is one observed incident in one project, but it is the same shape as the stale-pane problem in D1, which suggests the failure class rather than the instance is what generalizes: any surface that is scanned for liveness must be cleaned by whoever consumes it, and the enforcement must be structural rather than a habit.

**Permanent knowledge parked in a volatile document is destroyed by correct behaviour.** The successor consumes and deletes the snapshot exactly as instructed, and a standing rule or an open decision that had no other home goes with it. Volatility becomes loss. Hence: send it to a canonical home first, then point at it.

**Query-recoverable state copied into a document is worse than absent.** It is written once, never refreshed, and read as authoritative. The written worktree list says three worktrees; the actual list says five.

### How to adopt

1. Create the two compartments and give each an owner rule: the snapshot is authored by the outgoing session and deleted by the incoming one; the ledger is updated by whoever currently holds the role.
2. Write the classification test into the handoff form itself, as a "what does not go here" section — the source's ledger opens by naming the things deliberately absent from it and why. That single paragraph does more work than a rule filed elsewhere.
3. Make the pointers section a required field of the snapshot form.
4. Declare both compartments in your structure registry, with the persistence exception scoped to the volatile compartment only.
5. Make the deletion and the pointer removal one commit, and rely on your link check to catch violations.
6. Require the successor's closing receipt to carry the one-line takeover record.

### Depends on / breaks without

- **A2 (structure declaration registry)** — without a registry that declares the series *and* its persistence exception, routine snapshot deletion reads as an undeclared-path or missing-path failure, and the pressure to "fix" it by keeping snapshots forever destroys the mechanism. This is the point where the minimal viable set A1 + A2 + E1 becomes load-bearing for this chapter.
- **A4 (manifest discipline)** — the ledger is a manifest-class document: it needs a named update owner, or it silently goes stale.
- **C3** — this defines the artifacts C3's checklist produces and consumes.
- **B1 (event chain)** — the takeover receipt and the canonical homes for outliving content (the deferred queue, the record layer) are B1's structures. Without B1 there is nowhere to send step 4's content, and everything collapses back into the snapshot.
- **Link checking (E-family enforcement)** — the same-commit deletion rule is enforced by a link check. Without one, dangling pointers accumulate and the rule degrades to a request.

### If you change it

CORE as a lifetime split, but the compartment count is yours. Some projects will want three tiers (per-handover, per-unit, per-role). What a substitute must preserve: (a) the query-recoverable exclusion, stated as a prohibition and not a preference; (b) at least one compartment that is deleted on consumption, so the "what is in flight" surface stays truthful; (c) at least one compartment that is not, living inside the repository; (d) a pointer discipline that keeps unit-outliving content out of the deleted compartment; and (e) structural enforcement of the deletion — a check that fails when a consumed artifact lingers or when a pointer outlives its target.

If you keep consumed snapshots for auditability, you must replace the liveness signal some other way — a status field that the successor is required to flip, checked by the validator. Merely agreeing to "read the date" reproduces the stale-reads-as-active failure.

---

## C5 — Commit discipline

**Tier: DEFAULT** — the failure it prevents is history that cannot be read back as a sequence of decisions; this particular set of habits is one workable way to prevent it, and a project with mechanized equivalents can substitute freely.

### What it is

C1 governs *where* history is written and *how* it lands: which workspace a session owns, when a unit is integrated, what shape the mainline keeps. C5 governs the hygiene of each commit taken on its own — what goes into it, what it is called, and who may publish it. **The boundary is worth stating in the text, because an adopter who has C1 will believe the commit question is already answered.** It is not. An isolated worktree with a correct landing path still produces commits that mix three units, carry no readable subject, and quietly undo work a person did by hand. Integration shape — no merge commits, rebase-and-fast-forward or cherry-pick — stays with C1 and is deliberately not restated here.

Seven rules.

**A meaningful completed operation ends with a commit, and publishing that commit to a remote is a separate authorization from making it.** A session commits freely inside the workspace it owns; it does not push unless it was asked to. An agent that reads "do the work" as including "publish the work" has collapsed two different permissions — the first is about the repository's content, the second about who else sees that content and when.

**The working tree is inspected at the start of a request, not only at the end of a unit.** If uncommitted changes are present and they belong to different work, say so and resolve them before mixing new changes in. C3 requires a clean tree when a unit *closes*; nothing in it requires one when a request *opens*, and that gap is where a predecessor's half-finished change gets absorbed into an unrelated commit and permanently attributed to it.

**Staging is per unit, by explicit path.** Reach for a stage-everything form only after confirming that every changed file belongs to the unit about to be committed. The commit boundary is set by intent; a staging command that enumerates nothing records whatever happened to be in the tree at that moment, which is a boundary set by timing.

**Commit binding follows provenance, not file type.** When an item is consumed or promoted, one item is one commit, and everything that came from that item belongs in it: the promoted document, the removal of its source, and any rule or wiring derived from it. The intuitive grouping is the one to refuse — all the documents in one commit, all the registry edits in a second, all the guidance edits in a third — because it makes history answer "what kind of file changed" when the question anyone asks later is "what did this item cause". This is the general clause. **F4** applies the same binding to a volatile workspace layer's consumption path; that is one instance of this rule, not its source, and an adopter who skips the optional workspace layer still needs the rule.

**A correction to an unpushed commit is folded into that commit, not stacked on top of it.** History is a sequence of semantic units, not a fix trail; a unit followed by three corrections to itself is one unit nobody can read as one. This is the rule that meets C1 head-on, and the two are ordered: **C1 first.** Folding in rewrites history, and C1 permits that only in a checkout no other session writes to. Where the fold-in cannot be done safely, the correction stays a separate commit and the reason is stated. Adopting this rule without C1's constraint reproduces the contamination C1 documents.

**The user's own changes are not reverted unless the user asked for that.** An agent that finds a hand-edited file inconsistent with what it is building has found a question, not a defect.

**Commit messages use a fixed form.** The source project's is a short prefix, a colon, a subject line, and concise bullets beneath. **The prefix set is a PARAMETER** — choose a small closed list naming the kinds of change your repository actually makes, and keep it small enough that picking one is not a decision. An open-ended prefix vocabulary provides no grouping, which is the only thing the prefix was for.

### Why it exists

Every rule here closes a way that history stops being readable, and the loss is discovered only when someone tries to read it — which is always later, and usually under time pressure.

An unrequested push makes a local state visible to everyone who pulls next, and the states most in need of review before they are shared are the ones an agent is most confident about. There is no undo that is not itself an event other people see.

A commit assembled from a dirty tree is attributed wrongly. Its subject describes one unit; its diff contains that unit plus whatever a previous request left behind. Nothing fails. The misattribution is permanent unless someone rewrites history to correct it, which the fold-in rule then constrains and C1 constrains further.

Grouping commits by file kind severs the causal link. Months later the question is "why does this rule exist", and the answer sits in a commit containing only the rule, beside a commit containing only the document it came from, with nothing tying them together but adjacency in time.

Corrections stacked as separate commits turn a unit into a thread. Reading the change means reading four commits and diffing them against each other, and a reviewer who reads only the first reads a version already known to be wrong.

Reverting a person's edit has the worst ratio of cost to visibility in this list: the agent is confident, the change is small, and the person who made the edit finds out by noticing it is gone.

### How to adopt

1. Put these rules in the instruction surface your agents load automatically, not in a policy document they consult after the fact. Commit discipline is applied many times per session; a rule read once per project is not applied at commit time (F6).
2. Fix your prefix set and write it down as a closed list beside the message form.
3. State the push rule as a prohibition with a named exception, not as a preference. "Prefer not to push" is read as "push when it seems useful".
4. Add the working-tree inspection to whatever your agents already do at the start of a request — the same step where routing is decided is the cheapest place to put it.
5. When you write a consumption or promotion procedure, state the commit binding inside that procedure, with the grouping it refuses spelled out. The refused grouping is the part that has to be shown; the correct one sounds obvious once seen and is not chosen on its own.

### Depends on / breaks without

- **C1** — bounds where the fold-in rule may be executed, and owns the integration shape this mechanism does not restate. C5 without C1's shared-checkout prohibition converts a hygiene rule into a contamination path.
- **C3** — supplies the meaning of "unit". A commit boundary set by intent needs the intent defined somewhere, and the work-unit boundary is where it comes from.
- **B1 / B3** — the provenance binding rule is written for the evidence chain's consumption and promotion paths. Without records that carry a provenance, "bind by provenance" has nothing to bind to.
- **F4** — the volatile workspace layer's consumption path is a special application of the binding rule above, not an independent rule.
- **F6** — these rules are read at commit time, so they belong in the always-loaded entry surface rather than in a document opened on demand.

### If you change it

DEFAULT as a set. The rules share one purpose — history that reads back as a sequence of decisions — but each is independently substitutable, and a project with a mechanized equivalent should prefer the mechanization: a remote that refuses unauthorized pushes, a hook that rejects an unprefixed subject. A rule that is enforced and a rule that is written are not the same class of thing, and this mechanism is written rather than enforced only because the source project's volume did not justify the machinery.

What a substitute must preserve: publishing separated from changing, as two authorizations rather than one; a commit boundary set by intent rather than by what happens to be in the tree; a grouping rule that still answers "what caused this" a year later; and the prohibition on undoing a person's work unasked. The message form and the prefix set are PARAMETER throughout.

---

## D1 — Three-role separation and the orchestration invariants

**Tier: CORE** — the invariants below are what make multi-agent parallelism safe rather than merely concurrent; each one closes a failure that isolation alone does not.

This is the largest mechanism in the chapter. It is organized below by invariant, not by procedure order.

### What it is

#### Role separation

Before the three agent roles, one axis that is **not** a role. The human's authority sits outside the role structure entirely, and the contract states the division explicitly rather than leaving it implied: the user selects what enters the repository, sets the goals, gives the feedback, and approves the changes that matter; the agents do the repeated work — processing, structuring, linking, integrating, verifying, and proposing improvements. All three roles below sit underneath that division. None of them is the user's role, and none of them acquires the user's authority by being the most senior agent present. Writing the division down is what makes the routing rules later in this mechanism executable: "return it to the user" is not an instruction in a contract that never says what the user is for.

**The director** assigns work, controls conflicts between parallel units, relays handoffs, and reviews whether the assignment structure is working. It performs **no real work** — no authoring, no editing, no issuing numbered artifacts. A director that starts doing the work stops doing the one job that cannot be parallelized, and burns the judgment capacity that assignment decisions require. It also does not author its own closing receipt; that is delegated, precisely because writing it would be real work.

**Workers** do the work. Each work unit gets a named worker session operating in its own worktree under C1 and C3. **A worker is the orchestrator of its own unit**: sub-delegation, commissioning reviews, splitting the work internally are all the worker's authority, and the director does not enter a unit's internals. The director's scope is *between* units, never *inside* one.

The one carve-out is runtime resource allocation: a worker's default sub-delegation mechanism is an in-session subagent, and creating a new top-level work surface requires the director's prior approval. Each surface carries an interactive process and a runtime task item; unlimited creation floods both, and the director's sweep set grows with them. This is not an exception to non-interference, because allocating shared runtime resources is between-unit coordination.

**The intake desk** receives user requests, does minimal fact-finding, and files assignment requests. It exists so request intake does not queue behind the director's assignment design. It does four things not: **no user interviews** (unresolved points become a question list for the worker who will execute the item), **no repository writes**, **no spawning**, **no design work** (decomposition, ordering, and scope are the director's and the workers'). Its fact-finding is bounded to what an assignment decision needs — does the target path exist, how large is it, is a unit already active on it.

**The desk gets its own top-level work surface rather than a split of the director's**, and the reason is worth stating because the obvious move is to place it the way workers are placed. Two things separate it. Its lifetime is not a work unit's — it outlives every unit it files, so a surface allocated on unit-lifetime terms is the wrong container for it. And split positions on the director's surface are a finite resource that workers need; a desk holding one is a worker slot spent on something that never does the work. Workers get splits; the desk gets a surface.

**Spawn authority belongs to the director alone**, and it is a genuine privilege: creating a work surface takes an arbitrary command string, which makes it effectively arbitrary process execution. It is granted by user action, not by an agent editing its own permissions.

**Worker model tier is pinned at launch**, at the same tier as the director, as an explicit launch argument. Shortcuts that select an agent type without forcing a model produce a silently lower tier. Correcting a wrongly launched worker is done in place, not by respawning — a worker's accumulated context is the expensive part, and respawning discards it. The corollary: the director does not close a live worker's surface, and if one dies it is recovered through session resume.

Read "live" precisely, because the rule inverts on the other side of it. A surface whose worker never came up — the launch failed, the session never attached, nothing has run inside it — holds no accumulated context. Preserving it preserves nothing, while it occupies a slot and shows up in every sweep as a unit that exists. Close it and relaunch. **The discriminant is whether context has accumulated, not how old the surface is.** A surface created a minute ago with a live worker inside it is protected; a surface created a minute ago whose launch failed is not, and the two are the same age. Stated only as "do not close workers", the rule reads as a preservation instinct and produces a sweep set full of empty surfaces that no one is willing to reap.

#### Authority routing: two paths that must not be confused

**User approvals never relay through the director.** The worker raises the interview in its own session, as an ordinary session would, and the user answers there. For contract- or structure-grade matters, the interview follows D3.

Relayed approval breaks four things at once. The question loses the context in which it arose, so the user answers a paraphrase. The answer is recorded as the director's summary of a user decision rather than as the user's own words, which corrupts the evidence chain at exactly the point where verbatim capture matters most. The worker cannot interrogate a second-hand answer. And the user cannot see the state being asked about while answering.

This is why the launch topology matters: worker surfaces are split from the director's surface so both stay on one screen. Direct interview only actually happens when the user can answer in place.

**Agent-to-agent coordination gates are the opposite — the director mediates them.** Who enters the issuance critical section first, who lands on mainline first, who yields a contested path group. That mediation *is* the conflict-control role.

**The discriminant**: does resolving this require the user's *authority* — approval, preference, scope, contract wording — or only *arbitration between agents over a shared exclusive resource*? The first goes directly to the user. The second goes to the director. **When ambiguous, treat it as requiring user authority and return it**, because the asymmetry favours it: mis-routing to the user costs latency, while mis-routing to the director produces a decision made without authority.

Two supports for this: the director **refuses to answer** approval-shaped questions and returns them, and **every assignment spec carries a precedence clause** stating the routing rule explicitly. The second exists because tooling can inject a preamble at worker startup that contradicts the assignment spec; the refusal makes a preamble win immediately visible instead of silently establishing a relay.

One more distinction in the same family: **approving an action is not approving its wording.** An instruction to "reflect this in the guidance" authorizes the act of reflecting, not the clause text that results. Canonical wording is shown to the user before it lands, and the two approvals are recorded separately.

#### Perception: active polling, never trusting push

**The director sweeps rather than waits.** Periodically it queries five things: unread messages; work-item states; the work-surface list, identifying dead and ghost surfaces; unlanded commits per worktree; and a **duplicate scan on every numbered sequence**, covering active worktrees and branches.

Two distinct failure modes drive this.

*A report arrives but is not perceived.* A worker replies to the sender handle of the message it received instead of the coordinator address registered in the dispatch record. The message is delivered. The director's blocking wait does not wake, because it is watching the coordinator address. The report sits unread while both sides believe communication happened. A related variant: a wait filter that omits the status-report class accumulates status replies unread, and the director concludes the workers are idle. Hence: reports always go to the address registered in the dispatch record, and the wait filter must include *every* class a worker can emit.

*Relying on the reporting duty means a missing report is silence.* The duty to report conflicts rests on worker diligence. When it lapses, nothing happens — a numbering collision passed unreported and stayed unnoticed until the user pointed it out. The duplicate scan is the axis that breaks that silence, so it runs **on every sweep, unconditionally**. Putting a condition on it means that when the condition is wrong, detection disappears entirely rather than degrading.

The scan has two known limits, and both must be stated where adopters will read them: it compares **numeric prefixes**, not whole filenames, because the observed collision is the same number with a different suffix; and **reference-based queries do not see uncommitted files**, so the sweep does not replace the issuing session's own scan under C2.

**Timeout is a checkpoint, not a failure.** On timeout the director confirms liveness — surface output, idle wait — and resumes waiting. Heartbeats and surface activity are *liveness* signals, never *completion* signals. A live worker is never interrupted, terminated, or restarted merely because it has not reported completion.

**Completion is a structured signal that prose cannot substitute for.** Surface output or a narrative "I'm done" does not close a work item; the director keeps waiting while the worker believes it has finished. Correspondingly, the completion signal does not verify anything — see the closure section.

**The same principle recurses.** A worker waiting on its own sub-tools — commissioned reviews, subagents, external commands — faces the same non-pushing counterpart. Both extremes fail: blocking in the foreground holds exclusive resources unusable for the duration, and abandoning the check leaves finished work idle. The rule is short periodic checks with other work in between, a check interval fixed at commissioning time, and escalation to the director when the agreed number of checks is exceeded. Note the practical trap: "check back in N minutes" is not executable unless something exists to wake you — decide the waking mechanism when you decide the interval.

#### Exclusivity: one writer per path group

**The director never assigns two active units that write the same path group.** Before assigning, it checks which units are active on the target group and serializes on overlap.

**Worktree isolation does not prevent this harm.** Isolation prevents write interference; it does not prevent judgment invalidation. Any judgment made about content is bound to the snapshot it was made against — in practice, file hashes. Another track landing on mainline invalidates already-issued judgments about those files, even though no write ever conflicted. In the source project, two sessions writing the same path group forced a wholesale baseline re-freeze and invalidated a large set of previously passing judgments. That is a single incident in a single project, but it is worth checking whether your project has any judgment that is bound to content state — review verdicts, approvals, quality gates, cached analysis. If it does, isolation is not enough.

**Unavoidable overlap is priced at assignment time.** If serializing is impossible, the assignment names the re-freeze cost — how many judgments must be re-issued, who decides exemptions — and includes that cost in the unit's scope. The failure to avoid is discovering the cost afterward.

**Repository-wide retroactive units cannot be controlled by path enumeration.** A terminology sweep or notation migration targets "everywhere the condition holds," not a path. Assign such a unit by (a) assuming it overlaps *every* concurrently active unit and (b) fixing the conflict disposition up front. A sound default disposition: take the latest mainline content and re-apply your change on top of it. If two units edited the same place in the same direction the result is identical either way, and taking the latest leaves simpler history.

**Path-group exclusivity and global-resource exclusivity are separate axes, and neither substitutes for the other.** A unit can be alone in its path group and still contend for a globally sequential identifier (C2). Entry into a globally exclusive resource is mediated by the director without exception.

**What that mediation concretely looks like is not specified here, and saying so is the point.** The source project's contract states the requirement — every entry goes through the director — and then states, in the same clause, that the concrete entry-coordination procedure does not yet exist in the contract. Adopt that form and not only that gap: **where a contract requires something it cannot yet tell you how to do, it says so at the place the requirement is stated.** The alternative is a clause that reads as complete, which produces improvised procedures that differ per session while each session believes it is following the procedure. An admitted gap is a work item; an unadmitted one is a silent divergence, and the divergence is discovered as a conflict rather than as a missing paragraph. The same move appears later in this mechanism at the adversarial review gate, where the residue the gate structurally cannot cover is named rather than glossed over.

**Conflicts are reported on discovery, even when self-repaired.** Which two units met on the same global resource is an input to the next assignment decision. Silent self-repair erases that signal and the same collision recurs. Reports are not batched until after the repair.

**A conflict is a signal of a broken rule, not an acceptable operating mode.** On learning of one — by report or by sweep — the director determines whether the disposition followed the recovery procedure (C2) *and* identifies where the procedure leaked, then closes that point. If the root cause is a procedure violation inside a session, tightening assignment will not stop recurrence; the procedure compliance is the thing to fix.

**Conflict history has no separate ledger.** The unit that experienced the conflict records circumstances, root cause, and disposition in its own durable receipt, and the director queries those receipts before assigning against the same resource. A dedicated conflict ledger would duplicate what the receipts already hold — the same reasoning as C4's query-recoverable exclusion.

#### Reporting economy

Reports to the director carry **verifiable values only**: commit hashes, issued identifiers, check counts, worktree state, whether blocked and at what scale, items needing the director's judgment. Not narrative, not the reasoning behind a verdict, not lessons learned, not alternatives considered — those belong in the unit's durable receipt, where they persist. The source project caps status reports at ten lines and blocked-or-conflict reports at twenty. The rationale is that the director's judgment capacity is finite and report volume consumes it before the decisions do.

**Brevity is a rule about volume and never a licence for silence.** The compression rule has an edge that cuts the wrong way if it is left unstated: an agent told to be brief drops the things that are hardest to say briefly, and those are exactly the things the recipient cannot reconstruct from anywhere else. Five signals are therefore never suppressed on length grounds — uncertainty, blockers, significant findings, requests for clarification, and final status. Two of them already appear in the mandatory-content list above; restating them here is not duplication, because the list by itself does not stop a compression instruction from overriding it. The clause is what does that, which is why the clause has to exist in its own right rather than being implied by the list. A report that drops the five reads as a clean result, and a clean result is acted on.

**Conflict reports are the exception and are not compressed** — circumstances, root cause, and disposition go in full, because that content is the input to the next assignment.

#### Instruction ordering

Messages to a worker queue sequentially, and there is generally no cancel or reorder primitive. A worker that consumes instructions in arrival order can act on a superseded instruction — including shutting down when it should not. So: **before acting, a worker performs a non-consuming read of the entire unread queue** and orders its execution from what it finds. Where instructions conflict, the latest wins and the older is not executed first. Correspondingly, a director reversing an instruction sends a *new* message that explicitly voids the previous one.

#### Closure: the adversarial review gate

**Before any unit closes, the worker commissions an adversarial review of its own unit's entire output.** Placement is after the work is complete and before the handoff snapshot is finalized.

- **The worker commissions it, not the director.** Routing it through the director shrinks the worker's orchestration role and adds load to the one session that must stay responsive.
- **Cross-tool by principle** — the reviewer comes from a different tool and model family than the worker, because the objective is perspective independence. Falling back to a same-family high-reasoning subagent is acceptable only on capacity or interface grounds.
- **No exemptions.** The gate applies to every unit and every worker, whatever tool or model family the worker itself belongs to. There is no class of worker whose output is exempt, and no stated ground on which one could be: a worker's own family determines which reviewer is chosen, never whether the gate runs. Leaving this unsaid is how the gate becomes optional in general, because every worker belongs to some family and each family's turn looks like a special case from inside it.
- **Reviewer quality floor**: the reviewer is the top reasoning model of its family at the top reasoning effort. The floor does not drop on the fallback path.
- **Verify that the model and effort were actually applied.** Execution paths exist that accept a model or effort argument, silently discard it, and blend it into the review prompt text — with no failure signal. The verification channel is the invocation record the executing tool stores — not its log output, which can omit the fields entirely and leave "not applied" indistinguishable from "not printed", and never the model's own account of itself. If the tool records no invocation, the run is unverifiable and the gate is not satisfied. See D4.
- **Scope the review to a fixed commit range, not a moving pointer.** A moving pointer advances while the review runs, so the gate never covers the final output. Note the honest structural residue: the gate's own products — repair commits, the review ledger — are by definition outside the range it reviewed.
- **The worker adjudicates.** It holds the context, so it reviews each finding, lands accepted ones as repair commits, and records the rationale for rejections.
- **The review ledger becomes a section of the handoff snapshot** — findings, verdicts, repair commits, rejection rationale. This adds one section; it does not redefine C3's completion criteria.
- **Order**: adversarial review → adjudication and repair → snapshot finalized → closure requested → director verification → shutdown.

**Task completion is not closure approval.** The completion signal marks a work item done without checking whether the gate ran. The director verifies commits, the handoff document, and the review ledger before cleaning anything up, and on verification failure returns the item to failed or reassigns it.

**Surface cleanup is the director's duty, after verification.** An abandoned surface reads as an active unit, polluting the sweep and holding resources. A worker does not close its own surface, since that would amount to approving its own closure. The rule is symmetric: no close before verification, mandatory close after it.

**Director turnover keeps the surface alive.** When the director's own context is exhausted, the session is replaced but the surface is not closed — the coordinator address is bound to the surface, so keeping it means every worker's report path and every dispatch record stays valid and no worker has to rediscover an address. The operating ledger (C4) carries what the successor needs; the turnover snapshot is a separate volatile file. The handover list explicitly names **unfulfilled notification duties** — things the outgoing director owed to workers and has not yet sent. During the gap, workers report and escalate as usual.

### Why it exists

Every invariant above is stated with its failure mode inline, because the failures are what make them non-negotiable. The one general observation: in a multi-agent setup, the dominant failure class is not a wrong action but **an action that returns success without succeeding** — a message that is accepted and never delivered, a model argument that is accepted and never applied, a report that arrives and is never read, a repair that works and is never reported. Every invariant here is a verification path attached to something whose return value cannot be trusted.

### How to adopt

1. Name the three roles and write down, for each, what it does *not* do. The prohibitions carry more weight than the permissions.
2. Put the authority-routing discriminant into every assignment spec as a standing clause, not into a policy document workers may not read.
3. Give the director a written sweep list with a fixed cadence, and mark which sweep items are unconditional.
4. Define the closure sequence and make the completion signal structurally distinct from prose.
5. Write the adversarial review gate with its verification requirement — the model/effort confirmation and the fixed commit range are the two parts that get dropped.
6. Add a path-group registry (even a flat list of groups) and check it at assignment time.
7. Set report content rules and length caps. Direct narrative to durable receipts.

### Depends on / breaks without

- **C1** — without worktree isolation, parallel workers corrupt each other and no assignment discipline helps.
- **C3** — without session boundaries and handoff criteria, "unit" has no closure semantics and the closure gate has nothing to gate.
- **C4** — the director's own state management is C4's classification test applied to the director role.
- **C2 / B2** — the duplicate scan and the issuance-order mediation both presuppose a numbered-resource discipline.
- **D2** — the runtime capability slots. Without them the director cannot dispatch, wait, or enumerate, and the role discipline degrades to sequential operation (see D2's degradation mapping).
- **D3** — supplies the *content* of the approval procedure that D1 routes.
- **E1** — the director's verification step checks validator results; without wired validation there is nothing to verify.

### If you change it

CORE as a whole. Individual **PARAMETER**s within it: the report length caps (ten and twenty lines in the source, tuned to one director's capacity — raise them if your director has spare capacity, lower them if assignment decisions are queuing behind reading), the sweep cadence, and the number of sweep items.

The **role count** is closer to DEFAULT than CORE. A two-role setup (director plus workers, no intake desk) works when request volume is low; the desk exists to keep intake from queuing behind assignment design. What may not be collapsed is the director-versus-worker split — a director that does real work is the failure this whole mechanism prevents.

---

## D2 — Coordination runtime capability slots

**Tier: CORE** as a slot specification — D1's role discipline requires these five capabilities to exist in some form; any particular implementation is OPTIONAL, and the fallbacks below let a project with no coordination runtime at all still adopt D1.

### What it is

The harness does not specify a coordination tool. It specifies five capabilities and the invariant each must guarantee. The adopter supplies an implementation.

A cross-cutting rule first: **do not hardcode a runtime's subcommands or flags into your procedures.** Describe the operation conceptually and resolve the concrete command form from the runtime's own version-matched guide at execution time. Procedures that name flags rot silently when the tool updates, and the rot is discovered as an unexplained failure mid-unit.

A second cross-cutting rule: **runtime coordination state is globally volatile.** Work items, dispatch records, and messages die when the runtime is reinitialized. So assignment specs *point at committed documents* rather than carrying state in the message body, and completion payloads carry commit hashes and paths rather than prose descriptions of what was done. Anything that must survive the runtime lives in the repository (C4).

#### The five slots

**1. Work item registry.**
*Operation*: create a work item with a stable identifier; query its state; transition it.
*Invariant*: **ownership binds to the work-item identifier, not to a surface handle.** Handles rotate on process restart and runtime reinitialization; an ownership model built on handles loses track of who owns what the first time a surface restarts.
*Breaks without it*: the director has no way to answer "what is in flight" except by asking, which is push-dependent and therefore unreliable.

**2. Dispatch record with a fixed report destination.**
*Operation*: record an assignment, binding a work item to a worker, and register the coordinator address to which all reports for that assignment must be sent.
*Invariant*: the report destination is **resolvable independently of any message the worker received.** If a worker can only reply to the sender of an incoming message, reports go to whichever address last spoke, not to the one the director is waiting on.
*Additional requirement*: addresses are re-verified against the live surface listing immediately before sending — an address stored in the environment can diverge from the one the runtime currently manages.
*Breaks without it*: reports are delivered and never perceived (the primary D1 failure).

**3. Blocking wait with a class filter.**
*Operation*: block until an event of a specified set of classes arrives, or until a timeout.
*Invariant*: the filter must be able to name **every** class a worker can emit — completion, escalation, decision gate, and plain status report at minimum. It must also return on timeout with a distinguishable "nothing arrived" result rather than an error.
*Breaks without it*: classes omitted from the filter accumulate unread while the director concludes the workers are idle. And if timeout is indistinguishable from failure, the director kills live workers.
*Usage requirement*: run the wait as a background loop that restarts on return, so the director is always waiting on something.

**4. Completion signal.**
*Operation*: a structured signal, distinct from any prose or terminal output, that transitions the work item and wakes the wait.
*Invariant*: it must be **impossible to satisfy by writing prose.** If narrative output can be mistaken for completion, closure detection becomes a reading-comprehension problem.
*Explicit non-guarantee*: the signal does **not** verify that closure preconditions were met. Keep that separation visible — D1's closure gate depends on the director not treating the signal as approval.

**5. Work-surface listing.**
*Operation*: enumerate active work surfaces with their current addresses and liveness.
*Invariant*: it must distinguish a live surface from a dead one and expose ghosts — surfaces the runtime still lists but nothing occupies.
*Breaks without it*: the director cannot clean up, cannot verify addresses before sending, and its sweep gradually fills with stale entries until it stops reflecting reality.

#### One property that applies to all five

**A success return is not evidence of effect.** In the source project's runtime, a send returned success and the recipient's inbox held nothing; a submission was accepted and never submitted. Every slot needs an independent confirmation path — confirm delivery by observing the effect (the recipient acted, the item transitioned), not by reading the return value. Build this expectation into your procedures rather than discovering it per-incident.

### Why it exists

Without a slot specification, "use a coordination tool" is unimplementable advice, and the mechanisms in D1 read as tool-specific trivia rather than as requirements. Naming the slots separates what the harness needs from what one tool happens to provide, so an adopter can evaluate a candidate runtime against a checklist rather than by trying it and discovering the gap mid-effort.

It also protects the specification from tool churn. The invariants above outlived several versions of the underlying runtime; the flags did not.

### How to adopt

1. Evaluate your candidate runtime against the five slots and their invariants. Record which invariants it fails — those are the failure modes you will experience.
2. Verify runtime availability *before* starting a parallel effort, not on first use. If the coordination layer depends on an optional or experimental feature, confirm it is enabled.
3. For each newly spawned worker, run a **read-only round-trip check** — query runtime state and the worker's inbox from the worker's own surface — before assigning it any work. A worker that fails the round-trip is not given work. This catches the silent-non-delivery class at the cheapest possible moment.
4. Write your procedures against the slot names, resolving concrete commands at execution time.
5. Make every assignment spec point at a committed document rather than carrying state.

### Depends on / breaks without

- **D1** — this exists to serve D1; the slots are derived from D1's invariants, not from a tool's feature list.
- **C3** — assignment specs point at committed handoff documents, which requires those documents to exist and be canonical.
- **C4** — the durability boundary. What the runtime holds is volatile by definition; what must survive goes to the repository.

### If you change it

The slot spec is CORE; **the implementation is OPTIONAL, and its precondition is that a coordination runtime exists at all.** A project without one can still adopt D1's role discipline in a degraded, sequential form. The degradation mapping:

| Slot | With a coordination runtime | Without one |
|---|---|---|
| Work item + state query | Runtime task record with an id and state | A committed assignment queue file, one row per unit, state in a column |
| Dispatch record + fixed report destination | Coordinator address registered in the dispatch record | Reports land as commits under a known path; the "destination" *is* the path, and it does not rotate |
| Blocking wait with class filter | Wait call with a class filter, restarted on return | The next session reads the queue and the report path at startup; the "wait" is the session boundary |
| Completion signal | Structured done message | A committed receipt carrying a specific machine-checkable marker; the validator can assert its presence |
| Work-surface listing | Surface/session enumeration | Worktree listing plus branch listing — which is often *more* reliable, since it cannot go stale |

What the sequential fallback loses: real concurrency, and the ability to arbitrate a live contest between two agents. What it keeps — and this is the point — is the entire role discipline. Assignment still happens before work; the assigning turn still does no work; approvals still go to the user directly rather than through a summarizing intermediary; a unit still passes an adversarial review before it closes; a path group still has one writer at a time (trivially, since there is one worker); and closure is still a verified state rather than an assertion. Every D1 invariant except the concurrency-arbitration ones survives the degradation. An adopter with no coordination runtime should adopt D1 in this form rather than skipping it.

If you substitute a different runtime, the substitute must preserve all five invariants — particularly slot 2's independently-resolvable destination and slot 3's exhaustive class filter, which are the two that fail quietly.

---

## D3 — The approval boundary

**Tier: CORE** — without it, agents apply structural changes and then discuss them, which converts a design conversation into a rollback negotiation.

### What it is

Structural, contract-level, and schema-level changes follow a fixed sequence:

**1. Report observations in prose, as a standalone turn.** Before asking anything structured, state what you found, what you understand the situation to be, and what flow you intend — in ordinary prose, in a turn that contains nothing else. This is a mechanical requirement, not a courtesy: text placed in the same turn as a tool call may never reach the user at all, and an explanation compressed into option descriptions is not read as an explanation. The user then chooses among options without ever having seen the frame that produced them.

**2. Align direction through structured questions.** The source project's rule is at least three questions, each covering a different angle, each offering at least three genuinely selectable options. If a user's answer contains a directive, execute that directive before asking the next question.

**3. Synthesize and re-confirm.** Present the resolution assembled from the answers and get it confirmed before finalizing. Answers to separate questions can combine into something the user did not intend, and the synthesis step is where that surfaces.

**4. Obtain explicit approval.**

**5. Execute only the approved scope.**

Two absolute rules ride on top.

**Nothing is applied during a review or design round.** Anything applied without approval is reverted and resubmitted as an approval request — not kept with an apology.

**Approving an action is not approving its wording.** An instruction to incorporate something authorizes the incorporation; it does not authorize the specific clause text. Canonical wording is shown before it lands, and the two approvals are recorded as distinct events.

The boundary applies to contract- and structure-level matters. It does **not** apply to mechanical execution work, and applying it there is its own failure — an interview for every routine action trains the user to approve without reading, which destroys the signal exactly where it matters.

**Reaching outside the repository is a separate approval axis, and it runs at a right angle to the one above.** Web search, fetching a page, and importing external material are not covered by a general instruction to do the work: the instruction authorizes the work, not the reach. This axis is independent of the contract-versus-mechanical distinction — an external fetch during purely mechanical work still needs its own authorization, and an approved contract change does not carry one along with it.

The scope of that authorization is cut **by purpose, not by session**. Where a procedure's own contract requires trustworthy sources — a composition standard that demands citations, a review that must check claims against originals — external access *for acquiring those sources* is covered by the approval of that task, because the task cannot be performed without it and approving a task while withholding its only means of execution is not a coherent instruction. Every other purpose stays separately approved. The cut matters in the direction that gets abused: an approval to fetch a cited source is not an approval to search for something else in the same session, and the session is not the unit the permission attaches to.

### Why it exists

An agent that presents a review and applies its recommendations in the same round has changed what the conversation is about. The user's objection now has to be executed as a revert of committed state rather than discussed as a design question, and the already-applied change biases the discussion — arguing against something already done is harder than arguing against a proposal, and both parties feel the sunk cost.

Structured questions without a prose preamble produce approvals that are not informed. The user selects from three options for a question whose framing they never saw, and the resulting approval is recorded as if it were a considered decision.

Fewer than three questions, or fewer than three options each, degenerates into the agent presenting its preferred answer with token alternatives. The user rubber-stamps, and the evidence chain records agent judgment as user decision. Far more than three inverts the cost: the interview exceeds the change it governs, and the user starts batch-approving.

Skipping the wording confirmation produces canonical text nobody approved, in a document that binds every future session. The instruction to incorporate was real; the clause that resulted was written by an agent and treated as though the user had endorsed its exact terms.

An agent that reads "do the work" as covering external access has taken a decision the user never delegated: what leaves the repository, what enters it, and from where. Both directions carry a cost the instruction did not price. Outbound, whatever is in the query has left. Inbound, material of unknown provenance lands beside material whose provenance is the entire point of the layering (A1), and the layer boundary was crossed by an action nobody classified as a change.

### How to adopt

1. Write the five-step sequence into your operating contract, with the standalone-prose-turn requirement stated as a mechanical constraint and its reason attached.
2. Define which changes are in scope. Be concrete — the structure registry, layer contracts, procedures, quality standards — and state explicitly that mechanical work is out of scope.
3. Set your question and option counts, with the reasoning.
4. Add the revert-and-resubmit rule for pre-applied changes.
5. Separate the two approval kinds — action and wording — and record both.
6. State external access as its own axis, and write the purpose-scoped carve-out immediately beside it. A carve-out filed in a different document is read as an exception nobody remembers, which turns into either a blanket permission or a blocked procedure depending on which side the reader guesses.

### Depends on / breaks without

- **B1 (event chain)** — approval is worthless without a durable record of what was approved, in the user's own words. Without the evidence chain, the approval exists only in a conversation that does not survive the session (C3's rule that conversation state does not transfer applies here with full force).
- **B3 (promotion ladder and preference lifecycle)** — D3 governs *how* a change is approved; B3 governs *whether* a piece of evidence is even eligible to become a rule. Without B3, a single piece of feedback goes straight to an approval interview and becomes a global rule from one data point.
- **D1** — D1 decides *who* conducts the interview (the executing worker, never the director). D3 decides what the interview is. Adopting D3 without D1's no-relay rule produces a well-structured approval process conducted with the wrong party.

### If you change it

The **three-questions / three-options counts are PARAMETER**. The source used three and three for contract-grade changes only. Raising them buys coverage at the cost of interview fatigue; lowering them below three collapses toward a single recommendation with decoration.

A substitute must preserve three properties. **Multi-angle coverage** — the questions must be capable of changing the answer, not merely confirming a preferred one; a set of questions that all point the same way is one question. **Genuine alternatives** — each option must be one the agent would actually be willing to implement. **A synthesis re-confirmation step** — because separately reasonable answers combine into unreasonable wholes, and that is the failure the individual questions cannot catch.

The prose-first turn and the no-pre-application rule are not parameters. They are the mechanism.

The external-access axis is not a parameter either; what varies is its carve-out. A project whose procedures never require external sources simply has none to write, and should say so rather than leaving the question open — an unanswered carve-out question is answered ad hoc at the moment it first matters, by the agent that wants the answer to be yes.

---

## D4 — Delegation discipline

**Tier: CORE** (the task-class-to-tier map is **DEFAULT**). Delegation is how a session exceeds its own context, and an undisciplined delegation returns something that reads like work and is not.

### What it is

Five rules, each closing a different way a delegated result goes wrong.

**Tier by task class.** Investigation and mechanical verification go to a lighter model; full-rewrite-level generation goes to the strongest one available. The classes are what matter, not the specific names: reading a corpus and reporting what is in it degrades gracefully at a lower tier, while writing a document from a blank page does not.

**State the model and the reasoning effort in both the launch label and the completion report.** Not as a courtesy — as the thing that makes the next rule checkable. **This includes values nobody typed.** A model or an effort level inherited from a session default is stated as explicitly as one passed as an argument, because an omitted field is read as "not applicable" rather than as "inherited", and the inherited value is precisely the one no one chose deliberately for this task. The delegations that silently run at the wrong tier are not the ones with a wrong argument; they are the ones with no argument at all.

**Verify the tier was actually applied, through the executing tool's own record.** Execution paths exist that accept a model or effort argument and discard it with no failure signal. Worse, an intermediary — a forwarding agent, a wrapper whose own contract says "leave effort unset unless explicitly requested" — can strip the argument before the tool ever sees it, so the tool is not lying; it was never told. The verification channel must be a record the *tool* writes: the invocation it stored, not its log output and never the model's own account of itself. A log that simply omits the model is indistinguishable from a run that ignored the model.

**One artifact per agent for non-mechanical work.** An agent asked to write three documents writes the first one well. Mechanical passes — sweeps, format conversions, link rewiring — are exempt, because their quality does not decay with breadth.

**Verify the assembly, not the report.** A delegated component can pass every test it was given and still not fit the thing it belongs to. The receiving session's check is not "is the report true" — it usually is — but "does the assembled whole run".

Those five govern *how* a delegation is executed. Three more govern *whether* it happens at all, *how deep* it may go, and *what is done when it stops early* — the questions that sit before and after the execution, and the ones most often left unwritten.

**When not to delegate is as much a rule as when to.** Withhold the delegation when the task needs tight control of the full context, when it turns on interpreting what the user actually meant, when the judgement is sensitive, or when a decision has to be made now by the session holding the thread. Delegate when an independent perspective is genuinely needed — from an agent not shaped by your own prior reading and assumptions — when the work travels with limited context and the orchestrating session is more valuable orchestrating than executing, when the task is large and its boundary is clear, or when separate areas can be explored in parallel. And when the user did not ask for delegation, ask before delegating if it would change cost, latency, scope, or what the user can see. Those four are the axes on which a delegation stops being a private choice of working method and becomes a decision about the user's situation.

The negative half is the one that gets dropped, and the reason is structural rather than careless: a delegation rule is written by someone thinking about how to delegate well, so it accumulates quality controls for the delegations that happen and says nothing about the ones that should not have. An agent reading only the positive half concludes that delegation is the default and that the rules exist to make it go smoothly.

**Sub-delegation does not recurse by default.** An agent that was itself delegated to does not delegate onward. Where onward delegation would genuinely help, it reports back and says so before proceeding, rather than deciding on behalf of a session that cannot see what it is deciding. Depth is the property being controlled: each level restates the original intent in its own words, so a third-level agent works from a paraphrase of a paraphrase while the report travelling back up reads as first-hand throughout. The exception exists — recursion is allowed where it is clearly efficient — but it is granted by the level above, not taken by the level below.

**An interrupted delegation is resumed before it is restarted.** When a delegated run is cut short by a usage limit, a network failure, or a tool error, the first question is whether the work already done can be picked up, not whether to launch a fresh agent. Restarting is the reflex because it is the easier thing to describe; it also discards accumulated context that cost real time to build and re-does work whose output may already be on disk. This is the same principle D1 applies to a worker that dies mid-unit, one level down: recover the session rather than respawn it.

**Where the tier names live is itself a rule.** The class-to-tier *role* map — which kind of task goes to the strongest model available, which goes to a lighter one — belongs in this specification and in your repository's canonical contract, because the roles do not change when the tool changes. The concrete *names* filling those roles do change with the tool, and they belong in that tool's own entry file, which is the surface guaranteed to be loaded when that tool is the one running. This specification therefore names no models anywhere, and the silence is deliberate rather than an omission: a name written here would be wrong for every adopter and stale for the project it was taken from. **F6** owns the entry-file side of this split — how those files relate to the canon, what may be duplicated into them and what may not, and what happens to them when the canonical rule changes. Do not solve the placement question twice.

Two rules from elsewhere ride along and are restated here because they are read at delegation time: delegated executions never issue numbered resources (B2), and a document rebuild is written by an agent that has not read the original (B4).

### Why it exists

**A delegated component passed 89 of its own tests and the assembly did not start.** The starter configuration shipped in the same kit used one top-level key; the engine shipped beside it expected another. Each half was internally correct and separately verified. The receiving session found it by copying the kit into an empty repository and running the documented first command — the one thing neither test suite did. Accepting the report at face value would have recorded the unit as passing.

**A specified reasoning effort was silently dropped and the review ran a tier below the floor.** The forwarding layer's own contract told it not to pass an effort argument unless the user had explicitly asked for one, so the argument never reached the tool. The log carried no model or effort line at all. The run looked entirely normal — correct scope, real findings — and only a comparison against the tool's stored invocation record showed the field was absent where other runs had it. Had the check been "does the log look right", it would have passed.

**An agent given three documents produces one good one and two that read like summaries of it.** Breadth costs depth in a way that is hard to see in the output and easy to see in a re-read a week later.

### How to adopt

1. Write the task-class map explicitly, in the document your agents actually read at delegation time — not in a policy file they consult after the fact.
2. Require model and effort in the launch label and in the completion report, as a fixed field rather than prose.
3. Find where your tooling records the invocation it actually made, and make *that* the verification channel. If it records nothing, that is a finding: you cannot honour a quality floor you cannot confirm.
4. Cap non-mechanical delegations at one artifact each, and say which of your work is mechanical.
5. Make the receiving check an assembly check. Run the delegated component in the place it will actually live, using the path a newcomer would use.
6. Write the withholding criteria in the same place as the delegating criteria. A list of when to delegate, filed apart from the list of when not to, is read as the whole rule by everyone who finds the first list.
7. Put the tier roles in the canonical contract and the tier names in each tool's entry file, and check that changing one does not require a hand edit to the other (F6).
8. Decide the resumption check before you need it: what a delegated run leaves behind that a successor can pick up, and where it leaves it. A resumption rule with no recoverable artifact behind it is an instruction to check an empty place.

### Depends on / breaks without

- **D1** — the role structure that makes delegation an orchestration act rather than an ad-hoc habit; D1's adversarial-review gate is where the tier-verification rule was first needed.
- **B2** — the no-issuance rule for delegated executions.
- **B4** — the rebuild protocol's role split is this discipline applied to one specific job.
- **E3** — the assembly check is a fixture question: a component test that never assembles is a fixture set with a hole in exactly the shape of the integration.
- **F6** — the tier-name placement rule is the entry-point split applied to delegation: roles in the canon, names in the tool file. Without F6 there is no tool file for the names to live in, and they migrate into the canon, where the next tool change makes them wrong without making them fail.

### If you change it

The tier map is **DEFAULT** — your tiers, your task classes. What a substitute must preserve: a stated class-to-tier rule that exists before the delegation rather than after it; a verification channel written by the tool rather than by the delegate; and a receiving check that exercises the assembled whole. Drop the third and you get a unit that passes on reports.

Add to that list a stated withholding rule. Which tasks fall on the do-not-delegate side is yours to set and will differ by project; having no such side at all is not a variant of this mechanism but its absence, because a discipline that only describes good delegation reads as encouragement to delegate.

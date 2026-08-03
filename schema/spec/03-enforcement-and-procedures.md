# Chapter 3 — Enforcement, Verification, and Procedures

This chapter covers the mechanisms that make the rest of the harness *execute*. Everything in the layer and evidence chapters describes what should be true. Nothing here describes what should be true — these are the mechanisms that make an untrue state detectable at a guaranteed moment, and the procedures that stay discoverable and undrifted over time.

Read E1 first. The harness has a minimal viable set of three mechanisms — provenance-based layer separation (A1), the structure declaration registry (A2), and the producer wiring duty (E1). A1 and A2 tell you what is true about the tree. E1 is the only reason anyone finds out when it stops being true. An adopter who transplants A1 and A2 and skips E1 has built a filing system, not a harness.

Sample-size note that applies to every mechanism below: this harness ran in exactly one project, with agents as the primary committers. Where a claim rests on a single observed failure, the text says so.

---

## E1 — Producer wiring duty

**Tier: CORE.** Every other check in this chapter is inert without it; detection timing is a property of this wiring and of nothing else, so removing it converts the entire enforcement layer into documentation.

### What it is

Every canonical procedure that produces or mutates a governed artifact contains an explicit, numbered step near its end: *run the validator before committing; on failure, do not commit; repair and re-run.* Not "make sure things are valid," not "lint as appropriate" — the literal command, positioned as the last step before the commit step, with the failure branch written out.

The division of labour is deliberate. The check catalogue (E2) owns what checks exist, what they judge, and at what severity. It owns none of the binding force. The binding force comes from the fact that fourteen separate procedure documents each name the validator run as a step, so that an agent following any of those procedures runs it without deciding to. Detection timing is therefore a structural property: a governed artifact cannot reach a commit through a canonical procedure without a validator run in between.

There is a deliberate non-adoption here that adopters will question immediately. Commit hooks and CI enforcement were considered and rejected; enforcement stays at the level of procedure text. The reasoning: the executor is an agent that reads the procedure document before acting, so procedure text *is* the execution path for that executor, and a hook adds a second enforcement surface that can disagree with the first. Be honest about the trade-off — for a repository with human committers, or with any path that bypasses the procedures, procedure-text wiring is strictly weaker than a hook, because a human does not read the procedure before every commit. If your committers are human, add the hook and keep the wiring; the wiring is what makes the hook's failure comprehensible.

Coverage in the source project was fourteen of seventeen procedure specs. The three without the step are an external-collector procedure, a session-archiving procedure, and a reference annex that produces nothing. That is not a clean hundred percent, and the gap is instructive: the procedures that got skipped are the ones whose output felt least governed, which is exactly where an adopter should expect the first drift.

### Why it exists

A repository accumulates a structure registry and sixty checks, and then nobody runs them. Running is a separate act of remembering, and remembering competes with the actual task. The tree drifts for weeks. When someone finally runs the validator it emits several hundred findings at once, which is operationally indistinguishable from noise — nobody can tell which finding is today's mistake and which is six weeks of accumulated sediment. The rational response to a three-hundred-line report is to suppress it or ignore it, and both responses kill the check catalogue permanently. The catalogue's actual output becomes a backlog nobody will ever burn down, and the registry becomes a document that describes a tree that no longer exists.

The second failure is subtler and is why *timing* is in the mechanism's name rather than just *running*. A check that runs at unpredictable moments cannot be depended on by any other mechanism. An identifier-collision scan is only useful if it runs before the number lands in history; a manifest-drift check is only useful if it runs before the stale manifest is read by the next agent. Mechanisms that need a guarantee — the serialized issuance procedure (C2), the manifest discipline (A4) — are building on a check whose execution moment is defined. "Someone runs the validator periodically" does not support anything.

A third, measured failure: chaining the verification command into the commit command lets a failure pass ungated. Writing `validate && commit` looks like a gate and is one; writing them chained in the other order, or chaining verification output into a commit whose message was already composed, is not. Verification, inspection of the verification output, and commit must be three separate acts. This was observed once, in a bulk migration where the chained form let a failing run land.

### How to adopt

- One validator entry point. One command, one exit code, whole-repository scan. Not a suite of scripts a caller must assemble — assembly is a decision, and decisions get skipped.
- Keep the whole-repository run fast. A run measured in seconds is wired everywhere; a run measured in minutes gets moved to "before the PR" and then to "before the release" and then nowhere.
- Edit every procedure document to carry the step, with the failure branch spelled out. Grep your procedure directory for the command name; the count of files carrying it is your actual coverage number, and you should know it.
- Position the step immediately before the commit step, and keep verify / inspect / commit as three separate instructions. Never emit a procedure that chains them.
- Write the ordering as generate-then-validate where a mechanism has a generator: regenerate all derived views first, then validate, so the validator judges the post-generation tree rather than reporting drift the generator was about to fix.
- Add a routing row to your always-loaded entry document pointing at the validator as a producer duty, so an agent working outside any named procedure still finds the obligation.

### Depends on / breaks without

- **A2** — the validator's strongest check asks whether every tracked path is accounted for by a declaration. With no registry, that question has no answer and the validator degrades to a syntax checker.
- **E2** — E1 supplies the moment, E2 supplies the content. E1 without a catalogue runs an unspecified set of checks whose severities drift with the implementation.
- **A4, E3, F1** each state their enforcement as "the check is wired into the validator run." That sentence is a claim about E1. If E1 is absent, all three degrade to conventions.
- **C2** depends on a collision scan executing at a defined moment relative to issuance; that guarantee is E1's.

---

## E2 — Check catalogue governance

**Tier: CORE.** A check set that is not itself governed drifts in severity and identity until the enforcement layer's behaviour is a property of the implementation rather than of any decision, at which point nothing above it can be relied on.

### What it is

Four sub-mechanisms, all cheap, all load-bearing.

**Closed identifier family.** Check ids match a strict kebab-case grammar, and the first token is a *family* drawn from a closed set. In the source project the families were roughly: version-control hygiene, parser and schema, document-class classification, naming, frontmatter discipline, machine-field references, body links, manifests, generated-artifact comparison, registry and paths, and the event chain — plus one family reserved but not implemented, for an adjacent tool whose checks are out of this catalogue's jurisdiction. The reserved-namespace idea is worth copying: it lets you say "these ids belong to someone else" without pretending the checks don't exist. A self-check fixture asserts that every id in the catalogue parses under the grammar and that its family is in the set, with zero self-violations.

**Three-way binding.** A check id appears in exactly three places: as a row in the catalogue table, as a value in a decision record's `required_checks` list, and as a registration constant in the implementation. The catalogue table is canonical; a cross-check lint compares it against the implementation's registration constants *in both directions*. A catalogue row with no implementation and an implemented check with no row are equally errors. Disagreement between the three is itself a lint finding — the binding is not an aspiration, it is a check.

**Severity discipline.** Default severity is error. Contract violations — schema, naming, uniqueness, dangling references, manifest currency, path ownership — are all error by default, and performance is not an accepted reason to relax any of them. Warning is admissible only under four enumerated conditions, and the conditions are written into the contract so that "let's make this a warning" is a claim someone has to justify against a list:

1. **Heuristic checks** — the judgment is a probabilistic signal and structurally can misfire. This is a nudge, not a contract violation.
2. **Acknowledged debt** — a known deficiency explicitly marked in the document's own frontmatter. Silent suppression is forbidden; the marker is what buys the warning.
3. **Agreed two-stage rollout** — warning first, error later, where the promotion moment is bound to a specific decision. Indefinite warning residency is forbidden. A check that has been "warning for now" for six months is a check that will never be an error.
4. **Release-only escalation** — warning in the default mode, error at a release or strict gate.

And a **no-downgrade list**: a named set of checks that may never be reduced to warning, where doing so is itself a contract violation. In the source project it covered manifest currency, both global-uniqueness checks, dangling and ambiguous references, the parser schema gate, the single-classification check, the unregistered-path check, and the decision-receipt check.

**Parser unification.** The frontmatter parser, the registry loader, and the protected-span extractor live in shared modules, and the validator and every generator import the same modules. A second parser is forbidden. The parser is a strict subset parser: it enumerates the shapes it accepts (scalars, flat arrays, top-level block literals) and treats duplicate keys, unrecognized shapes, non-integer version fields, malformed arrays, and empty selector lists as immediate errors. Markdown frontmatter and standalone YAML documents are judged under one schema — a document's carrier format does not change its rules.

Paired with parser unification is a **fail-open prohibition**: a file that violates the schema is reported as an error, and one violation must never cause other checks over the same scan set to pass silently. Where a generator's input is corrupt, that carrier stops; where a document is corrupt, downstream checks on that file are suppressed *and the whole run fails*. Suppression without failure is the shape of a green build over a broken tree.

Two further pieces are needed once the catalogue is real. **Renames need a read-side alias landed in the same commit as the successor id.** The alias is accepted when reading existing records and when matching fixtures, and is never valid for new writes. Alias keys are excluded from the family self-check (they are not check ids) but the alias table itself is cross-checked against the rename mapping. **Retirement timing:** when a check's target is itself being removed by a migration, the removal commit and the successor check's activation must be the same commit — otherwise you get either a jurisdiction gap (a window where nothing guards the invariant) or a double-red (two checks both firing on the same condition, so every run is noisy and both get ignored).

Finally, the catalogue codifies what lint must *not* flag. False-positive exclusions — code spans and fences, protected verbatim regions, deliberately curated rather than exhaustive manifest sections, historical mentions of retired identifiers in plain text, reserved sentinel values — are defined once in a shared module, not re-implemented per check. Per-check exclusion logic is how two checks come to disagree about what a code fence is.

### Why it exists

**Downgrade deletes an invariant, it does not weaken a check.** This is the argument to give an adopter, because "these checks are important" persuades nobody at 6pm. Each no-downgrade check guards an invariant that *other mechanisms assume*:

- A currency check at warning level means the manifest is *sometimes* true. That is worse than having no manifest, because readers trust manifests and stop enumerating for themselves. A manifest known to be unreliable would at least be re-derived; a manifest believed reliable is read.
- A global-uniqueness check at warning level means duplicate ids exist in the tree. Every id-based reference is then potentially ambiguous, and the entire reference-resolution model — the thing that lets a document cite another by id rather than by path — stops being well-defined. You cannot have "mostly unique" ids; the resolution rule is either total or absent.
- An unregistered-path check at warning level means the registry is no longer a closed description of the tree. Every "is this path declared?" question returns to a human, and A2 has quietly become advisory.

**Two parsers over one file produce two truths and no error.** A document has a duplicate key. One parser takes first-wins, the other last-wins. The validator approves the value it read. The generator emits the value *it* read. They are different values. Nothing fails, because from each tool's perspective the file was fine. The silent-skip variant is worse still: a file that one tool considers unparseable is simply absent from that tool's scan set, and absence is quiet — the check reports zero findings over a set that silently excluded the one file that would have failed.

**An ungoverned catalogue drifts into a state where nobody knows what is enforced.** Someone lowers a check to warning for a migration and never raises it. Someone renames a check in the implementation and the decision records that named the old id now reference nothing. Someone adds a check with an id that collides conceptually with an existing family. None of these are visible without the three-way binding, because each of the three places looks internally consistent on its own.

### How to adopt

- Write the catalogue as a table: id, target, criterion, severity, where it is implemented, and whether it is active yet. That last column matters more than it looks — it lets you land a check as specification before it is implemented, which is how you stage enforcement without a jurisdiction gap.
- Fix the family set before you have twenty checks. Retrofitting a closed family set later means renaming, which means aliases, which means the alias machinery above.
- Write the self-check as a test: every id parses, every family is in the set, catalogue and implementation registration constants match in both directions, rename mapping and alias table agree.
- Write the four warning-admission conditions and the no-downgrade list into the contract, as prose an author has to argue against.
- Put the parser in one module and forbid a second. Make the strict-subset acceptance list explicit; anything not listed is an error, not a best-effort parse.
- Route severity changes through the same decision gate as any other contract change. An implementation that changes a severity on its own is drift, and should be caught by the cross-check.

### Depends on / breaks without

- **E1** — a catalogue nobody runs is documentation. This is the sharpest edge in the chapter and it points one way: E2 without E1 has zero effect on the repository.
- **A2** — the unregistered-path check is a registry query; without the registry that check, and the entire path-ownership family, has no referent.
- **E5** — the exclusion-zone definitions the false-positive rules depend on come from the protected-span extractor. Two definitions of "protected" means prose checks and the substitution driver disagree about which bytes are untouchable.
- **B1** — the `required_checks` leg of the three-way binding lives on decision records. Without records that carry machine-readable check lists, the binding has only two legs and the catalogue floats free of any decision.

---

## E3 — Regression fixture gate

**Tier: CORE.** Self-declared regression scope is the failure this prevents, and the failure is not detectable after the fact — a contract change that skipped the fixture that would have caught it looks identical to one that had no fixtures to run.

### What it is

A small named set of existing artifacts is designated as the regression baseline. Each fixture entry records the artifact, the contract it exercises, a role tag (`known-failure-regression-case` for artifacts that encode a bug the system once had, `representative-current-case` for artifacts that encode current good behaviour), a prose list of expected properties, a flag for whether a human has actually reviewed it, and a pointer to the last regression run recorded as an *event id rather than a date* — so the run is traceable to a record with evidence in it rather than to a timestamp anyone could type.

The gate is that **fixture selection is by binding, not by declaration**. The fixture contract carries a `targets:` field holding selectors — layer tags and path globs. A decision record carries `affected_targets` describing what the change touches, and `required_checks` listing what must run. When a decision's `affected_targets` match a fixture contract's `targets:`, that fixture set is automatically pulled into `required_checks`. The author does not choose. The author describes what they are changing, which they know, and the mechanism derives what must be re-verified, which they usually do not.

A second, independent check then enforces the receipt. Every decision record must carry a verification receipt pointer *or* an explicit stated reason why verification does not apply — mutually exclusive, and both absent is an error. The validator checks independently that the declared receipt actually exists. Self-declaration alone cannot pass the gate: you can declare a receipt, but the check goes and looks for it.

Alongside the artifact-level fixtures sit **code-level fixture directories**: one directory of input files per check family (frontmatter shapes, generator behaviour, registry states, document structure, protected-span extraction), each with a runner script. These are ordinary unit tests, but two properties are worth copying. They contain *negative* cases — inputs that must fail, so that a check quietly ceasing to fire is detectable. And their acceptance conditions are written into the check catalogue as a hand-over specification, so that a reimplementation of the validator has a defined bar to clear rather than "passes the existing tests," which a reimplementation trivially satisfies by not implementing the tests.

The evaluation procedure itself is constrained: regenerate the candidate output into a temporary location, diff it against the live artifact, and gate on human approval. Never overwrite immutable inputs during evaluation, and never touch unrelated live artifacts. An evaluation that mutates the thing it evaluates has destroyed its own baseline.

### Why it exists

**The author who changes a contract is precisely the person who cannot enumerate what depends on it.** That is not a failure of diligence — it is the definition of the situation. If they could enumerate the dependents, the change would not be risky. Asked to declare which fixtures to run, they declare the ones they thought about while making the change, which is the set of dependents they already had in mind, which is exactly the set that was never at risk.

**Declaration is also an incentive problem.** Declaring a fixture means running it, and running it means it might fail, and a failure means more work now. Under time pressure the honest declaration is the first thing to shrink, and it shrinks invisibly — a short `required_checks` list is indistinguishable from a change with genuinely narrow scope. Binding removes the choice. The author still describes scope, but scope description is a claim about the change (checkable against the diff) rather than a claim about consequences (checkable against nothing).

**A gate people cannot pass honestly gets routed around.** This is why the receipt check accepts an explicit non-applicability reason. If the only passing state is "I ran the fixtures," then a genuinely inapplicable change either fabricates a run or the check gets disabled. Two exits, mutually exclusive, both recorded, and neither of them silence.

### How to adopt

- Keep the fixture set small — the source used nine artifacts total. A large fixture set is one nobody re-runs. Fixtures are chosen for coverage of *contract surface*, not for coverage of the corpus.
- Include known-failure cases explicitly and label them. The artifact that encodes a bug you already fixed is the one that tells you the fix is still in place.
- Make the selector shape the transplantable part: tagged selectors (`layer:<name>`, `path:<glob>`) in the fixture contract's `targets:`, matched against the change record's `affected_targets`. Both fields must be machine-readable frontmatter, not prose.
- Require the two-exit receipt field on every decision record, mutually exclusive, both-absent an error, and have the validator verify the referenced receipt exists rather than trusting the pointer.
- Add code-level fixture directories per check family, with negative cases, and write their pass conditions into the check catalogue as a reimplementation bar.
- Record the last regression run as a pointer to an evidence record, not as a date.

### Depends on / breaks without

- **B1** — auto-selection needs decision records carrying machine-readable scope fields. With decisions written as prose, there is nothing to match against and selection reverts to declaration.
- **E1** — the receipt check has to actually run at a defined moment; a receipt check run occasionally is a receipt check that catches nothing.
- **E2** — `required_checks` values come from the check catalogue's controlled vocabulary. Free-text check names mean a decision can require a check that does not exist, and nothing notices.
- **F5** — recorded profile versions are what let a contract change identify which existing artifacts were produced under which rules. Without them, "what does this change affect" has no queryable answer even with the binding in place.

---

## E4 — Closed frontmatter schema

**Tier: DEFAULT.** An open schema that warns on unknown fields is workable at a cost, so this specific form is substitutable — but the closedness itself is what makes every downstream mechanism able to trust a field's presence.

### What it is

Each governed document belongs to exactly one document class, determined by an **ordered decision list** evaluated top to bottom — not by self-declaration. The list is fail-closed: no match is an error, and a self-declared class outside the allowed deviation set for that document's series is an error. Exactly one class must result; ambiguity is a finding. The classification boundary is pinned by a set of boundary fixtures, including cases that must resolve to *out of jurisdiction* — the fixtures that prove the classifier correctly declines to classify are as important as the ones that prove it classifies.

For each class, the schema declares a **closed field set**. An unknown key is an error, not a warning. Enum-valued fields are checked against the controlled vocabularies. Reference-valued fields must hold plain identifiers with no link markup mixed in — a separate check then verifies the referenced identifier exists, and for mandatory reference fields, absence is also an error. Version fields must be integers. Selector lists must be non-empty.

Two accommodations are what make the closed set survivable:

**Block literals are pre-extracted byte-verbatim** before the strict loader sees the document. A closed schema and a strict parser would otherwise be in direct conflict with the requirement that user-authored text is byte-immutable — the parser would normalize whitespace inside a quotation. Only top-level block literals are accepted; any other block-scalar shape stays a hard parse error.

**A legacy acceptance flag.** Documents predating a naming or field migration are accepted as legacy — no strict parse, no new-form field enforcement — under a configuration flag, and flipping the flag is the cutover. This is what lets you install a strict schema before the corpus complies with it, rather than requiring a flag day.

Where the specification is silent, the implementation records the interpretation it took and reports the gap rather than inventing a rule. Interpretations accumulating in a module docstring is a smell worth acting on: each one is a place the contract needs a sentence.

### Why it exists

Without closedness, field names drift and every consumer needs a synonym table. Two records carry the same information under two spellings of the same key; a query for one finds half the corpus, and the half it misses is invisible. Nobody notices because both spellings look correct in isolation. The cost lands on every future consumer forever, and it compounds — the third spelling appears because someone grepped for the first two and concluded the field was optional.

Without a fail-closed classifier, a document declares its own class and picks the one whose rules it already satisfies. This is not dishonesty; it is the path of least resistance, and it makes class membership a statement about convenience rather than about the document.

Without the byte-verbatim carve-out, a strict parser silently rewrites quoted human text on the next round-trip — a schema mechanism defeating a protection mechanism, with no error anywhere.

### How to adopt

- Write the class decision list as ordered rules with an explicit no-match error at the bottom.
- Put per-class field tables in data, not in code branches. The tables are what you will edit; branches are what you will forget to edit.
- Reject unknown keys. Detect known-legacy keys by name and report them as *migration needed* rather than as *unknown* — the distinction is the difference between a fixable finding and a mysterious one.
- Pre-extract protected literal blocks before parsing, and accept exactly one block shape.
- Ship a legacy-acceptance flag from day one so the schema can land before the corpus complies.
- Pin the classifier with boundary fixtures, including negative and out-of-jurisdiction cases.

### If you change it

An open schema can work if you accept the synonym-table cost and add a periodic field-census check that surfaces near-duplicate key names. Whatever you substitute must preserve three things: an unknown key produces a *finding*, not silence; a document resolves to exactly one class by a rule rather than by declaration; and per-class field requirements are declared as data that a human can read without reading the validator.

### Depends on / breaks without

- **E2** — the strict parser and the schema are the same module. Split them and the two disagree about what a document is.
- **E5** — the byte-verbatim pre-extraction exists specifically to keep schema validation from touching protected text. Without E5's extractor definition, the carve-out has no boundary.
- **A2** — the classifier's jurisdiction (which paths are classified at all) is a registry declaration. A path outside the classifier's jurisdiction must be *registered as out of jurisdiction*, not merely unmatched — otherwise "not classified" and "not noticed" are the same state.
- **F7** — a closed field set assumes one spelling per field. Where the working language is not English, the axis that holds metadata keys to English is what keeps that assumption true; without it a key arrives in the working language, the closed set rejects it as unknown, and the pressure is to open the set rather than to fix the key.

---

## E5 — Protected spans

**Tier: CORE.** Text a human actually wrote is the one artifact in the repository that cannot be regenerated; a mechanism that corrupts it has destroyed evidence, and every evidence-based mechanism above depends on the verbatim record being verbatim.

### What it is

A structural extractor enumerates every region of the tree that holds user-authored original text, and those regions are byte-immutable across any mechanical operation. Protection is defined by *recognized carriers*, not by heuristics:

- Named frontmatter keys reserved for verbatim content, in any document. Two shapes are recognized — a top-level block literal and a single-line scalar. Any other shape on those keys raises.
- In user-feedback records, the quotation payload. Recognized carriers are the reserved frontmatter key, a verbatim-marked section (a heading whose text contains the marker word, case-insensitively, covering dated and suffixed variants) whose body carries fenced blocks or blockquote runs, or both. A record with no recognizable carrier fails.
- In archived conversation files, every blockquote run and every fenced block, because that is how prompt text is preserved. A conversation file with no blockquote at all, or an unterminated fence, fails.

Every one of those failures is an **abort**, not a skip. An unknown layout means the extractor does not know where the protected bytes are, and proceeding would substitute inside human text. Fail-closed is the entire posture.

Over-protection is deliberate. Agent-authored text that happens to sit inside a quotation or a fence gets protected too, and that is accepted, because a false positive leaves a stale string that a later pass can catch, while a false negative rewrites words a person wrote and cannot be undone from the artifact.

The immutable input layer gets a stronger rule than protection: it is **never processed at all**. The extractor raises if a caller so much as passes it one of those paths. "Protected" means a tool examined it and left it alone; "never processed" means no tool has an opportunity to make a mistake about it. Immutable inputs get the second.

The exclusion-zone definitions the extractor produces are shared: prose checks, link checks, and naming checks all treat protected spans as out of jurisdiction, reading the same definition the substitution driver reads. One definition, several consumers.

### The bulk-substitution procedure (this sub-part is `OPTIONAL`)

**Precondition:** you need to rename identifiers or move paths across the whole repository, including body-text references, on a tree that contains protected spans.

Choreography — **freeze → map → protect → apply → verify → thaw**:

1. **Freeze.** Fix a base commit on a clean tree and bind its hash into the mapping table. The mapping table must be regenerable from that frozen tree alone, and regeneration must be idempotent. Anything issued after the freeze is *not cargo* — count guards must be computed against the mapping table's cargo, never against live totals.
2. **Map.** Produce old→new for every item as a file, bound by a set hash. Split ambiguous adjudications into a separate table and embed *that table's byte hash* into the mapping table — the reproducibility of a judgment is what makes the judgment evidence rather than assertion.
3. **Protect.** Extract every protected span and record byte signatures before touching anything. Unknown layout aborts the campaign. After substitution, compare all signatures.
4. **Apply.** Generate the run's own artifacts outside the tree, execute, then bring the artifacts in as a commit — this avoids a self-hash cycle where the mapping table's hash covers a file the run is about to modify. Dry-run first and assert four numbers: target count, substitution count, zero protected-span violations, zero fixpoint violations. Bulk rewrites pass an explicit human approval gate.
5. **Verify.** Idempotent regeneration from the frozen commit, per-category totals, full reference resolution, zero validator failures. Verify, inspect, and commit as three separate acts.
6. **Thaw.** The state-machine flip is its own commit, followed by every gate plus one live exercise of the success path. Evidence tables and hashes are promoted to a durable receipt before the working files are discarded.

**Pitfall ledger — every item below was measured, not hypothesized:**

- **Tool self-contamination.** The substitution driver rewrites its own inputs — its fixtures, its override tables, its adjudication table. This happened three separate times in one campaign. Explicitly exclude the tool, its fixtures, and its evidence files from the substitution universe, and watch the evidence files with byte-hash gates for the duration.
- **Restore-then-checkout.** Repairing a contaminated file and then running a checkout before committing reverts to the contaminated index copy. Commit the repair immediately, or update the index.
- **Undeclared hash universe.** A set hash must be bound to a declaration of *what it is a set of*. Once the freeze lifts, new issuance inflates the destination-side total and an unfiltered count guard is destroyed.
- **Stem-set blind spot.** If one move contains several items sharing a name stem at different paths, a stem-set guard hides individual losses. Bind cargo per path.
- **Case-only renames.** On a case-insensitive filesystem, existence tests and version-control detection disagree about a rename that changes only capitalization. Use case-exact comparison.
- **Post-move check semantics.** Checks phrased as "compare against the live source side" are valid only before the move. After it, the semantics must be repaired to compare against table-embedded hashes, or a perfectly honest declaration fails and someone disables the check.
- **Document the exclusion list itself.** Code fences, inline spans, frontmatter, historical verbatim, and fixture shadows are excluded from the judgment universe — and the exclusion rules are written down, because an undocumented exclusion is indistinguishable from a bug.

Magnitude, for calibration: roughly four hundred files renamed and about two thousand body substitutions, with zero protected-span violations. One campaign, one project.

### Why it exists

Mechanical substitution over a repository that contains human-authored quotations will, given enough passes, rewrite one of those quotations. The rewrite is small — a renamed identifier inside a sentence someone typed — and it is undetectable afterward, because the corrupted text is well-formed and plausible. The evidence chain's entire value rests on the claim that the verbatim record is what the person said. One silent substitution makes that claim false everywhere, because you cannot tell which records were touched.

The reason unknown layouts abort rather than skip is that skipping is the failure. A skipped file is a file the driver substituted into without knowing where its protected regions were — "I could not find the protected spans, so I proceeded" is precisely backwards, and it is the natural behaviour of code written without this rule.

### How to adopt

- Enumerate carriers explicitly. Do not detect protected text by heuristic; declare the keys, headings, and file classes that carry it.
- Raise on any unrecognized shape. Make the exception type distinct so callers cannot swallow it alongside ordinary parse errors.
- Extract byte signatures before and compare after, on every mechanical pass, not just the risky-feeling ones.
- Refuse to process the immutable input layer at all — enforce this in the extractor, not in the callers.
- Publish exclusion zones from this module so prose and link checks consume the same definition.
- Keep the extractor as a permanent module even after the campaign that motivated it ends. One-shot drivers can be retired to version-control history; the extractor is a standing asset.

### If you change it

The bulk-substitution procedure is `OPTIONAL` because a project that never renames en masse never needs it. If you build a substitute, it must preserve: a frozen base commit bound to the mapping, cargo-based rather than live-based count guards, byte-signature comparison across the operation, an abort on unknown layout, exclusion of the driver's own inputs from the substitution universe, and verify / inspect / commit as three separate acts. Drop any one and the campaign's guarantees become claims.

The byte-immutability core is not substitutable. What can vary is which carriers exist in your corpus.

### Depends on / breaks without

- **A1** — protection presupposes that immutable inputs are a *declared layer*. Without the provenance split there is no principled answer to which text is human-authored, and protection becomes a per-file judgment call.
- **B1** — verbatim user-feedback records are the primary protected carrier. Without the event chain there is much less to protect, and the mechanism's tier would genuinely drop.
- **E2** — the false-positive exclusion rules depend on this extractor's zone definitions; two definitions of protected means prose checks and the substitution driver disagree about which bytes are untouchable.
- **E4** — schema validation must not normalize protected text, which is why block literals are pre-extracted verbatim before parsing.

---

## F1 — Canonical procedure → adapter generation

**Tier: CORE.** Multiple tools each load procedures from their own location, so without generation plus a drift check the tools silently diverge and agents following "the procedure" follow different procedures.

### What it is

One canonical specification per procedure lives in a single directory. A sync script copies each canonical file into every tool's expected location. The script has two modes: `sync` deploys, and `check` diffs every deployed copy against its canon and fails on any difference. The `check` mode runs as a subprocess *inside the validator*, so drift is caught by the same gate as everything else rather than by a separate ritual.

Two details do most of the work.

**Deployment is bounded by a declared exact set**, not by a directory glob. The script lists the procedure names it deploys. Files sitting beside the canon that are not in the set are never deployed — in the source project, a reference annex that documents input-format handling lives next to the procedure specs and is deliberately never shipped as a procedure, because it is reference material, not something an agent should be routed to as a workflow. A glob would ship it, and an agent would eventually invoke it as if it were a procedure.

**Copies are currently byte-identical, and the moment they are not, the difference goes in the generator.** If one tool ever needs different frontmatter, the fix is an explicit per-tool adapter step in the script — never a hand edit to the generated file, because a hand edit is exactly what the drift check reports, and the person doing it will then be tempted to make the drift check quieter.

**F1 and A4 are the same principle applied at two scopes.** One named canonical source → mechanical generation → a drift check wired into the validator run. A4 generates *regions inside* a hand-owned file, delimited by markers, with the surrounding prose hand-maintained. F1 generates whole files. The invariants are identical: the generated thing is never the edit point, the generator is idempotent, and the drift check is not optional. State this symmetry to adopters explicitly — recognizing it means they implement one pattern twice rather than two mechanisms.

### Why it exists

An agent asked to fix a procedure edits the copy its own tool loaded, because that is the file in its context and it looks authoritative — it is a complete, correct-looking procedure document sitting exactly where the tool expects it. The canon stays stale. Then one of two things happens. Either the next sync silently reverts the fix, and the same bug gets fixed again by a later agent, and again; or the sync never runs and the two tool copies diverge, so two agents on the same repository follow materially different procedures while both believe they are following the canon. Neither notices, because from each agent's position there is nothing to compare against.

The scope failure is separate and quieter: a glob-based deployment ships every file next to the canon. Reference material, drafts, and annexes all become invokable procedures. Nothing errors — the file is well-formed — and an agent follows a document that was never meant to be followed.

### How to adopt

- One canonical directory. Generated locations are never edit points, and saying so in a comment at the top of the generator is worth the two lines.
- A generator with `sync` and `check` modes and a non-zero exit on drift, whose failure message names both the drifted file and the canon it should have matched, and tells the reader the two available fixes (regenerate, or move the intended edit into the canon).
- Wire `check` into the validator run. Not into a separate command anyone must remember.
- Declare the deployment set explicitly. If a file beside the canon should not ship, it must be absent from the set, not merely different in some field.
- Treat missing canonical sources as a hard error, not a skip.

### Depends on / breaks without

- **E1** — the drift check is only as good as its execution moment. Unwired, it becomes a command someone runs after noticing the drift they were supposed to be told about.
- **A4** — the same pattern, and the two should share their vocabulary and failure-message style so that "drift" means one thing in the repository.
- **F2** — the routing table is generated from the canonical procedures' frontmatter. If the canon is not the single edit point, the routing table indexes something no tool actually loads.

---

## F2 — Trigger-routed procedures

**Tier: DEFAULT.** Discoverability can be achieved other ways, but a procedure library that is not indexed by *situation* is reinvented rather than found.

### What it is

Each procedure declares in its own frontmatter a list of **trigger condition sentences** — full sentences of the form "when such-and-such situation arises" — plus a status and the tools it binds. A generated routing table is derived from those fields and nothing else: one row per procedure with its link, its triggers, its status, and its bound tools. The table is a generated view with the generator named as its update owner and hand-editing forbidden (A4 applies).

The rule that turns the table from a catalogue into a router is one sentence in the always-loaded entry document: **when a task matches a procedure's triggers, follow that procedure.** Without that sentence the table is a nice list. With it, matching is an obligation.

Trigger sentences are written as situations, not as topics. "When you need to rename identifiers repository-wide while preserving user-authored text byte-for-byte" is a trigger. "Migration" is a topic and is useless, because the agent does not yet know it is doing a migration — it knows it was asked to rename some things.

### Why it exists

Procedures accumulate, and past some count nobody knows what exists. An agent that does not know a procedure exists reinvents it — badly, and differently each time. The specific loss is the worst part: the value of a mature procedure is concentrated in its pitfall ledger, the accumulated list of things that went wrong and the guards that were added. That ledger is precisely what a reinvention does not have, so the reinvention hits the same pitfalls in the same order, and the second traversal costs as much as the first.

Topic-based organization does not fix this, because discovery happens from the wrong end. The agent knows its situation, not the topic the situation belongs to. Indexing by situation puts the index in the same vocabulary as the query.

### How to adopt

- Put triggers in the procedure's own frontmatter as a list of condition sentences. One edit point.
- Generate the routing table; never hand-maintain it. Include status, so retired procedures stay listed and visibly retired rather than silently vanishing.
- Add the binding sentence to the always-loaded entry document, and make it an obligation rather than a suggestion.
- Bind tools in the frontmatter too — an agent that finds the procedure should find its scripts in the same row.
- Write triggers from the position of someone who does not yet know what they are doing.

### If you change it

Honest scale note: the source project had six routed procedures. At that scale a generated routing table is barely necessary; the mechanism's value is asserted for growth, not measured under load. If you have fewer than a handful of procedures, a hand-written list is fine.

Substitutes — a search-indexed procedure library, or tool-native routing where the tool itself matches situations to procedure descriptions — must preserve three properties: triggers live with the procedure so there is one edit point; the routing view is generated rather than maintained; and there exists a binding instruction that matching a trigger obliges following the procedure, not merely reading it.

### Depends on / breaks without

- **F1** — triggers live in the canonical procedure specs. If the canon is not the single edit point, the routing table routes to documents nobody loads.
- **A4** — the routing table is a generated view and needs the marker-and-drift discipline, or it goes stale in the usual way: someone adds a row by hand, the generator overwrites it, and the row is lost with no error.

---

## F3 — Onboarding discipline and the doc-gap loop

**Tier: DEFAULT.** The specific three-document split is one workable arrangement, but the underlying rule — entry documents describe durable mechanisms, and a discovery failure is evidence rather than an inconvenience — is what keeps them from rotting.

### What it is

**Three entry documents with strictly separated jobs.**

- A *principles guide* — the first thing a newcomer reads. Core operating model, quick start, a few representative scenarios. Principle level only.
- An *operating map* — the always-loaded contract document, carrying the situation → contract routing table. Its rows say "in this situation, consult this canon first, then that." Rule bodies are never duplicated into it; it organizes pointers by situation.
- A *capability manifest* — a complete discovery map of everything the repository can do, with the promise that every capability and every directory role is reachable from it **within two hops, by link rather than by duplication**.

**A boundary clause is what keeps three documents from becoming three stale documents.** Each declares what it does *not* contain. The capability manifest enumerates capabilities and usage paths only and never restates structure — structure is the registry's job, the operating map's job is the operating model, principles are the guide's job. Overlap between entry documents is the mechanism by which they drift, because an overlapping fact gets updated in one place.

**The same exclusivity runs one level down, at every directory.** The clause above governs the three top-level entry documents. Below them, a directory typically holds two files of its own: a guide and a manifest, and they are defined *against each other* rather than each on its own terms. The guide is the guide to that directory — what it is for, how to write into it — and nothing else. The manifest enumerates the items the directory owns, their state, and pointers outward, on the precondition that an update owner is named (A4 owns that side and is not restated here). Defined separately, each drifts toward the other: the guide accumulates a partial item list that is current on the day it is written and wrong a month later, and the manifest accumulates explanation until a reader cannot tell which of the two is authoritative about what the directory contains. The rule that prevents both is one sentence in each file naming what the other holds.

**No changelogs.** Entry documents stay at the level of durable mechanisms. Localized fixes, one-off formatting techniques, and migration history are explicitly excluded — those belong in the evidence chain and in the procedures. Entry documents are updated when a core mechanism changes, not when something is fixed.

**A named update owner** — and here the source does something worth copying: the capability manifest's owner is a *contract clause*, not a person or a script. Its owner field points at the doc-gap duty itself. The document is maintained by the rule that anyone who discovers it incomplete must repair it. (Its generated section has the generator as a second owner; the file is mixed-mode.)

**The doc-gap loop.** During ordinary work, if you or the user need a fact that *should* have been discoverable from an entry document and was not — a directory role, a capability, a usage path — that is a gap, and three things happen, not one:

1. Apply the obvious local repair immediately. Add the missing role or entry point.
2. Record the gap in the evidence chain — verbatim if the user stated it, as an observation otherwise.
3. For structural or contract-level gaps, open a proposal and route it through the review cycle. Apply contract changes only on approval.

### Why it exists

**Why not just fix it and move on** is the question every adopter will ask, and the answer has two parts.

The local repair fixes the symptom and destroys the evidence. Recurrence is the only signal that distinguishes "one reader did not look carefully" from "this entry document has the wrong shape," and the promotion ladder needs a recurrence count before it can justify a rule. Fix-and-move-on means the same gap is rediscovered by every subsequent reader forever, each of whom also fixes it locally, each of whom also leaves no trace — a repository can absorb the same discovery a dozen times and have nothing to show for it.

Second: the repair that feels obvious in the moment is almost always *one more row in a table*. A gap that recurs three times usually indicates the table is the wrong shape — the reader is looking up by a dimension the table is not organized around. Without records you cannot see that, so you keep adding rows, and the table grows past the point of usefulness while each individual addition looked correct.

The design value is that the loop **adds no new machinery**. It reuses the existing evidence chain and the existing promotion ladder. No new store, no new workflow, no new discipline to remember — which is exactly why it survives, because a separate doc-quality process would be the first thing dropped.

### How to adopt

- Split entry documents by job and write the boundary clause into each. Every entry document should contain a sentence naming what it does not cover and where that lives.
- Apply the same pair rule per directory: a guide that is about that directory only, a manifest that enumerates and points, and one sentence in each naming the other's job.
- State the reachability promise as a number (two hops) so "is the manifest complete?" is a checkable question.
- Ban changelog content from entry documents in writing, and say where that content goes instead — a ban without a destination just relocates the pressure.
- Name an update owner for each entry document. A contract clause is a legitimate owner; "the team" is not.
- Write the three-part doc-gap response into the always-loaded document, with the *record* step non-optional and explicitly not satisfied by the repair.
- Preserve the approval gate: the loop does not authorize silent restructuring of entry documents.

### If you change it

Substitutes must preserve: entry documents that do not overlap, a completeness promise that is checkable, an explicit rule against accumulating incident history in them, and a discovery failure that produces a durable record and not merely a fix. The number of documents and the hop count are yours to set.

### Depends on / breaks without

- **B1** — the record step writes into the event chain. Without it, "record the gap" has no destination and the loop collapses back to fix-and-move-on.
- **B3** — the promotion ladder is what turns three recorded gaps into a structural change. Recording without a promotion path produces an archive nobody reads.
- **A4** — the manifest is mixed-mode, with a generated section. Same marker-and-drift discipline.
- **D3** — structural repairs to entry documents go through the approval sequence like any other contract change.

---

## F4 — Volatile workspace layer

**Tier: OPTIONAL.** Precondition: work units that span many sessions and mix unsettled design questions with executable tasks. The harness is complete without it — the evidence chain alone performs the full workflow — and this is a management optimization for a specific shape of work.

That subsidiarity statement is itself worth transplanting. Declaring a layer optional in its own contract, and naming what the system does without it, is what stops an optional layer from being treated as mandatory by the next reader.

### What it is

A volatile workspace ("camp," in the source) per large work unit, holding six elements: a manifest with the goal and a resume procedure; a *departure* ledger; one file per open question; one file per settled decision, carrying the grounds verbatim; one file per work item; and a drafts area.

**State canon is file location plus frontmatter — never duplicated into the manifest.** Only items that *leave* the workspace get ledger rows, recording existence, final state, and destination. Resident items are tracked by the directory itself. This single rule is what keeps the ledger from becoming a second, diverging copy of the workspace's state.

**Question→decision conversion.** When a question is answered, its file *converts* into the next decision number and moves; an origin pointer preserves the question's identity. No copy stays behind in the questions directory. Question and decision numbers advance independently.

**Local ids are structurally separate from the global event sequence.** Workspace item ids are short, workspace-local, and issued by the owning session only — derived as max-plus-one across resident files and the ledger, with no separate counter, valid only under the single-owner assumption. Because the workspace is deleted at close, its ids must never become permanent references. On promotion, a workspace decision is *regenerated* as a real event with a globally issued number; it is not renamed into one.

**Ownership.** The workspace manifest declares an owner session key. Other sessions treat an active workspace as read-only — reference freely, modify never — and escalate to the user when their own work overlaps its scope. A successor session performs the resume procedure and then carries the ownership update in its first write commit to that workspace; that commit *is* the handover declaration, and nothing may be modified before it.

**Two mid-life optimizations**, both under one principle — a departing file does not stay behind, its management is transferred:

- *Consume*: an item needing no separate work, needed by other sessions, and actionable now is converted mid-flight and handed up to the permanent layer. Completion means the rule is in force — including judging whether the always-loaded entry documents need wiring, and doing it.
- *Spin-off*: a cluster of settled work that is mutually exclusive with the remaining open questions becomes its own workspace, with a provenance pointer and an explicit scope boundary so it can be run in parallel.

Commit binding for these follows *provenance, not file type*: the promoted document, the removal of the original, and any entry-document wiring derived from that item all belong to one commit, so history shows which item each edit came from. Shared bookkeeping closes as its own unit.

**Close.** Residues convert by a fixed mapping: contract-affecting decisions become permanent events; unresolved questions become deferred-queue entries; adopted designs go to their canonical homes; execution tracking is not promoted and is summarized in a closing receipt. The close gate produces a *drain map* from local id to promoted location, rewrites live normative documents to point at the promotions, leaves historical references alone, and requires **zero remaining references to the workspace from live normative documents** — with the scan universe being the whole repository, not the workspace.

### Why it exists

Multi-session structural work otherwise keeps its state in conversation. A session ends, and the successor either re-litigates settled questions or, worse, silently reverses them — because a decision that exists only as a message has no location, so nobody can check whether it was made.

The failure the numbering separation prevents is specific and observed: workspace-local ids leak into permanent documents. They look like real identifiers, and they resolve fine while the workspace exists. Then the workspace is deleted at close and every one of those references dangles, pointing at something that not only does not exist but was designed not to. The drain map plus the zero-live-references close gate exist because that cleanup is not optional and will not happen by itself.

### If you change it

Precondition again: if your work units fit in one session, skip this entirely. Substitutes must preserve: state lives in files rather than in conversation; the workspace's ids can never be mistaken for permanent ones; there is a defined conversion mapping at close; and a close gate verifies that nothing living still points at the deleted workspace.

### Depends on / breaks without

- **B2** — the separation between local and global numbering *is* the mechanism. Without a global issuance discipline to be separate from, local ids drift into permanent documents and the close gate has nothing to enforce.
- **C1, C3** — workspace ownership presupposes session isolation and a session-per-work-unit boundary. Without them, "the owning session" does not identify anything.
- **B1** — the close mapping's destinations are the permanent event stores. Without them, closing has nowhere to promote to and the workspace either becomes permanent (defeating the point) or is lost.
- **A4** — the departure ledger is a manifest and follows the manifest discipline.

---

## F5 — Profile composition

**Tier: OPTIONAL.** Precondition: you generate many artifacts of one family whose correct shape varies with input characteristics, so that a fixed template is either too loose to be useful or wrong for a large fraction of inputs.

### What it is

Output is composed, not templated:

```
artifact = core contract + shape profile + presentation profile + confirmed user override
```

The core contract holds requirements that every artifact of the family must satisfy. The shape profile is selected by what the input *is structurally*. The presentation profile governs how the result is laid out. User overrides apply only when confirmed.

**Axis orthogonality is the substantive claim.** What an input is *about* and how it is *shaped* are independent, and structure must never be chosen from subject matter alone. A third axis — how the consumer intends to use the artifact — is applied only when explicitly stated, and an inferred purpose is never recorded as if it were a fact about the input.

**Profiles are versioned artifacts, not config.** Each carries an integer version, a status, selection signals ("choose this when the input has these characteristics"), the structure it adds on top of the core contract, notes on which presentation profile it defaults to, **known exceptions** ("if the input is actually X, use profile Y instead"), and a version history with a line per bump. The known-exceptions section is the highest-value part and the one adopters skip: it is how the profile set stays a decision procedure rather than a menu.

**Where a profile governs prose rather than structure, attach a paired-example ledger and require it to be read before writing.** A register profile can state its rules exactly and still fail to transmit the judgment behind them, because the rules are about degree — how much hedging is too much, when a metaphor stops carrying its weight — and a sentence about degree does not tell a writer where the line is. A ledger of matched pairs does: a rejected passage, its accepted revision, and one line on what moved between them. It is a separate asset from the profile, not a section of it, because it grows by a different rule — each pair earns its place by having been a real disagreement, so the ledger is an accumulating record while the profile is a versioned standard. The load-bearing part is *when* it is consulted: before writing, as a step in the composition procedure. Left to review time it becomes an appeals file, read only when a judgment is already contested, which is after the writing cost has been paid and after the author has something to defend.

**The generated artifact records which profiles and versions produced it**, as machine-readable fields, checked by the validator: a declared profile must exist in the registry (error), a missing version is a warning, a registry entry nothing declares is an error. Artifacts still declaring a superseded version are reported as a single aggregated row with a count and a sample, not as one finding per artifact.

### Why it exists

Without recorded profile versions, improving a profile leaves you unable to say which existing artifacts were built under the old rules. Every quality question then requires a full re-read of the corpus, and since nobody does a full re-read, the honest answer becomes "we do not know." Under a two-stage severity rollout this gets acute: artifacts produced under the old profile fail the new check en masse, and there is no way to distinguish *not yet migrated* from *actually broken*. The aggregated-row reporting exists for exactly that reason — a hundred individually-reported not-yet-migrated artifacts drown the three real failures, and the usual response is to downgrade the check, which E2 forbids for good reasons.

Without axis orthogonality, structure gets chosen by subject, and two inputs on the same subject with completely different shapes receive the same skeleton — one of them badly. The symptom is a template that grows optional sections until it fits everything and constrains nothing.

Without a known-exceptions section, profile selection becomes a taste judgment made fresh each time, and the same input shape lands on different profiles depending on who processed it.

### How to adopt

- Separate the invariant contract from the variable profile. Anything that is true of every artifact in the family belongs in the contract; if a requirement has exceptions, it is profile material.
- Make the shape and presentation axes independent, and write the orthogonality rule down — it is counterintuitive and gets violated by default.
- Give each profile explicit selection signals and a known-exceptions section pointing at sibling profiles.
- Version profiles as integers with a version-history section, and record the profile ids and versions in the generated artifact's frontmatter.
- Add registry checks in both directions: declared-but-unregistered is an error, registered-but-never-declared is an error.
- Report stragglers on an old version as one aggregated row, never as one finding per artifact.

### If you change it

If your artifact family genuinely has one shape, use a template and skip this. A substitute must preserve: the invariant/variable split; selection by input characteristics rather than by author preference; recorded provenance of which rule version produced the output; and aggregated rather than per-artifact reporting of version stragglers.

### Depends on / breaks without

- **E3** — recorded profile versions are what let a contract change compute its blast radius. Without them, fixture auto-selection can identify *which contract* changed but not *which artifacts embody it*.
- **B4** — the rebuild threshold reads accumulated-patch counters on the artifact; profile-version fields sit in the same frontmatter and are maintained by the same discipline. Both answer "is this artifact still what the current rules would produce?"
- **E4** — profile and version fields must be in the closed field set and enum-checked, or they drift into free text and the registry cross-check has nothing reliable to compare.
- **B3** — profiles sit on the middle rung of the promotion ladder: technique becomes profile, profile becomes automated check. A profile system with no ladder above it accumulates prose that never becomes enforceable.

---

## F6 — Tool entry points: one canon, thin links

**Tier: CORE.** Every agent tool auto-loads its own entry file, so a repository worked by more than one tool has more than one always-loaded instruction file — and duplicated instructions diverge silently, leaving each tool's agents following a different contract while both believe they follow the same one.

### What it is

Each agent tool reads an instruction file at a filename of its own choosing, automatically, before doing anything. A repository worked by two tools therefore has two such files, and neither tool reads the other's.

The rule is a split by *nature*, not by convenience:

- **One file is canonical** and carries every tool-agnostic instruction: the layers, the gate command, the evidence chain, the parallel rules, the approval boundary.
- **Every other tool's entry file contains a link to the canon plus only what is genuinely specific to that tool** — its model tier names, its subagent interface, its own switches. If a rule holds regardless of which tool executes it, it does not belong there.
- **Long procedures are never duplicated into a compatibility file.** The compatibility file points; the canon holds.

**The canonical file is itself some tool's entry point, and that is a case inside the rule rather than an exception to it.** The filename chosen as canon is chosen because a tool already loads it, so when that tool is the one executing, the canon is *its* entry file too — and the content specific to it has no other file to live in. Write this case down. A reader who finds a tool-specific table inside a document declared canonical, with no clause admitting the case, reads the boundary as already broken, and then either deletes content the tool needs or concludes the boundary is decorative. The clause is one sentence: content specific to the tool that reads this file directly belongs here, because for that tool this file is the thin one.

**Roles live in the canon; names live in the tool files.** The mapping from task class to tier *role* — which class of work needs the strongest model available and which degrades gracefully at a lighter one — is true whichever tool executes it, so it is stated once, tool-agnostically, and it is D4's rule rather than this one's. What varies with the tool is the *identifier* that fills each role. Each tool's entry file therefore carries a role-to-name table and the reasoning for none of it. This split is why a tool file can stay short, and it is what keeps a model name from being written into a rule: the rule names a role, and roles outlive names. By the previous paragraph, the tool that reads the canon directly puts its own row in the canon.

The test for whether a line belongs in a tool file: would it still be true if the repository were worked by a different tool? If yes, it belongs in the canon.

This is the same shape as F1 — one canonical source, thin generated or linked copies — applied one level up, to the files the tools load rather than to the procedures they invoke. If your tool files ever grow past pointers and tool-specific settings, generate them instead of hand-maintaining them, and put a drift check on the result (A4).

### Why it exists

Duplicated instructions do not stay duplicated. Someone corrects a rule in the file their own tool loaded, because that is the file in front of them and it looks authoritative. The other tool's file keeps the old rule. Both files remain internally coherent, so nothing looks wrong from either side, and no check fires — the divergence is only visible to someone who diffs two documents nobody thinks to diff. Later, two agents on the same repository enforce different contracts and each cites its instruction file.

The mirror failure is a compatibility file that grew into a second canon. It starts as a pointer, gains a helpful summary, then a clarification, and eventually contains rules that exist nowhere else — at which point deleting it loses content and keeping it means the canon is no longer canonical.

There is also a plain cost: instructions that load on every single run are the most expensive text in the repository. A rule stated twice is paid for twice, forever.

**A principle shipped without the object it applies to is the third failure, and this specification committed it.** An earlier packaging of this harness carried F6 as CORE and shipped no entry file at all — neither the canon nor a thin one. An adopter reading the rule had to invent the artifact before applying the rule to it, and the shape they invent is the shape the rule exists to prevent: tool-agnostic content lands wherever it was first written, which is whichever file the adopter's own tool loads, and the canon is then reconstructed later out of a file that was never neutral. Measured once, in this harness's own packaging, and the repair was to ship the entry files filled rather than described. The general form is worth carrying: a mechanism whose adoption produces a *file* is not adopted until the file exists as a starting artifact.

### How to adopt

1. Name the canonical file and say so inside it. Do not leave it implicit.
2. In every other tool's entry file, keep a link to the canon and nothing that would be true under a different tool. State that prohibition inside the file, so the next agent to edit it sees the boundary before adding to it.
3. Sort the existing content by the test above. Anything tool-agnostic moves to the canon; anything left should be short enough to read at a glance.
4. Declare all of them in the structure registry (A2), so a new tool's entry file cannot appear undeclared.
5. If you have more than two, generate the thin files from a template and add the drift check (F1, A4). Below that, the discipline is cheaper than the generator.
6. Create both files in the same commit, populated. Writing the canon and leaving the tool file for later is the failure above in slow motion: every rule that arrives in the interval is written where the acting tool can see it, and by the time the thin file exists there is nothing left to put in it.
7. Adopting into a repository that already has a file at the canonical name: do not overwrite it. Place the harness's content inside an exact paired marker region — inside the markers is the harness's to replace, outside is the adopter's and no update touches it — and take a later version by replacing the region rather than by merging the file. The marker form, the exclusivity rules, and the near-miss failure are A4's; this is that discipline applied to a file the harness does not own. Without the boundary, a later version can only be hand-merged, and hand-merging an always-loaded instruction file is how the two halves of it start disagreeing.

### Depends on / breaks without

- **F1** — the same one-canon-many-copies principle; adopt them together and share the vocabulary, or "drift" comes to mean two different things in one repository.
- **F2, F3** — the routing sentence that binds trigger-matched procedures, and the entry-document boundary rules, both live in the canon and are the first things to get duplicated.
- **A2** — entry files are paths like any other and must be declared, or a new tool's file arrives unnoticed.
- **A4** — the transplant region inside an adopter-owned entry file is a marker-bounded region under someone else's roof. Without the marker discipline there is no locatable boundary between what the harness maintains and what the adopter wrote, and the next version arrives as a merge conflict rather than as a replacement.
- **D4** — the roles the tool files name models for. If the class-to-tier rule is not stated somewhere tool-agnostic, each tool file grows its own reasoning about which work needs which tier, and two tools on one repository delegate by different rules while both cite their instruction file.

### If you change it

CORE, though the number of tool files is set by your toolchain rather than by you. A substitute must preserve three properties: exactly one file is canonical for tool-agnostic rules; every other entry file is bounded to pointers plus genuinely tool-specific content; and no long procedure is restated in a compatibility file. Keeping full copies in sync by hand is not a substitute — that is the failure, not an implementation of the rule.

---

## F7 — Working-language policy

**Tier: OPTIONAL.** Precondition: the language the repository works in is not English. Where it is, the axes below collapse harmlessly — everything is already English and there is nothing to hold apart — and the mechanism costs a paragraph nobody needs. State that precondition inside the mechanism rather than in a note about it, the way F4 does: an optional mechanism that does not name the condition under which it is skippable gets adopted as ceremony by the next reader, who has no way to tell that it was meant to be skippable.

### What it is

Four axes, declared separately in the always-loaded canonical entry document (F6), each with its own value:

- **Replies to the user** — the working language.
- **Human-readable prose inside the repository** — the working language, and set independently of the line above. A repository can answer in one language and hold its durable prose in another; these are different decisions with different audiences.
- **File and directory names** — English, in a fixed casing convention, regardless of the two above.
- **Metadata keys** — frontmatter fields, registry keys, machine fields — English, regardless of the two above.

**The separation is the mechanism, not a formatting choice.** Collapsed into one declaration — "this repository works in language X" — the rule about prose silently becomes a rule about filenames. Nothing objects at the moment it happens, because the collapsed sentence is true of prose and the reader extends it by default. What arrives later is a path that no glob written in English matches, an identifier that sorts differently on two filesystems, and a metadata key that a closed field schema (E4) has to be widened to accept. Each of those is repaired one at a time and none of them points back at the declaration that caused it.

**A cross-language brief.** Where the working language is not English, every durable document carries a short English summary section. The reader who does not share the working language is not hypothetical — it is any newcomer, any reviewer brought in for one question, and any tool whose own operating vocabulary is English. What the brief has to support is *routing*, not reading: is this the document I need, and what does it claim. A brief written as a translation of the document is a second document to maintain and will go stale; a brief written as a few sentences of orientation will not.

**The rule states where its own mechanical coverage ends.** A language or terminology rule that is enforced by a check is enforced over the paths that check scans and nowhere else — typically some directories and not others, and typically not over the agent's own utterances to the user at all. Write that boundary into the rule body: name where the check reaches, and say that beyond it the rule holds only as far as it is read. This is the same move E1 makes when it names its coverage as fourteen of seventeen procedure specs and calls the gap the instructive part. The failure it prevents is specific: a rule with a check attached reads as fully enforced, so the places the check does not reach are not treated as unguarded — they are not treated at all. The person who eventually finds the gap experiences it as a discovery about the system, and reacts by distrusting the check, when the honest version would have made it a stated limit from the beginning.

**Preserve phrasing that carries meaning — and this is the weaker of two layers, deliberately.** E5 protects bytes a person wrote, inside recognized carriers, against mechanical operations, and it is fail-closed: an unknown layout aborts. F7 asks something softer of a different actor. It governs prose the *agent* writes — a summary, a paraphrase, a translation of a constraint into a rule — and asks that the one word carrying the constraint survive the compression. There is no carrier, no mechanical operation, and no check; the only enforcement is that the rule is read. Keep the direction explicit when you write both down, because collapsing them is a live error: this specification's own coverage audit initially recorded the soft rule as satisfied by the byte-level one, which had the effect of retiring a rule that was never covered.

### Why it exists

**A collapsed language declaration produces failures far from where it was made.** The declaration is one sentence and reads as obviously correct. Months later the repository has directory names an English-language glob cannot address and frontmatter keys that appear in two spellings, and every one of those was written by an agent correctly following the sentence it read. There is no moment at which the rule was broken, which is why the repair is at the declaration rather than at the symptoms.

**A repository whose prose is in one language becomes unreadable to everyone else at the routing level first.** Not at the reading level — a reader who cannot read the prose knows it. At the routing level a reader can see filenames, headings, and structure, forms an impression of what each document is, and is wrong, with nothing to signal it. The brief exists because being unable to read a document is a recoverable state and believing you have identified it is not.

**An enforced rule is assumed to be enforced everywhere.** The presence of a check changes how a rule is read — from "follow this" to "this is handled" — over the whole scope the rule names, not the smaller scope the check covers. Naming the boundary is what keeps the uncovered part in the category of things an agent must actually do.

### How to adopt

- Declare the four axes as four separate lines in the canonical entry document. Four lines, even when two of them carry the same value; the redundancy is what stops the collapse.
- Set the file-name and metadata-key axes to English regardless of the working language, and say *regardless* in the text. A reader who has to infer independence will infer dependence.
- Require a short English section in every durable document class, and specify it as orientation rather than translation, so it is cheap enough to actually be written.
- For every language or terminology check you wire in, write the covered paths into the rule body next to the rule, and a sentence saying what holds beyond them and on what basis.
- Keep the agent-prose preservation rule textually separate from byte-level protection (E5), with a sentence stating which is stronger. Two rules that sound alike and differ in strength get merged by the next person to tidy the document.

### Depends on / breaks without

- **F6** — the axis declaration belongs in the canonical entry document, because it is true regardless of which tool executes. Declared in a tool file instead, agents under the other tool work in an undeclared language.
- **E5** — the strong layer this one sits under. Without it, the soft preservation rule is the only thing standing between a mechanical pass and text a person wrote, which is a load it cannot carry.
- **E4** — the metadata-key axis is what keeps the closed field set to one spelling per field.
- **E1** — the coverage statement is a claim about which checks run over which paths. With no wired validator there is no mechanical jurisdiction to bound, and the whole rule reduces to the read-only half.

### If you change it

Skip the mechanism entirely if the precondition is false — that is what OPTIONAL means here, and the check before skipping is one question: is any durable prose in this repository written in a language other than English. If you keep it, a substitute must preserve four things: the axes are declared separately rather than derived from one another; identifiers and machine keys are pinned to one language independent of the prose language; a reader who does not share the working language can route without reading; and every rule with partial mechanical enforcement states where that enforcement stops.

---

## F8 — Reporting to the user

**Tier: DEFAULT.** The item list is one workable set and yours can differ. What is not substitutable is that a channel addressed to the person exists at all, separately from the records the repository keeps for itself — a repository whose only reporting surface is its own evidence chain has an operator who cannot see what happened without becoming a reader of that chain.

### What it is

After a meaningful operation, the agent reports to the user a fixed set of items:

- files read,
- files created,
- files modified,
- conflicts and open questions,
- commits, by hash and subject.

Fixed is the operative word. A report assembled fresh each time is assembled out of what the run *felt* like, and what a run feels like is dominated by whatever was hardest — which is usually not what the user needs to know. A fixed set is answerable even when a slot is empty, and an empty slot is itself information.

**Absence is reported as absence.** If a source could not be found, say so. If a claim cannot be supported by what was read, say so. If part of the requested scope was not done, say which part. An unstated gap is read as a covered one: the reader cannot distinguish "not mentioned because it was fine" from "not mentioned because it was never looked at," and the default reading of silence is the first. This is the item most often dropped, because every other item in the list is a record of work done and this one is a record of work not done.

**Three reporting channels exist, and each drops what another reader needs.** They look interchangeable because they carry overlapping facts; they are not, and the discriminator is what each one is entitled to leave out.

- **The run receipt (B1)** is the repository's own memory: immutable, stateless, written to be read later by an agent reconstructing what a past unit did. The property that makes it good evidence — it cannot be revised — is exactly what makes it useless as an answer to the person waiting now, who is asking about a state that is still moving.
- **The report to an orchestrator (D1)** is capped and restricted to verifiable values, with narrative, reasoning, and alternatives deliberately excluded, because the orchestrator's judgment capacity is the scarce resource and report volume consumes it before the decisions do. It does **not** drop uncertainty, blockers, significant findings, requests for clarification, or final status — D1 forbids suppressing those on length grounds, and this document does not weaken that. What the caps legitimately remove is everything that would let a reader *judge* rather than *route*: why the agent is uncertain, what it considered and rejected, what the thing it is unsure about would cost if it is wrong. An orchestrator needs to know a question exists so it can be routed. The person who has to answer it needs the part that was cut.
- **The report to the user** is ephemeral and shaped for one person's immediate decision. It leaves no durable trace at all, which is why it does not replace the receipt.

Collapse any two and one reader is served a document shaped for a different one. The common collapse is treating the receipt as the report — the facts are all there, so the report becomes a pointer to it — and the result is a user who must open a record store to learn what just happened to their repository.

**Nothing checks this one.** Enforcement is the always-loaded entry document and the procedure text, and nothing else: no validator can determine whether an agent said something to a person, and none of the artifacts a check can read change depending on whether the report was made. Say so where the rule is written. An unstated absence of enforcement is the same defect F7's jurisdiction clause exists to prevent, and it would be an odd document that demanded the disclosure of one and concealed the other.

### Why it exists

**An operation completes and the user cannot say what changed.** The work was correct and the repository is in a good state, and neither of those facts is available to the person who asked, because the only record of them is inside files they would have to go read. What follows is not a complaint — it is a slow withdrawal of oversight. A user who cannot cheaply see what an agent did stops trying to, and the review that would have caught the one wrong change stops happening.

**A partial result reads as a whole result.** An agent that completed four of five requested items and reports the four has said nothing false. The user, having no list to check against, reads a completed request. This is the single highest-value item in the set and the one a report drops first, because the four are the work and the fifth is an admission.

**"It is in the receipt" is a pointer, not a report.** The evidence chain is written for a reader who arrives later with a question. The user in front of you has a different question — what did you just do — and answering it with a location is answering a different reader's question at their expense.

### How to adopt

- Write the item list into the always-loaded canonical entry document as a fixed set, and report every slot including the empty ones.
- Include the absence item explicitly and name its three forms — missing source, unsupportable claim, unfinished scope — because a general instruction to be honest does not produce them.
- State in the same place that this channel is distinct from the durable receipt and from any report to an orchestrator, and say in one line what each is for. Without that sentence the next person to tidy the document merges two of them.
- Say that nothing checks it. A rule that is procedure-text-only should be labelled as procedure-text-only wherever it is stated.
- Keep the report short enough to be read. The gate is whether a user can see what happened without opening a file, not whether the report is complete in the way a receipt is.

### Depends on / breaks without

- **B1** — the durable half of the same facts. Without a receipt the user-facing report becomes the only record, and it is ephemeral, so the repository loses its memory of the run while appearing to have reported it.
- **D1** — the orchestrator-facing report with its verifiable-values-only rule and its length caps. The two are distinguished by reader; if the orchestration channel is the only one defined, its economy rules get applied to the user and remove exactly the signals the user is there to receive.

### If you change it

DEFAULT: the item set is yours, and a project whose users read commits directly may need less. A substitute must preserve three properties. The set is fixed in advance rather than composed per run. Absence is an item, with unfinished scope named as a form of it. And the channel is distinguishable from the repository's durable records — a report that consists of a pointer to where the facts were written is not a report, it is a change of subject.

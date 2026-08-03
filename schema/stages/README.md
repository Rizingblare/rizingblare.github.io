# Volatile workspaces — OPTIONAL

Skip this entire layer if your work units fit in one session. The harness is
complete without it: the evidence chain alone performs the full workflow, and
this is a management optimization for one shape of work — units spanning many
sessions that mix unsettled design questions with executable tasks.

That subsidiarity statement is deliberate. An optional layer that does not say
what the system does without it gets treated as mandatory by the next reader.

One workspace per large unit, holding: a manifest with the goal and a resume
procedure, a departure ledger, one file per open question, one file per settled
decision with its grounds verbatim, one file per work item, and drafts.

Three rules carry the weight.

**State canon is file location plus frontmatter, never duplicated into the
manifest.** Only items that *leave* get ledger rows. Resident items are tracked
by the directory itself.

**Local ids are structurally separate from the global event sequence**, and can
never become permanent references. On promotion a workspace decision is
*regenerated* as a real event with a globally issued number — not renamed into
one. The failure this prevents was observed: local ids leaked into permanent
documents, resolved fine while the workspace existed, and dangled the moment it
was deleted, pointing at something designed not to exist.

**No files at the top level of this directory.** That is how undeclared-path
practice reproduces itself.

Close by a fixed mapping: contract-affecting decisions become permanent events,
unresolved questions become queue items, adopted designs go to canonical homes,
execution tracking is summarized in a closing receipt and not promoted. The close
gate produces a map from local id to promoted location and requires **zero
remaining references from live normative documents** — scanning the whole
repository, not just the workspace.

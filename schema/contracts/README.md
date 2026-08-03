# Contracts

Rules whose violation is a failure. This is the middle rung of the promotion
ladder: technique note (no violation concept) → contract (versioned, scoped) →
automated check (an id in the closed catalogue).

Keep the rungs distinct. Everything-is-a-rule makes the rule set unusable;
nothing-is-a-rule leaves verified findings advisory forever.

Suggested subdivisions, none of them mandatory: layer charters, artifact shapes,
quality criteria, controlled vocabularies, individual user preferences, and
operating policies.

Two shapes are worth copying from the source project.

**One file per preference.** A preference carries a statement, a scope, evidence
links, and a status — candidate, active, superseded, or conflict. Bullet points
in a shared document cannot carry per-item status: supersession gets lost in the
edit and the conflict state has nowhere to live.

**Three scope levels**, not two: this artifact, this class of artifact, and
global. With only local and global there is nowhere to put "true for this class,
not everywhere", so a later contradiction forces someone to delete the earlier
rule, and the case it was right about is lost.

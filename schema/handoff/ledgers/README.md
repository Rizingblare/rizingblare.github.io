# Operating ledgers — persistent

State that outlives a session but belongs to an ongoing unit: decisions awaiting
the user, assignment rationale, unfulfilled notification duties, incident history
that informs the next assignment.

Updated by whoever currently holds the role. Never deleted.

**Inside the repository, and this is the part that was learned the hard way.** In
the source project a ledger was twice placed in a temporary directory and twice
lost wholesale to a runtime restart. The reasoning that leads there is seductive
— in-progress state is not repository content, so it seems to belong outside.
The correction: *durability requirement*, not content type, decides the home. A
ledger the next session must read is a durability requirement.

Being outside the repository is not a persistence mechanism.

Open each ledger by naming what is deliberately absent from it and why. That one
paragraph does more work than the same rule filed somewhere else.

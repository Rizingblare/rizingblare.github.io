# CLAUDE.md

@AGENTS.md

<!--
  This file exists because Claude Code auto-loads a file at this exact name
  before doing anything, and it does not read AGENTS.md on its own. The link
  above is what makes the canon reach this tool.

  THE BOUNDARY, and read it before adding anything below: the only content that
  belongs in this file is content that would be FALSE under a different tool.
  Everything else — layers, the gate command, the evidence chain, parallel rules,
  approval boundaries, git discipline — lives in AGENTS.md and is reached through
  the link.

  The test is one question: would this line still be true if this repository were
  worked by a different agent tool? If yes, it belongs in the canon.

  This matters more than it looks. A compatibility file that grew into a second
  canon starts exactly like this one — a pointer, then a helpful summary, then a
  clarification, and eventually rules that exist nowhere else. At that point
  deleting it loses content and keeping it means the canon is not canonical.
  Meanwhile instructions that load on every single run are the most expensive
  text in the repository: a rule stated twice is paid for twice, forever.

  Replace every <ANGLE-BRACKET> placeholder with your own values.
-->

## Delegation tiers

`AGENTS.md` sets the rule — rewrite-class generation goes to the strongest model
available, investigation and mechanical verification go to a lighter one. This
section supplies only the **names**, because the names are the part that changes
with the tool.

| Role in the canon | Model for this tool |
|---|---|
| Rewrite-class generation — writing a document from a blank page, a full rebuild, composing an artifact against a contract | <top-tier model, e.g. Opus-class> |
| Investigation and mechanical verification — reading a corpus and reporting what is in it, sweeps, format conversions, link rewiring, checking a claim against a file | <lighter model, e.g. Sonnet-class> |

An explicit user instruction overrides this table.

`AGENTS.md` already requires the model and reasoning effort in every launch label
and completion report, and requires verifying that the specified tier was actually
applied. Both rules hold under any tool, so neither is restated here — this file
supplies only the two values that differ per tool:

- **Label form:** `<what the agent is doing> [<model>·effort <level>]`
- **Verification channel:** `<the record THIS tool writes when it invokes a model
  — the stored invocation, not its console log and never the delegate's own
  account of itself>`

Fill the second one in carefully. The canon can say to verify through a record the
tool writes; only someone using this tool can say which file that is.

## Tool-specific notes

- `<diagnostic command, e.g. the one that lists loaded instruction files>` — use
  only when you need to confirm which instruction files this tool actually
  loaded. It answers a question about the tool, not about the repository.
- `<any other switch, subagent interface detail, or setting that is genuinely
  specific to this tool>`

<!--
  If your toolchain grows past two entry files, stop hand-maintaining them:
  generate the thin ones from a template and put a drift check on the result.
  Below two, the discipline is cheaper than the generator.
-->

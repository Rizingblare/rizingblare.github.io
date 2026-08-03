# Repository harness engine

Three small modules that give a repository a machine-checkable structure, and
a gate that enforces it. They are project-neutral: the engine knows about
paths, selectors, markers and exit codes, and nothing about what your files
mean. Your vocabulary is injected; your checks are plugged in.

| Module | What it is |
| --- | --- |
| `registry.py` | A fail-closed loader for a structure declaration document, plus a selector engine that maps any path to exactly one declaration. |
| `markers.py` | Scan, extract and replace generated regions inside otherwise hand-written files, with atomic writes. |
| `validate.py` | One command, one exit code: the project-neutral check series, plus your project's checks. |

No third-party dependencies. Python 3.10 or newer (the code uses `X | Y`
annotations).

**The three modules import each other by bare name**, so they resolve only when
the engine directory itself is on `sys.path`. They are not a package: `import
scripts.engine.validate` fails at `validate.py`'s own `import markers`. Every
Python example below therefore begins by putting that directory on the path, and
the shipped `scripts/check.sh` does the equivalent for the command line. If you
would rather have a real package, add an `__init__.py` and rewrite the three
sibling imports to be relative — that is a fork of the engine, not a setting.

---

## 1. The structure registry

### Why

A repository accumulates directories faster than anyone documents them. The
registry inverts that: one document declares which selector owns which part of
the tree, and the gate fails when a tracked path matches nothing. New
directories then cannot appear without someone stating what they are.

### The document

```yaml
schema_version: 1

declarations:
  - select: docs/**
    role: content
    disposition: ship
    overrides:
      - select: docs/internal/**
        disposition: skip
  - select: "*"
    role: support
    disposition: ship
  - select: src/
    role: content
    disposition: ship

exclusions:
  - select: build/**
    reason: compiler output, regenerated on every run
```

`schema_version` and `declarations` are required. `exclusions` is optional
unless your schema requires it. Any other top-level key must be named in
`extra_top_level_keys`; the engine then preserves it verbatim under
`Registry.extra` and leaves its meaning to you.

An exclusion needs a written reason. It is the one declaration that turns a
check off, and an unexplained silenced check is indefensible a year later.

### Selectors

Six shapes, and nothing else compiles:

| Shape | Kind | Reach |
| --- | --- | --- |
| `docs/guide.md` | exact | that one file |
| `docs/` | direct | files directly inside `docs`, no deeper |
| `docs/**` | subtree | every file at any depth below `docs` |
| `*` | root | files sitting directly at the repository root |
| `docs/*` | single | one segment below `docs` (same reach as `direct`, scored lower) |
| `**/name/**` | anysub | any directory called `name`, at any depth |

Specificity is the triple `(exactness, literal segment count, -wildcards)`,
compared left to right. Exact beats every glob; among globs the longer literal
prefix wins; among equals, fewer wildcards wins.

Two declarations that tie on specificity for the same path are an **error**,
not a first-one-wins. Order-dependent resolution is a rule that exists in the
document's line numbering and nowhere in anyone's head.

An `overrides` entry must be strictly more specific than its parent *and*
contained in it. A wider override would shadow its parent everywhere; one
pointing outside would claim paths the parent never owned. Both are load
errors.

### Injecting your vocabulary

The engine validates structure. `RegistrySchema` supplies meaning:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("scripts/engine").resolve()))

from pathlib import Path
import registry

SCHEMA = registry.RegistrySchema(
    roles=("content", "support", "generated"),
    dispositions=("ship", "skip", "stub"),
    required_declaration_keys=("select", "role", "disposition"),
    optional_declaration_keys=("note", "overrides"),
    extra_top_level_keys=("project_block",),
    require_exclusions=True,
    max_key_depth=4,
)

reg = registry.load_registry(Path("schema/kernel/layout.yaml"), SCHEMA)
```

An empty tuple for `roles` or `dispositions` means *not constrained here*: the
value must still be a non-empty string, but membership is your problem. That
is what `PERMISSIVE_SCHEMA` uses, and it is what the standalone command line
falls back to, because a command line cannot know your enums. It is a
deliberate weakening. Pass your own schema whenever you can, so a typo in a
disposition fails at load rather than travelling downstream.

### Asking questions

```python
reg.verdict("docs/guide.md")     # PathVerdict(status="declared", disposition="ship")
reg.verdict("build/out.js")      # status="excluded"
reg.verdict("stray/file.md")     # status="undeclared"

reg.disposition_of("docs/internal/plan.md")   # "skip" (from the override)
reg.disposition_of("build/out.js")            # None -- excluded, no disposition
reg.disposition_of("stray/file.md")           # raises KeyError

reg.resolve_one("a/x.md")        # the one owning Declaration, or None
                                 # raises AmbiguousPathError on a tie

reg.audit(tracked_paths)         # [PathIssue(kind="undeclared" | "ambiguous"), ...]
```

*Declared*, *excluded* and *undeclared* are three distinct answers. Collapsing
them into one nullable result is how "nobody declared this path" comes to look
like "this path is deliberately out of scope".

If your project has its own top-level blocks, validate them yourself and feed
the resulting declarations back in, so they take part in the same resolution
and the same duplicate check:

```python
reg.extend([
    registry.Declaration(
        origin="project",
        label="project:tools",
        selector=registry.compile_selector("tools/**"),
        disposition="ship",
    )
])
```

### Failure behaviour

`load_registry` raises `RegistryError` carrying **every** collected message,
and returns nothing partial. A half-loaded registry is worse than none:
callers would resolve some paths correctly and silently mis-attribute the
rest.

The parser accepts a closed subset -- block mappings, block lists, and
single-line flow shorthand. Anchors, aliases, merge keys, type tags, block
scalars, duplicate keys, tab characters and nesting past `max_key_depth` are
all hard errors. The subset is small so that a reader can hold all of it in
mind and two parsers cannot disagree.

---

## 2. Generated regions

A generated region is a span of a hand-written file that a tool owns:

```text
<!-- gen:begin key=index -->
... generator territory ...
<!-- gen:end key=index -->
```

A whole-file generator uses a single sentinel line instead:

```text
<!-- gen:file key=index -->
```

Both examples sit inside fenced blocks on purpose. The near-miss rule below
treats any unfenced marker-like line as a defect, including in this file, so
naming a marker form in running prose would make the documentation fail its
own gate. The spelling is configurable through
`MarkerSyntax(token=..., open_delim=..., close_delim=..., key_word=...)`, so
the form can match another language's comment syntax or a spelling a
repository already uses. Set it once, in your plugin: a repository whose
markers say `carrier=` would otherwise see every correct marker reported as a
near miss, and a wall of false failures is how a gate loses its readers.

```python
import markers

body = markers.render_body("## Items", ["- alpha", "- beta"])
updated = markers.replace_section(text, "index", body)
markers.atomic_write(path, updated)

markers.check_text(text)          # [MarkerIssue(code=..., lineno=..., message=...)]
markers.extract_section(text, "index")
```

Three behaviours are non-negotiable, and each exists because the opposite
fails quietly:

- **A near-miss marker line is an error.** `key=index-->` with the space
  dropped still looks like a marker to a reader, but no generator will ever
  match it, so the region silently freezes at whatever it last contained.
  Silent staleness beats a crash at hiding itself, which is why it is worse.
- **An empty body is refused.** `replace_section` raises rather than writing a
  blank region, and `check_text` reports an existing blank region. Use
  `render_body`, which always emits a header and a count, so "found nothing"
  stays distinguishable from "did not run".
- **Writes are atomic.** A generator interrupted mid-rewrite must not leave a
  file that is neither the old version nor the new one.

Lines inside fenced code blocks are skipped entirely, including by the
near-miss probe -- otherwise documenting the marker form would be impossible.

---

## 3. The gate

```
sh scripts/check.sh
```

That wrapper is the supported entry point: it invokes the engine by path, sets
`PYTHONPATH` so a plugin import resolves, and demotes `worktree-clean` during
development. Calling the engine directly works too, and then those three things
are yours to get right:

```
PYTHONPATH=. python3 scripts/engine/validate.py \
  --root . --registry schema/kernel/layout.yaml
```

| Option | Effect |
| --- | --- |
| `--root DIR` | repository root (default: current directory) |
| `--registry PATH` | load the registry; enables `undeclared-path` |
| `--plugin module:attr` | your checks and your registry schema |
| `--warn CHECK_ID` | demote one demotable check to warning (repeatable) |
| `--marker-suffix SUFFIX` | file suffixes scanned for markers (repeatable) |
| `--strict` | treat warnings as failures |

Output is one line per finding, then a count:

```text
WARN: [temp-file] docs/scratch.tmp: tracked file looks temporary
FAIL: [os-metadata] .DS_Store: tracked operating-system metadata
Validation complete: 1 failure(s), 1 warning(s).
```

Exit codes: `0` clean, `1` findings, `2` usage or configuration error.

### The check series

The series is closed. Every id defaults to **error** severity, because a gate
whose findings default to advisory teaches people to scroll past it.

| Check id | Reports | Demotable |
| --- | --- | --- |
| `scan-source` | the path universe could not be enumerated (no git, or not a repository) | no |
| `worktree-clean` | uncommitted changes | yes |
| `merge-conflict` | unmerged index entries, or leftover conflict text in a tracked file | no |
| `os-metadata` | tracked operating-system junk files | no |
| `temp-file` | tracked scratch or backup files (name heuristic) | yes |
| `marker-integrity` | malformed, unpaired, nested or near-miss markers | no |
| `empty-state` | an empty path universe, or a generated region that reports nothing | no |
| `undeclared-path` | a tracked path no declaration owns, or an ambiguous tie | no |

`NON_DEMOTABLE` in `validate.py` lists the ids that refuse demotion. Passing
`--warn` for one of them fails at configuration time with exit `2`, rather
than being accepted and ignored. Each of them reports either a defect that is
invisible until it causes damage, or a state in which the rest of the report
cannot be trusted.

`scan-source` deserves a note: when git is missing or the root is not a
repository, the tracked path list is empty, and every path-based check would
otherwise pass on a repository the validator never read. It fails loudly
instead, and says that the checks below it did not run.

`undeclared-path` needs `--registry`. Without it the check has nothing to
compare against, so the run prints a `NOTE:` line saying it did not run. A
skipped check that prints nothing is indistinguishable from a check that
passed, and this is the one check that catches a directory nobody declared.

Marker scanning defaults to `.md`, `.markdown`, `.txt` and `.rst`. Source
files routinely discuss markers in comments, and flagging those would train
people to ignore the check that catches a mistyped marker. Widen the scope
with `--marker-suffix` when you generate into other file types.

### Adding your own checks

One plugin object carries your checks, the registry vocabulary they assume and
the marker spelling they read, so a plugin cannot be loaded with checks that
expect enums the loader was never told about.

```python
# harness_plugin.py — at the repository ROOT, because the command below imports
# it as the top-level module `harness_plugin`. Saving it inside a package would
# make its module path `<package>.harness_plugin` and the command would look for
# a different file.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "scripts" / "engine"))

import markers
import registry
import validate


def check_headings(ctx):
    for relpath in ctx.tracked:
        if not relpath.endswith(".md"):
            continue
        text = ctx.read_text(relpath)
        if text is not None and not text.startswith("# "):
            yield validate.Finding("heading-required", "file does not open with a title", relpath)


PLUGIN = validate.Plugin(
    checks=(validate.Check("heading-required", check_headings),),
    registry_schema=registry.RegistrySchema(
        roles=("content", "support"),
        dispositions=("ship", "skip"),
    ),
    marker_syntax=markers.MarkerSyntax(key_word="carrier"),
)
```

```
# The plugin is imported by module path, so its package must be importable.
# Running validate.py by path puts only the engine directory on sys.path, which
# is why PYTHONPATH is set here: without it the import fails with
# "cannot import plugin module".
PYTHONPATH=. python3 scripts/engine/validate.py \
  --root . --registry schema/kernel/layout.yaml --plugin harness_plugin:PLUGIN
```

A check receives a `Context` (`root`, `tracked`, `registry`, `read_text`,
`git_available`) and yields `Finding(check_id, message, path="")`. File reads
go through `ctx.read_text`, which caches and returns `None` for anything that
is not decodable text.

A plugin check id that collides with the closed series is refused at load: a
reused id could quietly replace an engine check, or make one id mean two
things in one report. Plugin ids are demotable by default -- `NON_DEMOTABLE`
covers the engine series only, and it is yours to extend if a project check
must never be softened.

You can also embed the gate instead of shelling out:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("scripts/engine").resolve()))

import validate
from harness_plugin import PLUGIN

sys.exit(validate.main(sys.argv[1:], plugin=PLUGIN))
```

---

## 4. What this engine deliberately does not do

The omissions are the design, not a backlog. Everything below was left out
because it cannot be right for two projects at once, and a half-generic
version of it would be worse than none.

- **No file schemas.** Front-matter fields, required sections, heading order,
  naming conventions, identifier formats: all of that is a project's own
  vocabulary. Write it as a plugin check.
- **No document-type knowledge.** The engine never asks what kind of document
  it is reading. It reads paths and, for markers, text.
- **No link or reference checking.** Cross-reference syntax differs per
  project. The engine will not guess which bracket dialect you use.
- **No natural-language rules.** Terminology, register, tone and word-choice
  checks depend entirely on a project's own standards.
- **No content generation.** `markers.py` maintains regions; deciding *what*
  goes in them is your generator's job.
- **No opinion about your enums.** Roles and dispositions are strings the
  engine compares against the tuples you supply. It attaches no behaviour to
  any particular value.
- **No severity policy beyond the series.** Which of your own checks may be
  demoted is your call; the engine only guarantees that its own critical ids
  cannot be quietly softened.

The dividing line is simple: if a rule would need to be reworded for a
different repository, it belongs in a plugin, not in here.

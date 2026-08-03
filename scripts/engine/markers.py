#!/usr/bin/env python3
"""Generated-region markers: scan, extract, replace, write.

A *generated region* is a span of a hand-written file whose contents a tool
owns. Delimiting it with markers lets a document mix prose nobody may touch
with a table a generator rebuilds on every run.

    <!-- gen:begin key=index -->
    ... generator territory ...
    <!-- gen:end key=index -->

A whole-file generator uses the single sentinel form instead:

    <!-- gen:file key=index -->

Three rules earn their keep, and each exists because the opposite behaviour
fails quietly rather than loudly:

* A near-miss marker line is an error, not something to skip. A marker with a
  stray space or a misspelled key looks right to a reader while the generator
  no longer sees a region at all, so the section silently freezes at whatever
  it last contained. Silent staleness is worse than a crash.
* An empty replacement body is refused. A generator that produced nothing has
  either found nothing or broken; either way the region should say so in words
  ('0 items'), because a blank region is indistinguishable from a deleted one.
* Writes are atomic. A generator interrupted halfway through a rewrite must
  not leave a file that is neither the old version nor the new one.

Marker syntax is configurable only in its delimiters and token, so the same
engine can annotate comment styles other than the enclosing-comment form.
"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

__all__ = [
    "MarkerError",
    "MarkerSyntax",
    "DEFAULT_SYNTAX",
    "Marker",
    "MarkerIssue",
    "scan",
    "pair_sections",
    "check_text",
    "extract_section",
    "replace_section",
    "render_body",
    "atomic_write",
]


class MarkerError(Exception):
    """Raised when a requested marker operation cannot be performed."""


_FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class MarkerSyntax:
    """How a marker line is spelled.

    `token` namespaces the markers so two independent generators can annotate
    the same file without colliding. The delimiters adapt the form to the host
    language's comment syntax.
    """

    token: str = "gen"
    open_delim: str = "<!--"
    close_delim: str = "-->"
    key_word: str = "key"

    exact_re: re.Pattern[str] = field(init=False, repr=False, compare=False)
    nearmiss_re: re.Pattern[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        for name, value in (("token", self.token), ("key_word", self.key_word)):
            if not re.fullmatch(r"[a-z][a-z0-9-]*", value):
                raise ValueError(f"marker {name} must be lowercase kebab-case: {value!r}")
        # `key_word` is configurable because a repository that already spells
        # its markers another way would otherwise see every one of its correct
        # markers reported as a near miss -- a wall of false failures is how a
        # gate loses its readers.
        exact = re.compile(
            rf"^{re.escape(self.open_delim)} {re.escape(self.token)}:(file|begin|end) "
            rf"{re.escape(self.key_word)}=([a-z][a-z0-9-]*) {re.escape(self.close_delim)}$"
        )
        # The near-miss probe is deliberately loose: it fires on anything that
        # mentions the token and a marker kind, so a line that was *meant* to
        # be a marker cannot slip past as ordinary prose.
        # Any keyword after the token, not just the three spellings that are
        # correct. Restricting the probe to the correct keywords meant a typo in
        # the keyword itself (`begn` for `begin`) read as ordinary prose, so the
        # region silently stopped being regenerated -- the exact failure the
        # near-miss rule exists to prevent.
        nearmiss = re.compile(rf"{re.escape(self.token)}:[A-Za-z][A-Za-z0-9_-]*")
        object.__setattr__(self, "exact_re", exact)
        object.__setattr__(self, "nearmiss_re", nearmiss)

    def line(self, kind: str, key: str) -> str:
        if kind not in ("file", "begin", "end"):
            raise ValueError(f"unknown marker kind: {kind!r}")
        return f"{self.open_delim} {self.token}:{kind} {self.key_word}={key} {self.close_delim}"


DEFAULT_SYNTAX = MarkerSyntax()


@dataclass(frozen=True)
class Marker:
    kind: str  # file | begin | end
    key: str
    lineno: int


@dataclass(frozen=True)
class MarkerIssue:
    lineno: int
    code: str  # near-miss | unpaired | nested | duplicate | empty-section
    message: str


def scan(text: str, syntax: MarkerSyntax = DEFAULT_SYNTAX) -> tuple[list[Marker], list[MarkerIssue]]:
    """Collect exact markers outside fenced code blocks.

    Lines inside a fence are documentation *about* markers, not markers, so
    they are skipped entirely -- including the near-miss probe, which would
    otherwise make it impossible to write an example.
    """
    markers: list[Marker] = []
    issues: list[MarkerIssue] = []
    in_fence = False
    for lineno, line in enumerate(text.split("\n"), start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = syntax.exact_re.match(line)
        if m:
            markers.append(Marker(kind=m.group(1), key=m.group(2), lineno=lineno))
        elif syntax.nearmiss_re.search(line):
            issues.append(
                MarkerIssue(
                    lineno,
                    "near-miss",
                    "marker-like line is not the exact marker form; a generator "
                    "will not see it and the region will silently go stale",
                )
            )
    return markers, issues


def pair_sections(markers: Sequence[Marker]) -> tuple[dict[str, tuple[int, int]], list[MarkerIssue]]:
    """Pair begin/end markers into line spans. Nesting is forbidden.

    Returns {key: (begin_lineno, end_lineno)} for well-formed pairs plus an
    issue per defect. A `file` sentinel owns the whole file and takes part in
    no pairing, so it is ignored here and checked by the caller.
    """
    sections: dict[str, tuple[int, int]] = {}
    issues: list[MarkerIssue] = []
    open_marker: Marker | None = None

    for m in markers:
        if m.kind == "file":
            continue
        if m.kind == "begin":
            if open_marker is not None:
                issues.append(
                    MarkerIssue(
                        m.lineno,
                        "nested",
                        f"nested begin marker inside open section {open_marker.key!r}",
                    )
                )
                continue
            if m.key in sections:
                issues.append(
                    MarkerIssue(m.lineno, "duplicate", f"duplicate section for key {m.key!r}")
                )
                continue
            open_marker = m
        elif m.kind == "end":
            if open_marker is None:
                issues.append(
                    MarkerIssue(m.lineno, "unpaired", "end marker without a matching begin")
                )
                continue
            if m.key != open_marker.key:
                issues.append(
                    MarkerIssue(
                        m.lineno,
                        "unpaired",
                        f"end marker key {m.key!r} does not close open section "
                        f"{open_marker.key!r}",
                    )
                )
                open_marker = None
                continue
            sections[m.key] = (open_marker.lineno, m.lineno)
            open_marker = None

    if open_marker is not None:
        issues.append(
            MarkerIssue(
                open_marker.lineno,
                "unpaired",
                f"begin marker {open_marker.key!r} is never closed",
            )
        )
    return sections, issues


def check_text(text: str, syntax: MarkerSyntax = DEFAULT_SYNTAX) -> list[MarkerIssue]:
    """Full marker integrity of one document, including empty regions."""
    markers, issues = scan(text, syntax)
    sections, pair_issues = pair_sections(markers)
    issues = list(issues) + pair_issues

    file_markers = [m for m in markers if m.kind == "file"]
    if len(file_markers) > 1:
        for extra in file_markers[1:]:
            issues.append(
                MarkerIssue(extra.lineno, "duplicate", "more than one whole-file sentinel")
            )
    if file_markers and sections:
        issues.append(
            MarkerIssue(
                file_markers[0].lineno,
                "nested",
                "whole-file sentinel cannot coexist with begin/end sections",
            )
        )

    lines = text.split("\n")
    for key, (begin, end) in sorted(sections.items()):
        body = lines[begin : end - 1]
        if not any(line.strip() for line in body):
            issues.append(
                MarkerIssue(
                    begin,
                    "empty-section",
                    f"generated section {key!r} is empty; a region with nothing to "
                    "report must still say so (header and a zero count)",
                )
            )
    return sorted(issues, key=lambda i: (i.lineno, i.code))


def extract_section(
    text: str, key: str, syntax: MarkerSyntax = DEFAULT_SYNTAX
) -> str | None:
    """The inner body of the begin/end pair for `key`, or None if absent."""
    lines = text.split("\n")
    begin = syntax.line("begin", key)
    end = syntax.line("end", key)
    try:
        b = lines.index(begin)
        e = lines.index(end, b + 1)
    except ValueError:
        return None
    return "\n".join(lines[b + 1 : e])


def replace_section(
    text: str, key: str, body: str, syntax: MarkerSyntax = DEFAULT_SYNTAX
) -> str:
    """Replace the inner body of the pair for `key`; everything else is untouched.

    Raises MarkerError when the pair is missing or when `body` is blank. Both
    are generator bugs, and returning the document unchanged would hide them
    behind a run that reports success.
    """
    if not body.strip():
        raise MarkerError(
            f"refusing to write an empty body into section {key!r}; "
            "render a header and an explicit zero count instead"
        )
    # Locate through scan() so this sees exactly what check_text() sees. Doing a
    # raw line search instead let the generator rewrite a marker pair that lives
    # inside a fenced code block -- a region the checker deliberately ignores as
    # documentation. The two disagreeing is worse than either rule alone: the
    # check reports a clean document while the generator edits an example.
    lines = text.split("\n")
    found = [m for m in scan(text, syntax)[0] if m.key == key]
    begin_marks = [m for m in found if m.kind == "begin"]
    end_marks = [m for m in found if m.kind == "end"]
    if not begin_marks or not end_marks:
        raise MarkerError(f"no complete marker pair for section {key!r}")
    b = begin_marks[0].lineno - 1
    e = next((m.lineno - 1 for m in end_marks if m.lineno - 1 > b), None)
    if e is None:
        raise MarkerError(f"no complete marker pair for section {key!r}")
    return "\n".join(lines[: b + 1] + body.split("\n") + lines[e:])


def render_body(header: str, items: Iterable[str], empty_note: str = "_none_") -> str:
    """Build a section body that is valid even when there is nothing to list.

    The header and a count always appear. An empty list renders `empty_note`
    rather than nothing, which is what makes 'the generator found no items'
    distinguishable from 'the generator did not run'.
    """
    rows = [str(item) for item in items]
    out = [header.rstrip(), "", f"Total: {len(rows)}"]
    out.append("")
    out.extend(rows if rows else [empty_note])
    return "\n".join(out)


def atomic_write(path: Path, text: str) -> None:
    """Write `text` to `path` through a same-directory temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".marker-write-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise

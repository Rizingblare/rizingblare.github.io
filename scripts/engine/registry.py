#!/usr/bin/env python3
"""Structure-declaration registry: fail-closed loader plus a selector engine.

A *structure declaration registry* is a single small document that states, for
every path a repository tracks, which declaration owns it and what should be
done with it. Two properties make such a registry worth having:

1. It is the only place that knows the shape of the tree, so tools stop
   rediscovering the layout by walking directories and guessing.
2. It is fail-closed. A tracked path that no declaration owns is an error, so
   new directories cannot appear unnoticed.

This module carries only the mechanism. It does not know the vocabulary of any
particular project: the set of legal roles, the set of legal dispositions and
the required key set are *injected* by the caller through `RegistrySchema`.
The engine therefore contains no project nouns, and adopting projects keep
their vocabulary in their own code.

The three parts, in dependency order:

* a strict YAML-subset parser -- a closed set of accepted shapes, everything
  else is an error, and an error loads nothing at all;
* a selector grammar with a total specificity order, where an equal-specificity
  double match is an error rather than a silent first-wins;
* the registry object model: load, resolve a path to exactly one declaration,
  find tracked paths nobody declared, and read dispositions.

Nothing here writes to disk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

__all__ = [
    "RegistryError",
    "AmbiguousPathError",
    "RegistrySchema",
    "PERMISSIVE_SCHEMA",
    "Selector",
    "compile_selector",
    "Declaration",
    "PathVerdict",
    "PathIssue",
    "Registry",
    "load_registry",
    "parse_strict_yaml",
    "DECLARED",
    "EXCLUDED",
    "UNDECLARED",
]


DECLARED = "declared"
EXCLUDED = "excluded"
UNDECLARED = "undeclared"


class RegistryError(Exception):
    """Raised on any load failure; carries every collected message.

    Load is all-or-nothing on purpose. A partially loaded registry is worse
    than no registry: callers would resolve some paths correctly and silently
    mis-attribute the rest.
    """

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = list(errors)
        super().__init__("; ".join(self.errors) or "registry load failed")


class AmbiguousPathError(Exception):
    """Raised when a path matches several declarations of equal specificity.

    Resolving such a tie by declaration order would make the answer depend on
    text position in the document, which is exactly the kind of invisible rule
    a declaration registry exists to remove.
    """

    def __init__(self, path: str, labels: Sequence[str]) -> None:
        self.path = path
        self.labels = list(labels)
        super().__init__(
            f"ambiguous attribution (equal specificity): {path} -> "
            + ", ".join(sorted(self.labels))
        )


# ═══════════════════════════════════════════════════════════════════════
# 1. Strict YAML-subset parser
# ═══════════════════════════════════════════════════════════════════════
#
# The accepted shapes are: block mappings, block lists of scalars, block lists
# of mappings, and single-line flow shorthand ({...} / [...]). Rejected, each
# as a hard error: anchors and aliases, merge keys, type tags, block scalars,
# duplicate keys, tab characters, and nesting deeper than the configured cap.
#
# Rejecting rather than supporting is the point. A registry is read by every
# tool in the repository, so its dialect must be small enough that a reader can
# hold all of it in mind, and small enough that two parsers cannot disagree.


class _ParseError(Exception):
    pass


@dataclass
class _Tok:
    indent: int
    text: str
    lineno: int


_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(\S.*))?$")
_INT_RE = re.compile(r"^-?\d+$")
_FLOW_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")


def _strip_comment(line: str) -> str:
    """Drop a trailing comment, honouring quotes so a '#' inside a string stays."""
    out: list[str] = []
    quote: str | None = None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _tokenize(text: str) -> list[_Tok]:
    toks: list[_Tok] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw:
            raise _ParseError(
                f"line {lineno}: tab character (indentation must be spaces)"
            )
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        toks.append(_Tok(indent, line.strip(), lineno))
    return toks


class _Parser:
    def __init__(self, toks: list[_Tok], max_depth: int) -> None:
        self.toks = toks
        self.i = 0
        self.max_depth = max_depth

    def _peek(self) -> _Tok | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    @staticmethod
    def _err(lineno: int, msg: str) -> None:
        raise _ParseError(f"line {lineno}: {msg}")

    def _depth_guard(self, depth: int, lineno: int, what: str) -> None:
        if depth > self.max_depth:
            self._err(lineno, f"key nesting depth exceeds {self.max_depth}: {what}")

    def parse_document(self) -> dict:
        if not self.toks:
            raise _ParseError("empty registry document")
        first = self.toks[0]
        if first.indent != 0:
            self._err(first.lineno, "document must start at column 0")
        if first.text.startswith("-"):
            self._err(first.lineno, "document root must be a mapping")
        doc = self.parse_mapping(0, 1)
        tok = self._peek()
        if tok is not None:
            self._err(tok.lineno, "unexpected trailing content")
        return doc

    def _split_key(self, tok: _Tok) -> tuple[str, str | None]:
        if tok.text.startswith("<<"):
            self._err(tok.lineno, "merge key '<<' rejected (fail-closed loader)")
        m = _KEY_RE.match(tok.text)
        if not m:
            self._err(tok.lineno, f"invalid mapping entry: {tok.text!r}")
        assert m is not None
        return m.group(1), m.group(2)

    def parse_mapping(self, indent: int, depth: int) -> dict:
        result: dict = {}
        while True:
            tok = self._peek()
            if tok is None or tok.indent < indent:
                break
            if tok.indent > indent:
                self._err(tok.lineno, "unexpected indentation")
            if tok.text == "-" or tok.text.startswith("- "):
                break
            key, rest = self._split_key(tok)
            if key in result:
                self._err(tok.lineno, f"duplicate key: {key!r}")
            self._depth_guard(depth, tok.lineno, repr(key))
            self.i += 1
            result[key] = self._pair_value(rest, indent, depth, tok.lineno)
        tok = self._peek()
        if tok is not None and tok.indent > indent:
            self._err(tok.lineno, "unexpected indentation")
        return result

    def _pair_value(self, rest: str | None, key_indent: int, depth: int, lineno: int):
        if rest is not None:
            return self._inline_value(rest, depth + 1, lineno)
        nxt = self._peek()
        if nxt is None or nxt.indent <= key_indent:
            self._err(lineno, "key has no value")
        assert nxt is not None
        if nxt.text == "-" or nxt.text.startswith("- "):
            return self.parse_list(nxt.indent, depth + 1)
        return self.parse_mapping(nxt.indent, depth + 1)

    def parse_list(self, indent: int, depth: int) -> list:
        items: list = []
        while True:
            tok = self._peek()
            if tok is None or tok.indent != indent:
                break
            if not (tok.text == "-" or tok.text.startswith("- ")):
                break
            content = tok.text[1:].strip()
            if not content:
                self._err(tok.lineno, "empty sequence item")
            if content.startswith("{") or content.startswith("["):
                self.i += 1
                items.append(self._flow(content, depth, tok.lineno))
                continue
            if content.startswith("<<"):
                self._err(tok.lineno, "merge key '<<' rejected (fail-closed loader)")
            m = _KEY_RE.match(content)
            if m:
                # A mapping item carries its first pair on the dash line; the
                # remaining keys sit two columns to the right of the dash.
                self.i += 1
                item: dict = {}
                key, rest = m.group(1), m.group(2)
                self._depth_guard(depth, tok.lineno, repr(key))
                item[key] = self._pair_value(rest, indent + 2, depth, tok.lineno)
                while True:
                    nxt = self._peek()
                    if nxt is None or nxt.indent != indent + 2:
                        break
                    if nxt.text == "-" or nxt.text.startswith("- "):
                        break
                    k2, r2 = self._split_key(nxt)
                    if k2 in item:
                        self._err(nxt.lineno, f"duplicate key: {k2!r}")
                    self.i += 1
                    item[k2] = self._pair_value(r2, indent + 2, depth, nxt.lineno)
                nxt = self._peek()
                if nxt is not None and nxt.indent > indent and nxt.indent != indent + 2:
                    self._err(nxt.lineno, "unexpected indentation")
                items.append(item)
            else:
                self.i += 1
                items.append(self._scalar(content, tok.lineno))
        tok = self._peek()
        if tok is not None and tok.indent > indent:
            self._err(tok.lineno, "unexpected indentation")
        return items

    def _inline_value(self, rest: str, child_depth: int, lineno: int):
        rest = rest.strip()
        if rest.startswith("{") or rest.startswith("["):
            return self._flow(rest, child_depth, lineno)
        return self._scalar(rest, lineno)

    # ── single-line flow shorthand ──

    def _flow(self, s: str, child_depth: int, lineno: int):
        value, pos = self._flow_value(s, 0, child_depth, lineno)
        if s[pos:].strip():
            self._err(lineno, f"trailing content after flow value: {s[pos:].strip()!r}")
        return value

    def _flow_value(self, s: str, pos: int, child_depth: int, lineno: int):
        while pos < len(s) and s[pos] == " ":
            pos += 1
        if pos >= len(s):
            self._err(lineno, "unterminated flow value")
        ch = s[pos]
        if ch == "{":
            return self._flow_mapping(s, pos, child_depth, lineno)
        if ch == "[":
            return self._flow_list(s, pos, child_depth, lineno)
        if ch in ("'", '"'):
            end = s.find(ch, pos + 1)
            if end == -1:
                self._err(lineno, "unterminated quoted string in flow value")
            return s[pos + 1 : end], end + 1
        end = pos
        while end < len(s) and s[end] not in ",}]":
            end += 1
        return self._scalar(s[pos:end].strip(), lineno), end

    def _flow_mapping(self, s: str, pos: int, child_depth: int, lineno: int):
        self._depth_guard(child_depth, lineno, "flow mapping")
        result: dict = {}
        pos += 1  # consume '{'
        while True:
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == "}":
                return result, pos + 1
            colon = s.find(":", pos)
            if colon == -1:
                self._err(lineno, "flow mapping entry missing ':'")
            key = s[pos:colon].strip()
            if not _FLOW_KEY_RE.fullmatch(key):
                self._err(lineno, f"invalid flow mapping key: {key!r}")
            if key in result:
                self._err(lineno, f"duplicate key: {key!r}")
            value, pos = self._flow_value(s, colon + 1, child_depth + 1, lineno)
            result[key] = value
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos >= len(s):
                self._err(lineno, "unterminated flow mapping")
            if s[pos] == ",":
                pos += 1
                continue
            if s[pos] == "}":
                return result, pos + 1
            self._err(lineno, f"unexpected character in flow mapping: {s[pos]!r}")

    def _flow_list(self, s: str, pos: int, child_depth: int, lineno: int):
        items: list = []
        pos += 1  # consume '['
        while True:
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == "]":
                return items, pos + 1
            value, pos = self._flow_value(s, pos, child_depth, lineno)
            items.append(value)
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos >= len(s):
                self._err(lineno, "unterminated flow list")
            if s[pos] == ",":
                pos += 1
                continue
            if s[pos] == "]":
                return items, pos + 1
            self._err(lineno, f"unexpected character in flow list: {s[pos]!r}")

    def _scalar(self, text: str, lineno: int):
        t = text.strip()
        if not t:
            self._err(lineno, "empty scalar")
        if t[0] in ("'", '"'):
            if len(t) < 2 or not t.endswith(t[0]) or t[0] in t[1:-1]:
                self._err(lineno, f"malformed quoted string: {t!r}")
            return t[1:-1]
        if t.startswith("&") or t.startswith("*"):
            self._err(lineno, f"anchor/alias rejected (fail-closed loader): {t!r}")
        if t.startswith("!"):
            self._err(lineno, f"tag rejected (fail-closed loader): {t!r}")
        if t.startswith("|") or t.startswith(">"):
            self._err(lineno, f"block scalar rejected (fail-closed loader): {t!r}")
        if t == "null":
            return None
        if t == "true":
            return True
        if t == "false":
            return False
        if _INT_RE.match(t):
            return int(t)
        if ": " in t:
            self._err(lineno, f"ambiguous unquoted scalar containing ': ' -- quote it: {t!r}")
        return t


def parse_strict_yaml(text: str, max_depth: int = 4) -> dict:
    """Parse the accepted subset. Raises RegistryError; never partial data."""
    try:
        return _Parser(_tokenize(text), max_depth).parse_document()
    except _ParseError as exc:
        raise RegistryError([str(exc)]) from None


# ═══════════════════════════════════════════════════════════════════════
# 2. Selector grammar and specificity
# ═══════════════════════════════════════════════════════════════════════
#
# The grammar is a frozen minimal set of six shapes:
#
#   docs/guide.md   exact       one file
#   docs/           direct      files directly inside docs, no deeper
#   docs/**         subtree     every file at any depth below docs
#   *               root        files sitting directly at the repository root
#   docs/*          single      one path segment below docs (same reach as
#                               `direct`, kept as a separate spelling because
#                               it reads as a glob and is scored lower)
#   **/name/**      anysub      any directory called `name`, at any depth
#
# Anything else -- character classes, partial-segment globs, leading slashes --
# is a compile error. A grammar that grows on demand cannot keep a total
# specificity order, and without a total order ties become silent.
#
# Specificity is the triple (exactness, literal segment count, -wildcards),
# compared lexicographically. Exact beats everything; among globs, the longer
# literal prefix wins; among equals, fewer wildcards wins. Two declarations
# that tie are an error at resolution time, never a first-one-wins.


@dataclass(frozen=True)
class Selector:
    pattern: str
    kind: str  # exact | direct | subtree | root | single | anysub
    base: str  # literal prefix directory ('' when there is none)
    spec: tuple[int, int, int]

    def match(self, path: str) -> bool:
        if self.kind == "exact":
            return path == self.pattern
        if self.kind == "subtree":
            return path.startswith(self.base + "/")
        if self.kind in ("direct", "single"):
            prefix = self.base + "/"
            return path.startswith(prefix) and "/" not in path[len(prefix) :]
        if self.kind == "root":
            return "/" not in path
        if self.kind == "anysub":
            return self.base in path.split("/")[:-1]
        return False


_FORBIDDEN_CHARS = set("[]{}?\\!&<>|\t")


def compile_selector(pattern: Any) -> Selector:
    """Compile one selector of the frozen set; raise on anything outside it."""
    if not isinstance(pattern, str) or not pattern:
        raise _ParseError(f"selector must be a non-empty string: {pattern!r}")
    if any(ch in _FORBIDDEN_CHARS for ch in pattern):
        raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
    if pattern.startswith("/") or "//" in pattern:
        raise _ParseError(f"invalid selector path: {pattern!r}")
    if pattern == "*":
        return Selector(pattern, "root", "", (1, 0, -1))
    if pattern in ("**", "**/"):
        raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
    segs = pattern.split("/")
    if len(segs) == 3 and segs[0] == "**" and segs[2] == "**" and segs[1] and "*" not in segs[1]:
        return Selector(pattern, "anysub", segs[1], (1, 0, -4))
    if pattern.endswith("/**"):
        base = pattern[:-3]
        if not base or "*" in base:
            raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
        return Selector(pattern, "subtree", base, (1, len(base.split("/")), -2))
    if pattern.endswith("/*"):
        base = pattern[:-2]
        if not base or "*" in base:
            raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
        return Selector(pattern, "single", base, (1, len(base.split("/")), -1))
    if pattern.endswith("/"):
        base = pattern[:-1]
        if not base or "*" in base:
            raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
        return Selector(pattern, "direct", base, (1, len(base.split("/")), 0))
    if "*" in pattern:
        raise _ParseError(f"selector uses a shape outside the frozen set: {pattern!r}")
    if any(not s for s in segs):
        raise _ParseError(f"invalid selector path: {pattern!r}")
    return Selector(pattern, "exact", pattern, (2, 1_000_000, 0))


def _containment_error(parent: Selector, child: Selector) -> str | None:
    """Explain why `child` is not a legal override of `parent`, or return None.

    Checked per parent kind rather than by probing with a synthetic path: a
    probe answers 'no' for the root and any-depth kinds too, but for the wrong
    reason, and the resulting message sends the reader hunting for a typo that
    is not there.
    """
    if parent.kind == "exact":
        return "an exact-file selector owns a single file and cannot carry overrides"
    if parent.kind == "anysub":
        return "an any-depth selector has no fixed base and cannot carry overrides"
    if parent.kind == "root":
        if child.kind == "exact" and "/" not in child.pattern:
            return None
        return "an override of the root selector must be an exact file at the root"
    if parent.kind in ("direct", "single"):
        prefix = parent.base + "/"
        if child.kind == "exact" and child.pattern.startswith(prefix):
            if "/" not in child.pattern[len(prefix) :]:
                return None
            return f"selector reaches below the direct children of {parent.base!r}"
        return f"an override of {parent.pattern!r} must be an exact file directly inside it"
    # parent.kind == "subtree"
    #
    # Containment is about the SET of paths, not about a shared prefix string.
    # A single-segment or any-depth selector matches a directory name wherever it
    # occurs, so it reaches outside the parent subtree no matter what its base
    # looks like. Accepting one on a base-string comparison let a selector that
    # the parent does not own inherit the parent's override -- an adversarial
    # review took a disposition that way.
    # Reject by kind only where the kind itself reaches outside any fixed base:
    # an any-depth selector has no base to compare, and a root selector is about
    # the repository root rather than this subtree. A direct or single selector
    # does have a fixed base and can be judged on it -- rejecting those outright
    # was an over-correction that refused legitimate overrides such as `docs/`
    # or `docs/internal/*` under a `docs/**` parent.
    if child.kind in ("anysub", "root"):
        return (
            f"a {child.kind!r} selector has no fixed base inside {parent.base!r} "
            "and cannot be an override of it"
        )
    if child.kind == "exact":
        # An exact file must sit strictly below the parent base; the base itself
        # is a directory, so an exact selector equal to it is malformed.
        if child.pattern.startswith(parent.base + "/"):
            return None
        return f"selector is not contained in the subtree {parent.base!r}"
    # direct, single, subtree: the base must be the parent base or below it.
    if child.base == parent.base or child.base.startswith(parent.base + "/"):
        return None
    return f"selector is not contained in the subtree {parent.base!r}"


# ═══════════════════════════════════════════════════════════════════════
# 3. Injected schema
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class RegistrySchema:
    """The project vocabulary the engine validates against.

    Every field is supplied by the adopting project. An empty tuple for an
    enum field means 'not constrained here' -- the value must still be a
    non-empty string, but the engine does not police its membership. That is
    the escape hatch for a project that validates a field itself; it is not a
    default anybody should reach for without deciding to.
    """

    roles: tuple[str, ...] = ()
    dispositions: tuple[str, ...] = ()
    required_declaration_keys: tuple[str, ...] = ("select", "disposition")
    optional_declaration_keys: tuple[str, ...] = ("role", "note", "overrides")
    extra_top_level_keys: tuple[str, ...] = ()
    required_extra_top_level_keys: tuple[str, ...] = ()
    declaration_field_enums: tuple[tuple[str, tuple[str, ...]], ...] = ()
    require_exclusions: bool = False
    max_key_depth: int = 4

    def __post_init__(self) -> None:
        if "select" not in self.required_declaration_keys:
            raise ValueError("'select' must be a required declaration key")
        if "overrides" in self.required_declaration_keys:
            raise ValueError("'overrides' is optional by nature; do not require it")
        overlap = set(self.required_declaration_keys) & set(self.optional_declaration_keys)
        if overlap:
            raise ValueError(f"keys are both required and optional: {sorted(overlap)}")
        reserved = {"schema_version", "declarations", "exclusions"}
        extra = set(self.extra_top_level_keys)
        required_extra = set(self.required_extra_top_level_keys)
        clash = reserved & (extra | required_extra)
        if clash:
            raise ValueError(f"extra top-level keys clash with engine keys: {sorted(clash)}")
        overlap = extra & required_extra
        if overlap:
            raise ValueError(f"extra top-level keys are both required and optional: {sorted(overlap)}")
        enum_fields: set[str] = set()
        declaration_keys = set(self.declaration_keys)
        for field_name, allowed in self.declaration_field_enums:
            if field_name in enum_fields:
                raise ValueError(f"duplicate declaration enum field: {field_name!r}")
            if field_name not in declaration_keys:
                raise ValueError(f"declaration enum field is not in the closed declaration shape: {field_name!r}")
            if not allowed or any(not isinstance(value, str) or not value for value in allowed):
                raise ValueError(f"declaration enum field has invalid allowed values: {field_name!r}")
            enum_fields.add(field_name)

    @property
    def declaration_keys(self) -> tuple[str, ...]:
        return tuple(self.required_declaration_keys) + tuple(self.optional_declaration_keys)


PERMISSIVE_SCHEMA = RegistrySchema()
"""A schema that constrains structure but not vocabulary.

The standalone command line has no way to know a project's enums, so it loads
registries with this. It is a deliberate weakening, not the intended mode: an
embedding project should pass its own schema so that a typo in a role or a
disposition fails at load instead of travelling downstream.
"""


# ═══════════════════════════════════════════════════════════════════════
# 4. Object model
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class Declaration:
    origin: str  # "declaration" | "override" | "exclusion" | anything a caller adds
    label: str
    selector: Selector
    disposition: Any = None  # None means: inherit from parent
    role: str | None = None
    parent: "Declaration | None" = None
    data: dict = field(default_factory=dict)

    def effective_disposition(self) -> Any:
        decl: Declaration | None = self
        while decl is not None:
            if decl.disposition is not None:
                return decl.disposition
            decl = decl.parent
        return None


@dataclass(frozen=True)
class PathVerdict:
    """The answer for one path. `status` is DECLARED, EXCLUDED or UNDECLARED.

    These three are kept apart on purpose. Collapsing them into one nullable
    answer is how 'nobody declared this path' comes to look like 'this path is
    deliberately out of scope'.
    """

    path: str
    status: str
    declaration: Declaration | None = None
    disposition: Any = None


@dataclass(frozen=True)
class PathIssue:
    path: str
    kind: str  # "undeclared" | "ambiguous"
    message: str


class Registry:
    def __init__(
        self,
        schema: RegistrySchema,
        declarations: list[Declaration],
        document: dict,
    ) -> None:
        self.schema = schema
        self.declarations = declarations
        self.document = document
        self.schema_version: int = document["schema_version"]
        self._patterns = {d.selector.pattern for d in declarations}

    # ── extension ──

    @property
    def extra(self) -> dict:
        """Top-level blocks the engine does not interpret, keyed as written.

        A project with its own blocks validates them itself and feeds the
        resulting declarations back through `extend`, which keeps them inside
        the same resolution and the same duplicate check.
        """
        engine_keys = {"schema_version", "declarations", "exclusions"}
        return {k: v for k, v in self.document.items() if k not in engine_keys}

    def extend(self, declarations: Iterable[Declaration]) -> None:
        errors: list[str] = []
        added: list[Declaration] = []
        # Both against what is already registered and against this batch: the
        # pre-existing set is not updated until the loop ends, so two identical
        # selectors arriving in one call used to pass and produce two winners
        # for the same path.
        batch: set[str] = set()
        for decl in declarations:
            pattern = decl.selector.pattern
            if pattern in self._patterns or pattern in batch:
                errors.append(
                    f"duplicate selector {pattern!r} added by {decl.label}"
                )
                continue
            batch.add(pattern)
            added.append(decl)
        if errors:
            raise RegistryError(errors)
        for decl in added:
            self._patterns.add(decl.selector.pattern)
            self.declarations.append(decl)

    # ── resolution ──

    def resolve(self, path: str) -> list[Declaration]:
        """Every best-specificity declaration matching `path` (0, 1, or a tie)."""
        matches = [d for d in self.declarations if d.selector.match(path)]
        if not matches:
            return []
        best = max(d.selector.spec for d in matches)
        return [d for d in matches if d.selector.spec == best]

    def resolve_one(self, path: str) -> Declaration | None:
        """The single owning declaration, None if undeclared; tie raises."""
        winners = self.resolve(path)
        if not winners:
            return None
        if len(winners) > 1:
            raise AmbiguousPathError(path, [d.label for d in winners])
        return winners[0]

    def verdict(self, path: str) -> PathVerdict:
        decl = self.resolve_one(path)
        if decl is None:
            return PathVerdict(path, UNDECLARED)
        if decl.origin == "exclusion":
            return PathVerdict(path, EXCLUDED, decl)
        return PathVerdict(path, DECLARED, decl, decl.effective_disposition())

    def disposition_of(self, path: str) -> Any:
        """Effective disposition of a declared path.

        Raises for an undeclared path and for a tie; returns None for an
        excluded path, which is the one case where 'no disposition' is a real
        answer rather than a hole.
        """
        verdict = self.verdict(path)
        if verdict.status == UNDECLARED:
            raise KeyError(f"undeclared path: {path}")
        return verdict.disposition

    def is_excluded(self, path: str) -> bool:
        return self.verdict(path).status == EXCLUDED

    # ── bulk audit ──

    def audit(self, paths: Iterable[str]) -> list[PathIssue]:
        """Report undeclared and ambiguous paths without raising on the first.

        Attribution reads the path only. A file cannot exempt itself by
        containing a marker, because then the check would be asking the
        suspect for its alibi.
        """
        issues: list[PathIssue] = []
        for path in paths:
            winners = self.resolve(path)
            if not winners:
                issues.append(PathIssue(path, "undeclared", f"undeclared path (tracked or untracked-and-not-ignored): {path}"))
            elif len(winners) > 1:
                labels = ", ".join(sorted(d.label for d in winners))
                issues.append(
                    PathIssue(
                        path,
                        "ambiguous",
                        f"ambiguous attribution (equal specificity): {path} -> {labels}",
                    )
                )
        return issues


# ═══════════════════════════════════════════════════════════════════════
# 5. Validation and loading
# ═══════════════════════════════════════════════════════════════════════


def _check_keys(
    errors: list[str],
    ctx: str,
    mapping: Any,
    required: Sequence[str],
    optional: Sequence[str] = (),
) -> bool:
    if not isinstance(mapping, dict):
        errors.append(f"{ctx}: expected a mapping")
        return False
    ok = True
    for key in required:
        if key not in mapping:
            errors.append(f"{ctx}: missing required key {key!r}")
            ok = False
    for key in mapping:
        if key not in required and key not in optional:
            errors.append(f"{ctx}: unknown key {key!r} (closed shape)")
            ok = False
    return ok


def _check_enum(errors: list[str], ctx: str, field_name: str, value: Any, allowed: Sequence[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{ctx}: {field_name} must be a non-empty string, got {value!r}")
        return
    if allowed and value not in allowed:
        errors.append(f"{ctx}: unknown {field_name} {value!r} (allowed: {tuple(allowed)})")


def _selector_or_error(errors: list[str], ctx: str, pattern: Any) -> Selector | None:
    try:
        return compile_selector(pattern)
    except _ParseError as exc:
        errors.append(f"{ctx}: {exc}")
        return None


def _validate(doc: Any, schema: RegistrySchema) -> Registry:
    errors: list[str] = []
    if not isinstance(doc, dict):
        raise RegistryError(["registry root must be a mapping"])

    top_required = ["schema_version", "declarations", *schema.required_extra_top_level_keys]
    if schema.require_exclusions:
        top_required.append("exclusions")
    top_optional = ["exclusions", *schema.extra_top_level_keys]
    for key in top_required:
        if key not in doc:
            errors.append(f"missing required top-level key {key!r}")
    for key in doc:
        if key not in top_required and key not in top_optional:
            errors.append(f"unknown top-level key {key!r} (closed shape)")
    if errors:
        raise RegistryError(errors)

    version = doc["schema_version"]
    if not isinstance(version, int) or isinstance(version, bool):
        errors.append("schema_version must be an integer")

    declarations: list[Declaration] = []
    seen_patterns: dict[str, str] = {}

    def register(decl: Declaration) -> None:
        prev = seen_patterns.get(decl.selector.pattern)
        if prev is not None:
            errors.append(
                f"duplicate selector {decl.selector.pattern!r} declared by both "
                f"{prev} and {decl.label} (ambiguous attribution)"
            )
        else:
            seen_patterns[decl.selector.pattern] = decl.label
        declarations.append(decl)

    entries = doc["declarations"]
    if not isinstance(entries, list) or not entries:
        errors.append("declarations must be a non-empty list")
        entries = []

    override_optional = tuple(
        k for k in schema.declaration_keys if k not in ("select", "overrides")
    )

    for idx, entry in enumerate(entries):
        ctx = f"declarations[{idx}]"
        if not _check_keys(
            errors,
            ctx,
            entry,
            schema.required_declaration_keys,
            schema.optional_declaration_keys,
        ):
            continue
        selector = _selector_or_error(errors, ctx, entry["select"])
        ctx = f"declaration {entry['select']!r}"
        if "disposition" in entry:
            _check_enum(errors, ctx, "disposition", entry["disposition"], schema.dispositions)
        if "role" in entry:
            _check_enum(errors, ctx, "role", entry["role"], schema.roles)
        for field_name, allowed in schema.declaration_field_enums:
            if field_name in entry:
                _check_enum(errors, ctx, field_name, entry[field_name], allowed)
        if selector is None:
            continue
        parent_decl = Declaration(
            origin="declaration",
            label=f"declaration:{entry['select']}",
            selector=selector,
            disposition=entry.get("disposition"),
            role=entry.get("role"),
            data=dict(entry),
        )
        register(parent_decl)

        overrides = entry.get("overrides") or []
        if not isinstance(overrides, list):
            errors.append(f"{ctx}: overrides must be a list")
            continue
        for override in overrides:
            octx = f"{ctx} override"
            if not _check_keys(errors, octx, override, ("select",), override_optional):
                continue
            osel = _selector_or_error(errors, octx, override["select"])
            if osel is None:
                continue
            octx = f"{ctx} override {override['select']!r}"
            if "disposition" in override:
                _check_enum(errors, octx, "disposition", override["disposition"], schema.dispositions)
            if "role" in override:
                _check_enum(errors, octx, "role", override["role"], schema.roles)
            for field_name, allowed in schema.declaration_field_enums:
                if field_name in override:
                    _check_enum(errors, octx, field_name, override[field_name], allowed)
            # An override must be strictly narrower than its parent and lie
            # inside it. Both halves matter: a wider override would shadow the
            # parent everywhere, and one pointing outside would silently claim
            # paths the parent never owned.
            if not osel.spec > selector.spec:
                errors.append(
                    f"{octx}: is not strictly more specific than {entry['select']!r}"
                )
            reason = _containment_error(selector, osel)
            if reason is not None:
                errors.append(f"{octx}: {reason}")
            register(
                Declaration(
                    origin="override",
                    label=f"override:{override['select']} (of {entry['select']})",
                    selector=osel,
                    disposition=override.get("disposition"),
                    role=override.get("role"),
                    parent=parent_decl,
                    data=dict(override),
                )
            )

    exclusions = doc.get("exclusions", [])
    if schema.require_exclusions and (not isinstance(exclusions, list) or not exclusions):
        errors.append("exclusions must be a non-empty list under this schema")
        exclusions = []
    if not isinstance(exclusions, list):
        errors.append("exclusions must be a list")
        exclusions = []
    for exclusion in exclusions:
        ctx = "exclusions[]"
        if not _check_keys(errors, ctx, exclusion, ("select", "reason")):
            continue
        sel = _selector_or_error(errors, f"exclusion {exclusion['select']!r}", exclusion["select"])
        if sel is None:
            continue
        # A reason is required because an exclusion is the one declaration that
        # turns a check off, and an unexplained silenced check is indefensible
        # a year later.
        if not isinstance(exclusion["reason"], str) or not exclusion["reason"].strip():
            errors.append(f"exclusion {exclusion['select']!r}: reason must be a non-empty string")
        register(
            Declaration(
                origin="exclusion",
                label=f"exclusion:{exclusion['select']}",
                selector=sel,
                data=dict(exclusion),
            )
        )

    if errors:
        raise RegistryError(errors)
    return Registry(schema, declarations, doc)


def load_registry(source: Path | str, schema: RegistrySchema = PERMISSIVE_SCHEMA) -> Registry:
    """Load and validate a registry from a path or from document text.

    Fail-closed: any parse or schema violation raises RegistryError carrying
    every collected message, and no partial registry is returned.
    """
    if isinstance(source, Path):
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            raise RegistryError([f"cannot read registry: {exc}"]) from None
    else:
        text = source
    return _validate(parse_strict_yaml(text, schema.max_key_depth), schema)

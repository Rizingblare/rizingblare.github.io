#!/usr/bin/env python3
"""Repository validator: one entry point, one exit code, project-neutral checks.

This is the shell a repository gate runs. It sweeps every tracked path once,
applies a closed series of checks that hold for any repository, and reports in
a single format with a single exit code. Everything specific to a project --
its file schemas, its naming rules, its vocabulary -- arrives through the
plugin hook rather than living here.

The checks carried here are the ones that are true everywhere:

    scan-source       the path universe could actually be enumerated
    worktree-clean    no uncommitted changes
    merge-conflict    no unmerged index entries and no leftover conflict text
    os-metadata       no tracked operating-system junk files
    temp-file         no tracked scratch or backup files (a heuristic)
    marker-integrity  generated-region markers are well formed
    empty-state       nothing that reports on a collection reports nothing
    undeclared-path   every tracked path is owned by the structure registry

Every check defaults to error severity. A gate whose findings default to
advisory teaches people to scroll past it. A few ids may be demoted to warning
by the operator; the rest are listed in NON_DEMOTABLE and refuse demotion at
configuration time rather than ignoring it at run time.

Exit codes: 0 clean, 1 findings, 2 usage or configuration error.
"""

from __future__ import annotations

import argparse
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

# The two sibling modules are imported by bare name. Running this file as a
# script already puts its own directory first on the import path, and an
# embedding project puts the engine directory there to import this module at
# all. Inserting the path here instead would claim the very generic names
# `registry` and `markers` for the whole process, which is not this module's
# to decide.
import markers as markers_engine
import registry as registry_engine

__all__ = [
    "CHECK_IDS",
    "NON_DEMOTABLE",
    "Finding",
    "Check",
    "Context",
    "Plugin",
    "Validator",
    "main",
]


# ── the closed series ────────────────────────────────────────────────────────

CHECK_SCAN_SOURCE = "scan-source"
CHECK_WORKTREE_CLEAN = "worktree-clean"
CHECK_MERGE_CONFLICT = "merge-conflict"
CHECK_OS_METADATA = "os-metadata"
CHECK_TEMP_FILE = "temp-file"
CHECK_MARKER_INTEGRITY = "marker-integrity"
CHECK_EMPTY_STATE = "empty-state"
CHECK_UNDECLARED_PATH = "undeclared-path"

CHECK_IDS: tuple[str, ...] = (
    CHECK_SCAN_SOURCE,
    CHECK_WORKTREE_CLEAN,
    CHECK_MERGE_CONFLICT,
    CHECK_OS_METADATA,
    CHECK_TEMP_FILE,
    CHECK_MARKER_INTEGRITY,
    CHECK_EMPTY_STATE,
    CHECK_UNDECLARED_PATH,
)

# Demoting any of these would defeat the reason the check exists: each one
# reports a state in which the rest of the report cannot be trusted, or a
# defect that is invisible to a reader until it causes damage.
NON_DEMOTABLE: frozenset[str] = frozenset(
    {
        CHECK_SCAN_SOURCE,
        CHECK_MERGE_CONFLICT,
        CHECK_OS_METADATA,
        CHECK_MARKER_INTEGRITY,
        CHECK_EMPTY_STATE,
        CHECK_UNDECLARED_PATH,
    }
)

# `worktree-clean` and `temp-file` stay demotable: a dirty tree is the normal
# state during development, and the scratch-file rule is a name heuristic that
# a project may legitimately outgrow.

ERROR = "error"
WARN = "warn"


# ── default scan scope ───────────────────────────────────────────────────────

# Marker scanning defaults to prose documents. Source files routinely discuss
# markers in comments and examples, and flagging those would train people to
# ignore the check that exists to catch a mistyped marker.
DEFAULT_MARKER_SUFFIXES = (".md", ".markdown", ".txt", ".rst")

OS_METADATA_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
OS_METADATA_PARTS = ("__MACOSX",)

_TEMP_DIR_RE = re.compile(r"(^|/)(tmp|temp|\.tmp)(/|$)")
_TEMP_SUFFIXES = (".tmp", ".bak", ".orig", ".swp", ".rej")

# Only the labelled open and close lines are matched. The bare seven-equals
# separator is left alone because an underlined heading produces the same run,
# and a check that fires on ordinary documents stops being read.
_CONFLICT_RE = re.compile(r"^(<{7}|>{7}) \S")
_CONFLICT_SUFFIX_SKIP = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2")


# ── data model ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Finding:
    check_id: str
    message: str
    path: str = ""


@dataclass(frozen=True)
class Check:
    check_id: str
    run: Callable[["Context"], Iterable[Finding]]


@dataclass
class Context:
    root: Path
    tracked: list[str]
    registry: "registry_engine.Registry | None" = None
    marker_syntax: markers_engine.MarkerSyntax = markers_engine.DEFAULT_SYNTAX
    marker_suffixes: tuple[str, ...] = DEFAULT_MARKER_SUFFIXES
    git_available: bool = True
    git_error: str = ""
    _text_cache: dict = field(default_factory=dict, repr=False)

    def read_text(self, relpath: str) -> str | None:
        """File contents as text, or None when unreadable or not text."""
        if relpath in self._text_cache:
            return self._text_cache[relpath]
        try:
            text = (self.root / relpath).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            text = None
        self._text_cache[relpath] = text
        return text


@dataclass(frozen=True)
class Plugin:
    """What an adopting project contributes.

    One injection point on purpose: the project-specific checks, the registry
    vocabulary they assume and the marker spelling they read all travel
    together, so a plugin cannot be loaded with checks that expect enums the
    loader was never told about.
    """

    checks: tuple[Check, ...] = ()
    registry_schema: "registry_engine.RegistrySchema | None" = None
    marker_syntax: "markers_engine.MarkerSyntax | None" = None


class ConfigError(Exception):
    """Raised for an unusable configuration; reported before any check runs."""


# ── git access ───────────────────────────────────────────────────────────────


def _git(root: Path, args: Sequence[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout, proc.stderr


def build_context(
    root: Path,
    registry: "registry_engine.Registry | None" = None,
    marker_suffixes: Sequence[str] = DEFAULT_MARKER_SUFFIXES,
    marker_syntax: "markers_engine.MarkerSyntax | None" = None,
) -> Context:
    """Enumerate the path universe: tracked files plus untracked-not-ignored files.

    An enumeration failure is recorded rather than papered over. Returning an
    empty list on a git error would make every path-based check pass on a
    repository the validator never actually read.
    """
    code, out, err = _git(root, ["-c", "core.quotePath=false", "ls-files"])
    common = {
        "root": root,
        "registry": registry,
        "marker_suffixes": tuple(marker_suffixes),
        "marker_syntax": marker_syntax or markers_engine.DEFAULT_SYNTAX,
    }
    if code != 0:
        detail = (err or "git command failed").strip().splitlines()
        return Context(
            tracked=[],
            git_available=False,
            git_error=detail[0] if detail else "git command failed",
            **common,
        )
    universe = [line for line in out.splitlines() if line]

    # Untracked-but-not-ignored files join the universe.
    #
    # `ls-files` alone reads the index, so a file that exists on disk but has not
    # been staged is invisible here. That is a fail-open: the undeclared-path
    # check reports nothing, the run exits green, and the author concludes the
    # new directory is declared when it has never been looked at. The failure is
    # silent in the worst way — a passing gate that checked an empty set.
    #
    # Ignored files stay out: they are the declared untracked axis, and the
    # registry's exclusions already speak for them.
    code, others, _ = _git(
        root, ["-c", "core.quotePath=false", "ls-files", "--others", "--exclude-standard"]
    )
    if code == 0:
        seen = set(universe)
        universe.extend(
            line for line in others.splitlines() if line and line not in seen
        )

    return Context(tracked=universe, **common)


# ── the checks ───────────────────────────────────────────────────────────────


def check_scan_source(ctx: Context) -> list[Finding]:
    if ctx.git_available:
        return []
    return [
        Finding(
            CHECK_SCAN_SOURCE,
            "cannot enumerate tracked paths -- not a git repository, or git is "
            f"unavailable ({ctx.git_error}); no path-based check below ran",
        )
    ]


def check_worktree_clean(ctx: Context) -> list[Finding]:
    if not ctx.git_available:
        return []
    code, status, _ = _git(ctx.root, ["status", "--short"])
    if code == 0 and status.strip():
        count = len([line for line in status.splitlines() if line.strip()])
        return [Finding(CHECK_WORKTREE_CLEAN, f"working tree has {count} uncommitted change(s)")]
    return []


def check_merge_conflict(ctx: Context) -> list[Finding]:
    findings: list[Finding] = []
    if ctx.git_available:
        code, unmerged, _ = _git(ctx.root, ["ls-files", "-u"])
        if code == 0 and unmerged.strip():
            findings.append(
                Finding(CHECK_MERGE_CONFLICT, "unmerged index entries exist (merge in progress)")
            )
    for relpath in ctx.tracked:
        if relpath.lower().endswith(_CONFLICT_SUFFIX_SKIP):
            continue
        text = ctx.read_text(relpath)
        if text is None:
            continue
        for lineno, line in enumerate(text.split("\n"), start=1):
            if _CONFLICT_RE.match(line):
                findings.append(
                    Finding(
                        CHECK_MERGE_CONFLICT,
                        f"line {lineno}: leftover conflict marker {line.strip()[:16]!r}",
                        relpath,
                    )
                )
                break
    return findings


def check_os_metadata(ctx: Context) -> list[Finding]:
    findings: list[Finding] = []
    for relpath in ctx.tracked:
        name = relpath.rsplit("/", 1)[-1]
        if name in OS_METADATA_NAMES or any(part in relpath for part in OS_METADATA_PARTS):
            findings.append(Finding(CHECK_OS_METADATA, "tracked operating-system metadata", relpath))
    return findings


def check_temp_file(ctx: Context) -> list[Finding]:
    findings: list[Finding] = []
    for relpath in ctx.tracked:
        if _TEMP_DIR_RE.search(relpath) or relpath.endswith(_TEMP_SUFFIXES):
            findings.append(Finding(CHECK_TEMP_FILE, "tracked file looks temporary", relpath))
    return findings


def _marker_targets(ctx: Context) -> list[str]:
    return [p for p in ctx.tracked if p.lower().endswith(tuple(ctx.marker_suffixes))]


def check_marker_integrity(ctx: Context) -> list[Finding]:
    findings: list[Finding] = []
    for relpath in _marker_targets(ctx):
        text = ctx.read_text(relpath)
        if text is None:
            continue
        for issue in markers_engine.check_text(text, ctx.marker_syntax):
            if issue.code == "empty-section":
                continue  # reported by check_empty_state
            findings.append(
                Finding(CHECK_MARKER_INTEGRITY, f"line {issue.lineno}: {issue.message}", relpath)
            )
    return findings


def check_empty_state(ctx: Context) -> list[Finding]:
    """Nothing that reports on a collection may report nothing at all."""
    findings: list[Finding] = []
    if ctx.git_available and not ctx.tracked:
        findings.append(
            Finding(
                CHECK_EMPTY_STATE,
                "the path universe is empty; a validator that validates "
                "nothing must not report success",
            )
        )
    for relpath in _marker_targets(ctx):
        text = ctx.read_text(relpath)
        if text is None:
            continue
        for issue in markers_engine.check_text(text, ctx.marker_syntax):
            if issue.code == "empty-section":
                findings.append(
                    Finding(CHECK_EMPTY_STATE, f"line {issue.lineno}: {issue.message}", relpath)
                )
    return findings


def check_undeclared_path(ctx: Context) -> list[Finding]:
    # With no registry there is nothing to check against. The caller says so
    # out loud (see `main`) rather than letting a run without a registry look
    # like a run that found every path properly declared.
    if ctx.registry is None:
        return []
    return [
        Finding(CHECK_UNDECLARED_PATH, issue.message, issue.path)
        for issue in ctx.registry.audit(ctx.tracked)
    ]


ENGINE_CHECKS: tuple[Check, ...] = (
    Check(CHECK_SCAN_SOURCE, check_scan_source),
    Check(CHECK_WORKTREE_CLEAN, check_worktree_clean),
    Check(CHECK_MERGE_CONFLICT, check_merge_conflict),
    Check(CHECK_OS_METADATA, check_os_metadata),
    Check(CHECK_TEMP_FILE, check_temp_file),
    Check(CHECK_MARKER_INTEGRITY, check_marker_integrity),
    Check(CHECK_EMPTY_STATE, check_empty_state),
    Check(CHECK_UNDECLARED_PATH, check_undeclared_path),
)


# ── runner ───────────────────────────────────────────────────────────────────


class Validator:
    def __init__(
        self,
        checks: Sequence[Check] = ENGINE_CHECKS,
        demotions: Iterable[str] = (),
    ) -> None:
        seen: set[str] = set()
        for check in checks:
            if check.check_id in seen:
                raise ConfigError(f"duplicate check id: {check.check_id}")
            seen.add(check.check_id)
        self.checks = list(checks)
        self.known = seen
        self.demotions: set[str] = set()
        for check_id in demotions:
            if check_id not in self.known:
                raise ConfigError(f"unknown check id cannot be demoted: {check_id}")
            if check_id in NON_DEMOTABLE:
                raise ConfigError(
                    f"check {check_id} refuses demotion to warning; it reports a state "
                    "in which the rest of this report cannot be trusted"
                )
            self.demotions.add(check_id)

    def severity(self, check_id: str) -> str:
        return WARN if check_id in self.demotions else ERROR

    def run(self, ctx: Context) -> tuple[list[str], list[str]]:
        failures: list[str] = []
        warnings: list[str] = []
        for check in self.checks:
            for finding in check.run(ctx):
                where = f" {finding.path}:" if finding.path else ""
                line = f"[{finding.check_id}]{where} {finding.message}"
                if self.severity(finding.check_id) == ERROR:
                    failures.append(line)
                else:
                    warnings.append(line)
        return failures, warnings


def add_plugin_checks(base: Sequence[Check], plugin: Plugin) -> list[Check]:
    """Append plugin checks, refusing any id that collides with the series.

    A plugin that reused an engine id could quietly replace an engine check,
    or make one id mean two things in the same report.
    """
    engine_ids = {c.check_id for c in base}
    out = list(base)
    for check in plugin.checks:
        if check.check_id in engine_ids:
            raise ConfigError(
                f"plugin check id {check.check_id!r} collides with the engine's closed series"
            )
        engine_ids.add(check.check_id)
        out.append(check)
    return out


def load_plugin(spec: str) -> Plugin:
    """Import a plugin given as 'module:attribute'.

    The attribute is a Plugin, or a zero-argument callable returning one. The
    object is accepted by shape rather than by class identity: when this file
    runs as a script the plugin's `import validate` yields a second copy of
    this module, so an identity test would reject a perfectly good plugin for
    a reason nobody could see from the message.
    """
    if ":" not in spec:
        raise ConfigError(f"plugin must be given as 'module:attribute', got {spec!r}")
    module_name, attr_name = spec.split(":", 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ConfigError(f"cannot import plugin module {module_name!r}: {exc}") from None
    try:
        attr = getattr(module, attr_name)
    except AttributeError:
        raise ConfigError(f"plugin module {module_name!r} has no attribute {attr_name!r}") from None
    provided = attr() if callable(attr) else attr
    if not hasattr(provided, "checks"):
        raise ConfigError(f"plugin {spec!r} did not provide a plugin object with `checks`")
    checks: list[Check] = []
    for item in provided.checks:
        if not hasattr(item, "check_id") or not callable(getattr(item, "run", None)):
            raise ConfigError(f"plugin {spec!r} supplied something that is not a check: {item!r}")
        checks.append(Check(str(item.check_id), item.run))
    return Plugin(
        tuple(checks),
        getattr(provided, "registry_schema", None),
        getattr(provided, "marker_syntax", None),
    )


# ── command line ─────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a repository against the project-neutral check series."
    )
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument(
        "--registry",
        default=None,
        help="path to the structure declaration registry; enables undeclared-path",
    )
    parser.add_argument(
        "--plugin",
        default=None,
        help="project checks and registry vocabulary, as 'module:attribute'",
    )
    parser.add_argument(
        "--warn",
        action="append",
        default=[],
        metavar="CHECK_ID",
        help="demote one demotable check to warning (repeatable)",
    )
    parser.add_argument(
        "--marker-suffix",
        action="append",
        default=[],
        metavar="SUFFIX",
        help="file suffix to scan for generated-region markers (repeatable)",
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    return parser


def main(argv: Sequence[str] | None = None, plugin: Plugin | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    root = Path(args.root).resolve()

    try:
        if args.plugin:
            if plugin is not None:
                raise ConfigError("a plugin was both supplied in code and named on the command line")
            plugin = load_plugin(args.plugin)
        plugin = plugin or Plugin()
        checks = add_plugin_checks(ENGINE_CHECKS, plugin)

        loaded_registry = None
        if args.registry:
            schema = plugin.registry_schema or registry_engine.PERMISSIVE_SCHEMA
            loaded_registry = registry_engine.load_registry(Path(args.registry), schema)

        validator = Validator(checks, demotions=args.warn)
    except ConfigError as exc:
        print(f"CONFIG: {exc}", file=sys.stderr)
        return 2
    except registry_engine.RegistryError as exc:
        for message in exc.errors:
            print(f"FAIL: [registry-load] {args.registry}: {message}", file=sys.stderr)
        print(
            f"Validation aborted: registry did not load ({len(exc.errors)} error(s)); "
            "nothing was validated.",
            file=sys.stderr,
        )
        return 1

    suffixes = tuple(args.marker_suffix) or DEFAULT_MARKER_SUFFIXES
    ctx = build_context(
        root,
        registry=loaded_registry,
        marker_suffixes=suffixes,
        marker_syntax=plugin.marker_syntax,
    )
    failures, warnings = validator.run(ctx)

    if loaded_registry is None:
        print(
            f"NOTE: [{CHECK_UNDECLARED_PATH}] no registry was supplied, so this "
            "check did not run; undeclared paths were not looked for"
        )
    for line in warnings:
        print(f"WARN: {line}")
    for line in failures:
        print(f"FAIL: {line}")
    print(f"Validation complete: {len(failures)} failure(s), {len(warnings)} warning(s).")

    if failures:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

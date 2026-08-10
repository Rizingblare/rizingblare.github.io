#!/usr/bin/env python3
"""Project registry schema and the six adopted event-contract checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

if __package__:
    from .catalog_sync_check import PLUGIN as _CATALOG_PLUGIN
    from .engine import registry as registry_engine
else:
    from catalog_sync_check import PLUGIN as _CATALOG_PLUGIN
    from engine import registry as registry_engine


Finding = namedtuple("Finding", "check_id message path")
Check = namedtuple("Check", "check_id run")
Plugin = namedtuple("Plugin", "checks registry_schema non_demotable")

CHECK_EVENT_FRONTMATTER = "event-frontmatter"
CHECK_EVENT_IDENTITY = "event-identity"
CHECK_EVENT_PROTECTED_SPAN = "event-protected-span"
CHECK_EVENT_REFERENCE = "event-reference"
CHECK_EVENT_UNIQUENESS = "event-uniqueness"
CHECK_DECISION_RECEIPT = "decision-receipt"
CHECK_PROJECT_LAYOUT = "project-layout-contract"

_LAYOUT_PATH_VALUES = (
    "not-applicable",
    "AGENTS.md",
    "CLAUDE.md",
    "DESIGN.md",
    "PRODUCT.md",
    "index.html",
    "knowledge/README.md",
    "schema/contracts/README.md",
    "scripts/catalog_sync_check.py",
    "scripts/check.sh",
    "scripts/engine/README.md",
    "scripts/event_check.py",
    "scripts/harness_manifest.py",
    "scripts/public_surface_check.py",
)

REGISTRY_SCHEMA = registry_engine.RegistrySchema(
    roles=("contract", "support", "site", "content"),
    dispositions=("ship", "skip", "stub", "seed"),
    required_declaration_keys=(
        "select",
        "role",
        "disposition",
        "owner",
        "provenance_layer",
        "charter",
        "entry_document",
        "artifact_schema",
        "exposure",
        "exposure_target",
        "producer_gate",
        "exposure_gate",
    ),
    optional_declaration_keys=("note", "overrides"),
    required_extra_top_level_keys=(
        "canonical_contract",
        "project_manifest",
        "language_lint",
    ),
    declaration_field_enums=(
        ("owner", ("harness", "repository-support", "content", "site")),
        (
            "provenance_layer",
            ("operating-contract", "generated-output", "derived-material"),
        ),
        ("charter", _LAYOUT_PATH_VALUES),
        ("entry_document", _LAYOUT_PATH_VALUES),
        ("artifact_schema", _LAYOUT_PATH_VALUES),
        ("exposure", ("repository-only", "public-site")),
        ("exposure_target", ("none", "github-pages")),
        ("producer_gate", ("scripts/check.sh",)),
        (
            "exposure_gate",
            ("not-applicable", "scripts/public_surface_check.py"),
        ),
    ),
    require_exclusions=True,
)

_DIRECT_CATEGORIES = {
    "observations": ("observation", "obs"),
    "feedbacks": ("feedback", "fb"),
    "proposals": ("proposal", "prop"),
    "evaluations": ("evaluation", "eval"),
    "decisions": ("decision", "dec"),
}
_COMMON_FIELDS = {"id", "kind", "form", "created"}
_REQUIRED_FIELDS = {
    "observation": {"unit"},
    "feedback": {"scope", "source_locator", "source_sha256", "source_byte_count"},
    "proposal": {"status", "evidence"},
    "evaluation": {"evaluates", "verdict"},
    "decision": {"status", "gated_by", "targets", "required_checks"},
    "deferred": {"status", "severity"},
}
_OPTIONAL_FIELDS = {
    "observation": set(),
    "feedback": set(),
    "proposal": set(),
    "evaluation": set(),
    "decision": {"verification_receipt", "verification_not_applicable"},
    "deferred": set(),
}
_LIST_FIELDS = {"evidence", "targets", "required_checks"}
_INTEGER_FIELDS = {"source_byte_count"}
_ENUM_FIELDS = {
    ("feedback", "scope"): {"local", "recurring"},
    ("proposal", "status"): {"open", "approved", "rejected", "superseded"},
    ("evaluation", "verdict"): {"pass", "fail", "partial"},
    ("deferred", "status"): {"todo", "done"},
    ("deferred", "severity"): {"blocking", "quality", "polish"},
}
_BEGIN = "<!-- protected span: begin -->"
_END = "<!-- protected span: end -->"


def _effective_declaration_value(declaration, field_name: str) -> Any:
    current = declaration
    while current is not None:
        if field_name in current.data:
            return current.data[field_name]
        current = current.parent
    return None


def _safe_repository_file(root: Path, relpath: Any) -> bool:
    if not isinstance(relpath, str) or not relpath or "\\" in relpath:
        return False
    pure = PurePosixPath(relpath)
    if pure.is_absolute() or pure.as_posix() != relpath or any(part in {"", ".", ".."} for part in pure.parts):
        return False
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return candidate.is_file()


def registry_contract_errors(root: Path, registry) -> list[str]:
    errors: list[str] = []
    path_fields = (
        "charter",
        "entry_document",
        "artifact_schema",
        "producer_gate",
        "exposure_gate",
    )
    for declaration in registry.declarations:
        if declaration.origin == "exclusion":
            continue
        for field_name in path_fields:
            value = _effective_declaration_value(declaration, field_name)
            if value != "not-applicable" and not _safe_repository_file(root, value):
                errors.append(f"{declaration.label}: {field_name} is not a repository file: {value!r}")
        exposure = _effective_declaration_value(declaration, "exposure")
        target = _effective_declaration_value(declaration, "exposure_target")
        gate = _effective_declaration_value(declaration, "exposure_gate")
        role = declaration.role
        current = declaration.parent
        while role is None and current is not None:
            role = current.role
            current = current.parent
        if exposure == "public-site":
            if role != "site" or target != "github-pages" or gate != "scripts/public_surface_check.py":
                errors.append(f"{declaration.label}: public-site exposure requires site role, github-pages target, and public surface gate")
        elif target != "none" or gate != "not-applicable":
            errors.append(f"{declaration.label}: repository-only exposure requires target none and no exposure gate")

    language_lint = registry.document.get("language_lint")
    if not isinstance(language_lint, dict) or set(language_lint) != {"check", "coverage", "outside_coverage"}:
        errors.append("language_lint must have exactly check, coverage, and outside_coverage")
        return errors
    if language_lint.get("check") != "scripts/harness_manifest.py":
        errors.append("language_lint.check must be scripts/harness_manifest.py")
    if language_lint.get("outside_coverage") != "contract-policy-only":
        errors.append("language_lint.outside_coverage must be contract-policy-only")
    coverage = language_lint.get("coverage")
    if (
        not isinstance(coverage, list)
        or not coverage
        or any(not isinstance(path, str) for path in coverage)
        or coverage != sorted(set(coverage))
    ):
        errors.append("language_lint.coverage must be a non-empty sorted unique path list")
        return errors
    for relpath in coverage:
        if not _safe_repository_file(root, relpath):
            errors.append(f"language_lint.coverage path is not a repository file: {relpath!r}")
            continue
        winners = registry.resolve(relpath)
        if len(winners) != 1:
            errors.append(f"language_lint.coverage path must resolve exactly once: {relpath!r}")
    return errors


def check_project_layout(ctx):
    if ctx.registry is None:
        return []
    return [
        Finding(CHECK_PROJECT_LAYOUT, message, "schema/kernel/layout.yaml")
        for message in registry_contract_errors(ctx.root, ctx.registry)
    ]


@dataclass(frozen=True)
class EventRecord:
    path: str
    category: str
    prefix: str
    fields: dict[str, Any]
    body: str
    parse_errors: tuple[str, ...]


@dataclass(frozen=True)
class IssuedChange:
    status: str
    source_path: str
    candidate_path: str | None


def _event_category(path: str) -> tuple[str, str] | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 3
        and parts[0] == "schema"
        and parts[2].endswith(".md")
        and parts[2] not in {"README.md", "INDEX.md"}
    ):
        return _DIRECT_CATEGORIES.get(parts[1])
    if (
        len(parts) == 4
        and parts[:2] == ("schema", "defers")
        and parts[2] in {"_todo", "done"}
        and parts[3].endswith(".md")
        and parts[3] not in {"README.md", "INDEX.md"}
    ):
        return "deferred", "def"
    return None


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, tuple[str, ...]]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return {}, text, ("frontmatter must start on the first line",)
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if closing is None:
        return {}, text, ("frontmatter has no closing delimiter",)
    try:
        fields = registry_engine.parse_strict_yaml("".join(lines[1:closing]))
    except registry_engine.RegistryError as exc:
        return {}, "".join(lines[closing + 1 :]), tuple(exc.errors)
    return fields, "".join(lines[closing + 1 :]), ()


def _records(ctx) -> list[EventRecord]:
    records: list[EventRecord] = []
    for path in ctx.tracked:
        event_type = _event_category(path)
        if event_type is None:
            continue
        text = ctx.read_text(path)
        if text is None:
            records.append(EventRecord(path, *event_type, {}, "", ("record is not UTF-8 text",)))
            continue
        fields, body, errors = _parse_frontmatter(text)
        records.append(EventRecord(path, *event_type, fields, body, errors))
    return records


def _scalar(record: EventRecord, key: str) -> str:
    value = record.fields.get(key)
    return value if isinstance(value, str) else ""


def _index(records: list[EventRecord]) -> dict[str, list[EventRecord]]:
    index: dict[str, list[EventRecord]] = defaultdict(list)
    for record in records:
        record_id = _scalar(record, "id")
        if record_id:
            index[record_id].append(record)
    return index


def check_event_frontmatter(ctx):
    findings: list[Finding] = []
    for record in _records(ctx):
        for error in record.parse_errors:
            findings.append(Finding(CHECK_EVENT_FRONTMATTER, error, record.path))
        if record.parse_errors:
            continue

        required = _COMMON_FIELDS | _REQUIRED_FIELDS[record.category]
        allowed = required | _OPTIONAL_FIELDS[record.category]
        for key in sorted(required - record.fields.keys()):
            findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"missing required field {key}", record.path))
        for key in sorted(record.fields.keys() - allowed):
            findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"unknown field {key}", record.path))

        for key in sorted((required | _OPTIONAL_FIELDS[record.category]) & record.fields.keys()):
            value = record.fields[key]
            if key in _LIST_FIELDS:
                if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
                    findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"field {key} must be a non-empty string list", record.path))
            elif key in _INTEGER_FIELDS:
                if type(value) is not int or value < 0:
                    findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"field {key} must be a non-negative integer", record.path))
            elif not isinstance(value, str) or not value.strip():
                findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"field {key} must be a non-empty string", record.path))

        if record.category == "feedback" and "source_sha256" in record.fields:
            digest = record.fields["source_sha256"]
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                findings.append(Finding(CHECK_EVENT_FRONTMATTER, "field source_sha256 must be 64 lowercase hexadecimal characters", record.path))
        if record.category == "feedback" and "source_locator" in record.fields:
            locator = record.fields["source_locator"]
            if not isinstance(locator, str) or re.fullmatch(r"[a-z][a-z0-9-]*:[^\s]+", locator) is None:
                findings.append(Finding(CHECK_EVENT_FRONTMATTER, "field source_locator must be a scheme-prefixed stable pointer", record.path))

        if _scalar(record, "kind") and _scalar(record, "kind") != record.category:
            findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"kind must be {record.category}", record.path))
        expected_form = f"{record.category}@1"
        if _scalar(record, "form") and _scalar(record, "form") != expected_form:
            findings.append(Finding(CHECK_EVENT_FRONTMATTER, f"form must be {expected_form}", record.path))

        for (category, key), allowed_values in _ENUM_FIELDS.items():
            if record.category != category or key not in record.fields:
                continue
            value = _scalar(record, key)
            if value and value not in allowed_values:
                findings.append(
                    Finding(
                        CHECK_EVENT_FRONTMATTER,
                        f"field {key} must be one of {sorted(allowed_values)}",
                        record.path,
                    )
                )
        if record.category == "decision" and "status" in record.fields:
            status = _scalar(record, "status")
            if status not in {"active", "rolled-back"} and not status.startswith("superseded-by "):
                findings.append(Finding(CHECK_EVENT_FRONTMATTER, "invalid decision status", record.path))
    return findings


def _identity_match(record: EventRecord, value: str):
    return re.fullmatch(
        rf"{re.escape(record.prefix)}-([0-9]{{4}})-[a-z0-9]+(?:-[a-z0-9]+)*-([0-9]{{8}})",
        value,
    )


def check_event_identity(ctx):
    findings: list[Finding] = []
    for record in _records(ctx):
        stem = PurePosixPath(record.path).stem
        record_id = _scalar(record, "id")
        if not _identity_match(record, stem):
            findings.append(Finding(CHECK_EVENT_IDENTITY, "filename does not match the category id form", record.path))
            continue
        if record_id != stem:
            findings.append(Finding(CHECK_EVENT_IDENTITY, "id must equal the filename stem", record.path))
        match = _identity_match(record, stem)
        assert match is not None
        date_token = match.group(2)
        try:
            created = datetime.strptime(date_token, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            findings.append(Finding(CHECK_EVENT_IDENTITY, "filename date is not a calendar date", record.path))
        else:
            if _scalar(record, "created") != created:
                findings.append(Finding(CHECK_EVENT_IDENTITY, "created does not match the filename date", record.path))
    changes, errors = _issued_changes(ctx)
    for error in errors:
        findings.append(Finding(CHECK_EVENT_IDENTITY, error, "schema"))
    for change in changes:
        if not _issued_protected_change(change):
            continue
        if change.status == "D":
            findings.append(
                Finding(CHECK_EVENT_IDENTITY, "issued feedback/proposal may not be deleted", change.source_path)
            )
        elif change.status == "R":
            findings.append(
                Finding(CHECK_EVENT_IDENTITY, "issued feedback/proposal may not be renamed", change.source_path)
            )
        elif change.status == "M":
            original_id = _frontmatter_id(_head_bytes(ctx, change.source_path))
            candidate_id = _frontmatter_id(_index_bytes(ctx, change.source_path))
            if original_id is None or candidate_id is None or candidate_id != original_id:
                findings.append(
                    Finding(CHECK_EVENT_IDENTITY, "issued feedback/proposal id differs from HEAD", change.source_path)
                )
    return findings


def _protected_payload(body: str) -> tuple[str | None, str | None]:
    lines = body.splitlines(keepends=True)
    marker_lines = [
        (index, line.rstrip("\r\n"))
        for index, line in enumerate(lines)
        if "protected span" in line.lower()
    ]
    if len(marker_lines) != 2:
        return None, "requires exactly one protected begin/end pair"
    (begin_index, begin), (end_index, end) = marker_lines
    if begin != _BEGIN or end != _END or begin_index >= end_index:
        return None, "protected span uses a near-miss, nested, or reversed marker"
    payload = "".join(lines[begin_index + 1 : end_index])
    if not payload.strip():
        return None, "protected span payload is empty"
    return payload, None


def _protected_payload_bytes(content: bytes) -> bytes | None:
    lines = content.splitlines(keepends=True)
    markers = [
        (index, line.rstrip(b"\r\n"))
        for index, line in enumerate(lines)
        if b"protected span" in line.lower()
    ]
    if len(markers) != 2:
        return None
    (begin_index, begin), (end_index, end) = markers
    if begin != _BEGIN.encode() or end != _END.encode() or begin_index >= end_index:
        return None
    return b"".join(lines[begin_index + 1 : end_index])


def _head_bytes(ctx, path: str) -> bytes | None:
    baseline = getattr(ctx, "baseline_bytes", None)
    if callable(baseline):
        return baseline(path)
    try:
        proc = subprocess.run(
            ["git", "-C", str(ctx.root), "show", f"HEAD:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _current_bytes(ctx, path: str) -> bytes | None:
    reader = getattr(ctx, "current_bytes", None)
    if callable(reader):
        return reader(path)
    try:
        return (ctx.root / path).read_bytes()
    except OSError:
        return None


def _index_bytes(ctx, path: str) -> bytes | None:
    reader = getattr(ctx, "index_bytes", None)
    if callable(reader):
        return reader(path)
    try:
        proc = subprocess.run(
            ["git", "-C", str(ctx.root), "show", f":{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _issued_changes(ctx) -> tuple[list[IssuedChange], list[str]]:
    reader = getattr(ctx, "issued_changes", None)
    if callable(reader):
        return list(reader()), []
    try:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(ctx.root),
                "diff",
                "--cached",
                "--name-status",
                "-z",
                "--find-renames=1%",
                "HEAD",
                "--",
                "schema/feedbacks",
                "schema/proposals",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], [f"cannot inspect staged issued records: {exc}"]
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        return [], [f"cannot inspect staged issued records: {detail or 'git diff failed'}"]

    fields = proc.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    changes: list[IssuedChange] = []
    index = 0
    try:
        while index < len(fields):
            status = fields[index].decode("ascii")
            index += 1
            if not status or status[0] not in {"A", "C", "D", "M", "R", "T", "U"}:
                raise ValueError(f"unexpected status {status!r}")
            source_path = fields[index].decode("utf-8", errors="surrogateescape")
            index += 1
            if status[0] in {"C", "R"}:
                candidate_path = fields[index].decode("utf-8", errors="surrogateescape")
                index += 1
            else:
                candidate_path = None if status[0] == "D" else source_path
            changes.append(IssuedChange(status[0], source_path, candidate_path))
    except (IndexError, ValueError) as exc:
        return [], [f"cannot parse staged issued records: {exc}"]
    return changes, []


def _issued_protected_change(change: IssuedChange) -> bool:
    event_type = _event_category(change.source_path)
    return event_type is not None and event_type[0] in {"feedback", "proposal"}


def _frontmatter_id(content: bytes | None) -> str | None:
    if content is None:
        return None
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    fields, _, errors = _parse_frontmatter(text)
    value = fields.get("id")
    return value if not errors and isinstance(value, str) else None


def check_event_protected_span(ctx):
    findings: list[Finding] = []
    for record in _records(ctx):
        if record.category not in {"feedback", "proposal"}:
            continue
        payload, error = _protected_payload(record.body)
        if error:
            findings.append(Finding(CHECK_EVENT_PROTECTED_SPAN, error, record.path))
            continue
        if record.category == "feedback":
            payload_bytes = _protected_payload_bytes(_current_bytes(ctx, record.path) or b"")
            expected_digest = record.fields.get("source_sha256")
            expected_count = record.fields.get("source_byte_count")
            if payload_bytes is not None and (
                hashlib.sha256(payload_bytes).hexdigest() != expected_digest
                or len(payload_bytes) != expected_count
            ):
                findings.append(
                    Finding(
                        CHECK_EVENT_PROTECTED_SPAN,
                        "protected payload does not match source_sha256/source_byte_count",
                        record.path,
                    )
                )
        baseline_bytes = _head_bytes(ctx, record.path)
        if baseline_bytes is None:
            continue
        current_bytes = _current_bytes(ctx, record.path)
        if current_bytes is None:
            continue
        current_payload = _protected_payload_bytes(current_bytes)
        baseline_payload = _protected_payload_bytes(baseline_bytes)
        if current_payload is not None and baseline_payload is not None and current_payload != baseline_payload:
            findings.append(Finding(CHECK_EVENT_PROTECTED_SPAN, "protected payload differs from HEAD", record.path))
    changes, errors = _issued_changes(ctx)
    for error in errors:
        findings.append(Finding(CHECK_EVENT_PROTECTED_SPAN, error, "schema"))
    for change in changes:
        if not _issued_protected_change(change) or change.status not in {"M", "R"}:
            continue
        assert change.candidate_path is not None
        baseline_payload = _protected_payload_bytes(_head_bytes(ctx, change.source_path) or b"")
        candidate_payload = _protected_payload_bytes(_index_bytes(ctx, change.candidate_path) or b"")
        if baseline_payload is None or candidate_payload is None:
            findings.append(
                Finding(
                    CHECK_EVENT_PROTECTED_SPAN,
                    "cannot compare staged protected payload with its HEAD origin",
                    change.candidate_path,
                )
            )
        elif candidate_payload != baseline_payload:
            findings.append(
                Finding(
                    CHECK_EVENT_PROTECTED_SPAN,
                    "staged protected payload differs from its HEAD origin",
                    change.candidate_path,
                )
            )
    return findings


def _resolve(index, record_id: str, categories: set[str]) -> bool:
    matches = index.get(record_id, [])
    return len(matches) == 1 and matches[0].category in categories


def check_event_reference(ctx):
    records = _records(ctx)
    index = _index(records)
    findings: list[Finding] = []
    for record in records:
        if record.category == "proposal":
            evidence = record.fields.get("evidence")
            if isinstance(evidence, list):
                for record_id in evidence:
                    if isinstance(record_id, str) and not _resolve(index, record_id, {"observation", "feedback"}):
                        findings.append(Finding(CHECK_EVENT_REFERENCE, f"unresolved or ambiguous evidence {record_id}", record.path))
        elif record.category == "evaluation":
            proposal_id = _scalar(record, "evaluates")
            if proposal_id and not _resolve(index, proposal_id, {"proposal"}):
                findings.append(Finding(CHECK_EVENT_REFERENCE, f"unresolved or ambiguous proposal {proposal_id}", record.path))
        elif record.category == "decision":
            evaluation_id = _scalar(record, "gated_by")
            if evaluation_id and not _resolve(index, evaluation_id, {"evaluation"}):
                findings.append(Finding(CHECK_EVENT_REFERENCE, f"unresolved or ambiguous evaluation {evaluation_id}", record.path))
    return findings


def check_event_uniqueness(ctx):
    findings: list[Finding] = []
    ids: dict[str, list[EventRecord]] = defaultdict(list)
    numbers: dict[tuple[str, str], list[EventRecord]] = defaultdict(list)
    for record in _records(ctx):
        record_id = _scalar(record, "id")
        if not record_id:
            continue
        ids[record_id].append(record)
        match = _identity_match(record, record_id)
        if match:
            numbers[(record.category, match.group(1))].append(record)
    for record_id, matches in ids.items():
        if len(matches) > 1:
            for record in matches:
                findings.append(Finding(CHECK_EVENT_UNIQUENESS, f"duplicate event id {record_id}", record.path))
    for (category, number), matches in numbers.items():
        if len(matches) > 1 and len({_scalar(record, "id") for record in matches}) > 1:
            for record in matches:
                findings.append(Finding(CHECK_EVENT_UNIQUENESS, f"duplicate {category} number {number}", record.path))
    return findings


def check_decision_receipt(ctx):
    records = _records(ctx)
    index = _index(records)
    findings: list[Finding] = []
    for record in records:
        if record.category != "decision":
            continue
        has_receipt = "verification_receipt" in record.fields
        has_reason = "verification_not_applicable" in record.fields
        if has_receipt == has_reason:
            findings.append(
                Finding(
                    CHECK_DECISION_RECEIPT,
                    "decision requires exactly one verification receipt or non-applicability reason",
                    record.path,
                )
            )
            continue
        if has_receipt:
            receipt = _scalar(record, "verification_receipt")
            if not receipt or not _resolve(index, receipt, {"observation"}):
                findings.append(Finding(CHECK_DECISION_RECEIPT, f"receipt is missing, ambiguous, or not an observation: {receipt}", record.path))
        else:
            reason = _scalar(record, "verification_not_applicable")
            if not reason.strip():
                findings.append(Finding(CHECK_DECISION_RECEIPT, "verification non-applicability reason is empty", record.path))
    return findings


EVENT_CHECKS = (
    Check(CHECK_EVENT_FRONTMATTER, check_event_frontmatter),
    Check(CHECK_EVENT_IDENTITY, check_event_identity),
    Check(CHECK_EVENT_PROTECTED_SPAN, check_event_protected_span),
    Check(CHECK_EVENT_REFERENCE, check_event_reference),
    Check(CHECK_EVENT_UNIQUENESS, check_event_uniqueness),
    Check(CHECK_DECISION_RECEIPT, check_decision_receipt),
)

PROJECT_CHECKS = (Check(CHECK_PROJECT_LAYOUT, check_project_layout),)

PLUGIN = Plugin(
    (*_CATALOG_PLUGIN.checks, *PROJECT_CHECKS, *EVENT_CHECKS),
    REGISTRY_SCHEMA,
    (
        "project-manifest",
        "project-layout-contract",
        "harness-projection",
        "model-launch-verification",
    ),
)


class _FixtureContext:
    def __init__(
        self,
        root: Path,
        baseline_root: Path | None = None,
        overlay_root: Path | None = None,
        changes: tuple[IssuedChange, ...] = (),
    ):
        self.root = root
        self.baseline_root = baseline_root
        self.overlay_root = overlay_root
        self.changes = changes
        self.tracked = sorted(
            {
                path.relative_to(base).as_posix()
                for base in (overlay_root, root)
                if base is not None
                for path in base.rglob("*")
                if path.is_file()
            }
        )

    def read_text(self, path: str) -> str | None:
        content = self.current_bytes(path)
        if content is None:
            return None
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def current_bytes(self, path: str) -> bytes | None:
        for base in (self.root, self.overlay_root):
            if base is None:
                continue
            try:
                return (base / path).read_bytes()
            except OSError:
                continue
        return None

    def baseline_bytes(self, path: str) -> bytes | None:
        if self.baseline_root is None:
            return None
        try:
            return (self.baseline_root / path).read_bytes()
        except OSError:
            return None

    def index_bytes(self, path: str) -> bytes | None:
        return self.current_bytes(path)

    def issued_changes(self) -> tuple[IssuedChange, ...]:
        return self.changes


def _fixture_context(
    root: Path,
    overlay_root: Path | None = None,
    changes: tuple[IssuedChange, ...] = (),
) -> _FixtureContext:
    candidate = root / "candidate"
    if candidate.is_dir():
        baseline = root / "baseline"
        return _FixtureContext(
            candidate,
            baseline if baseline.is_dir() else None,
            overlay_root,
            changes,
        )
    return _FixtureContext(root, overlay_root=overlay_root, changes=changes)


def _fixture_findings(ctx: _FixtureContext) -> list[Finding]:
    return [finding for check in EVENT_CHECKS for finding in check.run(ctx)]


def _manifest_changes(raw: Any, case_name: str) -> tuple[tuple[IssuedChange, ...], list[str]]:
    failures: list[str] = []
    if raw is None:
        return (), failures
    if not isinstance(raw, list):
        return (), [f"negative fixture {case_name} changes must be a list"]
    changes: list[IssuedChange] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict) or set(item) != {"status", "source", "candidate"}:
            failures.append(f"negative fixture {case_name} change {index} has invalid fields")
            continue
        status = item.get("status")
        source = item.get("source")
        candidate = item.get("candidate")
        if status not in {"D", "M", "R"} or not isinstance(source, str):
            failures.append(f"negative fixture {case_name} change {index} has invalid status/source")
            continue
        if status == "D":
            if candidate is not None:
                failures.append(f"negative fixture {case_name} deletion {index} must have null candidate")
                continue
        elif not isinstance(candidate, str):
            failures.append(f"negative fixture {case_name} change {index} requires a candidate path")
            continue
        changes.append(IssuedChange(status, source, candidate))
    return tuple(changes), failures


def run_fixtures(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"fixture manifest cannot be read: {exc}"]
    if not isinstance(manifest, dict) or set(manifest) != {"valid", "negative_cases"}:
        return ["fixture manifest must contain exactly valid and negative_cases"]

    valid = manifest["valid"]
    if not isinstance(valid, dict) or set(valid) != {"path", "required_categories", "required_records"}:
        return ["fixture manifest valid entry has invalid fields"]
    valid_path = valid.get("path")
    required_categories = valid.get("required_categories")
    required_records = valid.get("required_records")
    all_categories = set(_REQUIRED_FIELDS)
    if not isinstance(valid_path, str) or not (root / valid_path).is_dir():
        failures.append("valid fixture path is missing")
        valid_root = root / "valid"
    else:
        valid_root = root / valid_path
    if not isinstance(required_categories, list) or set(required_categories) != all_categories:
        failures.append(
            f"valid fixture required_categories must be exactly {sorted(all_categories)}"
        )
    if not isinstance(required_records, list) or any(not isinstance(path, str) for path in required_records):
        failures.append("valid fixture required_records must be a list of paths")
        required_records = []

    valid_context = _FixtureContext(valid_root)
    missing_records = sorted(set(required_records) - set(valid_context.tracked))
    if missing_records:
        failures.append(f"valid fixture is missing required records {missing_records}")
    record_categories = {
        event_type[0]
        for path in required_records
        if (event_type := _event_category(path)) is not None
    }
    if record_categories != all_categories:
        failures.append(
            "valid fixture required_records do not cover the six categories "
            f"(got {sorted(record_categories)})"
        )
    valid_findings = _fixture_findings(valid_context)
    if valid_findings:
        failures.extend(
            f"valid fixture failed: [{item.check_id}] {item.path}: {item.message}"
            for item in valid_findings
        )

    negative_cases = manifest["negative_cases"]
    if not isinstance(negative_cases, list):
        failures.append("fixture manifest negative_cases must be a list")
        return failures
    check_ids = {check.check_id for check in EVENT_CHECKS}
    names: set[str] = set()
    declared_paths: set[str] = set()
    invalid_root = root / "invalid"
    actual_paths = {
        case.relative_to(root).as_posix()
        for group in invalid_root.iterdir()
        if group.is_dir()
        for case in group.iterdir()
        if case.is_dir()
    } if invalid_root.is_dir() else set()
    for case in negative_cases:
        if not isinstance(case, dict) or set(case) - {"name", "path", "expected_check_ids", "changes"}:
            failures.append("negative fixture manifest entry has invalid fields")
            continue
        name = case.get("name")
        case_path = case.get("path")
        expected = case.get("expected_check_ids")
        if not isinstance(name, str) or not name or name in names:
            failures.append(f"negative fixture has invalid or duplicate name {name!r}")
            continue
        names.add(name)
        if not isinstance(case_path, str) or not case_path.startswith("invalid/") or case_path in declared_paths:
            failures.append(f"negative fixture {name} has invalid or duplicate path")
            continue
        declared_paths.add(case_path)
        if not isinstance(expected, list) or not expected or any(item not in check_ids for item in expected):
            failures.append(f"negative fixture {name} has invalid expected_check_ids")
            continue
        if len(set(expected)) != len(expected):
            failures.append(f"negative fixture {name} repeats an expected check id")
            continue
        case_root = root / case_path
        if not case_root.is_dir():
            failures.append(f"negative fixture {name} path is missing: {case_path}")
            continue
        changes, change_failures = _manifest_changes(case.get("changes"), name)
        failures.extend(change_failures)
        if change_failures:
            continue
        context = _fixture_context(case_root, valid_root, changes)
        candidate_root = case_root / "candidate" if (case_root / "candidate").is_dir() else case_root
        baseline_root = case_root / "baseline"
        for change in changes:
            if not (baseline_root / change.source_path).is_file():
                failures.append(
                    f"negative fixture {name} is missing baseline record {change.source_path}"
                )
            if change.status == "D":
                if (candidate_root / change.source_path).exists():
                    failures.append(
                        f"negative fixture {name} deletion still contains {change.source_path}"
                    )
            else:
                assert change.candidate_path is not None
                if not (candidate_root / change.candidate_path).is_file():
                    failures.append(
                        f"negative fixture {name} is missing candidate record {change.candidate_path}"
                    )
                if change.status == "R" and (candidate_root / change.source_path).exists():
                    failures.append(
                        f"negative fixture {name} rename still contains {change.source_path}"
                    )
        found = {finding.check_id for finding in _fixture_findings(context)}
        if found != set(expected):
            failures.append(
                f"negative fixture {name} produced the wrong checks "
                f"(expected {sorted(expected)}, got {sorted(found)})"
            )
    if actual_paths != declared_paths:
        failures.append(
            "negative fixture subcases differ from the manifest "
            f"(expected {sorted(declared_paths)}, got {sorted(actual_paths)})"
        )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    args = parser.parse_args(argv)
    failures = run_fixtures(args.fixtures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("event fixtures: PASS (manifest verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

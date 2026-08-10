#!/usr/bin/env python3
"""Validate and deterministically project the repository agent harness."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from scripts.engine import registry as registry_engine
from scripts.event_check import REGISTRY_SCHEMA, registry_contract_errors


CHECK_PROJECT_MANIFEST = "project-manifest"
CHECK_HARNESS_PROJECTION = "harness-projection"
CHECK_MODEL_LAUNCH = "model-launch-verification"

CANONICAL_CONTRACT = "AGENTS.md"
CLAUDE_ADAPTER = "CLAUDE.md"
SYNC_SKILL = ".agents/skills/harness-sync/SKILL.md"
LINT_SKILL = ".agents/skills/harness-lint/SKILL.md"
GENERATOR_PATH = "scripts/harness_manifest.py"
CLAUDE_ADAPTER_BYTES = b"# CLAUDE.md\n\n@AGENTS.md\n"

BEGIN_SOURCE_MARKER = "<!-- harness:begin v1 -->"
END_SOURCE_MARKER = "<!-- harness:end -->"
REGISTRY_LOCATOR_MARKER = re.compile(
    r"<!-- harness:registry-locator ([a-z0-9][a-z0-9._/-]*\.yaml) -->"
)
PROVENANCE_PREFIX = "<!-- harness:provenance "


@dataclass(frozen=True)
class Projection:
    source: str
    target: str
    sentinel: str


PROJECTIONS: tuple[Projection, ...] = (
    Projection(
        SYNC_SKILL,
        ".claude/skills/harness-sync/SKILL.md",
        "harness-sync-v1",
    ),
    Projection(
        LINT_SKILL,
        ".claude/skills/harness-lint/SKILL.md",
        "harness-lint-v1",
    ),
)

KOREAN_CANONICAL_DOCS: tuple[str, ...] = (
    "DESIGN.md",
    "PRODUCT.md",
    "knowledge/README.md",
    "schema/contracts/README.md",
    "schema/defers/INDEX.md",
    "schema/defers/USER-DEFERRED.md",
    "schema/handoff/README.md",
    "schema/handoff/ledgers/README.md",
    "schema/spec/00-overview.md",
    "schema/spec/01-layers-and-evidence.md",
    "schema/spec/02-parallelism-and-orchestration.md",
    "schema/spec/03-enforcement-and-procedures.md",
    "schema/stages/README.md",
    "schema/template/events/decision.md",
    "schema/template/events/deferred.md",
    "schema/template/events/evaluation.md",
    "schema/template/events/feedback.md",
    "schema/template/events/observation.md",
    "schema/template/events/proposal.md",
    "schema/template/handoff-snapshot.md",
    "schema/template/operating-ledger.md",
    "scripts/engine/README.md",
)

INPUT_KINDS: tuple[str, ...] = (
    "locator-registry",
    "canonical-contract",
    "sync-skill",
    "lint-skill",
    "project-manifest",
    "generator",
)


class HarnessError(Exception):
    def __init__(self, check_id: str, messages: str | Iterable[str]) -> None:
        self.check_id = check_id
        self.messages = [messages] if isinstance(messages, str) else list(messages)
        super().__init__("; ".join(self.messages))


@dataclass(frozen=True)
class State:
    root: Path
    registry_locator: str
    registry_bytes: bytes
    registry_doc: dict[str, Any]
    registry: registry_engine.Registry
    project_manifest: str
    manifest_bytes: bytes
    manifest: dict[str, Any]
    source_bytes: dict[str, bytes]
    generator_bytes: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative_path(root: Path, relpath: str) -> Path:
    root = root.resolve()
    if not isinstance(relpath, str) or not relpath or "\\" in relpath:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"unsafe repository path: {relpath!r}")
    pure = PurePosixPath(relpath)
    if pure.is_absolute() or pure.as_posix() != relpath or any(part in ("", ".", "..") for part in pure.parts):
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"unsafe repository path: {relpath!r}")
    candidate = root.joinpath(*pure.parts)
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError):
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            f"repository path escapes through an absolute path, '..', or symlink: {relpath}",
        ) from None
    return candidate


def _read_canonical(root: Path, relpath: str, check_id: str) -> bytes:
    path = _relative_path(root, relpath)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise HarnessError(check_id, f"cannot read {relpath}: {exc}") from None
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HarnessError(check_id, f"{relpath} is not UTF-8: {exc}") from None
    if b"\r" in data or not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise HarnessError(
            check_id,
            f"{relpath} must use UTF-8/LF and end with exactly one newline",
        )
    return data


def _parse_yaml(data: bytes, relpath: str, max_depth: int = 10) -> dict[str, Any]:
    try:
        parsed = registry_engine.parse_strict_yaml(data.decode("utf-8"), max_depth=max_depth)
    except registry_engine.RegistryError as exc:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            [f"{relpath}: {message}" for message in exc.errors],
        ) from None
    if not isinstance(parsed, dict):
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath}: document root must be a mapping")
    return parsed


def _expect_keys(node: Any, required: set[str], context: str) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context} must be a mapping")
    actual = set(node)
    if actual != required:
        missing = sorted(required - actual)
        unknown = sorted(actual - required)
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            f"{context} has a non-closed shape (missing={missing}, unknown={unknown})",
        )
    return node


def _nonempty_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context} must be a non-empty string")
    return value


def _sentence_count(value: str) -> int:
    return len(re.findall(r"[.!?](?=\s|$)", value.strip()))


def _localized_pair(value: Any, context: str) -> None:
    pair = _expect_keys(value, {"ko", "en_brief"}, context)
    ko = _nonempty_string(pair["ko"], f"{context}.ko")
    brief = _nonempty_string(pair["en_brief"], f"{context}.en_brief")
    if re.search(r"[가-힣]", ko) is None:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.ko must contain Korean text")
    count = _sentence_count(brief)
    if not 2 <= count <= 4:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            f"{context}.en_brief must contain 2-4 sentences, got {count}",
        )


def _validate_launch_verification(value: Any) -> None:
    context = "manifest.tools.codex.launch_verification"
    verification = _expect_keys(
        value,
        {"profile", "identity_sources", "worker_record", "completion_record"},
        context,
    )
    if verification["profile"] != "orca-worker-completion-v1":
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.profile is invalid")
    identity_sources = _expect_keys(
        verification["identity_sources"],
        {"task", "dispatch"},
        f"{context}.identity_sources",
    )
    if identity_sources != {"task": "task_issued", "dispatch": "live"}:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.identity_sources is invalid")

    worker = _expect_keys(
        verification["worker_record"],
        {"fields", "allowed_values"},
        f"{context}.worker_record",
    )
    worker_fields = _expect_keys(
        worker["fields"],
        {"success", "task", "dispatch", "requested", "effective"},
        f"{context}.worker_record.fields",
    )
    expected_worker_fields = {
        "success": "ok",
        "task": "result.dispatch.task_id",
        "dispatch": "result.dispatch.id",
        "requested": "result.worker.startOptions.launch.requested",
        "effective": "result.worker.startOptions.launch.effective",
    }
    if worker_fields != expected_worker_fields:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.worker_record.fields is invalid")
    worker_allowed = _expect_keys(
        worker["allowed_values"],
        {"success"},
        f"{context}.worker_record.allowed_values",
    )
    if worker_allowed != {"success": True}:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.worker_record.allowed_values is invalid")

    completion = _expect_keys(
        verification["completion_record"],
        {"fields", "allowed_values"},
        f"{context}.completion_record",
    )
    completion_fields = _expect_keys(
        completion["fields"],
        {
            "success",
            "messages",
            "type",
            "payload",
            "task",
            "dispatch",
            "outcome",
            "files_modified",
        },
        f"{context}.completion_record.fields",
    )
    expected_completion_fields = {
        "success": "ok",
        "messages": "result.messages",
        "type": "type",
        "payload": "payload",
        "task": "taskId",
        "dispatch": "dispatchId",
        "outcome": "outcome",
        "files_modified": "filesModified",
    }
    if completion_fields != expected_completion_fields:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.completion_record.fields is invalid")
    completion_allowed = _expect_keys(
        completion["allowed_values"],
        {"success", "type", "outcome"},
        f"{context}.completion_record.allowed_values",
    )
    if completion_allowed != {
        "success": True,
        "type": "worker_done",
        "outcome": "succeeded",
    }:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{context}.completion_record.allowed_values is invalid")


def _validate_manifest(doc: dict[str, Any]) -> None:
    root = _expect_keys(doc, {"schema_version", "project", "language", "execution", "tools"}, "manifest")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest.schema_version must be integer 1")

    project = _expect_keys(root["project"], {"id", "purpose", "non_goal"}, "manifest.project")
    project_id = _nonempty_string(project["id"], "manifest.project.id")
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id) is None:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest.project.id must be lowercase kebab-case")
    _localized_pair(project["purpose"], "manifest.project.purpose")
    _localized_pair(project["non_goal"], "manifest.project.non_goal")

    language = _expect_keys(
        root["language"],
        {"user_replies", "durable_human_prose", "path_names", "metadata_keys"},
        "manifest.language",
    )
    if language["user_replies"] != "ko":
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest.language.user_replies must be ko")
    durable = _expect_keys(
        language["durable_human_prose"],
        {
            "canonical_language",
            "coverage",
            "mechanical_enforcement",
            "english_brief",
        },
        "manifest.language.durable_human_prose",
    )
    if (
        durable["canonical_language"] != "ko"
        or durable["coverage"] != "existing-and-new"
        or durable["mechanical_enforcement"] != "layout-registry"
    ):
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest durable prose policy has an invalid value")
    brief = _expect_keys(
        durable["english_brief"],
        {"min_sentences", "max_sentences"},
        "manifest.language.durable_human_prose.english_brief",
    )
    if type(brief["min_sentences"]) is not int or type(brief["max_sentences"]) is not int or brief != {"min_sentences": 2, "max_sentences": 4}:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest English brief range must be exactly 2-4")
    if language["path_names"] != "english-kebab-case" or language["metadata_keys"] != "english":
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest machine-facing language values are invalid")

    execution = _expect_keys(root["execution"], {"defaults", "opt_out"}, "manifest.execution")
    defaults = _expect_keys(
        execution["defaults"],
        {
            "supervisor_for_meaningful_units",
            "harness_for_meaningful_units",
            "dedicated_worktree_for_write_units",
        },
        "manifest.execution.defaults",
    )
    if any(value is not True for value in defaults.values()):
        raise HarnessError(CHECK_PROJECT_MANIFEST, "all manifest execution defaults must be true")
    opt_out = _expect_keys(
        execution["opt_out"],
        {"authority", "scope", "cascade"},
        "manifest.execution.opt_out",
    )
    if opt_out != {"authority": "explicit-user", "scope": "current-unit", "cascade": "none"}:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest opt-out values are invalid")

    tools = _expect_keys(root["tools"], {"codex", "claude"}, "manifest.tools")
    claude = _expect_keys(tools["claude"], {"delegation"}, "manifest.tools.claude")
    if claude["delegation"] != "disabled":
        raise HarnessError(CHECK_PROJECT_MANIFEST, "Claude delegation must be disabled in manifest v1")

    codex = tools["codex"]
    if not isinstance(codex, dict) or codex.get("delegation") not in {"enabled", "disabled"}:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "manifest.tools.codex.delegation is invalid")
    if codex["delegation"] == "disabled":
        _expect_keys(codex, {"delegation"}, "manifest.tools.codex")
        return
    codex = _expect_keys(
        codex,
        {"delegation", "supervisor_binding", "launch_verification", "model_bindings"},
        "manifest.tools.codex",
    )
    if codex["supervisor_binding"] != "orca-stored-orchestration":
        raise HarnessError(CHECK_PROJECT_MANIFEST, "Codex supervisor binding is invalid")
    _validate_launch_verification(codex["launch_verification"])
    bindings = _expect_keys(
        codex["model_bindings"],
        {"rewrite", "adversarial-review", "routine"},
        "manifest.tools.codex.model_bindings",
    )
    for tier, binding in bindings.items():
        binding = _expect_keys(binding, {"model", "effort"}, f"manifest.tools.codex.model_bindings.{tier}")
        _nonempty_string(binding["model"], f"manifest.tools.codex.model_bindings.{tier}.model")
        _nonempty_string(binding["effort"], f"manifest.tools.codex.model_bindings.{tier}.effort")


def _check_korean_brief(data: bytes, relpath: str, *, contract: bool = False) -> None:
    text = data.decode("utf-8")
    if re.search(r"[가-힣]", text) is None:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath} must contain Korean canonical prose")
    marker = "## English brief\n\n"
    if text.count(marker) != 1:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath} must contain one exact English brief section")
    brief = text.split(marker, 1)[1]
    if contract:
        brief = brief.split(END_SOURCE_MARKER, 1)[0]
    else:
        brief = re.split(r"(?m)^## ", brief, maxsplit=1)[0]
    count = _sentence_count(brief)
    if not 2 <= count <= 4:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath} English brief must contain 2-4 sentences, got {count}")


def _check_registry_language_brief(data: bytes, relpath: str) -> None:
    text = data.decode("utf-8")
    if re.search(r"[가-힣]", text) is None:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath} must contain Korean canonical comments")
    marker = "# English brief\n"
    if text.count(marker) != 1:
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"{relpath} must contain one exact comment English brief")
    lines: list[str] = []
    for line in text.split(marker, 1)[1].splitlines():
        if not line.startswith("#"):
            break
        lines.append(line.removeprefix("#").lstrip())
    count = _sentence_count(" ".join(lines))
    if not 2 <= count <= 4:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            f"{relpath} comment English brief must contain 2-4 sentences, got {count}",
        )


def _extract_registry_locator(data: bytes) -> str:
    text = data.decode("utf-8")
    lines = text.splitlines()
    if lines.count(BEGIN_SOURCE_MARKER) != 1 or lines.count(END_SOURCE_MARKER) != 1:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "canonical contract must contain one exact source marker pair")
    marker_lines = [line for line in lines if "harness:" in line]
    locator_matches = [REGISTRY_LOCATOR_MARKER.fullmatch(line) for line in marker_lines]
    locator_lines = [
        line for line, match in zip(marker_lines, locator_matches) if match is not None
    ]
    if len(locator_lines) != 1:
        raise HarnessError(
            CHECK_HARNESS_PROJECTION,
            "canonical contract must contain one exact registry locator marker",
        )
    if marker_lines != [BEGIN_SOURCE_MARKER, locator_lines[0], END_SOURCE_MARKER]:
        raise HarnessError(
            CHECK_HARNESS_PROJECTION,
            "canonical contract contains a duplicate, missing, or near-miss harness marker",
        )
    begin = lines.index(BEGIN_SOURCE_MARKER)
    locator = lines.index(locator_lines[0])
    end = lines.index(END_SOURCE_MARKER)
    if not begin < locator < end:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "canonical contract markers are reversed")
    match = REGISTRY_LOCATOR_MARKER.fullmatch(locator_lines[0])
    if match is None:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "canonical contract registry locator marker is invalid")
    return match.group(1)


def _validate_skill(data: bytes, relpath: str, expected_name: str) -> None:
    lines = data.decode("utf-8").splitlines()
    if len(lines) < 4 or lines[0] != "---" or lines[1] != f"name: {expected_name}":
        raise HarnessError(
            CHECK_HARNESS_PROJECTION,
            f"{relpath} frontmatter name must be exactly {expected_name}",
        )


def _resolve_contract_role(state_registry: registry_engine.Registry, relpath: str) -> None:
    winners = state_registry.resolve(relpath)
    if len(winners) != 1 or winners[0].role != "contract":
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            f"registry path must resolve exactly once with role contract: {relpath}",
        )


def _load_state(root_arg: str | Path) -> State:
    root = Path(root_arg).resolve()
    if not root.is_dir():
        raise HarnessError(CHECK_PROJECT_MANIFEST, f"repository root is not a directory: {root}")

    entry_bytes = _read_canonical(root, CANONICAL_CONTRACT, CHECK_HARNESS_PROJECTION)
    registry_locator = _extract_registry_locator(entry_bytes)
    _relative_path(root, registry_locator)
    registry_bytes = _read_canonical(root, registry_locator, CHECK_PROJECT_MANIFEST)
    registry_doc = _parse_yaml(registry_bytes, registry_locator)
    if REGISTRY_SCHEMA.required_extra_top_level_keys != (
        "canonical_contract",
        "project_manifest",
        "language_lint",
    ):
        raise HarnessError(CHECK_PROJECT_MANIFEST, "registry schema harness pointer extension is not exact")
    try:
        registry = registry_engine._validate(registry_doc, REGISTRY_SCHEMA)
    except registry_engine.RegistryError as exc:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            [f"{registry_locator}: {message}" for message in exc.errors],
        ) from None
    layout_errors = registry_contract_errors(root, registry)
    if layout_errors:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            [f"{registry_locator}: {message}" for message in layout_errors],
        )

    pointers: dict[str, str] = {}
    for key in ("canonical_contract", "project_manifest"):
        value = registry_doc.get(key)
        if not isinstance(value, str) or not value:
            raise HarnessError(CHECK_PROJECT_MANIFEST, f"registry pointer {key} must be one non-empty scalar")
        _relative_path(root, value)
        _resolve_contract_role(registry, value)
        pointers[key] = value

    canonical_contract = pointers["canonical_contract"]
    canonical_bytes = _read_canonical(
        root, canonical_contract, CHECK_HARNESS_PROJECTION
    )
    if (
        _relative_path(root, canonical_contract).resolve()
        != _relative_path(root, CANONICAL_CONTRACT).resolve()
        or canonical_bytes != entry_bytes
    ):
        raise HarnessError(
            CHECK_HARNESS_PROJECTION,
            "registry canonical_contract must identify the same auto-loaded AGENTS bytes",
        )

    project_manifest = pointers["project_manifest"]
    manifest_bytes = _read_canonical(root, project_manifest, CHECK_PROJECT_MANIFEST)
    manifest = _parse_yaml(manifest_bytes, project_manifest)
    _validate_manifest(manifest)

    source_bytes: dict[str, bytes] = {
        canonical_contract: canonical_bytes
    }
    for projection in PROJECTIONS:
        _resolve_contract_role(registry, projection.source)
        _resolve_contract_role(registry, projection.target)
        if projection.source not in source_bytes:
            source_bytes[projection.source] = _read_canonical(
                root, projection.source, CHECK_HARNESS_PROJECTION
            )
    language_coverage = registry_doc["language_lint"]["coverage"]
    expected_language_coverage = sorted(
        {canonical_contract, *(projection.source for projection in PROJECTIONS), *KOREAN_CANONICAL_DOCS}
    )
    if language_coverage != expected_language_coverage:
        raise HarnessError(
            CHECK_PROJECT_MANIFEST,
            "registry language_lint.coverage must exactly cover the declared Korean canonical documents",
        )
    for relpath in language_coverage:
        if relpath not in source_bytes:
            source_bytes[relpath] = _read_canonical(root, relpath, CHECK_PROJECT_MANIFEST)
        _check_korean_brief(
            source_bytes[relpath],
            relpath,
            contract=relpath == canonical_contract,
        )
    _check_registry_language_brief(registry_bytes, registry_locator)
    _validate_skill(source_bytes[SYNC_SKILL], SYNC_SKILL, "harness-sync")
    _validate_skill(source_bytes[LINT_SKILL], LINT_SKILL, "harness-lint")

    _resolve_contract_role(registry, CLAUDE_ADAPTER)
    claude_bytes = _read_canonical(root, CLAUDE_ADAPTER, CHECK_HARNESS_PROJECTION)
    if claude_bytes != CLAUDE_ADAPTER_BYTES:
        raise HarnessError(
            CHECK_HARNESS_PROJECTION,
            f"{CLAUDE_ADAPTER} must contain only its title and @AGENTS.md pointer",
        )

    generator_bytes = _read_canonical(root, GENERATOR_PATH, CHECK_HARNESS_PROJECTION)
    _resolve_contract_role(registry, registry_locator)
    _resolve_contract_role(registry, project_manifest)
    if "deployment_authority" in manifest_bytes.decode("utf-8"):
        raise HarnessError(CHECK_PROJECT_MANIFEST, "deployment_authority is outside manifest v1")
    contract_text = canonical_bytes.decode("utf-8")
    if "Published outputs" in contract_text or "published-output" in contract_text:
        raise HarnessError(CHECK_PROJECT_MANIFEST, "publication must not be declared as a provenance layer")
    forbidden = (
        "rizingblare-github-io",
        "Resume, Portfolio, Blog",
        "knowledge/",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "/Users/",
        "task_",
        "ctx_",
        "harness:projection-begin",
        "harness:provenance",
        "harness:projection-end",
    )
    for value in forbidden:
        if value in contract_text:
            raise HarnessError(
                CHECK_HARNESS_PROJECTION,
                f"canonical contract contains forbidden project/model/runtime/envelope value: {value}",
            )

    return State(
        root,
        registry_locator,
        registry_bytes,
        registry_doc,
        registry,
        project_manifest,
        manifest_bytes,
        manifest,
        source_bytes,
        generator_bytes,
    )


def _projection_markers(projection: Projection) -> tuple[str, str]:
    return (
        f"<!-- harness:projection-begin {projection.sentinel} -->",
        f"<!-- harness:projection-end {projection.sentinel} -->",
    )


def _render_projection(state: State, projection: Projection) -> bytes:
    body = state.source_bytes[projection.source]
    provenance: dict[str, Any] = {
        "schema": 1,
        "target": projection.target,
    }
    provenance["sources"] = [
        {"path": projection.source, "sha256": _sha256(body)}
    ]
    provenance["generator"] = {
        "path": GENERATOR_PATH,
        "sha256": _sha256(state.generator_bytes),
    }
    provenance["body_sha256"] = _sha256(body)
    provenance_json = json.dumps(provenance, ensure_ascii=False, separators=(",", ":"))
    begin, end = _projection_markers(projection)
    return (
        begin.encode("utf-8")
        + b"\n"
        + PROVENANCE_PREFIX.encode("utf-8")
        + provenance_json.encode("utf-8")
        + b" -->\n"
        + body
        + end.encode("utf-8")
        + b"\n"
    )


def _render_all(state: State) -> dict[str, bytes]:
    first = {projection.target: _render_projection(state, projection) for projection in PROJECTIONS}
    second = {projection.target: _render_projection(state, projection) for projection in PROJECTIONS}
    if first != second:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "projection renderer is nondeterministic")
    return dict(sorted(first.items()))


def _valid_projection_envelope(data: bytes, projection: Projection) -> bool:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    begin, end = _projection_markers(projection)
    lines = text.splitlines()
    if not lines or lines[0] != begin or lines[-1] != end:
        return False
    if lines.count(begin) != 1 or lines.count(end) != 1:
        return False
    provenance_lines = [line for line in lines if line.startswith(PROVENANCE_PREFIX)]
    if len(provenance_lines) != 1 or lines[1] != provenance_lines[0] or not provenance_lines[0].endswith(" -->"):
        return False
    marker_like = [line for line in lines if "harness:projection-" in line]
    return marker_like == [begin, end]


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _exclusive_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise HarnessError(CHECK_HARNESS_PROJECTION, f"refusing to overwrite existing bootstrap plan: {path}") from None
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _input_rows(state: State) -> list[dict[str, str]]:
    canonical_contract = state.registry_doc["canonical_contract"]
    ordered = (
        ("locator-registry", state.registry_locator, state.registry_bytes),
        ("canonical-contract", canonical_contract, state.source_bytes[canonical_contract]),
        ("sync-skill", SYNC_SKILL, state.source_bytes[SYNC_SKILL]),
        ("lint-skill", LINT_SKILL, state.source_bytes[LINT_SKILL]),
        ("project-manifest", state.project_manifest, state.manifest_bytes),
        ("generator", GENERATOR_PATH, state.generator_bytes),
    )
    return [
        {"kind": kind, "path": path, "sha256": _sha256(data)}
        for kind, path, data in ordered
    ]


def _plan_document(state: State) -> dict[str, Any]:
    expected = _render_all(state)
    targets: list[dict[str, str]] = []
    for relpath, new_bytes in expected.items():
        path = _relative_path(state.root, relpath)
        old = _sha256(path.read_bytes()) if path.is_file() else "absent"
        targets.append({"path": relpath, "old": old, "new_sha256": _sha256(new_bytes)})
    return {"schema_version": 1, "inputs": _input_rows(state), "targets": targets}


def _canonical_json_bytes(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, separators=(",", ": ")) + "\n").encode("utf-8")


def _validate_plan_bytes(data: bytes) -> dict[str, Any]:
    try:
        plan = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError(CHECK_HARNESS_PROJECTION, f"bootstrap plan is not canonical JSON: {exc}") from None
    if not isinstance(plan, dict) or set(plan) != {"schema_version", "inputs", "targets"} or plan.get("schema_version") != 1:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan has a non-closed root shape")
    if _canonical_json_bytes(plan) != data:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan bytes are not canonical")
    inputs = plan.get("inputs")
    targets = plan.get("targets")
    if not isinstance(inputs, list) or not isinstance(targets, list):
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan inputs and targets must be lists")
    actual_kinds: list[str] = []
    for row in inputs:
        if not isinstance(row, dict) or list(row) != ["kind", "path", "sha256"]:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan input row has a non-closed shape")
        kind, path = row.get("kind"), row.get("path")
        actual_kinds.append(kind)
        if not isinstance(path, str) or not path or "\\" in path:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan input path is invalid")
        pure = PurePosixPath(path)
        if pure.is_absolute() or pure.as_posix() != path or any(part in ("", ".", "..") for part in pure.parts):
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan input path is unsafe")
        if re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256"))) is None:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan input digest is invalid")
    if actual_kinds != list(INPUT_KINDS):
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan input order or coverage is invalid")
    target_paths: list[str] = []
    for row in targets:
        if not isinstance(row, dict) or list(row) != ["path", "old", "new_sha256"]:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan target row has a non-closed shape")
        path, old, new = row.get("path"), row.get("old"), row.get("new_sha256")
        if not isinstance(path, str) or not isinstance(old, str) or not isinstance(new, str):
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan target values must be strings")
        if old != "absent" and re.fullmatch(r"[0-9a-f]{64}", old) is None:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan old digest is invalid")
        if re.fullmatch(r"[0-9a-f]{64}", new) is None:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan new digest is invalid")
        target_paths.append(path)
    expected_targets = sorted(projection.target for projection in PROJECTIONS)
    if target_paths != expected_targets:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan target order or coverage is invalid")
    return plan


def _create_plan(root: Path, out_arg: str) -> tuple[str, list[dict[str, str]]]:
    state = _load_state(root)
    plan = _plan_document(state)
    data = _canonical_json_bytes(plan)
    out = _relative_path(state.root, out_arg)
    _exclusive_write(out, data)
    digest = _sha256(data)
    return digest, plan["targets"]


def _apply_plan(root: Path, plan_arg: str, approved_digest: str) -> tuple[int, list[tuple[str, str]]]:
    if re.fullmatch(r"[0-9a-f]{64}", approved_digest or "") is None:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "approved bootstrap plan digest must be 64 lowercase hex")
    plan_path = _relative_path(root.resolve(), plan_arg)
    try:
        plan_bytes = plan_path.read_bytes()
    except OSError as exc:
        raise HarnessError(CHECK_HARNESS_PROJECTION, f"cannot read bootstrap plan: {exc}") from None
    if _sha256(plan_bytes) != approved_digest:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap plan digest differs from the approved digest")
    plan = _validate_plan_bytes(plan_bytes)
    state = _load_state(root)

    current_inputs = _input_rows(state)
    if current_inputs != plan["inputs"]:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "bootstrap input path or digest drifted after plan approval; target writes: 0")
    expected = _render_all(state)
    planned_targets = {row["path"]: row for row in plan["targets"]}
    for relpath, data in expected.items():
        if _sha256(data) != planned_targets[relpath]["new_sha256"]:
            raise HarnessError(CHECK_HARNESS_PROJECTION, "rendered target differs from approved new_sha256; target writes: 0")

    states: list[tuple[str, str]] = []
    for relpath, data in expected.items():
        path = _relative_path(state.root, relpath)
        row = planned_targets[relpath]
        if path.is_file():
            current_bytes = path.read_bytes()
            current_digest = _sha256(current_bytes)
            if current_digest == row["new_sha256"] and current_bytes == data and _valid_projection_envelope(data, next(p for p in PROJECTIONS if p.target == relpath)):
                target_state = "complete"
            elif current_digest == row["old"]:
                target_state = "pending"
            else:
                target_state = "conflict"
        elif row["old"] == "absent":
            target_state = "pending"
        else:
            target_state = "conflict"
        states.append((relpath, target_state))
    conflicts = [path for path, target_state in states if target_state == "conflict"]
    if conflicts:
        raise HarnessError(CHECK_HARNESS_PROJECTION, f"bootstrap target conflict before write: {', '.join(conflicts)}; target writes: 0")

    written = 0
    for relpath, target_state in states:
        if target_state == "pending":
            _atomic_write(_relative_path(state.root, relpath), expected[relpath])
            written += 1
    return written, states


def _sync(root: Path, check: bool) -> int:
    state = _load_state(root)
    expected = _render_all(state)
    drift: list[str] = []
    for projection in PROJECTIONS:
        path = _relative_path(state.root, projection.target)
        current = path.read_bytes() if path.is_file() else None
        if current != expected[projection.target]:
            drift.append(projection.target)
            if not check and (current is None or not _valid_projection_envelope(current, projection)):
                raise HarnessError(
                    CHECK_HARNESS_PROJECTION,
                    f"refusing to overwrite target without one exact projection envelope: {projection.target}",
                )
    if check:
        if drift:
            raise HarnessError(CHECK_HARNESS_PROJECTION, f"projection drift: {', '.join(sorted(drift))}")
        return 0
    for relpath in sorted(drift):
        _atomic_write(_relative_path(state.root, relpath), expected[relpath])
    return len(drift)


def _lint(root: Path) -> None:
    state = _load_state(root)
    expected = _render_all(state)
    errors: list[str] = []
    for projection in PROJECTIONS:
        path = _relative_path(state.root, projection.target)
        try:
            current = path.read_bytes()
        except OSError:
            errors.append(f"generated target is missing: {projection.target}")
            continue
        if not _valid_projection_envelope(current, projection):
            errors.append(f"projection marker or provenance cardinality is invalid: {projection.target}")
        if current != expected[projection.target]:
            errors.append(f"source/generator/body digest or exact target bytes drifted: {projection.target}")
    contract = state.source_bytes[CANONICAL_CONTRACT].decode("utf-8")
    claude = _read_canonical(state.root, CLAUDE_ADAPTER, CHECK_HARNESS_PROJECTION).decode("utf-8")
    forbidden = (
        "rizingblare-github-io",
        "Resume, Portfolio, Blog",
        "knowledge/",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "/Users/",
        "task_",
        "ctx_",
    )
    for value in forbidden:
        if value in contract or value in claude:
            errors.append(f"canonical entry contains forbidden project/model/runtime appendix value: {value}")
    if errors:
        raise HarnessError(CHECK_HARNESS_PROJECTION, errors)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError(CHECK_MODEL_LAUNCH, f"cannot read {label} stored record: {exc}") from None
    if not isinstance(value, dict):
        raise HarnessError(CHECK_MODEL_LAUNCH, f"{label} stored record must be a JSON object")
    return value


def _expected_binding(manifest: dict[str, Any], tool: str, tier: str) -> dict[str, str]:
    tools = manifest.get("tools")
    if not isinstance(tools, dict) or tool not in tools or tool != "codex":
        raise HarnessError(CHECK_MODEL_LAUNCH, f"tool has no verified launch binding: {tool}")
    config = tools[tool]
    if not isinstance(config, dict) or config.get("delegation") != "enabled":
        raise HarnessError(CHECK_MODEL_LAUNCH, f"tool delegation is not enabled: {tool}")
    bindings = config.get("model_bindings")
    if not isinstance(bindings, dict) or tier not in bindings:
        raise HarnessError(CHECK_MODEL_LAUNCH, f"unknown model tier: {tier}")
    binding = bindings[tier]
    if not isinstance(binding, dict):
        raise HarnessError(CHECK_MODEL_LAUNCH, f"invalid model tier: {tier}")
    return {"agent": tool, "model": binding["model"], "effort": binding["effort"]}


def _record_value(record: Any, path: str, label: str) -> Any:
    current = record
    try:
        for segment in path.split("."):
            current = current[segment]
    except (KeyError, TypeError):
        raise HarnessError(
            CHECK_MODEL_LAUNCH,
            f"{label} is missing Manifest-bound field {path}",
        ) from None
    return current


def _verify_launch_data(
    manifest: dict[str, Any],
    tool: str,
    tier: str,
    worker_record: dict[str, Any],
    completion_record: dict[str, Any],
    task_issued: str,
    dispatch_live: str,
) -> tuple[str, ...]:
    expected = _expected_binding(manifest, tool, tier)
    verification = manifest["tools"][tool]["launch_verification"]
    identity_sources = verification["identity_sources"]
    expected_identity = {
        identity_sources["task"]: task_issued,
        identity_sources["dispatch"]: dispatch_live,
    }
    worker_binding = verification["worker_record"]
    worker_fields = worker_binding["fields"]
    worker_allowed = worker_binding["allowed_values"]
    if _record_value(worker_record, worker_fields["success"], "worker record") is not worker_allowed["success"]:
        raise HarnessError(CHECK_MODEL_LAUNCH, "worker record is not an authoritative worker-show record")
    worker_task = _record_value(worker_record, worker_fields["task"], "worker record")
    worker_dispatch = _record_value(worker_record, worker_fields["dispatch"], "worker record")
    requested = _record_value(worker_record, worker_fields["requested"], "worker record")
    effective = _record_value(worker_record, worker_fields["effective"], "worker record")
    if (
        worker_task != expected_identity[identity_sources["task"]]
        or worker_dispatch != expected_identity[identity_sources["dispatch"]]
    ):
        raise HarnessError(CHECK_MODEL_LAUNCH, "worker taskId or dispatchId does not match the expected identity")
    if requested != expected or effective != expected:
        raise HarnessError(CHECK_MODEL_LAUNCH, "requested/effective launch differs from the expected agent/model/effort")

    completion_binding = verification["completion_record"]
    completion_fields = completion_binding["fields"]
    completion_allowed = completion_binding["allowed_values"]
    if _record_value(completion_record, completion_fields["success"], "completion record") is not completion_allowed["success"]:
        raise HarnessError(CHECK_MODEL_LAUNCH, "completion record is not an authoritative orchestration inbox record")
    messages = _record_value(completion_record, completion_fields["messages"], "completion record")
    if not isinstance(messages, list):
        raise HarnessError(CHECK_MODEL_LAUNCH, "completion stored record messages must be a list")
    matches: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        try:
            message_type = _record_value(message, completion_fields["type"], "completion message")
            if message_type != completion_allowed["type"]:
                continue
            payload = json.loads(
                _record_value(message, completion_fields["payload"], "completion message")
            )
        except (HarnessError, TypeError, json.JSONDecodeError):
            continue
        try:
            if (
                _record_value(payload, completion_fields["task"], "completion payload")
                == expected_identity[identity_sources["task"]]
                and _record_value(payload, completion_fields["dispatch"], "completion payload")
                == expected_identity[identity_sources["dispatch"]]
            ):
                matches.append(payload)
        except HarnessError:
            continue
    if len(matches) != 1:
        raise HarnessError(CHECK_MODEL_LAUNCH, "completion task/dispatch join is missing or ambiguous")
    completion = matches[0]
    if _record_value(completion, completion_fields["outcome"], "completion payload") != completion_allowed["outcome"]:
        raise HarnessError(CHECK_MODEL_LAUNCH, "completion outcome is not succeeded")
    files_modified = _record_value(
        completion,
        completion_fields["files_modified"],
        "completion payload",
    )
    if (
        not isinstance(files_modified, list)
        or not files_modified
        or any(
            not isinstance(relpath, str)
            or not relpath
            or "\\" in relpath
            or PurePosixPath(relpath).is_absolute()
            or any(part in {"", ".", ".."} for part in PurePosixPath(relpath).parts)
            for relpath in files_modified
        )
        or len(files_modified) != len(set(files_modified))
    ):
        raise HarnessError(
            CHECK_MODEL_LAUNCH,
            "completion filesModified must be a non-empty unique list of safe repository paths",
        )
    return tuple(files_modified)


def _copy_fixture_tree(source_root: Path, target_root: Path) -> None:
    state = _load_state(source_root)
    paths = {
        state.registry_locator,
        state.registry_doc["canonical_contract"],
        state.project_manifest,
        CLAUDE_ADAPTER,
        SYNC_SKILL,
        LINT_SKILL,
        GENERATOR_PATH,
    }
    for declaration in state.registry.declarations:
        for field_name in (
            "charter",
            "entry_document",
            "artifact_schema",
            "producer_gate",
            "exposure_gate",
        ):
            value = declaration.data.get(field_name)
            if isinstance(value, str) and value != "not-applicable":
                paths.add(value)
    language_lint = state.registry_doc["language_lint"]
    paths.add(language_lint["check"])
    paths.update(language_lint["coverage"])
    for relpath in sorted(paths):
        source = source_root / relpath
        if not source.is_file():
            continue
        target = target_root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def _write_fixture(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _fresh_fixture(source_root: Path) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    holder = tempfile.TemporaryDirectory(prefix="harness-manifest-fixture-")
    root = Path(holder.name)
    _copy_fixture_tree(source_root, root)
    return holder, root


def _fresh_preflight(source_root: Path, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(source_root / GENERATOR_PATH),
            "preflight",
            "--root",
            str(root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def _expect_error(check_id: str, action: Callable[[], Any]) -> None:
    try:
        action()
    except HarnessError as exc:
        if exc.check_id != check_id:
            raise AssertionError(f"expected {check_id}, got {exc.check_id}") from exc
        return
    raise AssertionError(f"expected {check_id} failure")


def _record_assign(record: dict[str, Any], path: str, value: Any) -> None:
    segments = path.split(".")
    current = record
    for segment in segments[:-1]:
        child = current.setdefault(segment, {})
        if not isinstance(child, dict):
            raise AssertionError(f"fixture field path collides at {path}")
        current = child
    current[segments[-1]] = value


def _fixture_launch_records(
    profile: dict[str, Any], manifest: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    task_id = "task_fixture_launch"
    dispatch_id = "ctx_fixture_launch"
    launch = {"agent": profile["agent"], "model": profile["model"], "effort": profile["effort"]}
    verification = manifest["tools"]["codex"]["launch_verification"]
    worker_binding = verification["worker_record"]
    worker_fields = worker_binding["fields"]
    worker_allowed = worker_binding["allowed_values"]
    worker: dict[str, Any] = {}
    _record_assign(worker, worker_fields["success"], worker_allowed["success"])
    _record_assign(worker, worker_fields["task"], task_id)
    _record_assign(worker, worker_fields["dispatch"], dispatch_id)
    _record_assign(worker, worker_fields["requested"], launch)
    _record_assign(worker, worker_fields["effective"], dict(launch))

    completion_binding = verification["completion_record"]
    completion_fields = completion_binding["fields"]
    completion_allowed = completion_binding["allowed_values"]
    payload: dict[str, Any] = {}
    _record_assign(payload, completion_fields["task"], task_id)
    _record_assign(payload, completion_fields["dispatch"], dispatch_id)
    _record_assign(payload, completion_fields["outcome"], completion_allowed["outcome"])
    _record_assign(payload, completion_fields["files_modified"], profile["files_modified"])
    message: dict[str, Any] = {}
    _record_assign(message, completion_fields["type"], completion_allowed["type"])
    _record_assign(
        message,
        completion_fields["payload"],
        json.dumps(payload, separators=(",", ":")),
    )
    completion: dict[str, Any] = {}
    _record_assign(completion, completion_fields["success"], completion_allowed["success"])
    _record_assign(completion, completion_fields["messages"], [message])
    return worker, completion


def _run_fixtures(fixture_root: Path) -> int:
    source_root = fixture_root.resolve().parents[2]
    source_state = _load_state(source_root)
    registry_locator = source_state.registry_locator
    project_manifest = source_state.project_manifest
    locator_line = next(
        line
        for line in source_state.source_bytes[CANONICAL_CONTRACT].decode("utf-8").splitlines()
        if REGISTRY_LOCATOR_MARKER.fullmatch(line)
    )
    try:
        manifest = json.loads((fixture_root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(CHECK_HARNESS_PROJECTION, f"fixture manifest is unreadable: {exc}") from None
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "cases"} or manifest.get("schema_version") != 1:
        raise HarnessError(CHECK_HARNESS_PROJECTION, "fixture manifest root shape is invalid")
    cases = manifest.get("cases")
    expected_cases = [
        ("valid-minimal", "pass", {"name", "expect"}),
        ("manifest-registry-shape", CHECK_PROJECT_MANIFEST, {"name", "expect"}),
        ("path-marker-safety", CHECK_HARNESS_PROJECTION, {"name", "expect"}),
        ("bootstrap-resume", CHECK_HARNESS_PROJECTION, {"name", "expect"}),
        ("projection-drift", CHECK_HARNESS_PROJECTION, {"name", "expect"}),
        (
            "launch-identity",
            CHECK_MODEL_LAUNCH,
            {"name", "expect", "profile"},
        ),
    ]
    if not isinstance(cases, list) or len(cases) != len(expected_cases):
        raise HarnessError(CHECK_HARNESS_PROJECTION, "fixture manifest must contain the exact six ordered cases")
    for index, expected in enumerate(expected_cases):
        case = cases[index]
        name, expect, keys = expected
        if (
            not isinstance(case, dict)
            or set(case) != keys
            or case.get("name") != name
            or case.get("expect") != expect
        ):
            raise HarnessError(
                CHECK_HARNESS_PROJECTION,
                f"fixture manifest case {index} has an invalid closed shape, name, or expect value",
            )
    profile = cases[-1].get("profile")
    if (
        not isinstance(profile, dict)
        or set(profile) != {"agent", "model", "effort", "files_modified"}
        or profile.get("agent") != "codex"
        or not isinstance(profile.get("model"), str)
        or not isinstance(profile.get("effort"), str)
        or not isinstance(profile.get("files_modified"), list)
        or not profile["files_modified"]
        or any(not isinstance(path, str) or not path for path in profile["files_modified"])
    ):
        raise HarnessError(CHECK_MODEL_LAUNCH, "launch fixture profile has an invalid closed shape")

    holder, root = _fresh_fixture(source_root)
    try:
        state = _load_state(root)
        rendered = _render_all(state)
        if len(rendered) != 2 or any(b'"registry_locator"' in data for data in rendered.values()):
            raise AssertionError("generated skill target count or provenance shape is invalid")
        for relpath, data in rendered.items():
            _atomic_write(_relative_path(root, relpath), data)
        _lint(root)
        if _sync(root, True) != 0:
            raise AssertionError("valid sync check changed files")
        worker, completion = _fixture_launch_records(profile, state.manifest)
        _verify_launch_data(state.manifest, "codex", "routine", worker, completion, "task_fixture_launch", "ctx_fixture_launch")
        fresh_success = _fresh_preflight(source_root, root)
        if fresh_success.returncode != 0:
            raise AssertionError(f"fresh-process valid preflight failed: {fresh_success.stderr}")
    finally:
        holder.cleanup()

    manifest_variants: list[Callable[[Path], None]] = [
        lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"canonical_contract: AGENTS.md\n", b"")),
        lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(f"project_manifest: {project_manifest}".encode(), b"project_manifest:")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"  metadata_keys: english\n", b"  metadata_keys: english\n  unknown: value\n")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"    mechanical_enforcement: layout-registry\n", b"    mechanical_enforcement: implicit\n")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"It is the source workspace for the public GitHub Pages site.", b"")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"This repository is not the distribution source for the generic agent harness. It is also not a reusable site template.", b"One. Two. Three. Four. Five.")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"          files_modified: filesModified\n", b"")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"          files_modified: filesModified\n", b"          files_modified: filesModified\n          unknown: value\n")),
        lambda candidate: _write_fixture(candidate / project_manifest, (candidate / project_manifest).read_bytes().replace(b"          files_modified: filesModified\n", b"          files_modified: changedFiles\n")),
    ]
    for mutate in manifest_variants:
        holder, root = _fresh_fixture(source_root)
        try:
            mutate(root)
            _expect_error(CHECK_PROJECT_MANIFEST, lambda: _load_state(root))
            fresh_failure = _fresh_preflight(source_root, root)
            if fresh_failure.returncode == 0:
                raise AssertionError("fresh-process invalid Manifest preflight passed")
        finally:
            holder.cleanup()

    path_variants: list[tuple[str, Callable[[Path], None]]] = [
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(f"project_manifest: {project_manifest}".encode(), b"project_manifest: /tmp/manifest.yaml"))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(f"project_manifest: {project_manifest}".encode(), b"project_manifest: ../manifest.yaml"))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"  - select: schema/**\n    role: contract", b"  - select: schema/**\n    role: support"))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"    owner: harness\n", b"", 1))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"    provenance_layer: operating-contract\n", b"    provenance_layer: unknown-layer\n", 1))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"    exposure: repository-only\n", b"    exposure: public-site\n", 1))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / registry_locator, (candidate / registry_locator).read_bytes().replace(b"  outside_coverage: contract-policy-only\n", b"  outside_coverage: unchecked\n"))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / "knowledge/README.md", (candidate / "knowledge/README.md").read_bytes().replace(b"Canonical authoring-content root for the concept wiki.", b"One. Two. Three. Four. Five."))),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / CANONICAL_CONTRACT, (candidate / CANONICAL_CONTRACT).read_bytes().replace(BEGIN_SOURCE_MARKER.encode(), b"<!-- harness:begn v1 -->"))),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / CANONICAL_CONTRACT, (candidate / CANONICAL_CONTRACT).read_bytes().replace(BEGIN_SOURCE_MARKER.encode(), (BEGIN_SOURCE_MARKER + "\n" + BEGIN_SOURCE_MARKER).encode()))),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / CANONICAL_CONTRACT, (candidate / CANONICAL_CONTRACT).read_bytes().replace((locator_line + "\n").encode(), b""))),
        (CHECK_PROJECT_MANIFEST, lambda candidate: _write_fixture(candidate / CANONICAL_CONTRACT, (candidate / CANONICAL_CONTRACT).read_bytes().replace(locator_line.encode(), b"<!-- harness:registry-locator schema/kernel/changed.yaml -->"))),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / CANONICAL_CONTRACT, (candidate / CANONICAL_CONTRACT).read_bytes().replace(locator_line.encode(), (locator_line + "\n" + locator_line).encode()))),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / CLAUDE_ADAPTER, (candidate / CLAUDE_ADAPTER).read_bytes() + b"extra\n")),
        (CHECK_HARNESS_PROJECTION, lambda candidate: _write_fixture(candidate / SYNC_SKILL, (candidate / SYNC_SKILL).read_bytes().replace(b"name: harness-sync", b"name: wrong"))),
    ]
    for expected_check, mutate in path_variants:
        holder, root = _fresh_fixture(source_root)
        try:
            mutate(root)
            _expect_error(expected_check, lambda: _load_state(root))
            fresh_failure = _fresh_preflight(source_root, root)
            if fresh_failure.returncode == 0:
                raise AssertionError("fresh-process invalid path or marker preflight passed")
        finally:
            holder.cleanup()

    holder, root = _fresh_fixture(source_root)
    outside_holder = tempfile.TemporaryDirectory(prefix="harness-outside-")
    try:
        manifest_path = root / project_manifest
        manifest_path.unlink()
        outside_manifest = Path(outside_holder.name) / "manifest.yaml"
        shutil.copyfile(source_root / project_manifest, outside_manifest)
        manifest_path.symlink_to(outside_manifest)
        _expect_error(CHECK_PROJECT_MANIFEST, lambda: _load_state(root))
    finally:
        holder.cleanup()
        outside_holder.cleanup()

    holder, root = _fresh_fixture(source_root)
    try:
        state = _load_state(root)
        for relpath, data in _render_all(state).items():
            _atomic_write(_relative_path(root, relpath), data)
        target = root / PROJECTIONS[0].target
        _write_fixture(target, target.read_bytes().replace(b'"body_sha256":"', b'"body_sha256":"0', 1))
        _expect_error(CHECK_HARNESS_PROJECTION, lambda: _lint(root))
    finally:
        holder.cleanup()

    holder, root = _fresh_fixture(source_root)
    try:
        state = _load_state(root)
        plan_bytes = _canonical_json_bytes(_plan_document(state))
        plan_rel = "schema/stages/bootstrap/fixture-plan.json"
        _exclusive_write(root / plan_rel, plan_bytes)
        digest = _sha256(plan_bytes)
        before = {projection.target: (root / projection.target).read_bytes() if (root / projection.target).is_file() else None for projection in PROJECTIONS}
        for source in (
            state.registry_doc["canonical_contract"],
            state.project_manifest,
            SYNC_SKILL,
            LINT_SKILL,
        ):
            original = (root / source).read_bytes()
            _write_fixture(root / source, original.replace(b"\n", b" \n", 1))
            _expect_error(CHECK_HARNESS_PROJECTION, lambda: _apply_plan(root, plan_rel, digest))
            after = {projection.target: (root / projection.target).read_bytes() if (root / projection.target).is_file() else None for projection in PROJECTIONS}
            if after != before:
                raise AssertionError("input drift wrote a bootstrap target")
            _write_fixture(root / source, original)
    finally:
        holder.cleanup()

    holder, root = _fresh_fixture(source_root)
    try:
        state = _load_state(root)
        plan = _plan_document(state)
        plan_bytes = _canonical_json_bytes(plan)
        plan_rel = "schema/stages/bootstrap/fixture-plan.json"
        _exclusive_write(root / plan_rel, plan_bytes)
        digest = _sha256(plan_bytes)
        expected = _render_all(state)
        if any(row["old"] != "absent" for row in plan["targets"]):
            raise AssertionError("bootstrap resume plan did not start with both targets absent")
        first_target = sorted(expected)[0]
        _atomic_write(root / first_target, expected[first_target])
        existing_targets = [path for path in sorted(expected) if (root / path).is_file()]
        if existing_targets != [first_target]:
            raise AssertionError("bootstrap resume fixture did not seed exactly one target")
        command = [
            sys.executable,
            str(source_root / GENERATOR_PATH),
            "bootstrap",
            "--root",
            str(root),
            "--plan",
            plan_rel,
            "--plan-sha256",
            digest,
        ]
        resumed = subprocess.run(command, text=True, capture_output=True, check=False)
        if resumed.returncode != 0 or "bootstrap apply: PASS (changed 1)" not in resumed.stdout:
            raise AssertionError(f"fresh-process bootstrap resume failed: {resumed.stderr}")
        if any((root / path).read_bytes() != data for path, data in expected.items()):
            raise AssertionError("resumed bootstrap differs from a complete execution")
        noop = subprocess.run(command, text=True, capture_output=True, check=False)
        if noop.returncode != 0 or "changed 0" not in noop.stdout:
            raise AssertionError("third bootstrap execution was not a no-op")
    finally:
        holder.cleanup()

    for projection in PROJECTIONS:
        holder, root = _fresh_fixture(source_root)
        try:
            state = _load_state(root)
            for relpath, data in _render_all(state).items():
                _atomic_write(root / relpath, data)
            target = root / projection.target
            current = target.read_bytes()
            first, provenance, body = current.split(b"\n", 2)
            _write_fixture(target, first + b"\n" + provenance + b"\nX" + body)
            _expect_error(CHECK_HARNESS_PROJECTION, lambda: _lint(root))
            if _sync(root, False) != 1:
                raise AssertionError("projection drift sync did not change exactly one target")
            _lint(root)
        finally:
            holder.cleanup()

    holder, root = _fresh_fixture(source_root)
    try:
        state = _load_state(root)
        worker, completion = _fixture_launch_records(profile, state.manifest)
        task_id, dispatch_id = "task_fixture_launch", "ctx_fixture_launch"
        verification = state.manifest["tools"]["codex"]["launch_verification"]
        worker_fields = verification["worker_record"]["fields"]
        completion_fields = verification["completion_record"]["fields"]
        variants: list[tuple[dict[str, Any], dict[str, Any], str, str]] = []
        requested = copy.deepcopy(worker)
        requested_launch = copy.deepcopy(
            _record_value(requested, worker_fields["requested"], "fixture worker")
        )
        requested_launch["model"] = "wrong"
        _record_assign(requested, worker_fields["requested"], requested_launch)
        variants.append((requested, completion, task_id, dispatch_id))
        effective = copy.deepcopy(worker)
        effective_launch = copy.deepcopy(
            _record_value(effective, worker_fields["effective"], "fixture worker")
        )
        effective_launch["effort"] = "wrong"
        _record_assign(effective, worker_fields["effective"], effective_launch)
        variants.append((effective, completion, task_id, dispatch_id))
        variants.append((worker, completion, "task_wrong", dispatch_id))
        variants.append((worker, completion, task_id, "ctx_wrong"))
        changed_completion = copy.deepcopy(completion)
        changed_messages = _record_value(
            changed_completion,
            completion_fields["messages"],
            "fixture completion",
        )
        changed_message = changed_messages[0]
        payload = json.loads(
            _record_value(
                changed_message,
                completion_fields["payload"],
                "fixture completion message",
            )
        )
        _record_assign(payload, completion_fields["files_modified"], ["../outside"])
        _record_assign(
            changed_message,
            completion_fields["payload"],
            json.dumps(payload, separators=(",", ":")),
        )
        variants.append((worker, changed_completion, task_id, dispatch_id))
        missing_files = copy.deepcopy(completion)
        missing_messages = _record_value(
            missing_files,
            completion_fields["messages"],
            "fixture completion",
        )
        missing_message = missing_messages[0]
        missing_payload = json.loads(
            _record_value(
                missing_message,
                completion_fields["payload"],
                "fixture completion message",
            )
        )
        del missing_payload[completion_fields["files_modified"]]
        _record_assign(
            missing_message,
            completion_fields["payload"],
            json.dumps(missing_payload, separators=(",", ":")),
        )
        variants.append((worker, missing_files, task_id, dispatch_id))
        for candidate_worker, candidate_completion, candidate_task, candidate_dispatch in variants:
            _expect_error(
                CHECK_MODEL_LAUNCH,
                lambda w=candidate_worker, c=candidate_completion, t=candidate_task, d=candidate_dispatch: _verify_launch_data(
                    state.manifest, "codex", "routine", w, c, t, d
                ),
            )
    finally:
        holder.cleanup()
    return len(cases)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--root", default=".")

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--root", default=".")
    bootstrap.add_argument("--check", action="store_true")
    bootstrap.add_argument("--out")
    bootstrap.add_argument("--plan")
    bootstrap.add_argument("--plan-sha256")

    sync = subparsers.add_parser("sync")
    sync.add_argument("--root", default=".")
    sync.add_argument("--check", action="store_true")

    lint = subparsers.add_parser("lint")
    lint.add_argument("--root", default=".")

    verify = subparsers.add_parser("verify-launch")
    verify.add_argument("--root", default=".")
    verify.add_argument("--tool", required=True)
    verify.add_argument("--tier", required=True)
    verify.add_argument("--worker-record", required=True)
    verify.add_argument("--completion-record", required=True)
    verify.add_argument("--task-id", required=True)
    verify.add_argument("--dispatch-id", required=True)

    fixtures = subparsers.add_parser("fixtures")
    fixtures.add_argument("--root", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "preflight":
            state = _load_state(args.root)
            expected = _render_all(state)
            print(f"preflight: PASS ({len(expected)} deterministic targets calculable)")
        elif args.command == "bootstrap":
            root = Path(args.root).resolve()
            creating = args.check and args.out and not args.plan and not args.plan_sha256
            applying = not args.check and not args.out and args.plan and args.plan_sha256
            if not creating and not applying:
                raise HarnessError(
                    CHECK_HARNESS_PROJECTION,
                    "bootstrap requires either --check --out or --plan --plan-sha256",
                )
            if creating:
                digest, targets = _create_plan(root, args.out)
                print(f"bootstrap plan sha256: {digest}")
                for row in targets:
                    print(f"target {row['path']} old={row['old']} new_sha256={row['new_sha256']}")
            else:
                changed, states = _apply_plan(root, args.plan, args.plan_sha256)
                for relpath, target_state in states:
                    print(f"target {relpath} state={target_state}")
                print(f"bootstrap apply: PASS (changed {changed})")
        elif args.command == "sync":
            changed = _sync(Path(args.root).resolve(), args.check)
            label = "sync check" if args.check else "sync"
            print(f"{label}: PASS (changed {changed})")
        elif args.command == "lint":
            _lint(Path(args.root).resolve())
            print("harness lint: PASS (project-manifest, harness-projection)")
        elif args.command == "verify-launch":
            state = _load_state(args.root)
            worker = _read_json(Path(args.worker_record), "worker")
            completion = _read_json(Path(args.completion_record), "completion")
            files_modified = _verify_launch_data(
                state.manifest,
                args.tool,
                args.tier,
                worker,
                completion,
                args.task_id,
                args.dispatch_id,
            )
            print(
                "launch verification: PASS "
                f"(model-launch-verification; filesModified={','.join(files_modified)})"
            )
        elif args.command == "fixtures":
            case_count = _run_fixtures(Path(args.root))
            print(
                f"harness fixtures: PASS ({case_count} cases; "
                "bootstrap input-drift target writes 0)"
            )
    except HarnessError as exc:
        for message in exc.messages:
            print(f"FAIL: [{exc.check_id}] {message}", file=sys.stderr)
        return 1
    except AssertionError as exc:
        print(f"FAIL: [harness-projection] fixture assertion: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

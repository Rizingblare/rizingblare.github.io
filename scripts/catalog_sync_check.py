"""Gate plugin: the search shards must be regenerable from knowledge/catalog.

Wired into scripts/check.sh as `--plugin scripts.catalog_sync_check:PLUGIN`.
A stale shard means someone edited a build output instead of its catalog
source (or edited the source and forgot to rebuild); either way the two
layers have diverged and the derivation direction is broken.
"""
from __future__ import annotations

import json
import re
from collections import namedtuple

Finding = namedtuple("Finding", "check_id message path")

GUIDE = "knowledge/guides/document-authoring.md"
PROGRAM_COUNT_PATTERNS = (
    ("Korean body", re.compile(r"(?m)^([0-9][0-9,]*)개 개념 문서 프로그램에서")),
    (
        "English brief",
        re.compile(r"(?m)^Authoring blueprint for the ~([0-9][0-9,]*)-document wiki program:"),
    ),
)


def _run(ctx):
    try:
        import importlib

        build = importlib.import_module("scripts.build_search")
    except Exception as exc:  # pragma: no cover - import environment problem
        yield Finding("catalog-sync", f"cannot import scripts.build_search: {exc}", "")
        return
    try:
        outputs = build.build_outputs()
    except SystemExit as exc:
        yield Finding("catalog-sync", f"catalog sources unreadable: {exc}", "")
        return
    catalog_count = sum(
        len(json.loads(source.read_text(encoding="utf-8")))
        for source in sorted(build.CATALOG.glob("*.json"))
    )
    for rel, content in outputs.items():
        path = ctx.root / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            yield Finding(
                "catalog-sync",
                "stale build output; regenerate with: python3 scripts/build_search.py",
                rel,
            )
    guide = ctx.read_text(GUIDE)
    if guide is None:
        yield Finding("catalog-sync", "authoring guide is missing or unreadable", GUIDE)
        return
    for label, pattern in PROGRAM_COUNT_PATTERNS:
        matches = pattern.findall(guide)
        if len(matches) != 1:
            yield Finding(
                "catalog-sync",
                f"expected exactly one explicit program count in {label}, found {len(matches)}",
                GUIDE,
            )
            continue
        guide_count = int(matches[0].replace(",", ""))
        if guide_count != catalog_count:
            yield Finding(
                "catalog-sync",
                f"{label} program count {guide_count:,} does not match catalog total {catalog_count:,}",
                GUIDE,
            )


Check = namedtuple("Check", "check_id run")
PLUGIN = namedtuple("Plugin", "checks")(checks=(Check("catalog-sync", _run),))

"""Gate plugin: the search shards must be regenerable from knowledge/catalog.

Wired into scripts/check.sh as `--plugin scripts.catalog_sync_check:PLUGIN`.
A stale shard means someone edited a build output instead of its catalog
source (or edited the source and forgot to rebuild); either way the two
layers have diverged and the derivation direction is broken.
"""
from __future__ import annotations

from collections import namedtuple

Finding = namedtuple("Finding", "check_id message path")


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
    for rel, content in outputs.items():
        path = ctx.root / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            yield Finding(
                "catalog-sync",
                "stale build output; regenerate with: python3 scripts/build_search.py",
                rel,
            )


Check = namedtuple("Check", "check_id run")
PLUGIN = namedtuple("Plugin", "checks")(checks=(Check("catalog-sync", _run),))

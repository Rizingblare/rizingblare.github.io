"""Regenerate the wiki search shards from the editable catalog sources.

Derivation direction (declared in knowledge/README.md):

    knowledge/catalog/<domain>.json   --   the editable source of truth
        -> search/wiki/<domain>.json       public published/pending projection
        -> search/manifest.json            public shard locations and counts
        -> build-report.json               public document/domain counts

Usage:
    python3 scripts/build_search.py            # write outputs
    python3 scripts/build_search.py --check    # exit 1 if outputs are stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "knowledge" / "catalog"
SHARDS = ROOT / "search" / "wiki"
MANIFEST = ROOT / "search" / "manifest.json"
BUILD_REPORT = ROOT / "build-report.json"


def dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


REQUIRED_KEYS = {"type", "id", "title", "status", "summary", "primaryDomain", "domain"}
PUBLIC_STATUSES = {"published", "pending"}
PUBLIC_KEYS = ("type", "id", "title", "aliases", "status", "summary", "domain")


def public_item(item: dict) -> dict | None:
    """Project one catalog record into the public search contract."""
    if item.get("status") not in PUBLIC_STATUSES:
        return None
    projected = {key: item[key] for key in PUBLIC_KEYS if key in item}
    if item["status"] == "published":
        projected["url"] = item.get("url")
    return projected


def build_outputs() -> dict[str, str]:
    """Return {relpath: content} for every file this build owns.

    The owned set is exactly `search/wiki/<stem>.json` for each catalog
    source: a shard with no matching catalog file is an orphan and is
    reported (deleting a catalog source must not silently strand its shard).
    Items are validated: required keys, id unique across all domains, and
    domain fields matching the file stem.
    """
    sources = sorted(CATALOG.glob("*.json"))
    if not sources:
        raise SystemExit(f"no catalog sources under {CATALOG}")
    outputs: dict[str, str] = {}
    counts: dict[str, int] = {}
    published_count = 0
    pending_count = 0
    seen_ids: dict[str, str] = {}
    errors: list[str] = []
    for src in sources:
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{src.name}: invalid JSON: {exc}")
            continue
        if not isinstance(data, list):
            errors.append(f"{src.name}: expected a JSON array of concepts")
            continue
        for i, item in enumerate(data):
            where = f"{src.name}[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{where}: not an object")
                continue
            missing = REQUIRED_KEYS - item.keys()
            if missing:
                errors.append(f"{where}: missing keys {sorted(missing)}")
            cid = item.get("id")
            if not isinstance(cid, str) or not cid:
                errors.append(f"{where}: id must be a non-empty string, got {cid!r}")
            elif cid in seen_ids:
                errors.append(f"{where}: duplicate id {cid!r} (also in {seen_ids[cid]})")
            else:
                seen_ids[cid] = src.name
            for key in ("primaryDomain", "domain"):
                if key in item and item[key] != src.stem:
                    errors.append(f"{where}: {key}={item[key]!r} != file domain {src.stem!r}")
            if item.get("status") == "published" and not item.get("url"):
                errors.append(f"{where}: published item requires a public url")
        public_data = []
        for item in data:
            if not isinstance(item, dict):
                continue
            projected = public_item(item)
            if projected:
                public_data.append(projected)
        counts[src.stem] = len(public_data)
        published_count += sum(1 for item in public_data if item["status"] == "published")
        pending_count += sum(1 for item in public_data if item["status"] == "pending")
        outputs[f"search/wiki/{src.stem}.json"] = dumps(public_data)
    owned = {f"search/wiki/{s.stem}.json" for s in sources}
    for shard in sorted(SHARDS.glob("*.json")):
        rel = f"search/wiki/{shard.name}"
        if rel not in owned:
            errors.append(f"{rel}: orphan shard with no catalog source (delete it or add the source)")
    if errors:
        raise SystemExit("catalog validation failed:\n  " + "\n  ".join(errors))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    order = [entry["id"] for entry in manifest.get("wiki", [])]
    known = [d for d in order if d in counts] + [d for d in sorted(counts) if d not in order]
    manifest.pop("generatedAt", None)
    manifest["wiki"] = [
        {"id": d, "count": counts[d], "url": f"/search/wiki/{d}.json"}
        for d in known
        if counts[d]
    ]
    manifest["conceptCount"] = sum(counts.values())
    outputs["search/manifest.json"] = dumps(manifest)
    report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    report.pop("generatedAt", None)
    report.pop("concepts", None)
    report["publicWikiDocuments"] = sum(counts.values())
    report["publishedWikiDocuments"] = published_count
    report["inProgressWikiDocuments"] = pending_count
    report["domains"] = sum(1 for count in counts.values() if count)
    outputs["build-report.json"] = dumps(report)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify outputs are current, write nothing")
    args = parser.parse_args(argv)

    outputs = build_outputs()
    stale = []
    for rel, content in outputs.items():
        path = ROOT / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            stale.append(rel)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    if args.check:
        for rel in stale:
            print(f"stale: {rel} (run: python3 scripts/build_search.py)")
        return 1 if stale else 0
    for rel in stale:
        print(f"wrote {rel}")
    if not stale:
        print("outputs already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())

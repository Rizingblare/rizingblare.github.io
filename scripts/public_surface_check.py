"""Validate the catalog-to-public publication boundary."""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "knowledge" / "catalog"
PUBLIC_STATUSES = {"published", "pending"}
PUBLIC_KEYS = {"type", "id", "title", "aliases", "status", "summary", "domain", "url"}
PUBLIC_HTML_FILES = ("404.html", "index.html")
PUBLIC_HTML_ROOTS = ("404-page", "blog", "portfolio", "resume", "search", "wiki")
NON_PUBLIC_SCAN_DIRS = {
    ".claude",
    ".git",
    ".impeccable",
    ".orca",
    ".playwright-mcp",
    "__pycache__",
    "dist",
    "node_modules",
    "temp",
    "tmp",
}
BANNED_PUBLIC_COPY = (
    "Static build ready for GitHub Pages",
    "세부 학력 정보 입력",
    "취득일 입력",
    "추가 자격증명 입력",
    "발급기관 입력",
    "YYYY.MM.DD",
    "프로토타입에서는",
    "실제 사본으로 교체",
    "실제 적용 시",
    "개념 노트",
    'id="pending-concepts"',
    'option value="proposed"',
)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
MISLEADING_METRICS = {
    "1,399": (
        re.compile(r"1,399\s*개(?:의)?\s*(?:모두\s*)?(?:공개(?:된|하는)?|발행(?:된)?)\s*(?:문서|자료|개념|콘텐츠)"),
        re.compile(r"(?:공개|발행)(?:된)?\s*(?:문서|자료|개념|콘텐츠)\s*(?:는|은|가|를|:)?\s*1,399\s*개"),
        re.compile(r"(?:공개|발행)(?:된)?\s*1,399\s*개\s*(?:문서|자료|개념|콘텐츠)"),
        re.compile(r"\b1,399\s+public\s+(?:documents|items|concepts|content)\b", re.IGNORECASE),
    ),
    "682": (
        re.compile(r"682\s*(?:개(?:의)?\s*)?(?:공개(?:된)?|구성)\s*(?:문서|자료|개념|콘텐츠)?"),
        re.compile(r"(?:공개|발행)(?:된)?\s*(?:문서|자료|개념|콘텐츠)\s*(?:는|은|가|를|:)?\s*682\s*개"),
        re.compile(r"\b682\s+public\s+(?:documents|items|concepts|content)\b", re.IGNORECASE),
    ),
}
CERTIFICATE_AUTHORING_PLACEHOLDER_PATTERNS = (
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
    re.compile(r"자리\s*표시자|모형"),
    re.compile(
        r"\breplace\s+(?:this\s+)?(?:image\s+)?with\s+(?:an?\s+)?"
        r"(?:redacted\s+|masked\s+)?(?:certificate\s+)?(?:image|copy|scan)\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?:자격증\s*)?(?:이미지|사본|스캔(?:본)?).{0,40}(?:교체할\s*위치|(?:으)?로\s*교체)"),
)


def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key: value or "" for key, value in attrs}


def classes(values: dict[str, str]) -> set[str]:
    return set(values.get("class", "").split())


def normalized_text(parts: list[str]) -> str:
    return " ".join(" ".join(parts).split())


class Element:
    def __init__(self, tag: str, attrs: dict[str, str] | None = None, line: int = 0) -> None:
        self.tag = tag
        self.attrs = attrs or {}
        self.line = line
        self.children: list[Element | str] = []


class ParsedHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("document")
        self._stack = [self.root]

    def _add(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        node = Element(tag, attrs_dict(attrs), self.getpos()[0])
        self._stack[-1].children.append(node)
        if push:
            self._stack.append(node)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs, tag not in VOID_TAGS)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs, False)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == tag:
                del self._stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self._stack[-1].children.append(data)


def elements(node: Element):
    for child in node.children:
        if isinstance(child, Element):
            yield child
            yield from elements(child)


def element_text(node: Element) -> str:
    parts = [child if isinstance(child, str) else element_text(child) for child in node.children]
    return normalized_text(parts)


def prose_text(node: Element) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag not in {"script", "style"}:
            parts.extend(child.attrs.get(key, "") for key in ("content", "alt", "title", "aria-label"))
            parts.append(prose_text(child))
    return normalized_text(parts)


def first_text(node: Element, tag: str) -> str:
    return next((element_text(child) for child in elements(node) if child.tag == tag), "")


def json_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in json_strings(child)]
    if isinstance(value, list):
        return [text for child in value for text in json_strings(child)]
    return []


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def public_files(directory: Path, suffix: str) -> list[Path]:
    paths: list[Path] = []
    for current, directories, filenames in os.walk(directory):
        directories[:] = [
            name for name in directories
            if not name.startswith(".") and name not in NON_PUBLIC_SCAN_DIRS
        ]
        paths.extend(Path(current) / name for name in filenames if name.endswith(suffix))
    return paths


def public_html_paths() -> list[Path]:
    paths = [ROOT / name for name in PUBLIC_HTML_FILES]
    for root_name in PUBLIC_HTML_ROOTS:
        paths.extend(public_files(ROOT / root_name, ".html"))
    return sorted(path for path in paths if path.is_file())


def main() -> int:
    failures: list[str] = []
    catalog_rows: list[dict] = []
    public_by_domain: dict[str, list[dict]] = defaultdict(list)
    public_by_id: dict[str, dict] = {}
    statuses: Counter[str] = Counter()

    for source in sorted(CATALOG.glob("*.json")):
        rows = json.loads(source.read_text(encoding="utf-8"))
        catalog_rows.extend(rows)
        for row in rows:
            statuses[row.get("status", "")] += 1
            if row.get("status") in PUBLIC_STATUSES:
                public_by_domain[source.stem].append(row)
                public_by_id[row["id"]] = row

    for source in sorted(CATALOG.glob("*.json")):
        shard_path = ROOT / "search" / "wiki" / source.name
        shard = json.loads(shard_path.read_text(encoding="utf-8"))
        expected_count = len(public_by_domain[source.stem])
        if len(shard) != expected_count:
            failures.append(f"{rel(shard_path)}: {len(shard)} rows, expected {expected_count} public rows")
        for index, item in enumerate(shard):
            where = f"{rel(shard_path)}[{index}]"
            if item.get("status") not in PUBLIC_STATUSES:
                failures.append(f"{where}: non-public status {item.get('status')!r}")
            extra = set(item) - PUBLIC_KEYS
            if extra:
                failures.append(f"{where}: internal fields exposed: {sorted(extra)}")
            if item.get("status") == "published" and not item.get("url"):
                failures.append(f"{where}: published item has no url")
            if item.get("status") == "pending" and "url" in item:
                failures.append(f"{where}: pending item must not render as a completed link")

    public_count = sum(len(rows) for rows in public_by_domain.values())
    published_count = statuses["published"]
    pending_count = statuses["pending"]
    active_domains = {domain for domain, rows in public_by_domain.items() if rows}

    manifest_path = ROOT / "search" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "generatedAt" in manifest:
        failures.append("search/manifest.json: generatedAt is build metadata, not public search data")
    if manifest.get("conceptCount") != public_count:
        failures.append(f"search/manifest.json: conceptCount must be {public_count}")
    manifest_domains = {entry.get("id") for entry in manifest.get("wiki", [])}
    if manifest_domains != active_domains:
        failures.append(
            f"search/manifest.json: domains {sorted(manifest_domains)} != active public domains {sorted(active_domains)}"
        )
    for entry in manifest.get("wiki", []):
        expected = len(public_by_domain[entry["id"]])
        if entry.get("count") != expected:
            failures.append(f"search/manifest.json: {entry['id']} count must be {expected}")

    report = json.loads((ROOT / "build-report.json").read_text(encoding="utf-8"))
    expected_report = {
        "publicWikiDocuments": public_count,
        "publishedWikiDocuments": published_count,
        "inProgressWikiDocuments": pending_count,
        "domains": len(active_domains),
    }
    for key, expected in expected_report.items():
        if report.get(key) != expected:
            failures.append(f"build-report.json: {key} must be {expected}")
    for internal_key in ("generatedAt", "concepts"):
        if internal_key in report:
            failures.append(f"build-report.json: remove internal field {internal_key}")

    public_html = public_html_paths()
    metric_surfaces: dict[str, list[str]] = {}
    parsed_html: dict[Path, ParsedHTML] = {}
    for path in public_html:
        text = path.read_text(encoding="utf-8")
        for banned in BANNED_PUBLIC_COPY:
            if banned in text:
                failures.append(f"{rel(path)}: banned public-surface text {banned!r}")
        parser = ParsedHTML()
        parser.feed(text)
        parser.close()
        parsed_html[path] = parser
        for node in elements(parser.root):
            if node.attrs.get("data-status", "").strip().lower() == "proposed":
                failures.append(f"{rel(path)}:{node.line}: <{node.tag}> exposes data-status=proposed")
        metric_surfaces[rel(path)] = [prose_text(parser.root)]

    public_json = [ROOT / "build-report.json", *sorted(public_files(ROOT / "search", ".json"))]
    for path in public_json:
        metric_surfaces[rel(path)] = json_strings(json.loads(path.read_text(encoding="utf-8")))
    for path in (ROOT / "feed.xml", ROOT / "sitemap.xml"):
        metric_surfaces[rel(path)] = [normalized_text(list(ET.parse(path).getroot().itertext()))]
    for where, contents in metric_surfaces.items():
        for metric, patterns in MISLEADING_METRICS.items():
            if any(pattern.search(content) for content in contents for pattern in patterns):
                failures.append(f"{where}: misleading public-surface metric {metric}")
                break

    certificate_assets = ROOT / "assets" / "certificates"
    for path in sorted(candidate for candidate in certificate_assets.rglob("*") if candidate.is_file()):
        searchable = f"{rel(path)}\n{path.read_bytes().decode('utf-8', errors='ignore')}"
        if any(pattern.search(searchable) for pattern in CERTIFICATE_AUTHORING_PLACEHOLDER_PATTERNS):
            failures.append(f"{rel(path)}: authoring placeholder certificate asset must not be public")

    expected_domain_urls = {f"/wiki/domains/{domain}/" for domain in active_domains}
    for path in (ROOT / "wiki/index.html", ROOT / "wiki/atlas/index.html"):
        text = path.read_text(encoding="utf-8")
        links = set(re.findall(r'href="(/wiki/domains/[^"?#]+/)"', text))
        if links != expected_domain_urls:
            failures.append(f"{rel(path)}: domain links {sorted(links)} != {sorted(expected_domain_urls)}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_domains = {
        re.sub(r"^https://rizingblare\.github\.io", "", node.text or "")
        for node in sitemap.findall("sm:url/sm:loc", namespace)
        if "/wiki/domains/" in (node.text or "")
    }
    if sitemap_domains != expected_domain_urls:
        failures.append(f"sitemap.xml: domain URLs {sorted(sitemap_domains)} != {sorted(expected_domain_urls)}")

    for domain in sorted(path.stem for path in CATALOG.glob("*.json")):
        path = ROOT / "wiki" / "domains" / domain / "index.html"
        text = path.read_text(encoding="utf-8")
        expected_rows = public_by_domain[domain]
        if f"<span>{len(expected_rows)}개 공개 자료</span>" not in text:
            failures.append(f"{rel(path)}: header public count must be {len(expected_rows)}")
        if f"<b data-catalog-count>{len(expected_rows)}</b>개 결과" not in text:
            failures.append(f"{rel(path)}: result count must be {len(expected_rows)}")
        catalogs = [
            node for node in elements(parsed_html[path].root)
            if "catalog-list" in classes(node.attrs) and "data-catalog-list" in node.attrs
        ]
        if len(catalogs) != 1:
            failures.append(f"{rel(path)}: missing static catalog fallback")
            continue
        actual_items = []
        for node in elements(catalogs[0]):
            if "concept-row" not in classes(node.attrs):
                continue
            actual_items.append({
                "tag": "a" if node.tag == "a" else "non-link",
                "href": node.attrs.get("href", ""),
                "title": first_text(node, "strong"),
                "summary": first_text(node, "small"),
                "status": first_text(node, "b"),
            })
        expected_items = [
            {
                "tag": "a" if row["status"] == "published" else "non-link",
                "href": row.get("url", "") if row["status"] == "published" else "",
                "title": row["title"],
                "summary": row.get("summary", ""),
                "status": "학습 문서" if row["status"] == "published" else "작성 중",
            }
            for row in expected_rows
        ]
        if actual_items != expected_items:
            failures.append(f"{rel(path)}: rendered catalog items do not match the public projection")

    published_by_url = {
        row["url"]: row
        for row in public_by_id.values()
        if row.get("status") == "published" and row.get("url")
    }
    for row in public_by_id.values():
        if row.get("status") != "published" or not row.get("url"):
            continue
        document_path = ROOT / row["url"].strip("/") / "index.html"
        if not document_path.exists():
            failures.append(f"catalog {row['id']}: public document missing at {rel(document_path)}")
            continue
        document_nodes = list(elements(parsed_html[document_path].root))
        refs = [node for node in document_nodes if "concept-ref" in classes(node.attrs)]
        for ref_node in refs:
            ref = ref_node.attrs
            target = public_by_id.get(ref.get("data-concept-id", ""))
            where = f"{rel(document_path)}:{ref_node.line}"
            if ref_node.tag != "a" or ref.get("data-status") != "published" or not target or target.get("status") != "published":
                failures.append(f"{where}: concept-ref must be a published document link")
            elif ref.get("href") != target.get("url"):
                failures.append(
                    f"{where}: concept-ref {target['id']} href {ref.get('href')!r} != {target.get('url')!r}"
                )
        glossaries = [node for node in document_nodes if "glossary-card" in classes(node.attrs)]
        for glossary_node in glossaries:
            glossary = glossary_node.attrs
            target_id = glossary.get("data-concept-id")
            target = public_by_id.get(target_id or "")
            where = f"{rel(document_path)}:{glossary_node.line}"
            if glossary.get("data-status") and glossary.get("data-status") != "published":
                failures.append(f"{where}: glossary-card status must be published when present")
            if target_id and (not target or target.get("status") != "published"):
                failures.append(f"{where}: glossary-card target must be in the published projection")
            elif target_id and glossary.get("href") and glossary["href"] != target.get("url"):
                failures.append(f"{where}: glossary-card href does not match its published target")
        graph_containers = [
            node for node in document_nodes
            if node.attrs.get("id") in {"concept-graph", "document-connections"}
            or classes(node.attrs) & {"concept-map-wrap", "local-graph", "local-relation-list"}
        ]
        graph_nodes = {node for container in graph_containers for node in elements(container)}
        for graph_link in sorted((node for node in graph_nodes if node.tag == "a"), key=lambda node: node.line):
            if graph_link.attrs.get("href") not in published_by_url:
                failures.append(f"{rel(document_path)}:{graph_link.line}: graph link must target a published document")
        for graph_node in sorted((node for node in graph_nodes if "map-node" in classes(node.attrs)), key=lambda node: node.line):
            target_id = graph_node.attrs.get("data-concept-id")
            target = public_by_id.get(target_id or "")
            where = f"{rel(document_path)}:{graph_node.line}"
            if graph_node.attrs.get("data-status") and graph_node.attrs.get("data-status") != "published":
                failures.append(f"{where}: graph node status must be published when present")
            if target_id and (not target or target.get("status") != "published"):
                failures.append(f"{where}: graph node target must be in the published projection")

    if failures:
        print("public-surface: failed")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "public-surface: ok "
        f"({published_count} published, {pending_count} pending, {len(active_domains)} active domains, 0 proposed)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

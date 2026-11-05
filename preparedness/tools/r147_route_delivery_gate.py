#!/usr/bin/env python3
"""R147: offline Preparedness route, evidence and draft-output collision gate.

A structural check is not medical/source approval, independent QD, WordPress
release authority, or verified commerce. No network or CMS writes occur.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")
SAFE_URL = re.compile(r"/preparedness/(?:[a-z0-9-]+/){0,2}\Z")
SITE = "https://finalvestige.com"


class Hold(ValueError):
    """Missing or altered evidence: fail closed."""


def demand(ok, reason):
    if not ok:
        raise Hold(reason)


def read_file(path):
    demand(path.is_file() and not path.is_symlink(), f"missing/linked file: {path}")
    return path.read_text(encoding="utf-8", errors="strict")


def load_json(path):
    result = json.loads(read_file(path))
    demand(isinstance(result, dict), f"not a JSON object: {path}")
    return result


def route_key(value):
    """Conservative collision key. Never redirect/rewrite a public URL."""
    demand(isinstance(value, str) and value, "route must be nonempty text")
    u = urlsplit(value)
    if u.scheme or u.netloc:
        demand(u.scheme == "https" and u.netloc.lower() == "finalvestige.com"
               and not u.username and not u.password and not u.port,
               "external/ambiguous URL")
    demand(not u.query and not u.fragment, "route contains a query or fragment")
    decoded = unquote(u.path, encoding="utf-8", errors="strict")
    demand("%" not in decoded and "\\" not in decoded and "//" not in decoded
           and not any(x in decoded for x in ("\x00", "\r", "\n")),
           "unsafe encoded route")
    path = decoded.lower().rstrip("/") + "/"
    demand(SAFE_URL.fullmatch(path) is not None and path.startswith("/preparedness/"),
           f"not a safe Preparedness route: {value!r}")
    return path


def inspect(root, *, expected_citations=2000, expected_tools=6,
            wp_inventory=None, require_build=True):
    """Read-only structural check. All successful outcomes still require HOLD."""
    root = Path(root).resolve(strict=True)
    tax = load_json(root / "taxonomy.json")
    demand(tax.get("base_path") == "/preparedness/", "changed canonical base path")
    sections, slate, tools = (tax.get(x) for x in ("sections", "slate", "tools"))
    demand(all(isinstance(x, list) for x in (sections, slate, tools)),
           "taxonomy sections/slate/tools missing")
    section_ids = []
    for section in sections:
        demand(isinstance(section, dict), "invalid section")
        s = section.get("slug")
        demand(isinstance(s, str) and SLUG.fullmatch(s) is not None,
               "unsafe section slug")
        section_ids.append(s)
    demand(len(section_ids) == len(set(section_ids)) == 8,
           "expected eight distinct Preparedness hubs")
    demand(len(slate) == 35, "35 original article taxonomy entries required")

    # Archive landing/hub routes AND draft export filenames are reserved.
    routes, filenames = {}, {}

    def reserve(route, owner, filename):
        key = route_key(route)
        demand(key not in routes, f"canonical route collision {key}: {routes.get(key)} / {owner}")
        demand(filename not in filenames,
               f"WordPress draft filename collision {filename}: {filenames.get(filename)} / {owner}")
        routes[key], filenames[filename] = owner, owner

    reserve("/preparedness/", "landing", "landing.html")
    for s in section_ids:
        reserve(f"/preparedness/{s}/", f"hub:{s}", f"{s}.html")

    known = set()
    citations = 0
    # The taxonomy declares nine possible tools, but the frozen draft contains
    # SIX implemented tool body/meta pairs. Unbuilt slots are NOT deliverables.
    for kind, taxonomy_rows, count in (("articles", slate, 35), ("tools", tools, expected_tools)):
        folder = root / "content" / kind
        metas = sorted(folder.glob("*.meta.json"))
        bodies = sorted(folder.glob("*.body.html"))
        demand(len(metas) == count, f"{kind}: expected {count} metadata files")
        demand(len(metas) == len(bodies), f"{kind}: unmatched body/metadata files")
        stems = {p.name.removesuffix(".meta.json") for p in metas}
        demand(stems == {p.name.removesuffix(".body.html") for p in bodies},
               f"{kind}: body/metadata stems differ")
        reference = {}
        for row in taxonomy_rows:
            demand(isinstance(row, dict), "invalid taxonomy row")
            slug = row.get("slug")
            demand(isinstance(slug, str) and SLUG.fullmatch(slug) is not None,
                   "unsafe taxonomy article/tool slug")
            demand(slug not in reference, f"duplicate taxonomy slug {slug}")
            reference[slug] = row
        demand(stems == set(reference) if kind == "articles" else stems.issubset(set(reference)),
               f"{kind}: actual content and taxonomy disagree")
        for path in metas:
            meta = load_json(path)
            slug = path.name.removesuffix(".meta.json")
            demand(meta.get("slug") == slug and slug not in known,
                   f"{kind}: duplicate/mismatched slug {slug}")
            known.add(slug)
            section = meta.get("section")
            demand(section in section_ids and (kind == "tools" and section == "field-tools"
                   or reference[slug].get("section") == section), f"{slug}: section mismatch")
            demand(meta.get("status", {}).get("publish") == "draft",
                   f"{slug}: publication state not draft")
            demand(meta.get("safety_review", {}).get("state") in
                   ("pending", "approved", "not-required"), f"{slug}: safety state invalid")
            body = read_file(folder / f"{slug}.body.html")
            cites = CITE.findall(body)
            demand(body.count("{{cite:") == len(cites),
                   f"{slug}: malformed citation token")
            use = meta.get("source_use")
            demand(isinstance(use, dict) and set(cites) == set(use) and all(
                   isinstance(v, str) and v.strip() for v in use.values()),
                   f"{slug}: missing/unused author-specific citation explanation")
            if kind == "articles":
                citations += len(cites)
            reserve(f"/preparedness/{section}/{slug}/",
                    f"{kind}:{slug}", f"{slug}.html")
    demand(citations == expected_citations,
           f"article citation baseline mismatch: {citations} vs {expected_citations}")

    fingerprint = hashlib.sha256("\n".join(
        f"{p} {routes[p]}" for p in sorted(routes)).encode("utf-8")).hexdigest()
    build_state = "NOT_EXECUTED"
    if require_build:
        folder = root / "build"
        report = load_json(folder / "build-report.json")
        entries = report.get("articles")
        demand(isinstance(entries, list) and len(entries) == len(known),
               "draft build did not include every article and tool exactly once")
        seen = {}
        for entry in entries:
            demand(isinstance(entry, dict) and isinstance(entry.get("slug"), str),
                   "invalid build entry")
            slug = entry["slug"]
            demand(slug not in seen, f"duplicate build article {slug}")
            seen[slug] = entry.get("canonical")
            demand(SITE + route_key(seen[slug]) in
                   (seen[slug], seen[slug].rstrip("/") + "/"),
                   f"invalid canonical URL for {slug}")
        demand(set(seen) == known, "build lost or added a document")
        for path, owner in routes.items():
            if owner.startswith(("articles:", "tools:")):
                demand(route_key(seen[owner.split(":", 1)[1]]) == path,
                       f"{owner}: canonical differs from route")
        hubs = report.get("hubs")
        demand(isinstance(hubs, list) and len(hubs) == len(section_ids) and
               {x.get("section") for x in hubs} == set(section_ids),
               "missing/duplicated section hub in build")
        evidence = report.get("release_evidence", {})
        demand(evidence.get("state") == "HOLD" and
               evidence.get("independent_qa_verified") is False and
               evidence.get("wordpress_publication_performed") is False and
               evidence.get("article_published") == 0 and
               evidence.get("article_drafts") == len(known),
               "draft build contains release/approval contradiction")
        for filename in filenames:
            for subdir in ("wp", "preview"):
                artifact = folder / subdir / filename
                demand(bool(read_file(artifact).strip()),
                       f"empty draft output: {artifact}")
        build_state = "DRAFT_ARTIFACTS_STRUCTURALLY_CHECKED_NOT_PUBLISHED"

    inventory_state = "EXTERNAL_WORDPRESS_INVENTORY_NOT_PROVIDED"
    if wp_inventory is not None:
        data = load_json(wp_inventory)
        demand(isinstance(data.get("urls"), list),
               "invalid external WordPress URL inventory")
        observed = set()
        for item in data["urls"]:
            demand(isinstance(item, str), "external inventory contains non-text URL")
            key = route_key(item)
            demand(key not in observed, f"duplicate WordPress inventory route: {key}")
            observed.add(key)
        overlap = sorted(observed & set(routes))
        demand(not overlap,
               f"existing WordPress route collision requires owner adjudication: {overlap}")
        inventory_state = "NO_COLLISION_IN_SUPPLIED_UNVERIFIED_SNAPSHOT_HUMAN_AUDIT_REQUIRED"

    return {"schema": "FV-PREP-R147-ROUTES-1",
            "status": "STRUCTURAL_CHECK_PASSED_RELEASE_HOLD",
            "article_count": 35, "tool_count": len(known) - 35,
            "article_citation_occurrences": citations,
            "unique_draft_routes": len(routes), "route_manifest_sha256": fingerprint,
            "build": build_state, "external_wp": inventory_state,
            "publication_allowed": False, "automatic_merge": False,
            "medical_safety_verified": False, "merchant_offer_verified": False,
            "independent_qd": "NOT_APPROVED"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preparedness", type=Path, default=Path("preparedness"))
    p.add_argument("--wp-inventory", type=Path)
    p.add_argument("--skip-build", action="store_true",
                   help="route-only diagnostic, not draft build verification")
    a = p.parse_args(argv)
    result = {"schema": "FV-PREP-R147-ROUTES-1", "status": "HOLD",
              "publication_allowed": False, "medical_safety_verified": False,
              "merchant_offer_verified": False, "independent_qd": "NOT_APPROVED"}
    try:
        result.update(inspect(a.preparedness, wp_inventory=a.wp_inventory,
                              require_build=not a.skip_build))
        code = 0
    except (Hold, ValueError, TypeError, OSError, UnicodeError) as exc:
        result["error"], code = str(exc), 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

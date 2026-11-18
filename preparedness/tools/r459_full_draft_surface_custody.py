#!/usr/bin/env python3
"""R459: exact complete draft-transport custody, building on R458; NEVER release approval.

Source/citation correctness cannot be inferred from matching generated files.
This gate catches mutation, omission, stale extra outputs and deceptive sidebands
outside the authored pa-body: source/review notices, date and provenance labels,
free-access JSON-LD, breadcrumbs, CTA wrappers, hub cards and the landing page.
It pins the reviewed builder and scoped CSS blobs. Read-only; no network or CMS.

After authentic local validation/build:
    python -I preparedness/tools/r459_full_draft_surface_custody.py --root preparedness
Exit 2 = HOLD. Exit 0 = structural parity only, still DRAFT / HARD HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

STATE = "DRAFT_HARD_HOLD"
BUILDER_BLOB = "349173d1e1d735eade218d95c7a0a2649c8cccd9"
CSS_BLOB = "e354395cdb7985eb2fe16b99ca9fd66c9885557e"
MAX_BYTES = 5_000_000
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class SurfaceHold(ValueError):
    """Fail closed without implying independent medical/emergency/QD review."""


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def safe_bytes(path: Path, *, label: str) -> bytes:
    if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
        raise SurfaceHold(f"{label}: missing, linked or non-regular")
    if not 0 < path.stat().st_size <= MAX_BYTES:
        raise SurfaceHold(f"{label}: empty or oversized")
    return path.read_bytes()


def pinned_asset(path: Path, blob: str, label: str) -> None:
    found = git_blob(safe_bytes(path, label=label))
    if found != blob:
        raise SurfaceHold(f"{label}: unreviewed blob {found}; expected {blob}; manual review required")


def exact_surface(actual: bytes, expected: str, label: str) -> str:
    if not isinstance(expected, str) or not expected:
        raise SurfaceHold(f"{label}: empty expected render")
    want = expected.encode("utf-8", errors="strict")
    if len(want) > MAX_BYTES:
        raise SurfaceHold(f"{label}: expected render oversized")
    if actual != want:
        limit = min(len(actual), len(want))
        diff = next((i for i in range(limit) if actual[i] != want[i]), limit)
        raise SurfaceHold(f"{label}: unauthorized full-export mutation at byte {diff}; "
                          f"actual={len(actual)} expected={len(want)}")
    return hashlib.sha256(actual).hexdigest()


def checked_name(name: str) -> str:
    if not isinstance(name, str) or not SLUG.fullmatch(name):
        raise SurfaceHold(f"unsafe or duplicate-suspect artifact slug: {name!r}")
    return name


def audit_surfaces(root: Path, lib, build, *, prior: dict) -> dict:
    """Pure integration contract; synthetic fixtures test this without native files."""
    if not isinstance(prior, dict) or prior.get("release_state") != STATE or prior.get("qualified_qd_pass") is not False:
        raise SurfaceHold("R458 parent fail-closed source/body gate receipt required")
    if not isinstance(lib.articles, dict) or len(lib.articles) < 35:
        raise SurfaceHold("authenticated 35-article/tool inventory missing")
    if getattr(lib, "root", None) != root:
        raise SurfaceHold("library does not match authenticated root")
    report_path = root / "build" / "build-report.json"
    try:
        report = json.loads(safe_bytes(report_path, label="native build report"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise SurfaceHold(f"unparseable native build report: {exc}") from exc
    release = report.get("release_evidence") or {}
    if not (release.get("state") == "HOLD" and release.get("independent_qa_verified") is False
            and release.get("wordpress_publication_performed") is False):
        raise SurfaceHold("native build claims unsafe release/independent QD/publication status")
    if any(m.get("status", {}).get("publish") != "draft" for m in lib.articles.values()):
        raise SurfaceHold("the prepared draft-only slate contains a published/unknown status")
    originals = set(lib.articles)
    if any(not SLUG.fullmatch(s) for s in originals):
        raise SurfaceHold("invalid original article/tool slug")
    if len(prior.get("entries") or []) != len(originals):
        raise SurfaceHold("R458 body inventory and this surface inventory differ")
    if {e.get("slug") for e in prior["entries"]} != originals:
        raise SurfaceHold("R458 receipt lacks unique complete body identities")
    rows = report.get("articles")
    if not isinstance(rows, list) or len(rows) != len(originals):
        raise SurfaceHold("build-report articles not complete")
    report_slugs = [r.get("slug") for r in rows if isinstance(r, dict)]
    if len(report_slugs) != len(originals) or len(set(report_slugs)) != len(originals) or set(report_slugs) != originals:
        raise SurfaceHold("native report article identities altered")

    expect = {}
    kinds = {}
    for slug in sorted(originals):
        art = build.build_article(lib, slug)
        meta = lib.articles[slug]
        if art.get("slug") != slug or art.get("meta") is not meta:
            raise SurfaceHold(f"{slug}: renderer changed original article identity")
        want_url = "https://finalvestige.com" + lib.url_path(slug)
        if art.get("canonical") != want_url:
            raise SurfaceHold(f"{slug}: article canonical retargeted")
        row = next(r for r in rows if r["slug"] == slug)
        if row.get("canonical") != want_url or row.get("sources") != art.get("sources"):
            raise SurfaceHold(f"{slug}: report canonical/citations do not match authored source render")
        if any(row.get(key) != art.get(key) for key in ("words", "minutes")):
            raise SurfaceHold(f"{slug}: article depth/reading-time metadata changed")
        expect[slug] = (build.wp_wrap(lib, art["inner"]),
                        build.preview_wrap(lib, art["inner"],
                                           f'{meta["h1"]} | The Preparedness Archive', meta["description"]))
        kinds[slug] = "article_or_tool"

    secs = lib.taxonomy.get("sections")
    if not isinstance(secs, list) or not secs:
        raise SurfaceHold("missing taxonomic hub inventory")
    hub_specs = []
    for sec in secs:
        section = sec.get("slug")
        checked_name(section)
        hub = build.build_hub(lib, section, include_drafts=True)
        if hub is None:
            continue
        name = checked_name(hub.get("slug"))
        if name in expect or name != "hub-" + section:
            raise SurfaceHold("duplicate/wrong hub identity")
        expect[name] = (build.wp_wrap(lib, hub["inner"]),
                        build.preview_wrap(lib, hub["inner"], hub["title"], hub["description"]))
        kinds[name] = "hub"
        hub_specs.append({"section": section, "guides": hub["count"]})
    if report.get("hubs") != hub_specs:
        raise SurfaceHold("hub index or article counts differ from real rendered slate")
    land = build.build_landing(lib, include_drafts=True)
    if land.get("slug") != "landing" or "landing" in expect:
        raise SurfaceHold("landing identity collision")
    desc = "Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure."
    expect["landing"] = (build.wp_wrap(lib, land["inner"]),
                         build.preview_wrap(lib, land["inner"], "The Preparedness Archive | Final Vestige", desc))
    kinds["landing"] = "landing"
    if report.get("landing") != {k: land[k] for k in ("populated_sections", "article_cards")}:
        raise SurfaceHold("landing/card scope does not match draft inventory")

    expected_files = {slug + ".html" for slug in expect}
    result = []
    for n, folder in ((0, "wp"), (1, "preview")):
        parent = root / "build" / folder
        if not parent.is_dir() or parent.is_symlink():
            raise SurfaceHold(f"{folder}: output directory missing or linked")
        all_files = {p.name for p in parent.iterdir()}
        if all_files != expected_files:
            raise SurfaceHold(f"{folder}: stale, unexpected, missing or duplicate-route export files: "
                              f"missing={sorted(expected_files-all_files)} extra={sorted(all_files-expected_files)}")
        for slug in sorted(expect):
            path = parent / (slug + ".html")
            actual = safe_bytes(path, label=f"{folder}/{slug}")
            sha = exact_surface(actual, expect[slug][n], f"{folder}/{slug}")
            result.append({"slug": slug, "surface": folder, "kind": kinds[slug], "sha256": sha,
                           "size": len(actual)})
    return {"release_state": STATE, "qualified_qd_pass": False, "human_safety_review": "NOT_APPROVED",
            "wordpress_publication_performed": False, "merchant_conversion_verified": False,
            "source_claim_support_verified": False, "draft_export_count": len(result),
            "article_and_tool_count": len(originals), "hub_count": len(hub_specs),
            "landing_count": 1, "entries": result}


def read_module(path: Path, module_name: str):
    if not path.is_file() or path.is_symlink():
        raise SurfaceHold(f"native {module_name} missing or linked")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise SurfaceHold(f"native {module_name} cannot load")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def verify_native(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink() or not (root / "tools").is_dir():
        raise SurfaceHold("original native Preparedness checkout absent/linked")
    pinned_asset(root / "tools" / "build.py", BUILDER_BLOB, "reviewed native builder")
    pinned_asset(root / "assets" / "preparedness.css", CSS_BLOB, "reviewed scoped CSS")
    build = read_module(root / "tools" / "build.py", "r459_native_builder")
    previous = read_module(root / "tools" / "r458_authored_body_export_parity.py", "r459_parent_r458")
    prior = previous.verify_native(root)
    return audit_surfaces(root, build.Library(root), build, prior=prior)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        print(json.dumps(verify_native(args.root.absolute()), sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, KeyError, AttributeError, ValueError, UnicodeError, ImportError) as exc:
        print(json.dumps({"release_state": STATE, "qualified_qd_pass": False,
                          "wordpress_publication_performed": False, "integrity": "HOLD", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

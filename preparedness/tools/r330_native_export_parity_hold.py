#!/usr/bin/env python3
"""R330: deterministic, read-only native draft export parity and release-state gate.

This does not mark published material, sources, emergency advice, accessibility,
merchant suitability, or independent QD as approved. Run only AFTER the authentic
native validator and builder, and keep the resulting artifacts PRIVATE.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "fv-preparedness-r330-native-export-parity-hold-v1"
EXPECTED_ARTICLES = 35
EXPECTED_TOOLS = 6
SITE = "https://finalvestige.com"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DOC_FILE = re.compile(r"preparedness/content/(articles|tools)/([a-z0-9-]+)\.(body\.html|meta\.json)\Z")
WP = re.compile(r"\A<!-- wp:html -->\n<style>.*?</style>\n(?P<inner>.*)\n<!-- /wp:html -->\n?\Z", re.S)
PREVIEW = re.compile(r"<body><main>(?P<inner>.*)</main></body></html>\s*\Z", re.S)
TOKEN = re.compile(r"\{\{(?:cite|link|hub|cards|inline-js):", re.I)
RELEASE = {"public_release_authorized":False,"qualified_safety_approved":False,
           "independent_qd_pass":False,"source_claim_support_verified":False,
           "paid_sale_confirmed":False,"wordpress_publishing_performed":False}


def strict_json(data: bytes) -> dict:
    if type(data) is not bytes: raise ValueError("missing JSON bytes")
    def unique(pairs):
        out = {}
        for k,v in pairs:
            if k in out: raise ValueError("duplicate JSON key: " + k)
            out[k] = v
        return out
    value = json.loads(data.decode("utf-8", "strict"), object_pairs_hook=unique)
    if type(value) is not dict: raise ValueError("top-level object required")
    return value


def expected_from_source(manifest: dict, taxonomy: dict) -> dict:
    """Build 41 canonical route expectations, never treating taxonomy flags as QD."""
    if type(manifest) is not dict or type(taxonomy) is not dict:
        raise ValueError("missing source custody or taxonomy")
    if manifest.get("expected",{}).get("article_bodies") != EXPECTED_ARTICLES or manifest.get("expected",{}).get("tool_bodies") != EXPECTED_TOOLS:
        raise ValueError("R319 custody cardinality drift")
    rows = manifest.get("records")
    if type(rows) is not list: raise ValueError("missing source records")
    paths, kinds = set(), {"articles":set(), "tools":set()}
    for row in rows:
        path = row.get("path") if type(row) is dict else None
        match = DOC_FILE.fullmatch(path or "")
        if not match or path in paths: raise ValueError("unexpected or duplicate document path")
        paths.add(path)
        if match.group(3) == "body.html": kinds[match.group(1)].add(match.group(2))
    for kind, count in (("articles",EXPECTED_ARTICLES),("tools",EXPECTED_TOOLS)):
        slugs = kinds[kind]
        if len(slugs) != count: raise ValueError("source files missing for " + kind)
        if any(f"preparedness/content/{kind}/{slug}.meta.json" not in paths for slug in slugs):
            raise ValueError("metadata missing for " + kind)
    slate = taxonomy.get("slate")
    if type(slate) is not list or len(slate) != EXPECTED_ARTICLES:
        raise ValueError("slate not 35")
    section_names = {s.get("slug") for s in taxonomy.get("sections",[]) if type(s) is dict}
    if len(section_names) != 8 or "field-tools" not in section_names:
        raise ValueError("section route drift")
    routes = {}
    for row in slate:
        if type(row) is not dict: raise ValueError("invalid slate row")
        slug,sec=row.get("slug"),row.get("section")
        if slug not in kinds["articles"] or sec not in section_names or slug in routes:
            raise ValueError("slate/source route mismatch")
        routes[slug] = SITE + "/preparedness/" + sec + "/" + slug + "/"
    if set(routes) != kinds["articles"]: raise ValueError("slate missing article")
    for slug in kinds["tools"]:
        if slug in routes: raise ValueError("tool and article slug collision")
        routes[slug] = SITE + "/preparedness/field-tools/" + slug + "/"
    if len(set(routes.values())) != EXPECTED_ARTICLES + EXPECTED_TOOLS:
        raise ValueError("duplicate canonical URL")
    return routes


def scan(report: dict, expected_routes: dict, outputs: dict[str,bytes]) -> dict:
    """Validate *provided* build artifacts; synthetic inputs confer no authenticity."""
    errors = []
    witnesses = []
    if type(expected_routes) is not dict or len(expected_routes) != EXPECTED_ARTICLES+EXPECTED_TOOLS or any(
        type(k) is not str or SLUG.fullmatch(k) is None or type(v) is not str or not v.startswith(SITE+'/preparedness/')
        for k,v in expected_routes.items()): errors.append("INVALID_EXPECTED_ROUTE_MANIFEST")
    if type(report) is not dict: report={}; errors.append("NO_BUILD_REPORT")
    rel=report.get("release_evidence")
    if type(rel) is not dict or (rel.get("state")!="HOLD" or rel.get("independent_qa_verified") is not False
        or rel.get("wordpress_publication_performed") is not False
        or type(rel.get("article_drafts")) is not int or rel.get("article_drafts")!=41
        or type(rel.get("article_published")) is not int or rel.get("article_published")!=0
        or type(rel.get("unresolved_collisions")) is not int or rel.get("unresolved_collisions") < 1):
        errors.append("BUILD_REPORT_FALSE_RELEASE_OR_UNVERIFIED_SOURCE_CLEARANCE")
    articles=report.get("articles")
    if type(articles) is not list or len(articles)!=41:
        articles=[]; errors.append("BUILD_REPORT_MISSING_41_ARTICLES")
    ids, urls = set(), set()
    for row in articles:
        if type(row) is not dict: errors.append("INVALID_ARTICLE_REPORT_ROW"); continue
        slug,canonical=row.get("slug"),row.get("canonical")
        if type(slug) is not str or SLUG.fullmatch(slug) is None:
            errors.append("MALFORMED_REPORTED_SLUG"); continue
        if slug in ids: errors.append("DUPLICATE_REPORTED_SLUG:"+slug)
        ids.add(slug)
        if canonical in urls: errors.append("DUPLICATE_REPORTED_CANONICAL:"+str(canonical))
        urls.add(canonical)
        if canonical!=expected_routes.get(slug): errors.append("CANONICAL_ROUTE_DRIFT:"+slug)
        if (type(row.get("words")) is not int or row["words"] <=0 or type(row.get("minutes")) is not int
                or row["minutes"]<=0 or type(row.get("sources")) is not list or not row["sources"]
                or len(row["sources"])!=len(set(map(str,row["sources"])))):
            errors.append("READING_DEPTH_OR_SOURCE_REPORT_MISSING:"+slug)
    if ids != set(expected_routes): errors.append("REPORT_AND_SOURCE_SLATE_DISAGREE")
    hubs=report.get("hubs")
    if type(hubs) is not list: hubs=[]; errors.append("HUB_REPORT_MISSING")
    hub_ids=set()
    for hub in hubs:
        if type(hub) is not dict or type(hub.get("section")) is not str or not SLUG.fullmatch(hub["section"]):
            errors.append("INVALID_HUB_ROW"); continue
        slug="hub-"+hub["section"]
        if slug in hub_ids: errors.append("DUPLICATE_HUB:"+slug)
        hub_ids.add(slug)
        if type(hub.get("guides")) is not int or hub["guides"]<=0:
            errors.append("EMPTY_OR_INVALID_HUB:"+slug)
    landing=report.get("landing")
    if type(landing) is not dict or type(landing.get("article_cards")) is not int or landing["article_cards"] != 41:
        errors.append("LANDING_CARD_COUNT_DRIFT")
    if type(landing) is dict and (type(landing.get("populated_sections")) is not list or
        set(landing["populated_sections"])!={x[4:] for x in hub_ids}):
        errors.append("LANDING_HUB_COVERAGE_DRIFT")
    expected_files = {f"wp/{slug}.html" for slug in ids|hub_ids|{'landing'}} | {f"preview/{slug}.html" for slug in ids|hub_ids|{'landing'}}
    if type(outputs) is not dict:
        outputs={}; errors.append("NO_NATIVE_OUTPUTS")
    if set(outputs)!=expected_files:
        errors.append("MISSING_OR_EXTRA_WORDPRESS_PREVIEW_OUTPUTS")
    for slug in sorted(ids|hub_ids|{'landing'}):
        wpraw=outputs.get(f"wp/{slug}.html")
        preraw=outputs.get(f"preview/{slug}.html")
        if type(wpraw) is not bytes or type(preraw) is not bytes:
            errors.append("MISSING_BYTES_PAIR:"+slug); continue
        try: wp=wpraw.decode("utf-8","strict"); preview=preraw.decode("utf-8","strict")
        except UnicodeError: errors.append("INVALID_UTF8_PAIR:"+slug); continue
        w=WP.fullmatch(wp); p=PREVIEW.search(preview)
        if not w or not p: errors.append("INVALID_OUTPUT_WRAPPER:"+slug); continue
        if w.group("inner")!=p.group("inner"):
            errors.append("WORDPRESS_PREVIEW_BODY_MISMATCH:"+slug)
        if not preview.lower().startswith('<!doctype html><html lang="en">') or '<meta name="robots" content="noindex,nofollow">' not in preview:
            errors.append("PREVIEW_NOT_PRIVATE_NOINDEX:"+slug)
        if TOKEN.search(wp) or TOKEN.search(preview): errors.append("UNRESOLVED_TEMPLATE_TOKEN:"+slug)
        if slug in expected_routes and f'data-slug="{slug}"' not in w.group("inner"):
            errors.append("WRONG_ARTICLE_EXPORT_IDENTITY:"+slug)
        witnesses.append({"slug":slug,"wp_sha256":hashlib.sha256(wpraw).hexdigest(),
                          "preview_sha256":hashlib.sha256(preraw).hexdigest(),
                          "body_sha256":hashlib.sha256(w.group("inner").encode("utf-8")).hexdigest(),
                          "body_pair_equal":w.group("inner")==p.group("inner")})
    return {"schema":SCHEMA,"state":"INVALID_HARD_HOLD" if errors else "DRAFT_HARD_HOLD",
            "errors":sorted(set(errors)),"expected_article_tool_pairs":41,
            "tested_export_pairs":len(witnesses),"witnesses":witnesses,"release":RELEASE.copy(),
            "note":"Build parity is not claim support, medical/emergency clearance, independent QD, or publishing approval."}


def read_native(root: Path) -> dict:
    """Read only authenticated local inputs and reject linked paths / stray HTML."""
    from preparedness.tools import r319_three_way_custody_hold as custody
    from preparedness.tools import r320_conflict_adjudication_docket_hold as docket
    manifest=strict_json(custody.safe_bytes(root,custody.MANIFEST_PATH))
    adjudication=strict_json(custody.safe_bytes(root,"preparedness/audits/r320_conflict_adjudication_docket.json"))
    if custody.validate_manifest(manifest,root)["errors"] or docket.validate_docket(manifest,adjudication)["errors"]:
        raise ValueError("authenticated custody / unresolved docket missing or altered")
    taxonomy=strict_json(custody.safe_bytes(root,"preparedness/taxonomy.json"))
    routes=expected_from_source(manifest,taxonomy)
    report=strict_json(custody.safe_bytes(root,"preparedness/build/build-report.json"))
    outputs={}
    for folder in ("wp","preview"):
        base=root/"preparedness"/"build"/folder
        if base.is_symlink() or not base.is_dir(): raise ValueError("untrusted or missing export directory")
        for path in base.iterdir():
            if path.is_symlink() or not path.is_file() or not path.name.endswith(".html"):
                raise ValueError("unexpected or symlink output: " + path.name)
            outputs[f"{folder}/{path.name}"]=custody.safe_bytes(root,f"preparedness/build/{folder}/{path.name}")
    return scan(report,routes,outputs)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    try:
        report=read_native(args.root.resolve())
    except (OSError,ValueError,TypeError,UnicodeError,KeyError,ImportError):
        report={"schema":SCHEMA,"state":"INVALID_HARD_HOLD","errors":["AUTHENTIC_NATIVE_41_DRAFT_EXPORT_AND_SOURCE_DOCKET_REQUIRED"],"release":RELEASE.copy()}
    print(json.dumps(report,indent=2,sort_keys=True))
    # Exit 2: artifact structurally matches, but still NOT RELEASED. Exit 1: invalid.
    return 2 if report["state"]=="DRAFT_HARD_HOLD" else 1

if __name__=="__main__": raise SystemExit(main())

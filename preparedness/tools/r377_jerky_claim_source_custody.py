"""R377: read-only source-to-claim conflict custody for held Article #11.

Fail-closed: neither matching original blobs nor passing tests grant emergency,
Qualified Domain, merchant, or publication approval.  Requires the original
R374/R375 authentic Git-object data and source-specific independent review.
"""
from __future__ import annotations
import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

REPOSITORY = "finalvestigestudios/final-vestige-site-layer"
ORIGINAL_BODY_SHA = "6fa55c397b161437e016d5d4a6c27da7ce3fa6bd"
ORIGINAL_META_SHA = "50b365e8109c14bdb9ce1a9365db88215a678ec5"
ORIGINAL_CROSSWALK_SHA = "24b49f0a423119c2f612455f021669709a3f22b5"
ORIGINAL_COLLISION_SHA = "36cb108ddd26ee9890fafa3e77d61d9e66c60544"
ORIGINAL_MANIFEST_SHA = "5e7d9a8972872c82b4bc46ac13aab18883d8149a"
HELD_SOURCE_IDS = frozenset(("fsis-power-failure", "loc-pioneer-diaries",
    "loc-prairie-traveler", "nchfp-home", "nchfp-jerky"))
CRITICAL_JERKY_ID = "nchfp-jerky"
EXPECTED_EXTERNAL = {
    "cdc-trichinellosis-prevention": "https://www.cdc.gov/trichinellosis/prevention/index.html",
    "cdc-eid-bear-jerky-2026": "https://wwwnc.cdc.gov/eid/article/32/7/26-0062_article",
    "nchfp-jerky-existing": "https://nchfp.uga.edu/how/dry/recipes/jerky",
}
CITES = re.compile(r"\{\{cite:([a-z][a-z0-9-]*)\}\}")
RISK_PATTERNS = {
 "wild_game_freezing": re.compile(r"(?:pork.{0,35}wild game|wild game.{0,70}trichinella|trichinella.{0,65}wild game).{0,220}freez|freez.{0,160}(?:pork.{0,35}wild game|wild game)", re.I),
 "method_choice": re.compile(r"whichever method|whichever (?:approach|route)|either (?:method|route).*?(?:safe|use)", re.I),
 "competing_heat_sequences": re.compile(r"(?:before.{0,90}after|after.{0,90}before).{0,250}(?:dry|heat|FSIS|NCHFP)|FSIS.{0,150}NCHFP.{0,120}(?:disagree|tension)", re.I),
 "shelf_life_disagreement": re.compile(r"(?:shelf li(?:fe|ves)|room.temperature).{0,180}(?:different|disagree|2 weeks|two weeks|2 months|two months)", re.I),
}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class _BodyText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in ("p", "tr", "li", "h2", "h3"):
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def claim_risk_lines(html: str) -> dict[str, list[int]]:
    """Flag (not resolve) source-dependent high-risk original manuscript claims."""
    lines = html.splitlines()
    out = {}
    for key, pattern in RISK_PATTERNS.items():
        found = []
        for index, raw in enumerate(lines, 1):
            p = _BodyText()
            p.feed(raw)
            line = unescape(" ".join(p.parts))
            if pattern.search(line):
                found.append(index)
        out[key] = found
    return out


def _signature(v: dict) -> tuple:
    keys = ("branch", "fragment", "source_blob", "id", "url", "publisher",
            "kind", "verified_on", "human_link_check", "supports", "notes")
    return tuple(v.get(k) for k in keys)


def validate(body: bytes, meta: object, crosswalk: object, audit: object,
             manifest: object, evidence: object, *, synthetic: bool = False) -> dict:
    errors: list[str] = []
    if not isinstance(meta, dict) or not isinstance(crosswalk, dict) or not isinstance(audit, dict) or not isinstance(manifest, dict) or not isinstance(evidence, dict):
        return {"status":"INVALID_HARD_HOLD", "errors":["document types invalid"],
                "publication_approved":False, "qualified_safety_approved":False,
                "paid_offer_approved":False}
    if not isinstance(body, bytes):
        errors.append("body must be byte-identical source evidence")
        body = b""
    if not synthetic and git_blob(body) != ORIGINAL_BODY_SHA:
        errors.append("original article #11 body Git identity drift")
    try:
        html = body.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        html = ""
        errors.append("body not UTF-8")
    if meta.get("slug") != "safe-jerky-dehydration" or meta.get("n") != 11:
        errors.append("original article identity changed")
    if meta.get("status") != {"editorial":"drafted", "publish":"draft"}:
        errors.append("draft editorial state changed")
    if meta.get("safety_review") != {"state":"pending", "reviewer":None, "date":None}:
        errors.append("unreviewed safety state changed")
    if meta.get("section") != "food" or meta.get("track") != "modern":
        errors.append("article taxonomy changed")
    for label, doc in (("crosswalk",crosswalk), ("audit",audit), ("manifest",manifest)):
        if doc.get("repository") != REPOSITORY or doc.get("release_state") != "DRAFT_HARD_HOLD" or doc.get("schema_version") != 1:
            errors.append(f"{label} identity/release state changed")
    if not synthetic:
        if crosswalk.get("record_occurrences") != 280 or crosswalk.get("distinct_source_ids") != 203 or crosswalk.get("original_fragment_count") != 7:
            errors.append("R374 full source reading-scope inventory changed")
        if manifest.get("article_count") != 35 or manifest.get("conflict_count") != 9 or len(manifest.get("branch_pins",[])) != 9:
            errors.append("original article inventory/branch provenance changed")
        if len(audit.get("shared_url_docket",[])) != 17:
            errors.append("shared URL reading-scope inventory changed")
    if audit.get("branch_pins") != manifest.get("branch_pins"):
        errors.append("R375 original branch provenance diverges from manifest")
    if audit.get("source_crosswalk_git_blob") != ORIGINAL_CROSSWALK_SHA or audit.get("object_manifest_git_blob") != ORIGINAL_MANIFEST_SHA:
        errors.append("upstream source Git identities absent")
    if audit.get("release_state") != "DRAFT_HARD_HOLD":
        errors.append("source audit no longer hard held")
    for key in ("publication_approved","qualified_emergency_safety_approved",
                "qualified_privacy_approved", "commercial_checkout_approved"):
        if audit.get(key) is not False:
            errors.append(f"source audit asserted release/commerce approval: {key}")
    uses = meta.get("source_use")
    if not isinstance(uses, dict) or not uses:
        uses = {}
        errors.append("metadata source_use missing")
    raw_cites = CITES.findall(html)
    if not raw_cites:
        errors.append("all article citations lost")
    missing = sorted(set(raw_cites) - set(uses))
    if missing:
        errors.append("body citations lack original metadata source_use: " + ", ".join(missing))
    unused = sorted(set(uses) - set(raw_cites))
    if unused:
        errors.append("metadata source_use no longer cited by article: " + ", ".join(unused))
    src_rows = crosswalk.get("source_id_variants")
    collision_rows = audit.get("semantic_conflict_docket")
    if not isinstance(src_rows, list) or not isinstance(collision_rows, list):
        src_rows, collision_rows = [], []
        errors.append("missing source crosswalk/collision list")
    sources = {r.get("id"):r for r in src_rows if isinstance(r,dict)}
    collisions = {r.get("source_id"):r for r in collision_rows if isinstance(r,dict)}
    if len(sources) != len(src_rows):
        errors.append("crosswalk duplicate/missing source identities")
    if len(collisions) != len(collision_rows) or set(collisions) != HELD_SOURCE_IDS:
        errors.append("five original same-ID review groups altered")
    if set(uses) - set(sources):
        errors.append("article source_use cannot resolve to crosswalk")
    for sid in HELD_SOURCE_IDS:
        row, col = sources.get(sid), collisions.get(sid)
        if not isinstance(row,dict) or not isinstance(col,dict):
            errors.append(f"missing collision custody: {sid}")
            continue
        variants, audits = row.get("variants"), col.get("variants")
        if not isinstance(variants,list) or not isinstance(audits,list) or len(audits)<2:
            errors.append(f"no original two-plus variants: {sid}")
            continue
        if len(variants) != len(audits) or {_signature(v) for v in variants if isinstance(v,dict)} != {_signature(v) for v in audits if isinstance(v,dict)}:
            errors.append(f"source reading-scope or contributor record tampered: {sid}")
        if col.get("release_disposition") != "HUMAN_ADJUDICATION_REQUIRED_NO_AUTO_SELECT":
            errors.append(f"unreviewed source selected: {sid}")
        for v in variants:
            if not isinstance(v,dict) or v.get("id") != sid or v.get("human_link_check") is not False:
                errors.append(f"source status/identity changed: {sid}")
                continue
            if not v.get("supports") or not v.get("notes") or not v.get("source_blob"):
                errors.append(f"source reading depth/provenance missing: {sid}")
            u = urlsplit(str(v.get("url","")))
            if u.scheme != "https" or not u.netloc or u.username or u.password:
                errors.append(f"source URL invalid: {sid}")
    if CRITICAL_JERKY_ID not in uses or CRITICAL_JERKY_ID not in raw_cites:
        errors.append("critical jerky citation removed instead of reviewed")
    if evidence.get("release_state") != "DRAFT_HARD_HOLD" or evidence.get("target_slug") != "safe-jerky-dehydration":
        errors.append("R377 current article/source risk evidence missing")
    rows = evidence.get("official_evidence",[])
    if not isinstance(rows,list) or {v.get("id"):v.get("url") for v in rows if isinstance(v,dict)} != EXPECTED_EXTERNAL:
        errors.append("official source links changed or omitted")
    for row in rows if isinstance(rows,list) else []:
        if not isinstance(row,dict) or row.get("qualified_review") is not False or not row.get("reading_scope"):
            errors.append("official source unreviewed scope falsely upgraded")
    if evidence.get("editorial_disposition") != "SUPPRESS_ACTIONABLE_DISPUTED_CLAIMS_PENDING_QUALIFIED_REVIEW":
        errors.append("conflicting actionable advice not held")
    if evidence.get("paid_offer_verified") is not False or evidence.get("publication_approved") is not False:
        errors.append("unverified offer/publication state falsified")
    risk = claim_risk_lines(html)
    return {"status":("INVALID_HARD_HOLD" if errors else ("SYNTHETIC_HARD_HOLD" if synthetic else "ORIGINAL_CLAIM_CONFLICT_HARD_HOLD")),
            "errors":sorted(set(errors)), "original_body_sha":git_blob(body),
            "unresolved_source_ids":sorted(HELD_SOURCE_IDS),
            "article_11_claim_flags":risk,"article_11_citation_occurrences":len(raw_cites),
            "publication_approved":False,"qualified_safety_approved":False,
            "paid_offer_approved":False, "verified_net_revenue":None}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    for n in ("body","meta","crosswalk","audit","manifest","evidence"):
        p.add_argument(n,type=Path)
    a=p.parse_args()
    try:
        paths=[getattr(a,n) for n in ("body","meta","crosswalk","audit","manifest","evidence")]
        raws=[p.read_bytes() for p in paths]
        results=validate(raws[0],*(json.loads(raw) for raw in raws[1:]))
        for label,raw,expected in zip(("meta","crosswalk","audit","manifest"),raws[1:5],
            (ORIGINAL_META_SHA, ORIGINAL_CROSSWALK_SHA, ORIGINAL_COLLISION_SHA, ORIGINAL_MANIFEST_SHA)):
            if git_blob(raw)!=expected:
                results["status"]="INVALID_HARD_HOLD"
                results["errors"].append(f"Git-blob readback mismatch: {label}")
    except (OSError,ValueError,TypeError) as e:
        results={"status":"INVALID_HARD_HOLD","errors":[type(e).__name__],
                 "publication_approved":False,"qualified_safety_approved":False,
                 "paid_offer_approved":False}
    print(json.dumps(results,indent=2,sort_keys=True))
    return 2  # always release hard hold; never a QD PASS

if __name__=="__main__":
    raise SystemExit(main())

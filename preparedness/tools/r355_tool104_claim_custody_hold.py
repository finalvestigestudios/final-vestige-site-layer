#!/usr/bin/env python3
"""R355: immutable Tool #104 safety-claim custody; READ ONLY, NEVER release approval.

A government fillable form's data-handling statement cannot establish how
FV's web page, browser, extensions, downloads, printer or WordPress plugins
handle data. This gate is a reviewer docket, not safety/privacy certification.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA = "fv-preparedness-r355-tool104-claim-custody-hold-v1"
BODY_GIT_BLOB = "be8698ac5d020476ff649d85813810e2000c6f98"
META_GIT_BLOB = "47da1e7e20e39f0ea85e26d54a8d58301f6e0a15"
SLUG = "family-reunification-card"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
CONTRACT = ("privacy_absolute", "privacy_metadata", "emergency_911_sms",
            "child_card_scope", "print_accessibility", "script_dependency",
            "source_transfer", "consent_and_merchant_separation")
HOLD = {"may_merge": False, "may_publish": False, "qualified_qd_pass": False,
        "human_source_link_checked": False, "medical_emergency_safe": False,
        "privacy_verified": False, "mobile_print_a11y_verified": False,
        "native_build_verified": False, "merchant_confirmed_orders": False}

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

class Extractor(HTMLParser):
    """Visible text only; CSS/script source text cannot count as reviewer prose."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hide = 0
        self.words = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hide += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hide = max(self.hide - 1, 0)
    def handle_data(self, data):
        if not self.hide:
            self.words.append(data)

def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).lower().strip()

def _hit(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(expr, text, flags=re.I) for expr in patterns)

def inspect(body: str, meta: dict, *, pin_original: bool = False,
            render_surfaces: dict | None = None) -> dict:
    """Pure deterministic scanner. A clean result remains a qualified-review HOLD."""
    errors = set()
    obligations = sorted(CONTRACT)
    if not isinstance(body, str) or not isinstance(meta, dict):
        return {"schema": SCHEMA, "status": "INVALID_HARD_HOLD",
                "errors": ["INVALID_INPUT"], "obligations": obligations, **HOLD}
    try:
        canonical_meta = json.dumps(meta, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"))
    except (TypeError, ValueError, RecursionError):
        return {"schema": SCHEMA, "status": "INVALID_HARD_HOLD",
                "errors": ["INVALID_METADATA"], "obligations": obligations, **HOLD}
    parser = Extractor()
    try:
        parser.feed(body)
        parser.close()
    except (ValueError, AssertionError, RecursionError):
        errors.add("UNPARSEABLE_BODY")
    text = normalized(" ".join(parser.words))
    prose = normalized(" ".join(str(meta.get(k, "")) for k in
                                 ("title", "dek", "description")))
    tags = normalized(" ".join(str(x) for x in meta.get("tags", [])
                               if isinstance(x, str)))
    source_use = meta.get("source_use", {})
    if (not isinstance(source_use, dict) or not source_use or
            not all(isinstance(k, str) and isinstance(v, str)
                    for k, v in source_use.items())):
        errors.add("SOURCE_USE_REGISTER_MISSING_OR_INVALID")
        source_use = {}
    marker_ids = list(dict.fromkeys(CITE.findall(body)))
    if set(marker_ids) - set(source_use):
        errors.add("INLINE_SOURCE_IDS_NOT_DECLARED")
    if not marker_ids:
        errors.add("INLINE_CITATION_EVIDENCE_MISSING")
    if (meta.get("slug") != SLUG or meta.get("kind") != "tool" or
            meta.get("n") != 104):
        errors.add("TOOL_104_IDENTITY_DRIFT")
    status = meta.get("status", {})
    safety = meta.get("safety_review", {})
    if not isinstance(status, dict) or status.get("publish") != "draft":
        errors.add("UNAUTHORIZED_PUBLISH_STATE")
    if not isinstance(safety, dict) or safety.get("state") != "pending":
        errors.add("SAFETY_REVIEW_STATE_MUST_STAY_PENDING")
    if any(k in meta for k in ("qd_pass", "may_publish",
                               "independent_approval", "verified_paid_orders")):
        errors.add("UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD")
    if _hit(text, (r"what you type stays on this page",
                   r"it is not sent or saved",
                   r"closing the tab clears it", r"nothing (?:is|gets) stored")):
        errors.add("ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF")
    if _hit(prose + " " + tags, (r"local.only", r"runs locally",
                               r"nothing is stored", r"never (?:saved|stored|sent)",
                               r"no data (?:is )?stored")):
        errors.add("META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED")
    if _hit(text, (r"call 911 for anything life.threatening",
                   r"text messages rather than calls for everything else")):
        errors.add("BLANKET_EMERGENCY_AND_SMS_ADVICE_UNREVIEWED")
    if _hit(text, (r"do not put a child.s full name",
                   r"do not put .*medical diagnosis",
                   r"first names or nicknames and phone numbers are usually enough")):
        errors.add("CHILD_CARRIED_CARD_SCOPE_REQUIRES_QUALIFIED_REVIEW")
    if _hit(body, (r"font.size\s*:\s*[0-8](?:\.\d+)?pt",
                   r"font-size\s*:\s*7\.5pt")):
        errors.add("SMALL_PRINT_REQUIRES_ACCESSIBILITY_REVIEW")
    if "{{inline-js:" in body or _hit(body, (r"<script\b",
                       r"on(?:load|submit|change|input)\s*=")):
        errors.add("CLIENT_SCRIPT_PRIVACY_NO_JS_NOT_VERIFIED")
    if "<noscript" not in body.lower():
        errors.add("NO_JS_ALTERNATIVE_NOT_EVIDENCED")
    if (_hit(text, (r"not saved, stored or shared by any government agency",))
            and _hit(prose + " " + tags + " " + text,
                     (r"nothing is stored", r"what you type stays on this page"))):
        errors.add("GOVERNMENT_FORM_PRIVACY_NOT_TRANSFERABLE_TO_FV")
    if _hit(text, (r"cdc suggests .*contact cards", r"cdc .*school bags",
                   r"child.*emergency contact card")):
        errors.add("CDC_CARD_COMPLETENESS_AND_CONTEXT_NOT_CERTIFIED")
    if pin_original and git_blob(body.encode("utf-8")) != BODY_GIT_BLOB:
        errors.add("ORIGINAL_BODY_GIT_BLOB_DRIFT")
    surfaces_present = []
    if render_surfaces is None:
        errors.add("PRIVATE_RENDER_SURFACES_NOT_PROVIDED")
    elif not isinstance(render_surfaces, dict):
        errors.add("INVALID_RENDER_SURFACES")
    else:
        for name in ("wp", "preview"):
            surface = render_surfaces.get(name)
            if not isinstance(surface, str) or not surface:
                errors.add("PRIVATE_" + name.upper() + "_SURFACE_MISSING")
                continue
            surfaces_present.append(name)
            if _hit(surface, (r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']index',
                              r'"datePublished"', r'"qualified_qd_pass"\s*:\s*true')):
                errors.add("PRIVATE_RENDER_PUBLICATION_SIGNAL:" + name)
            if not _hit(surface, (r"human (?:source-)?link check pending",
                                  r"pending (?:safety|review)", r"not (?:yet )?reviewed")):
                errors.add("PRIVATE_RENDER_HOLD_DISCLOSURE_NOT_ESTABLISHED:" + name)
            for literal in ("nothing is stored", "what you type stays on this page"):
                if literal in surface.lower():
                    errors.add("PRIVATE_RENDER_ABSOLUTE_PRIVACY_COPY:" + name)
        if (len(surfaces_present) == 2 and
                render_surfaces["wp"] == render_surfaces["preview"]):
            errors.add("IDENTICAL_RENDER_WRAPPERS_ARE_NOT_AUTHENTIC_PARITY")
    return {"schema": SCHEMA,
            "status": "INVALID_HARD_HOLD" if errors else "REVIEW_DOCKET_HARD_HOLD",
            "errors": sorted(errors), "obligations": obligations,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "metadata_semantic_sha256":
                hashlib.sha256(canonical_meta.encode("utf-8")).hexdigest(),
            "citation_ids": marker_ids,
            "surfaces_inspected": sorted(surfaces_present), **HOLD}

def native_probe(repo_root: Path) -> dict:
    """Require original byte-pinned Tool #104 files. No browser/network/writes."""
    try:
        root = Path(repo_root).resolve(strict=True)
        if not (root / ".git").exists():
            raise ValueError("NATIVE_CHECKOUT_MISSING")
        folder = root / "preparedness" / "content" / "tools"
        body_path = folder / (SLUG + ".body.html")
        meta_path = folder / (SLUG + ".meta.json")
        if any(p.is_symlink() or not p.is_file()
               for p in (body_path, meta_path)):
            raise ValueError("PINNED_INPUT_MISSING_OR_NONREGULAR")
        body_bytes, meta_bytes = body_path.read_bytes(), meta_path.read_bytes()
        if (git_blob(body_bytes) != BODY_GIT_BLOB or
                git_blob(meta_bytes) != META_GIT_BLOB):
            raise ValueError("SOURCE_BLOB_DRIFT_REQUIRES_REVIEW")
        result = inspect(body_bytes.decode("utf-8"),
                         json.loads(meta_bytes), pin_original=True)
        result["native_body_blob_verified"] = True
        result["native_meta_blob_verified"] = True
        return result
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError,
            RecursionError) as exc:
        return {"schema": SCHEMA, "status": "INVALID_HARD_HOLD",
                "errors": ["NATIVE_SOURCE_CUSTODY_UNAVAILABLE:" + type(exc).__name__],
                "obligations": sorted(CONTRACT),
                "native_body_blob_verified": False,
                "native_meta_blob_verified": False, **HOLD}

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path,
                    default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_probe(ap.parse_args().repo_root),
                     indent=2, sort_keys=True))
    raise SystemExit(2)

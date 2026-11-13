#!/usr/bin/env python3
"""Read-only, source-pinned A15/Tool104 claim witnesses. NEVER a qualified safety/QD pass.

The scope is the authentic integrated manuscript, not a substitute for independent
source reading, local emergency-communications review, or native WordPress QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from preparedness.tools import r319_three_way_custody_hold as custody

SCHEMA = "fv-preparedness-r328-emergency-claim-witness-draft-hold-v1"
DOCS = {
    "a_body": ("preparedness/content/articles/family-communication-plan.body.html", "8ac8bd7dba3be15d477c15737e54d83364d72527"),
    "a_meta": ("preparedness/content/articles/family-communication-plan.meta.json", "dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3"),
    "t_body": ("preparedness/content/tools/family-reunification-card.body.html", "be8698ac5d020476ff649d85813810e2000c6f98"),
    "t_meta": ("preparedness/content/tools/family-reunification-card.meta.json", "47da1e7e20e39f0ea85e26d54a8d58301f6e0a15"),
}
# Witnesses are redline QUEUES, not approved claims or automated replacements.
# The official URLs indicate reviewer reading priorities, not that cited content proves a claim.
WITNESSES = (
    ("A15-911-SCOPE", "a_body", "call 911 for anything life-threatening", "P0_EMERGENCY", "https://www.911.gov/calling-911/"),
    ("T104-911-SCOPE", "t_body", "call 911 for anything life-threatening", "P0_EMERGENCY", "https://www.911.gov/calling-911/"),
    ("T104-TEXT-EMERGENCY", "t_body", "use text messages rather than calls for everything else", "P0_EMERGENCY", "https://www.911.gov/calling-911/frequently-asked-questions/"),
    ("A15-LOCAL-PRIVACY", "a_body", "keeps what you type on your own device", "P0_CHILD_PRIVACY", None),
    ("T104-PRIVACY-METADATA", "t_meta", "Nothing is stored.", "P0_CHILD_PRIVACY", None),
    ("A15-UNREVIEWED-CARD-LINK", "a_body", "{{link:family-reunification-card|", "P0_CHILD_PRIVACY", None),
    ("T104-PRINTED-CHILD-PRIVACY", "t_body", "A printed card can be lost", "P0_CHILD_PRIVACY", "https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html"),
    ("A15-MISSING-CHILD", "a_body", "If a child is missing after a disaster", "P0_REUNIFICATION", "https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html"),
    ("T104-MISSING-CHILD", "t_body", "If a child is missing after a disaster", "P0_REUNIFICATION", "https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html"),
    ("T104-SCHOOL-REUNIFICATION", "t_body", "School and childcare reunification", "P0_JURISDICTION", "https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html"),
)
RELEASE = dict.fromkeys(("publication_authorized", "independent_qd_pass", "qualified_emergency_review",
                         "child_privacy_approved", "source_claim_support_verified", "paid_offer_approved"), False)


def strict_json(raw: bytes):
    def unique_pairs(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError("duplicate JSON metadata key")
            data[key] = value
        return data
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_pairs)


def inspect(documents: dict) -> dict:
    """Classify *review needs* in supplied bytes; do not treat this as Git provenance."""
    errors, rows = [], []
    if type(documents) is not dict or set(documents) != set(DOCS):
        errors.append("FOUR_AUTHENTIC_DOCUMENT_ROLES_REQUIRED")
        documents = {}
    text = {}
    for role in DOCS:
        raw = documents.get(role)
        if type(raw) is not bytes:
            errors.append("MISSING_OR_NONBYTE_" + role.upper())
            continue
        try:
            text[role] = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            errors.append("NON_UTF8_" + role.upper())
    for role, number, slug in (("a_meta", 15, "family-communication-plan"),
                               ("t_meta", 104, "family-reunification-card")):
        if role not in documents or type(documents[role]) is not bytes:
            continue
        try:
            data = strict_json(documents[role])
            if (type(data) is not dict or type(data.get("n")) is not int or data["n"] != number or
                data.get("slug") != slug or data.get("status") != {"editorial": "drafted", "publish": "draft"} or
                type(data.get("safety_review")) is not dict or data["safety_review"].get("state") != "pending" or
                data["safety_review"].get("reviewer") is not None or
                data["safety_review"].get("date") is not None or
                type(data.get("source_use")) is not dict):
                errors.append("DRAFT_IDENTITY_OR_SAFETY_METADATA_DRIFT_" + role.upper())
            else:
                body = text.get("a_body" if role == "a_meta" else "t_body", "")
                citations = set(re.findall(r"\{\{cite:([a-z0-9-]+)\}\}", body))
                declared = set(data["source_use"])
                if citations != declared:
                    errors.append("CITATION_SOURCE_USE_DRIFT_" + role.upper())
        except (ValueError, UnicodeDecodeError, TypeError, KeyError):
            errors.append("MALFORMED_METADATA_" + role.upper())
    for claim_id, role, needle, risk, official_url in WITNESSES:
        content = text.get(role, "")
        occurrences = [m.start() for m in re.finditer(re.escape(needle), content)]
        if len(occurrences) != 1:
            errors.append("ANCHOR_MISSING_OR_DUPLICATED_" + claim_id)
            continue
        pos = occurrences[0]
        context = content[max(0, pos - 120): min(len(content), pos + len(needle) + 120)]
        rows.append({"id": claim_id, "file": DOCS[role][0], "risk": risk,
                     "offset_utf8": len(content[:pos].encode("utf-8")),
                     "context_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
                     "official_review_start": official_url, "review": "UNRESOLVED_QUALIFIED_HUMAN_REVIEW",
                     "publication_or_revenue_clearance": False})
    return {"schema": SCHEMA, "state": "INVALID_HARD_HOLD" if errors else "DRAFT_HARD_HOLD",
            "errors": sorted(set(errors)), "witnesses": rows,
            "review_required_count": len(WITNESSES), "qualified_approved_count": 0,
            "release": RELEASE.copy()}


def audit(reader) -> dict:
    """Git-pinned source audit; no data is written to input tree."""
    docs, errors = {}, []
    for role, (path, sha) in DOCS.items():
        try:
            raw = reader(path)
            if type(raw) is not bytes or custody.blob(raw) != sha:
                raise ValueError("Git source blob identity mismatch")
            docs[role] = raw
        except (OSError, ValueError, TypeError):
            errors.append("PINNED_GIT_BLOB_UNAVAILABLE_OR_DRIFT_" + role.upper())
    report = inspect(docs)
    report["errors"] = sorted(set(report["errors"] + errors))
    if errors:
        report["state"] = "INVALID_HARD_HOLD"
    report["git_pins_checked"] = len(docs)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    root = ap.parse_args().root.resolve()
    try:
        manifest_raw = custody.safe_bytes(root, custody.MANIFEST_PATH)
        docket_raw = custody.safe_bytes(root, "preparedness/audits/r320_conflict_adjudication_docket.json")
        if manifest_raw is None or docket_raw is None:
            raise OSError("Missing complete native source custody")
        manifest = strict_json(manifest_raw)
        docket = strict_json(docket_raw)
        if custody.validate_manifest(manifest, root)["errors"]:
            raise ValueError("native 82-source custody mismatch")
        if (len(docket.get("records", [])) != 15 or
            any(r.get("status") != "UNRESOLVED_HOLD" or r.get("automatic_selection") is not False
                for r in docket["records"])):
            raise ValueError("unreviewed source disputes cannot be removed or auto selected")
        report = audit(lambda p: custody.safe_bytes(root, p))
    except (OSError, ValueError, TypeError, UnicodeError, KeyError):
        report = {"schema": SCHEMA, "state": "INVALID_HARD_HOLD",
                  "errors": ["COMPLETE_NATIVE_CUSTODY_REQUIRED"],
                  "witnesses": [], "git_pins_checked": 0, "release": RELEASE.copy()}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report["state"] == "DRAFT_HARD_HOLD" else 1

if __name__ == "__main__":
    raise SystemExit(main())

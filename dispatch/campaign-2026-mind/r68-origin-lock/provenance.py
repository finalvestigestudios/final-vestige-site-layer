"""Read-only exact-Git-blob manuscript provenance verification for FV Dispatch R68.

Does not access WordPress, Gmail or the network. Does not write or send. A PASS
means file integrity of the currently stacked drafts ONLY, never send approval.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def blob_sha(content):
    """Git blob SHA-1 over the exact bytes, independent of Git CLI."""
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\x00" + content).hexdigest()


def load_manifest(path=MANIFEST):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit(manifest=None, root=ROOT, override=None):
    """Return an anonymized, deterministic and fail-closed provenance report.

    override maps repo-relative path -> substitute bytes; suitable for tests
    and never written to disk.
    """
    manifest = manifest or load_manifest()
    override = override or {}
    items = []
    for e in manifest["editions"]:
        rel = e["path"]
        path = Path(root) / rel
        raw = override[rel] if rel in override else path.read_bytes()
        actual = blob_sha(raw)
        text = raw.decode("utf-8")
        m = re.search(r"^\*\*Subject:\*\*\s*(.+)$", text, flags=re.M)
        subject = m.group(1).strip() if m else None
        correct_path = path.resolve().is_relative_to(Path(root).resolve())
        current_integrity = actual == e["stacked_blob"] and correct_path
        origin_drift = actual != e["original_blob"]
        approval_match = e["founder_approved_final_sha"] == actual
        if not e["founder_approved_final_sha"]:
            approval_match = False
        problems = []
        if not current_integrity:
            problems.append("SOURCE_BLOB_CHANGED")
        if not subject or subject != e["stacked_subject"]:
            problems.append("SUBJECT_MISMATCH")
        if origin_drift and not approval_match:
            problems.append("UNAPPROVED_SOURCE_DRIFT")
        if "[[VALID_POSTAL_ADDRESS_REQUIRED]]" not in text:
            problems.append("LEGAL_ADDRESS_HOLD_REMOVED")
        if "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]" not in text:
            problems.append("UNSUBSCRIBE_HOLD_REMOVED")
        if e["role"] == "commercial-reserved" and (
            "[[APPROVED_" not in text or "commission" not in text.lower()
        ):
            problems.append("MERCHANT_GATE_OR_DISCLOSURE_REMOVED")
        items.append({
            "id": e["id"], "role": e["role"], "subject": subject,
            "expected_stacked_blob": e["stacked_blob"],
            "actual_blob": actual, "current_integrity": current_integrity,
            "different_from_initial_master": origin_drift,
            "approved_as_final": approval_match,
            "problems": problems,
            "release": "HOLD_UNSENT_AND_HOLD_MERCHANT"
                if e["role"] == "commercial-reserved" else "HOLD_UNSENT",
        })
    flags = manifest["approvals"]
    approvals_missing = sorted(k for k, v in flags.items() if not v)
    integrity_ok = all(e["current_integrity"] for e in items)
    return {
        "schema": "fv-dispatch-origin-lock/report-1",
        "integrity_check": "PASS" if integrity_ok else "FAIL",
        "master_sha": manifest["original_master_commit"],
        "stacked_sha": manifest["observed_stack_commit"],
        "editions": items,
        "origin_drift_count": sum(e["different_from_initial_master"] for e in items),
        "subject_drift_count": sum(
            e["subject"] != manifest["editions"][i]["original_subject"]
            for i, e in enumerate(items)),
        "approvals_missing": approvals_missing,
        "launch_decision": "HOLD_UNSENT",
        "note": "PASS means source bytes only, not consent, deliverability, or legal compliance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Fail only on unexpected source bytes; all releases still HOLD")
    args = parser.parse_args()
    out = audit()
    print(json.dumps(out, indent=2))
    if args.check and out["integrity_check"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

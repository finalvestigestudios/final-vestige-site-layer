"""Read-only gate for Dispatch R104: NEVER sends, approves, or modifies anything."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LEDGER = HERE / "version_and_delivery_lock.json"
PROOFS = (
    "affiliate_zen12_email_permission",
    "affiliate_total_focus_email_permission",
    "live_zen12_warmup_guide",
    "live_total_focus_warmup_guide",
    "valid_final_vestige_postal_address",
    "received_real_jetpack_mime",
    "working_unsubscribe",
    "verified_subscriber_eligibility",
    "founder_exact_version_selection",
    "founder_final_send_approval",
)

def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + bytes([0]) + data).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def audit(root=ROOT, ledger_path=LEDGER):
    root, ledger_path = Path(root), Path(ledger_path)
    lock = read_json(ledger_path)
    problems = []
    manifest_path = root / "manifest.json"
    manifest = read_json(manifest_path)
    inherited = lock.get("inherited", {})
    original = lock.get("original", {})
    if git_blob_sha(manifest_path.read_bytes()) != inherited.get("manifest_sha"):
        problems.append("Inherited manifest blob mismatch.")
    issues = inherited.get("issues", [])
    if len(issues) != 6:
        problems.append("Six inherited issue blobs required.")
    for item in issues:
        filename = item.get("file", "")
        p = root / "issues" / filename
        if not p.is_file() or git_blob_sha(p.read_bytes()) != item.get("sha"):
            problems.append("Issue source mismatch: " + filename)
    older = original.get("issues", [])
    if original.get("manifest_sha") == inherited.get("manifest_sha") or len(older) != 6:
        problems.append("Original and inherited master manifest provenance invalid.")
    for a, b in zip(older, issues):
        if a.get("file") != b.get("file") or a.get("sha") == b.get("sha"):
            problems.append("Original versus inherited master issue provenance invalid.")
    if lock.get("founder_version_selection") is not None or lock.get("founder_send_approval") is not False:
        problems.append("Unexpected founder approval/selection assertion.")
    for key in PROOFS:
        if lock.get("required_evidence", {}).get(key) is not False:
            problems.append("Unverified or modified evidence: " + key)
    wp = lock.get("current_jetpack", {})
    if (wp.get("mode") != "excerpt" or wp.get("auto_send") is not False or
            wp.get("verified_email_eligible") is not None or wp.get("welcome_received") is not False):
        problems.append("Native newsletter delivery or audience assumptions altered.")
    if any(x is not None for x in lock.get("metrics", {}).values()):
        problems.append("Fabricated email/affiliate analytics must be absent.")
    if lock.get("commerce_slots") != [3, 5] or lock.get("editorial_slots") != [1, 2, 4, 6]:
        problems.append("Original 4:2 pilot allocation altered.")
    listed = manifest.get("issues", [])
    if len(listed) != 6:
        problems.append("Manifest must contain six issues.")
    if [i.get("number") for i in listed if i.get("kind") == "commercial-review-pending"] != [3, 5]:
        problems.append("Commercial issue slots no longer match.")
    for item in listed:
        if item.get("publish_state") != "hold" or item.get("merchant_affiliate_url") is not None:
            problems.append("Unapproved sending/link activation for issue " + str(item.get("number")))
        if item.get("kind") == "commercial-review-pending" and not item.get("editorial_cta", "").startswith("[[APPROVED_"):
            problems.append("Commercial warm-up guide was activated without evidence.")
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        problems.append("Master scheduling guard removed.")
    if lock.get("status") != "HOLD_UNSENT":
        problems.append("Lock status tampered with.")
    return {
        "status": "HOLD_UNSENT",
        "issues_03_05": "HOLD_MERCHANT",
        "source_audit_passed": not problems,
        "problems": problems,
        "verified_email_audience": None,
        "permission_to_send": False,
        "note": "Source integrity NEVER constitutes founder approval or live email rendering evidence."
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))

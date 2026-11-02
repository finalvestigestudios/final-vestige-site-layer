#!/usr/bin/env python3
"""Write release/production-change/* from an inline-delivery stage.

  python make_production_change.py --stage <work/stage built with --delivery inline>

Refuses to run unless the original block, rebuilt from the public snapshot, hashes to the live
block_hash recorded by page-sections.list on 2026-11-02 (so the rollback copy is verifiably the
live bytes).
"""
import argparse, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LIVE_BLOCK_HASH = "1c97fec5cc356a02fb2f51a092f749c81efcd98c"
LIVE_BLOCK_HASH_2 = "abc983ae1b3cf45d35589c7e5366ccc522cb0462"
TOKENS = {"expected_modified": "2026-10-30T09:14:14", "expected_content_hash": "7afdb933d2ec68fd993ef015c97a6eb9edfe0576"}
sha1 = lambda t: hashlib.sha1(t.encode()).hexdigest()
sha256 = lambda t: hashlib.sha256(t.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True, type=Path); a = ap.parse_args()
    out = HERE.parent / "release" / "production-change"; out.mkdir(parents=True, exist_ok=True)
    snap = (HERE / "snapshot" / "page6-live-frontend-body.html").read_text(encoding="utf-8")
    i, j = snap.index('<section class="fv-studios-hero"'), snap.index('<section class="fv-focus-cta"')
    orig = "<!-- wp:html -->\n" + snap[i:j].strip() + "\n<!-- /wp:html -->"
    if sha1(orig) != LIVE_BLOCK_HASH:
        raise SystemExit("original block does not match the live block_hash; do not proceed")
    new = (a.stage / "production-replacement-block.html").read_text(encoding="utf-8").rstrip("\n")
    # --- operation 2: Focus CTA accessible name (WCAG 2.5.3 Label in Name). The original is the RAW
    # block (read via pages.get context=edit on 2026-11-02) and must hash to the live block_hash.
    o2 = (out / "original-block-index2.html").read_text(encoding="utf-8")
    if sha1(o2) != LIVE_BLOCK_HASH_2:
        raise SystemExit("original block 2 does not match the live block_hash; do not proceed")
    label = ' aria-label="Get the free Seven Day Focus Fieldbook"'
    if o2.count(label) != 1:
        raise SystemExit("expected exactly one aria-label on the Focus CTA button")
    n2 = o2.replace(label, "")  # accessible name becomes the visible text, which is what 2.5.3 requires
    (out / "replacement-block-index2.html").write_text(n2, encoding="utf-8", newline="")
    (out / "original-block-index1.html").write_text(orig, encoding="utf-8", newline="")
    (out / "replacement-block-index1.html").write_text(new, encoding="utf-8", newline="")
    keep = [(0, "core/html", "72 Hidden in the Margins strip", "6948a35c4e60ff43154440a7fad980dc3cae6859"),
            (3, "core/group", "home shell incl. Jetpack subscription (Dispatch), latest, trails, research desk", "f9da41225609adcca1c23f18b39079d1275c9249"),
            (4, "core/html", "Enter the record", "e53df6922591588603a41ce2e56dfdc418ba2d98"),
            (5, "core/html", "Organization JSON-LD", "9454d1e44ee4932a4975796a88d2640ab9ecae8d")]
    doc = {
        "status": "PROPOSED - NOT APPLIED - requires explicit founder approval; re-run page-sections.list first and refuse if modified/content_hash differ from these tokens",
        "target": {"wpcom_site": 256784396, "page_id": 6, "read_at": "2026-11-02", "top_level_blocks": 6,
                   "block_to_replace": {"index": 1, "type": "core/html", "block_hash_sha1": LIVE_BLOCK_HASH, "what": "old Studios hero (+ its <style>)"}},
        "blocks_left_untouched_byte_for_byte": [{"index": k, "type": t, "what": w, "block_hash": h} for k, t, w, h in keep],
        "apply": {"operation": "page-sections.replace",
                  "params": {"id": 6, "index": 1, "expected_block_type": "core/html", "expected_block_hash": LIVE_BLOCK_HASH, **TOKENS, "block_markup_file": "replacement-block-index1.html"},
                  "replacement_sha256": sha256(new), "replacement_sha1": sha1(new), "replacement_bytes": len(new.encode())},
        "operation_2_optional": {"what": "Focus CTA button: remove aria-label so the accessible name equals the visible text (WCAG 2.5.3)",
                                 "run_after": "operation 1, with FRESH lock tokens from page-sections.list (content_hash changes after operation 1)",
                                 "params": {"id": 6, "index": 2, "expected_block_type": "core/html", "expected_block_hash": LIVE_BLOCK_HASH_2, "block_markup_file": "replacement-block-index2.html"},
                                 "replacement_sha1": sha1(n2), "replacement_bytes": len(n2.encode()),
                                 "rollback_params": {"id": 6, "index": 2, "expected_block_type": "core/html", "expected_block_hash": sha1(n2), "block_markup_file": "original-block-index2.html"},
                                 "original_block_sha1_verified_against_live_block_hash": True},
        "rollback": {"operation": "page-sections.replace",
                     "params": {"id": 6, "index": 1, "expected_block_type": "core/html", "expected_block_hash": sha1(new), "block_markup_file": "original-block-index1.html"},
                     "original_block_sha1_verified_against_live_block_hash": True,
                     "also_available": "WordPress post revisions for page 6 (restore the revision dated 2026-10-30T09:14:14)"},
        "no_plugin_install": True, "no_theme_or_navigation_change": True, "no_new_pages_in_the_change_itself": True,
        "unverified_on_wordpress_com": "Whether WordPress.com keeps inline <style>/<script> inside a core/html block on the Personal plan is NOT TESTED: existing blocks already carry <style> and a JSON-LD <script>, but a dry run is required (RELEASE_AND_ROLLBACK.md step 1).",
    }
    (out / "PROPOSED_PRODUCTION_CHANGE.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(json.dumps({"replacement_bytes": len(new.encode()), "replacement_sha256": sha256(new), "original_bytes": len(orig.encode())}))


if __name__ == "__main__":
    main()

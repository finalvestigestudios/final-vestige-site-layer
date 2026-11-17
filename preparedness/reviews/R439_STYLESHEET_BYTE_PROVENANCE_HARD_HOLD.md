# R439 — Offline stylesheet byte, SRI and import-graph custody (DRAFT / HARD HOLD)

**2026-11-17 PT · Issues #136 / #820 · Preparedness-only engineering.** Parent R438 PR #2885 at exact SHA `335c0fe4f6ed25e366dbe3aff38ffdc54dd1511a`. No edits to the original 35 article manuscripts, original 203 source IDs / 280 occurrences, 17 exact-URL review groups, 5 source-scope disputes, 9 unresolved Shelter forks, canonical routes, existing safety states, production pages, navigation, analytics or contributor branches.

## Gap and scope
R438 detects unverified `<link rel=stylesheet>` and `@import` dependencies but cannot prove their actual CSS bytes. R439 is an **additional offline evidence bridge**, not a reason to clear R438's hard hold. Given independently captured CSS bytes, exact SHA-256/length/MIME/capture records and authentic WordPress/private-preview exports, R439 checks both channels' complete *referenced CSS import graph* with a deterministic digest. It validates available SRI sha256/384/512, rejects stale pins, missing bytes, invalid/untrusted origin, encoded path traversal, cycles, depth/node overrun, unreferenced asset records and unsafe local file identities. It escalates non-import `url()`, CSS escapes and unknown import grammar to a human/browser review rather than granting clearance. Linked screen-only and print styles are both included. No network fetch and no writes.

**Threat boundary:** Correctly matched CSS bytes and capture IDs do **not** establish author trust, accessibility, visible warning effectiveness, source/citation accuracy, safe advice, QD approval, or a real site release. A recorded `capture_id` is a provenance *claim*, not an independently attested capture. Real CSS can include legitimate remote assets, query-versioned stylesheet URLs or WordPress dynamic template dependencies: current conservative rejection/flags require manual adjudication, not silent production whitelisting.

## Exact locally executed evidence
- `python -I -m unittest discover -s preparedness/tests -p 'test_r43*.py' -q`: **637/637 PASS** in one locally reconstructed R430–R439 test-only tree, including **75/75 new R439** cases. Earlier 562 inherited. The run does *not* establish a native 35-article repository build.
- `python -m compileall -q preparedness/tools preparedness/tests`: PASS.
- R439 CLI with nonexistent authentic inputs: **exit 2 / DRAFT_HARD_HOLD**, with release/qualified-safety/commerce boolean fields false.
- Executed source Git blob **`31493028511bbe6150705d9624fff940e9688278`**, executed test Git blob **`eb5b515990a4234ce0d0266952c1c132117b7e7d`**; both remotely fetched from this PR and match tested local byte content.
- Tests are synthetic/adversarial, not actual CSS/browser/CMS/source/merchant or QD checks. Hosted CI is not claimed green.

## Evidence still necessary
1. A complete authenticated native checkout and explicit `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and complete isolated unittest suite from the *exact* final commit.
2. The 35 genuine original article manuscripts, original Git object pins, all 70 authentic WP/private-preview export HTML artifacts, and CSS asset byte captures with independent origin attestation, hashes and content-type records.
3. Actual mobile/desktop/print/no-JavaScript browser computed-style QA and qualified food/emergency/medicine/child-privacy source adjudication. PR #157, fixture #169 and dependent #2205 remain independent draft proposals; no bypasses.
4. A genuinely purchasable, FV-owned/approved, rights-cleared Preparedness practical pack with working payment, fulfillment and refunds before any paid CTA. Tool #102 plan-builder vs. Tool #104 wallet-card distinctions are unresolved. Do not reuse retired water freebies.

## Conversion-first pilot *proposal only*
**Offer** existing verified paid Preparedness SKU (none authenticated) → **funnel step** already-published rights-cleared Grok family-contact asset_id → existing LIVE FREE `https://finalvestige.com/preparedness/` official-resource guide → optional separately qualified practical tool → explicitly optional confirmed paid pack. **Blockers** missing asset_id/post rights/UTM, Tool #102/#104 identity and QD, merchant SKU/payment/delivery/refund proof. **Experiment** only after founder release/commerce approval, match one proven social intent and mobile URL, draft free CTA “Review the official household emergency checklist,” perform keyboard/mobile/print/no-JS/privacy/disclosure and checkouts before release. **Pass evidence** actual source-backchecked article, approved offer, verified paid order and fees/refunds, 7/30d attributable qualified human sessions; **owner** Grok/Praxxis creator verification, Preparedness/QD content, Claude site/analytics, founder commerce/release. Unknown orders and net revenue per 1,000 qualified sessions: **NOT COMPUTABLE**. Clicks, leads and checkout starts are not sales.

**Review state is permanently DRAFT / HARD HOLD for this technical gate.** No publishing, CMS/navigation changes, affiliate/merchant activation, social/email/analytics writes, spending, or false QD PASS.

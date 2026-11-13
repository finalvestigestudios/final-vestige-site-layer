# Dispatch R323 — merchant sample ≠ Final Vestige subscriber
R323 is a distinct additive review-only draft PR based on master PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. It does **not** replace the approved six-issue manifest, email manuscripts or the previously built PR #201 readiness system. Review with Dispatch #174 and Mind #171; source-of-truth business issue #820.

## Artifacts
- `03-merchant-consent-review.txt`: original full Issue #03 optional subject/preheader/body with disabled guide CTA, adjacent prospective disclosure, official source URLs, legal footer hard stops.
- `03-merchant-consent-review.html`: static table-based, inline-style no-image no-JS reviewer version. NOT an actual Jetpack/MIME preview.
- `gate.cjs` and `gate.test.cjs`: standalone read-only synthetic provider separation and settled-revenue guards. Execute `node --test dispatch/r323/gate.test.cjs` in a proper full checkout. Inputs are hypothetical; passing tests does NOT prove real providers, email compliance or consent.
- `EVIDENCE_LEDGER.json`: evidence statuses with unknowns and all approvals FALSE.
- `BUYER_CONSENT_AND_CONVERSION_DOSSIER.md`: official merchant versus FV consent boundary, 4:2 editorial ratio, checked claims, exact commercial blockers and analytics handoffs.

## Required review sequence
1. Re-run native master `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` on exact PR #175. Use Git blob hashes for source identity. Do not reword originals.
2. Validate complete source links and visibly conditional disclosure. Seller gift https://zen12.com/gift explicitly states the visitor receives seller newsletter; that is not the FV Dispatch list.
3. Verify separate FV provider active email subscription via private source-of-truth, not a success URL or PDF download. No raw recipient addresses in GitHub.
4. Obtain independently witnessed sender postal/unsubscribe and actual received Jetpack HTML/plaintext. A static preview is not that witness.
5. Obtain Mind/Commerce signed account approval for email promotion, exact issued earning URL, current checkout/refund rights, and *published approved* first-party guide. Never insert a merchant link into draft without these.
6. Founder approves final selected copy, recipient audience, cadence, and separately sending before any publication. Keep newsletter default-post-send OFF and commercial editions on HOLD.

## Verification categories, NEVER conflate
BUILT = asset committed. TESTED = actual tests executed and exact source captured. LIVE = on production (none of this package). VERIFIED = independent evidence from the actual claimed provider/merchant. No real subscriber, purchase, delivery, affiliate rights, A/B win or revenue is asserted.

## Relevant first party pages
https://finalvestige.com/dispatch/ ; https://finalvestige.com/focus/ ; https://finalvestige.com/editorial-standards/

# Dispatch R104 — master manuscript provenance lock and native Jetpack release gate

**DRAFT REVIEW ONLY. Nothing here authorizes publication, a test message, a subscriber contact, or sending.** Owner: GitHub Issue #174; companion #171. Built on R103 draft PR #872. Frozen homepage PR #49 not touched.

## Critical correction: two masters are different

The original six-issue source in PR #175 at d57ccdba3aee8f065e143e101c2945f4f3d01647 is **not** the same as the six master issues inherited by later stacked branches after PR #178. All six issues and the manifest have different Git blob SHA-1 values (7/7). The embedded version_and_delivery_lock.json pins both sets of blob hashes, original commit and inherited commit b40c6cc5784175e743ccd99381bfee191e693deb.

An example that matters: original Issue 04 subject **Fourteen seconds. A much longer explanation.** became **Seventeen seconds. A much longer explanation.** The independent, optional R103 Apollo issue proposes **The test they called nonhazardous**, not an automatic substitution. The original founder approval covered a six-issue draft framework, not each revision or permission to email. The final creative selection must be **issue-by-issue with exact source SHA**.

## Live WordPress source-of-truth checks at November 4, 2026 02:33 UTC

Authenticated WordPress ID 256784396: newsletter enabled; new-post automatic sending OFF; reply-to no-reply; sender display Final Vestige; delivery mode EXCERPT. Exact Fieldbook PDF is configured in the 52-page welcome message, but actual receipt is unverified. Status endpoint: total=2, confirmed=2, unconfirmed=2. A separate, complete Jetpack follower report: email=0, WordPress.com=2, partial=false. **Verified email-eligible recipients: UNKNOWN** (neither four nor two should be claimed as recipients). Five recent events are never_sent_opted_out and have no dispatched timestamp or sent/recipient counts; they are not campaign emails.

The official WordPress documentation says EXCERPT mode uses the manually set post excerpt or, failing that, the first 55 words. A complete 400–500 word newsletter manuscript would not arrive as written under this configuration. The campaign preheader is only proposed copy; an independent preheader field is not verified in Jetpack. WordPress sender address is donotreply@wordpress.com even when visible From name says Final Vestige. We must compare the real received MIME, including multipart HTML and plain text, address and unsubscribe, before approving anything. No custom email platform, no second subscriber list, no settings changes.

WordPress official: https://wordpress.com/support/newsletter-settings/ and https://wordpress.com/support/newsletter/email-appearance/ .

Live /dispatch/ (page 523) has the sole Jetpack signup block and offers investigations, archive finds and the Focus Fieldbook, but lacks the affiliate-recommendation expectation present on /focus/ (page 1579). A separate approved live-page revision would be required; this PR does not edit WordPress. The live /editorial-standards/ (page 17) emphasizes primary sources, disclosure of uncertainty, correction notes, and independence from commercial relationships.

## Commercial and evidence hold

Original pilot is 01/02/04/06 editorial, 03 Zen12 and 05 Hypnosis Live Total Focus reserved for commercial placement. Mind & Affiliate Studio Issue #171 owns the not-live product guides. Current exact Total Focus seller page describes a **33 minute / 47 MB audio** by J.A. Amos; prices differ across recent seller snapshots ($17.95 observed on a recent indexed result, versus older $24.44 reports), so the newsletters must not advertise a fixed price or current discount. The seller's hypnosis and brain-changing outcome claims are **not independently established**. Zen12's 12-minute = 60-minute equivalence likewise remains a marketing claim, not a demonstrated result. Specific refund and purchase terms must be checked directly at final checkout, rather than assuming a catalog page establishes them.

An affiliate portal or seller product page **is not** proof that Final Vestige was accepted, that email promotion is authorized, that a tracking link is licensed, that creative is approved, or that personally identifiable referral records may be excluded. Gmail searches Nov 3 found no qualifying named Inspire3 authorization or received Jetpack welcome; a 2026-10-25 signup confirmation isn't the welcome email. No merchant was contacted, and no link made live.

Before any commercial send: a valid Final Vestige postal mailing address (merchant/Automattic address does not qualify), legal/compliant opt-out that actually works in received email, named sender, honest subject, near-offer disclosure, proof of authorized email promotion, verified checkout/refund/audio claims, the two approved first-party buyer guides, and final founder authorization of audience/cadence/exact creative. FTC guidance: https://search.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## QA execution / operational behavior

Run: python dispatch/campaign-2026-mind/r104-release-lock/release_gate.py
Test: python -m unittest discover -s dispatch/campaign-2026-mind/r104-release-lock/tests

The read-only audit checks every inherited blob SHA using Git's own SHA-1 blob framing, compares it with original PR #175 source provenance, validates the 4 editorial / 2 commercial contract, verifies inactive links and all false attestation flags, rejects invented audience or metrics, and **returns HOLD_UNSENT in every case**. The 24 native unittest definitions include adversarial mutations. Tests cannot prove the truth of claims, legal sufficiency, recipient eligibility or actual send rendering.

Historical CI last completed with **2,215 Python tests at R101**. R102 and R103 GitHub Actions were observed failing pre-run, before any job steps (do NOT count their new test definitions as passed). Independently verify GitHub Actions behavior before reporting hosted success. No homepage, newsletter, list, posts, settings or live affiliate destinations changed.

## Exact next release decisions

1. Founder selects the exact SHA for every issue; do not assume PR #178-derived master supersedes PR #175 or later optional copy.
2. Mind owner supplies live vetted first-party Zen12/Total Focus guides and written offer-specific email permission, link format/creative approval and aggregate-only reporting.
3. Verify a registered Final Vestige business mailing address, genuine received MIME + functioning unsubscribe, private subscriber eligibility and actual Fieldbook welcome receipt.
4. Only after those proofs, explicitly seek final founder approval to send with precise recipients, schedule and copy. Until then: **all six HOLD_UNSENT; 03/05 extra HOLD_MERCHANT**.

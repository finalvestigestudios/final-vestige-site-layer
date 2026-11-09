# Dispatch R232 — Hidden-footer / multipart legal-proof gate (DRAFT, UNSENT)

**Master:** [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · **Inherited baseline:** [R231 #1740](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1740), HEAD `9fd69b1d62dc684e3cf11fa9e280dffd3a39b089`. **The original six issues and R231 files are untouched.** Homepage PR #49 remains untouched. The four-editorial/two-commercial campaign is unchanged.

## Independently reproduced problem in R231

The R231 MIME inspection is intentionally incapable of authorizing a send, but its *technical candidate* may show zero blockers while the purported physical-address and unsubscribe evidence is hidden from the reader. The old HTMLParser suppresses `<script>`, `<style>`, and `<head>`; it **does not suppress `hidden`, `style="display:none"`, `aria-hidden="true"`, or `<template>`**. The old address check also combines plain text and HTML, enabling a plaintext-only address to satisfy a purported rendered-email check when HTML lacks it.

**Controlled synthetic reproduction:** one HTML alternative contains only a hidden address and hidden `Unsubscribe` anchor; text/plain says "No footer". R231 reports `verified_publisher_address_visible=true` and `has_syntactically_valid_body_optout_url=true`. These signals are **false evidence of visual compliance**, not proof that a real Jetpack email violates CAN-SPAM. R231 still returns `HOLD_UNSENT_REVIEW_ONLY` and never authorizes sending.

## New fail-closed independent implementation

- `visible_footer_gate.py` wraps R231 and separately inspects plain-text and HTML MIME alternatives, ignoring attachments and handling common hidden content: `hidden`, `aria-hidden`, `inert`, `display:none`, `visibility:hidden`, `opacity:0`, and `template` / script / style / head / noscript. Hidden link text cannot count.
- Require separately: an externally attested publisher-address string in plaintext AND visible HTML; an HTTPS opt-out instruction in plaintext AND a visible, labeled, syntactically valid HTML opt-out anchor. A header-only List-Unsubscribe is insufficient for this more conservative offline review requirement.
- Opaque HTTPS opt-out URLs remain acceptable when the visible label is `Unsubscribe`; invalid `javascript:`/mailto-only anchors are not treated as verified Jetpack HTTPS opt-outs. The runtime reports only booleans, generic blockers and HOLD; **no sender, recipient, address, URL token or email body is emitted.**
- This is **not** a full email client renderer or a legal opinion. Stylesheets, responsive rendering, dark mode, accessibility, live opt-out, mailing-address ownership and actual provider delivery require separately authorized verification. It never sends email or enables merchant links.

## Native verification

**Executed locally with Python 3.13 on exact GitHub-matched R232 module and test source**, not a simulated V8 port:

`python -m unittest discover -s dispatch/r231/tests -q` → 25/25 PASS on inherited R231 source;
`python -m unittest discover -s dispatch/r232/tests -q` → 18/18 PASS on new R232 source.

Git blobs: R232 module `28b49fc300001177d3c057f2bc0e9b4a87894519`; R232 tests `24e10e12df462172323f5c4db49f6c7691437382`. Exact R231 module `2fb3c12ee588fa3b97022476c329f7eb2ee2f39e`, tests `146e20731e94d010e83c235e3e177bfdb9a8074f`. These tests use **example.invalid-only synthetic fixtures**. The original campaign #175's full six-test Python suite still has **not** been executed against a native complete checkout; no claim otherwise.

## Dated source of truth — November 9, 2026

Authenticated read-only Jetpack status at 12:31 UTC: Newsletter enabled; new-post auto-emails OFF; full-content format; sender display Final Vestige Studios; configured 52-page Focus Fieldbook welcome; five recent posts never sent. Counters total=3, confirmed=3, unconfirmed requests=2, suppressed=0; populations NOT additive, actual eligible recipient count UNKNOWN. No validated received Fieldbook welcome, genuine Jetpack EML, approved FV postal address, working unsubscribe, or subscriber consent ledger. This artifact neither alters settings nor contacts any recipient.

Official seller sources reviewed November 9: https://zen12.com/hnp (advertises 12 levels / 48 Premium MP3s and unsupported product-specific 12-minute equivalence); https://hypnosislive.com/mental-skills/total-focus (advertises one 33-min 47-MB recording, $24.44 standalone display vs $19.95 per-item *bundle* display, not verified cart); https://hypnosislive.com/faq (refund caveats). **No named Final Vestige merchant acceptance, EMAIL promotion rights, issued earning link or approved live warm-up guide verified; do not use merchant promises as evidence of efficacy.** See Mind handoff #171 and draft #1743.

## Owner priorities (OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER)

| Offer | Funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| Zen12 | editorial issue 03 → guide → purchase | account email rights, guide, real earning URL missing | authenticated merchant attestation and exact published guide | **HOLD_MERCHANT** | Mind #171 |
| Total Focus | issue 05 → guide → checkout | same rights/guide; checkout/refund not independently verified | permission and current cart / terms | **HOLD_MERCHANT** | Mind #171 |
| Focus / Dispatch | confirmed signup → welcome | counters do not establish eligible consent, real receipt unknown | read-only status reconciliation and authorized received-mail inspection | **UNKNOWN** | Focus #129 / Dispatch |
| Dispatch | newsletter → inbox | R231 hidden-footer false-positive plus no real sample | apply R232 to *separately authorized* authentic EML and manual rendering / opt-out QA | synthetic **43/43 PASS**, real evidence **NOT TESTED** | Dispatch / Site QA |
| Affiliate | paid order → realized net revenue | no independently settled order data, no qualified-session denominator | provider-confirmed conversions less refunds and fees | **NOT COMPUTABLE** | Commerce / Praxxis #820 |

**Release: all six HOLD_UNSENT; issues 03/05 HOLD_MERCHANT.** No email, test email, schedule, WP post/settings/list modification, merchant activation, analytics deployment, Grok publishing/queue edits, spend or PR merge. Founder retains final release rights.
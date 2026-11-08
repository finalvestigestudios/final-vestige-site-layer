# Final Vestige Dispatch — R9 MIME integrity security gate (DRAFT / HOLD)

Owner: Issue #174, coordinated with Mind & Affiliate Issue #171. **Parent PR #227**; separate stacked branch. Final Vestige homepage priority #1 and frozen homepage PR #49 untouched.

## Four original red-case findings

The previous exact PR #227 auditor passed **49/49 existing tests**, but a new synthetic adversarial corpus found **four false-positive classes**:

1. An HTML-visible vendor purchase URL without a clickable \`<a>\` tag, absent from plain text, was ignored: \`no_direct_merchant_link=PASS\` even though email clients may auto-link it.
2. A vendor-hosted \`<img src>\` URL passed because only anchors were inspected; the email could initiate an unapproved vendor resource request.
3. A commission disclosure hidden with \`<style>.ghost{display:none}</style>\` passed as visible. This also affects postal and unsubscribe elements and approved first-party CTA links.
4. Two conflicting \`text/html\` MIME alternatives were concatenated, allowing separate renditions to jointly satisfy checks even if no reader would see both.

## New source-controlled gate

The existing read-only \`mail-proof/received_email_audit.py\` now inventories HTTP(S) URL references from HTML text, all tags and attributes, CSS URL declarations, and comments. Merchant URL detection still uses parsed hostnames; a lookalike \`zen12.com.evil.invalid\` is **not** misclassified as the merchant. Simple class/id CSS visibility is handled even when the stylesheet occurs after markup. Complex/media hidden CSS returns \`HOLD_RENDERING_UNVERIFIED\`, never a fabricated visible disclosure. Multiple HTML/plain parts, malformed/duplicated/missing From/To/Subject, and embedded forwarded MIME produce a fail-closed HOLD. The report explicitly marks real email-client computed visibility UNKNOWN. No extra network API, email sending, publishing, contact collection or merchant earning links.

**Executed local QA** on identical staged source: the **49 inherited tests** plus **23 new R9 regression tests** in \`tests/test_rendition_integrity_r9.py\` all PASS, **72/72 total**. New test inputs are deliberately fictional and private. The patched auditor's Git blob SHA must match locally tested \`079a965169a1abea973b4b3b55ec908b518775d1\`, and R9 test blob must match \`5e454c1ae9b107f79a5f0b2e7313b66f79b7ec52\`. Rerun on exact GitHub checkout and CI; hosted CI is not certified by this local run.

## Authentic source-of-truth reads (2026-10-30)

Authenticated WP (site ID 256784396): Jetpack newsletter enabled, \`email_new_posts_by_default=false\`, \`email_content_format=excerpt\`, \`recent_sends=[]\`; welcome **configured** with 52-page Focus PDF but actual delivery unverified. Subscriber counters are logically contradictory as nonoverlapping sets: total=2/confirmed=2/unconfirmed=2/suppressed=0/imported=0; deduplicated eligible audience NOT verified. Published /dispatch/ (page 523), /focus/ (1579), Editorial Standards (17) and Affiliate Disclosure (14) were read-only reviewed. The Focus/Dispatch forms were not submitted. A targeted Gmail search showed consumer promotions and a subscription confirmation, but not merchant-specific affiliate email permission or actual received Focus welcome.

Zen12 product page https://zen12.com/about describes 12-minute sessions, 12 levels and music/guided/nature/white-noise options. Its equivalence to an hour of meditation is **seller rhetoric**, not independently established. Hypnosis Live Total Focus https://hypnosislive.com/mental-skills/total-focus describes 33 minutes and 47MB; sale price and refund claims are checkout-sensitive and must be rechecked. Inspire3 public affiliate portal https://affiliates.inspire3.com/ describes registration, **not account acceptance/email-channel permission or approved links**.

FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business specifies accurate headers/subjects, sender physical address and opt-out requirements for qualifying commercial email. Automattic's address in a subscription-confirmation message cannot establish Final Vestige's business mailing address.

## Scope, limitations and release HOLD

**No** WordPress test email, newsletter send or scheduling, publish, setting change, subscriber import, official partner outreach, or live first-party/merchant earning link was performed. Original six issues and optional commercial rewrites remain unchanged at the founder's 4:2 split. No paid platform added. The email auditor only parses *authorized supplied* .eml files; it does **not** authenticate DKIM, simulate Outlook, prove unsubscribe function, run WordPress email client, prove email consent or legal compliance, or authorize anything. No actual .eml exists yet.

**Outstanding:** founder-authorized genuine WP self-test/received .eml; legal FV postal address and unsubscribe verification; private eligible/audience reconciliation; published vetted first-party product guides; account-specific Inspire3 acceptance + email→guide→merchant traffic rights, link format, creative license and current checkout terms; independent QD/hosted CI and explicit final founder issue/audience/date/send approval. **All six sends remain HOLD.**

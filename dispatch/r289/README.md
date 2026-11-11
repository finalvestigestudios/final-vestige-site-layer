# Dispatch R289 — Plaintext merchant-link escape, not another newsletter draft

**2026-11-11 13:30 PT. Unpublished / unsent / review-only.** Stacked over draft PR #2094; source of truth [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Original six from PR #175, release gate from #201, exact six email HTML/plaintext specimens from PR #2087. **Do not adopt these two additional review specimens as campaign copy.** No production writes, social posting, subscriber operations, paid services or test sends.

## Material new observation — HIGH severity for release governance

The original **commercial HTML** specimens in `dispatch/r287/issue-03.html` and `issue-05.html` removed clickable seller-page anchors. However the accompanying **plaintext** specimens still contain full seller destinations in their `SOURCES FOR REVIEW` sections: two Zen12 URLs in Issue 03 and one Hypnosis Live Total Focus URL in Issue 05. Many email clients auto-link bare HTTPS URLs. Calling a source URL 'not a purchase link' does not make it inert; one goes to a special-promotion checkout. This could bypass the intended disabled buyer-guide CTA if somebody copies the draft plaintext into an outbound email. This is an **offline source-risk finding**, not proof that an email was sent or a customer clicked.

## Narrow mitigation — review-safe plaintext without changing source manuscripts

- Two `issue-XX.safe-review.txt` variants are byte-derived from the original PR #2087 plaintext with only those **three merchant-source URLs** replaced by explicit non-URL reviewer-ledger references. Original copy, disclosure, blocked CTA, official independent research sources, and all release HOLD markers remain unchanged. The original sources remain preserved for traceability at `source-evidence.json`, which is **not distributable email copy**.
- `merchant-link-auditor.mjs` is a dependency-free, read-only preflight. It finds ordinary, percent-encoded, numeric-entity-encoded, case-normalized, whitespace-padded and zero-width-obfuscated seller domains in prospective email text. This is a risk screen, **not** complete URL deobfuscation, an email sender, or a legal compliance certificate.
- `merchant-link-auditor.test.mjs` tests adversarial and valid fixtures and asserts that both derivatives match the original files except for intended URL removal. This suite can be executed with Node, and the underlying pure functions were also independently executed on the exact current GitHub originals in the R289 review.
- `review-board.html` contains a static accessible comparison of the three link findings and live evidence gaps. It has no vendor outbound links, analytics or scripts.

## Why this must remain unsendable

Even the safer plaintext variants contain unresolved `[[APPROVED_...]]` CTA placeholders and legal footer placeholders. The publisher-specific final physical postal address, recipient eligibility, vendor approval, permission to use the **email channel**, issued earning URL, creative rights and actual Jetpack unsubscribe rendering are NOT VERIFIED. The test deliberately reports **HOLD_UNSENT** despite passing the seller auto-link screen. A plain-text vendor URL is neither proof of affiliate acceptance nor attribution, and an academic source link is not an efficacy guarantee.

### Source quality and product-message boundaries

Official Zen12 pages describe twelve levels / four formats per level and advertise significant claims about the effect of twelve-minute sessions. The seller's promotional pages have changeable coupon pricing; DO NOT quote a price or assert equivalence to hour-long meditation as independent science. Official Hypnosis Live's Total Focus sales page describes a 33-minute / 47-MB recording and makes strong focus-effect claims; neither these claims nor its advertised refund wording is a publisher-specific approved policy. Independent NCCIH overviews cover broad meditation and hypnosis research, not those two products. Evidence links are in the separate non-sending ledger. No partner acceptance, email permission, payout URL, price, refund or approved creative was verified.

### Read-only WordPress verification (2026-11-11 21:32 UTC)

Jetpack Newsletter ON; default new-post emails OFF; full post format; configured 52-page Fieldbook welcome; sender label Final Vestige Studios; reply-to no-reply. Diagnostic `total=3, confirmed=3, unconfirmed=2`. Separate follower breakdown `wpcom=3, email=0`. These are **not additive**; email-eligible audience is UNKNOWN. The five recent sends inspected are each `never_sent_opted_out`, which is not proof of zero lifetime emails. Gmail read-only search found an Oct 25 subscription confirmation request but no welcome message or Final Vestige-specific affiliate email authorization. No one was contacted. Native WordPress preview is documented, but not opened here. Neither welcome receipt nor a working unsubscribe / postal footer has been observed.

## Conversion-first prioritized plan — OWNER / evidence / gate

| Offer → step | Blocker | Proposed change or experiment | Required PASS evidence | Owner |
|---|---|---|---|---|
| Zen12 → eligible guide → verified purchase | Affiliate acceptance, email permission, earning link and live warm-up guide missing | Publish no commercial email until account approval and guide rights/terms are attested | Merchant-account evidence and verified approved destination, both in the same commercial message near clear commission disclosure | Mind & Commerce |
| Focus → confirmed lead | Arbitrary client-side UI state can look like success; actual email population unknown | Claude defines one provider-confirmed `confirmed_signup` and suppresses duplicates/opt-outs | Authenticated provider lifecycle, one logical confirmation per subscriber, no PII logged in analytics | Claude / Focus |
| Dispatch → inbox | Plaintext seller URLs leaked; legal footer and actual Jetpack rendering untested | Keep merchant links in reviewer ledger; use the native **Preview email** (not Send test email), then verify an actually received footer only after separate founder approval | Byte-identical approved email plus verified sender/postal and functioning opt-out for a consented recipient | Dispatch |
| Grok asset → qualified landing | Campaign IDs and qualified-human visit trail incomplete | Preserve `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=asset_id`; no extra tracking scripts | Verified asset IDs from Grok; existing analytics shows qualified sessions; 7/30-day cohort provenance | Grok / Praxxis / Claude |
| Order → realized net revenue | No independently settled orders or fees/returns | Reconcile paid conversion at merchant/Payhip source-of-truth, deduplicate orders and subtract applicable refunds/fees | Independently confirmed net receipts and verified denominator; otherwise metric **N/A**, never zero or click-estimated | Commerce |

**Privacy and compliance:** Do not extract or expose subscriber emails, create an independent list, or emit a confirmed lead from a successful-looking download panel. For commercial-email primary purpose, the FTC requires accurate sender details, a suitable postal address and a functioning opt-out; assume none from an offline HTML test. All six original issues remain HOLD_UNSENT and 03/05 additionally HOLD_MERCHANT. Founder's final approval is still required to send, schedule or publish. Homepage PR #49 remains untouched.

## Test commands and limitations

`node dispatch/r289/merchant-link-auditor.test.mjs` and `node dispatch/r289/merchant-link-auditor.mjs`. Static and synthetic checks cannot establish real client auto-link behavior, Jetpack sanitizer/rendering, inbox eligibility, affiliate approval or paid revenue. Pure function fixture checks were actually performed in isolated V8 during creation; Node runtime and actual received email not claimed unless separately executed.

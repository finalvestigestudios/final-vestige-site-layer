# Dispatch R204 — exact-source sprint evidence (2026-11-07 23:37– PT / 2026-11-08 UTC)

## Isolation and provenance
- Founder master six-issue campaign: PR #175 exactly `d57ccdba3aee8f065e143e101c2945f4f3d01647`; original 4 editorial + 2 commercial, 6/6 still HOLD_UNSENT. Prior independent gate PR #201 at `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`. Parent R203 PR #1544 at `ea3d27c49cd61f368f030b44aa0e3e77a6fe085d`.
- This R204 branch stacks ONLY on R203 and adds files ONLY under `dispatch/r204/`. No rework of #175/#201, no homepage #49, Mind, WordPress, Gmail writes, newsletter sends or subscriber modification.
- Original PR #175 independently read again; test and manifest and all 6 issues reconstructed in isolated local test directory and each of the **8 Git blob SHA-1 hashes matches** GitHub `fetch_file` content for exact PR #175 HEAD.
- **Native Python 3 test run on exact master content:** `python -I -m unittest discover -s /mnt/data/fv_dispatch_r204/master/tests -v` → 6/6 PASS.
- New `receipt_review.py` and `test_receipt_review.py` source were authored locally, tested natively (`python -I -m unittest discover -p 'test_*.py' -v` → **8/8 PASS**) and independently fetched from GitHub after commit, with the **same Git blob hashes as the native-tested local bytes**:
  - receipt_review.py: `bb8714e3ce7c9739ffc6c1f548eb02ef00f785dc`
  - test_receipt_review.py: `5b337e472003efd860ff1fef42ef58f3f2df26cc`.
- Additional exact-GitHub-source assertion run: **37/37 static checks PASS** across seven committed R204 files: six withheld native gates, privacy-safe MIME parser, synthetic test examples, two offer text/HTML reviewer variants, inline-styled email-only markup, adjacent commission disclosure, no active affiliate earning link, no unverified price, sources/placeholder legal footer, two provider subscriber paths, and seller refund caveat. An initial QA **assertion**, not repository code, failed due to imprecise search wording; corrected to actual documentary phrase and rerun 37/37 PASS. This is static V8 source testing, **NOT** hosted CI, actual email rendering, browser viewport proof, received-mail delivery, functional unsubscribe or a live paid-conversion test.

## Newly verified, as opposed to configured
- WordPress authenticated `wpcom_jetpack_newsletter` 2026-11-08T07:38:29Z: subscriptions ON, site_can_send true, no send blockers; automatic new-post send OFF; five previous posts all `never_sent_opted_out`, not campaign sends. Status counters total=3, confirmed=3, unconfirmed=2, suppressed=0, paid=0. Counters are NONADDITIVE and not a verified recipient list.
- WordPress settings 2026-11-08T07:38:30Z: `email_content_format=full`, `from_name=Final Vestige Studios`, `reply_to=no-reply`; welcome text configured with 52-page PDF. Neither delivered welcome nor a verified email-eligible aggregate is proven.
- Live WordPress pages `/dispatch/` (ID 523), `/focus/` (ID 1579), and Editorial Standards (ID 17) read by authenticated connector. Focus's client-side apparent success still is NOT provider-confirmed consent.
- Critical two-path correction from WordPress.com primary docs: email-only subscriptions receive confirmation before welcome; pre-authenticated WordPress.com users **skip email-confirmation-link step** and receive welcome directly. Count a `confirmed_signup` only after authoritative provider subscription state/transition, not mandatory link click for everyone or browser success. https://wordpress.com/support/newsletter-settings/
- Gmail bounded Inspire3-related email lookup found no qualifying named FV affiliate EMAIL-channel authorization. This **does not prove** lack of an approval in external merchant dashboard or another email account.
- Exact official Zen12 Premium sales features: 12 levels/48 MP3; hour-equivalence is unverified seller claim. https://zen12.com/hnp
- Exact Total Focus seller listing: 33-minute/47-MB audio and a displayed 14-day refund; **separate official FAQ restricts refunds to five sessions per year**. https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq
- FTC CAN-SPAM guide: commercial email identity, truthful subject, physical postal address, clear unsubscribe instructions, 10-business-day opt-out processing. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- WordPress preview docs: existing-post View > Email preview is a visual tool, **not received email verification**; no email/test was authorized/sent. https://wordpress.com/support/newsletter-email-design/

## New actionable package
1. **Offline real-MIME reviewer:** Python standard-library `.eml` inspector (redacted Boolean-only output; no send); 8 native synthetic tests and fixed fail-closed `ready_to_send=False`. Note a downloaded .eml itself does not prove provider delivery.
2. **Two-path subscriber state protocol:** WP.com member vs email-only; provider-filtered eligibility and private dedup, with privacy-safe aggregate event.
3. **Six-issue consent-to-customer progression:** no duplicate Fieldbook welcome, single provisional Zen12 offer, 4:2 unchanged, verified payouts only.
4. **Original conditional Issue 03 follow-up candidate:** story-led focus log, optional free observation exercise, vendor/NIH sources, **one inactive guide CTA + near-CTA disclosure**, HTML and plaintext; no extra seventh send and not approved substitution.
5. **Specific merchant source/objection ledger** and ready/not-ready checklist.

## Hard release verdict and next-owner plan
**ALL SIX: HOLD_UNSENT. #03/#05: HOLD_MERCHANT. Paid net revenue per 1,000 qualified-human sessions: NOT COMPUTABLE.**

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 → warmup guide → buyer | No FV named affiliate approval, express EMAIL rights, issued URL, approved LIVE Mind-owned guide | Obtain account-side acceptance + verified URL + product checkout/terms | Missing, HOLD | Mind #171 |
| Focus → confirmed subscriber | WP counter 3/3/2 nonadditive; browser success not consent | Confirm eligible provider filtered count and transitions incl WP.com account path | Provider counts read; private reconciliation missing | Claude / Focus #129 |
| Subscriber → Fieldbook welcome | Message configured but actual final receipt unknown | Read-only inspect properly authorized previously received final welcome | Missing, HOLD | Dispatch |
| Newsletter → compliant recipient | FV postal/unsub/render unknown | Authorized real received MIME, manual footer/opt-out validation, native preview | Offline code tested 8/8; genuine receipt missing | Dispatch/Site QA |
| Purchase → net per 1k qualified humans | Paid orders/payouts and human denominator unavailable | Independently reconcile 7/30-day actual transactions, refunds, fees and source assets | Not computable | Commerce / Praxxis #820 |

**Explicit founder final approval of actual creative, exact target audience and send times is separately required.** No publishing, sending, scheduling, test emails, toggles, merchant activation, pixel additions, list manipulation, pricing/promotions, spending or social posting occurred.
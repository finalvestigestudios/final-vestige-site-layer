# R333 exact-source and non-sending QA — November 13, 2026

## First-mile evidence: independently fetched and executed
- Read GitHub Issues #174/#171/#820 and latest #174 comments; checked PR #175 current HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`, #201 and upstream R332 #2360 before branch creation.
- Used the pre-existing locally mounted R332 archive of original #175 materials; ran *native Python* `python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v` on those exact source files: **6/6 PASSED**. Compared the eight original archive Git blob identities against *fresh* GitHub `fetch_file` SHA for manifest, test and all six original issues: **8/8 MATCHED**. The archive is local evidence, not a changed GitHub original.
- Read connected live WP newsletter `status` and `get_settings` at **2026-11-13 16:29 UTC**, `/dispatch/`, `/focus/`, and published `/editorial-standards/`; independent follower aggregate showed WordPress.com=3, direct-email=0, comments=0, nonpartial at 16:30 UTC.
- Targeted connected Gmail metadata searches found one earlier Oct 25 **subscription confirmation** but not a verified final 52-page Fieldbook *received* welcome or individual Inspire3 affiliate EMAIL authorization. Consumer campaigns/orders are not merchant account rights. No private messages or subscriber addresses reproduced.
- Read Grok/Praxxis Drive TASK-008 and handoff through native Drive connector; no task queue or Grok creative touched.
- Re-checked public official seller Zen12 paid checkout and free MP3 list disclosure, Inspire3 terms, Hypnosis Live exact Total Focus product, and public affiliate login/recruitment page. Seller's terms and website claims remain distinct from private affiliate account/creative rights. See ONE_OFFER_MERCHANT_CONTRACT.md.

## New source-control and test method
- R333 is **additive** on R332 exact `0861e61399f329226bcb5641f9faccf1681f7f15`. Canonical draft files, historical source data, published WordPress, homepage #49 and preceding QA all unchanged.
- New `non_sending_decision_audit.cjs` and `non_sending_decision_audit.test.cjs` fetched from the actual R333 branch and executed using a narrow isolated V8 CommonJS shim against the **exact fetched GitHub source/ledger and original manifest**: **39/39 PASS**. This included 20 constructed invalid states and eight permission-false-to-true attacks. Initial test harness had two portability errors (boolean predicate and structuredClone in isolate), corrected in two isolated commits and retested. The judge always returns `send_allowed=false` and `release_status=HOLD_UNSENT`.
- Original/current ID/source checked; warnings emitted for repeated 01/02 CTA, 06 repeated acquisition CTA, 04 undefined 14-second endpoint, 05 ambiguous brand-only product. It also refuses to derive recipient eligibility from 3/3/2 or 3 WordPress.com followers, and refuses to fabricate paid-revenue metrics.
- **Native Node on exact newly committed R333 source was NOT executed**. The source-level isolated V8 result is not a Node or hosted CI run.
- New reviewer is static, has semantic heading/list/article markup, text link affordances, viewport-relative grid and keyboard-focus CSS. **Actual browser/device, screen reader, WordPress sanitizer, inbox rendering and functional unsubscribe were NOT executed/tested**. The reviewer must not be presented as a verified inbox email.
- Links from this reviewer to R327/R325/R324/R326 are fully qualified commit-pinned GitHub file links, because those alternatives are **not** ancestors of R333's stacked branch. Ancestor R332/R331 and R328 previews are local repository links.
- FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; WordPress native preview: https://wordpress.com/support/newsletter/email-appearance/ ; current sender/subject: https://wordpress.com/support/newsletter/send-newsletter-emails/ .

## Release decision and ownership
- **ALL 6 ORIGINAL ISSUES HOLD_UNSENT. 03/05 additionally HOLD_MERCHANT. All optional candidates NOT_ADOPTED.** No final founder selection or final campaign approval exists.
- **Offer → funnel → blocker → change/experiment → pass/fail evidence → owner:**
  1. Zen12 Premium → vetted guide → settled order. **Blocker:** individual merchant EMAIL rights, issued earning link, approved live guide, checkout and disclosure not verified. **Change:** Mind/Commerce supplies redacted private permissions and guide release evidence. **FAIL/UNKNOWN**, Mind/Commerce.
  2. Existing Focus → confirmed Dispatch lead. **Blocker:** aggregate provider counts conflict, welcome delivery missing. **Change:** Claude/Focus reviews consent-scoped provider records privately without exports or new signups. **UNKNOWN**, Claude/Focus.
  3. Dispatch → native inbox. **Blocker:** sender postal address/functional opt-out/actual received preview missing. **Change:** separately founder-authorized non-sending native preview and later explicitly authorized received test. **FAIL/UNKNOWN**, Dispatch/Founder.
  4. Grok asset → qualified human session → independently paid order. **Blocker:** actual asset identifiers and settled source join absent. **Change:** Claude/Grok/Praxxis/Commerce first-party privacy-safe join; do not add scripts until authorized. **UNKNOWN**, respective owners.
  5. Paid orders → net realized revenue/1k qualified sessions. **Blocker:** authentic settled commissions, refunds, fees and qualified-human denominator unavailable. **Change:** Commerce source-of-truth verification. **NOT COMPUTABLE**, Commerce.

No actual email/test email, subscriber contact/import, paid service, WP settings/post changes, deployment, affiliate link activation, social posting, merge or expenses.

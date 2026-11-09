# R243 Authored Active Markup / Citation-Link Source Safety Gate

**Issue:** #136. **Commercial coordination:** #820 and charter #818. **STATE: BUILT / 87 ISOLATED PYTHON TESTS PASSED / DRAFT / HARD HOLD / NOT NATIVE-VALIDATED / NOT PUBLISHED.**

**Stack parent:** R242 draft PR #1762 exact HEAD 97f2c37bb76ece7718efea431a473cc4185a3ab0 (unmerged).

## Material safety improvement

Earlier R238/R239/R242 checks protect source-citation visibility, HTML tokenizer states, and encoded attribute grammar. These do not independently reject otherwise syntactically valid authored active HTML such as script tags, forms, event handlers, SVG animation, deceptive URLs and remote loading.

New R243 gate: preparedness/tools/r243_active_source_markup_custody_hold.py. It rejects executable or interactive authored elements/attributes, obfuscated scripting schemes (including character references and whitespace), protocol-relative/backslash destinations, remote resource URLs, unsafe blank-target links, duplicate browser-behavior attributes, and CSS resource imports. It keeps SVG static geometry and source-citation/link tokens usable. Every source check returns DRAFT_HARD_HOLD with FALSE release, QD, medical, merchant and source approvals.

R220 runs this separately authenticated SHA-1 Git-blob-pinned gate on the frozen 35 article bodies BEFORE the WordPress producer and rechecks the guard's SHA after the audit. No article, metadata, source row, canonical route, source crosswalk, safety state, six tools or render output changed.

## Actually performed / limitations

**Isolated Python 87/87 tests PASS, Python compilation PASS.** Test family includes 24 distinct active HTML tags, 16 event listeners, 20 URL scheme mutations, 15 browser-behavior attributes, CSS and new-tab controls, and immutable 35-source custody tests. Executed local Python bytes match the committed GitHub source/test blob identities.

Authenticated separate GitHub reading of all 35 original article bodies in batches 12+12+11 yielded exactly 2,000 citation occurrences. A separate JavaScript regex text screen found zero matching active form/script/frame tags, event handlers, raw URL-bearing attributes, and URL-based inline CSS candidates. This was NOT execution of the committed Python gate against the full original repository.

Local git ls-remote against the repository FAILED: Could not resolve host: github.com. Hence native Python validate.py, build.py, inherited tests, WordPress preview exports, qualified source-support/safety/QD and merchant acceptance remain NOT EXECUTED / UNVERIFIED.

Original Claude branch SHAs compared with frozen manifest, 7/7 unchanged:
start 2122d856fce9f64887c16df3d52e64be9f59a55b;
shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976;
food f911ff7a655de8d81535ea86ec3d65a49ee76648;
health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17;
hist-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c;
hist-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d;
hist-home 7504a5f099594d635e3dd7332a33a2e1346c43a2.

Independent QA #157 (HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa), synthetic-fixture PR #169 (HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5) and homepage lead #1689 (HEAD f55c36b6598eec558dd8bb24e4c8988becc51be0) checked; all unmerged, untouched. All 32 shared-source review groups and three disputed original citation occurrences (two CDC in #7, one Ready.gov in #20) remain unreviewed.

## One buyer-intent funnel (disabled, source/commerce held)

**Audience:** households organizing emergency contacts and essential family records. **Free public destination:** https://finalvestige.com/preparedness/ with existing official-source resources; the original detailed Article #1 is NOT verified live. Do NOT resurrect the retired water giveaway or gate safety information behind email.

**Provisional commercial candidate ONLY:** Legacy Triage, previously advertised as a $19 estate/incapacity/document-organizing PDF. Audience suitability for an emergency-preparedness visitor, full PDF/account-security/privacy advice, rights, merchant checkout/fulfillment/refunds and founder approval remain unverified. NOT an approved Preparedness offer. No paid link.

**Disabled free CTA draft:** “Build your household emergency contact plan with free, source-backed resources. No purchase or signup required.” Publication requires real Grok published asset ID, hook, platform destination/rights and mobile/UTM handoff via TASK-008.

| OFFER → STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Published Grok asset → free Archive | Authentic asset ID, rights, hook, destination/UTM absent | Reconcile **existing** creator post and mobile intent in TASK-008, no new post | UNVERIFIED | Grok / Praxxis |
| Free Archive → full evidence-led guide | Native build and expert claim/source safety signoff absent | Complete all original validation/build + 41 draft-route and depth checks | 87 synthetic tests PASS; native HARD HOLD | Preparedness / QA |
| Free guidance → Legacy Triage | Product/privacy/merchant rights and audience fit not cleared | Inspect whole PDF, owner permissions, privacy disclosures | NOT APPROVED; CTA disabled | Founder / Commerce |
| Paid optional pack → order/delivery | Checkout, fees/refunds, fulfillment untested | Authorized merchant payment and delivery test | NOT TESTED | Commerce / Founder |
| Human-qualified visits → realized net sales | Confirmed asset-attributed human sessions and settled orders absent | Measure sessions → CTA → verified lead → confirmed paid order → refunds/fees; 7/30d | Net revenue per 1,000 sessions NOT COMPUTABLE | Claude analytics / Commerce |

**No public CMS, WordPress, navigation, social posting, email, analytics script, affiliate/merchant activation, spending, merge or false QD PASS.**
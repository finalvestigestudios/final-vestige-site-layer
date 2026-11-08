# R121 Dispatch canonical editorial decision — NO SEND

2026-11-04. Owner #174; companion #171; subscriber #129; business #820. Parent draft PR #981 at a11f350e3e8c30c1a6910ab1be34f2811c259755. Master draft PR #175 at d57ccdba3aee8f065e143e101c2945f4f3d01647. Frozen homepage #49 untouched.



## Concrete findings

All SIX inherited newsletters have changed Git blobs relative to original master #175; the manifest also changed (the previous R120 audit pinned that fact). Neither is automatically the founder-approved send version. These exact issue-specific source pairs and proposed decisions appear in audit.json.



**Issue 1 (editorial):** Original subject: “The mind is not a camera”. Current stacked: “The mind is not a camera”. Finding: Simons/Levin 1998 DOI supported; do not generalize pedestrian detection rates to all eyewitnesses. Status: HOLD_UNSENT.

**Issue 2 (editorial):** Original subject: “Before hypnosis had a name”. Current stacked: “Before hypnosis had a name”. Finding: May 4, 1784 and Victor Race are precise: Wellcome catalogue establishes publication not incident. Verify dated primary/scholarly account. Status: HOLD_UNSENT.

**Issue 3 (commercial-review-pending):** Original subject: “The twelve-minute meditation question”. Current stacked: “The twelve-minute meditation question”. Finding: Zen12 free 1+9+2 routine useful; official package descriptions are seller features; email approval and live guide absent. Status: HOLD_UNSENT.

**Issue 4 (editorial):** Original subject: “Fourteen seconds. A much longer explanation.”. Current stacked: “Seventeen seconds. A much longer explanation.”. Finding: NASA: 17.1 seconds is elapsed first-to-last transmission interval; actual speech totals 10.3 seconds with 6.8 seconds of radio silence. Original 14 seconds unsupported. Status: HOLD_UNSENT.

**Issue 5 (commercial-review-pending):** Original subject: “Before you press play on a hypnosis audio”. Current stacked: “Before you press play on a hypnosis audio”. Finding: Total Focus seller lists 33-minute 47-MB audio; manuscript lacks direct official product-specific citation. No permitted email promotion or live guide. Status: HOLD_UNSENT.

**Issue 6 (editorial):** Original subject: “What did seven days of attention reveal?”. Current stacked: “What did seven days of attention reveal?”. Finding: Already-subscribed reader is directed to /focus/ signup landing; direct verified Fieldbook PDF should be tested instead. PDF receipt and page count unverified. Status: HOLD_UNSENT.



## Direct source evidence and recommended candidate edits

**Apollo 1:** NASA's primary Apollo 204 reconstruction gives transmissions 23:31:04.7–10.0 GMT and 23:31:16.8–21.8 GMT. First-to-last span is 17.1 seconds, the combined transmissions are 10.3 seconds, with 6.8 seconds of silence. Change the subject to “Apollo 1: the 17.1-second record, not the whole explanation” if founder approves revised copy; do not assert 17 seconds of continuous speech, full fire duration, or elapsed escape attempt. https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html

**Issue 06:** The source for 90% paper-reported vs 11% sensor-confirmed diary use is BMJ Stone et al. (2002), not proof of meditation effectiveness; maintain this critical context. https://www.bmj.com/content/324/7347/1193. Proposed destination for already-confirmed subscribers: the existing WordPress media PDF ID 1737, but only after confirming public retrieval, actual 52-page count and legitimate welcome receipt. Until then the existing /focus/ CTA remains a known possible re-enrollment loop, not a passing customer journey.

**Issue 05:** Product-specific merchant citation currently missing from the email text even though its 33min/47MB detail matches public product page: https://hypnosislive.com/mental-skills/total-focus. Add source as a non-affiliate reference if approved, not a checkout CTA. Price/refunds/affiliate email permissions must be reconfirmed before any live commercial email; these public sales-page details do not confer named Final Vestige partnership rights.

**Issue 02:** Wellcome's 1784 catalogue entry supports the work's publication, not independently the exact dated May 4 observation, its witness name, or reported amnesia. Attribute the scene and verify with a legible first-hand passage/scholarly source before freeze. https://wellcomecollection.org/works/es4ayp6q

**Issue 01:** Simons and Levin's 1998 field experiment supports the real-world change-blindness framing, but not a population-wide eyewitness-failure rate. https://doi.org/10.3758/BF03208840

**Issue 03:** Keep the valuable no-purchase meditation practice. Zen12 12-minute equivalence, brain-state claims and benefits are seller claims; no product-specific independent confirmation, Final Vestige affiliate approval, permission to email-promote, approved link or published first-party guide.



## Native WordPress & consent, independently read-only 20:32 UTC

Newsletter enabled; automatic new-post email OFF; excerpt mode; no-reply configured; five latest posts never emailed by choice. Authenticated status: total=3, confirmed=3, unconfirmed=2, imported_last_24h=1. These are NOT additive and neither the delta nor import counter proves unique qualified signup, consent origin, reachable email, delivered welcome or paid sale. Welcome is configured with a PDF URL, not verified delivered. WordPress media ID 1737 reports application/pdf and 599,946 bytes, NOT successful independent download or 52 inspected pages.

The /dispatch/ subscriber promise of alerts on publication conflicts with automatic-email OFF and lacks /focus/'s commercial context. R112 already proposes aligned copy; this PR makes no production changes.



## OFFER → STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER

Fieldbook → returning subscriber → /focus/ re-enrollment loop → propose direct PDF after read-only verification → FAIL: public PDF, actual welcome and 52 pages not verified → Dispatch/QA.

Zen12 → consideration → written affiliate acceptance and email permission absent → have Mind Studio verify approval, link, guide and current terms → HOLD_MERCHANT → Mind Studio.

Dispatch → inbox → excerpt rendering, postal and unsubscribe unknown → authorized native preview/actual received email and publisher address → FAIL: received proof absent → Dispatch/Founder.

Grok asset → legitimate subscriber/customer → no authoritative per-asset consent/order tie → source-tag existing URL and deduplicated confirmed event, merchant-settled order, fees/refunds → NOT COMPUTABLE for 7/30-day net revenue per 1,000 qualified-human sessions → Claude/Praxxis.



## Legal and change-control gates

FTC commercial email requires truthful headers/subjects, sender physical postal address, clear opt-out, and appropriate ad identification; Automattic/Inspire3 addresses are not FV publisher address: https://search.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business.

Select one source set in a dated founder editorial decision (or explicitly approve a mixed revision as new copy), pin immutable blobs, rerun native Python master suite on selected head, then inspect genuine Jetpack email preview. No test sends without separate explicit final approval. No newsletter platform, new list, extra scripts, commerce activation, payments, social changes, import, WordPress settings changes or subscriber contact.



## Verification boundaries

Independent connector-refetched comparison of 12 manuscript blobs (six original, six inherited) and manifest metadata; 6 exact revision subject/preheader matches, 4 editorial + 2 commercial, six nonidentical blob pairs, NASA window, #05 seller-source omission and #06 CTA route V8 assertions: passed. This is **source QA**, not CI, native WordPress rendering, actual email/Fieldbook receipt, sales confirmation or native execution of committed tests.

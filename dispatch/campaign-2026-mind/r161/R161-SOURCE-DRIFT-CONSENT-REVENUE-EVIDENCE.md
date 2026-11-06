# Dispatch R161 — consent-to-customer rehearsal, source-drift audit and commercial hard stops

**2026-11-06 04:30–05:xx Pacific / 12:32 UTC authenticated provider snapshot**  
**Owner:** Dispatch Campaign Studio / GitHub #174; Mind & Affiliate #171; Focus #129; business #820.  
**Disposition:** ALL 6 `HOLD_UNSENT`; issues 03 and 05 independently `HOLD_MERCHANT`. This is not a production release or email-send approval.

## 1. Verified source / prior PR inventory

- Canonical [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) still open/draft at exact HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`; `manifest.json`, `tests/test_campaign.py`, and all six newsletter manuscript Git blobs were read and reconstructed locally **byte-identically**. All eight original blobs were validated against GitHub's individually returned SHA-1s. On this exact reconstructed tree, **native Python 3.13** `python -I -m unittest discover -s tests -v` passed **6/6** on 2026-11-06. The README is separately inspected but not in the eight checked blobs.
- [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) still open/draft at `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`; existing per-edition gates / board / fallbacks were **not** recreated or overwritten.
- [PR #1247](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1247) still open/draft at `60814c39c995cfa9d7830bad62ecafcc59689769`. R161 branches from this exact immutable commit. This leaves frozen homepage PR #49 and all original newsletter files untouched.
- Source integrity of the **new** `journey_gate.cjs` and `test_journey_gate.cjs` can be checked with GitHub blob SHA `2b565441fd9f8bd0f361640fc15eb5bae54b918b` / `dabafbfb7a5af813144a2bd2efdc577376d1ac34`. These are byte-identical to the source used for a **native Node.js 22.16.0** `node --test test_journey_gate.cjs`: **7/7 test cases PASS**, including 28 missing-evidence mutation scenarios across fourteen gates. This is local native test evidence, not live WordPress QA or CI.

## 2. Current real WordPress facts and what they do NOT establish

Read-only authenticated WordPress Jetpack Newsletter calls at `2026-11-06T12:32:05Z` and `12:32:07Z`:

| Source | Provider-observed result | Release meaning |
| --- | --- | --- |
| Newsletter | `subscriptions=true`, `site_can_send=true`, `send_blockers=[]` | Technical capacity only; explicit send is NOT authorized. |
| Automatic email | `email_new_posts_by_default=false` | Off; editors can still elect per-post delivery, so don't publish campaign posts. |
| Format / reply / sender | `full`, `no-reply`, `Final Vestige Studios` | Configuration only; not real inbox rendering. |
| Count endpoint | `total=3 / confirmed=3 / unconfirmed=2` | Overlapping provider categories. NOT 5 recipients and not 3 verified reachable addresses. |
| Followers endpoint | `wpcom=3 / legacy email-only=0 / total=3`, no partial error | WP.com followers are not equivalent to email-enabled recipient statuses. |
| Welcome | Configured exact 52-page Focus Fieldbook media URL | Earlier provider media item #1737 has matching URL; neither send, receipt nor actual PDF retrieval is proven. |
| Recent five WordPress posts | Each `never_sent_opted_out` | No automatic campaigns to these posts. NOT global email-delivery verification. |

Authenticated `/dispatch/` (#523) and `/focus/` (#1579) content representations were read at current revisions: Jetpack subscription blocks appear in CMS data; no literal HTML email input or form in the returned serialized content. That alone does not prove a signed-out visitor cannot subscribe: the functional control may be rendered by client-side Jetpack. Live browser is separately **UNVERIFIED**, and the offline browser here reports `ERR_BLOCKED_BY_ADMINISTRATOR` for public page navigation. Respect site QA's R160 non-submitting real-browser probe; don't claim its execution.

A bounded Gmail search on Nov 6 found a **Oct 25** WordPress `Confirm your subscription` message, but no received `Welcome to The Dispatch` or Fieldbook message matching the limited queries and no named affiliate email authorization. Absence in bounded searches is not proof they cannot exist elsewhere. No subscriber identifiers or email addresses have been stored here. **No new email or test email was sent.**

## 3. Independent copy/conversion finding: page-specific price is not stable evidence

The Zen12 official [exact product page](https://zen12.com/?no-popup=1) describes 12 levels, four listening choices each and **48 MP3** in the Premium package. Public text inspected Nov 6 displays `$87` for Premium, while current Mind R167 issue notes a `$87.99` seller display. **Neither is a verified checkout total.** These discrepancies are the reason Issue 03 alternative deliberately contains no quoted price, percentage saved or limited-time claim.

The official [Hypnosis Live Total Focus page](https://hypnosislive.com/mental-skills/total-focus) describes 33 minutes and 47 MB. Public text displayed `$2` in one retrieved view, while a search-indexed representation showed `$17.95` and earlier internal observations recorded another promotional amount. These are divergent sales-page representations (possibly date, presentation, offer or cache differences), NOT proof of checkout price or an actual discount. Keep Issue 05 **separately blocked**. The merchant's 14-day guarantee is an advertisement, not independently verified refund fulfillment.

Both sellers make assertive claims about cognitive results or rapid equivalence. Do not adopt those outcomes as proven. The seller's own site is adequate evidence of **what it says is in the package**, not clinical proof of a benefit. Original sponsor creative/partner permission for this account remains UNKNOWN. The public [Inspire3 affiliate sign-up portal](https://affiliates.inspire3.com/) establishes only that a network exists and says affiliates receive a specialized link; it does not establish Final Vestige's account approval, approved exact earning URL or permitted use of an email list. Never infer rights from a public affiliate landing page.

**Specific canonical copy-conversion concerns from exact-source review:**

| Edition | Existing positioning | Highest-impact editorial concern / proposed disposition |
| --- | --- | --- |
| 01 | Mind is not a camera; Puységur CTA | Good identity bridge. No original-study bibliography in email; primary source on linked site must support detail. Keep draft. |
| 02 | History of early hypnosis; same Puységur CTA | Consecutive duplicate CTA destination. R155 proposed alternate Mesmerism file; not an approved substitution. |
| 03 | Generic Zen12 meditation question | No live guide, no approved earning link. R161 decision card gives exact seller format and a single disabled CTA, but is optional and NOT approved. |
| 04 | Apollo 1 `Fourteen seconds` subject | Precision requires primary NASA timestamp evidence; R154 Apollo alternative avoids unsupported specificity. Keep canonical draft unchanged. |
| 05 | Generic Hypnosis Live catalog | Should identify Total Focus exact product, enforce current terms and channel rights; R156 alternate exists. HOLD. |
| 06 | Free Fieldbook CTA after welcome supplied same Fieldbook | Redundant as a first-time lead. R155 Piri Reis editorial alternative offers a distinct published historical page; optional only. |

## 4. New R161 deliverables: one-offer, consent-first rehearsal

**Program:** `journey_gate.cjs` is a pure local evaluator with an allowlist of fourteen *boolean/null proof attestations*. It rejects unknown fields and email/phone-like PII. It does not request subscribers, fetch sites, call an email API, write logs or emit a `confirmed_signup` or a synthetic sale. All fourteen attestations default false/UNKNOWN; `null` never passes. Its decision tree prioritizes provider email eligibility + confirmed transition, then received welcome and Fieldbook retrieval, then native Jetpack rendering + Final Vestige postal address + unsubscribe, then named seller approval/email rights/earning link/live vetted guide/terms/disclosure, then founder final approval. **Even a synthetic all-true fixture returns `HOLD_UNSENT`** and no network action; a human-controlled release process is required.

**Editorial:** `issue03-conditional-decision-card.md`, `.html` and `.txt` are original optional, unsent Issue 03 reviewer materials. They explain exact Zen12 package contents, distinguish marketing promises from evidence, suggest using the free Fieldbook first, avoid time-limited offer pressure, and use ONE deliberately inactive vetted-guide CTA. The commercial disclosure is immediately adjacent to the placeholder. The HTML uses a table-based email-safe layout and inline styles, no script, font download, external image, active affiliate URL, tracking pixel or form. The mockup is **NOT** a genuine Jetpack inbox preview; the preview must not be mistaken for delivery readiness.

**Subscriber progression hypothesis:** A reader who explicitly elects confirmed newsletter delivery and actually receives the welcome may first receive useful historical/perception content (original issue 01/02) and, if personally interested in structured meditation audio, an optional offer review (commercial issue 03) **after** separate named partner email permission. No inference of purchase intent from a pageview or a checked signup box. Do not segment/target individual existing subscribers without a legitimate source and user consent. No new list; no auto-follow-up job has been scheduled or enabled.

**Measurement:** Reuse the existing R152/R159 creator-ID and allowed-route conventions. `confirmed_signup` is only a provider-verified newly confirmed transition with consent and deduplication, never a page query flag or follower count. Keep aggregated source-tagged `utm_source / utm_medium / utm_campaign / utm_content` separate from private subscriber data. Sales require independently reported paid orders or settled affiliate commissions, adjusted for fees/refunds; visits, clicks, signups and checkout starts are NOT sales. No revenue denominator is verified, so 7/30 day `realized net revenue per 1,000 qualified human sessions` is **NOT COMPUTABLE**; zero would be a false statement.

## 5. Conversion-first prioritization and release governance

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Grok → Focus → subscriber | Signed-out first-click and native recipient eligibility unknown | Existing R160 non-submitting browser probe and provider-native `Email subscription` reconciliation | **UNVERIFIED**; no fabricated signup | Claude / Site QA / Dispatch |
| Confirmed signup → free Fieldbook | Received welcome and actual PDF download unknown | Read-only authorized received-email and PDF retrieval verification | Media-record URL **MATCHED**, delivery **UNVERIFIED** | Dispatch / Site QA |
| Subscriber → newsletter | Real email preview, FV physical address, unsubscribe unknown | Native Jetpack non-sending preview; inspect real rendered footer and verified FV postal address | **HOLD**, FTC-required commercial-mail safeguards not attested | Dispatch / Claude |
| Issue 03 → Zen12 guide | No active approved live warm-up guide, affiliate acceptance, email-rights proof or link | Mind owner obtains explicit named merchant authorization, approved earning URL, guide release and current checkout terms | **HOLD_MERCHANT**, optional new specific letter & safe test gate BUILT/TESTED | Mind & Affiliate |
| Issue 05 → Total Focus guide | Separate named product and email-link rights, price mismatch | Independent offer clearance; no substitution for Zen12 evidence | **HOLD_MERCHANT** | Mind & Affiliate |
| Attributed buyer → net revenue | No independently verified orders, fees, refunds or qualified-human sessions | Owner-only aggregate transaction reconciliation | **NOT COMPUTABLE**, no fake sales | Commerce / Praxxis |

### FTC/legal release notes

FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful from/subject, clear advertising identity when commercial, valid publisher postal address, effective opt-out and prompt honoring of opt-outs. An address visible in a WordPress confirmation sent by Automattic or in Inspire3's seller footer is **not** evidence of Final Vestige's valid publisher address. Promotional email is not automatically exempt merely because the recipient subscribed to an editorial newsletter; classify by **primary purpose** of the actual message, including mixed editorial/sales content. Verify real Jetpack footer and consent before any message goes live.

**Release disposition:** `ALL HOLD_UNSENT`; `03+05 HOLD_MERCHANT`; new materials are draft reviewer assets only. No WordPress writes, audience exports/imports, emails, test sends, new analytics, live affiliate links, payments, social work, expenses, homepage PR #49 edits or production changes performed. This PR targets only `dispatch/campaign-2026-mind/r161/`, stacked on prior Dispatch R160, and changes nothing outside its own directory.

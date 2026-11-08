# Dispatch R15 — exact-SKU copy repair and release evidence (UNSENT)

**Review date:** 2026-10-31 (PT). **Owner:** Dispatch Campaign Studio. **Scope:** prospective Issue 05 only; the six-issue 4:2 allocation, source-led site identity and all publishing blocks remain unchanged. **Stacked on:** draft PR #267 @ `a37a1fe691f135e53282be99e4485f16b7ca3bfa`. **Master:** draft PR #175, Issue #174. **Product-guide owner:** Issue #171.

## Why this intervention was necessary

The previously proposed Issue 05 described the **entire Hypnosis Live catalog**, referred to the merchant's typical recording length and quoted a limited refund allowance from a generic FAQ. Such information is less useful to readers contemplating one specific purchase, and time-dependent policies are particularly vulnerable to becoming outdated during a six-week pilot. In contrast, the merchant's live **Total Focus** page describes a particular 33-minute, 47-MB downloadable hypnosis recording with an audio preview. This is a *seller product description*, not an independently measured benefit.

R15 makes a surgical editorial change to the *existing unsent manuscript*, rather than substituting the alternative Option B letter in PR #220 or the optional noncommercial fallback in PR #201. It changes the two affected explanation paragraphs and the near-CTA disclosure, retaining the original subject, preheader, three-question framework, historical Puységur bridge, NIH context, legal holds and incomplete guide token. **The master PR #175 and its original six-issue contents remain intact; R15 is a separate draft proposal.**

### Evidence-to-copy mapping

| Assertion | Evidence / interpretation | Permitted copy |
|---|---|---|
| Total Focus recording length | Seller's SKU page displays 33 minutes. | "Seller lists 33 minutes"; not independent usage testing. |
| Total Focus download size | Same seller page displays 47 MB. | "Seller lists 47 MB"; access/file behavior needs purchase verification. |
| Audio preview | Same seller page presents "Total Focus Preview". | "Seller page has an audio preview"; no claim it was listened to or evaluated. |
| Improved concentration | Seller's page promises focus benefits and talks about neurological "reprogramming". | **Not independently verified for Total Focus**; do not imply a clinically proven result. |
| Evidence for hypnosis generally | NIH NCCIH overview surveys specific applications and notes evidence limitations. | Context only; **not** evidence for this focus product. |
| Price, discount and refund | Seller pages currently advertise prices and refund terms; these can change. | Omit all fixed numbers. Check actual checkout and policy shortly before any approved promotion. |
| Commission opportunity | Public Inspire3 affiliates page describes a network. | Not proof Final Vestige is approved, owns a tracking link, or has email permission. |
| Reader's alternative | Existing Focus Fieldbook landing page is published. | Offer free workbook without buying anything; never suggest an unverified effect. |

**Source links checked on 2026-10-31:**
- Seller SKU: https://hypnosislive.com/mental-skills/total-focus
- NIH independent overview: https://www.nccih.nih.gov/health/hypnosis
- Seller's network recruitment page: https://affiliates.inspire3.com/
- Existing public free resource: https://finalvestige.com/focus/
- FTC commercial-email guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsement/affiliate disclosure guidance: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking

**Sales resources are not independently approved affiliate creative.** No logged-in publisher affiliate account was accessed, no account-specific product eligibility or e-mail permission was established, and no vendor pricing/refund/efficacy claim is authorized for recipients. The direct seller URL above lives only in this internal evidence record, **not** as a clickable recipient-facing merchant CTA.

## Copy/conversion review

- **Hook and fit:** The existing opening connects the temptation of convenient audio with the historical distinction between a report and evidence; it is valuable for an evidence-first readership. Preserve it.
- **Objection reduction without hype:** Three questions (what is included, what is the claim, what if it is unsuitable) build credibility before introducing a commercial product.
- **Stronger SKU specificity:** A 33-minute/47-MB statement tells the reader what is purportedly being sold; the old >200-item catalog description did not.
- **Scientific limits:** Copy explicitly separates seller promises from studies of hypnosis in other contexts. No unsupported "brain reprogramming" or guaranteed focus claim is endorsed.
- **Commercial transparency:** Disclosure precedes the pending *independent guide* CTA; the guide URL remains a literal blocking token.
- **Value without buying:** The free seven-day Focus Fieldbook remains available; no purchase pressure, deadline, unverified testimonial or invented performance stat.
- **No direct affiliate link:** Neither a publisher earning link nor a direct checkout/seller link is present in the recipient copy.
- **Editorial continuity:** The adjacent Apollo 1 editorial and Puységur source issues are unchanged. Original six subjects and preheaders remain as in the R14 branch.

## Operational evidence and hard stops

**Authenticated WordPress snapshot:** 2026-10-31 08:29 UTC. Newsletter subscriptions enabled; automatic new-post mail disabled; email_content_format `excerpt`; sender display Final Vestige; no recent sends; configured welcome message includes 52-page Focus Fieldbook. Subscriber counters return **total=2, confirmed=2, unconfirmed=2**; this is not reliable evidence of 4 distinct users or of 2 fully eligible delivered subscribers. Do not display subscriber email addresses. No site or list writes were made.

The published `/dispatch/` and `/focus/` pages have Jetpack subscription blocks in authenticated Gutenberg source. Server-side content alone cannot establish logged-out browser behavior. R14 live browser probe was blocked by this execution environment; **signup success remains UNKNOWN**, not broken. The existing WordPress configuration is **excerpt delivery**, so the standalone preview HTML is not a genuine Jetpack MIME rendition, and a separate campaign preheader is not verified as a native Jetpack field.

**GitHub Actions red evidence:** R14 PR #267 exact-head run #41181746427 reports `local-content-safety` **failure**. The connected GitHub log endpoint returned a BlobNotFound 404 and job step summaries are empty; root cause **unclassified**. The actual workflow comprises Python 3.11 `unittest discover`, Node 20 `node --check`, and exact-source `build_previews.cjs --check`. Source-level campaign assertions were independently checked against six current GitHub documents; the exact JS preview builder was executed in an in-memory V8/virtual-FS harness against the 13 current R14 preview assets, which all matched. **This does not prove that actual hosted Python, Node or runner startup succeeded.** Do not modify the shared Actions workflow speculatively.

**As of this PR, NO release attestations:**
1. Founder approval of final creative/audience/date — NOT GRANTED.
2. Account-specific Inspire3 acceptance, email promotion permission, permitted links and product eligibility — NOT VERIFIED.
3. Published, reviewed Total Focus warm-up guide — NOT LIVE / NOT VERIFIED (Mind & Affiliate Studio owns).
4. Distinct eligible subscribers and consent history — NOT RECONCILED.
5. Final Vestige's own legally valid postal mailing address — NOT ATTESTED. A vendor/Automattic address is insufficient.
6. Actual Jetpack-recipient unsubscribe, sender and excerpt/full rendition — NOT VERIFIED; no real test email authorized.
7. Accurate live referral conversions, revenue or A/B outcomes — NO DATA; no invented statistics.
8. GitHub Actions release-path CI — RED/UNCLASSIFIED.

**Release verdict:** Every Dispatch issue remains `HOLD_UNSENT`; commercial Issues 03 and 05 additionally remain `HOLD_MERCHANT`. No sends, imports, subscriber contact, WordPress writes, public posts, campaigns, or merchant-link activation are authorized. Homepage PR #49 remains untouched. Do not merge this draft as permission to send.

## Reproduction commands when a full current PR checkout is available

```sh
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
node --check dispatch/campaign-2026-mind/tools/build_previews.cjs
node dispatch/campaign-2026-mind/tools/build_previews.cjs --check
```

In particular, the last command must find **all 13 pre-generated previews identical** to the generator output, or the PR must remain red. The Python suite now includes `test_r15_total_focus_copy.py` with nine extra fail-closed checks. Do not mislabel local JavaScript simulations as an executed Python checkout or as successful hosted CI.

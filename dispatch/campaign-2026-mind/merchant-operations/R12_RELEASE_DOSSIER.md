# Dispatch R12 — merchant-rights and native-delivery evidence dossier

**Status: DRAFT ONLY / HOLD_UNSENT.** 30 October 2026, 22:32 PT (31 October 05:32 UTC). This is an independently scoped operational review, **not** a sending authorization, approval of alternate copy, a live-site request, or advice to import or contact subscribers.

**Upstream custody:** original campaign [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) @ `d57ccdba3aee8f065e143e101c2945f4f3d01647`; per-edition gate [draft PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) @ `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`; immediate stacked parent [draft PR #247](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/247) @ `35330eb6c55af3625917a4f274b993baa9205793`. Master [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind product owner [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Frozen homepage PR #49 remains out of scope.

## 1. What we actually know, and the limit of that evidence

Authenticated WordPress.com read-only checks on 2026-10-31 at 05:32 UTC, site ID 256784396:
- Jetpack Newsletter: **enabled**; `site_can_send=true`; `email_new_posts_by_default=false`; **no recent sends**; sender display label **Final Vestige**, Reply-To **no-reply**.
- `email_content_format=excerpt` — **the drafted full emails and standalone HTML previews do not demonstrate the contents of a native subscriber email**. Without a custom excerpt the platform typically shows a short excerpt plus a read-more link. Custom excerpts in other draft PRs are **proposed, not applied**. A drafted preheader is **not proof of a native Jetpack preheader field**.
- Welcome message is **configured** with the 52-page Seven Day Focus Fieldbook and its existing PDF URL; an actual welcome **delivery has not been proven**. A 2026-10-25 Gmail subscription **confirmation** is neither a final welcome nor an issue-specific newsletter. Do not infer subscriber consent, receipt, or legal footer from it.
- Reported subscriber aggregates: total=2, confirmed=2, unconfirmed=2, suppressed=0, imported_last_24h=0. The subsets conflict; `confirmed + unconfirmed` must not be treated as four distinct recipients. **Deliverable unique permissioned audience = unknown.** No subscriber PII is collected in this branch.
- Live /dispatch/ (ID 523), /focus/ (ID 1579), /editorial-standards/ (ID 17), and /affiliate-disclosure/ (ID 14) inspected read-only. They preserve an evidence-oriented newsletter and single existing Jetpack signup. Existing public historical bridge: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ .
- **Not proven:** WordPress editor-native preview, actual received campaign MIME, Jetpack unsubscribe destination/function, Final Vestige's *own valid business mailing address*, legal/opt-in deliverable audience, distinct site-wide marketing classification, product affiliate eligibility, or founder's final approval.
- **Do not substitute** the Automattic address in WordPress's confirmation email or a seller's postal address for the legal sender's verified address.

## 2. Underlying creative review — the six originals remain unchanged

| Edition | Function / source fit | Hard-nosed copy / conversion review | Release |
|---|---|---|---|
| 01 · The mind is not a camera | Historical source-led introduction to perception, CTA to live Puységur archive | Strong evidence-first bridge, but the title alone could suggest a general cognition explainer: avoid implying an experimentally demonstrated memory distortion from an eighteenth-century record. Keep exact sources visible. | HOLD |
| 02 · Before hypnosis had a name | Historical witness accounts; Puységur primary-source trail | Distinguish retrospective vocabulary from the language of the 1780s. Remove any easy leap from observer testimony to efficacy. Avoid the implicit narrative that modern commercial hypnosis validates historical accounts. | HOLD |
| 03 · The twelve-minute meditation question | Practical free exercise + **Zen12 only as an optional seller-under-review** | The twelve-minute *time fit* is the usable promise; no claim of one-hour equivalence, superior brainwave effects, clinically proven outcomes, testimonials, or personal trials. First-party guide URL is deliberately non-live, even if generic source URLs work. Near-guide commission disclosure is properly framed but requires actual eligible relationship. Optional SKU-specific alternative in PR #220 is *not* founder-approved substitution. | HOLD + MERCHANT |
| 04 · Seventeen seconds. A much longer explanation. | Apollo 1 investigation; historical trust anchor | A strong antidote to promo-heavy mix. NASA's complex causal record is more useful than a simplistic ignition explanation; verify original live article and primary report references. The short timeline is an anchor, not the accident's whole cause. | HOLD |
| 05 · Before you press play on a hypnosis audio | Evaluation checklist + Hypnosis Live candidate | Greatest conversion mismatch in the original set: the email describes a broad catalog while the practical candidate guide is **Total Focus**, one SKU. If founder later approves, prefer a **33-minute / 47 MB seller-described recording** comparison over 200+ titles; the 14-day/five-session FAQ terms and promotional prices can change, so avoid specific refund guarantees in production excerpt. Don't silently replace original issue or assume the recording changes behavior. | HOLD + MERCHANT |
| 06 · What did seven days of attention reveal? | Evidence log, live /focus/ page and free 52-page Fieldbook | Good closing payoff for free readers. Subject's past tense could imply we observed actual participants' seven-day results; retain explicit “you can run your own log” phrasing rather than reporting invented outcomes. No product requirement. | HOLD |

**Conversion position:** 4/6 editorial and 2/6 optional commercial is a good *editorial ratio*, not an FTC legal exemption. Even principally informative mail promoting a commercial website/product may be covered depending on its primary purpose. Conservatively verify true sender identity, physical address and unsubscribe functionality **for each send**, regardless of the internal type field. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## 3. Merchant substantiation crosswalk — verified format is not verified effect

**Zen12, issue 03**
- Exact source of seller descriptions: https://zen12.com/about . Advertises twelve-minute sessions, twelve progressive levels, and four styles (guided, music, nature, white noise). These are **seller-listed features**, not first-hand product testing. Compare what a user will actually receive, whether the downloadable files are accessible and compatible, and whether a free routine could meet the same immediate need.
- **Do not repeat as established fact** “twelve minutes equals one hour of meditation,” automatic brainwave induction as an achieved outcome, or exceptional concentration/mental health benefits. Meditation's general research cannot establish a result for this specific commercial audio: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .
- **Obstacle:** account-specific approval, permitted email channel, SKU eligibility, authorized attribution link, first-party public Zen12 evaluation and merchant creative/term permission are **all missing**. The official public recruiting site does not approve this individual account: https://affiliates.inspire3.com/ .

**Hypnosis Live · Total Focus, issue 05**
- Exact SKU: https://hypnosislive.com/mental-skills/total-focus . Seller lists 33-minute audio, 47 MB. Do **not** conflate the Total Focus runtime with the general FAQ statement that *most* sessions run around 40 minutes.
- Seller FAQ: https://hypnosislive.com/faq . Prior source review found 14-day refund requests and a per-year quantity restriction, but these are **changeable terms**; do not offer a current money-back guarantee or certainty without contemporaneous confirmation.
- Official-page snapshots have varied across reviews: a prior observation listed $17.95/$22.95, whereas the page fetched on October 30 currently shows $2/$29.95. The current display is not a guaranteed future or checkout price. Therefore any number in a campaign likely to be sent later is stale. The safe copy **does not state price, discount, countdown, guarantee or urgency**. Efficacy claims about guaranteed sharper focus are vendor claims; a general NCCIH hypnosis overview https://www.nccih.nih.gov/health/hypnosis is not SKU-specific proof.
- A **specific** independent Total Focus guide would set an appropriate expectation, explain what is included, distinguish seller assertions from demonstrated effects, note contraindications and other options without prescribing medical treatment, and disclose a verified earning relationship adjacent to its eventual link. No live guide or tracked merchant URL currently exists.
- **Obstacle:** same rights/guide/approval blockers as Zen12. General “Hypnosis Live” affiliate approval, if ever shown, might still be insufficient without SKU and email-marketing scope.

## 4. Native WordPress evidence procedure — strict no-send boundary

**Stage A: read-only diagnostics (authorized now).** Capture newsletter settings and count aggregates. Note as-of UTC. Do not collect subscribers' emails, raw subscriber table or private unsubscribe tokens. A configured welcome is not a received welcome.

**Stage B: authenticated editor-native preview (not yet completed).** Only in a non-published, no-send workflow and after founder's separate go-ahead to inspect the native editor UI: ensure actual post identity, preview rendering, title, real effective excerpt, any Read More destination, footer, disclosure visibility, link target, sender, mobile legibility and no accidental “send to subscribers” checkbox. A locally generated HTML file, browser simulation or Node/Python source gate **cannot satisfy** this step. Merely opening a post editor must never trigger publishing.

**Stage C: received-message proof (requires separately explicit authorization).** Obtain founder-designated test recipient and specific test-message permission. Never use the existing list as the test population. Inspect the received raw MIME with the existing audit script in PR #214/#233; check visible legal footer, live opt-out path and sender address, multipart integrity, links, excerpt, media and privacy. A draft Gmail confirmation email does not count.

**Stage D: count/consent reconciliation (private admin only).** On the native WordPress subscriber admin screen, distinguish filters/timestamps/confirmation statuses; capture *only aggregates* and explain count semantics. Determine unique confirmed, eligible-to-email recipients from permission records without uploading or exposing addresses. If filters cannot be reconciled, continue to mark UNKNOWN and HOLD. **Never add, import or remove subscribers to make counts look consistent.**

**Stage E: explicit release record (not created here).** After permissions, actual guides, sender address, opt-out, native rendering, audience, and final-copy approvals are proven, founder must separately approve **exact edition copy + audience + dates + sending**. No current evidence can satisfy Stage E.

## 5. Honest native-excerpt and subject standards

- **Never promise** a separate branded preheader in actual native Jetpack output without verifying that the feature exists and renders. Draft preheader text in the manifest is an editorial plan only.
- Excerpts must carry an actual reader benefit and one reliable destination; on #03/#05 the disclosure must be visible **inside what is truly emailed**, not merely in a long website post that the email truncates.
- Exact price, discount, refund expiry, seller outcome, or time-limited scarcity should **not** appear in evergreen subjects or preview text. Do not quote “expert recommended,” “miracle,” “scientifically proven,” or simulated results.
- Use original concise writing; avoid manufacturing tension with exaggerated shock/hidden secrets, especially for sensitive hypnosis claims.
- One primary CTA per email. Research citations can be secondary hyperlinks; distinguish an actual live source/archive link from a still-unpublished warm-up route.
- Plain text and table-based HTML previews remain review assets, **not actual Jetpack MIME**.
- For 2–4 known site subscribers (and the number currently unresolved), **no valid A/B significance claims**. Record no open rates, click counts, unique users, sales or conversion absent provider evidence. Click ≠ purchase.
- If a merchant refuses email promotion, remove *that* offer placement **only with founder editorial approval**; the two PR #201 no-offer alternate letters remain unapproved alternatives. Do not covertly replace them.

## 6. Release blocking matrix and owner

| Evidence | Owner / safe verification | Actual |
|---|---|---|
| Final Vestige physical postal address | Founder/operations confirms real valid business mailing/PO box/registered private mailbox for compliance | **UNKNOWN** |
| Unsubscribe actually rendered and functional | Founder-approved native received test, inspected securely; no raw tokens in issues | **NOT VERIFIED** |
| Native Jetpack preview, correct excerpt/subject/preheader/footer | WordPress editor operator, non-published/no-send | **NOT VERIFIED** |
| Received campaign MIME | Founder-authorized explicit recipient + test-send | **NOT RECEIVED / NOT AUTHORIZED** |
| Recipient semantics and consent | Private WordPress subscriber admin review | **CONFLICT: total2/confirmed2/unconfirmed2** |
| Site welcome delivery | Authorized received welcome only | **CONFIGURED, NOT PROVEN** |
| Zen12 account/SKU/email channel rights | Private Inspire3 partner account/terms or written manager confirmation | **UNVERIFIED** |
| Total Focus account/SKU/email channel rights | Same, independently per SKU | **UNVERIFIED** |
| Published / accessible first-party offer guides | Mind & Affiliate Studio Issue #171; direct public route check | **BOTH NOT LIVE** |
| Founder final subject/copy/recipient/date/send approval | Separate explicit decision *after* evidence review | **NOT GRANTED** |

**Every issue stays HOLD_UNSENT.** No new platform, spend, list, imported subscribers, sending, tests to recipients, WordPress changes, merchant contact, tracked links or published pages. The homepage is first priority, without changes to frozen PR #49.

### Direct sources and custody

- Live Editorial Standards: https://finalvestige.com/editorial-standards/
- Live Affiliate Disclosure: https://finalvestige.com/affiliate-disclosure/
- WordPress newsletter settings/excerpt: https://wordpress.com/support/newsletter-settings/
- WordPress email preview guidance: https://wordpress.com/support/newsletter/email-appearance/
- FTC CAN-SPAM primary-purpose and compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsement disclosures: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- NIH meditation: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety
- NIH hypnosis: https://www.nccih.nih.gov/health/hypnosis
- Inspire3 affiliate recruitment: https://affiliates.inspire3.com/
- Zen12 format source: https://zen12.com/about
- Total Focus exact SKU: https://hypnosislive.com/mental-skills/total-focus
- Hypnosis Live FAQ: https://hypnosislive.com/faq

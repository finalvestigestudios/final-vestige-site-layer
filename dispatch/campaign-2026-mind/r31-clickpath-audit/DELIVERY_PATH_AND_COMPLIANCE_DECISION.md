# Dispatch R31 — Real Click-Path, Native Rendering and Commercial Release Decision
**Status: INTERNAL, UNSENT.** Owner: Issue #174; companion merchant/pre-sell work Issue #171. Base: draft PR #370, SHA `27b0c79205544d39e0b58d86864b6fd1b6593b75`. Homepage and frozen PR #49 excluded.

## Newly prioritized finding: the optional excerpt is not the primary manuscript CTA
The six optional custom excerpts have accurate short-form claims (PR #370), but they do not contain hyperlinks to the investigation pages or approved guide pages. Under WordPress's own model, the *Read-more* link appended to an excerpt opens **the full WordPress post**. It does not inherit `manifest.issues[].editorial_cta` as its destination. That is a **two-hop reader route**: inbox → campaign post → actual historical dossier/free Fieldbook or vetted product guide. Without the published full post containing an explicitly linked CTA, the apparent invitation "Read The Missing Caption" is plain text, not the destination of Jetpack's automatic link. There is currently **no published newsletter post and no verified route 1** for any of the six editions. A static local HTML preview cannot establish a working link or click attribution.

Editorial consequence: **do not claim a one-click path to The Missing Caption, the Apollo investigation, the Puységur file or the Focus Fieldbook when using the optional excerpt mode.** If that extra click is unacceptable, choose the per-post full-content editor override when available and prove the exact result with a received-email test after founder authorization. The per-post override is documented on Jetpack, but is **not yet verified on our actual editor**. Do not change the sitewide default as part of this review. A *More* block can shorten content; it is not an independently proven way to force a full newsletter under a global excerpt setting.

## Six-edition resolution matrix
| Edition | Role | Manifest destination | Missing proof |
|---|---|---|---|
| 01 — Mind is not a camera | Editorial | /the-missing-caption/ | Newsletter post exists with real internal CTA |
| 02 — Before hypnosis | Editorial | /free-resources/puysegurs-animal-magnetism-files/ | Same; source list preserved |
| 03 — Zen12 | Conditional affiliate | `[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]` | Approved published guide **and** written account/EMAIL promotion permission/link eligibility |
| 04 — Apollo 1 | Editorial | /2026/08/20/the-hatch-opened-inward-apollo-1/ | Same; first report ≠ ignition |
| 05 — Total Focus | Conditional affiliate | `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]` | Approved published guide **and** written account/EMAIL promotion permission/link eligibility |
| 06 — Fieldbook | Editorial | /focus/ | Same; Fieldbook receipt separately unproven |

No direct affiliate link is added to any email. The Mind & Affiliate Studio owns both guide publication, current merchant pricing/refund/creative review and final earning links. Four editorial, two commercial are reserved, not activated.

## Actual system snapshot — authenticated WordPress 2026-11-01T00:34Z
Newsletter enabled; `site_can_send=true`; new-post default auto-email **OFF**; email content global default `excerpt`; `reply_to=no-reply`; display name "Final Vestige"; recent sends []; configured Focus Fieldbook 52-page welcome. Subscriber counters: total=2, confirmed=2, unconfirmed=2. **These categories are non-additive**; they are not proof of four people, of deliverability, or of eligibility for a specific campaign. The October 25 confirmation email found in connected Gmail is not the final welcome; a further read-only Gmail search through October 31 found **no received welcome message or proof of an affiliate account acceptance**. No subscriber email addresses were used or exposed.

## Source-of-truth merchant alignment, not permission
- **Zen12** official sales page and About page are the source for tier descriptions (Beginner six levels/24 MP3, Premium twelve/48, Advanced final six/24; four formats as seller describes). Seller equivalence/effectiveness promises are **not independently established** for the marketed product. Product price, refund and eligibility must be rechecked on live checkout. Sources: https://zen12.com/ , https://zen12.com/about .
- **Hypnosis Live Total Focus** advertises an MP3 recording of **33 minutes, 47 MB** with a preview; "reprogramming" and dramatic focus gains are *seller claims*. Do not treat a general NIH hypnosis article as Total Focus efficacy proof. Source: https://hypnosislive.com/mental-skills/total-focus .
- **Do not borrow rights from another offer**. Inspire3's public Limitless Labs page advertises downloadable affiliate swipe copy suitable for mailing **for that offer**, yet also requires a specific approval request. That says nothing authoritative about Final Vestige's ability to use the Zen12 or Total Focus programs, merchant creatives, tracking URLs or email channel. Source: https://inspire3.com/ll/ .
- No applicant account-specific acceptance, verified tracking link, product email right, or proof of current checkout terms is on file. The drafts use seller **descriptions**, not endorsements.

## FTC and production-native evidence required
Every edition remains HOLD. **No legal classification shortcut:** editorial mail with a qualifying commercial primary purpose may be regulated. For commercial messages, require clear and truthful sender/subject, conspicuous advertisement/affiliate relationship disclosure, a **valid physical postal address belonging to the responsible Final Vestige sender** (NOT the Automattic/WordPress.com address and NOT Inspire3's listed business address), a working and clear opt-out, and timely honoring of requests. FTC guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . General affiliate-disclosure page alone does not replace proximity beside the earning link.

The site currently allows `Preview email` only while a post's **Send this post to subscribers** switch is on. That switch must not be left armed during publishing. The editor's screenshot preview is useful **but does not prove an actual message**. Test-send and recipient selection require separate founder authorization; none granted. The exact original received `.eml`, if later authorized, must be checked with existing PR #312 MIME evidence tool. Do not reimplement the already-available MIME or overall release-gate system.

**Hard-stop sequence**: (1) founder approves a safe native-preview and later separate test-send scope; (2) WordPress internal draft/manual editor state reviewed with send OFF when not previewing; (3) native device visual preview plus separately authorized received inbox sample; (4) verify preheader, actual Read-more and internal CTA route, postal/unsubscribe, sender identity, no draft warnings; (5) independent merchant and guide approvals for #03/#05; (6) founder finally approves exact six issue creative, audience and dates. Until then, no post publication, test, send, subscriber contact, changes to WordPress or new list.

## What is measured honestly
With two reported confirmed subscriptions, do **not** run statistical A/B tests or report uplift. Future attribution should distinguish WordPress-delivered email (only when actual Stats show delivery), observed visits to the published campaign post (not inferred from opens), clicks from that post to guide (where observable), merchant-outbound clicks (if permitted), and merchant-confirmed sales **only with authoritative reporting**. Jetpack's automatic Read-more is its own first-hop CTA and must not be conflated with the site's final editorial or affiliate CTA. No live event-tag, tracking pixels or UTMs were implemented here.

## Evidence and limitations
- Independent source read: master Issue #174, companion #171, exact current PR #370 files and six canonical manuscripts; review current Mind PR #374 source before any guide activation.
- Official WordPress email appearance: https://wordpress.com/support/newsletter/email-appearance/ (reviewed Oct 6, 2026); Jetpack newsletter customization: https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ (as retrieved Oct 31, 2026).
- Native WordPress 2026-11-01 00:34Z read-only evidence: `excerpt`, auto-email off, welcome configured but not received, zero sends. No real inbox, no subscriber list export, no affiliate account check possible from public evidence.
- This audit records *expected* excerpt route only; exact editor and received-email behavior unverified. **Do not merge as launch-ready.**

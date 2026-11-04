# R126 Preparedness reader-to-revenue handoff — DRAFT / HOLD

**Scope:** Issue #136 Preparedness safety/source gates, cross-reference business #818 and attribution #820. **Never publish, merge, send, spend, add analytics, change WordPress/CMS/navigation, or turn on a merchant link under this document.** No QD PASS or qualified emergency safety claim. Reviewed-on date for any underlying emergency advice is not established by this engineering work.

## Candidate audience and authentic existing free destination

**High-intent hypothesis, not observed Grok traffic:** households who need a written contact / meeting / family reunification plan, especially a school pickup backup and one out-of-area contact. Existing authentic internal article: **A household emergency plan that actually gets practiced** (`household-emergency-plan`). It remains a draft in candidate PR #584 and **cannot be advertised as live or safety approved**. Candidate route to validate at release: `/preparedness/start-here/household-emergency-plan/`. Keep all essential emergency planning steps free and ungated, and require qualified safety/citation review before making this page public.

**Draft-only on-site module, not HTML for production:**

> Make a one-page contact and meeting plan your household can actually find. **Read the free Household Emergency Plan** — source-linked guidance, review pending. 

The last phrase above is an internal caution; the public-facing wording must be edited after qualified review and approval. **Do not advertise the guide or claim its advice is safe until then.**

**Optional practical pack (CONDITION NOT MET):** no owned, rights-cleared, currently purchasable, audience-fit FV Preparedness SKU has been authenticated through seller records. **Render no paid CTA, price, fake checkout, waitlist, urgency claim, affiliate link, or conversion promise.** If such a product is eventually verified and separately approved, candidate secondary language for further review: “Want a printable companion? See what’s included in the optional planning pack.” Maintain complete free guidance and separate any commercial disclosure from source/safety citations.

## Evidence-based review prioritization

The R126 author-use inventory maps 35 draft article metadata files to 32 pending shared-URL source groups through **94 author-specific `source_use` bindings**. These are *declared citation-explanation scopes*, not visible body citation counts. Use the three immutable parts in `preparedness/docs/r126/` for exact Git blobs and original language. Top candidate review exposure by count of distinct articles declaring a source-use:

| Shared source URL | Articles declaring scoped use |
|---|---:|
| https://www.ready.gov/people-disabilities | 10 |
| https://www.ready.gov/plan | 6 |
| https://www.ready.gov/evacuation | 5 |
| https://www.ready.gov/kit | 5 |
| https://www.cdc.gov/natural-disasters/response/what-to-do-protect-yourself-during-a-power-outage.html | 5 |
| https://www.ready.gov/power-outages | 5 |
| https://www.loc.gov/resource/gdcmassbookdig.prairietravelerh01marc/?st=list | 5 |

Every one of the 32 groups remains **pending human review**. High usage counts are a *review queue ordering aid*, not a source-quality grade or proof of claim safety. Existing metadata state census: **29 pending; two historical "approved" states (NOT independently accepted); four not-required.** Nothing upgraded.

## Funnel and release acceptance contract

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One current FV-owned Preparedness pack only | Product → paid checkout → download | No authenticated current SKU, owned rights, payment terms, usable deliverable or refunds | Growth supplies authenticated seller-origin product ID, price, licensing manifest, download, refund/fee policies; Site QA tests a permitted purchase and delivery before *any* CTA | **HOLD / UNVERIFIED**; never count checkout clicks as sales | Growth, Claude/merchant QA |
| Free household plan | Social landing → ungated full guide | Guide and source/citation/safety reviews incomplete; no verified release | Review all shared scopes and dangerous guidance, confirm actual canonical route, print/mobile and a11y 320/360/390/768/1440 | **HOLD / UNPUBLISHED** | Preparedness, independent QA |
| Grok/Praxxis social topic | Asset ID + allowed link → landing | TASK-008 lacks a verified matching Preparedness asset ID, publish time, post URL, destination and permitted CTA surface | Grok supplies exact immutable `asset_id`, platform, actual post link or `pending`, source rights; Praxxis QAs; Claude maps destination and correct canonical | **UNVERIFIED**; no published asset claimed | Grok/Praxxis, Claude |
| Optional distinct paid companion | Reader → offer detail → checkout | No approved, appropriate product or merchant fulfillment | Draft only: no display until rights, relevance, real price, adjacent disclosure, terms and accessible downloadable pack verified | **NOT TESTED** | Growth, Claude, Site QA |
| Optional email capture | Reader → current /focus/ signup | Consent, confirmation and delivery cannot be inferred from pageviews | Use existing approved list only; confirm opt-in and file delivery in authorized QA; do not create subscriber records or send without permission | **NOT VERIFIED**; lead ≠ sale | Dispatch, Claude, Site QA |
| Source-confirmed purchase | Qualified visitor → reconciled net revenue | Missing orders, attribution, session-human quality, fees/refunds | Use existing sanctioned analytics; reconcile source-of-truth merchant-paid orders, fees/refunds, 7/30-day cohorts; mark unknown attribution | **N/A** net revenue / 1,000 qualified human sessions | Growth/Claude |

## Nonproduction campaign test spec

Only after Grok/Praxxis confirmation and founder authorization: standard `utm_source=<youtube|tiktok|...>&utm_medium=organic_social&utm_campaign=preparedness_pilot_2026_11&utm_content=<unique_asset_id>`. Preserve asset-ID ↔ platform URL ↔ actual permitted clickable surface (profile/bio, caption or permitted pinned source comment). Do not assume TikTok captions contain clickable links; record attribution gaps. Keep video scripts free of spoken CTA under current TASK-008. No new measurement vendor, duplicate tags, personally identifiable visitor details, cookies without consent, or claims based on bots/QA sessions.

Staged acceptance: landing shows matching intent, source/status labels and a complete readable free guide; no dead route, no inaccessible CTA, no 320/360/390/768/1440px reflow/keyboard failures, no unsupported hazard claims, no disguised paid safety instructions, no published paid CTA without product verification. Confirmed paid order = merchant-side completed payment (not click/start), net = gross minus refunds and fees. Small sample warnings mandatory.

## Reproducible engineering and remaining HOLD

R126 manifest files + `r126_author_scope_gate.py` and 88 synthetic tests. R126 stacked branch and RC have different taxonomy bytes; command **requires two exact checkouts**:

```sh
python -I preparedness/tools/r126_author_scope_gate.py --root /path/to/r126 --candidate-root /path/to/exact-rc584
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

No real full-checkout run, native build, independent browser QA, qualified safety assessment, source URL human checks, mandatory integrity or QD approval has been obtained. See independent safety PR #157; separate fixture PR #169 and isolated follow-up #973. Preserve homepage lead and production boundaries.

**RELEASE STATUS: HOLD.**
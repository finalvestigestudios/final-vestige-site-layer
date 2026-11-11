# Mind R292 — Founder's commercial-accuracy and film QA acceptance dossier
**Status: UNPUBLISHED · ONE CANONICAL PRESELL · ALL COMMERCIAL GATES HARD HOLD · 2026-11-11 PT**

## Executive decision: protect conversion by fixing trust and checkout authorization first

This is an additive, isolated Mind-only development sprint stacked on R291 commit `ae77e2b6bf97c680964524bf708b8ce529203223`. It does **not** edit the homepage flagship PR #49, Issue #150, Mind hub PR #172, production WordPress, the current Focus/Jetpack/Dispatch welcome, Grok's content queue, marketing emails, or analytics configuration. Merge, deployment, mail sends, affiliate activation and spending require separate founder release authorization.

**Commercial conclusion:** Zen12 remains one research-stage candidate for an organized meditation-audio course, **not a merchant-authorized FV offer**. Exact official seller https://zen12.com/getstarted describes 12 levels/48 MP3 and displays variable checkout urgency/discount. Public affiliate recruitment at https://affiliates.inspire3.com/ describes the network, but not FV publisher approval, earning URL, granted ad channels, or contract terms. Targeted Gmail searches on Nov 11 found promotional messages, not an account-specific approval. No connection to a private affiliate dashboard or signed agreement was authenticated. An eligible owned FV paid Mind SKU and its purchase/fulfillment/rights were **not authenticated**, despite previous discussion of Final Vestige products. Therefore no live paid CTA is legitimate yet. Do not infer absence of sales from absence of matching Payhip notification mail.

The most productive immediate action is not another glossy presell page. It is an approval-first evidence packet and an accurate controlled test of the **already existing** unpublished pair:
- A = `mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html`;
- B = `mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html`;
- proposed B media insert candidate = R291 `ORIGINAL-42S-OPTIONAL-VIDEO-INSERT-UNPUBLISHED.html` with `render_original_thatcher_short.py`.

**Never call R284 B playable.** It is a static original storyboarding concept. R291 did locally produce an MP4/PNG/VTT, but this branch does not claim that exact assets have been uploaded into the repository, WordPress or an approved hosting destination. There is no tested live A/B experiment.

## Independent Praxxis QA review of R291 — take corrective action, not repeated claims

Praxxis's dated TASK-008/handoff review identified material defects in assurance and narrative consistency. This sprint records explicit, testable repairs and boundaries:

**1. Distinguish an artistic schema from a replicated Thatcher stimulus.** The R291 renderer's `face()` code changes drawing positions and arcs; it does not construct an experimentally faithful set of upright/inverted photographs with selectively inverted eyes and mouths and then globally rotate the same image. The film may be labeled **“schematic original research explainer”** only. No viewer-response rate, illusion induction or claim of reproducing Thompson's 1980 stimulus is permissible. The 42-second script is explanatory narration text, **not experimental visual proof**.

**2. Binary and captions are not committed media.** R291's committed code references generated `poster.png`, `film.mp4` and `captions.vtt` in the video component, but its seven-file PR lacks those binaries. A real rendering was later reported and locally checked, including 41.9167 seconds and a 170,359-byte MP4, SHA-256 `21fc5ac5db8606dbf72ff2389049a968d070de177c5653f984f4de2067d90715`. Those are local artifact facts, not proof of hosted playback. **Never deploy the component with broken relative sources**; before staging, add rights-cleared versioned media artifacts via the existing approved asset workflow, read back content hashes, and validate actual browser media/captions on a signed-out device. This R292 PR intentionally does not pretend the missing binaries have been uploaded.

**3. Reconcile one creator roster.** The canonical research-only mapping is exactly **Thatcher illusion → manuscript → /focus/**; **Change blindness → published investigation → /focus/**; **Puységur/suggestion → historical archive → /focus/**. The R291 JSON's different third topic, invisible gorilla, is not another independently verified Grok campaign. There is **no authenticated Grok asset_id, post URL, media-rights permission, time of posting or tested mobile destination** for any of the three. Grok/Praxxis, not the Mind writer, must authenticate those details in existing TASK-008; no new content/production instruction.

**4. Use only one guide destination.** “Separate buyer guide” phrasing in any upstream runbook means the same inherited A/B Zen12 guide after required approvals, not a newly proliferating sales landing page. The R292 WP candidate is a **research-room module**, not a second offer page.

**5. Qualify source tests.** A passing regex/source check proves only the invariants actually asserted on the exact fetched inputs; it does not establish arbitrary URL-safety, HTML sanitization, caption sync, WCAG conformance, checkout security or user conversion. The R292 verifier is bounded and calls out each untested category. Real tests at 360/390/768/1440px, no-JS, keyboard, reduced-motion, autoplay behavior, focus outline, transcript and timed caption accuracy are still required. Use a retained test artifact including screenshots/console/network logs and independent Site QA approval before any deploy.

## Editorial-to-offer product fit — with real audience intent

| Creator topic (NOT an assigned Grok post) | Evidence-led reader question | Published/candidate article | Free relevant action | Optional eligible commercial explanation |
| --- | --- | --- | --- | --- |
| Thatcher illusion | Why can an inverted face hide a visual change? | R291 unpublished original investigation | Current /focus/ routine; no diagnosis | Zen12 only to visitors explicitly seeking structured meditation audio, not “fix your eyesight.” |
| Change blindness | Why did I miss a conspicuous change? | https://finalvestige.com/2026/11/02/change-blindness/ | Read sources / free Fieldbook | Zen12 only as separately considered audio course; no inferred attention improvement |
| Puységur / self-hypnosis | Can suggestion change experience, and what makes an account credible? | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ + new R292 manuscript | Documentary source trail + same Fieldbook | Hypnosis Live only an independent seller-reviewed reference, **not** an authorized FV CTA; prefer the single approved Zen12 experiment if fit actually exists. |

The current high-intent audience is not “anyone who watches illusion videos.” It is a reader who has voluntarily moved from source-based perception or suggestion research to a practical question: **Should I pay for a structured meditation audio course when a timer and workbook are free?** That sequence keeps editorial learning complete even when no purchase happens.

## One offer → funnel step → blocker → controlled change → evidence → owner

| Offer / step | Blocker | Change/experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Zen12 / authorized purchase | FV publisher identity, category/channel rights, earning URL NOT verified | Authenticate issued agreement, exact product URL, restrictions and approved media | Named account acceptance + independent portal readback; currently FAIL/HOLD | Founder + Mind |
| FV owned Mind SKU / fallback | Current paid SKU, rights, delivery, refunds, price NOT authenticated | Review existing product inventory, select a single relevant SKU **only if real** | Merchant inventory screenshot + real checkout & fulfillment record; currently UNKNOWN | Commerce + Founder |
| Creator landing / genuine human visit | media IDs, rights and mobile link absent | Reconcile 3 existing Grok topics without posting or queue changes | Immutable asset ID, post URL/date, rights and signed-out URL; currently UNKNOWN | Praxxis/Grok |
| Landing / A vs B | B playable hosted film not available | Keep text guide as control; stage B only after verified accessible media | Same copy/CTAs, only optional media differs; actual-browser tests unrun | Mind + Site QA |
| Source article → Focus | Unknown attributable confirmed subscriber | Preserve **one** existing /focus/ / Dispatch list; use native platform data only | Provider-confirmed subscription keyed to permitted campaign; currently UNKNOWN | Claude + Dispatch |
| Future link → affiliate_click | missing account terms and earning link | When authorized, visible disclosure directly alongside a real off-site CTA | Verified first-party event `affiliate_click` + QA of destination; currently NOT IMPLEMENTED | Claude + Mind |
| Commission → net revenue | no merchant-paid report, refunds/fees ledger or traffic-quality denominator | Reconcile merchant payouts and 7/30-day qualified cohorts | independently cleared commission and settled refunds, fees, order IDs aggregated; currently NOT COMPUTABLE | Commerce |

## CTA disclosure and UX contract

**Prospective copy adjacent to a future link:**
> If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.

Until publisher approval and an actual issued URL are authenticated, use a real **`<button disabled>`**, not a fake `aria-disabled` link or a clickable direct merchant URL. The button text should explain the unavailable status. Keep FTC material-connection disclosure close to the button as an understandable **prospective** statement. Place it again adjacent to any later permitted earning link after a separate review. Do not imply commission payments have been received.

The seller's Zen12 checkout displays a countdown and a public $87.99 total on 2026-11-11, but this is **not** an authorized price for Final Vestige, a verified duration of a promotion, or an earning link; no discount, scarcity, price or refund guarantee is asserted in the CTA. Separate merchant newsletter consent from the existing FV Jetpack consent. Paid links remain withheld.

FTC sources: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . Product description sources: https://inspire3.com/ ; https://zen12.com/getstarted ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://brainwaveshots.com/focus-shot ; https://brainwaveshots.com/faq .

## First-party privacy-safe measurement specification (proposal, not installation)

Use `utm_source=tiktok|youtube|instagram`, `utm_medium=organic_social`, `utm_campaign=mind_source_2026_11`, `utm_content={verified_asset_id}` only on actual authorized Grok posts where links are supported; store no email address, phone, name, raw session fingerprint or unnecessary IP. If a platform routes through a bio link, record that legitimate intermediary and do not invent a direct post click. Claude should check currently installed WP/Ahrefs/Jetpack tags and avoid duplicate event scripts. An event ID alone is not a person, and impressions cannot be labeled unique humans.

Events are distinct: `qualified_human_session` (conservative, documented bot exclusion) → `article_to_fieldbook_click` → `provider_confirmed_subscriber` (where attributable) → `affiliate_click` (**not a sale**) → `merchant_confirmed_order` → `cleared_commission` → `net_realized_revenue`. No raw merchant PII should enter analytics. Merchant refunds and chargebacks belong to the settlement ledger, not to the click event.

`net_revenue_per_1000_qualified_human_sessions = 1000 * (cleared_commissions + settled_FV_gross_sales - refunds - payment_fees - fulfillment_costs) / verified_qualified_human_sessions`.

If denominator, settlement, refunds or fees are missing, report **NOT COMPUTABLE**, not zero. Stratify 7- and 30-day acquisition cohorts with lagging attribution windows and tiny-sample caveats. Do not claim A/B superiority until purchase/reporting data, matching audiences and uncertainty justify it. In absence of approvals, both conversion-rate denominators and numerical commercial outputs remain unknown.

## Controlled A/B scientific hypothesis, after authorization only

**H0:** Adding an original optional 30–45-second film to an otherwise identical independent Zen12 buyer guide does not increase **net realized revenue per 1,000 qualified-human sessions** relative to a text-only guide. **H1:** It may improve buyer comprehension and conversion enough to overcome added asset performance, production and accessibility costs. The film could also reduce conversion or attract low-intent visitors; this is not an optimization guarantee.

Allocation requires eligible and consent-aware randomly assigned qualified visits where technically and legally appropriate; one offer, one approved destination, same price if permitted, same near-link disclosure, identical CTA, same summary length/source citations, no autoplay, native controls, captions/transcript/poster and a working no-JS text baseline. Compare 7/30-day cohorts and first test checkout/buyer understanding; avoid significance claims with a few sessions. Never optimize outbound click-through while hiding settled purchase outcomes.

### Release governance and blockers

**BUILT:** R292 independent 2,000+ word investigation, source-joined claim matrix, HTML hub insert and this acceptance dossier. **TESTED:** only source checks explicitly executed and reported in the R292 record. **NOT BUILT:** hosted MP4 integration into canonical R284 Variant B. **NOT VERIFIED:** account-specific publisher eligibility, earning link, allowed channels, email rights, paid owned SKU, verified Grok asset IDs, provider-confirmed cohorts, payment settlement, realized revenue. **LIVE:** no R292 content or commercial changes.

Explicit independent review handoffs: Mind Issue #171 owns buyer evidence; Business #820 owns conversion acceptance; Site QA #126 checks browser/WordPress/rights; homepage art owner #150 reviews only visual fit (must not touch PR #49); Dispatch #174 consumes only approved downstream guide references; Grok/Praxxis TASK-008 receives **research-only** topic handoff with no queue edits.

**Final decision: HARD HOLD — No CMS, socials, newsletter, merchant settings, affiliate link, analytics script, merge, deployment or spend.**

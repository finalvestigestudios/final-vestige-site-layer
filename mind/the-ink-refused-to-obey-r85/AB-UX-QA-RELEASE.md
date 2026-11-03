# R85 — Mind & Perception / Zen12 source-controlled pilot handoff

**Status: DRAFT / UNPUBLISHED / HARD HOLD**. Scope is independent Mind & Perception editorial and ethical Inspire3 presell review ONLY. All files newly added in the isolated R85 directory. No homepage flagship PR #49, Issue #150, canonical Mind hub PR #172, Dispatch #174, WordPress or Jetpack edits.

## What changed in this cycle
- New primary-source historical/suggestion investigation: `investigation.md` (*The Ink Refused to Obey*). Separate from commercial copy.
- Zen12 offer-specific impartial guide `zen12-guide-core.html` and complete Gutenberg Custom HTML candidate A text-only `zen12-a-text.blocks.html` / candidate B optional educational film concept `zen12-b-optional-film.blocks.html`.
- Candidate B includes original, explicit 40-second **storyboard / full visible transcript**, not a faux playable video. Existing earlier Mind runs produced separate review MP4s, but this milestone does **not** represent that an R85 video was rendered or uploaded.
- Noncanonical four-stream Mind hub `mind-hub-noncanonical.blocks.html`: editorial, no merchant URL, links only to verified existing published Puységur and Focus resources; PR #172 remains the authoritative canonical hub.
- Claim/proof/permissions matrix `claim-source-permission-matrix.json`: 19 source records, 32 claim/decision entries, 18 false activation gates.
- Nonimported, **disabled** synthetic-only privacy model `privacy-model.mjs` with strict allowed tuple dimensions and min-20 cohort suppression. No page loads this module and no production telemetry exists.
- Native Node regression test source `tests.mjs`; execute `node --test mind/the-ink-refused-to-obey-r85/tests.mjs` from repo root.

## Evidence and originality
Primary Stroop full text: https://psychclassics.yorku.ca/Stroop/ ; APA doi: https://doi.org/10.1037/h0054651 . The paper reports an increase from 63.3s to 110.3s across 100 ink-naming responses under the stated conditions, not a universal 74% human reading slowdown. Reading word stimuli in conflicting colors increased only 2.3s, reported nonreliable. Practice reduced interference, without elimination. MacLeod's synthesis: https://pubmed.ncbi.nlm.nih.gov/2034749/ . Suggestion systematic review, 19-study narrative and 14-study interference meta-analysis, with population limits: https://pubmed.ncbi.nlm.nih.gov/38874567/ . No implication that consumer audio reproduces those effects.

Zen12 official *exact* public sales page https://zen12.com/hnp ; product About https://zen12.com/about ; Research https://zen12.com/research ; checkout https://zen12.com/getstarted ; Inspire3 catalog https://inspire3.com/ ; privacy https://inspire3.com/privacy/ . Twelve-minute format, four styles, 48/24/24 track differences are seller descriptions. **Do not inherit** seller claim that 12 minutes equals an hour of advanced meditation. A 2023 synthesis https://doi.org/10.1371/journal.pone.0286023 of studies of binaural beats is not a Zen12 product trial. Merchant full terms https://inspire3.com/terms/ inaccessible during audit: detailed refund procedure NOT confirmed. Public recruitment https://affiliates.inspire3.com/ is not Final Vestige account authorization, rights to ads/swipe, payout proof, or permission for email and social media.

FTC source for adjacent commercial disclosures: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; objective health claim rules: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Original low-friction offer construction
**Hook:** A known experiment shows competing responses; can a listening routine be chosen without believing an extraordinary marketing claim?  
**Micro-story:** Stroop's stopwatch and the asymmetry in naming ink vs reading words.  
**Useful demonstration:** three independent free twelve-minute listening preferences, no audio vendor dependence.  
**Actual offer value:** a seller-described library of twelve-minute MP3 audio in multiple listening styles and levels.  
**Limits:** no own experience, no verified product efficacy, health outcome, commission, pricing, funnel rights or terms.  
**Near-CTA disclosure:** future conditional commission text immediately before a real native disabled button.  
**No active merchant link** in either variant, despite the merchant source URLs being documented outside the outgoing offer UI.

## A/B decision design — hypothesis, not a result
- A = full independent guide with no film element; B = same byte-identical guide preceded by optional **unhosted** 40s video concept + visible full transcript.
- Before any user-exposed test, replace storyboard with a first-party original 30–45s MP4 (<250KB aspirational, **not yet measured**), poster with meaningful alt, WebVTT cues timed to real media, controls and `preload="none"`; check total transferred bytes on representative constrained mobile connection. **No autoplay**.
- Do not randomly assign or persist visitor IDs. Do not infer a causal lift from a handful of visits. If a formal test is ever authorized, pre-register primary metric (approved offer link intent, NOT sales), time window, traffic source strata, exclusion criteria, required power/sample and event minimization with QA. Organic/TikTok sources likely create selection confounding. Video watch duration is not a required metric.
- Current privacy model accepts **synthetic counts only** in topic/variant/source/action enumerations; rejects full URLs, IP, emails, click IDs, user agents, query strings; excludes rows under 20. It MUST remain unimported until separate privacy and lawful measurement approval. Referrer/query-string logging is NOT assumed safe.
- No new form and no email-list duplication. The single published /focus/ destination remains the only Focus/Jetpack funnel.

## Internal links and routing
1. When approved, Mind hub can be linked once through Explore / Library (and limited homepage teaser coordinated with homepage lead, not edited by this branch). Preserve six historic category tiles.
2. Independent article should contain a sources desk and link to authentic published Puységur archive; optionally end with **existing free Focus Fieldbook**. It should not be an advertorial and must not embed Zen12 links.
3. The separately labeled commercial evidence guide can be linked from a “Tools Under Review” card with editorial context, but only when destination is approved as a published link. No placeholder broken paths.
4. TikTok “The word says BLUE. The ink says red. Which one do you answer?” is a truthful fact-first hook; description should route to the actual published investigation when one exists, not to an unpublished or disguised merchant page.
5. Dispatch #174 owns newsletter issue drafts and email compliance. This lane owns only the evidence buyer-page destination. Share verification status but never edit, schedule or send Dispatch emails.

## QA/release protocol
- Source verification: primary paper/context checked; exact merchant SKU and checkout rechecked against release-day pages; FTC disclosure and implied health claims independently reviewed.
- Semantics: a single H1, anchor destinations real and authorized, keyboard focus indicators, contrast tokens, accessible no-JS text, right-to-left and zoom check, color not sole channel of meaning.
- Responsive: real Chromium checks at 360/390/768/1440/1920, keyboard and screen-reader, 200% zoom, touch, dark-mode/reduced-motion, no-JS. Current source-level CSS is NOT a substitute for these real-browser checks.
- Security: no scripts, iframes, inline event handlers, forms, autoplay, third-party libraries, external video widgets, redirect cloaks, untrusted `innerHTML`, data collection or newly activated merchant URL. Confirm Gutenberg does not strip or reshape critical disabled attributes during actual private preview.
- Conversion hypothesis: optional film may or may not improve comprehension and engagement; no measured effect is claimed.
- CI: execute exact-head native Node test in GitHub Actions or authenticated checkout, record run URL and SHA; independent Site QA must review exact final head and public WordPress draft output if founder separately authorizes safe draft CMS writes. This work has NOT done those CMS actions.
- Release: only explicit founder publication authorization + partner acceptance, allowed product/website/TikTok/email channels, approved creatives, validated link, privacy safeguards, terms/refunds, testing and independent QA may remove HOLD. No live publish/merge/deploy under this ticket.

## Blockers
1. Final Vestige-specific written Inspire3 affiliate acceptance; explicit Zen12 SKU, channel rights, tracking link and creative permissions.
2. Revalidate accurate checkout/terms/refund and customer-level affiliate reporting data exposure; **reject buyer-level PII** by default.
3. Render a unique, accessible first-party 40s MP4; poster/captions sync; legal/creative review; performance validation.
4. Native Node/hosted CI on exact final SHA; Chromium/WebKit mobile and full WCAG audit; founder release/WordPress approval.
5. Coordination: independent Site QA #126, homepage art lead #150 (do not edit), Dispatch #174 (no email writes). Existing PR #172 hub remains canonical.

**No claim of product sales, conversions, health benefits, personal testing, prices, affiliate approval, real user analytics, browser compliance or completed video.**

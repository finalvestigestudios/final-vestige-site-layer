# R196 — subscriber-to-one-offer progression and attributed paid conversion contract (NO SEND)

## Goal and one offer first
Audience: people who voluntarily confirm Dispatch through the Focus Fieldbook and voluntarily continue reading evidence-based focus material. The **single provisional offer under evaluation** is Zen12 Premium; never market it as scientifically proven to replace longer meditation. Issue 05's separately allocated Hypnosis Live opportunity remains on HOLD, protecting the four-editorial/two-commercial split; do not activate both simply to fill slots. If Zen12 email-channel approval remains absent, keep issue 03 commercial CTA blocked or use the explicitly **unapproved** no-offer fallback from PR #201 only after editorial decision, not automatic substitution.

## Sequence within original weekly cadence, not additional email volume
- Existing welcome: already configured with 52-page Fieldbook; no commercial purchase suggestion is required. Receipt and actual provider-confirmed consent are UNKNOWN.
- Week 01 (original issue 01): source-led perception investigation; CTA to a **published** investigation. Measure email-to-site interest only if legitimate received emails eventually exist.
- Week 02 (original issue 02): history of suggestion / Puységur; reinforce Final Vestige's evidence standard, not 'hypnosis works' rhetoric.
- Week 03 (original commercial issue 03): optional independently written Zen12 evaluation guide **only if** publisher email permission, exact offer, guide and near-link FTC disclosure all verified. If not, HOLD rather than send an empty CTA or off-platform earnings link.
- Week 04 (historical issue 04): return to history and records. The Nightingale alternative here is *not* approved to replace Apollo 1.
- Week 05 (original commercial issue 05): separate Hypnosis Live gate; its release does not inherit Zen12 permission.
- Week 06 (original issue 06): existing **confirmed subscribers should not be asked to join the list again**. Proposed changed CTA is a direct permitted copy of the already-configured PDF or a fresh published investigation; evaluate editorially before modifying original issue 06.

## Segmentation hypotheses, not observed counts
First-time confirmed Fieldbook recipients may value a free practical resource; newsletter subscribers who click historical investigation sources may value archives; readers who deliberately click the audio-evaluation guide may be closer to purchase. **No behavioral tagging or third-party retargeting** without a valid consent basis and data inventory. Keep issue content broadly useful, avoid coercive 'you downloaded, so buy' messages. When the count is three, report cohorts descriptively and suppress personal profiles.

## Proposed event/UTM contract, not deployed
First-touch platform metadata from Grok: `utm_source=(tiktok|youtube|...)`, `utm_medium=organic_social`, `utm_campaign=cluster_pilot_2026_11`, `utm_content=<actual grok_asset_id>`; do not fabricate asset IDs. Subscriber confirmation event `confirmed_signup` emitted once ONLY after provider-confirmed transition; no PII to public analytics. Email CTA: `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue03_zen12_guide` (or the exact issue ID). Preserve first-touch separate from last-click; a click may come from someone who never visited from Grok and cannot be retroactively assigned to an asset.

Event classes: `qualified_human_session` (privacy-safe deduped session), `campaign_landing`, `editorial_cta_click`, `confirmed_signup` (provider backed), `fieldbook_welcome_delivered` (provider or authorized received proof, if available), `offer_guide_click`, `affiliate_outbound_click`, `merchant_confirmed_paid_order` (from independent merchant data), `net_revenue_reconciled`. An email open pixel is not a buyer; data gaps remain explicit. Respect platform consent and avoid duplicate Ahrefs/Jetpack instrumentation.

7- and 30-day verified cohorts: qualified human session count; confirmed subscriber transitions and reachability; *separately* merchant-confirmed paid orders and customers; gross paid revenue, settled commission, refunds, fees and realized net revenue. Formula only with verified inputs: `net_revenue_per_1000_qhs = 1000 * realized_net_revenue / verified_qhs`. Missing reconciliation or denominator = NOT COMPUTABLE, **not 0**. A true independently audited zero-transaction ledger may justify zero, but no such ledger was obtained today.

## Owner and experiment order
1. Claude / Focus / #129: truthful page success state; provider-confirmed aggregate; no browser `confirmed_signup`.
2. Dispatch / #174: actual received Jetpack email rendering, owner postal address and functional unsub (requires separate founder-approved test if none exists); source-based subject/accessibility QA.
3. Mind Studio / #171: exact publisher permissions, email channel, issued earning URL, live objective guide and checkout/refund claims.
4. Commerce/Praxxis / #820: independently corroborated paid orders/commissions/refunds and qualified-human denominator; no published claims from clicks.
5. Founder: explicit **final campaign send/audience/schedule authorization** after all gates. All six remain HOLD_UNSENT today.

# R197 · confirmed signup, email attribution and one-offer progression contract
**Status: proposed, non-deployed. Owner split:** Dispatch owns definitions/read-only QA; Claude/Focus #129 owns production implementation; Mind #171 owns guide and merchant eligibility; Commerce/Praxxis #820 owns independently reconciled paid orders; Grok owns creator assets and posting. No tracking snippet is authorized by this document.

## Event conditions and idempotence
`confirmed_signup` is generated **only** after the actual newsletter provider reports an eligible email subscription transition to `Subscribed`, with a provider-confirmed timestamp and double-opt-in provenance where required. A browser URL query such as `?subscribe=success`, a visible gift, download of the PDF, a Jetpack widget CSS class, a Reader follow, or an unconfirmed request is **not** acceptable evidence. Deduplicate by an internal opaque keyed event identity stored only on server/provider side; never transmit subscriber email, tokens or stable raw hashes to public analytics. Count repeated UI submissions as **one eventual confirmed lead**, not repeat leads.

If unsubscribe/suppression exists, forbid email eligibility even after a historic confirmation. Read-only status counts currently show 3 total, 3 confirmed, 2 unconfirmed, WPcom followers 3/email-only 0, and do not resolve this. Request a private filtered **aggregate** for `Email subscription = Subscribed` before any audience discussion. Preserve data minimization; no export of PII needed.

## Source attribution (proposal; no live UTM rewriting)
Acquisition by Grok (when genuinely published): `utm_source=tiktok|youtube|...&utm_medium=social&utm_campaign=<approved-campaign>&utm_content=<Grok-assigned-asset_id>`. Never invent an asset ID or overwrite Grok TASK-008. Restrict allowed values to approved names; discard untrusted free-text from telemetry.

Newsletter editorial click after approved send: `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026&utm_content=issue_0N_<editorial_slug>`. For issue03 use `issue_03_zen12_guide` only **once the actual guide is live and authorized**. Non-commercial emails can point directly to existing source-led investigations. This separates Grok's originating asset from later email nurture; attribution stitching should use only permitted consented/session-safe aggregate data, and never expose personal identifiers in URLs.

Define funnel stages with mutually exclusive evidence labels: qualified-human-landing (deduplicated and bot-filtered) → editorial CTA click → provider-confirmed email consent (if relevant) → verified welcome delivery → live independent buyer guide → verified merchant outbound click → paid settled order → reconciled refunds/fees → realized net revenue. Stages are **not interchangeable**; one visitor can contribute to multiple stages without becoming multiple orders.

## Proposed segments, not automatic blasts
- **Unconfirmed/pending:** no editorial or commercial nurturing; show appropriate confirmation guidance only in original consent UX.
- **Subscribed with unknown welcome receipt:** no claim of Fieldbook delivery. Verify delivery without contacting the list. Do not trigger automated resends.
- **Verified welcome + historical-interest:** send editorial-only candidate *after final approval*. No assumed consent to specific third-party marketing.
- **Verified welcome + explicitly relevant focus interest:** eligible for a *proposed* Zen12 guide edition only if one-offer merchant rights and legal gates pass; never infer interest merely from an opt-in or from a third-party newsletter.
- **Unsubscribed, suppressed or unknown status:** exclude from sends and experiment denominator.

## Non-sending follow-up hypothesis, no schedule
**Step A** — Editorial research: show one historically documented attention/perception finding with one investigation CTA.
**Step B** — Evidence log: encourage free Fieldbook use without another signup; one eligible CTA to the existing resource.
**Step C** — Only if interest, eligibility and merchant gates permit: compare an optional 12-minute audio practice against no-cost habits, explaining Zen12 as seller description and discussing limitations. One guide CTA with adjacent commission disclosure, no direct speculative affiliate link. Otherwise stop at free resources.
The *original founder 4:2 pilot allocation remains intact*. This is not permission to substitute Step A/B/C for the six issues or initiate another mail sequence.

## Source-of-truth revenue evidence
Only independently reported **settled paid orders/commissions** and confirmed refunds/chargebacks/fees count. For no orders, require an independently reconciled statement covering the cohort instead of assuming absent rows prove zero. Report 7- and 30-day cohorts separately and disclose tiny samples. Formula: `net_realized_USD / QHS * 1,000` when numerator and denominator exist. Else `NOT_COMPUTABLE`.

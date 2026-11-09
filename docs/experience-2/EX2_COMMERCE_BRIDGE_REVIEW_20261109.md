# EX2: review-only physical-record partner guide bridge
**2026-11-09 PT — Source-gated proposal, NOT deployed.** Parent #1689; frozen #49 untouched. This does not replace any of the seven existing chapters or the published Gutenberg homepage.

## Commercial thesis and exact route
Audience: a qualified visitor who finishes an archival investigation and wants to inspect physical history-related collectibles. Existing verified editorial destination: `/mini-museum-history-collectibles/` (WordPress page **2088**, published; modified **2026-11-05T20:01:36**), via existing `/collection/` hub (page **78**). The proposed link is a **single, optional internal editorial guide**, in the final archive exit — not a direct affiliate link, sponsored historical investigation, pop-up, new chapter or unverified merchant claim. The destination presently includes a plain-language commission disclosure adjacent to its Awin-sourced links, each with `rel="sponsored noopener noreferrer"`. Publisher permission, merchant settlement, current product inventory/price, tracking attribution and eligible commissions are **not verified** by the presence of WordPress links. Inspire3 is not activated; independent Mind #171 remains separate.

Hypothesis: a contextual, non-disruptive link after evidence engagement increases qualified visits to the existing collecting guide **without decreasing Focus signup or archival engagement**. A qualified guide visit or affiliate click is not a paid conversion. Revenue evidence must come from independent settled Awin orders, less refunds/fees, divided by qualified human sessions × 1,000. No monetization metrics are claimed here.

## Read-only source inspection
- **Production Page 6**, modified **2026-11-05T12:07:24**, examined through authenticated WordPress editor read. Its published exit presently offers four links: Investigations, Public Record, Research Library, and Focus. No link in that editor source points to the Mini Museum guide.
- Page 6 source has **seven chapter target IDs**, **72 historical Margins items** and **one native Jetpack subscription block**. None may be deleted or rewritten for this proposal.
- Destination Page 2088's editor source includes its own plain-language affiliate disclosure and Awin creative parameters; no new external/earning URL is inserted into Page 6.
- Actual source was processed **read-only in memory** with source-exact exit insertion and inverse restoration: **11/11 source/guide checks PASS**; source chars 150,710 → 151,095 for markup-only insertion (the separate scoped CSS is added only by the Python patcher). This was not a WordPress write or exact WordPress render.
- Python patcher fails closed if the actual exit markup changes, one of seven IDs is missing, the 72 items or Jetpack block change, the link already exists, the guide's disclosure/sponsored markup goes away, or any input/output path would overwrite the source. The candidate editor document is local only, never committed.

## Offline acceptance
- Python synthetic regression: **9/9 PASS**; original native Jetpack marker, 72 records, seven IDs and all original exit links preserved.
- Local Chromium **25/25 PASS**, using the exact observed published exit HTML and a representative extract of its CSS, with and without the new bridge at **320, 360, 390, 768, 1440 and 1920px**, no JavaScript and normal/reduced-motion. No horizontal overflow; keyboard focus and ≥44px target in representative fixture.
- One extra **CSS-zoom 200% simulation** passed. This is **not genuine browser 200% zoom**. Screenshots are explicitly offline excerpts, not live WordPress screenshots.
- No measured host Lighthouse/CWV, no actual WordPress/Assembler rendering, no hosted image bytes, no real Jetpack signup/confirmation, no Awin paid order, no independent axe or WCAG 2.2 AA certification, no QD/CI sign-off.

## Safety and handoff
**RELEASE HOLD.** The production homepage was already published independently of these draft PRs. No production CMS/theme/navigation/settings writes, merge, release, social distribution, paid service, subscriber events, email or analytics additions. This review can be accepted only if a *real* anonymous visitor path and current authorizations demonstrate improvement. To avoid conversion cannibalization, compare Focus engagement and paid conversion together, using Grok's existing approved asset IDs and Claude's attribution implementation; do not create parallel UTM scripts.

Owner decision: retain the published 7-chapter flagship; review this small after-evidence commercial bridge (not a hero replacement) as **one** experiment, only after the separate Focus false-success defect #1681 is resolved and validated with real Jetpack confirmation. Ensure partner permission/merchant eligibility and origin-render QA before release.

References: #150 art/release, #820 commerce, #818 charter, #171 Mind separation, #158 Apollo 1 custody, #1689 hero Focus review, #1681 Focus integrity. No pending WordPress.com native staging clone: current Personal plan; isolated WP Playground permitted, hosted acceptance still outstanding.

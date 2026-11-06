# R174 — Preparedness rendered-citation custody (DRAFT / HARD HOLD)

**Additive review-only gate; no merge, publishing, QD approval, food/medical-safety approval, monetization or CMS writes authorized.**

Stacked on R173 exact commit fcd0c6254e51e44dc52a6423695307be208b7b86. This change inspects in-memory WordPress-ready draft markup produced by existing build.Library and build.build_article rather than modifying the original 35 articles. The gate links every original citation marker to the exact ordinal in-text reference and article-origin-specific external source URL, its title, source-use explanation, pending human link check, and shared-URL reading-scope warning. It checks for duplicated/missing source entries, wrong URLs, false link approvals, altered draft labels, missing reading depth, duplicate article routes, and changed output wrappers. --check-export additionally compares existing generated WordPress and noindex preview files byte-for-byte to the trusted local renderer. No generated files are published.

Existing R161 original-body and R151 contributor pins remain immutable. Original 35 articles, 2,000 citations and 385 article-specific source relationships are unchanged. R173's ten selected claim-scope review decisions, the 75 earlier source-review decisions, the 32 shared-source review groups, and the NCHFP-versus-USDA FSIS jerky conflict all remain unresolved. Matching a citation to a source does NOT establish that the source substantiates the claim, nor that any food, water, medical or emergency instruction is safe. A structural match reports DRAFT_HARD_HOLD and EXIT 2. An invalid/missing input reports INVALID_HARD_HOLD and EXIT 2. Neither is QD PASS.

## Trusted repository commands (read-only gate; draft build only)

    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/r174_rendered_citation_gate.py --repo . --check-export

The new test suite runs 71 Python unittest cases on **synthetic fixtures only**, including 40 distinct URL substitution attacks. Source checkout and native 35-article validation/build remain unexecuted in the local environment while GitHub DNS fails. The gate never creates public content; WordPress rendering, real printing/privacy, full browser accessibility, expert source adjudication and independent QD must still be completed. Authentic output from a trusted checkout is not yet verified.

## Founder conversion-first funnel (draft, nothing enabled)

**ONE audience:** Caregivers arranging family emergency communication and school pickup. **Authentic free guide:** Household Emergency Plan, proposed /preparedness/start-here/household-emergency-plan/ (unpublished, ungated). **Optional free practical tool:** Family Reunification Card, unpublished and pending source/privacy/print QA. **Matching paid practical pack:** not authenticated; do not advertise, create a fake SKU, or introduce a poorly matched affiliate upsell.

| Offer → Funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Existing paid Preparedness SKU → confirmed purchase | Rights-cleared currently purchasable SKU, checkout/delivery/refund proof absent | Commerce audits genuine inventory, fulfillment and transaction records first | HOLD, no paid CTA | Commerce / Claude |
| Household Emergency Plan → free guide | Source/safety/QD and native build outstanding | Complete expert source check, genuine native build | DRAFT, NOT LIVE | Preparedness / independent QA |
| Guide → free Family Reunification Card | 11 source decisions and actual WP privacy, print and accessibility untested | Staged browser test at 360/390/768/1440 with synthetic information | HARD HOLD | Preparedness / Site QA |
| Grok asset → source-backed guide | Matching published Preparedness asset_id/post URL/destination not present in TASK-008 | Grok/Praxxis reconcile exact asset and approved link context; never seize creator queue | UNVERIFIED | Grok / Praxxis |
| Paid order → realized revenue | Qualified-human sessions, merchant sales, fees, refund records absent | Reconcile 7/30-day purchase cohorts, net revenue and human denominators | NOT COMPUTABLE | Commerce / Analytics |

Draft CTA (NOT LIVE): “Make a plan for how your household will reconnect. Read the free Household Emergency Plan.” After independent Card review only: “Use the free printable Family Reunification Card.” No active paid CTA without a verified existing product. Landing acceptance checks: social-to-page topic and URL match, accessible mobile link, source scope preserved, ungated public-service advice, privacy-safe existing analytics with no duplicate scripts, optional lead capture only via approved Focus infrastructure, real checkout and delivered files, merchant-confirmed purchases and refunds. Do not count clicks, signups or visits as sales.

Status and coordination: Issue #136 Preparedness; #820 creator-to-customer measurement; charter #818; shared TASK-008 (Praxxis/Grok). Seven original Claude branches remain frozen at documented exact SHAs (checked 2026-11-06). Independent QA #157 and synthetic test #169/#973 remain separate; homepage #49/#604 untouched. Founder keeps all posting, spending and production release approvals. No WordPress, navigation, email, social, analytics, merchant, checkout or affiliate changes.

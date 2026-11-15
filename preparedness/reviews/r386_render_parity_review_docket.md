# R386 — Original 35-article WordPress/preview citation and claim parity (review only)

2026-11-15 PT | Issue #136 | cross-ref #820 and business charter #818 | DRAFT / HARD HOLD / NO PUBLICATION

## Engineering objective and boundary

Extend the pinned-original R384/R385 source/citation custody to the **actual rendered HTML delivery boundary** without modifying the seven contributor branches, original articles, sources, CSS, WordPress, CMS, navigation, checkout, analytics, emails or Grok tasks.

`preparedness/tools/r386_rendered_citation_parity.py` compares each original `slug.body.html` provenance variant against two **read-only, privately generated** exports (`build/wp/<slug>.html` and `build/preview/<slug>.html`) after R384 obtains exact original original-Git SHA + byte-length verified inputs. It requires all 35 article identities and all nine unresolved Shelter forks and refuses any implied selection among original variants.

The tool fails closed on missing/mismatched WP vs preview artifacts, incorrect or duplicate article/canonical identity, source citation number/order changes, missing or duplicated source backlinks, hidden rendered citations/sources, changed claim prose paragraphs, lost `source_use` reading scopes, foreign-URL substitutions (including otherwise-valid HTTPS URLs), missing draft/QD caveats, preview noindex failure and unexpected extra artifact slugs. Source URL mapping is assembled from original SHA-checked R375 fragment crosswalk and BASE register with a preference for the originating contributor's source. It never confuses global source-ID presence with human adjudication.

**Important coverage limit:** The gate checks the 35 original articles. Additional index, hub and tool exports are enumerated for independent QA, not certified by a misleading article count. CSS-computed visibility, actual browser rendering, mobile accessibility, verified source passage meaning and risk/medical advice accuracy still require independent reviewers. Matching an original version is *not* proof that version is correct or safe, and is not authorization to choose it.

## Evidence produced in isolated environment

- New **58/58** distinct adversarial synthetic unittest cases PASS (`python -I -m unittest discover -s preparedness/tests -p 'test_r386*.py'`).
- Combined available **879/879** R374–R386 isolated Python unittest cases PASS. Source code Python compilation PASS.
- Native command using inaccessible original Git object repository: **exit 2**, `AUTHENTIC_INPUT_UNAVAILABLE:CalledProcessError` and `INVALID_HARD_HOLD`. This is expected when authentic full original repository/exports are absent; do not claim native build success.
- **NOT EXECUTED:** authenticated 35-article build/validator, authentic 50 WordPress + 50 private preview parity, hosted CI, source/food/water/emergency/child-privacy QD and final approval.
- Seven original Claude clusters plus two Shelter successors were checked against exact original SHA pins: 9/9 identical, ahead 0/behind 0. Independent QA PR #157 and fixture PR #169 were still unmerged drafts; dependent fixture #2205 and homepage lead #1689 unchanged.

## Acceptance, release and commerce controls

Always hold `publication_approved=false`, `qualified_safety_approved=false`, `merchant_offer_verified=false`, `live_release_allowed=false`. Exit 2 even if synthetic/real preview parity is successful. No public editorial step, live release or attribution conclusion can be inferred from isolated tests.

### Priority conversion matrix (offer → funnel → blocker → experiment/check → evidence → owner)

1. One existing FV-owned Preparedness practical pack → paid purchase → no authenticated rights-cleared payable/deliverable Preparedness SKU → founder/Commerce verify actual product, price, lawful rights, working mobile checkout and email delivery/refund ledger in a private approved test → **HOLD / no order evidence** → Founder/Commerce.
2. Grok family emergency-contact asset → free authentic Archive household guide → no verified published `asset_id`, exact factual hook, website destination or rights inventory → Praxxis independently checks TASK-008 asset-to-landing intent, caption/bio restrictions, mobile 360/390px and free guide linkage → **UNVERIFIED** → Grok/Praxxis.
3. Free household guide → optional Tool #104 family reunification card → child privacy, emergency source wording, physical print/trimming and accessibility not independently signed → keep tool PRIVATE and free CTA **draft only** pending QD; no retired water freebies → **HARD HOLD** → Preparedness/QD.
4. Verified qualified-human sessions tagged unique `asset_id`/campaign → landing → CTA → independently confirmed lead → merchant-confirmed paid order → net fees/refunds → 7/30-day net revenue per 1,000 qualified sessions → no merchant receipts, consent-approved attribution and session denominator → do not equate clicks/subscribes/checkouts/affiliate outbounds to sales; report KPI **not computable** → Claude/Commerce.

**Candidate free-only CTA (NOT DEPLOYED):** “Start With Trusted Preparedness Resources” → `https://finalvestige.com/preparedness/`. Do not promote any paid pack until actual product and checkout are verified. No live analytics changes or duplicate scripts.

## Next steps for qualified review

1. Acquire full authenticated Git objects and complete native repository, run validate/build plus R386 against real 35 article pairs and all extra hub/tool/landing artifacts. Preserve source and manuscript variants unselected until qualified adjudication.
2. Inspect exact rendered citations at mobile widths, including invisible-style and HTML edge cases, and externally verify source passages for Article #7 and Article #11.
3. Resolve five original divergent source reading-scope groups and nine Shelter blob forks without claiming the newer manuscript is superior, followed by separate QD and founder release governance.

Read-only review document, not WordPress content. No external production or commerce effects.
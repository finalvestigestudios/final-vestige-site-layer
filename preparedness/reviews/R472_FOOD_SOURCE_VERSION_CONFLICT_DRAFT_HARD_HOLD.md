# R472 — Article #11 source-version discrepancy release quarantine

**2026-11-18 PT** · Issue #136 · business constraints #820 / #818 · **DRAFT / HARD HOLD**. This is a read-only source/citation gate, **not** editorial replacement language or food-safety approval.

## Authenticated P0 finding
The *original* Article #11 \`safe-jerky-dehydration\` body **Git blob \`6fa55c397b161437e016d5d4a6c27da7ce3fa6bd\`** contains **two** distinct prescriptive wild-game/Trichinella freezing instructions:
1. Introductory **“What to do now”** list, original HTML source **line 7**, citing \`nchfp-jerky\`.
2. **“The hazards, named”** Trichinella table row, original HTML **line 37**, again citing \`nchfp-jerky\`.

Original metadata Git blob \`50b365e8109c14bdb9ce1a9365db88215a678ec5\` identifies #11, status \`draft\`, safety review \`pending\`, reviewer/date null, and explicitly records a \`nchfp-jerky\` reading scope including **“Trichinella freezing; handling; wild game”**. Source/citation structural provenance is intact; it **does not validate the method**.

## Source-version and claim-boundary custody
- [NCHFP jerky page, derived from *So Easy to Preserve*, sixth edition (2014)](https://nchfp.uga.edu/how/dry/meat-and-poultry/jerky/) gives a pork/wild-game freezer procedure.
- [CDC: Preventing trichinellosis (2024-03-12)](https://www.cdc.gov/trichinellosis/prevention/index.html) distinguishes pork from wild game and says freezing wild game may fail for freeze-resistant worms.
- [USDA FSIS: Does freezing destroy parasites? (updated 2025-02-03)](https://ask.fsis.usda.gov/article/Does-freezing-destroy-parasites) says not to rely on *home freezing* to destroy trichina.
- [CDC *Emerging Infectious Diseases*: 2024 NC bear-jerky incident (published July 2026)](https://wwwnc.cdc.gov/eid/article/32/7/26-0062_article) distinguishes observed freezing evidence from proof of infectivity and cautions freezing alone cannot be assumed reliable for wild game.
- Independent editorial source review remains on [draft #2789](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2789), **HEAD \`2a4a68a644c5ea89ae8a2dd31c988364eb984c58\`**; it also reports a 2011-vs-2014 University of Georgia numerical-source discrepancy. **Do not choose a temperature/duration as an automated solution.**

**Human decision required:** A qualified food-safety reviewer must evaluate the actual source versions, both separately situated claim passages, the entire processing/storage guidance, and the final corrected article. No statement that an unreviewed preparation method is “safe” is authorized. Article #11 remains draft; no source register, manuscript, metadata, QD state, canonical route, output, CMS, social, paid offer or attribution script is changed.

## New isolated engineering
\`preparedness/tools/r472_food_source_conflict_gate.py\`:
- Detects both original actionable claim blocks **by structural HTML location** (list item and table row) rather than only token counts; captures source IDs, per-block SHA-256 evidence and flags any extra/missing location.
- Requires original pinned body/metadata Git blobs, source-use reading scope, no duplicate metadata JSON keys, draft-only publication state and pending/nonexistent reviewer/date.
- Rejects citation substitution and all false QD/safety state claims. All outputs, even successful evidence matching, explicitly say **\`may_publish=false\`** and return exit code **2**.
- Calls pinned R471 source/citation/CSS/35-article deterministic WordPress/private-export gate **only when the complete authenticated checkout and artifacts are present**. R471 original source Git blob: \`f4387ec5c0c275ce6ceb21860e1535979a43e390\`.
- Never executes WordPress, navigation, public site writes, network uploads, checkout tests or revenue scripts.

### Test and execution boundary
- Local **60/60 individually named Python synthetic regressions PASS**, including 48 independent mutation cases + 12 core cases; compilation PASS. SHA comparison required with committed Git files.
- Independent *read-only connected GitHub source analysis*: exactly **2** matching original risk blocks among **48** original \`<li>\`/\`<tr>\` segments, both cite \`nchfp-jerky\`. Original body/metadata Git blobs above match the frozen R460 ledger.
- Nine original Claude/Shelter contributor branch refs compare **identical (ahead=behind=0)** to frozen pinned SHAs. Independent QA #157 head \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`, fixture #169 head \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`, repair #2205 head \`bbcf1859768624c611df4abadc564c18247cf32a\`, home lead #3054 head \`1ae792250862b45391c58cc41eca5523017dcb22\` untouched.
- Native original 35-article \`validate.py\`/\`build.py\` and genuine WP/private-preview comparison **NOT EXECUTED** in local runtime because the complete authenticated checkout and generated artifacts are absent. A missing-source exit **2** is a HOLD, not a PASS.
- Prior R471 59 committed tests were **not executed locally against exact checkout**; do not silently upgrade that status.

## Conversion-first hold map

| OFFER | FUNNEL STEP | BLOCKER | NEXT CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Existing FV-owned Preparedness paid pack (none authenticated) | Genuine paid order | No verified SKU, rights, deliverable, merchant checkout, refund/settlement | Authenticate one already purchasable approved pack and fulfill/refund conditions *before* drafting paid CTA | **HOLD**: no verified SKU or order | Founder/Commerce |
| Family-contact/reunification source-backed free article | Published Grok asset → landing | No genuinely matched posted \`asset_id\`, rights, exact hook, signed-out/mobile destination | Praxxis independently verify *existing* Grok asset and destination via TASK-008; do not assign posts | **UNMATCHED** | Grok/Praxxis |
| Free ungated Article #15 → optional free Tool #104 | Reader benefit and trust | Qualified emergency, child-privacy, printing, accessibility review unresolved | Review both separately; preserve original Tool #102 (not a replacement) | **HARD HOLD** | Preparedness / QD |
| Qualified source-linked sessions → confirmed paid customers | Revenue verification | No merchant order/refund/fee ledger or human-qualified cohort attribution | Reconcile 7/30-day cohorts without duplicate scripts | **NOT COMPUTABLE**: net revenue/1,000 qualified sessions | Claude/Commerce |

Retired water offers **not revived**. Paid, commercial, print, social and website releases remain owner-controlled and unapproved. Draft remains **HARD HOLD**, independently of whether tests pass.

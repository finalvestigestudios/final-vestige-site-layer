# R153 — Cross-round human source-review interlock (DRAFT / HARD HOLD)

Owner/scope: Preparedness Archive ONLY, Issue #136. Conversion coordination #820; charter #818. Date: **2026-11-05**. Parent is R152 PR #1152 at `db92b87abe9e5ea3f6dda5e4d161c2736f5bc94e`. None of the 35 original articles, metadata, citations, source registers, crosswalk, taxonomy, routes, safety states, WordPress drafts, or other agents' work are changed by R153.

## Why this engineering lift matters

R149 has 67 author-specific tool/source relationships (173 citation occurrences); R150 finds 58 unresolved IDs and **four** currently resolved IDs whose author-specific source interpretation would change after candidate remapping. Separately, R151/R152 quarantine eight Historical Food citation substitutions across Pemmican (7/46 citations) and Pioneer Travel Rations (1/39 citations). Reviewing either issue in isolation risks accidentally approving a URL alias while overlooking its related source-use interpretation.

The **R153 interlock** combines these into **75 discrete, deterministic human-review tasks**, preserving the exact source URL, publisher, author-specific `supports` reading, the original tool's `author_specific_use`, citation multiplicity, candidate origin, and per-occurrence Historical Food line context. Every task remains PENDING with no reviewer. Fingerprints allow reviewers to associate their later notes with an unchanged original task; a fingerprint is **not** an attestation or credential.

The R149 and R151 inputs are checked against their exact original Git blob SHA-1s (`e63aaaa35bcb5c4378f05ae45a07cc8cfc5c070c` and `9cf386519eda970209ff6be4ff0243661cd9d996`). The frozen R152 checker additionally requires the original historical Git objects and three distinct NCHFP source records, all `human_link_check=false`. **A matching NCHFP URL is not equivalence of supporting claims, and historical meat-preservation narratives are not modern safety instructions.**

The script detects forged reviewer/QD/medical/publication approvals, omissions/duplicates, lost source explanations, URL downgrades, altered candidate origins, citation-count drift, missing historical contexts and changes in source-scope flags. It does **not** contact websites, validate content medically, take payments, publish, update the crosswalk or generate CMS content. It deliberately reports `DRAFT_HARD_HOLD` and exits **2** on success, and `INVALID_HARD_HOLD`/2 on missing or tampered inputs. Structural passing is NEVER an independent QD PASS.

## Evidence and test status

- **Built:** `preparedness/tools/r153_review_packet_gate.py`; `preparedness/tests/test_r153_review_packet_gate.py`; this runbook. All three are additive review-only files.
- **Tested locally:** Python compilation and **70/70 adversarial unittest methods passing**, including **67 individual false-approval substitutions**, **67 individual source-explanation removals** and **eight individual historical-citation context deletion tests** (142 subcases within the 70 methods). Both committed Python blobs were compared to locally executed file identities.
- **Authentic upstream inventory inspected through GitHub:** R149 frozen 67 relationships/173 occurrences, R151 35 metadata identities and seven branch pins; R152 original-source comparison docs. No original content modified.
- **NOT TESTED/NOT VERIFIED:** R153 executed over a complete authenticated Git worktree; native validation/build, complete multi-round suite, independent WordPress drafts and mobile/print/offline QA, qualified source/food/medical review, QD approval or revenue. Local synthetic tests do not prove the 35-article archive passes. Container cannot resolve `github.com`, so the trusted Git history required by the R152 comparator is unavailable there.

In a complete, trusted checkout of **this exact draft head**, with the frozen referenced commits present:

```bash
python -I preparedness/tools/r153_review_packet_gate.py --repo . --report /tmp/fv-r153-review-packet.json
# Expected exit 2 / DRAFT_HARD_HOLD even if all source bytes and counts reconcile.
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -p 'test_r153_review_packet_gate.py' -v
python -I -m unittest discover -s preparedness/tests -v
```

**Important:** Running native `build.py` may create draft output; do so only in a disposable isolated checkout, not the main working directory. The report option refuses an existing path or one within the repo. No GitHub Actions manual reruns are authorized for pre-runner failures. R153 remains a stacked DRAFT PR, not approval to merge R133–R152.

## Coordination: exact state at this run

Seven Claude contributor branch comparisons (frozen pinned SHA → named branch): **start identical; shelter identical; food diverged (one ahead/one behind); health ahead 1; historical food ahead 1; historical home ahead 2; historical field ahead 1**. Most historical article body improvements are already present in the frozen candidate; only the two Historical Food source-ID substitutions remain quarantined. No later branch content is automatically imported.

QA #157 touches Household Emergency Plan, Three-Day Kit, `start.json`, taxonomy and tests; older article replacements risk losing reading depth/citations and medical wording requires qualified review. Synthetic fixture #169 and follow-up #973 both change `preparedness/tests/test_preparedness.py` and must be reconciled independently without writing shared source fixtures. Homepage #49/#604 is controlled by home lead; nothing modified here.

Additional human holds: 32 shared-URL/source interpretation groups, medicine/heat/food/high-rise fire guidance, 35 article source/safety states, fully verified CMS draft output and independent QD.

## Conversion-first pilot: offer → funnel → blocker → experiment → evidence → owner

| Offer → funnel | Blocker | Controlled change / acceptance | PASS / FAIL evidence | Owner |
| --- | --- | --- | --- | --- |
| **Existing sellable Preparedness pack** → merchant paid checkout | No authenticated matching, rights-cleared purchasable SKU, delivered file, refund terms or verified sales | Read-only merchant inventory + rights, price, full checkout, delivery, fees/refunds. **Do not create or link an imaginary offer.** | **HOLD / NOT VERIFIED** | Commerce/Claude/founder |
| **Free Household Emergency Plan** → article reader | Citation and safety approval, source link audit, full build and QD pending | Complete real source/safety review; compare WP draft to 35 original bodies/citations; preserve every safety instruction **free and ungated** | **DRAFT / HARD HOLD** | Preparedness + independent QA |
| Guide → **optional Family Reunification Card** | Eleven unresolved source IDs; privacy/local storage, keyboard, mobile and print unverified | Human provenance review, then staging QA at 360/390/768/1440 px, keyboard/zoom, offline print, no contact data transmission or exposed sensitive values | **NOT TESTED** | Preparedness + Site QA |
| Grok asset → matched guide | No verified Preparedness-specific `asset_id`, actual post URL or approved destination/UTMs in TASK-008 | Praxxis/Grok supply ID/link placement; Claude confirms canonical destination and uses existing #820 contract; no new tracking scripts or Grok content production takeover | **UNVERIFIED / NOT ATTRIBUTABLE** | Grok/Praxxis/Claude |
| Qualified human session → relevant CTA → confirmed lead → **confirmed paid order** → refunds/fees → realized net revenue | No reconciled qualified sessions, merchant-confirmed purchases or matching offer | Source-linked, privacy-safe event mapping + 7-/30-day cohort; report net dollars per 1,000 qualified human sessions only with real numerator and denominator, flag tiny samples | **NOT COMPUTABLE** | Analytics/Commerce |

**Unpublished, safety-gated CTA draft (NOT deployable):** “Make a household emergency contact plan you can practice. Read the free Household Emergency Plan, then use the optional Family Reunification Card once its source and print/privacy reviews are complete.”

For any approved Grok asset, staging must verify unique `utm_source`, `utm_medium=organic_social`, `utm_campaign` and `utm_content=asset_id`, allowed caption/pinned-source/profile link placement, direct intent-to-guide match, actual successful CTA activation, and approved mobile destination. Never infer a confirmed lead, merchant sale, affiliate commission, or net revenue from pageviews, video views or click counts. Preserve the sole existing Focus Fieldbook lead magnet; no retired water giveaway, ungated safety-to-paid coercion, affiliate activation, emails, public posting or spend.

## Release restrictions

All 35 instructional articles remain **DRAFT / HOLD**. Existing live `/preparedness/` overview is a distinct WordPress page and not proof that the 35 articles are released or independently safety-approved. No WordPress/CMS, navigation, homepage, analytics, payment, product, affiliate, email or social-platform writes occur. All review outcomes remain pending human adjudication, qualified source and safety inspection, full native regression and independent QD.

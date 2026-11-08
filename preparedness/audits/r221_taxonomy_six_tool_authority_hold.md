# R221 — frozen canonical-route and six-tool-source authority (DRAFT / HARD HOLD)

**Scope:** Preparedness Archive integration only, Issue #136. Conversion governance #820 and charter #818. **NO merge, public publishing, navigation/CMS changes, analytics deployment, affiliate activation, social posting, emails or spending.**

## Finding, correction and limitations

Independent handoff QA found two material weaknesses in R220 (draft PR #1608 at `deb4ab4c72b3c183d555399ff65ddb7fc7f00ef3`):
1. `verify_render` compared canonical output to `Library.url_path`, while `Library.url_path` derives the path from the **mutable taxonomy**. A changed taxonomy and regenerations could move every URL while preserving internal consistency.
2. Six tool inputs were counted but not independently pinned: their names, HTML bodies and metadata could be replaced together with generated outputs, outside the 35-article frozen custody.

R221 **adds no article edits**. It pins taxonomy Git blob `15c547bb3018ac182b12a51036389cfa39a59168`, and the six tool body and metadata blob pairs observed on the exact R220 head. It reads all 12 tool files through the existing symlink/traversal-safe read path, checks the exact file set, checks their draft state and section, verifies all 35 taxonomy entries against the original contributor roster, then checks all 41 canonical paths against **independent frozen routes**. The module is pinned by Git blob in the R220 custody audit and invoked before source/build verification, including `--originals-only`. Its route check runs after Library loads and before the render/report verifier. The original seven contributor versions and integrated body/meta SHAs remain untouched.

**TESTED:** `python -I -m unittest discover -s .../preparedness/tests -v` executed in isolated local synthetic module/test fixture: **64/64 PASS**, including 35 independent article route mutations, six tool route mutations, 12 tool body/metadata mutations, topology/baseline/extra/missing/duplicate JSON tests. `py_compile` of the same local module/test bytes PASS. Local files match the exact uploaded GitHub file blobs (checked after upload).

**NOT TESTED:** Native repository `python -I preparedness/tools/validate.py`, `build.py`, full existing suite and real 35-article/41-target/82-output exports remain **NOT EXECUTED** because this execution environment cannot resolve `github.com` to obtain a complete trusted checkout. R220's previous 246 results are author-reported isolated synthetic tests and were **not rerun** here. R221 does not establish external-link reachability, source accuracy, medical safety, quality, browser visibility, end-to-end checkout or WordPress deployment readiness.

**Release blockers unchanged:** three unresolved source-use citation occurrences (2 CDC in article #7, 1 Ready.gov in #20); seven historical shared source-ID collisions; qualified independent QD/source/safety review; native full build/test, browser and WordPress staging acceptance. The guard's only valid success state remains `DRAFT_HARD_HOLD`, never publication PASS.

## Cross-team checks

- Original seven Claude contributors matched R200 exact 40-character commits via GitHub compare; each comparison returned **identical / 0 ahead / 0 behind** on 2026-11-08.
- QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, fixture follow-up PR #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` inspected; no merge or overwrite.
- Homepage Experience 2.0 PR #1607 `9699672ee19837a62ffde3074f273e0890fb1e80` checked, unchanged.
- Grok/Praxxis TASK-008 and dated Drive handoff read. No new authentic Grok Preparedness post/asset identifier or validated destination was established.

## One-offer conversion acceptance docket (UNPUBLISHED)

**Audience:** households preparing essential contact, document and account-location information for loved ones. **Free destination:** existing live, ungated `https://finalvestige.com/preparedness/`, linking to primary Ready.gov/CDC resources; original unreviewed 35 detailed article routes must not be promoted. **Optional commercial candidate:** existing Payhip `Legacy Triage` ($19 listing; seller shown as *Vested Wisdom*). Offer is NOT approved as rights-cleared or reliably deliverable. Its account-access worksheets may hold sensitive information. No password collection by FV or false storage/security assurances.

**Draft CTA only (do not publish):** “Start with the free Preparedness Archive. If you also need a printable place to organize key contacts and document locations, review Legacy Triage separately. It is an optional paid PDF, not emergency advice. Keep completed records and any account details secure.” Disclosure must sit beside link after founder confirms ownership/rights, seller/merchant policies and approved placement.

| OFFER | FUNNEL STEP | BLOCKER | PROPOSED CHECK/EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Free Preparedness Archive | Social post → landing | Actual Grok asset_id, URL, posting time, original rights, usable destination and allowed UTMs missing | Reconcile the *existing* TASK-008 asset inventory against live post/link; no new queue instructions | UNVERIFIED | Grok / Praxxis |
| Free official-source archive | Archive → relevant free guidance | Original 35 articles remain unreviewed; three citation exceptions and seven source conflicts | Keep official-source links available; test no dead/unsafe guide CTA on mobile | LIVE archive observed; original detailed routes HOLD | Preparedness / independent QA |
| Legacy Triage PDF | Free guidance → optional paid offer | Seller/ownership rights, source relevance, privacy/disclosure and permitted link unverified | Review actual licensed PDF and its delivery/refund/contact policies; assess sensitive credential fields and mobile disclosure | Listing visible; merchant acceptance UNVERIFIED | Founder / Commerce |
| Legacy Triage PDF | CTA → confirmed purchase | Checkout, payment, file delivery, receipts/refunds and attribution unverified | Founder-authorized end-to-end real transaction plus delivery and refund-policy review, **no test order without approval** | FAIL / NOT TESTED | Commerce |
| Verified paid orders | Attribution → net revenue | No qualified-human denominator, settled order/refund/fee ledger, confirmed campaign pairing | Compare 7- and 30-day verified first-party `asset_id/utm_campaign` → landing → CTA → confirmed lead (if any) → merchant-confirmed order → fees/refunds | NOT COMPUTABLE | Analytics / Commerce |

**KPI:** realized net revenue per 1,000 qualified-human sessions = `1000 × (settled gross receipts – fees – refunds) / verified qualified-human sessions`, never estimate from outbound clicks, checkout starts or unconfirmed signups. Flag low counts and missing consent/attribution; no new analytics scripts, leads, merchant activity or affiliate claims.

**Release:** DRAFT / HARD HOLD; WordPress-ready drafts only. Revisit after native integration, independent review, commercial verification and explicit founder authorization.

# R195: source custody hardening and human citation-impact workorders

**Authority:** Preparedness Issue #136 only; business coordination #820 and charter #818.
**Status:** BUILT / EXACT-BLOB SYNTHETIC TEST PASS / DRAFT_HARD_HOLD.
**No publication, merchant activation, source approval, or independent QD PASS.**

## Source chain vulnerability and repair

R194 preserved both authentic versions of seven changed historical articles, but its
admission checker accepted body/meta Git blob identifiers supplied by the docket
itself. An altered docket plus substituted valid Git objects could self-rebaseline
source evidence without a deliberate reviewer decision. R195 introduces a
separate, immutable original-vs-observed pinning preflight.

The new preflight hard-pins the R194 docket Git blob
05d393013a952d9d2c92a6e1d9759ca53579ae8b and all **28 body/metadata
blob identities** for 7 changed articles, both frozen and observed versions.
Authenticated GitHub readback matched all seven literal pin rows, all 28 object
identities, and recorded old/new citation counts. No pin can be overridden by
the CLI. Future legitimate updates need a new reviewed docket version.

It also validates source-use explanations for each cited ID, article slugs
and duplicate routes, full draft-only state, conserved historical safety state,
absence of false approval claims, and greater than 90% reading-depth retention.
It prepares deterministic per-article human review workorders containing
old/new citation sequence edits, SHA-256 context excerpt fingerprints,
citation occurrence differences, and changes in source-use reading scopes.

The 8 jerky citation source-ID substitutions remain NOT ALIASED and
UNREVIEWED. Matching total citations never establishes equivalent evidence.
Source claims remain PENDING even after structurally valid input.

**Protected seven-article subtotal: 315 historical / 334 observed citations.**
These are NOT the complete original 35-article / 2000-citation totals.

## Verification / limitations

Local executed test command: python -I -m unittest discover -s
/mnt/data/preparedness_r195/tests -p test_r195*.py -v

**89/89 synthetic Python tests PASS, 0 skipped; isolated-mode py_compile PASS.**
The test module exercises 70 generated negative scenarios plus 19 foundational
and safety/approval cases. GitHub source and tests fetched back exactly match
the locally executed files, Git blob hashes:

- source: e2dd19a5af2783817562a4928c82a9a1929ab83c
- test: 611cec8bbfb683ae596086046e9a79e05c4b05ef

Important: tests are **exact committed code on synthetic fixtures**, NOT an
authentic 35+6 native validation/build, browser acceptance, or human source
reading. A local private checkout still fails with:
git ls-remote ... => Could not resolve host: github.com (exit 128).
The original repository's Python validation/build/36+ tests and its 41
WordPress-ready exports cannot be claimed executed here.

When a complete trusted checkout is available, run the original
preparedness/tools/validate.py, build.py, and unittest discovery with Python -I.
Then run the R194 two-version gate and new
preparedness/tools/r195_claim_impact_preflight.py with --repo and --docket
pointing at preparedness/review/r194/SEVEN-ARTICLE-DUAL-VERSION-OBJECTS.json.
R195 may optionally take --report to write an OFFLINE JSON reviewer artifact.
Exit **2 = structurally admitted DRAFT_HARD_HOLD**, exit **3 = invalid**
(never interpret nonzero as permission to publish).

## Live contributor and QA coordination (2026-11-07)

Each of seven original Claude cluster branches compared IDENTICAL (0 ahead/behind)
against its last recorded exact HEAD:

- Start 2122d856fce9f64887c16df3d52e64be9f59a55b
- Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
- Food f911ff7a655de8d81535ea86ec3d65a49ee76648
- Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17
- Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c
- Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d
- Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2

This does NOT imply the older frozen crosswalk equals current contributor heads:
Food has pre-existing divergence; Health/Hist Field/Hist Food/Hist Home
have pre-existing ahead commits. No branch overwritten or blindly merged.

Independent safety QA draft PR #157 HEAD
7d1ae6b8ef93d10cfb6810987672360885e9c1aa,
synthetic-fixture draft PR #169 HEAD
e9cd7766dac59d47ab467d8945269b9146c2aef5,
follow-up PR #973 HEAD
4d40996a559b0124d74a9bb3bdcd481ad1992aa8
remain open/draft/unmerged. Their shared tests/safety changes require
deliberate reconciliation. Homepage lead PR #1429 HEAD
700e9322306ef09aaf3ee05c9321ed02b3d75ddf is outside this lane.

## Conversion-first: ONE held, plausible audience → offer match

Research-only high-intent topic for Grok/Praxxis: "Could your household
locate identity, insurance and emergency contact records if you had to leave?"
Existing LIVE destination: https://finalvestige.com/preparedness/ contains
official-resource links, NOT the original 35 articles. Proposed authentic
ungated free guide after qualified release: Household Emergency Plan (includes
paper, money and insurance). Optional Family Reunification Card is a FREE
UNPUBLISHED planning/printable tool, not a paid lead magnet or modern medical
guarantee. The retired water freebie is explicitly excluded; the existing
Seven Day Focus Fieldbook remains the only approved email magnet.

**One candidate paid offer:** existing publicly mentioned Legacy Triage
records-continuity PDF. Seller ownership, rights, SKU, PDF, checkout, delivery,
fees/refunds and buyer fit remain unauthenticated: PAID CTA HARD HOLD.
Do not substitute school-pickup/reunification advice as sales copy for a
financial-records product.

Future, non-live free CTA copy after approval:
"Know where your essential records and family contact information are.
Read the free Household Emergency Plan. No email or purchase required."
No free-guide CTA is published from this PR.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer | Step | Blocker | Next acceptance / experiment | Evidence / owner |
| --- | --- | --- | --- | --- |
| Legacy Triage | paid checkout → usable delivery | merchant rights, real SKU, price/fees, download, refunds unverified | authenticate seller, contents and test fulfillment WITH founder authorization before any paid CTA | HARD HOLD / Founder-Commerce |
| Official preparedness gateway | real Grok post → qualified landing | no published matching asset ID, post URL, rights or approved UTM destination | Grok/Praxxis verify TASK-008 inventory, Claude/QA validate staging link and mobile fit | UNVERIFIED / Grok-Praxxis |
| Household Emergency Plan | ungated free reader | 35+6 native build, human source and safety reviews outstanding | source-claim adjudication + 41 real WP drafts, 360/390/768/1440 keyboard/print QA | DRAFT HOLD / Preparedness-QA |
| Family Reunification Card | free optional local printable | 11 source decisions and child/family privacy/printing held | test only synthetic identities; no storage/network leak, keyboard and paper acceptance | HARD HOLD / Site QA |
| Focus Fieldbook (separate) | confirmed direct lead | no Preparedness-specific consent/delivery proof | preserve existing Jetpack list, count only independently confirmed opt-ins | UNKNOWN / Claude-Dispatch |
| Any confirmed sale | realized net revenue | no authenticated orders, refunds/fees or qualified human sessions | reconcile 7/30-day orders and cohorts; calculate net per 1000 qualified sessions with small-sample caveat | NOT COMPUTABLE / Commerce-Analytics |

Source-to-funnel contract: real immutable Grok asset_id and utm_content /
utm_campaign → qualified human landing → relevant CTA click → confirmed
consented lead where applicable → independently verified paid order or
affiliate payment → fees and refunds → realized net revenue.
Clicks, follows, pageviews and attributed sessions are NOT orders.

Grok retains YouTube/TikTok/other content and Mini Museum priority;
Praxxis independently reviews TASK-008. The existing Google Docs TASK-008
and dated handoff were read this run without writes. Claude owns site/analytics.
No new measurement script, public release, CMS/navigation/homepage edit,
email/social action, paid service, merchant activation or spending occurred.

## Decision

**DRAFT_HARD_HOLD**. Authentic build of 35 original articles and six tools,
all independent source and food/medication review, full privacy/accessibility/
printing review, independent QD and founder approval remain mandatory.

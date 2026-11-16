# R404 — E395 ZIP member-identity preflight and conversion acceptance

**Scope:** Preparedness-only, read-only Article #11 source custody; GitHub Issues #136, #820 and business charter #818. **DRAFT / HARD HOLD / NOT FOR PUBLICATION.** No authentic ZIP transfer, human food-science clearance, site build, merchant checkout or QD PASS is asserted.

## Implemented source-safety change

R403 bounded original filesystem reads and rejected external symlinks/hardlinks. R404 adds a fail-closed ZIP-member identity preflight:

1. Directory entry names with trailing slash no longer bypass Unix mode validation. Symlink/regular-file disguised directory entries and directories with unexpected content fail.
2. Canonical aliases are checked across files **and** directories: NFC-unstable Unicode, Windows devices, trailing dot/space components, invisible Unicode controls, non-portable punctuation, NFKC/casefold duplicate identities.
3. File-as-parent-path collisions are rejected, including case-insensitive spellings.
4. More than 200 listed archive members now rejects **before** any member decompression, retaining existing bounded read, file-length, ratio, archive/article SHA-256 and membership checks.
5. Structural failures remain FAIL. Structural PASS always means **eligible=false, release=DRAFT_HARD_HOLD, qualified_food_safety_review=NOT_GRANTED**.

Only the prior R402/R403 custody checker, a new synthetic regression file and this note change. No editorial source text, source IDs, outbound URLs, article canonical URL, risk status, product or WordPress export is modified.

## Verification contract

- New adversarial Python suite **68/68 PASS** and inherited R403 suite **45/45 PASS**; available local combined **113/113 PASS**; Python byte compilation PASS.
- Exact committed source Git blob **26921d275a73676378ad69484f66c7c56f7824b2**, exact test Git blob **f22c10b2ec910e7611050701fbddea4252bf1bf4**; both matched the locally executed files.
- Original contributor pins: seven Claude and two Shelter branch compare operations **9/9 identical**, ahead=behind=0.
- Independent QA #157 **7d1ae6b8ef93d10cfb6810987672360885e9c1aa** open draft; its publication safety test patch inspected. Fixture PR #169 **e9cd7766dac59d47ab467d8945269b9146c2aef5** open draft; its source-mutation test still needs dependent unmerged repair #2205 **bbcf1859768624c611df4abadc564c18247cf32a**.
- Homepage lead PR #1689 **f55c36b6598eec558dd8bb24e4c8988becc51be0**, unchanged.
- Preserved pinned original inventory: **35 articles, 203 source IDs, 280 original source occurrences, 17 shared exact-URL groups, five original source disputes and nine unselected Shelter manuscript forks**.
- Authentic original E395 ZIP **NOT RECEIVED**. Editorial E396/E397 checks reported in Issue #136 do **not** replace receiver-side verification. E397 new Article #11 HTML bytes also not received.
- Complete native validate/build **NOT EXECUTED**: full authenticated checkout unavailable, local git ls-remote DNS resolution failed. Genuine private WordPress and preview exports **NOT VERIFIED**. Food, emergency, child-privacy and independent QD **NOT GRANTED**.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (DRAFT ONLY) | PASS / FAIL | OWNER |
|---|---|---|---|---|---|
| ONE existing FV-owned Preparedness toolkit/pack | qualified reader → verified checkout → delivered paid order | No authenticated payable rights-cleared Preparedness SKU, merchant listing, delivery, refunds or fees | Founder/Commerce read-only audit of one already-existing well-matched SKU; paid CTA disabled; exclude retired water or unrelated sellers' listings | HOLD, no confirmed order | Founder/Commerce |
| One genuinely already-published family-contact Grok asset → free public Archive | immutable asset_id + permitted URL/UTM → signed-out mobile landing → official Ready.gov checklist | Published on-topic asset ID, rights, hook, mobile and allowed destination UNVERIFIED | Praxxis independently audits one real existing asset with Grok via TASK-008; never edit creator queue or post. Draft free-only CTA "Start With Trusted Preparedness Resources" remains unpublished | UNVERIFIED traffic and CTA | Grok/Praxxis; Site QA |
| Existing free guide → optional printable Tool #104 | ungated family-contact practical download | Child privacy, school reunification, emergency advice, accessibility/no-JS printing not independently approved | Maintain private draft; qualified QD and real print/mobile evidence before linking; Tool #102 separate | HARD HOLD | Preparedness/QD |
| Human campaign sessions → relevant CTA → confirmed lead (where applicable) → merchant-confirmed paid order → realized net | 7/30-day qualified-human cohorts net of refunds/fees | Missing trustworthy attributable sessions, provider-confirmed lead, actual merchant settlements, refunds and fees | Claude/Commerce use existing consent-appropriate approved measurement, no duplicate scripts; establish settled transaction matching first | Net revenue / 1,000 qualified humans NOT COMPUTABLE, not zero | Claude/Commerce/Founder |

## Release boundary

Draft review only. No merge, publication, WordPress/CMS/navigation write, Focus change, social post, email send, paid service, analytics pixel, merchant or affiliate activation, product creation, spending or false scientific/QD approval.

**Next:** secure the authentic original E395 ZIP via approved private transfer, independently hash and inspect with R404, obtain named qualified decisions on household jerky scope / five original disputes / nine Shelter forks, run native 35-article validate/build and authentic private export audit, then seek independent QD and founder release approvals. Cross-reference #136 and #820.

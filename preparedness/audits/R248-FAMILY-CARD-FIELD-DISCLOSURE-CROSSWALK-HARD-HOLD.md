# R248 — Family-card field-level source / reader-disclosure crosswalk (UNAPPROVED)

**2026-11-09 PT · Issue #136 · conversion #820 · charter #818. DRAFT / HARD HOLD.**
All work is Preparedness-only; original Article #15, Tool #104, 35 manuscripts, six tools, canonical URLs, source records and safety states are unchanged. No public publishing or WordPress/CMS writes.

## Reproducible, bounded finding

R246–R247 established that the Tool #104 minimal-card wording omits identifying fields and that its no-JavaScript claim conflicts with the hidden form and blank paper-card fallback. R248 converts this into a deterministic **field-by-field crosswalk**, rather than treating the term "minimal" as self-evidently privacy-safe.

Authenticated original Git blobs: Article #15 body `8ac8bd7dba3be15d477c15737e54d83364d72527`; Tool #104 body `be8698ac5d020476ff649d85813810e2000c6f98`; Tool #104 metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`; `reunion_card.js` `b1a09b1eda1ae26f081de65b400a37bc19538035`; `shelter_common.js` `efe1c7910d99437e3687621dabab8ce55dc24fd4`.

### Output when all 13 fictitious fields are populated

| Printed label | JS input | Full | Minimal | Unresolved disclosure |
|---|---|---|---|---|
| Household | hhName | Yes | **YES** | Not in intro/checkbox "only" enumeration |
| Phone | hhPhone | Yes | **YES** | Not clearly distinguished from out-of-area phone |
| Out-of-area contact | outName | Yes | Yes | Existing description |
| Out-of-area phone | outPhone | Yes | Yes | Existing description |
| Meet first at | meet1 | Yes | Yes | Existing description |
| If not, meet at | meet2 | Yes | No | Omitted in minimal |
| School or childcare | school | Yes | No | Omitted in minimal |
| Reunification plan | schoolPlan | Yes | No | Omitted in minimal |
| Pick-up reminder | pickup | Yes | No | Omitted in minimal |
| Caregiver | careName | Yes | No | Omitted in minimal |
| Caregiver phone | carePhone | Yes | No | Omitted in minimal |
| Communication needs | access | Yes | No | Omitted in minimal |
| Reviewed | reviewed | Yes | Yes | Existing checkbox disclosure |

Actual original JS prints **13 populated user-entered fields in full mode**, **6 in minimal mode**, with **7 suppressed in minimal**. It also adds the fixed minimal-mode line **"Kept in our written plan at home."** without evidence a household has created such a plan. Field exclusion is conditional on entries having values; an empty value generates no row.

The authored Tool #104 intro states the minimal version prints **only** the out-of-area contact, a phone and first meeting place; the checkbox adds review date. Neither clearly discloses the extra **Household** and **household Phone** entries. Tool #104's unconditional `not sent or saved` and Article #15's on-device assurance require genuine browser/session/WordPress and print testing. These findings **do not establish exfiltration**.

## Added executable gate

New Python source `tools/r248_family_card_field_crosswalk_hold.py` authenticates five original blobs, rejects duplicate JSON keys/nonfinite metadata, preserves exact 13-label/14-call-site (Reviewed twice) code mapping, verifies conditional minimal branch, validates original reader claims and enforces draft/pending states. Returns a source-hash-only receipt plus per-field review matrix, all approval flags **FALSE**. Its `audit` is invoked through R220's cryptographically pinned loader **before** WordPress draft rendering and rehashed at the end. No runtime user inputs or personal data are read.

**Actual execution in this run:**
- **49/49 locally executed isolated Python regression tests PASS** + `python -I -m py_compile` PASS on the local implementation; the committed GitHub code differs in comments/path context, so **do not** call the Python tests exact Git-object reproduction.
- **93/93 V8 runtime assertions PASS** executing the authentic original GitHub-read `reunion_card.js` and `shelter_common.js` with wholly fictitious fields (13-field/full/minimal/empty/isolated checks, warning signals). Authenticated original source blob IDs matched the pinned versions.
- Authentic HTML/metadata checked separately through GitHub connector for the three exact reader-facing copy witnesses and the 13 print-field mappings; this is **not** a native complete Python audit.
- Fresh GitHub compare against all seven original Claude branches: **7/7 IDENTICAL** to R200 exact heads.
- Independent QA PR #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and fixture PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` are draft and unmerged; inspected, unchanged. Homepage lead #1689 remains outside scope.
- Full native `python -I preparedness/tools/validate.py`, `build.py`, inherited suite, all 41 WordPress draft exports and signed-out JS-on/off/print/mobile/storage tests: **NOT EXECUTED**. Container `git ls-remote` failed `Could not resolve host: github.com`. No independent QD PASS.

## Release and safety acceptance (still held)

Editorial/QA must adjudicate the actual 6-field minimal contract and the misleading no-JS and unconditional home-plan/privacy statements. Decide whether to remove household identifiers in minimal **or** update the disclosure with demonstrable user intent; no decision or copy modification is made here. Review child-contact disclosure, local school pickup scope, 11 unsigned proposed text changes, independent source safety, mobile screen-reader/print and retention/network behavior. The 32 shared-source groups and three disputed original citation occurrences (Article #7 CDC ×2; Article #20 Ready.gov ×1) remain unresolved. Article #7 water safety remains separate.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Acceptance / experiment (draft only) | Evidence | Owner |
|---|---|---|---|---|---|
| Existing free Preparedness Archive / held family-card guide | Grok creator hook → existing free landing | No verified published matched creator asset_id, hook, rights, signed-out mobile destination | TASK-008 read-only identify authentic video and destination; no social assignment | UNVERIFIED | Grok / Praxxis |
| Free Article #15 → printable Tool #104 | Reader's privacy expectations → usable printed card | "Minimal only" copy omits Household + Phone; no-JS and local-storage guarantees unresolved | Independent editorial decision, user-facing field disclosure, real browser + print tests | **SOURCE-LEVEL HARD HOLD**; 93 V8 checks do not substitute browser | Preparedness / Editorial QA |
| Existing provisional Legacy Triage owned PDF | Free guide → optional paid practical pack | Estate/incapacity fit, rights, file privacy and delivery unverified; not an approved preparedness toolkit | Founder/Commerce inspect complete PDF, purchaser fit, terms/privacy and authorization; draft CTA only after approval | NOT APPROVED | Founder / Commerce |
| Authorized merchant offer | CTA → paid order | Actual checkout, delivery, refunds/fees unverified | Authorized real merchant acceptance test and independent confirmed order | NOT TESTED; clicks ≠ paid sales | Commerce |
| Known Grok asset cohorts | Qualified-human landing → click → confirmed lead → settled paid order | Asset IDs/UTMs, consentful lead and settled purchase data missing | 7/30-day reconciliation and tiny-sample bounds; no duplicate scripts | **NET REVENUE / 1,000 QUALIFIED HUMAN SESSIONS NOT COMPUTABLE** | Praxxis / Claude analytics / Commerce |

Provisional nonactivated **draft** CTA for future consideration only: "Get the free household communication guide" → qualified free guide; accompanying clear explanatory text must tell the user what information appears on the card and when it may be carried. Optional paid pack must not appear unless independently approved and actually purchasable. No retired water freebie, manipulative scarcity or misleading safety promise.

**Nothing merged, published, promoted, emailed, posted or purchased.** No merchant links, analytics scripts, homepage/navigation changes or spend. Preserve founder approvals and Grok ownership.

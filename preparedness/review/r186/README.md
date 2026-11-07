# R186 — whole-archive native admission preflight (DRAFT HARD HOLD)

**Scope:** Preparedness Archive Issue #136 ONLY; conversion handoff #820 / charter #818. Exact pinned parent: R185 PR #1366 commit \`1f457168a94f69782cdea2ffced0d5f483a362cd\`. Do not merge, release or publish from this receipt.

## Substantial change

The previous R176 orchestrator checked native validation/build/36+ tests plus R174/R175 article gates, while R184/R185 subsequently introduced separate protection for 35 original article WordPress drafts and six companion tool exports. R186 combines the **41 original draft source-body pairs** and **12 mandatory steps** in **ONE disposable checkout**:

1. Original native \`validate.py\` — requires actual zero-error output.
2. Original native \`build.py\` — requires >=35 WordPress and preview outputs.
3. Actual Python unittest discovery — >=36 nonskipped passing tests.
4. R174 rendered 2,000 citations / 385 article-source uses + byte comparison.
5. R175 original article link/route graph + draft export comparison.
6. R177 two safety-critical wording and export preservation contracts.
7. R178 all 35 original safety-state admission contract.
8. R179 original 35-article source crosswalk.
9. R180 **21 unresolved** Family Card and jerky source/scope tickets (11 + 10, not additive with other dockets).
10. R182 QA #157/#169/#973 semantic custody (including R181 contributor evidence).
11. R184 whole 35-article build-report/WordPress review-truth gate.
12. R185 six-tool original-source, **67** source-use and **173** citation-custody/privacy gate.

Fail closed on missing gates, missing body/metadata, duplicate canonical, accidental published status, altered source snapshot, zero-exit "success" from intentional-HOLD gates, malformed JSON, any nested false publication/QD/commerce claim, or required corpus/ticket count drift. Preserve reading depth via R184 and source use via R174/R179/R185. A valid structural packet is **DRAFT_HARD_HOLD with exit code 2**, not PASS or publication permission.

Run from a **trusted complete exact checkout**, not a transient generated ZIP:

\`\`\`sh
python -I preparedness/tools/r186_whole_archive_preflight.py --repo . --timeout 300
\`\`\`

No WordPress writes, navigation, analytics changes, purchases, posts, email sends, or edits to article bodies/tools/source metadata. The runner copies inputs into a temporary directory; it executes repository code and is **not a security sandbox against malicious code**. Its source snapshot is checked before and after. Output hashes retain program receipts without exposing personal data.

## Verified execution vs outstanding

**BUILT / LOCALLY TESTED IN SYNTHETIC FIXTURES:** 83/83 Python \`unittest\` cases PASS with 0 skipped; \`py_compile\` PASS. Includes 72 distinct fail-closed adversarial cases across nine mandatory receipt types (unexpected return codes, non-JSON, invalid states, nested fake sale/QD, reported errors) and complete 41-item synthetic source/metadata census checks. Local gate \`git hash-object\` = \`a4af3aa8214938f04a5c47cf688ae2564a95cb4f\`; test blob = \`dbe83e58ce1926454fa9d2746dcaffd3dbda0709\`. These must match actual committed blobs (verified through connected GitHub).

**UNVERIFIED:** full native validator/build/full suite against authentic 35 original articles + six original tools. Local \`git ls-remote\` failed with \`Could not resolve host: github.com\`. On intentionally incomplete local checkout R186 returns JSON \`INVALID_HARD_HOLD\`, exit 2, with exact missing module; no fabricated native test report or WordPress preview claim.

**Source/QA HOLD:** historical approved labels (2), historical not-required labels (4), 21 indexed article source-review tickets, 58 tool-source relationship reviews, contributor independent PR reviews, applicable food/medication/utility safety, privacy/printing/keyboard/network browser testing and independent QD. The 21 and 58 may overlap other source-review counts; do not sum across categories as distinct claims.

## Fresh contributor coordination (connected GitHub, 2026-11-07 UTC)

All seven Claude branch refs compare **identical** with their recorded SHAs, each 0 ahead/0 behind: Start \`2122d856fce9f64887c16df3d52e64be9f59a55b\`, Food \`f911ff7a655de8d81535ea86ec3d65a49ee76648\`, Shelter \`5daeaf2dd5ab71806a6b73c91edfb1d8df5da976\`, Health \`d5ef5bafd68361434dd1cc9209915b8e8a4eaf17\`, Historical Field \`4e5caf812727953aa45e3bda2d382f2c67b6a09c\`, Historical Food \`67e116e536c7410bed30f8f3b1bb8c166f3c223d\`, Historical Home \`7504a5f099594d635e3dd7332a33a2e1346c43a2\`.

Independent PR #157 head \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`, #169 \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`, follow-up #973 \`4d40996a559b0124d74a9bb3bdcd481ad1992aa8\`: all open drafts, unchanged. \`test_preparedness.py\` collision remains under controlled R182 semantic custody; no blind merge. Current EX2 home lead draft PR #1372 head \`c2544b8407bc612b758d780c0036aad428961fed\` and Apollo #1369 head \`eac7b2bff411066f0d115c5ee8eac9d671cc40d0\` inspected, not changed.

## CONVERSION FIRST — OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / step | Blocker | Draft acceptance change | Evidence / state | Owner |
|---|---|---|---|---|
| **Existing paid preparedness/family continuity pack → paid order** | No authenticated rights-cleared FV SKU or merchant order/delivery/refund record | Publicly found a candidate \`Legacy Triage\` Payhip listing: $19 / 9-section instant PDF, notably financial/record continuity, **not a school reunification safety pack**. Authenticate seller ownership, current product contents, licensing, accurate scope, actual merchant acceptance, safe download, refund and fees **before any CTA**. | **CANDIDATE ONLY / NO SELLABLE FV SKU VERIFIED**; https://payhip.com/b/n1RhV | Founder / Claude commerce |
| **Grok social → free authoritative guide** | No matching published caregiver \`asset_id\`, placement, UTM and destination in TASK-008 | After Grok/Praxxis records actual media, test \`utm_source=actual_platform\`, \`utm_medium=organic_social\`, \`utm_campaign=preparedness_pilot_2026_11\`, \`utm_content=actual_asset_id\`. No spoken CTA or publishing here. | **UNVERIFIED** | Grok / Praxxis |
| **Free Household Emergency Plan → optional Family Reunification Card** | 11 unresolved tool source relationships, private data on printed card, guide withheld | Draft CTA: “Plan who can pick up your child when phones are down. Start with the free Household Emergency Plan.” Then optional *free* card, visible privacy/lost-card warnings; no emergency guidance behind signup. Staged test 360/390/768/1440, keyboard, fake data, print, outbound network. | **DRAFT HARD HOLD**; verified live /preparedness/ is a public **official-source gateway only**, not full original guide | Preparedness / independent Site QA |
| **Optional opt-in → qualified lead** | No guide-specific consent/delivery proof | Keep existing Seven Day Focus Fieldbook as sole lead magnet at /focus/; only offer if intent matches and confirmation/delivery verified. | **NOT VERIFIED** | Claude / Dispatch |
| **Verified paid orders → net revenue per 1,000 qualified sessions** | No verified first-party qualified human sessions or payment/refund/fee data | Use existing #820 measurement, 7/30-day cohorts; separately count CTA/checkout/lead vs confirmed sale. | **NOT COMPUTABLE** (not zero) | Commerce / Analytics |

**No release:** A staged 41-item preflight proves only structural custody, not that claims are safe, human-reviewed, live, or commercial. Product link is a research candidate, not an approved affiliate or FV purchase CTA. Do not revive retired water guides, introduce a replacement freebie, auto-enable sales, or modify TASK-008 or Grok's queue.

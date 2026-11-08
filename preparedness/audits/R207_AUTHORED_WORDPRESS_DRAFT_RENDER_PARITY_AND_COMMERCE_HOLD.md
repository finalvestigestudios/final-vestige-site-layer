# R207 — Authored body ↔ WordPress draft render parity | DRAFT / HARD HOLD

**Scope:** Preparedness Archive GitHub issue #136 only, conversion coordination #820, charter #818. Independent review-only stacked draft on R206 #1516, initial parent `4d803d497a22c71bf6ac66866676994c31f306ff`. **No original article, metadata, source register, page, permalink, contributor branch, WordPress, navigation, homepage, tracking, affiliate, merchant, email, social, or publishing write.** No QD pass.

## Why this lift

R200–R206 verified the seven contributor branches, original 35 article positions, source records, 1,971 original citation occurrences and draft route inventory. Those checks did **not** independently prove that a generated WordPress draft retains the substantive reading text, warnings and citation **occurrence sequence** of its frozen authored HTML.

Introduced `preparedness/tools/r207_wordpress_render_parity_gate.py`, a separate offline gate. Given (1) Git-verified frozen R200 article bodies/metadata at their original branch commits, (2) a locally generated 35-article WordPress HTML export, (3) the corresponding 35 preview HTML files and (4) the native build-report, it checks:

- Exactly 35 original body/metadata pairs; exact Git blob IDs and sizes, seven fixed source origins, unique canonical article paths. No extra/missing article in the expected 35.
- A deterministic plain-text comparison of **each full authored article body** to each exported `.pa-body`, preserving text from paragraphs, headings, lists, notes, tables and safety-warning prose. Citation markers are removed from the comparison, but separately checked; crosslink labels must remain as written. The normalized full prose SHA-256 is recorded per article. This is stronger than a minimum word-count heuristic, but not a substitute for visual QA, semantic image-alt review or source accuracy.
- The emitted `sup.pa-cite` footnotes must match the authored citation-occurrence ordering (not merely unique source counts), and the native build-report must contain the identical ordered first-use source list.
- The generated WordPress block must have one `wp:html` wrapper, one matching article slug/section/track, consistent canonical/free `Article` JSON-LD without `datePublished`, an explicit **Draft: not public** warning and **Safety review pending** notice, plus the statement that human safety review is required. Both WP and standalone preview files are independently checked.
- Reject accidental scripts or embedded active content in the article body, duplicate/foreign routes, drifted original Git identities, missing source tokens, missing citation numbers, rendered text loss, changed source ordering, fabricated approvals or revenue. **Successful structural examination intentionally remains DRAFT_HARD_HOLD (exit 2); missing or invalid evidence INVALID_HARD_HOLD (exit 3).** The tool does not publish or patch CMS.

## Exact-code tests executed

Local `python -I -m unittest discover -s /mnt/data/fv-r207/preparedness/tests -q`: **161/161 PASS** (synthetic fixtures); `python -I -m py_compile ...`: **PASS**. Four separate 35-article mutation matrices cover (a) changed WP prose, (b) changed preview prose, (c) dropped citation occurrences and (d) changed frozen body OIDs, plus 21 other unit tests of status, URL, source ordering, JSON-LD, draft markings, malformed markup and fail-closed CLI. Local Python code/test exact Git blob identities equal GitHub committed files:

- `r207_wordpress_render_parity_gate.py` — `7f09b81430f2fe457122cd09c92249fa894f760a` (15,493 bytes).
- `test_r207_wordpress_render_parity_gate.py` — `0fb35466ad67ba270fb20a1533c549d5151e1687` (8,501 bytes).

**NOT EXECUTED:** original 35 bodies through this parity gate, authenticated entire source-register reconciliation, native `preparedness/tools/validate.py`, native `build.py`, existing repository tests, all 41 export targets, browser/keyboard/print/device acceptance, human source review or independent QD. Local `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` still fails: `Could not resolve host: github.com`. The checked-out seven original contributor trees and native output were unavailable to local execution. Never infer a real 35-for-35 rendered parity pass from synthetic tests.

On a trusted complete checkout containing all seven pinned contributor commits and after independently reconciling native build conflicts, execute:

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r207_wordpress_render_parity_gate.py --repo . --report /tmp/fv-r207-render-parity.json
```

Review the actual fail-closed report. **Exit 2 is only draft custody, not publication approval; exit 3 blocks any integrity claim.**

## Branch and independent-QA handoff evidence — November 7 PT

All seven original Claude contributor heads were checked directly against current GitHub ref commits:

- start `claude/prep-start-bbfeb8` = `2122d856fce9f64887c16df3d52e64be9f59a55b`
- shelter `claude/prep-shelter-5e1e0e` = `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- food `claude/prep-food-ccdc55` = `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- health `claude/prep-health-837444` = `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- historical field `claude/prep-hist-field-9db767` = `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- historical food `claude/prep-hist-food-b81f19` = `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- historical home `claude/prep-hist-home-0e0e38` = `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Actual PR patches inspected: independent safety #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` removes unsafe main-breaker drill and strengthens refrigerated-medication qualifications; independent synthetic fixture isolation #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` and follow-up #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` stop source tests writing into the real repository's fragment directory. These PRs **remain independent and unmerged**; overlapping tests need deliberate integration. Homepage lead PR #1522 at `5220131734747879879fe77893056065a5aa8f2e` checked for branch isolation, untouched.

Outstanding human source review: **three original citation occurrences** not explained in per-article `source_use` (Article #7 two `cdc-find-clean-water`; Article #20 one `start-ready-plan`); **seven historical multi-origin source ID collisions** including distinct jerky-source identities. This parity gate does not resolve their evidence, safety or historical interpretation.

## Conversion-first lane — one specific audience/offer, no activation

**Audience/topic:** household document and family-contact continuity before evacuation or a household crisis. **Public free destination:** the existing live `https://finalvestige.com/preparedness/` currently links to an official FEMA emergency planning checklist (free and not gated); original `household-emergency-plan` remains unpublished. **Optional product candidate:** existing public `https://payhip.com/b/n1RhV` "Legacy Triage", listing observed November 7 PT at **$19**, described as an instant PDF (~580 KB) with nine sections for contacts, document locations and financial handoffs. This is a family-administration continuity pack, NOT an emergency survival guide, medical resource, legal instrument or substitute for official free instructions. Public product-listing visibility is **not proof** of FV seller rights, current merchant acceptance, successful payment, actual delivery, license, refund policy or net profit. No purchase CTA or offer status changed.

**Draft CTA only, not published:** "Start with the free emergency-planning resources. If you also want a separate fill-in record of essential contacts and where household documents are kept, explore the optional Legacy Triage PDF. Keep sensitive completed copies secure. The paid template is not required to access emergency guidance."

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Public Archive → official FEMA planning guide | Original FV long-form Household Emergency Plan still on safety/source hold | Match social intent to already-live official link; do not link unpublished guide | **LIVE public Archive; original FV article HOLD** | Preparedness editorial + QA |
| Grok evacuation/records asset → Archive landing | No verified actual published matching Grok immutable asset_id, post URL, rights, allowed CTA placement and UTM | Reconcile only existing TASK-008 board / handoff with Grok and Praxxis; do not replace queue | **UNKNOWN**; no attributable sessions | Grok / Praxxis |
| Free guide → optional Legacy Triage | $19 Payhip listing publicly visible, but ownership/rights/current checkout/fulfillment/refunds/device accessibility not tested | Founder/Commerce authorizes private test; read-only rights/terms and browser mobile/keyboard review first | **LISTING OBSERVED; COMMERCIAL HARD HOLD** | Founder / Commerce, independent Site QA |
| Optional free Family Reunification Card | Original draft, child-data privacy and staged printable acceptance not cleared | Keep private; synthetic entries only, no collection | **HARD HOLD** | Site QA |
| Verified human landing → relevant CTA → lead → paid order → fees/refunds → net | No matched Grok asset_id, qualified-human session denominator, verified orders or settlement ledger | Use existing privacy-approved measures, reconcile seven/thirty-day cohorts with tiny-sample disclosure | **NOT COMPUTABLE** (no sales inferred) | Commerce / Analytics |

**Reader engagement acceptance (staging only):** at 360/390/768/1440px ensure matching headline/source/CTA context; official links work and are freely accessible; paid option separately labeled with price, product type and clear distinction from safety guidance; no intrusive overlays, no mandatory email; keyboard/tab/contrast/print review; destination matches actual creator asset and platform-permitted link placement; UTM parameters only after Claude's duplicate-tracker/privacy review. Never equate a CTA click, email signup or link tap with a paid sale. Qualified-human sessions → independently confirmed paid orders → refunds/fees → realized net revenue; net revenue per 1,000 qualified human sessions not computable without valid data.

**BUILT / EXACT-CODE SYNTHETIC TESTED / REAL NATIVE BUILD NOT EXECUTED / DRAFT HARD HOLD / NOTHING LIVE CHANGED.**

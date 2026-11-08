# R225 — Authenticated R221/R222 gate execution / Preparedness HOLD

**Date:** 2026-11-08 PT. **Scope:** Preparedness Archive source/citation and 35-article/41-export integration gates only. Governing issues **#136**, **#820** (charter **#818**). Inherited exactly from R224 **PR #1634**, head `10207822c7e03dbc407dd015321d2da23ef55d27`. No original article, safety label, taxonomy, source text, page, WordPress route or commerce implementation changed.

## New structural finding

R224 fixed a module-cache ambiguity in the authenticated WordPress builder, but its loaders for the independently frozen **R221 taxonomy/tool route authority** and **R222 producer/source bundle gate** still called `importlib.util.spec_from_file_location(...).loader.exec_module(...)` **after** reading and validating the Git blob. That loader can read from disk again, allowing the code executed during source/safety verification to differ from the bytes pinned at preflight if the file is replaced between operations.

### Fix

The R220 custody gate now uses a single `load_frozen_gate` implementation that:
- Requires an exact lower-case 40-hex source receipt and the original no-symlink/no-traversal file reader.
- Reads and checks **source bytes before evaluation**, compiles those same bytes into a fresh private module rather than importing from a mutable filesystem path, and checks the same source identity **after** module initialization.
- Requires callable `verify_authorities` and `verify_routes` for R221 and `check_bundle` for R222.
- Uses neither Python's cached module imports nor global `sys.path` changes. Existing builder binding from R224 remains unchanged.
- Maintains `DRAFT_HARD_HOLD` / `INVALID_HARD_HOLD` only. It is an integrity safeguard, not a sandbox for malicious code, and it does not certify medical or source accuracy.

## Evidence and limits

**68/68 Python regression tests PASS** locally against an isolated, function-equivalent copy of the new binding implementation; 48 are distinct mutation cases. Additional tests cover module-cache poisoning, symlinked gate/directory paths, missing/changed files, malformed receipts, required-API failure, syntax/encoding errors, execution-time file substitution, and HOLD-only states. `python -I -m compileall` PASS. The committed test file's Git blob `e5dce422a22b9bdcf092192ab72ca835ebdb3ee4` was independently matched to the exact locally executed test file using `git hash-object`.

**Critical boundary:** The complete authentic R220 module and all sources were not recreated in the container; the 68 results are **isolated synthetic** proof of the new binding behavior, NOT a native integration run. Container `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` fails DNS (`Could not resolve host: github.com`). The complete `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v` and `python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness` remain **NOT EXECUTED** against original checkout. All 35 article bodies, 6 tools, 41 individual exports and 82 WordPress/preview HTML outputs retain HOLD pending real native QA.

R224's source exceptions remain **two** `cdc-find-clean-water` references in Article #7 and **one** `start-ready-plan` reference in Article #20, plus seven historical source-ID collisions. These were neither edited nor approved. Source reading, editorial depth, water/food/medical/CO safety checks and independent QD remain mandatory.

## Independent coordination (unchanged/not cherry-picked)

- Seven original Claude heads were checked using GitHub compare endpoint and found `identical` (0 ahead / 0 behind) to their frozen identities: start `2122d856`; shelter `5daeaf2d`; food `f911ff7a`; health `d5ef5baf`; hist-field `4e5caf81`; hist-food `67e116e5`; hist-home `7504a5f0`.
- Independent safety QA **PR #157** `7d1ae6b8`, food synthetic-fixture **#169** `e9cd7766`, follow-up **#973** `4d40996a`, homepage lead **#1620** `d20027e1` checked as open draft, unchanged. R225 does **not** merge or cherry-pick their code.
- One **potential public citation mismatch** identified from a fresh indexed view of `https://finalvestige.com/preparedness/`: the “Power outages: safe first decisions” card seems to display NCHFP curing/USDA jerky source labels where FEMA outage guidance would be expected. This is **SUSPECTED, NOT DIRECT HTML VERIFIED**, since the follow-up page fetch returned a cache miss. Escalate to independent site QA and verify exact DOM/href mapping before proposing any separate public change; **do not** modify production here.

## Conversion-first, draft-only acceptance (no CTA activation)

**One high-intent topic:** Emergency contact and essential-document organization during evacuation or sudden caregiver unavailability. **Authentic live free destination:** `https://finalvestige.com/preparedness/`, official-agency “Create a household emergency plan” card. Original in-depth articles and tool exports are not cleared for public campaign routing.

**ONE provisional product, not approved:** `https://payhip.com/b/n1RhV` publicly describes **Legacy Triage**, a **$19** 9-section, print-ready PDF with accounts/logins and documents. Listing establishes discoverability and a stated download format, **not** FV ownership/rights, merchant acceptance, actual settlement/delivery, refund handling, secure storage/credential practices, or a sale. No button or affiliate link authorized.

**Disabled draft CTA text:** “Start with the free official household-planning checklist. For families who also need a printable emergency contacts and important-documents organizer, a separate optional paid resource may be reviewed for inclusion. Keep completed records private and store access details securely.” Do not render or activate until product, claims, privacy and checkout approval.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok published asset → free official checklist | No authenticated platform post, `asset_id`, destination or consent/rights record | Match existing TASK-008 post URL, factual hook, posted date, mobile tap URL and `utm_campaign`/`utm_content` | **NOT VERIFIED**; do not invent attribution | Grok / Praxxis |
| Free public card → original Archive guide | Original source/citation and independent safety review incomplete | Native build + source crosswalk + 41 routes / 82 outputs + qualified review | **HARD HOLD** | Preparedness / QA |
| Free guide → optional Legacy Triage | Seller authorization, product contents/credential security and pricing disclosure not independently accepted | Founder/Commerce inspect complete PDF, merchant rights and privacy details; approve truthful optional CTA | **NOT APPROVED** | Founder / Commerce |
| Product CTA → paid purchase/delivery | Checkout, mobile accessibility, card receipt, PDF download and refund path untested | Authorized 360/390/768/1440px + keyboard + test order and refund/fee reconciliation | **NOT TESTED** | Commerce |
| Qualified human visitors → realized net | Reliable campaign denominator, paid orders and refunds/fees absent | 7/30-day asset cohorts, confirmed human landing→click→verified lead (if any)→merchant-paid order→net settlement | **NOT COMPUTABLE** | Analytics / Commerce |

Primary metric, **only when both inputs verified:** `1000 × (settled gross paid revenue − refunds − platform/payment fees) ÷ qualified human sessions`. Outbound clicks, affiliate referral clicks, signups, checkout starts, views and followers are **not sales**. Mark tiny denominators and missing attribution. Use existing approved analytics only; no duplicate scripts.

**Release:** BUILT / SYNTHETICALLY TESTED / DRAFT_HARD_HOLD. No WP, CMS, navigation, social asset, Grok queue, email, analytics, merchant, affiliate, spending, production merge or publication changes. Founder has release authority.

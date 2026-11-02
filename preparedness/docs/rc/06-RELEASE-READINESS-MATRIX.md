# Release readiness matrix

**Overall: HOLD. Release authorization NOT GRANTED.** Status values: PASS (evidence meets the criterion), FAIL (evidence shows it is not met), BLOCKED (cannot proceed without a human or an unmade decision), NOT TESTED. "Basis" says what supports the row: machine test, verified source (machine-read), browser run, independent reviewer, founder decision. A machine test is never a review. If any publication requirement is unmet the overall state is HOLD even when every automated test passes.

## A. Publication requirements (from the sprint brief)
| # | Requirement | Status | Basis / evidence | File |
|---|---|---|---|---|
| 1 | Safety and editorial review of consequential material | **BLOCKED** | None recorded. 29 articles + 6 tools `pending`; 2 articles `approved` only by an unscoped one-word chat reply (qualified) | 03 register, 04 X-2/X-3 |
| 2 | Human verification of release-critical links | **BLOCKED** | 0 of 244 source rows `human_link_check: true`; machine reads only | 05 section 5 |
| 3 | Complete article and source inventory | **PASS (machine)** with FAIL on frozen gates | 35 articles + 6 tools + 8 hubs + landing built (50 pages); every `{{cite}}` resolves; frozen-inventory gates fail until re-baseline | 05 |
| 4 | Actual rendered-page QA | **PASS (local previews)**, live theme **NOT TESTED** | browser run: 400 loads, 0 overflow, 0 console errors, axe 0 violations (150 runs), keyboard 50/50, Lighthouse 5 pages | 05 sections 3-4 |
| 5 | Accessibility assessment | **PARTIAL** | axe + keyboard + contrast tokens pass; screen reader NOT TESTED; 1 axe "incomplete" (`aria-prohibited-attr` on `reunification-plan`) unresolved | 05 |
| 6 | Approved shelter and Start Here decisions | **BLOCKED** | 0 of 22 decisions answered (X-1..X-5, S-1..S-7, H-1..H-10) | 04 |
| 7 | Independent QD on exact HEAD | **BLOCKED** | not performed; AI cross-checks only | n/a |
| 8 | Specific founder publication authorization | **BLOCKED** | not given | n/a |
| 9 | Custody re-baseline (R22/R23/R53-R59 gates) | **FAIL / BLOCKED** | 30 freeze/inventory assertions red; real tree fails closed | 04 X-1, 05 |

## B. Engineering
| Item | Status | Basis |
|---|---|---|
| Validate (real tree) | FAIL (closed by design) | `duplicate source id ... not documented in source crosswalk` |
| Validate + build (simulated custody copy) | PASS | machine, 0 errors, build exit 0 |
| Full test suite | FAIL | 87 failing of 4,924: 46 Windows environment, 41 other (30 new freeze/count gates). Linux/CI NOT TESTED |
| Shelter tool + browser tests | PASS | 28 tests (1 skipped without axe) |
| Start Here guard module | FAIL (5) | counts + one wording phrase; medicine-guard test passes after restore |
| QA-F1 (phone action box above the fold) | PASS | browser: 41/41 on first screen at 390x844 and 360x740 |
| QA-F2/F3 (water planner no-JS note, silent clamping) | FAIL (open) | not fixed; shared tool owner |
| QA-F4..F6 (flat hubs, table scroll at 360, live-region verbosity) | FAIL/NOT TESTED (open) | design/AT items |
| Lighthouse | PASS lab, 5 pages | 100/100/96/60 (SEO = intentional noindex); localhost, not CWV |
| Live Assembler theme render | NOT TESTED | needs authenticated WordPress draft |
| Screen reader / real devices / Firefox / Safari | NOT TESTED | no access |
| WordPress `wp:html` script/style survival | NOT TESTED | needs installed WordPress |

## C. Content and sources
| Item | Status | Basis |
|---|---|---|
| Quantified claims vs cited pages | 178 of 189 blocks fully matched (machine); 0 contradictions found | verified source (machine-read); 11 not matched = derived arithmetic / absence statements / unreadable |
| Cited sources unreadable by machine | 9 URLs (2 later read in a browser) | machine |
| Historical items flagged unsafe for modern use | Salt beef/pork article carries "Not validated for modern household use" verdict | content check; founder one-word approval (qualified) |
| 1796 vs 1798 cookbook | PASS (wording accurate) | edition metadata re-read at MSU 2026-11-02; passage claims not re-verified |
| Reviewer attribution | CORRECTED | name removed; records qualified (commit `ddedb2fe`) |
| Medicine guard text | RESTORED, pending review | commit `d44fc2c5` |
| Safety exceptions (SX-01..SX-15) | 15 OPEN, 0 closed | `docs/r48/SAFETY-EXCEPTION-REGISTER-2026-11-01.md` |
| Shared-source groups human-reviewed | 0 of 32 | crosswalk |
| Missing archive-level "Sources and safety notes" page | GAP | journey step 5 relies on per-article source lists + landing "Sources you can open" + /editorial-standards/; no new article added |

## D. User journey (Archive -> Start Here -> Practical Guides -> Lost Ways -> Sources and Safety Notes)
Landing links to the Start Here hub and each section hub; the Start Here hub links to water guides, tools, and the Lost Ways hub; every article has breadcrumbs, a TOC, related-guide links and a sources section. Internal-link check: 0 unresolved. Gap: no single "Sources and safety notes" destination (see C).

## E. What would move this to READY FOR QD (not publication)
1. Reviewed re-baseline (X-1). 2. Named reviewers and recorded decisions for X-2, X-3, S-1..S-7, H-1..H-10. 3. Human open of all release-critical links. 4. Independent QD on the exact head. 5. Live-theme and assistive-technology pass. 6. Founder's explicit publication authorization for each specific WordPress or navigation change.

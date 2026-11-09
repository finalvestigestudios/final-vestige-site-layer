# R230 — Preparedness HTML tokenizer-mode source/review HARD HOLD (2026-11-08 PT)

**Scope:** finalvestigestudios/final-vestige-site-layer Issue #136; commercial governance #820 / charter #818. This is an isolated DRAFT/HARD HOLD; no public WordPress, CMS, homepage, navigation, deployment, creator queue, merchant, analytics, email or spending write.

## Independent QA finding and boundary

Praxxis' November 9, 01:59 UTC TASK-008 handoff identified a residual static vulnerability in R229: a plain `<plaintext>` before the bibliography is parsed by Python `HTMLParser` as an ordinary start tag and its later source elements can be counted as visible, while a conforming HTML browser enters PLAINTEXT-to-EOF and does not build those later anchors. This is a *synthetic/parser parity finding*, NOT observed live malicious content.

References: https://html.spec.whatwg.org/multipage/parsing.html#plaintext-state and https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/plaintext . Similar tokenizer-state and legacy-body hazards include xmp, noembed, noframes and frameset-era tags. Rather than pretending full browser fidelity, R230 adopts an explicit conservative unsupported-element policy. The guard recognizes start tags using HTMLParser (not plain regex), so escaped text, attributes and HTML comments do not trigger false tag matches. It rejects nine unsupported elements, including deceptive `<plaintext/>` and `<plaintext></plaintext>`. Passing only means **no known forbidden elements were parsed**, not browser parity or source safety approval.

## Draft code and exact source custody

Based on reviewed **R229 PR #1669 HEAD `dc13eda2704a2c2bb68ded1d2f60629b197e4fe1`**, unmerged. Added the following files:

- `preparedness/tools/r230_html_tokenizer_state_hold.py`: exact Git blob `94e0eb8d790df732f5ae79d8aa2fc8c41d9b3f8e`; always returns `DRAFT_HARD_HOLD` or raises.
- `preparedness/tests/test_r230_html_tokenizer_state_hold.py`: exact Git blob `36ac89b457507a952a1ba1e8c76d1e090ff6bc83`; nine tags × three evidence positions × two spellings, 27 trailing-solidus variants and positive/negative controls.
- `preparedness/tools/r220_full_slate_draft_custody.py`: pins the R230 file by exact Git blob and executes it **before R226/R227** on every intended 41-item × two-format HTML export; repeats source identity check after rendered-corpus review. The invariant rejects any R230 result other than HOLD plus `release_authorized=false`.
- `preparedness/tests/test_r220_full_slate_draft_custody.py`: updates the inherited argument contract and adds 82 WordPress/preview plaintext-injection integration mutants and an explicit 82-invocation custody assertion.
- This audit. No original 35 article bodies/metadata, six tool bodies, taxonomy, source register, disputed citations, original Claude branch, public URL, safety/QD approval, or commercial record modified.

## Executed vs unexecuted

**EXECUTED in local isolated Python environment**: `python -I -m unittest discover -s preparedness/tests -p 'test_r230*.py' -v` = **97/97 PASS**; `python -m compileall -q preparedness` = PASS. Locally executed **both actual R230 file byte strings** were verified against their fetched Git blob identities (`94e0eb8d...` and `36ac89b...`). Negative variants and literal-text controls are deterministic. They are synthetic, and no authenticated 35-article content was present locally.

**BUILT / NOT EXECUTED**: expanded inherited R220 integration tests, including 82 exact-channel mutation fixtures; complete native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full Python discovery; authentic 35 article bodies, six tool bodies, 41 routes and 82 outputs. The local environment still returns `Could not resolve host: github.com` on `git ls-remote`. Connected GitHub reads/writes allowed verified individual files but not a trusted full repository checkout. Do **not** report 82 real exports validated or 82 inherited tests passing.

**Remaining review barriers:** Article #7 two disputed CDC citation occurrences; Article #20 one Ready.gov citation occurrence; seven historical shared source-ID scope conflicts; independent medical/food/fire/household safety, source provenance, accessibility/browser/assistive-tech, and QD reviews. No false QD PASS or medical-safety claim. R230's restricted-tag approach is conservative and is **not** a substitute for browser-equivalent DOM review or the R226/R227 visibility checks.

## Current coordination snapshot

Seven contributor branches independently compared with R200 frozen commit identities, **identical** (ahead=behind=0): start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent QA draft #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture draft #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; related follow-up draft #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. Separate homepage lead #1674 HEAD `95d58186fde4792f05869b12f6531ff82ef4b0a0`; its base #1667 HEAD `be072074459b0b5d78d75e4de5e12782e12b3bb0`. No branch merges, force-pushes or unapproved rebases.

## Conversion-first gating (no seller activation)

**ONE audience/hook:** households planning a practiced emergency contact, an out-of-area backup contact, meeting places and where essential records are kept. Existing free public destination: `https://finalvestige.com/preparedness/` → household emergency plan card → official Ready.gov checklist, which Praxxis verified as a link target; retrieval from that PDF returned HTTP 403 to one check (NOT proof visitors cannot access it). **DRAFT, unrendered on-site CTA:** “Start with the free household emergency planning checklist. Choose your out-of-area contact, meeting place, and where your family can find essential records.” The original detailed 35 guides remain on publication HOLD.

**Only provisional paid candidate:** publicly listed Legacy Triage `https://payhip.com/b/n1RhV` ($19 / 580KB previously observed, seller Vested Wisdom). Its estate/incapacity emphasis is weak-fit for evacuation topics, and account-access templates require a privacy review. Merchant authorization, full delivered PDF copyright/license, consent, suitability, purchase/refund fulfillment and verified orders are NOT independently proven. **NO PAID CTA**, no invented product or retired water freebie.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing Grok relevant post → free public guide | Published `asset_id`, actual hook, rights and mobile destination absent | Praxxis/Grok TASK-008: reconcile an already-posted video, platform URL, permissible UTM and actual final route | UNVERIFIED; no new post | Grok/Praxxis |
| Free guide → detailed Preparedness article | Three source exceptions, seven historical ID conflicts, authentic 82 exports, safety review unapproved | Run native validation/build, R230+R226+R227, exact source/reading-depth review and independent human safety QA | HARD HOLD | Preparedness/independent QA |
| Free plan → optional Legacy Triage | Audience mismatch, ownership, privacy/disclosure | Founder/Commerce check seller authority, full PDF, privacy-safe handling, fit and terms; prefer no upsell if fails | NOT APPROVED | Founder/Commerce |
| Optional product → paid order | Checkout, delivery, refund/fees not tested | Only founder-authorized purchase/download/refund verification | NOT TESTED | Commerce |
| Qualified session → realized net revenue | Missing actual creator ID, qualified-human sessions and confirmed merchant orders | Privacy-safe 7/30-day paid-order reconciliations; fees/refunds deducted | NOT COMPUTABLE | Analytics/Commerce |

**KPI:** realized net revenue per 1,000 qualified human sessions = 1,000 × confirmed net paid revenue ÷ qualified-human sessions, only when both independently verified. An attributed click, confirmed lead or checkout start is NOT a paid order. No personal-data harvesting, duplicate scripts or misleading urgency.

**RELEASE STATE: DRAFT_HARD_HOLD**; future merge/publication requires authenticated full checkout, independent QA/QD and founder authorization.
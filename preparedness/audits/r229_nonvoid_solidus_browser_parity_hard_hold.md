# R229 — source and disclosure HTML parser-parity HOLD (2026-11-08 PT)

**Own only:** Preparedness Archive integration/source/citation safety gates under #136. Parent business decisions #820 / #818. **DRAFT_HARD_HOLD**. No publish approval, QD PASS, safety or revenue claim.

## Precise failure and remediation

Independent Praxxis/Grok handoff review of R228 identified a meaningful browser-versus-Python parsing discrepancy: `HTMLParser.handle_startendtag` treats `<template/>`, `<script/>` and similar markup as immediately closed, whereas the WHATWG HTML parsing algorithm ignores the trailing slash for non-void HTML tags. A citation bibliography or review disclosure following the apparent self-closing tag can be inert in the browser even while both earlier Python gates count it as visible.

Both existing, separately bound validators now **reject non-void HTML trailing-solidus syntax**, retain the opening frame and return only errors or DRAFT_HARD_HOLD. Valid HTML void elements (`<br/>`, `<img/>`, `<wbr />`) and narrowly recognized SVG/MathML self-closing elements remain accepted. The foreign-element exception is deliberately conservative: it excludes `foreignObject`, SVG `desc`/`title` and MathML `annotation-xml` HTML integration points. Unknown foreign syntax fails closed rather than presuming correct browser tree construction.

**Authoritative standard:** https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus

### Exact custody, files changed

- `tools/r226_export_browser_custody.py` Git blob `f261e785c47af9556c3fe3864bbbccb46c3890bc`.
- `tools/r227_inert_context_citation_hold.py` Git blob `8e7a4b8334f7166630d8f362da94b9d56afdbc85`.
- `tests/test_r229_nonvoid_solidus_source_hold.py` Git blob `82c348a991018a6fd155b6eb0fb81e83b4ad3e96`.
- `tools/r220_full_slate_draft_custody.py` repinned both gate identities, preserving the existing 41-export × two-format validation sequence.
- This audit. No original article, tool, source, route, meta, CSS/JS, CMS or merchant change.

### Executed evidence

- **162/162 PASS**, Python `unittest`, actual GitHub-matching R226/R227/test bytes materialized into an isolated `preparedness/tools` + `preparedness/tests` directory, executed as `python -I -m unittest discover -s preparedness/tests -p 'test_r229*.py'`. Explicit 108 non-void syntax/location variants + 36 foreign HTML-integration cases + 18 explicit controls. Each negative case checks **both** guards. Python compileall PASS.
- Three direct Git blob identity calculations of locally executed sources/tests matched the GitHub connector's committed blob SHAs. **This is exact-module isolated execution, not native entire-repository execution.**
- Targeted negative control: temporarily restore each legacy parser method and submit `<template/>` before source section. Prior R226 and R227 individually accept `DRAFT_HARD_HOLD` as though content were visible; the new verified code raises `ValueError` in both. This is a synthetic security regression, not observed malicious public HTML.
- Full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, authentic 35 bodies, six tools and **82 WordPress/preview outputs NOT EXECUTED/VERIFIED** because full repository `git ls-remote` fails with `Could not resolve host: github.com`. The connector allowed exact selective files and commits but not a local full checkout.
- Browser/CSS/assistive-tech inspection and independent qualified source/safety/QD reviews remain outstanding. No automated verdict is a medical, food or fire-safety approval.

### Current independent coordination snapshot

Seven original Claude heads checked against themselves through GitHub compare (status identical, ahead=behind=0): start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. Independent QA draft #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`; homepage #1652 `c50045037a5fddd5d41af4fa850411ad340cb4bf`. No upstream branch touched. R228 base draft #1661 head `5c1805303b197be098a06e948739c32cad7f932d`.

**Unresolved:** Article #7 two CDC source-use occurrences, Article #20 one Ready.gov source-use occurrence, seven historical shared-source-ID/read-scope conflicts, all genuine source and qualified safety adjudication. The 35-article/41-export custody and output fidelity cannot be represented as verified by isolated tests.

## Conversion-first, one provisional candidate only — NOT ACTIVATED

**Audience:** households wanting to organize emergency contact numbers, out-of-area communication and essential document locations. **Existing no-gate public free route:** https://finalvestige.com/preparedness/ → “Create a household emergency plan” → official Ready.gov/FEMA checklist. **Draft on-site CTA concept:** “Start with the free household emergency checklist. Record a backup contact, meeting place and the locations of key documents.” This is an editorial proposal, not a live page change or newly approved printable.

**Optional commercial candidate only:** Legacy Triage, https://payhip.com/b/n1RhV — public `Vested Wisdom` listing $19 and a PDF 580KB; focuses on estate/incapacity continuity, financial accounts and access keys, not evacuation readiness. Merchant authorization, PDF rights, sensitive account-credential handling, product fit, checkout, delivered file, refund accounting and confirmed purchases remain unverified. **NO PAID CTA**; do not substitute retired water guides, create an unapproved product or claim the public seller listing proves a verified sale.

| OFFER → FUNNEL | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing Grok post → free official archive | No authenticated existing asset_id, post URL, rights, hook or mobile final URL | Reconcile actual prior post through established TASK-008, not queue edits | UNVERIFIED | Grok / Praxxis |
| Free archive → detailed 35-article guides | Three specific source occurrences, seven shared-ID conflicts, full native 82-render and QD still blocked | Native validation, export/source/readability review, independent safety adjudication | HARD HOLD | Preparedness / independent QA |
| Official free plan → optional Legacy Triage | Weak intent match, merchant rights and privacy uncertainties | Independent complete PDF/seller rights and matching-audience audit | NOT APPROVED | Founder / Commerce |
| Optional pack → completed order/delivery | No authorized fulfillment/refund test | Founder-authorized checkout, receipt, download, refund/disclosure test | NOT TESTED | Commerce |
| Verified paid orders → net revenue/1k qualified sessions | Missing verified Grok `asset_id` sessions, merchant orders, fees/refunds | Privacy-safe 7/30-day cohort reconciliation; avoid double-counting | NOT COMPUTABLE | Analytics / Commerce |

Acceptance before future public changes: source-correct and browser-visible citations on every genuine output; no lost reading depth, duplicate route or false approval; independent reviewed hazard advice; 360/390/768/1440px accessibility; approved offer disclosures and consent; merchant paid-settlement confirmation; explicit founder approval. Never conflate CTA clicks, email-success screens, outbound affiliate links or checkout intentions with paid orders.

**No production CMS, navigation, homepage, analytics script, merchant, affiliate, email, social, Grok queue, release or spending changes.**

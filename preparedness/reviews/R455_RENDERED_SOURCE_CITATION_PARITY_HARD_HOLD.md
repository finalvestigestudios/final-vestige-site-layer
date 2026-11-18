# R455 — Rendered citation, source identity and reading-scope parity (HARD HOLD)

**Scope:** Preparedness-only, stacked after R454 (PR #2972, parent commit `26e9ef2cd3ad2b74699e1e03c7f5696416ee0f53`). This is an additive **draft integration gate**, not permission to publish, merge, change WordPress, alter navigation or announce safety clearance.

## Concrete gap and patch

The R454 claim-anchor tool detects citations moving across authored paragraphs. It does not validate the **HTML that readers would actually receive** after `build.py` replaces `{{cite:id}}` tokens. A working source ID could silently point at the wrong numbered footnote, changed external URL or shortened reading scope while original authoring-side counts remain accurate.

`preparedness/tools/r455_rendered_citation_parity.py` supplies a read-only adapter for the current exact `build.py` output contract. For **both** WordPress-ready HTML and standalone preview HTML, it requires:

1. Every authored `{{cite:id}}` occurrence maps, in original sequence, to the correct `<sup class="pa-cite">...#src-N [N]</sup>` anchor and correct accessible source title; repeated citations are not collapsed.
2. Exactly one numbered `<li id="src-N">` for each distinct article source identity; distinct source IDs remain distinct even when their original literal URLs match. No duplicate source number, fabricated extra bibliography item or missing reference.
3. The exact source-record URL (not normalized or rewritten), title and publisher, including escaped query parameters, plus the full original documented `supports` reading scope or the article-specific `source_use` text actually chosen by the renderer.
4. Visible human-link-check pending/completed status, `rel="noopener"` on source links, no inline or ancestor hidden/inert/aria-hidden/display-none citation, and no concealment by supported inline styles.
5. Fail-closed outcome on both surfaces, no approval or release promotion, and no filesystem or CMS writes.

**Correct scope input matters:** `build.py` uses `Library.source_for(meta,sid)` and may select the article's original contributor fragment. Populate `sources` in the R455 manifest from that **article-specific exact selection**, never the global first-verified source or a normalized URL register. Derive `source_use` only from the authentic article metadata. This gate must not decide source disputes itself.

## Invocation

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r455_rendered_citation_parity.py' -v
python -I preparedness/tools/r455_rendered_citation_parity.py --manifest /path/to/READ_ONLY_MANIFEST.json
```

The input manifest is a local UTF-8 JSON document containing `body` (original HTML source string), `sources` (ID-keyed exact original article-specific source records with `url/title/publisher/supports`), `wordpress` (generated WordPress draft HTML), `preview` (generated standalone preview HTML), and optional `source_use` (article-specific scoped strings). The CLI only reads that file and prints a machine-readable result. It does not update repository artifacts or proof receipts.

**Run the native tool only on trusted exact checked-out source files and real generated exports.** The fully authenticated originals and 35-article build outputs were not accessible inside the local execution environment for this run. Never treat a synthetic manifest as proof that 35 original articles or 70 native HTML outputs passed.

## What has actually been tested, 2026-11-18 UTC

- **75/75 new synthetic unittest methods passed** (rendered citation order, two IDs sharing one URL, repeated occurrences, full source-use scope, duplicate source identities, hidden references, URL rewriting, malformed aria, missing human review status, altered WP or preview output, source record corruption, and other safety regressions).
- **302/302 local regression unittest methods passed** when combining this exact R455 source/test with the R452–R454 companion files supplied in the prior locally mounted evidence package. This does **not** constitute end-to-end native build integration.
- Python `compileall` passed.
- The exact committed Git blob identities of this R455 tool/test were compared against local `git hash-object`; any later Git head mutation requires fresh verification.
- Native `python -I preparedness/tools/validate.py` and `build.py` were attempted and both could not start: those files are absent from this limited local workspace; no native test, authenticated export, browser acceptance, qualified source interpretation or safety/QD PASS is claimed.
- Independent QA #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`), synthetic fixture #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) and dependent repair #2205 (`bbcf1859768624c611df4abadc564c18247cf32a`) remain open independent DRAFTs and must be reconciled without losing safety assertions.
- All seven original Claude branch heads and two Shelter follow-ups were checked by exact ref SHA in the run. Five source disputes, nine manuscript/source forks and 17 shared-URL review groups continue to require qualified adjudication; the original 35-article docket remains the governing baseline. R455 does not implicitly select any variant.

## Limitations and mandatory release hold

HTMLParser is a static structural preflight, **not a browser renderer, computed CSS audit, sanitizer proof, medical/food/emergency safety review or external URL availability check**. Proximity, links, scope text and even valid citations do **not** prove that advice is supported by the sources or safe for a household. Runtime JS/CSS effects, mobile readability, assistive-technology behavior, actual publisher pages, citations inside rendered shadow DOM and user consent still require independent review. Any unexpected template format requires engineering adaptation and fresh tests, not weakening the gate.

**Required before promotion:** exact original 35-article full checkout, `validate.py`, `build.py`, full native test discovery, authentic source-use manifest for all 35 articles and six tools, actual WordPress-ready and preview output parity, independent QA adjudication, qualified source/food/medical/emergency/child-privacy review, inaccessible-link rechecks, founder review and separate production approval.

## Conversion-first, one-topic acceptance: household contact and reunification

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| One **existing** rights-cleared and payable Preparedness digital pack (identity currently unverified; **no new sales offer**) | Optional paid checkout | No authenticated current FV-owned/licensed SKU, payable checkout, deliverable files, refunds/fees, settlement | Verify one actual product and rights, mobile checkout and delivery before proposing paid CTA | **HOLD**: zero merchant-confirmed purchases or product-authentication records in this lane | Founder / Commerce |
| Free official household planning guide on existing Preparedness resource page | One actual already-published family-contact Grok asset → landing | No verified published immutable asset ID, exact post URL/date, approved mobile destination or intent match | Praxxis independently QA one existing asset under TASK-008; no Grok queue edit or posting | **UNMATCHED** until real post/asset/date/link evidence is supplied | Grok/Praxxis |
| Free existing official checklist; optional original **free** Tool #104 (distinct from Tool #102) | Guide → optional printable | Article #15 and Tool #104 still held for 911/texting, child privacy, no-JS and print review | Draft-only CTA: **Review the official household emergency checklist**. Verify landing destination, exact official link and free printable accuracy before activation | **HARD HOLD**: never present held tool or article as safety-approved | Preparedness / QD |
| Verified commercial offer only | qualified human sessions → relevant CTA → confirmed lead (when applicable) → confirmed paid order → fees/refunds → realized net revenue | No attributable settled order nor qualified-human denominator | Use Claude's existing `utm_content=asset_id`, `utm_campaign` analytics contract; 7/30-day cohorts and tiny-sample warnings; no new script | **NOT COMPUTABLE**: clicks, affiliate outbounds and email subscribers are not paid sales | Claude / Commerce |

**Governing issues:** #136 engineering, #820 conversion and #818 charter. TASK-008 remains Grok/Praxxis creator coordination; nothing here authorizes posting, paid services, merchant/affiliate activation, email, analytics deployment, homepage work, or WordPress writes. **R455 = DRAFT / HARD HOLD.**

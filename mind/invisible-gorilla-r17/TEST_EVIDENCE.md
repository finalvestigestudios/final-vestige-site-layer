# Mind R17 — executed evidence log (2026-10-31 PT)
**Scope:** isolated feature branch `feature/mind-gorilla-attention-zen12-audit-20261031-r17`, child directory `mind/invisible-gorilla-r17/`, all new files; no live site writes. Source material and code were fetched from GitHub through the authenticated connector.

## Exact source readbacks for successful final execution
All six currently audited files were individually fetched by GitHub `fetch_file` from the feature branch and the committed `qa.cjs` pure audit/mutation exports executed in V8 against those same readbacks (not simulated file contents). Source blob hashes:

| Source | Git blob SHA |
| --- | --- |
| `INVESTIGATION_WP_DRAFT.html` | `d53dcd7fe92e6af9dbcac2b80b102f665e1042ed` |
| `ZEN12_EXACT_OFFER_GUIDE.md` | `ef282a4800aeb64f51d54c8d81b06894f4660bf9` |
| `EVIDENCE_MATRIX.json` | `a4b14e74137cfdbcb64e3bff0f2159f08441c084` |
| `ZEN12_FILM_PILOT_AND_PRIVACY_SPEC.md` | `128cb61addb29af76f972f3a481dfd1f7e0bb68e` |
| `ZEN12_WARMUP_PILOT_A_WP_DRAFT.html` | `1fcc54dece814095a980872705647c8172b23ea2` |
| `qa.cjs` | `e8ba712f42e9579c0ac90e91ee4462d92711f535` |

**Executed final audit: 98 / 98 PASS. Executed targeted adversarial mutations: 22 / 22 CAUGHT.** Seven contrast checks are included in those 98 checks, not separate. The checks specifically cover source presence and statistical caveats, first-party published links, no active merchant anchors, disclosure and disabled CTA, product-specific seller claims, claim IDs/foreign keys, privacy OFF flags, film concept/manual controls/caption/transcript constraints, media no-JS posture, local CSS responsive/keyboard/forced-colors/motion safeguards. The 22 deliberate in-memory regressions covered unauthorized affiliate approval and URL, script/form/iframe injection, missing original sources, missing Focus, incomplete disclosure, enabled CTAs, activation of analytics, false video hosting, copy divergence, and merchant outbound injection.

**Important test evolution, disclosed rather than hidden:**
1. First article+guide+matrix+pilot source test completed **80/80**, initially **17/18** mutations caught because removing the first of two identical research citations left the bibliography citation; hardened the mutation to replace *both* occurrences. Re-test: **80/80, 18/18**.
2. After adding a standalone warmup, initial QA edit had double-escaped regex and failed parsing. Corrected. Next QA had two false positives (a `<video>` token inside an HTML comment was not a rendered player; wording said merchant rather than seller claim). Narrowed tests transparently. Then **96/96, 22/22**.
3. Tightened release posture further by removing **all clickable merchant destinations** from the outward-facing article and warmup while keeping official checkout links in reviewer-only evidence documents. Added prohibitions on any `a href` for `zen12.com` or `inspire3.com` in either public candidate. Latest tests **98/98, 22/22**, no failed checks.

## Browser, CI, scientific and CMS limitations
- **Not run in this sprint:** Node checkout CLI execution, GitHub hosted Actions, WordPress staging/Gutenberg, NVDA/VoiceOver, Safari/Firefox actual browsers, screen reader keyboard/zoom, real color contrast after theme/global CSS, responsive viewport screenshot examination, WCAG certification, mobile CWV/Lighthouse, site search indexing, partner approval or commercial conversion A/B.
- Previously independently tested optional 40-second Zen12 portrait film exists in separate [PR #229](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/229) and prior offline review ZIP. **No live video embedding or performance assertion in R17.** Existing film cannot be taken as hosted/authorized/quality-cleared merely because an earlier fixture test passed.
- Source QA confirms static contracts and computed contrast for hard-coded draft CSS values; it does not certify the final WordPress template styling or full accessibility.
- We did **read-only** WordPress API `posts.list` returning exactly **61 published posts**, and `pages.get` confirming published Puységur (ID 1377) and Focus (ID 1579), no writes or content changes. Verified exact offer content in 2026-10-31 web read of `https://zen12.com/about` and `https://zen12.com/getstarted`; their dynamic promotional sections are **not** reproduced.
- Exact primary evidence: https://doi.org/10.1068/p281059 , https://doi.org/10.1068/i0386 , https://doi.org/10.1177/0956797613479386 , https://doi.org/10.1016/0010-0285(75)90019-5 . Independent context: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety and https://pubmed.ncbi.nlm.nih.gov/37205669/ . Regulatory: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Local reproduction
```sh
node mind/invisible-gorilla-r17/qa.cjs --mutation
```
CLI exit nonzero if any check or mutation fails; Node command offered for reviewers, **not falsely claimed executed in this run**. Audit runs on exact source GitHub readbacks using exported functions, not full Node process.

## Release and handoff
**Draft PR only. HOLD.** No original homepage PR #49, Issue #150 owner, Mind hub PR #172, Site QA #126, Dispatch Issue #174, live WordPress pages/menus, existing Jetpack Focus welcome/subscriber list, merchant creative, purchases, tracking or affiliate links modified. Pending actual staging, accessibility, partner account authorization and founder approval. Exact PR URL and branch head will be recorded in Issue #171 after PR creation.
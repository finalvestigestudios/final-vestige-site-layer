# Apollo R133 — deterministic offline Research Desk staging artifact (STAGING HOLD)
Date: 2026-11-05 (Pacific). Governing issues: #150, #820; business charter #818. Branch based on R132 commit `868e7454e31e7b8105ef2bd3c93d59631b99fe17`. No changes to frozen homepage PR #49, Research Desk PR #158, production WordPress, existing newsletter, sales platform or Grok/Praxxis task queues.

## Concrete implementation
`r133_build_research_desk_preview.cjs` reads the **actual source-controlled** R132 six-record editorial HTML and current Research Desk CSS/JS, verifies the existing R132 historical/rights gate, repairs a newly found preview-only progressive-enhancement bug, runs the editorial audit again, and builds one standalone, self-contained staging HTML document plus a SHA-256/Git-blob evidence manifest. No network calls, remote assets, photographs, paid services, visitor storage or analytics. The document has a visible STAGING ONLY warning and robots noindex; policy restricts outbound network/frames/images/forms via hash-based Content Security Policy. NASA *links* remain sources, not commercial image permission.

### Newly observed component defect
The R132 derivative HTML includes `data-fvx-search`, `data-fvx-status`, `data-fvx-tools hidden`, and `data-fvx-empty` but **omits `data-fvx-clear`**. The existing Research Desk JS returns early if that control is missing, so its optional search UI never becomes interactive. R133 inserts a single 44px-minimum Clear search button **only in the generated isolated review artifact** before source audit and render. No alteration of R132's original reviewed HTML, the PR #158 shortcode, or any production page. The no-JS complete list remains the default.

## Local reproducible commands (from repository root)
```bash
node --test experience2/apollo-creator-bridge/test_r133_build_research_desk_preview.cjs
node experience2/apollo-creator-bridge/r133_build_research_desk_preview.cjs --out /tmp/fv-apollo-r133-artifacts
sha256sum /tmp/fv-apollo-r133-artifacts/apollo-r133-research-desk-editorial-preview.html
```
The builder fails rather than emitting a document if the R132 source-custody audit fails, if required CSS/JS scopes disappear, or if remote styles, JS network/storage APIs or dynamic JS evaluation are introduced. Its manifest records input SHA-256 and Git-blob identities, generated HTML SHA-256, rights/revenue uncertainties, and **NOT_ESTABLISHED** browser acceptance.

## Evidence and limitations
- Native Node v22.16.0: **12/13 tests passed; 1 positively keyed repository-build test skipped** in the external isolated package because the actual R132 source inputs were not copied into that test container. The test and builder are now GitHub source-controlled and must run on an actual checkout for the required positive full-source build.
- This result verifies the actual committed R133 builder and test blobs, not a full Apollo webpage. No hosted Actions run on exact R133 SHA or actual-source builder artifact is claimed.
- Real Chromium 144 HTTP/file/data navigation previously returned `ERR_BLOCKED_BY_ADMINISTRATOR`. Do not count document injection or source tests as full-page Playwright, axe, actual LCP/CLS, screenshots, keyboard/touch, or WordPress/Assembler acceptance. Those remain release blockers.
- Official NASA photograph source metadata had been checked 6/6 in R131, but **individual commercial media reuse/publicity review remains 0/6**; crew photo `S67-19766` ID remains provisional.
- R132 six editorial source-role reconciliations are proposed for Research Desk and require separate maintainer/editorial sign-off, not a silent merge.

## Conversion contract and experiment
**Audience:** Secondary educators seeing a future Grok long-form Apollo evidence investigation, not an assumed published Grok asset. **Journey:** unique approved `utm_content=asset_id` organic social link → Apollo investigation / Source Drawer / Review Board → accessible free student evidence worksheet → *only after independent merchant verification* an optional, contextually relevant educational casefile link. No commerce embedded in the six-record historical chronology and no extra email signup.

**Hypothesis:** Transparent photographed-evidence boundaries and an actually usable accessible source search reduce educator uncertainty and improve free-resource completion, leading to informed interest in a rights-cleared paid classroom kit. This is **unproven**, and worksheet use or clicks are not sales.

| Priority | Offer → funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Existing FV educator-compatible SKU → merchant-confirmed paid order | No independently verified matching rights-cleared sellable SKU, fulfillment, fees or refunds | Read-only merchant validation; withhold checkout | BLOCKED | Claude/Growth + founder |
| P1 | Grok Apollo video → source proof → free worksheet | R132 preview's broken optional source search and incomplete browser evidence | R133 deterministic offline preview and progressive-search repair; review on real checkout | BUILT; native unit tests 12 PASS, 1 SKIP; full page NOT TESTED | Apollo + independent QA |
| P2 | Free worksheet → optional approved paid kit | No verified product or founder-approved link | Maintain free worksheet; draft link only after approval | NOT ACTIVATED | Founder/Claude |
| P3 | Paid sale → net revenue/1000 qualified-human sessions | No attributed qualified humans or reconciled merchant orders | Use issue #820 existing privacy-safe 7/30-day scorecard, no duplicate scripts | NOT COMPUTABLE | Claude/Growth |

**Release gate:** Keep draft and staging only until actual-source native Node success, Chromium 320/360/390/768/1440/1920 real-navigation keyboard/touch/reduced-motion/no-JS/axe/LCP/CLS, WordPress shortcode lifecycle/Assembler tests, six image-rights reviews, editorial signoff and founder approval. No PR merge, production, tracking, commercial activation, emails, social posts or spending authorized.

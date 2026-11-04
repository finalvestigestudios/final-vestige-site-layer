# Apollo R111 — classroom navigation, published Atlas reconciliation and release HOLD

**Classification (2026-11-04 UTC):** R111 **BUILT** on a separate stacked Apollo branch; no independent release certification or paid offer verification. Original Research Desk [#158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), frozen homepage [#49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) and homepage branches untouched. Parent [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); conversion requirements [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## Actual product improvement

The single existing free-classroom-action link now points to a natively focusable section (`tabindex="-1"`) with a visible `:target` outline, including forced-colors treatment. The classroom sample directly links back to the six-record NASA source custody register. This is a **source-checking path**, not another lead-capture form or a purchase button. JavaScript remains optional, so native fragment navigation and the evidence text continue to work with scripting disabled. Six NASA source page URLs and zero photograph binary embeds are preserved.

The pre-existing local HTTP/WordPress-bound acceptance runner now checks **actual fragment focus** after keyboard activation/mobile tap, not only the URL fragment and viewport. New `test_r111_fragment_contract.py` enforces source, commerce and accessibility boundaries on the real HTML.

`qa_r111_offline_dom.py` is an additional real Chromium/Playwright runner using `page.set_content` from a **local exact HTML file**. It covers 320/360/390/768/1024/1440/1920 × JS on/off; keyboard, touch, reduced motion, six NASA rows, four bounded evidence plates, native disclosures, no-JS, source-return navigation, no unexpected requests, no unsupported purchase controls, two SHA-256 screenshot receipts and optional **pre-approved local** axe-core (never auto-downloaded). Atomic partial status stays `INCOMPLETE_STAGING_HOLD` until all modes finish.

**The in-memory runner is not HTTP performance evidence.** It deliberately reports LCP and CLS `NOT_MEASURED_IN_MEMORY`, and cannot certify Assembler, hosted WordPress, physical devices, screen readers or a paid checkout. The original 2,500ms LCP and 0.1 CLS thresholds are unchanged in the HTTP runner.

## Newly relevant production-state difference — review, do not silently release

**Read-only authenticated WordPress.com inspection on 2026-11-04 UTC** of site 256784396 found existing page **2017** at `https://finalvestige.com/apollo-1-evidence-atlas/` with **`status=publish`**, `modified=2026-11-03T22:10:29` (site-local). The page's view-content body is **87,895 characters**, contains one inline script, zero `<img>` elements, zero forms, and no Payhip/checkout string. These are **read-only markup counts**, not a browser audit. The page was noted by independent Site QA in #150 as having a publication-state transition; **the approving release decision has not been independently established**. This already-published page must not be confused with R111's unmerged `landing-preview.html`, the Apollo original article with six photographs or homepage PR #49. No conclusion that the page was unauthorized should be inferred merely from missing approval records.

**Owner reconciliation requested:** Claude/WordPress release owner and QD identify the documented go/no-go, exact live artifact/version, accessibility and browser QA, restoration point and whether that separately scoped text-only page should be promoted. Founder retains release approval. R111 must not be deployed or treated as the live page. There were **no WordPress content/settings writes** from R111.

## Historical and commercial boundaries

- Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/. The specific ignition source remains unproven; approximate ground-test sequence is distinct from photographic dates. Do not create inferred geographic pins or causal Atlas edges.
- Pinned R37 six-photo custody ledger remains `INDIVIDUAL_REVIEW_REQUIRED` 0/6 for reproduction. The `S67-19766` crew catalog association remains provisional. Links to NASA originals are not blanket commercial image clearance.
- Grok owns future video production and platform posts, Praxxis owns creator QA/TASK-008, Claude owns website analytics/merchant tracking, and founder approves posting, publishing and spending. Apollo does not modify their queues or metrics.
- No verified Apollo-specific product, licensed fulfillment, paid merchant order, affiliate acceptance, refunded fees, qualified campaign sessions or revenue denominator exists in this lane. Never treat exercise engagement or outbound CTA taps as paid sales.

| Priority | OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| P0 | Proposed Apollo educational casefile → paid buyer | No verified matching live SKU, rights/fulfillment/refund evidence or buyer proof | Claude/Growth independently inspect seller inventory and rights, founder decides whether to list a pilot | **BLOCKED; no paid CTA or realized net revenue** | Claude/Growth/founder |
| P1 | Future Grok source-linked Apollo video → investigation → free classroom sample | Creator asset/campaign not approved; full browser QA pending | R111 native target focus/source-trail continuity; test 14 modes | **BUILT; browser fixture test does NOT certify actual staging** | Apollo; Grok/Praxxis |
| P2 | Publisher-approved sample → relevant product checkout | No verified merchant path, no permission to advertise commercial product | Controlled, consent-respecting staged checkout review only after offer rights clear | **NOT VERIFIED** | Claude/Site QA/founder |
| P3 | Verified paid orders → realized net revenue per 1,000 qualified humans | Missing UTM asset IDs, human sessions, merchant fees/refunds/orders | Reuse #820 attribution contract, never duplicate scripts | **NOT COMPUTABLE** | Claude/Growth |

## Reproduction / acceptance gates

```bash
python -m unittest discover -s experience2/apollo-creator-bridge -p test_r111_fragment_contract.py -v
python experience2/apollo-creator-bridge/qa_r111_offline_dom.py --output /tmp/apollo-r111-dom --chromium-path /usr/bin/chromium
python experience2/apollo-creator-bridge/qa_r108.py --output /tmp/apollo-r111-http
```

The `--chromium-path` example is for hosts with Chromium already installed; omit it if Playwright-managed Chromium is available. The optional `--axe /path/to/approved/axe.min.js` is allowed only for a preinstalled, reviewed local bundle.

**Local fixture test only (not the exact R111 landing):** Chromium 144 ran the new offline runner over a clearly labelled synthetic accessibility fixture: **14/14 mode checks passed**, two SHA-256 screenshot receipts, no axe. The harness file's local Git blob was rechecked against the canonical branch. This tests runner mechanics, **not** actual Apollo content correctness. Exact-head `test_r111_fragment_contract.py` and browser matrix against the committed landing require execution/review; CI runner health is not assumed.

**Release HOLD until:** actual exact-head Chromium DOM and local HTTP/WordPress/Assembler acceptance; real axe with a vetted bundle; mobile/screen-reader/manual checks; verified photograph rights/editorial; production page 2017 authorization reconciliation; merchant product verification; QD and explicit founder approval. No merges, promotion, WordPress settings/content changes, paid services, analytic scripts, social posts or emails authorized by this patch.

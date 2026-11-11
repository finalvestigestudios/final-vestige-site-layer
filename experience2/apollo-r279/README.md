# Apollo R279 — render-time NASA custody resilience (staging / HARD HOLD)

Parent: R278 draft PR #2006, HEAD `220299faa01bec29655006491dad7bbf1d1497dc`. Do not touch PR #49, Research Desk PR #158 or Claude/Grok ownership.

## Verified defect and correction

R278 guarded exceptions thrown during inclusion of its sibling PHP source, but not during subsequent execution of `fv_ex2_r273_review_panel([])`. Parent-adapter negative controls: renderer exception caused PHP exit code 255 and dropped NASA/free-investigation access; an empty return exited 0 but provided no evidence links.

R279 catches failures from **both** inclusion and execution, discards accidental sibling echo output, and checks the pending-only panel marker, exactly two approved NASA report anchors and one existing free-investigation anchor, three total links, and absence of embedded scripts/iframes. Unexpected runtime failures, incomplete HTML and accidental merchant-link drift fall back to static NASA primary source + original free investigation, never a blank panel, a false editorial approval or a new offer. This is an accidental-installation mismatch detector, not a sanitizer for intentionally malicious privileged PHP.

**Primary source:** https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — an electrical arc was the most probable initiator, but the exact ignition source was not established.

**Media rights:** https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — NASA has not endorsed the site or commercial offers; historical links are not clearance for astronaut likenesses, NASA identity marks or advertisements.

**Existing historical route:** https://finalvestige.com/apollo-1-evidence-atlas/ → https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . Two existing Atlas editorial statuses remain *Not yet reviewed*; no status was changed in production.

## QA / exact commands

```sh
php -l experience2/apollo-r277/apollo-review-shortcode.php
php experience2/apollo-r277/qa/wp_contract_gate.php
python experience2/apollo-r278/qa/failopen_gate.py /tmp/r279-committed-gate
```

The source-controlled negative-control suite covers 14 real PHP sibling states and 70 Chromium width/JS contexts (320/390/768/1440/1920; keyboard/no-JS/touch/reduced-motion). A separate complete actual PHP/Chromium integration gate, receipt and screenshots are supplied in the reproducible QA bundle: 14/14 PHP, 40/40 Chromium, twice; SHA-256 of each JSON receipt `23618bfeeca54e038882123b7e7122333855029006d52d180c99f2a8cb003a7d`. Source-controlled adapter Git blob `821edd4118c44543dcf1cf3187fc2aedf289c116` matches the locally tested bytes.

**Not passed/not run:** installed WordPress, browser HTTP/CSP (`ERR_BLOCKED_BY_ADMINISTRATOR` in prior runtime), genuine axe-core (authenticated pinned distribution unavailable), independent screen reader, real browser-interface zoom, field LCP/CLS and CI release gates. Local Chromium PerformanceObserver entries are not production Core Web Vitals. No deployments, WordPress writes, analytics changes, posting, affiliate activations or spending.

## Conversion-first, one controlled path

Verified Grok published Apollo asset_id/UTM (currently unverified) → public Atlas → free original Apollo investigation → only after merchant/founder approvals, separately disclosed optional Mini Museum guide → authenticated paid order, fees, refunds and cleared commission. Do not classify clicks/leads as purchases. Realized net revenue per 1,000 qualified human sessions for 7/30-day cohorts remains **NOT COMPUTABLE**. Grok owns script/post; Praxxis owns creator QA; Claude owns analytics/production; founder owns releases and spending. Coordination: #150 / #820 / #818. **Release HARD HOLD**.

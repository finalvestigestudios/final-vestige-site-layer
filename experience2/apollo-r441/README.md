# Apollo R441 — evidence-to-offer staging acceptance gate

**BUILT / LOCAL QA PASS / NOT INSTALLED / NOT LIVE / NOT APPROVED.** This is a deliberately isolated, **test-only and staging-audit** sprint. It does not add another landing page, CTA, signup form, affiliate link, WordPress write or analytics script. Its value is to make the existing R438 Atlas → R439 source receipt → R440 educator preview release gate evidence-backed instead of perpetually extending the story UI without proving it works on a real browser origin.

Base: R440 draft #2925 `de1c3e3ac74574cfd775fb89aa544864f0bf3ff2`; parent components remain unchanged. The frozen homepage PR #49, original Research Desk PR #158, Grok/Praxxis TASK-008 and Claude's primary engineering branch remain untouched.

## Run only in a local checked-out, exact-head branch

```bash
python3 experience2/apollo-r441/qa/source_guard.py --repo-root . --report experience2/apollo-r441/QA/custody.json
python3 experience2/apollo-r441/qa/test_source_guard.py
python3 experience2/apollo-r441/qa/local_probe.py --repo-root . --out experience2/apollo-r441/QA/offline
python3 experience2/apollo-r441/qa/package_evidence.py
```

The six original Git blob identities are pinned and the eight unsatisfied commercial gates must remain false. Negative tests require unauthorized changes, missing documents and symlinks to **HOLD**. The offline probe executes the *actual R440 PHP fixture* in Chromium at 320, 360, 390, 768, 1024, 1440 and 1920px with JavaScript both enabled and disabled. It is not navigated WordPress and never claims axe or CWV.

## Real HTTPS staging acceptance (not yet runnable)

The staging URL must be a founder-approved **HTTPS nonproduction origin** with the R439 evidence Atlas and R440 educator preview mounted once each. A reviewed, local full axe-core JS bundle must be available; no CDN or fabricated stub.

```bash
FV_APOLLO_STAGING_URL=https://staging-host.example/apollo-review/ \
FV_APOLLO_APPROVED_ORIGIN=https://staging-host.example \
FV_AXE_CORE_JS=/approved/local/axe.min.js \
python3 experience2/apollo-r441/qa/staging_acceptance.py --out experience2/apollo-r441/QA/staging
```

The script **really navigates** every viewport with Playwright and checks actual source links, one editorial free CTA, zero paid CTAs, overflow, no-JS meaning, axe-core WCAG findings, and *lab* LCP <= 2.5s / CLS <= 0.1. Outputs screenshot PNG and JSON; no form submission or user tracking. Failure to navigate or measure is HOLD, not PASS. Independent real-device VoiceOver/NVDA, mobile touch, field Core Web Vitals, founder visual and QD still remain necessary. This runner must never be pointed at the public finalvestige.com origin.

## Source, rights and business boundaries

The flagship remains **Apollo 1**: NASA Review Board primary accident findings and NASA later flammability retrospective. Source access does not clear rights to commercial photographs or imply NASA endorsement. No speculative pins or fabricated attribution. One visitor journey: independently authenticated Grok Apollo video → curated Atlas/receipt → original free educator task → existing full free investigation → founder-approved, *future* paid original classroom dossier. That paid dossier is a **proposal only**; no verified SKU, fulfilled checkout, merchant settlement or financial return.

**Release HOLD:** underlying R417 discrepancy, actual staging, real axe, lab CWV, screen readers, reviewer/QD, merchant verification, and founder authorization.

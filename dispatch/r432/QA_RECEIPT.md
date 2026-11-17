# R432 — honest QA receipt and release constraints

**Execution date:** November 17, 2026 (Pacific). **Owner:** [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Merchant gates: [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). No actual email delivery, no paid order observed and no production mutations.

## Source and predecessor integrity

The original six canonical newsletter files, manifest and test from [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at **exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`** were independently fetched through connected GitHub and matched against the already mounted local first-mile package using native Git blob hashing. All **eight files matched**. Executed `python3 -m unittest discover -s campaign-2026-mind/tests -p 'test_*.py' -v`: **6/6 PASS** on native Python 3.13.5. The original master and previous R431 source assets were not edited. Parent stacked head was `b72b02c206b894e12b05152cc35d9bc41e9a0fb6` ([R431 #2911](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2911)).

## New R432 native test execution

New additive `broadcast_consent_gate.cjs` / `test_broadcast_consent_gate.cjs` were authored and executed **locally with Node v22.16.0**. `node dispatch/r432/test_broadcast_consent_gate.cjs` returned **PASS 94/94 native Node assertions**, exit code 0.

Exact GitHub readback source identities matched the locally executed bytes:

| Code | Native local Git blob and independent GitHub SHA |
| --- | --- |
| `dispatch/r432/broadcast_consent_gate.cjs` | `d3288062118fb9515887ab0c656d2b13a94df1ac` |
| `dispatch/r432/test_broadcast_consent_gate.cjs` | `0383a72d4855ae03adc51ebefb55001d21a927fb` |

The tests cover: false delivery state for all six actual missing-evidence issue classes, non-additive subscriber buckets and zero direct-email followers classified as **observations, not permanent blockers**, Reader/email scope differences, welcome configured vs **received**, forbidden recipient PII, category broadcast limits, repeated issues, editorial vs commercial isolation, exact offer type and one-offer-only rule, per-SKU channel permission, postal address and functioning unsubscribe evidence, malicious/missing attestation fields, strict no-send return, proposed source tags and all-false merchant settlement accounting.

**Additional GitHub-readback static QA:** 50/50 checks passed over the six committed code, ledger, guide and HTML source files. Validated mobile responsive CSS, semantic headings, focus indicator, accessible table headings, no scripts/forms/input/buttons/remote media/merchant checkout links and original 4:2 manifest. Initial QA false positive: a regex rejected the *words* "tracking pixel" in a warning, although there was no tracking element. Corrected the checker to inspect actual active elements and merchant `src/href` destinations before final 50/50 PASS; HTML source itself did not need a change.

## Live read-only facts, 2026-11-17 21:38 UTC

WordPress Newsletter ON, automatic new-post email OFF, full content, featured image ON, **newsletter categories OFF**, 52-page Fieldbook welcome configured. Dashboard: **total 3 / confirmed 3 / unconfirmed 2**, nonadditive. Jetpack followers: **Reader 3 / direct email 0**. Recent five post notifications `never_sent_opted_out` (does not prove lifetime zero). Unique consented receiving inbox count, welcome actual receipt, native Jetpack Preview, Final Vestige physical postal address, functional unsub, email affiliate rights, approved guide/earning URL and paid settlements **not verified**.

## Hard safety boundaries

- Code is **offline classification only**. It contains no WordPress/Gmail/API network integration and always returns `sendAuthorized:false`; even synthetic all-true cases produce `HUMAN_REVIEW_ONLY`, never a send action.
- No proof of subscriber delivery or provider authentication was obtained through these synthetic tests.
- Preview board is **not** a real Jetpack renderer or received inbox; no screenshot or mobile browser execution is claimed.
- Review-only proposed UTM conventions are not live; no merchant earning link is active; no subscriber emails or personal identifiers are included.
- The founder must approve final creative, valid receiving audience, sender legal footer and schedule after proof; partner requires separate authenticated EMAIL promotion authorization.
- Revenue per 1,000 qualified-human sessions remains **NOT_COMPUTABLE**, not zero, without audited source denominator and independently confirmed paid transactions/refunds/fees.

**Disposition: all original six issues HOLD_UNSENT; issues 03/05 HOLD_MERCHANT; original issue 04 HOLD_FACTUAL_COPY.** R426/R427/R428 optional alternatives remain unadopted. No sending, test email, scheduled sending, WordPress writes, list import, new newsletter service, merchant activation, merge, social post or spend.

### Final correction on the subscriber-count interpretation
WordPress's November 4 subscriber guide explains that **Not confirmed is excluded from the total subscriber count**. Therefore `3 total / 3 confirmed / 2 unconfirmed` may be entirely consistent with that interface and **must not be labeled database corruption**. The additional Reader 3 / direct email 0 measures distinct metrics. R432 first draft incorrectly treated `confirmed+unconfirmed>total` and reported zero direct email followers as irreversible release blockers even after hypothetical provider-verification. Corrected the final Node code to report both as **non-additive scope observations** and reserve hard-stop for missing authenticated receiving eligibility, consent, footer, preview and founder/merchant approval. The final exact GitHub code/test blobs match a fresh **94/94 native Node PASS**. This correction does not authorize sending; real-world approvals remain missing.

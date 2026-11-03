# Apollo R90 — Individually Bound NASA Source Cards (STAGING HOLD)

This sprint addresses a concrete custody vulnerability discovered in the prior R89 integration audit: every review page could contain all six correct NASA URLs while two **individual source cards linked to the wrong official NASA image**. The aggregate set and cross-document anchor checks alone could not detect that misattribution.

## Source-controlled implementation
- Extends the R89 generator with an independent `ScopedSourceCards` HTMLParser check, performed **after** generating all four actual staging surfaces and **before** copying any output to the requested destination.
- Verifies six source IDs in each of the four pages, for **24 individual record bindings**.
- Binds the reviewed NASA URL to its own card alongside that card's title, exact catalog token, photographic date, evidence limitation and retained rights warning. Verifies crew-portrait provisional identification language in every surface.
- Rejects swapped but still-valid NASA source links, other external links on a source card, omitted source cards, duplicate IDs, mislabelled titles, date precision claims, changed evidence limitations and false photographic-rights clearance.
- Adds the sorted 24-record attestation and source-ID URL map to the existing R89 deterministic receipt. The existing ZIP manifest records the modified generator, tests and exact generated preview, reproducibly.
- Adds adversarial regression tests, plus real Playwright assertions that all six links in the integrated hub resolve to their respective expected source IDs at 320, 390, 768, 1440, 1920 px with JavaScript on/off. Existing axe-core/keyboard/touch/print/reduced-motion/forced-colors/LCP/CLS gates remain unchanged.

## Reproduce against exact branch head

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experience2/evidence-atlas/tests -p test_review_hub_r89.py -v
PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_review_hub_r89.py /tmp/apollo-r90-a /tmp/apollo-r90-a.zip
PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_review_hub_r89.py /tmp/apollo-r90-b /tmp/apollo-r90-b.zip
cmp /tmp/apollo-r90-a.zip /tmp/apollo-r90-b.zip
```

## Protected boundaries

This branch is stacked on isolated Apollo R89 PR #761, NOT homepage PR #49 or the original Research Desk PR #158. No changes to homepage branches, production, WordPress content/settings or plugins. No NASA image is embedded and none of six photo-specific reuse decisions is approved. No speculative geographic pins or inferred edges are permitted.

**Release decision: HOLD.** NASA rights review 0/6, provisional S67-19766 association, authorized hosted WordPress acceptance, independent QA, manual NVDA/VoiceOver and real-device reviews, hosted Core Web Vitals and founder approval remain unresolved. R90 testing is laboratory acceptance only; it cannot authorize publication.

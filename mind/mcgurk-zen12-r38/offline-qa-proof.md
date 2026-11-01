# Mind & Affiliate Studio R38 — verification and review evidence (2026-11-01)

**Scope:** isolated draft, NO publishing/merchant checkout/analytics, no modifications to other agent files. All new additions under `mind/mcgurk-zen12-r38/`. Base `main` SHA `77a87635eb613ce6de268aee11350fa8242efa0f`.

## Exact actual tests

- Fetch-readback of **all 16 deliverables** from this branch via authenticated GitHub connector: 16/16 succeeded before adding this proof record.
- Execute `qa-r38.mjs`'s exported `checkWithFiles(map)` function in an isolated V8 environment **against those exact 16 GitHub source readbacks** (not simulated file contents): **78 source/claims/design/security assertions PASS, 0 FAIL**.
- Ten deliberately hazardous mutations: **10/10 caught** (active checkout action, missing disclosure, autoplay, absent captions, absent alt, extra email form, script, guide-core A/B drift, reenabled purchasing wording, hidden disclosure).
- Execute `attribution-privacy.mjs`'s exported `selfTest()` against readback: **30/30 synthetic privacy assertions PASS**; `ENABLED=false`; no request/storage/collector was connected.
- A/B guide core between `zen12-a-text.wp.html` and `zen12-b-optional-film.wp.html`: **14,288 bytes identical**. B's extra optional film is a visible static poster with timed transcript, no broken player or autoplay.
- Matrix: **43 claim, evidence and permissions rows**; independent/source register: **17 entries**.
- Both original manuscript and commercial guide are substantial (~2,093 and ~1,955 whitespace-count words respectively). The investigation contains no product endorsement.
- Native `node` checkout and hosted CI **NOT run or verified**; the V8 source-function execution above does not establish Node integration.
- WordPress staging and actual browser WCAG 2.2 AA keyboard/no-JS/reduced-motion/mobile/zoom, Lighthouse/CWV, caption timing on hosted video, live visitor outcomes and conversion are **NOT verified**.

## Original offline 40-second film review proof

A standalone offline matching original-film renderer was run in a Python/Pillow/FFmpeg environment. This is a production proof of an actual silent MP4, **not** a claim that the exact repository renderer was checked out and executed. The corresponding source-controlled Python renderer `render-mcgurk.py` is included for a later native reproduction test.

- Offline review MP4 `/mnt/data/fv_mind_r38/mcgurk-evidence-40s.mp4` (not in GitHub or WordPress).
- `ffprobe` found codec **H.264**, **540×960**, **12 fps**, **480 frames**, duration **40.000000 seconds**, file size **104,402 bytes**.
- MP4 SHA-256: `dc95aad40f5c0772bf5812b6cf02d0bfd5f45accbeb0d028f6173ac839b68594`.
- Original offline PNG poster `/mnt/data/fv_mind_r38/mcgurk-film-poster.png` and six-scene contact proof `/mnt/data/fv_mind_r38/storyboard-contact.png`.
- Representative frames from six segments visually inspected; no observed caption clipping or unreadable text. This is a silent schematic **explainer**, not a working BA/GA McGurk demonstration, endorsement, or seller product evidence.
- Original source-controlled SVG poster, six-cue .vtt, full on-page transcript, storyboard and Python renderer are included; B shows **poster+transcript only** pending accessible first-party hosting and caption sync QA.

## Exact sources / clear limitations

- McGurk & MacDonald 1976 `https://doi.org/10.1038/264746a0`, variability `https://pubmed.ncbi.nlm.nih.gov/25802068/`, debate `https://doi.org/10.3758/s13414-021-02265-6`; original and conflicting evidence covered in article.
- FV's authenticated published Puységur archive `https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/` and existing single Focus Fieldbook route `https://finalvestige.com/focus/`.
- Exact merchant source `https://inspire3.com/`, `https://zen12.com/hnp`, `https://zen12.com/about`, `https://zen12.com/getstarted`; independent binaural review `https://doi.org/10.1371/journal.pone.0286023`. Seller claims **not adopted**; studies **did not test Zen12**.
- FTC endorsements `https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking`; health-products `https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance`.
- Public affiliate signup `https://affiliates.inspire3.com/` **is NOT** FV-specific partner approval, licensed promo creative, channel authorization or actual earning tracking link. Seller sources accessible within guide are visibly labelled as merchant pages that may offer checkout.

## Release HOLD / coordination

Need written Final Vestige-specific Inspire3 acceptance, exact product SKU links/tracking/channel/creative rights, verified current buyer/refund/privacy/checkout terms, independent editorial+FTC claim review, Site QA #126 real-browser staging, homepage art Issue #150 design review only, Dispatch #174 receipt of landing-page status (NO newsletter edits/sends), proper first-party video with timed captions in B, and explicit founder permission for separate merge/publish/merchant CTA/tracking actions. Homepage PR #49 frozen and Mind hub PR #172 authoritative: untouched. Existing Jetpack/Focus welcome and subscriber funnel: untouched.

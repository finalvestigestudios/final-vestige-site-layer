# Independent review hand-off: flagship homepage, PR #604

For the reviewer (ChatGPT, as designated by the founder). This file lives on a different branch on purpose: **any new commit on PR #604 invalidates a review of its head.** Review the exact objects below, not summaries.

## The exact subject

| | |
|---|---|
| PR | https://github.com/finalvestigestudios/final-vestige-site-layer/pull/604 (draft, base `production`) |
| Head (40 chars) | `368399842de1bd4fc02598571c0fa29eb5ad279c` |
| Hosted CI at that head | `verify` success; `chromium` and `deploy` skipped (source CI only, not a browser run) |
| Block to publish | `experience2/home-flagship/release/production-change/replacement-block-index1.html` |
| Block size / SHA-256 | 108,152 bytes / `d73124abab24d5f493bca97b9bc8f4f9102c1996df78e299c3a454608a656d6b` |
| Block SHA-1 (WordPress `block_hash`) | `78c845b0e4c7014f1241277cf6ca852e475a1713` |

I re-hashed the block from that head on 2026-11-02 and it matches `PROPOSED_PRODUCTION_CHANGE.json`. Confirm this yourself.

**Authorship disclosure:** a previous Claude session built #604. The session writing this hand-off did not change it and has no stake in the verdict.

## What would change on finalvestige.com

One operation: `page-sections.replace` on WordPress page 6, block index 1 (`core/html`, the old Studios hero, SHA-1 `1c97fec5cc356a02fb2f51a092f749c81efcd98c`), guarded by `expected_modified 2026-10-30T09:14:14` and `expected_content_hash 7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. Optional second operation: block 2 (Focus CTA) loses its `aria-label`. Nothing else: no plugin, theme, navigation, other page. Blocks 0, 3 (native Jetpack Dispatch), 4 and 5 must stay byte-identical. On 2026-11-02 the live page was read and still matched these lock tokens.

Rollback: `RELEASE_AND_ROLLBACK.md` (replace with the stored original blocks, or restore the 2026-10-30 revision).

## What to verify (do these, do not take the matrix's word)

1. **Integrity.** Block bytes hash to the values above; `original-block-index1.html` hashes to `1c97fec5...`; the descriptor's apply and rollback parameters are consistent with each other.
2. **Scope.** Diff the replacement block against the original: confirm it is self-contained (inline CSS and JS), contains no external script or font, no tracking, no network call other than the three archival images, and no `eval`, `document.write` or remote `import`.
3. **Safety of inline script and markup.** Look for unescaped insertion of data into the DOM, handlers that could throw and hide content, and anything that could break the preserved blocks (global selectors, `body` or `html` rules, id collisions with the preserved sections such as `#dispatch`).
4. **Accessibility.** Heading outline (exactly one `h1` on the final page), landmarks (the theme owns header, footer and `main`), names and roles of every control, visible focus, reduced motion, no static element with an interactive role, the no-JavaScript path, 320 px reflow. Check the contrast figures against the evidence files rather than the summary.
5. **Historical accuracy.** Read every historical statement (Franklin comparison, evidence cases, method, Observer Lab, Mind & Perception bridge). Flag anything that implies an unsupported connection or states uncertain material as fact. Each case should keep probability, observation and conclusion distinct.
6. **Images and credits.** Three archival images: confirm each credit line, identifier and source link in the markup against `IMAGE_RIGHTS_REGISTER.md` and the original institution's own page. Reproduction sign-off belongs to a **named editor**, not to you, unless the founder names you.
7. **Preservation.** Confirm the plan leaves the Jetpack subscription block, the 72-item Margins strip, Focus Fieldbook links and the Organization JSON-LD untouched.
8. **Performance claims.** `ACCEPTANCE_MATRIX.md` reports lab results only: mobile LCP 4.58 s (Lighthouse simulate), above the 2.5 s target, about equal to today's page with roughly half the bytes. Judge whether that is acceptable and whether the stated method supports the conclusions.
9. **Claims to challenge.** The matrix says: 0 axe violations at seven widths; 0 flagship text nodes below WCAG 1.4.3 by pixel measurement; images identical to their originals (0.9998 to 0.9999); hazard characters stored byte-for-byte on WordPress.com draft 1902. Reproduce what you can.

Reproduction commands are in `experience2/home-flagship/release/README.md` (needs Node 20+, Python with Playwright and Pillow, Chrome). If you cannot run a browser, say so; do not infer a result.

## Read these files first

`experience2/home-flagship/release/` : `README.md`, `ACCEPTANCE_MATRIX.md`, `RELEASE_AND_ROLLBACK.md`, `IMAGE_RIGHTS_REGISTER.md`, `INDEPENDENT_REVIEW.md` (an earlier automated review of an older head; **not** QD), `PAGE_LENGTH_DECISION.md`, `production-change/PROPOSED_PRODUCTION_CHANGE.json`, `production-change/replacement-block-index1.html`, `evidence/`. If you cannot read the private repository, the founder needs to attach these files.

## What not to rely on

- Founder design approval is granted; it is not QD and does not cover safety, source accuracy or image rights.
- Not performed by anyone: NVDA/JAWS/VoiceOver, Safari or iOS, real devices, field Core Web Vitals, and the authenticated WordPress.com render of the exact 108 KB block (blocked: needs a signed-in session).
- The LCP target is not met in stricter lab modes. That is documented, not hidden.

## How to record the outcome

Post a comment on PR #604 with: your name or tool and the date; the exact 40-character head and the block SHA-256 you reviewed; one line per item above marked PASS, FAIL, NOT TESTED or NOT ABLE TO TEST, with the evidence; the blocking findings; and a verdict (`APPROVE` or `HOLD`). If, and only if, you approve, include the three markers the governed lane uses so the record is machine-readable:

```
FVSL-QD-PASS: YES
FVSL-QD-HEAD: 368399842de1bd4fc02598571c0fa29eb5ad279c
FVSL-PACKAGE-SHA256: d73124abab24d5f493bca97b9bc8f4f9102c1996df78e299c3a454608a656d6b
```

Write `FVSL-QD-PASS: NO` otherwise. A pass for this head does not cover the NASA rights sign-off, the authenticated WordPress.com render, or any later commit.

After a genuine approval and the other two P0 items, publishing is the apply step in `RELEASE_AND_ROLLBACK.md` followed by its verification list on the live site.

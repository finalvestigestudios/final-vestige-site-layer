# Flagship homepage: live release record (2026-11-02)

**Status: LIVE on https://finalvestige.com/ and verified.** The Experience 2.0 flagship replaced the old Studios hero (page 6, block index 1). Nothing else on the page changed.

## What was released

| | |
|---|---|
| Release candidate | PR #604, head `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` (draft, unmerged) |
| Block | `experience2/home-flagship/release/production-change/replacement-block-index1.html`, 108,155 bytes |
| SHA-256 | `506aa8d9d9d9c3fe7821d8e479dc8857957667f06f5f6ea5432e3f3ad0fbc7c9` |
| SHA-1 (WordPress `block_hash`) | `8c0dd5c3adce073fd58f5001e0f90d523ffad277` |
| Replaced | page 6 block 1, the old Studios hero, SHA-1 `1c97fec5cc356a02fb2f51a092f749c81efcd98c` |
| Applied | 2026-11-02, WordPress.com site 256784396, page `modified` became `2026-11-02T17:48:13` |

## Gates (all closed before the write)

1. **Independent QD:** ChatGPT, comment `https://github.com/finalvestigestudios/final-vestige-site-layer/pull/604#issuecomment-6593005759`: `FVSL-QD-PASS: YES`, head `bdf01b4a3e...`, package SHA-256 `506aa8d9...`. The comment text was read directly from GitHub before acting. It makes production readback mandatory and states what it did not test (no independent browser, Safari, screen reader or device run).
2. **Authenticated WordPress.com render:** `PR604_WPCOM_DRAFT_RENDER_EVIDENCE.md`.
3. **Named-editor image sign-off:** Bryan Rhodes, Founder, APPROVED (`PR604_GATE_PACKET.md`).
4. **Mobile LCP exception:** founder-approved as a temporary first-release exception, not a standard.

## Procedure as executed, and one deliberate deviation

1. Read page 6 with the connector: lock tokens `modified 2026-10-30T09:14:14`, `content_hash 7afdb933d2ec68fd993ef015c97a6eb9edfe0576`, six blocks, hashes as planned.
2. **Private full-page backup** taken from the signed-in session: 47,091 bytes, SHA-1 `7afdb933...` (equal to the lock token, so exact). Stored outside every repository at `C:\Users\brhod\OneDrive\Desktop\Projects\fv-release-backups\page6-raw-2026-10-30T09-14-14.html`. WordPress revision 1899 (2026-10-30T09:14:14) is a second restore point.
3. Original block 1 confirmed to occur exactly once in the raw page (index 15,503) and to hash to `1c97fec5...`; the replacement re-hashed to `8c0dd5c3...` from the git object.
4. A second connector read immediately before the write confirmed the lock tokens unchanged.
5. **Write:** a single call that refused to run unless the page's `modified`, content SHA-1 and block occurrence still matched the lock, then replaced exactly that block's bytes and nothing else.
6. **Readback through the connector:** six sections; block 1 `block_hash` = `8c0dd5c3adce073fd58f5001e0f90d523ffad277`; blocks 0, 2, 3, 4, 5 unchanged (`6948a35c...`, `abc983ae...`, `f9da4122...`, `e53df692...`, `9454d1e4...`), including the native Jetpack Dispatch group.

**Deviation from `RELEASE_AND_ROLLBACK.md`:** the documented operation is `page-sections.replace`. That connector call needs the 108 KB block passed as a hand-transcribed parameter, where one slip would corrupt the page, so the same replacement was made through the signed-in REST client from the verified file bytes, with the same lock guards and the same post-write hash check. The resulting stored bytes were verified identical to the expected substitution, and the connector's own listing confirms the block hash. The release identity (package, hashes, scope) is unchanged.

**Not applied:** optional operation 2 (removing the Focus CTA button's `aria-label`, WCAG 2.5.3). The QD verdict treats it as separate and it was not explicitly approved for this release; it remains a candidate follow-up.

**Also done with the release (approved):** media-library captions for record 473 (NASA photo) and 474 (Franklin note), exactly as in the gate packet. Private dry-run draft 1902 moved to the trash (recoverable). Live page 6 status remained `publish` throughout.

## Live verification (anonymous visitor, fresh Edge profile; raw results in `evidence/live-release-2026-11-02/live_verification.json`)

| Check | Result |
|---|---|
| Flagship present on the first anonymous load (no cache lag) | yes |
| `h1` | one: "Find what others miss." |
| `main` / footer / old hero / candidate or draft text | 1 / 1 / gone / none |
| Preserved sections | 72 Margins items; Jetpack form `#subscribe-blog` with an email field; 4 `/focus/` links; Organization JSON-LD present |
| Console errors, failed requests on first load | none |
| Case chooser, Franklin compare, Observer Frame B | work; pressed states correct; three archival images load once their cases are selected (890x693, 890x1416, 890x602) |
| Seven chapter anchors (settled) | land at 84 to 110 px, clear of the sticky nav |
| Skip link, reached with real Tab keypresses | focused after 15 Tabs; top-most at all three sample points; 3px outline |
| Overflow at 320, 360, 390, 768, 1024, 1440, 1920 | none |
| axe-core 4.10.2 (WCAG 2.0/2.1/2.2 A, AA, best-practice), four runs at 1440 and 390 | 0 violations |
| JavaScript disabled | flagship, 72 Margins, 3 of 3 photos, Jetpack form and 30 source links present; case buttons hidden |
| `/focus/`, `/sitemap.xml`, `/robots.txt` | all HTTP 200 |

**Not tested:** screen readers, Safari, iOS and real devices; the subscription form was **not submitted** (no real address used); Lighthouse on the live URL; field Core Web Vitals (none exist yet for the new page). Verification used a fresh anonymous browser, so the logged-in admin bar was not present.

## Performance baseline after release (lab; Playwright in Edge; cache disabled; not field data)

| Profile | LCP | FCP | CLS | TTFB |
|---|---|---|---|---|
| Desktop, 3 runs | 1.48 to 1.61 s | same as LCP | 0.003 | 1.03 to 1.14 s |
| Mobile 390 px, 4x CPU, about Slow 4G, 3 runs | 2.42 to 3.14 s | 1.79 to 2.31 s | 0 | 0.93 to 1.41 s |

**The LCP element is text, not an image:** the hero heading's emphasised words on desktop and the opening paragraph (`p.fv-hf__opening-dek`) on mobile. Server TTFB is about 1 s and the HTML is about 89 KB over the wire. This is a different picture from the earlier Lighthouse "simulate" figure of 4.58 s, which is a model, not a measurement. Implication for the follow-up PR: image optimization is not the lever; look at time to first byte and cache behaviour, render-blocking inline CSS, and font loading for that text.

## Rollback (ready, not needed)

Re-read page 6 (`modified` will be `2026-11-02T17:48:13` or later), then either restore the private backup bytes through the REST client, or replace block 1 with `original-block-index1.html` (SHA-1 `1c97fec5...`), or restore WordPress revision 1899. Success is proven when `content_hash` returns to `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. Triggers: a broken interaction, stripped markup, layout or form regression, or the founder's request.

## Watch

Compare Jetpack Stats and Search Console traffic and Dispatch signups against the prior week. The subscription form markup is unchanged, so a drop would point to layout. Field Core Web Vitals will appear in Search Console only after enough real visits.

## Still open

- PR #604 is **not merged**: the release went out as a WordPress content edit, not through the governed Site Layer bridge, and merging a PR that targets `production` with QD markers could trigger that deploy lane. Leave it as the source-of-record until the owner decides.
- The post-release PR for mobile LCP of 2.5 s or better (founder condition 5); see the baseline above.
- Optional operation 2 (Focus CTA accessible name).
- Mobile and device testing, screen-reader testing and Safari remain untested.

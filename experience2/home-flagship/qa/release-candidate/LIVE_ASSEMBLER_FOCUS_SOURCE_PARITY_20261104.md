# Live Page 6 and Assembler header: Focus source-path reconciliation (2026-11-04)

**Decision: SOURCE PARITY VERIFIED; BROWSER / CONVERSION / RELEASE HOLD.**

Read-only resolution of the open question in draft PR #998: Does WordPress/Assembler lack a top-level Focus Fieldbook CTA because the Page 6 editor HTML omits the separate candidate's masthead link?

## Read-only evidence, November 4, 2026
- WordPress wpcom_user_sites(environment=all) returned **only production site 256784396**. No separate staging. WordPress.com Personal has no native clone and no plan upgrade is proposed.
- Published **Page 6**, modified 2026-11-04T14:39:24 (WordPress local timestamp), includes seven linked and resolving chapter destinations, the Franklin folio, 72 Margins entries (0–71), four in-page Focus anchors, and Jetpack markup. The first in-page Focus anchor is in chapter 7, not the first six. This is HTML source order, not measured screen position.
- Active custom Assembler header template part **assembler//header** contains a native WordPress navigation link labelled **FREE EBOOK** pointing to **/focus/** AND a separate plain HTML ebook-strip anchor to **/focus/**. There are two source-level Focus paths in the header outside Page 6.
- The WordPress navigation post ID 5 also contains a Focus link, but its existence does not establish that that separate navigation record is the source of the active header; do not count it as an additional displayed path.
- Published Focus Page **1579**, modified 2026-11-03T14:36:15, retains Jetpack subscription block markup and the link to the Seven Day Focus Fieldbook PDF. This proves source presence, not actual email delivery, subscriber verification, PDF completeness or sales.
- Frozen PR #49 remains at 10495883299d53596992c26a8987f629b2904670; parent draft #998 exact base 4abde7342b2f0d92f614e0cf627d23d2cca77f21. Apollo R&D #158 remains untouched.

## Engineering deliverable
audit_assembler_focus_source_parity.mjs accepts only three local JSON files from read-only connector responses: Page 6, Assembler template-parts.list(area=header), and Focus Page 1579. It checks all live public-content preservation conditions and refuses missing Focus destinations, altered chapters, missing folio, Margins, Jetpack/PDF and wrong IDs. The source is never transmitted; only counts and release status are emitted. Companion Node test file contains 12 independent cases.

**Executed:** Eight V8 tests exercising exact function bodies passed, including missing destination and malformed source negative controls. The real connected WordPress inputs satisfied all eight source assertions. **Not executed:** the full Node checkout, anonymous Chrome/axe, real image transfer, physical mobile screenshots and measured Lighthouse because the isolated runtime cannot reach the public site. WordPress mshots returned a public screenshot URL, not independently inspected pixels. The CI/QD gates remain open.

## Blocker closed and next mandatory work
Do **not** add a third potentially duplicative Focus CTA to Page 6 based only on the missing candidate masthead anchor. Existing native Assembler header source carries Focus in its nav and ebook strip. This closes the **source-only missing-header-CTA concern**, not visual/keyboard or real visitor conversion evidence.

**Offer:** Existing free Focus Fieldbook. **Funnel:** Grok campaign asset ID -> homepage historical record -> visible context-specific Focus path -> independently confirmed Jetpack signup -> independently verified paid order/affiliate commission minus fees/refunds. **Blocker:** source-only comparison was being mistaken for missing visitor CTA. **Change:** reconcile the complete native WordPress header + Page6 + Focus source and add regression protection. **Evidence:** 8/8 function tests and 8/8 read-only real source checks, with 12 Node tests committed but not run. **Owner:** homepage QA for actual visitor click/keyboard and mobile; Claude for attribution and releases; Grok/Praxxis for distribution.

**Next must-pass gate:** Inspect actual anonymous WordPress.com homepage on 320/390/768/1440/1920 and physical 200% zoom. Physically hit-test native FREE EBOOK and the strip link through mobile navigation, keyboard/no-JS, axe 2.2 AA, intrusive popup interference, historical image transfer bytes and honest Lighthouse. Run separate isolated Playground/Assembler candidate tests without conflating those with live Atomic host qualification. Keep production HOLD until exact CI, independent QD, rights QA and founder approval.

No production CMS/theme/navigation changes, new instrumentation, competing UTMs, subscription purchases, affiliate activation, merchant testing, site merge or deployment were authorized or performed.
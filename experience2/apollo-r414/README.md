# Apollo Experience 2.0 — R414 rights-aware archive gallery (isolated staging)

**Status: BUILT + offline fixture TESTED; not installed, not LIVE, production HARD HOLD.**

## Scope and provenance

This additive gallery is separate from founder issue [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) homepage art lane, frozen PR #49 and original NASA Research Desk PR #158. Its six catalogue items come **at runtime** from the exact R411 SourceDrawer PHP file (`efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`, verified Git blob), not a copied staging ledger. The gallery's local CSS is pinned to blob `a5eeb96aeebe5569db4cef0d3d0a0e05fdf99c5f`.

`[fv_ex2_archive_gallery_r414]` renders only when `FV_R414_ENABLED === true`, `FV_R414_STAGING_PAGE_ID` matches the current singular page, `wp_get_environment_type() === staging`, and both source/style identities are exact. Otherwise it returns a simple link to the existing public Apollo investigation. Do not enable this on public WordPress, or edit settings, content or plugins, without independent QD and founder approval.

This is a **metadata-only gallery**: six visually differentiated source cards, no NASA photos or logos, no speculative map locations or relationships. Each card presents its source context, an expandable uncertainty boundary, a primary NASA archive page link and NASA's investigation text. The source shortcut nav and horizontally scrollable card gallery work with keyboard and touch and without JS. Native `<details>` gives a no-JS equivalent, with forced-colors, reduced-motion and print handling. One free article CTA; no new sales buttons, forms, cookies, analytics or paid services.

NASA primary sources: [Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (original ignition not conclusively identified, probable electric arc); [later 102 flammability ignitions](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) (Dec 1967–Feb 1968, not evidence of original initiator); [media-use guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) and [advertising/nonendorsement rules](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). A NASA link does **not** convey photo reuse clearance or imply NASA endorsement. Each specific media asset and third-party credit must be separately reviewed before adding a photograph. No unapproved photo assets are packaged.

## Executed local QA

```bash
php experience2/apollo-r414/qa/test_php.php
python experience2/apollo-r414/qa/test_browser.py
python experience2/apollo-r414/qa/package_evidence.py
```

- PHP: 30 assertions, including NASA exact host and HTTPS allowlist, missing/malformed/extra records, output escaping, two independent instances, no media or scripts, staging default off and exact missing dependency fallback.
- Actual Chromium Playwright via `page.set_content` of PHP-generated markup: six test methods, keyboard fragment and disclosure with JS **disabled**, touch, twelve responsive/special screenshots at 320, 360, 390, 768, 1024, 1440 and 1920px, reduced motion, forced colors, and enlarged base font. Zero document horizontal overflow on fixture in all captured contexts. Importantly a first visual test discovered 33-pixel cards on mobile due to a CSS grid sizing bug; fixed before final QA and recorded in source history/evidence.
- Archived screenshots + test records are deterministic in file membership and manifest, but PNG bytes can vary across browser versions; archive reproducibility applies to identical local inputs, not different Chromium versions.

**Not verified:** actual installed WordPress/Assembler, full original PR #158 template integration, navigated HTTP browser testing and CSP, axe-core (not available locally), screen-reader review, native 400% browser zoom, genuine LCP/CLS, hosted CI exact-head, founder/QD acceptance. The previously observed browser navigation blocker `ERR_BLOCKED_BY_ADMINISTRATOR` is unresolved. Do not equate offline fixture results to production acceptance.

## Conversion-first experiment / governance

Flagship: Apollo 1 historical source trail suitable for a **possible** Grok long-form documentary. Grok owns script and posting, Praxxis source/creator review through TASK-008, Claude measurement and checkout, founder commercial and release approvals. No genuine Apollo published Grok `asset_id` is verified; do not invent one.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Original rights-cleared educator dossier (proposed, **not** a verified SKU) | eventual paid order | no approved SKU, price, rights, merchant, fulfillment | founder/Commerce authenticate merchant and original licensed product before sales CTA | HOLD: no merchant proof or order | Founder / Claude |
| Free NASA evidence experience | gallery → free investigation | mobile/source navigation confidence | R414 staged metadata gallery, one relevant article action | fixture PASS, staging HOLD | Apollo / QD |
| Grok approved long-form | post asset → qualified-human website sessions | no matched actual published post ID, landing UTM, human cohort | verify Grok asset/rights/bio-link limitations in TASK-008; reuse existing attribution, no duplicate scripts | NOT VERIFIED | Grok / Praxxis / Claude |
| Leads/orders → net revenue | confirmed order and refund/fee accounting | merchant settlements, human denominator missing | 7/30-day approved privacy-conscious reporting | NOT COMPUTABLE; clicks/leads not sales | Commerce / Claude |

Controlled path: genuine Grok Apollo documentary **if published/approved** → this primary-source gallery → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → separately cleared relevant educational product (when real, not currently presented). Hypothesis: readable source constraints can improve genuine investigation progression among high-intent educators; **no conversion lift, revenues, customers or attribution measured**. For a future pilot, compute realized net revenue per 1,000 qualified human sessions only from verified paid transactions net of fees/refunds, with cohort sample warnings.

**No merge, public deploy, WordPress post/settings, social post, email, affiliate switch, tracker, checkout activation or paid service authorized.**

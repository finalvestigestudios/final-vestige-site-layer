# The Log Was Not the Voyage — nine-guide navigation release ledger

**As checked:** 2026-11-18, 02:43 Pacific. **Owner:** FV Library Resource Studio. **Disposition:** DRAFT / RELEASE HOLD. **Production pages changed:** 0. **Mail/social/expenses:** 0.

## Why this asset exists

The original 206,173-character compendium #2870 was split into nine separately reviewable Library drafts (#2886–#2894). Without a cross-guide route, a researcher could identify an archival problem in one page and have no path to the next relevant witness. This change installs one original shared, low-dependency nine-stop navigation block at the foot of each child guide. It is a reader map, **not** a reconstruction of any ship's route, and does not add new evidence claims. No public Library card was changed.

**Source of truth (one-block generator):** [ship-logbook-nine-guide-navigation-2026-11-18.js](ship-logbook-nine-guide-navigation-2026-11-18.js); commits `ddf1b0bc` (initial) and `1730193a` (selector-scope correction). Its nine page-local IDs ensure the CSS and aria-current marker belong to the relevant page.

## Guide manifest

| Order | WordPress ID | Pending child slug | Prior blocks retained | Final blocks | New reader links |
|---|---:|---|---:|---:|---:|
| 1 | 2886 | ship-logbook-archive-route | 2 | 3 | 8 |
| 2 | 2887 | ship-logbook-missing-record | 2 | 3 | 8 |
| 3 | 2888 | ship-logbook-vessel-identity | 2 | 3 | 8 |
| 4 | 2889 | ship-logbook-page-anatomy | 2 | 3 | 8 |
| 5 | 2890 | ship-logbook-crew-identity | 2 | 3 | 8 |
| 6 | 2891 | ship-logbook-position-track | 2 | 3 | 8 |
| 7 | 2892 | ship-logbook-port-dates | 2 | 3 | 8 |
| 8 | 2893 | ship-logbook-message-chain | 3 | 4 | 8 |
| 9 | 2894 | ship-logbook-correction-chain | 2 | 3 | 8 |

All nine are WordPress **pages**, parent Library #77, status **draft**, `jetpack_seo_noindex=true` and unchanged scholarly content. The unpublished master #2870 remains untouched. The sidebar/Library public index remains untouched.

## Independent source and rights trail

- U.S. National Archives and Records Administration, [An Introduction to Navy Deck Logs](https://www.archives.gov/research/military/logbooks/naval-deck-logs), inspected 2026-11-18. Distinguishes permanently retained deck logs of commissioned vessels and their administrative purpose. The guide is an **institutional explanation**, not a scanned deck log.
- NARA, [Information NOT Included in Deck Logs](https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs), inspected 2026-11-18. Defines boundaries including work assignments and detached-duty activities.
- FV, [The Archive Trail](https://finalvestige.com/the-archive-trail/) and [Editorial Standards](https://finalvestige.com/editorial-standards/), inspected 2026-11-18. Evidence method, quotations, source limits, image rights and correction policy.

**Rights/media:** The addition uses original Final Vestige HTML/CSS navigation and text; it makes no copies of historic photographs, scans, diagrams, or videos. No AI-generated documentary image. NARA resources are **linked**, not reproduced. Rights of each original source and any future photographs remain item-specific and are documented in the individual guides. This navigation is not an image license grant.

## Structural QA: completed, not a visual-test claim

- Authenticated WordPress **readback** on each of nine draft IDs after scoped append/replacement; **9/9 PASS**.
- Each page: one unique nav-root ID; one `aria-current=page` marker; nine ordered `<li>` items; eight unique sibling links; links to live Archive Trail and Editorial Standards; no duplicate document IDs detected; no blank local-fragment targets.
- CSS correction scoped the active-card selector to the nav root on all nine pages. **9/9 PASS**; no unintended global `.here` selector.
- Each page retains previous Gutenberg blocks; section operations used `expected_modified`, `expected_content_hash` and (for replace) `expected_block_hash`. No page-update wholesale replacement.
- CSS includes two responsive breakpoints (820px/560px), visible `:focus-visible`, readable no-JS ordered list and print rules. **Presence verified; rendering not verified.**
- Page meta: **9/9 draft**, **9/9 parent 77**, **9/9 noindex**.
- WordPress unsigned visitor readback: Library, Editorial Standards and Research Sources all HTTP **200** with existing canonical metadata. Proposed first child route HTTP **404**, which is expected until publication. No public page changed.
- WordPress newsletter settings readback: `email_new_posts_by_default=false`. This is a **default**, not an enforceable per-page delivery guarantee.

## Required release checks — DO NOT PUBLISH UNTIL RESOLVED

1. Authenticated real production-theme browser screenshots and overflow tests at **320/390/768/1440**, not local mock HTML or static media-rule assertions. Test header/foot, nine-card grid, text length, focus ring, tap targets, print and screen reader navigation. Verify role/labels and current-link handling.
2. **All nine sibling URLs currently 404** as drafts; they must be 200 with correct canonical, title, metadata and no noindex when actually released, or navigation must be gated until all pages are live. Inspect full series and Library card/link with a signed-out browser.
3. Enforce first-publish newsletter/social suppression: `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false` (or documented equivalent). The available WordPress page connector does **not** expose those as reliably writable/readable page meta; a mail-default-off setting is insufficient.
4. Actual worksheet keyboard and print checks, all 57 unique existing external URLs' health and item-level access/rights review, including the UK guide and catalog restrictions already qualified in earlier ledgers.
5. Have independent site QA owner #1589 accept the visual release evidence. The Library's published Research Sources count inconsistency is separate issue #1788 and was not modified in this run.

**Release decision:** HOLD. No publication, merge, homepage, Preparedness, Investigations, subscriber/list, social/Grok or spending action.

## Promotion coordination (proposal only)

After release and signed-out 200 checks, offer Grok one 35–50-second explainer: 'A missing log, a missing sailor, and a message that never reached the bridge are three different kinds of absence.' This is not an instruction to post or access social accounts.

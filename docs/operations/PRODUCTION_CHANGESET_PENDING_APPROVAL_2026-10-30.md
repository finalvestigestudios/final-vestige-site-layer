# Final Vestige production-change packet — 2026-10-30

**STATUS: PENDING OWNER'S SPECIFIC APPROVAL.** This file is an exact change proposal, not a completed production write. Never use it to bypass WordPress.com Atomic's explicit-confirmation protocol. Re-fetch the latest page/nav revision and re-run tests immediately before every edit. No spending, plugin activation or visitor-facing write is authorized by storing this document.

## Small, low-risk content patches

1. **Focus SEO field only — WordPress page 1579, /focus/**
   - Currently saved `advanced_seo_description`: `A free 7-page fieldbook: a twelve-minute routine, a seven-day log and a checklist for judging any meditation audio. Enter your email to get the PDF.`
   - Proposed replacement: `Free 52-page Seven Day Focus Fieldbook Complete Edition: seven daily sessions, practical worksheets, a 30-day log, and a guide to assessing audio claims.`
   - Preserve existing 52-page page body, native Jetpack form, JS scroll-anchor helper, download media, subscriber list and URL. Recheck CMS revision/hash before updating only this meta field. Inspect actual rendered `<meta name="description">` after change. Do not rename hosted PDF or claim hash match without its bytes.

2. **Homepage Films CTA accuracy — WordPress page 6, /**.
   - Current live card: `<a class="fv-studios-hero__card" href="/watch/films/">` with badge `04 · FILMS & MEDIA`, copy `Visual investigations, source collections, and documentary work.`, CTA `Watch and research →`.
   - `/watch/films/` is published but says films will appear as they are released. Proposed minimum surgical fix: link the existing card to published `/watch/`, change badge to `04 · WATCH & RESEARCH`, and make card explicitly about *currently available* source collections and recorded materials. Preserve all other homepage blocks and all query attributes. If this changes founder-approved homepage art direction, coordinate with PR #49 before editing.

3. **Primary navigation — WordPress navigation ID 5**.
   - Currently 14 top-level links/groups. Proposal for **review**, not a blind overwrite: a compact 6-item header grouping `Journal`, `Explore`, `The Public Record`, `The Library`, `Labs`, `Free Focus Fieldbook`; preserve every secondary page via Explore page, a verified utility-menu/mega-menu or footer. Keep History Lab/Exchange visible from Explore or their parent areas. Inspect responsive menu screenshots and keyboard/VoiceOver focus before confirming hierarchy. Avoid losing subscription pathways or breaking URLs.
   - Duplicate Jetpack subscription blocks once found in nav were already removed from live navigation; don't reapply stale fixes.

## Identity / resilience

4. **Site Identity** currently `site_icon: 0`, `site_logo:0`, WordPress site title `FINAL VESTIGE`; actual theme header may already have a logo. Wait for explicit founder selection of exact icon/logo assets and title `Final Vestige Studios` before touching global identity fields.
5. **Uptime monitor** `monitor_active:false`, site currently `up`. Ask owner to approve activating Jetpack Monitor for finalvestige.com, then check supported entitlement/notifications and record the observed result. Do not enroll in a paid plan or add DNS/routing changes.
6. **Plugins** 19 installed / 18 active at audit; Site Kit by Google 1.187.0→1.190.0 and WPCode Lite 2.4.0→2.4.1 advertise updates. First test conflict risk on staging, take a backup/restore checkpoint, and request explicit upgrade approval. History Lab LIVEPASS One-Shot Controller, Vector Activator and Vector Attach Probe remain active; do not disable without inventorying runtime hooks/routes and getting History Lab owner confirmation.

## Measurement plan

Use first-party, privacy-conscious analytics only where supported. No new vendor fee by default.

- Standard UTM query keys: `utm_source` (e.g. `tiktok`, `facebook`, `x`, `bluesky`, `linkedin`), `utm_medium=social`, `utm_campaign=focus_52page_launch`, `utm_content=<post_identifier>`. Do not put names, email addresses, account IDs or sensitive data into UTMs.
- Proposed events: `focus_cta_click`, `focus_signup_form_view`, `focus_signup_submit`, `focus_confirmed_subscription` (**only** after genuine confirmed evidence, not merely form click), `focus_pdf_open`, `research_source_open`, `labs_waitlist_click`.
- Each event uses no raw email addresses, no personal health fields and no full page source text; capture page path, campaign/referrer category and anonymous session identifier only if configured with proper disclosure/consent.
- Conversion rate `confirmed_signups / unique_focus_landing_visitors` only when both numerator and denominator are measured consistently; otherwise show `unavailable`, not estimated.
- Weekly report: latest completed 7 days versus preceding 7; views, visitors, new published investigations, new confirmed subscribers (when available), UTM traffic and conversion counts (only when instrumented).
- Editorial cadence proposal: one **evidence-backed investigation per week**, three original short-form social clips pointing to the article, one source-forward Dispatch digest. Apply only after author/editor approves content and sources; no unattended publication.

## Operational release gates

- PR #49 exact QD PASS **not yet issued**, CI dispatch remains failed. Do not merge/deploy.
- Preparedness Archive #136 has safety-sensitive draft work; human review and tests required before publication.
- Desktop Labs #73 requires actual Windows binaries, safety/executable verification, premium licensing and owner approval before website download links.
- Experience 2.0 #150 retains standalone R&D prototype source in archive; staging-only WP plugin candidate, no live install.
- Preserve production backups, published permalinks, Jetpack signup and WordPress source/revision; perform post-change HTTP/browser verification.

# R89 — QA, browser plan and release blockers (HARD HOLD)

### Design/security/accessibility properties provided
- All HTML is under a `.fv89` class; scoped CSS, responsive max widths, no external fonts, images, remote embeds or scripts.
- Native disabled, not merely aria-disabled, merchant control; clear prospective compensation disclosure directly above disabled control.
- A/B share exact full guide core; film only in B. Film **has been rendered offline**, but B honestly presents an illustrated text storyboard and always-visible transcript rather than a broken player.
- Links go only to verified first-party destinations and scholarly/regulatory sources; no merchant earning anchors, injected tracking pixels, autoplay, iframes, newsletter forms or cookies.
- Focus exists; no replacement welcome automation or second email list. Motion reduced via media query.
- B film text does not depict itself as actual experimental footage; no suggestion the McGurk effect proves Zen12's outcome.
- Multi-width style intended for 360/390/768/1440/1920, but NOT browser-tested as of initial commit; must test before final approval.

### Current evidence / known gaps
- McGurk 1976 original abstract, Brown 2018 abstract and open peer-reviewed material, Teramoto & Ernst 2023 open methods, Zen12 public offer/About/Research/checkout, Inspire3 privacy, and both FTC guidance pages inspected November 3, 2026. Literature does not validate Zen12.
- Full paid MP3s NOT tested. Partner acceptance, channel-specific rights, earning URL, approved creatives, full terms, refund implementation, privacy opt-out, legal signoff missing.
- No current paid program price embedded because volatile and subject to checkout changes.
- R89 40-second silent film **rendered offline**, 40.000s H.264 540x960 12fps, but NO first-party site host or playable video in A/B. Local static preview exists in the offline review ZIP; real hosted VTT browser sync remains required.
- Native Node, actual Gutenberg render, full keyboard/screen reader, Lighthouse and conversions require independent execution; do not inflate tests.

### A/B acceptance plan (not an experiment that has occurred)
Content and ethics must be constant between A and B; only original 40s optional first-party media differs once created. Keep poster aspect ratio small and explicit controls, no auto sound or autoplay, lazy load with preload none, caption track, visible transcript and static no-JS fallback; target <=300 KB video where feasible subject to quality/legibility rather than inventing measured results. Record aggregate page views, offer CTA visibility and outbound events only once approved; k-anonymity threshold at least 20, source categories, absolutely no raw referer URL, ID, IP, UA, email, or buyer data. A click is not a sale.

### HOLD gates
All values in claim-source-permissions.json release_gates must remain FALSE. Require signed Inspire3 FV-specific partner permission, separate website/TikTok/email approval, exact approved link and no buyer PII, source/claims/legal and Site QA signoff, tested mobile/desktop accessible first-party film, and founder pinned-SHA publication authorization. No auto merge, deploy, CMS writes, partner outreach, test sends or newsletter changes.

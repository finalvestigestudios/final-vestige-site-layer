# Focus conversion UI: minimal source-only engineering proposal

**OWNER:** Claude + Focus #129. **DRAFT ONLY:** no edits to page 1579, to WordPress subscriber blocks, to homepage #49, or to existing analytics. Cross-team proposal, not a release instruction.

## Scope of proposed patch

Current block `#fvf-gift`: `hidden role="status"`; text “Your fieldbook is ready to download”; anchor to the existing published 52-page PDF with `data-fv-event="focus_pdf_click" data-fv-location="after_signup"`; second paragraph reminds people to confirm by email. Current `fvf-gift-v2` JS selectively unhides by `subscribe` query or `is-subscriber` class.

**Proposed semantic change:** make the free public PDF a normal visible resource rather than an apparent subscriber-success state. Keep the approved download URL and PDF title unchanged, use an ordinary `<section id="fvf-gift" aria-labelledby="fvf-gift-heading">` (no `role=status` or `hidden`), label title as “Download the free 52-page Focus Fieldbook”, set `data-fv-event="focus_pdf_click" data-fv-location="focus_public_download"`, and explain separately: “Joining The Dispatch is optional; please confirm your subscription if WordPress requests it. The welcome email includes this same PDF link.” **Do not** claim email delivery on the strength of a visible PDF. Remove `fvf-gift-v2` only after regression tests show no other page dependency. The visitor's subscription choice and consent text must remain plainly visible.

Alternative if founder insists on post-submit-only panel: it may show a **“request received — confirmation may be required”** UI, but neither the panel nor the `subscribe` query may count as a confirmed lead. This avoids a fake verification token in browser JS.

## Acceptance tests before any separately approved WP deployment

1. At 320/360/390/768/1440 widths and 200% zoom, visible PDF link and sign-up block remain usable without overlap or excessive layout shift.
2. `?subscribe=anything`, `?subscribe=blocked`, no query, logged-in Reader class and anonymous visitor all see the **same** accurate PDF description. A query parameter is not a confirmation.
3. The real Jetpack Subscribe block remains functional and is not replaced with a decorative button; keyboard focus and privacy wording work.
4. `focus_pdf_click` may fire on actual download click only. `confirmed_signup_v1` must not fire from display, click, query, or Reader membership.
5. Private provider-confirmed unique email eligibility + consent time is proven separately without publishing addresses. Deduplicate repeat opt-ins with a durable provider key.
6. Welcome message remains the same 52-page link; verify actual receipt through existing authorized evidence only. Don't create a new subscriber/test send without founder consent.
7. Compare current WP revision/hash before a minimal edit to avoid overwriting Claude's work. Keep homepage frozen priority.

**Data/analytics contract:** `focus_public_download` is a **content engagement label**, not a new lead or paid order. Never relabel history of `after_signup` clicks as confirmed subscribers without provider reconciliation. Migrate only if analytics owner establishes what existing `data-fv-*` attributes actually feed. This proposal adds no new script or paid service.

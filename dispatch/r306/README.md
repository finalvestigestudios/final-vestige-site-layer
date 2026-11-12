# Dispatch R306 — Jetpack post-delivery feasibility and fail-closed control

**UNSENT DRAFT / REVIEW ONLY. No WordPress posts, test emails, settings changes, lists or spending.**

## Newly verified operational constraint

[Jetpack's official newsletter guide](https://jetpack.com/support/newsletter/) (updated November 4, 2026) states that **new post publication** triggers emails; pages, edits of published posts, and custom post types do not. [WordPress.com guidance](https://wordpress.com/support/newsletter/send-newsletter-emails/) (reviewed November 9) uses **the post title as the email subject**. Creating Markdown or HTML files does not itself create a sendable standalone Jetpack email. The six weekly draft issues would require separately approved WordPress post publication and post-level send actions. The founder has NOT authorized them.

The global email-new-posts-by-default setting is currently OFF, but an individual unpublished/scheduled post can override it. A site_can_send=true diagnostic shows platform capability, not permission. Native visual preview occurs in the unpublished-post editor; a test email is a real email and requires separate founder authorization. We did not create an unpublished post to inspect the native preview because WordPress writes remain prohibited. Manuscript preheader metadata has not been verified as a controllable Jetpack email preheader.

## New source and QA

- jetpack_release_gate.py: offline stdlib Python; six independent issue statuses and per-post dispatch risk; requires consent, eligibility, actual welcome/Fieldbook proof, received native email rendering/legal proof, and partner-specific permissions for issues 03/05. No send, publish or network calls.
- tests/test_jetpack_release_gate.py: 20 native executed software-level tests, including post-level toggle override, approved affiliate account without EMAIL rights, missing postal/unsubscribe, preview-not-receipt, and a fully fictional all-green state that still has sender_authorized=false.
- delivery-plan.md: issue-by-issue copy gaps, conversion and founder sign-off plan.
- evidence.md: source-of-truth read-only status and source references.

Run: python -m unittest discover -s dispatch/r306/tests -v

Original [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) SHA d57ccdba3aee8f065e143e101c2945f4f3d01647: 8/8 independently matched Git source blob identities, 6/6 native tests passed. R306 native tests 20/20 passed on identical local and GitHub source. No live WordPress, subscriber, MIME, CI or merchant tests.

Original 4 editorial / 2 commercial allocation remains. Original manuscripts unchanged, prior alternatives NOT_ADOPTED. All 6 HOLD_UNSENT, 03 and 05 HOLD_MERCHANT; 04 original timing headline requires a correction decision. [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) | [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) | [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) | [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Frozen #49 unaffected.

# The Dispatch — per-edition release readiness / source-custody sprint

**DRAFT / HOLD.** Tracking [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion Mind [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked campaign PRs **#175 → #178 → #187 → #194 → this PR**. Frozen homepage PR #49 and WordPress production untouched. All artifacts are review-only.

## Why this is an actual improvement
The existing global evidence gate in delivery/release_attestations.json correctly refuses to approve *any* campaign if either Inspire3 product is unapproved. That is unnecessarily restrictive for historical **noncommercial** issues **01, 02, 04 and 06**. This independent companion gate separates their editorial/source obligations from the two commercial issues **03 and 05** while still requiring real audience consent, an approved WordPress send-path, real received-email review, Final Vestige business postal address, functional opt-out and founder issue/audience/date approval for every single edition.

Run from source checkout:
- python -I -m unittest discover -s dispatch/campaign-2026-mind/readiness/tests -v
- python -I dispatch/campaign-2026-mind/readiness/per_issue_preflight.py
- python -I dispatch/campaign-2026-mind/readiness/build_review_board.py
- python dispatch/campaign-2026-mind/readiness/browser_qa.py (optional installed Playwright + Chromium)

The gate **never authorizes a send**, writes to WordPress, changes settings, imports a subscriber, or activates a product link. An all-green editorial gate returns only HUMAN_REVIEW_CANDIDATE_ONLY. Even all-true merchant attestations cannot pass commercial editions while their guide CTA strings remain deliberately blocked. Bare boolean approvals are rejected; opaque internal ticket and reviewer-role references are mandatory, with no actual PII or token data stored in the repository. No claim is made that this schema is cryptographically secure or an independent legal certification.

## Source ledger, exact live verification — October 30, 2026
WordPress site 256784396 read-only:
- Puységur archive page 1377 **published**, used in editions 01/02.
- Apollo 1 post 434 **published**, edition 04.
- Focus Fieldbook page 1579 **published**, edition 06.
- Dispatch signup page 523 **published** with existing single Jetpack signup, same 52-page Fieldbook welcome.
- Proposed Zen12 /mind/zen12-guide/ (Mind PR #180) and Hypnosis Live /mind/hypnosis-live-guide/ (Mind PR #188) **not verified published**; commercial CTA tokens remain inert.

Live newsletter: subscriptions true, can-send true, email-new-posts-by-default false, email-content-format **excerpt**, zero recent sends. Subscriber diagnostics contradict themselves: total 2, confirmed 2, unconfirmed 2. This is **not** proof of two distinct eligible recipients. The welcome content is configured, but its actual receipt has not been verified.

A real **subscription confirmation** email was found in the connected inbox from October 25. It confirms that one WordPress subscription prompt was generated, not that the subscriber confirmed, not that the updated 52-page welcome arrived, and **not** that any Dispatch newsletter was delivered. Its footer identifies Automattic, which cannot substitute for Final Vestige's own valid postal address when the commercial email rules apply. No contact addresses or tokenized sign-up links were copied to GitHub.

## WordPress and merchant conditions
WordPress post title is the email subject; a separate preheader control is **not verified**. With the current excerpt email setting, a post without a custom excerpt yields approximately the first 55 words; see official https://wordpress.com/support/newsletter-settings/ and https://wordpress.com/support/newsletter/email-appearance/ . Existing six custom excerpts in PR #187 are draft fallback, not tested actual email MIME. Changing the global setting to full-text requires explicit founder approval.

FTC CAN-SPAM covers commercial promotions, including certain promotions of commercial websites: require valid sender identity, honest subject, disclosure where relevant, *Final Vestige's* valid postal address, functional opt-out and timely suppression. Apply a conservative footer/opt-out gate to all six. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

Public Inspire3 promotional pages, commercial consumer emails or generic affiliate invitations are **not** proof Final Vestige's account is accepted or that email affiliate marketing is authorized. Verify account-specific approvals, products, URLs and link rules privately. Seller claims on https://zen12.com/ and https://hypnosislive.com/faq are not independent outcome science; compare with https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety and https://www.nccih.nih.gov/health/hypnosis .

## Two optional fallback editions
If partner approvals remain blocked, contingency/03-meditation-no-offer.md and contingency/05-hypnosis-no-offer.md provide entirely **noncommercial** educational substitutes. They are UNSENT and require a separate founder approval to change the original 4 editorial / 2 commercial draft ratio. Do not silently substitute them or publish early.

## QA evidence and remaining gates
**Executed in local development:** 25 Python unit tests passed on reviewed source plus manifest snapshot; actual Chromium exercised the *static review board* with JavaScript off at 320/360/390/768/1024/1440/1920 px and a separate 390px / 200% zoom check, with no horizontal overflow, page errors or broken keyboard details controls. Local screenshots are available in the separate downloadable review ZIP. These tests are **not** a WordPress delivered-email preview, live site full accessibility audit, actual GitHub-hosted CI, or proof of merchant permissions.

**Still held:** reconcile confirmed audience privately, authorized real Jetpack preview/received test, legal address and unsubscribe in that actual email, valid merchant offer-specific approval, published independent offer guides, final founder signoff. No messages sent or scheduled; no paid platform, signup list, tracking changes or homepage edits.

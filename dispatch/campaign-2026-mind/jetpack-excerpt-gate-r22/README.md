# R22: Jetpack excerpt/full delivery-risk gate (DRAFT · NO SEND)

Parent [draft PR #312](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/312) at exact 17d2976b0be23da220165a0684f1da7df343193d. Governing [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), independent merchant guide lane [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), original six letters in PR #175. Homepage frozen PR #49 not touched.

## Important new finding

Authenticated live WordPress at 2026-10-31 15:33 UTC: newsletter enabled, automatic emails for newly published posts OFF, email content format **excerpt**, sender name Final Vestige, reply-to no-reply, established 52-page Focus Fieldbook welcome configured, zero recent sends. Counts: 2 total, 2 confirmed, 2 unconfirmed, zero suppressed; their bucket semantics can coexist but eligible, deliverable subscriber audience is NOT established.

Official [WordPress Newsletter Settings](https://wordpress.com/support/newsletter-settings/) (reviewed Oct 26, 2026) says an excerpt email uses a post's specifically authored excerpt, or **first 55 words** when no explicit excerpt exists. Original campaign manuscripts are 253–499 body words. An explicitly labeled approximate no-custom-excerpt model finds:

| Issue | Body words approx | Visible in 55-word model | Manuscript CTA in model | Commercial disclosure in model |
| --- | ---: | ---: | --- | --- |
| 01 modern change blindness | 375 | 14.7% | No | n/a |
| 02 historical Puységur | 253 | 21.7% | No | n/a |
| 03 Zen12 buyer evaluation | 477 | 11.5% | **No** | **No** |
| 04 Apollo 1 investigation | 436 | 12.6% | No | n/a |
| 05 Total Focus evaluation | 331 | 16.6% | **No** | **No** |
| 06 attention diary | 499 | 11.0% | No | n/a |

This is **not** a native WordPress preview or received email. Exact WordPress excerpt rules, explicit post excerpt, added template/footer and mail-client behavior can differ. No campaign WordPress post, post excerpt or test email exists. Do not claim WordPress actually delivered any of these truncated emails.

## New source-controlled deliverables

- audit_excerpt.cjs: offline, no-network audit of manifest and six source manuscripts; fails closed when 4:2 allocation, subjects/preheaders, source CTAs, valid hold placeholders or blocked commercial URLs are changed. Never sends or authorizes email.
- tests/test_excerpt.cjs: 28 unit/adversarial checks. Commit was read back and executed with original GitHub manuscript bytes in isolated JavaScript V8 (28/28 passed); a native Node CLI test and hosted CI are **not yet verified**.
- R22_MODEL_SNAPSHOT.json: exact-source model with no personal data and explicit NOT_NATIVE proof classification.
- OFFLINE_REVIEW.html: accessible, responsive six-issue side-by-side comparison. No external product links, subscriber data or tracking.
- WORDPRESS_NATIVE_PREVIEW_PROTOCOL.md: noninteractive operational checklist for future separately authorized CMS preview.
- MERCHANT_AND_COMPLIANCE_CHECK.md: exact seller features, private account-permission finding and FTC gates.
- QA_EVIDENCE.md: exact evidence boundaries.

To rerun on a complete checkout: node dispatch/campaign-2026-mind/jetpack-excerpt-gate-r22/tests/test_excerpt.cjs ; node dispatch/campaign-2026-mind/jetpack-excerpt-gate-r22/audit_excerpt.cjs (the latter prints summary); --write only updates local JSON/HTML files, never WordPress.

## Creative decision required later, not taken

**Option A**: separately authorize full-text newsletter mode, then inspect native Preview email and (if separately authorized) received MIME. Closest to original six full-length letters. **Option B**: retain excerpt mode but author explicit short digest excerpts with clear value, guide CTA and near-offer disclosures; that *changes* the founder-approved long-email format. Do not silently substitute B. Both require final compliant postal/unsubscribe, audience and merchant checks.

WordPress [Send Newsletter](https://wordpress.com/support/newsletter/send-newsletter-emails/) explains that the post title determines subject and that the native Preview email is a no-send action separate from Send test email. **Safety constraint discovered in the official [Email appearance guide](https://wordpress.com/support/newsletter/email-appearance/):** the per-post 'Send this post to subscribers' toggle must be ON for 'Preview email' to appear. Any future founder-authorized draft-only preview must strictly prevent publishing/scheduling while this hazardous toggle is on; never change global automatic email settings or test-send without separate approval. No editor interaction was attempted. Manifest preheaders are unverified as actual Jetpack inbox snippets.

**Every edition: HOLD_UNSENT. #03/#05 additionally HOLD_MERCHANT.** No publication, scheduling, send or test send; no new platform, list, tracking, costs, purchases or WordPress writes.
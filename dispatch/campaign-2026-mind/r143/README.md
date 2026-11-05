# R143 | Dispatch delivery configuration changed relative to previous reports — HOLD (Nov 5, 2026)

**Owner:** Issue #174; companion #171; conversion charter #820. **Base:** Draft PR #1126 at `57a5af0e1fc5e9f354c9918968da54d554b678af`. Original master PR #175 remains frozen at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. PR #201 per-issue QA and PR #49 homepage untouched.

## Material live-setting discrepancy

Fresh **authenticated, read-only WordPress get_settings at 2026-11-05 18:30:53 UTC** returned `email_content_format=full`, `from_name=Final Vestige Studios` and `reply_to=no-reply`. Previous Dispatch authenticated reports through R142 called the mode `excerpt` and sender `Final Vestige`. **These are differences between recorded snapshots, not proof of a particular actor, timestamp, unauthorized change or causation.** Do not silently carry forward the excerpt assumption or revert settings; the founder did not authorize writes.

The parallel WordPress `status` read at 18:30:50 UTC returned Newsletter ON, `site_can_send=true`, `email_new_posts_by_default=false`, latest five notifications `never_sent_opted_out`, totals `total=3`, `confirmed=3`, `unconfirmed=2`, `imported_last_24h=1`. No summing or subscriber IDs. The dashboard is **not** evidence of a subscriber's email permission, welcome receipt or paid sale. The public /dispatch/ page #523 and /focus/ page #1579 were read, and the existing Editorial Standards were reviewed. **No signup submitted.**

## Why delivery-mode drift directly threatens conversion and compliance

The R140/R141 campaign's proposed *excerpt* title/shortened-body cards are **not a verified preview of the currently reported full-email setting**. If complete posts are emailed, the full body could include production notes, inactive placeholders or extra source/disclosure links, and a manually written preheader is not proved to map to native inbox preview text. The original six markdown manuscripts all retain the publisher address and Jetpack unsubscribe sentinel strings. Commercial #03 and #05 also retain inactive future guide placeholders. **Never paste raw source manuscript into a publishable WordPress post** or allow footer sentinels to be delivered. All six require actual native mode-aware preview and founder final approval. A screenshot or synthetic HTML is not native evidence.

## Six-issue first-click decision register

| Issue | Reader intent / canonical first click | Decision |
|---|---|---|
| 01 editorial | Perception promised, but canonical CTA shares Issue 02's Puységur destination | Optional change-blindness CTA PR #1126; founder editorial review first |
| 02 editorial | Puységur documented evidence | Preserve first-party investigation; live link verified in WordPress |
| 03 commercial reserve | Zen12 **Premium**, not Beginner or Advanced | HOLD_MERCHANT; prospective commission disclosure must be near guide CTA; no affiliate URL |
| 04 editorial | Apollo 1 record | Prefer reviewed non-precision title in PR #1104/#1118; original 14-second subject not yet sourced |
| 05 commercial reserve | Hypnosis Live **Total Focus** (33 min, 47 MB), **not** Hypnotize Yourself | HOLD_MERCHANT; no affiliate URL, no fixed price in email |
| 06 editorial | Already-subscribed reader seeks 52-page Fieldbook | Avoid repeat signup loop; optional direct PDF CTA in PR #1126 awaiting review |

Canonical existing ratio = four editorial / two commercial slots. None approved for sending; no alternatives auto-substituted.

## Exact merchant and compliance sources checked (Nov 5)

- Zen12 **Premium** official sales page: https://zen12.com/hnp — 12 levels, 48 MP3 files, seller-advertised 1-year refund promise; a quoted page price is **not independently checked checkout price**. Equivalence between 12 min audio and 1 hour of meditation is not a proven product outcome.
- Hypnosis Live **Total Focus** specific SKU: https://hypnosislive.com/mental-skills/total-focus — seller describes 33-min / 47-MB MP3; dynamic promotional prices appear and cannot be quoted as fixed. Its 14-day return promise requires eligibility review: https://hypnosislive.com/faq.
- Inspire3 affiliate portal: https://affiliates.inspire3.com/ — general claims of a program are **NOT named Final Vestige acceptance, email permission, or an earning link**. Review actual merchant-provided approved email creative/terms *if and when accessible*; not accessed in this run.
- FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — commercial email requires truthful identity/subject, valid publisher postal address, conspicuous opt-out and appropriate compliance.
- FTC endorsement guidance https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — paid/affiliate connection clear beside offer.
- FV Editorial Standards: https://finalvestige.com/editorial-standards/ — source provenance and documented uncertainty.

## Native verification and consent dependencies

1. **Claude/Site QA:** read-only recheck delivery mode and sender before preparing a genuine *non-sending* WordPress visual preview for both full/excerpt modes; obtain only approved evidence, never modify settings without separate permission. Inspect complete post body vs actual email, preheader behavior, footer, rendering, keyboard/mobile. Any actual test email needs separate founder approval.
2. **Dispatch:** validate sender's real **FV** postal address; inspect native one-click/acceptable unsubscribe output and operating behavior via properly authorized safe path; separate welcome *configured* vs *received*, contact-level consent, WordPress.com follower vs Jetpack subscriber. Do not export PII.
3. **Mind Studio #171:** verify named affiliate acceptance, exact email promotion rights, exact earning URL, live approved guide, checkout terms/refund; neither product may send without it.
4. **Claude/Praxxis #820:** trust only confirmed platform signup events and independently reported settled orders; use `utm_source` platform, `utm_medium=organic_social`, `utm_campaign=<cluster>_pilot_2026_11`, `utm_content=<Grok asset_id>`; don't generate new scripts or pretend these events currently exist.
5. **Founder:** final edition body, target audience, legal footer, visual/email rendering and date require explicit approval before ANY send or WordPress publishing.

## Tests / tools

`runtime_truth.py` is offline and GET-free: it reads the redacted snapshot, PR #175 master manifest and manuscripts; emits an unsendable issue-by-issue risk report. `test_runtime_truth.py` covers delivered-mode drift, legal/merchant gates, nonadditive subscribers and revenue evidence rejection. Validated locally with **Python 3.13: 26/26 R143 native tests pass**, plus original master PR #175 **6/6 Python tests pass** against eight byte-identical GitHub-source files. This does not constitute native Jetpack preview, independently received email, or hosted CI. Example:

```sh
python -I -m unittest discover -s . -p 'test_runtime_truth.py' -v
python runtime_truth.py authenticated-snapshot.json ../manifest.json ../issues > audit-result.json
```

**R143 final state: HOLD_UNSENT (6/6); #03/#05 additionally HOLD_MERCHANT.** No live sending, posting, imports, settings, commerce, analytics or social changes.

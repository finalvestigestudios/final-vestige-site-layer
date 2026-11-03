# R92 — Jetpack excerpt truth / newsletter production adapter (DRAFT ONLY)

**Recorded:** 2026-11-03 14:30 UTC. Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); commercial co-owner [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). **Stacked after [R91 #789](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/789)**. Canonical six-issue draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and independent gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) are unchanged. Homepage PR #49 untouched.

## New verified architectural mismatch

Final Vestige's authenticated WordPress settings report `email_content_format=excerpt` and `email_new_posts_by_default=false`. The canonical manuscripts are substantial source-rich letters with carefully composed CTAs, footers and proposed preheaders. **Those manuscripts will NOT simply appear as those full letters in Jetpack inboxes under the observed excerpt setting.** Official WordPress.com Newsletter settings guidance says a custom **post excerpt** can supply the emailed introduction and that its automatic fallback is **55 words**, while the **Jetpack-specific** newsletter guide instead states a **350-character fallback**. Both explicitly support supplying a manual custom excerpt. These differing fallback lengths are **documentation models, not proof of which fallback this connected site actually renders**. Until a real site-specific native preview is inspected, neither automatic fallback is verified. An excerpt email then links to the **WordPress post permalink**, **not automatically the editorial URL mentioned in the manuscript**. WordPress also documents that the **post title** becomes the email subject. Native manual preheader editing is **not established**; our proposed preheaders are planning notes only.

**Implication for conversion and compliance:** A product disclosure or source link deep in a long draft is not necessarily present in the actual email. HTML review boards from earlier PRs are *not* previews of the Jetpack transport. A valid final campaign must choose and explicitly approve (A) Jetpack excerpt/post-first strategy using source-controlled custom post excerpts plus complete on-site investigation and native continued-reading CTA, or (B) separately authorize a mode change and verify native full-text rendering. **This R92 package implements only offline candidate A. It changes no WordPress settings or content.**

### Candidate first-screen copy

`candidate_excerpts.json` holds six newly edited *optional* native post-excerpt candidates, with story/problem hooks, specific limitations and appropriate tone. Commercial reservations remain **03 Zen12** and **05 Hypnosis Live Total Focus**; both excerpts start with a conspicuous **prospective** commercial note even though there is no active earning link. No manual merchant link is included. The affiliate guide destination stays **null**. First-party research links in the JSON are **source/further-reading references only**; Jetpack's actual generated CTA will link to the newsletter post's own permalink. Future newsletter post(s) are not created, published or approved.

This adaptation does **not** approve replacing the six master manuscripts or historical subject candidates. Issue 04 deliberately avoids the unsupported fourteen-second framing identified in R90. All six are still hold. The pilot retains four editorial and two commercial slots, weekly proposed cadence, no schedule.

### Run verified, read-only QA

```bash
python -I dispatch/campaign-2026-mind/r92-excerpt-mode-truth/excerpt_contract.py --check
python -I -m unittest discover -s dispatch/campaign-2026-mind/r92-excerpt-mode-truth/tests -v
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```

`excerpt_contract.py --preview-html` outputs escaped, clearly labeled *simulation HTML* to stdout, without network or sending. `preview.html` and `preview.txt` are standalone, accessible static reviewers (do **not** treat as Jetpack, client-rendered or received emails). Native Python tests include 31 deliberate data-mutation and source/privacy/HTML checks. This does not establish any preheader, sender address, unsubscribe functionality, actual eligible audience, final sales page, or deliverability.

## Verified WordPress and FTC source-of-truth (read-only)

- Authenticated Jetpack status and settings, 2026-11-03 14:30 UTC: newsletter enabled; site can send; default new-post email OFF; excerpt selected; from name Final Vestige, actual configured reply-to no-reply. Five latest posts = `never_sent_opted_out`; no lifetime no-send inference.
- Subscriber status: `total=2, confirmed=2, unconfirmed=2` (internal ambiguity); separate WordPress.com followers endpoint: `email=0, wpcom=2`, no partial error. **Actual eligible email recipients UNKNOWN**. Never add counts or expose addresses.
- `/dispatch/` (page #523) and `/focus/` (#1579) use existing Jetpack subscribers; /focus/ discloses occasional affiliate opportunities and /dispatch/ does not yet align; both published pages unchanged.
- Editorial Standards (#17) requires record/inference separation and material relationship disclosure; adopted here.
- **Official docs (different fallback models):** https://wordpress.com/support/newsletter-settings/ (WordPress.com: 55-word fallback); https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ (Jetpack-specific: 350-character fallback, *updated 2026-10-28*); https://wordpress.com/support/newsletter/email-appearance/ (manual custom excerpt, full vs excerpt); https://wordpress.com/support/newsletter/send-newsletter-emails/ (post-title subject, per-post selection); https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (advertisement ID, physical mailing address and unsubscribe). This project does **not** pick a fallback on intuition: site-specific native rendering is required.

## Latest merchant review / privacy friction (not eligibility proof)

The official seller sales pages https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus repeat effectiveness claims that are **seller assertions**, not specific independent scientific verification of these audio products. Zen12 checkout https://zen12.com/getstarted asks for a mobile number and displays a countdown; its statements about 48 audios and marketing equivalence are not independent efficacy evidence. Official https://inspire3.com/privacy/ permits data sharing with referring affiliates in certain cases per companion Mind R95 review. Final Vestige does not accept buyer-level identity data; any sharing requires explicit opt-out arrangement and partner written terms. Pricing, refund, approved email creative, product-specific Final Vestige affiliate acceptance and trackable link remain **NOT VERIFIED**. Never copy a countdown or price into the email.

## Correct operational next actions (no writes authorized)

1. Inspect the real WordPress **post editor's** actual Newsletter Preview email with the per-post sending toggle in draft/preview context and **do not publish/send**. Check where custom excerpt, read-more link, generated disclosures/footer, images, subject and mobile breaks actually land. If preview cannot be obtained without activation of per-post send setting, stop and seek separate approval rather than toggle.
2. Founder approves final **publication/delivery mode**, whether draft snippets replace originals and individual native post titles; then only in separately authorized content production create WordPress drafts with controlled excerpts and site-side full source trail.
3. Obtain a qualifying real Final Vestige commercial postal address and verify it displays in the **received email** alongside a functioning opt-out link; Automattic's footer address does not substitute for Final Vestige.
4. Privately reconcile recipient eligibility without exposing contacts, obtain merchant-specific email marketing authorization and privacy protections from Inspire3, wait for reviewed **published** guides from #171, and require explicit final founder approval of exact six creative items/audience/schedule.
5. Preserve homepage flagship work, avoid frozen #49, no separate ESP, tracking spend, new list, test send or public WordPress write.

**Decision: ALL SIX HOLD_UNSENT; #03/#05 extra HOLD_MERCHANT.**

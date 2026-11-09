# R239 postcommit QA, actual tool evidence — November 9, 2026 11:40 Pacific

Branch: `dispatch-r239-evidence-first-attention-20261109`. Parent original master PR #175, exact SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. New files confined to `dispatch/r239/`. Original master six manuscripts and frozen homepage PR #49 unchanged. Optional Issue 01 revised proposal is **not adopted**.

## Original master Python suite
Read-only authenticated original source `dispatch/campaign-2026-mind/manifest.json` and six manuscripts verified on current #175 head; the previously source-authenticated October 30 ZIP snapshot was unpacked locally. Executed `python -I -m unittest discover -s original_175_exact/tests -v` using Python 3.13.5 during this sprint: **6/6 native tests passed, zero failures**. Master manifest at this SHA is still `DRAFT_UNSENT_NO_SCHEDULING`. Archived snapshot Git blob SHA matches fetched manifest SHA `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` (new file content not included in that original suite). The complete private repository was not cloned; this is native execution of the verified eight-file master source snapshot, not of a remote checkout.

## Exact committed new source, independent tests
All six new authored files were created on isolated branch. Five new assets plus the *actual source guard* and master manifest were re-fetched from GitHub; identities:

- Markdown alternative `845b9d11a03c235fbed052138bc8b3424aca8729`.
- Plaintext `78689218f2bdf1a3b0b6dde1d283d23630526cb1`.
- HTML review `1d71eb9066d5dfa4805e1361dca83d5002c7b23a`.
- Release contract `4bad09218c74e7da10c48958030d17a54e1dedf0`.
- Original R239 JS source guard `db9ec31cb71b5c2ada24179ee1ab2a1a03297394`.
- Unchanged master manifest `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`.

The exact committed CJS guard source was evaluated as a function in isolated JavaScript/V8 with mocked, nonreading filesystem imports. **Baseline PASS; 16/16 distinct adversarial unsafe mutations REJECTED.** Mutations included wrong CTA, missing citations, fake founder approval, fake merchant email permission, fabricated net revenue, tracked merchant URL, image pixel, script injection, legal-address placeholder removal, source tampering, dishonest subject, 4:2 mix alteration, unapproved UTM tracking, duplicated primary CTA, missing HTML language attribute, master manifest status flip. **Not native Node, browser visual check, WordPress preview, or a real received message.** A static source review confirms inline styling, presentation tables, limited permitted outbound links, visible high-contrast proposed preheader, readable structure, no forms/images/pixels/scripts; no cross-client rendering guarantee.

## Live read-only findings / blocks
Authenticated WordPress at 2026-11-09 19:39Z: Jetpack subscriptions enabled, new-post default emails disabled, full-content email format, from_name Final Vestige Studios, welcome message contains direct 52-page Focus Fieldbook link; total=3 confirmed=3 unconfirmed=2 (NOT additive), suppressed=0. Followers: wpcom=3 email-only=0; this does not identify how many *receive email*. Five recent post jobs were `never_sent_opted_out`; zero confirmed campaign sends. No actual welcome receipt or inbox header/footer test authorized. Live /dispatch/ page 523 and /focus/ page 1579 published; Editorial Standards page 17 read; destination change-blindness article post 1922 verified as published CMS content.

## Source-specific research and merchant check
Rensink et al. (1997) DOI https://doi.org/10.1111/j.1467-9280.1997.tb00427.x and Simons/Chabris (1999) DOI https://doi.org/10.1068/p281059 were independently checked against publisher metadata/abstracts. Avoid eyewitness-unreliability universals; neither study tests meditation or hypnosis products. Exact official Zen12 https://zen12.com/hnp advertises 12 levels/48 MP3 Premium and an **unsubstantiated hour-in-12-minute equivalence**; official Total Focus https://hypnosislive.com/mental-skills/total-focus offers a 33-minute/47 MB recording and unverified concentration improvements. Their merchant pages are not Final Vestige approval, permission for commercial EMAIL, or evidence of final checkout/refund behavior. Current Mind issue #171 reports 16/16 commercial HOLD.

## Commercial-first next action
ONE offer: Zen12 as **provisional**, pending named authenticated acceptance and specific EMAIL permission, validated tracking URL and live reader-oriented guide by Mind Studio. Legitimately confirmed email-receiving subscribers needed before any Dispatch journey; /focus/ display is NOT provider confirmation. Proposed editorial Issue 01 sends interested readers only to the already-published change-blindness article. Conversion may only be counted from independently verified completed paid orders less fees/refunds with source-qualified human-session denominator. No live metrics or A/B measurements have been invented.

## Frozen holds
`HOLD_UNSENT` on all six; `HOLD_MERCHANT` on 03 and 05; `NOT_APPROVED_FOR_SUBSTITUTION` on this optional Issue 01. Genuine preheader rendered by Jetpack, verified sender business postal address, working unsubscribe, recipient eligibility, welcome delivery, and final founder release approval remain unknown. No emails, posts, drafts, settings, subscriber records, payments, pixels, URL activation, social posts, or account spend changed.

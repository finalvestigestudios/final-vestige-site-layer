# Dispatch R343 QA & provenance

**Branch:** `dispatch-r343-canonical-email-offline-previews-20261113` stacked on draft PR #2408 at exact SHA `2c012a9db0fbf58852d0a9733dd45061a2d6c61b`. Draft PR #175 original SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. The independent approval package #201 is a different branch and not touched. This iteration creates only additive `dispatch/r343/` files and NO publishing/settings/email actions.

## Native original test evidence

The prior saved original campaign fixture was locally unpacked, and its **eight** Git blob identities independently checked against GitHub exact PR #175 SHA (see `source_and_gates.json`). Locally executed command:
```
cd <unpacked-master>
python -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```
**Result: 6/6 PASS**: draft unscheduled; 4:2; no active merchant links; disclosures; no false promises; legal gate.

## New preview QA

- Separate local stdlib generator `render_originals.py` emitted six HTML files and six plaintext counterparts plus index and manifest, with 32/32 Python unit tests PASS. Local artifacts delivered separately as a reproducible no-send archive; **the local HTML formatter is not byte-identical to the separately derived GitHub static reviewer** (do not conflate proof).
- GitHub reviewer/static files were produced from the original #175 connector-returned bytes and asserted **64 precommit structural/negative checks** in an isolated JS environment: 6 content+language/table/accessibility baseline, 6 plaintext blocked footer checks, 4 editorial/2 commercial gates, zero merchant links, developer metadata and exact original SHA/filename checks. This is **source-level**, not native browser/client or Jetpack inbox QA.
- All static preview files carry an explicit `HOLD_UNSENT` banner and non-functional legal placeholders. #03/#05 guide links are rendered as **non-clickable text**, with disclosure intact. Neither README nor preview claims actual merchant authorization.
- **Not tested:** native received Jetpack email, actual preheader/headline behavior, CSS support across Outlook/Gmail/Apple Mail, functional opt-out, real FV postal address, subscriber consent reconciliation at individual level, deliverability, email spam placement, authorized merchant link and settlement. No fabricated measurements or live tests.

## Snapshot evidence, 2026-11-14 01:36 UTC, read-only WordPress.com

Newsletter subscriptions enabled, `email_new_posts_by_default=false`, format `full`, display name `Final Vestige Studios`, reply-to `no-reply`, configured 52-page PDF welcome. `total=3 confirmed=3 unconfirmed=2` **overlap**, `wpcom_followers=3 direct_email_followers=0`; actual eligible recipients unknown. Recent five posts `never_sent_opted_out`; a WordPress `site_can_send=true` flag is NOT founder authorization. Live /dispatch/ (page #523), /focus/ (#1579), Editorial Standards (#17) read, left untouched. The /focus/ publicly accessible PDF and signup challenge are separate from real welcome delivery.

## Research and release blockers

Current official seller pages [Zen12](https://zen12.com/), [Total Focus](https://hypnosislive.com/mental-skills/total-focus) and its [FAQ](https://hypnosislive.com/faq) reviewed; health/concentration/meditation equivalence are vendor claims, not product-specific evidence. Public [Inspire3 portal](https://affiliates.inspire3.com/) establishes no FV-specific email promotion authorization. [WordPress native preview](https://wordpress.com/support/newsletter/email-appearance/) ≠ Send test; [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires accurate publisher postal details and functioning unsubscribe for commercial primary purpose.

**Release summary:** All six originals remain `HOLD_UNSENT`, 03/05 additionally `HOLD_MERCHANT`; alternate copy not adopted; email CTA links not activated; actual order/commission/qualified sessions not observed. Realized net revenue per 1,000 qualified human sessions **NOT COMPUTABLE**.

**Operational restrictions observed:** no subscribers contacted, no emails or tests sent, no WordPress posts/pages/settings changed, no products activated, no social content posted, no new service or expense, no homepage PR #49 touch, no merges.

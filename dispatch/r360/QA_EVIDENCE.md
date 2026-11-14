# Dispatch R360 — verification ledger (2026-11-14 PT)

**Stage:** draft PR / isolated source only / all original emails HOLD_UNSENT, commercial 03/05 HOLD_MERCHANT. Parent master #175 `d57ccdba3aee8f065e143e101c2945f4f3d01647`; stacked from R359 #2505 `184cb5a1fd415c26cd721bc3fcb6cf48e7f61c77`. No homepage PR #49 edits, no Mind/Commerce guide changes.

## First-read provenance
- GitHub Issues #174 and #171, latest comments read; #201 and #2505 PR metadata and changed files checked; Grok's actual TASK-008 Google Drive document read.
- Authenticated WordPress newsletter read-only `status` 18:31:28Z, `get_settings` 18:32:11Z, follower stats; live /dispatch/ and /focus/ page representations and Editorial Standards inspected. Existing full-text welcome configuration does NOT equal received email.
- Gmail targeted read-only November 14: one October 25 subscription-confirmation candidate, **no located welcome** or named merchant email permission. Negative search is not proof of nonexistence.
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; WordPress email-native preview/test distinction: https://wordpress.com/support/newsletter/email-appearance/ . Vendor source pages are merchant descriptions only.
- Original six source texts/manifest inspected from prior authenticated master archival fixture. Current master PR #175 HEAD still exact d57ccdba3aee8f065e143e101c2945f4f3d01647.

## Executed native tests
`python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -p 'test*.py' -q`: **6/6 PASS** under local Python, using archived master fixture. `python -m unittest test_subscriber_truth -q`: **15/15 PASS**. The new two exact GitHub source blob hashes matched the local native-tested files (Git SHA-1 object hash):
- `subscriber_truth.py` — `4114ca2857dbf15e110a60086791a7c2a9d7586e`
- `test_subscriber_truth.py` — `6f6377fe4330bf87143ad59f289ee8c3b7e28f19`

All five source/evidence/plan files read back through GitHub's authenticated connector; no unreviewed binary or shared personal information. New classifier intentionally NEVER marks a send safe, even when all **synthetic** evidence fields are present; it is not a WordPress plugin, an analytics deployment, or a production audience reader.

## Explicitly NOT performed
No authorized native WordPress Preview email, browser screenshots, received-message rendering, signup submission, delivery/unsubscribe test, footer address verification, merchant account acceptance/link/permission read from a publisher contract, actual checkout or settled commission. No email/test email sent; no WordPress post/page/settings/list writes; no social posts; no merchant activation; no branch merge; no spend.

## Independent conclusion
The site's ability to send and the public dashboard count **do not prove recipient eligibility or consent**. The live publisher still needs private provider lifecycle reconciliation. Pending that, keep 4:2 draft as-is; honor founder's final approval and commercial rights gate. Earned net revenue per 1,000 qualified-human sessions is **not computable** without independently recorded net paid orders and qualified-human session denominator.

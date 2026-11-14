# R356 exact-source QA and owner evidence, 2026-11-14 PT

## Source-of-truth first (read-only)
- GitHub [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) and [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), newest comments; PR [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), original [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), previous [#2477](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2477) HEAD `96a7ee7e341f575d38267d48d7ff80ecfbef90a8`.
- Authenticated WordPress read-only: /dispatch/ id523, /focus/ id1579, /editorial-standards/ id17. Original editorial rules require primary/near-primary sources, documented disputes, AI-assisted checking, correction transparency and commercial separation.
- WordPress at **2026-11-14T14:58:58Z**: newsletter enabled, auto-post email OFF, sender `Final Vestige Studios`, full content, welcome configured, last five published posts never emailed. Overlapping 3 total / 3 confirmed / 2 unconfirmed; eligible email recipients unknown. **No subscriber addresses exposed.**
- Gmail read-only: existing October 25 subscription **CONFIRMATION**, not a welcome/consent closure/merchant authorization. No verified named Inspire3 EMAIL rights or received Fieldbook welcome from targeted search.
- Grok's existing TASK-008 Drive source: `utm_medium=organic_social`. No new social asset, task assignment or tracking deployed.

## Executed native tests, independently on original PR #175 exact content
The campaign source recovered from a prior local QA archive was hash-checked **independently against eight current GitHub blob identities** at original exact SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`, including manifest, six original Markdown emails and `tests/test_campaign.py`. All eight `git hash-object` values matched GitHub, not just filenames. Command: `python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -p test_campaign.py -v`. **6/6 PASS, native Python 3.13.5**. No original files edited.

## New R356 native tests, actual local implementation
- `python -m unittest -v test_received_email_audit` => **18/18 PASS native Python 3.13.5**.
- New tool `received_email_audit.py` Git blob intended SHA `74180a56bfbe96ad9c6449a9cc2d4774739e4c26`; test blob intended `34d21df0e3e04ce8e6e55233dc7c366b0c5d241c`. Compare exact pushed Git blobs with local tested hashes before claiming this code verified on remote.
- Tests use only **synthetic** RFC822 messages and address `Example City`, no actual unsubscribe/recipient contacts. Mutations check a confirmation mistaken for welcome, missing address/opt-out, sender ambiguity, provider-owned address, simulated previews, unreplaced placeholders, plausible but nonfunctional List-Unsubscribe header, privacy leakage, fake approvals, and exact subject mismatch.
- This tool intentionally **cannot** approve a send even if a locally examined message looks compliant; it returns `HOLD_UNSENT`.

## P0 unresolved, no inflation
1. Named publisher Inspire3 account acceptance + explicit EMAIL rights, issued earnings URL, live vetted presell guide and actual reader checkout/returns: **NOT VERIFIED**. Two commercial issues remain HOLD_MERCHANT.
2. Private provider-authoritative double-opt-in, eligible recipient count and genuine existing welcome receipt: **NOT VERIFIED**. WordPress aggregate counts cannot be added.
3. Native WordPress **Preview email** rendered in actual editor, publisher valid physical postal, final received mail, actual unsubscribe behavior: **NOT VERIFIED**. Static HTML/EML inspection cannot assert these.
4. Real qualified human sessions, authenticated paid affiliate settlements, refunds, fees and attribution join: **NOT AVAILABLE**, net revenue / 1,000 qualified sessions NOT COMPUTABLE.
5. Actual browser/mobile accessibility or native Jetpack HTML in this run: **NOT RUN**. Tests are local unit tests, not production evidence.

No mail sent or scheduled, no subscriber contact/import, no WordPress changes, no merchant URLs activated, no social post, no PR merged, no expenses. Six original emails stay `HOLD_UNSENT`, 03/05 additional `HOLD_MERCHANT`, 4:2 founder draft unchanged.

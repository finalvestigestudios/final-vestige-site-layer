# R366 QA evidence / reproducibility

**Original exact master:** [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Its 8 issue/manifest/test blob hashes matched the pre-existing R361 local archived fixture (including `manifest.json` `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` and test suite `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`); native `python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v` **6/6 PASS** this sprint. README exists on PR but is not part of the fixture.

**R366 in-memory preflight:** 48 source and output assertions, **0 failures**: exact subject/preheader matching, footer placeholders retained, CTA manifest matching, 4:2 edition mix, no activated merchant links in commercial editions, presence of near-offer disclosure and disabled merchant tokens, static HTML containing no executable script/image/pixel/form.

**Artifacts:** 6 original-derived offline HTML previews, 6 plaintext counterparts, HTML index, source+gate JSON map, decision plan, QA ledger. Never claim these are native WordPress or delivered emails, or that this static lint constitutes email-client/mobile testing.

**Unverified:** live subscriber eligibility/double opt-in, actual 52-page welcome received, real public PDF guest access, true email rendering and unsubscribe operation, valid Final Vestige publisher postal address, named merchant EMAIL permission, exact referred checkout price/refund, offer guide live status, independent affiliate settlements and genuine qualified-human session totals. Release gating remains fail-closed.

**Source locations:** official seller https://zen12.com/ ; merchant https://hypnosislive.com/ ; affiliate portal https://affiliates.inspire3.com/ ; WordPress https://wordpress.com/support/newsletter/email-appearance/ ; FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business.

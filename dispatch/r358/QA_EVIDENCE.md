# R358 QA / source-of-truth record

Parent draft PR #2492 `026fffaaf08f0b426730552003f6f13b660ea3fe`, master #175 `d57ccdba3aee8f065e143e101c2945f4f3d01647`, original release QA #201.

**Fresh provider WordPress status (2026-11-14 16:39 UTC, read-only):** enabled; new-post auto mail OFF; format FULL; from Final Vestige Studios; welcome text points to 52-page PDF but receipt not verified; total=3, confirmed=3, unconfirmed=2, do not add; five post notifications never_sent_opted_out. Actual eligible inbox count unknown. Public /dispatch/ and /focus/ both show email inputs, but no submission performed. Site Editorial Standards reviewed: primary records, explicit uncertainty, quotations/numbers, independence from commercial relationships. Live native Jetpack Preview email, test email, delivered message, working opt-out, valid FV publisher physical postal address NOT VERIFIED.

**Source audit:** official https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq read 2026-11-14. Specific 33 min /47 MB; general "most 40 min"; 14-day guarantee qualified by 5 refunded sessions/year in FAQ. Product marketing asserts efficacy without independent product-specific substantiation. Public listing prices vary by retrieved version; current authenticated checkout and any referral net terms not proven. https://affiliates.inspire3.com/ is a public login/marketing page, not a Final Vestige acceptance or EMAIL permission record. Gmail targeted search yielded consumer/promotional material; no account-specific approval evidence identified (search incompleteness is possible).

**Test commands in a complete stacked checkout:**
```sh
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
node dispatch/r358/test_gate.mjs
```
No test is evidence of real inbox delivery or compliance. Native release gates cannot replace real publisher postal and unsubscribe verification.

**Status:** All six original issues HOLD_UNSENT; Issues 03 and 05 additionally HOLD_MERCHANT; this SKU-specific candidate NOT_ADOPTED. No PR merge, email, test mail, subscriber contact, WP write, commerce link activation or spend.

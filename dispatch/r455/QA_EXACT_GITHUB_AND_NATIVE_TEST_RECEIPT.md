# Dispatch R455 — exact-source native QA and release hold receipt

Date: **2026-11-18**. Scope: **isolated, additive source-only draft stacked on R454 #3036**. Owner: Dispatch #174; Mind seam #171; Focus #129; attribution #820. This record is evidence of local code tests and authenticated READ-ONLY site observations; it is **not** a native Jetpack email rendering, received welcome, published campaign, verified partner approval or paid conversion.

## Verified predecessor and non-conflict checks

- Master draft #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` — six unchanged original issues / manifest / 6 Python tests. Previously independently run natively by R448; not rerun in this sprint.
- Safety draft #201 remains separate and unmodified; it already contains a release gate and alternate no-offer letters. R455 deliberately does not recreate its review board.
- R454 #3036 source HEAD `94d34f242638dfc89ccdfcb5127aefa354868f1f` was independently fetched before making this branch. No edits to original `dispatch/campaign-2026-mind/`, earlier `dispatch/r*/`, Mind, Grok, WordPress, or frozen homepage #49.

## Native Python execution and exact blob proof

Local `python -m unittest discover -s /mnt/data/r455 -p 'test_*.py' -v` executed **17 test methods, 17 PASS, 0 FAIL, 0 ERROR**, covering six explicit edition holds, legal footer on all six, native-preview dependency, two exact product identities, seven separate partner proofs, prohibited subscriber export and auto-sends, source count discrepancies, UTM validation/dedup and missing vs synthetic revenue.

Local SHA1 Git blob calculation on tested bytes and subsequent independent GitHub branch readback:

| File | Local tested blob SHA | GitHub returned SHA | Match |
|---|---|---|---|
| `release_contract.py` | `d5410a64fd7059f277223c2aba67d855b5e5036e` | `d5410a64fd7059f277223c2aba67d855b5e5036e` | **PASS** |
| `test_release_contract.py` | `500c1c94231307293dd9b596b05f2164be107399` | `500c1c94231307293dd9b596b05f2164be107399` | **PASS** |

A live-data-shaped offline fixture (not the live provider API inside the code runner) reproduced `SOURCE_CLASSIFICATION_DISAGREEMENT` from newsletter confirmed3/unconfirmed2; Stats Subscribers email3/Reader0; Stats Followers email0/Reader3. It evaluated Issues 01/02/04/06 as **HOLD_UNSENT** (7 unavailable universal proofs each), and 03/05 as **HOLD_UNSENT** (14 unavailable universal+commercial proofs each). These counts describe *missing attestations*, not 7 or 14 different people or purchases. A fully synthetic green fixture can yield `HUMAN_REVIEW_CANDIDATE_ONLY`, deliberately **never send authorization**. Revenue calculation tests used labeled synthetic numbers only; no live sales or traffic was claimed.

The three prose reviews and aggregate JSON were independently fetched from GitHub at this branch. Blob identities: `fada5111c4d10d0678fff13764fa9c6b091aab68` (transport), `aaf233322d3aa2182c3577a5ced23e737921c080` (merchant), `1080189e4aa37a4a1e3dbfbc1ebe647225ed9c57` (consent), `9c9ccefb6879a9fbcdbdbce4ca1c8a4fb48b51aa` (aggregate JSON). **No browser, MIME, WCAG, real preview, deliverability or live conversion test was executed.**

## Fresh source witnesses

- WordPress authenticated Newsletter `status` observed **2026-11-18T20:44:25Z**: total3 confirmed3 unconfirmed2 (separate), suppressed0, imported-last-24h0, site can send, five latest posts `never_sent_opted_out`. Settings: automatic post email OFF, full text, welcome PDF configured, sender display Final Vestige Studios, Reply-To no-reply.
- WordPress Stats Subscribers filters email3/Reader0 vs Stats Followers summary email0/Reader3, `partial=false`; discrepancy unresolved. Email stats posts array empty.
- Public `https://finalvestige.com/dispatch/` shows email entry+Subscribe; `https://finalvestige.com/focus/` shows the free download and signup; `https://finalvestige.com/editorial-standards/` demands visible evidence/uncertainty, affiliate editorial independence.
- Official Jetpack docs: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter/send-newsletter-emails/ . **Native Preview not witnessed**; no approved internal test email sent.
- FTC primary-purpose and postal/opt-out: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Official merchant offers: https://zen12.com/ (standard) vs https://zen12.com/secret/ (different promotion) and https://hypnosislive.com/faq . Merchant self-descriptions **cannot** prove email rights, buyer outcomes or referred checkout.
- Connected Gmail broad targeted search shows consumer marketing mail; R477 Mind's authorized account search still only identified 2026-08-24 **pending** Refersion application, not account acceptance. No subscriber address is reproduced.

## Concrete result and remaining release decision

**Built:** universal six-of-six legal/footer guard; product-exact two-of-six commercial guard; native tested source-crosswalk; original merchant-specific questions; first-party conversion proof docket.

**Tested:** 17/17 Python methods on exact GitHub byte-identical code; live data observed only through read-only official APIs.

**LIVE:** original WordPress newsletter enabled; automatic new-post email OFF; free /focus/ and /dispatch/ pages published. R455 assets NOT deployed.

**VERIFIED REVENUE:** no independent closed paid order, commission ledger or audited qualified-human-session denominator. **Net revenue per 1,000 qualified-human sessions = NOT COMPUTABLE**, not zero.

**Decision:** all six `HOLD_UNSENT`. No subscriber contact, send including tests, scheduling, newsletter settings change, post/page publication, affiliate activation, revenue script deployment, PR merge, social publishing or spending. Final founder campaign release approval required. Keep frozen homepage PR #49 untouched.

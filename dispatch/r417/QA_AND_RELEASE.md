# R417 QA and release receipt — DRAFT / HOLD_UNSENT

Source-of-truth: Issue #174; companion #171, #129, #820; canonical master PR #175 at exact HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`; previous Dispatch PR #2833 at exact HEAD `14a8efc0ee53ec3fad5707741895ab464597d5ea`. This branch is stacked on #2833 and adds only `dispatch/r417/`.

**Pre-branch independent master native suite:** archived source/test files from earlier R409 QA were unpacked in the current run. Each of eight Git blob IDs was checked with `git hash-object` against the R414 prior exact-source receipt; both sampled files `test_campaign.py` and `manifest.json` match live GitHub connector SHA at the still-current #175 HEAD. Native `python -m unittest discover -s dispatch/campaign-2026-mind/tests -v` returned **6/6 PASS**. This is not a claim of a live email render.

**New R417 local Python:** `python -m unittest -v test_merchant_drift_gate` returned **18/18 PASS**; `python merchant_drift_gate.py` returned global `HOLD_UNSENT`, two offer holds, and multiple public price contexts each (3 distinct Zen12 amounts; 2 Total Focus amounts). The suite includes fake permissions and shows no approval state or send path even in synthetic optimistic fixture.

**Source observations:** official Zen12 main and promotional pages, Hypnosis Live Total Focus and FAQ, Inspire3 public affiliate login, FTC guidance inspected on Nov 17 UTC; exact seller URL captures in `OFFER_SURFACE_SNAPSHOT.json`. No verified referred checkout, inferred price guarantee, named affiliate account, private promotion rights or independently documented sale.

**Site and consent observations:** connected read-only WordPress status/settings/followers; published /dispatch/, /focus/, Editorial Standards. The 52-page welcome is configured; its actual arrival is not verified. Total3/confirmed3/unconfirmed2 and Reader3/email0 do not prove eligible unique receiving inboxes.

**Limitations:** No non-sending *native* Jetpack email Preview, inbox-delivery witness, functional unsubscribe, publisher FV postal-address witness, authenticated affiliate portal access, paid purchase report, audited qualified sessions, or actual responsive email-client rendering. Offline HTML is a reviewer specimen, **not** a Jetpack render. Recheck exact committed source and test receipts after PR creation.

**Strict safety:** no emails or test emails sent, no subscribers contacted, no new list/provider, no WordPress/settings/post writes, no merchant links activated, no live social posts, no merging, spending or change to homepage #49. All six issues remain `HOLD_UNSENT`, 03/05 `HOLD_MERCHANT`, original 04 `HOLD_COPY`. No proposed replacement adopted.

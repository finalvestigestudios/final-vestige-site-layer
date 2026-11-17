# R418 exact-scope QA witness

**Upstream:** master six-issue PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`; new isolated draft stacked on R417 PR #2839 HEAD `88a56808dde54d9ddfa8f19341940dcd62345e7a`. No changes to #175, #201, frozen #49, WordPress, newsletter or Grok queue.

**Master native Python:** Previously preserved R414 master archive unzipped in local container and verified against current GitHub PR #175: all eight campaign input/test Git blob SHA1s matched. Python unittest native 6 passed / 0 failed.

**New inline V8 source QA:** 30 assertions passed in the code execution that produced exactly the `analyzeCohort` function body in `revenue_cohort_gate.mjs`. Tests cover fake consent, click-only sales, invalid funds, bot traffic, duplicate orders and leads, missing evidence, PII, 7/30 windows, tiny samples, no-denominator. The committed Node regression has now been **executed natively against source bytes exactly matching GitHub's blobs: 18/18 assertions PASS**, independently of the inline V8 30/30. The local engine blob is `733e8b622e9556ecdde347bbfb3b59134a225a9a` and test blob `6ac7deb4e32f2fd48b2a230b3274ed6854482de7`, both identical to remote GitHub at the pre-QA-update PR HEAD. This demonstrates synthetic deterministic correctness only: no real Jetpack or merchant records were supplied.

**Legal and platform:** WordPress GET settings/status and independent follower stats were read-only at Nov 17 07:34 UTC. No actual native Jetpack email Preview, no actual received welcome, no verified founder postal address or opt-out; no private Inspire3 permission/earning link. Merchant and FTC official public docs used only to ground claims, never as authorization. Offline reviewer HTML is static; no actual browser or email-client acceptance claimed.

**Commercial KPI:** NOT COMPUTABLE; zero claims about measured paid sales, actual subscriber count, A/B results or qualified human traffic. **All six HOLD_UNSENT.** No new list, script installed, email, test email, subscriber contact, public posts, settings changes, affiliate activation, purchase, merge or money spent.

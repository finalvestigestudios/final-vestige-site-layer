# R224 | Critical manuscript lineage and copy-approval reconciliation — NO SEND
Checked 2026-11-08 PT / 2026-11-09 UTC. Master Issue #174; related #171, #129 and #820.

## Substantive finding
It is **NOT accurate** to describe the six manuscripts under the current stacked Dispatch branch as byte-identical to the original founding draft PR #175. The original PR #175 remains intact and has exactly the first commit shown below. However, six original issue paths and their manifest have been changed **on the stacked branch**, beginning with review/copy improvements in DRAFT PR #178. The R223 #1676 pull request itself adds files only, but its PREVIEW BODY specimens and 162 source-level tests are based on the *revised stacked text*, not the unmodified #175 body.

- Original master PR #175: `d57ccdba3aee8f065e143e101c2945f4f3d01647`, unmerged DRAFT, original version.
- Copy/research revisions in PR #178: `aa2f0deff830589bc283b5770ccd451000a49dd2`, stacked atop #175; it explicitly lists all six issue source files and manifest as changed.
- R223 #1676: `c8abb1b3394a8ec7c4f0e6add961c76fd91ad3d5`, stacked; its own diff only adds R223 files.
- Drift at exactly **7 of 9** tracked source paths: SIX issue manuscripts and manifest. Original README and original six-test module are unchanged. Every row and exact Git blob ID is pinned in LINEAGE_LEDGER.json.

### Meaningful editorial differences (not a judgment that the revisions are incorrect)
1. Issue 01 gains the 1998 Simons/Levin door-switch field experiment and a more specific archive bridge; original was short.
2. Issue 02 gains a narrated May 4, 1784 Buzancy case and sources; source and quotation checks remain required.
3. Issue 03 gains a practical 1+9+2-minute exercise and sharper seller-claim distinction; no offer permission.
4. Issue 04 subject changes from **Fourteen seconds** to **Seventeen seconds**, with NASA report timestamps. This is a consequential factual correction and requires original-source verification.
5. Issue 05 gains a three-minute attention baseline and specific 33-minute format mention; product claims must remain qualified.
6. Issue 06 gains a source-cited diary study and substantially different opening; its ending sends existing subscribers to /focus/, a signup-oriented page, rather than a subscriber-safe PDF access route.
7. Manifest changes CTA 01 and several subjects/preheaders (and updates explanation of 2/2+ unconfirmed-count semantics).

The revised evidence-based copy may be superior to the original. **No claim is made that PR #178 was unauthorized**, only that its existence must not be hidden by the narrower claim that R222/R223 introduced zero changes to old paths. Founder approval of FINAL SELECTED campaign creative has NOT been found; the six original/revised versions must be treated as two distinguishable editorial versions, not silently substituted.

## Native / source verification
Run `node dispatch/r224/verify_lineage.cjs` from a repository checkout that has both commits. It retrieves Git blobs using `git show`, computes their real Git SHA-1 object IDs from bytes, validates the precise nine-item ledger, validates the 4 editorial / 2 provisional-commercial mix and all-null merchant earning URLs from BOTH manifests, and emits a fail-closed machine-readable result. The script **never** makes publication/email/WordPress/merchant/network calls and ALWAYS returns `HOLD_UNSENT` on a successful audit. `node --test dispatch/r224/test_verify_lineage.cjs` covers mutation rejection separately. Test results from a local test fixture do not constitute a native checkout of private PR #175.

## Ethical conversion consequence
Issue 06 goes to confirmed subscribers who received the Fieldbook link in their welcome. The existing CTA to `/focus/` may invite re-subscription, complicate event attribution, and create friction. A one-CTA subscriber-safe alternative in `ISSUE_06_CTA_DECISION.md` points to the SAME public PDF configured in Jetpack welcome, with no second opt-in. This alternative is **NOT approved**, NOT inserted into any of the six issues, and must be link-verified and reviewed before future use. A PDF click is never a signup or a paid order.

## Legal/provider release stop
WordPress.com diagnostic at 2026-11-09T03:38Z: newsletter enabled / site_can_send, new-post auto-email OFF, FULL content; total=3, confirmed=3, unconfirmed requests=2; follower report email=0 and WordPress.com=3. Nonadditive. Actual email-eligible audience unknown. Welcome template includes 52-page Fieldbook but receipt unknown. Valid publisher physical postal address, actual unsub footer + behavior, genuine received Jetpack content, merchant-issued links + EMAIL rights, and independently reconciled paid orders ALL unverified. Vendor Total Focus pricing conflicts between indexed snapshots and prior direct pages; no price goes in buyer emails.

### Release decision
All 6: **HOLD_UNSENT**. Commercial 03/05 additionally **HOLD_MERCHANT**. The founder retains the approval of which manuscript version is final, audience, schedule and sends. No WordPress/site/list/email/affiliate/social activity is authorized. Homepage/frozen #49 unaffected. This audit does not claim the original native Python suite ran in this run; source IDs are connector-verified, while native execution from a private checkout remains pending.

## Specific action ownership
**Dispatch:** pin original vs revised lineage and no-send review; test source and consent, once permitted. **Mind #171:** affiliate email rights/issued URL/current buyer-guide proof. **Claude/Focus #129:** no duplicate signup prompts, safe lead dedupe; inspect PDF experience, not a source of subscriber status. **Site QA:** received sender/footer/legal postal and Jetpack native preview after separate authorization. **Commerce/Praxxis #820:** attributed paid order and net revenue, not clicks. **Grok/Praxxis:** preserve TASK-008 ownership of actual creator IDs; no social posting by Dispatch.

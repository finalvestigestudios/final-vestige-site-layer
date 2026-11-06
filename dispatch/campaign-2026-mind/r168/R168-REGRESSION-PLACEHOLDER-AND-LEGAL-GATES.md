# R168 native received-email placeholder defect — reproducible regression and fix
**2026-11-06 PT · source-controlled only · UNSENT/HOLD.** Inherited R167 checker from [PR #1290](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1290). No live WordPress change.

## Finding
The previous Python `PLACEHOLDER` regex recognized `[INSERT_POSTAL]` and `{{VARIABLE}}`, but **not the canonical campaign's exact double-bracket placeholders** such as `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]`. Further, `has_no_placeholders` searched only visually extracted text, not an HTML anchor's `href`, so a pending `[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]` link could slip through with innocuous link text.

**Actual reproducer (synthetic MIME ONLY):** A valid `EmailMessage` with final campaign-style double-bracket postal/opt-out text and a pending commercial guide URL yielded `checks.has_no_placeholders == true` under exact inherited source `b6557db6b3af94e38f36974101ffb64a133f613f` while other evidence attestations properly kept `HOLD_UNSENT`. Thus this was a **false-positive *one check***, not an observed mis-send and not a total bypass of the hard release hold.

## Corrective change
- Update `dispatch/campaign-2026-mind/r167/received_eml_preflight.py`: add a bounded explicit double-bracket regex alternative while retaining the prior single-bracket and curly-brace detection.
- Inspect `plain + '\\n' + html` for unresolved tokens, **including HTML attributes**, instead of only concatenated visible text.
- Add three native unit tests for double-bracket legal placeholder, hidden anchor-href merchant guide token, and a clean fixture.
- Always return `HOLD_UNSENT` as before; never treat this checker as proof of legal compliance, actual email delivery, permissions, real unsubscribe or recipient consent.

## Native and source integrity evidence
Local existing R167 source/test initially verified against original GitHub blob SHAs `b6557db6b3af94e38f36974101ffb64a133f613f` / `5c6dfd0e12fc99dc1d8614fc2ca104f648986d24`. Synthetic pre-fix check: **`has_no_placeholders=true`** erroneously. After local patch, `python -I -m unittest discover -s . -p 'test_*.py' -v` → **19/19 PASS** (16 inherited + 3 new). Synthetic after patch: **`has_no_placeholders=false`**, **`has_no_placeholders` included in `failed_gates`**, **`release_decision=HOLD_UNSENT`**.

Exact new GitHub content blob SHA matches local `git hash-object` on both native-tested files:
- source `70c19b5dbcbe16e668d2230e2eefc19011f07d4c`
- tests `2f43362c49c8ed33ca67625232fceedf657901e0`

This proof is **local native Python + exact Git object readback**, not hosted CI, not a genuine Jetpack MIME or real subscriber message.

## Release-blocker verdict
Even with improved source scanning, provider-native email eligibility remains unknown (`total=3/confirmed=3/unconfirmed=2` overlapping); configured Fieldbook welcome does not prove receipt; native signed-out Focus signup is unverified; preview HTML is not a genuine WordPress editor `Preview email`; valid **Final Vestige** publisher postal address, actual Jetpack unsub and its operation, and merchant-specific Inspire3 EMAIL promotion rights/earning links are not verified. Do NOT send test email or ordinary newsletter, publish or schedule. No traffic or paid conversions inferred.

Conversion-first owners: Claude/Site QA live Focus integrity; Dispatch actual subscriber consent/welcome/preview and legal proof; Mind #171 exact partner authorization; Commerce/Praxxis settled net cohort reporting. Master [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), commercial [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), capture [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). CAN-SPAM official https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

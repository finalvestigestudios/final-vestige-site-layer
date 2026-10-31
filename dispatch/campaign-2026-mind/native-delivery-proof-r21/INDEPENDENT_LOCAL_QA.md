# R21 independent local verification — October 31, 2026

**Parent:** exact existing Dispatch R20 draft PR #307 at commit `ba2e78a3a1d2f6e44b05a9ff47282492b7517f16`. New R21 files are **additions only** under `dispatch/campaign-2026-mind/native-delivery-proof-r21/`; no existing newsletter, manifest, sender configuration, test or preview changed. Issue #174 governs; Issue #171 merchant-eligibility handoff; frozen #49 untouched.

## Actual execution (not simulated)

- Reconstructed the PR #307 source from the prior issue-by-issue archive packages **without editing any source**, then independently fetched `27` exact files (six issue manuscripts, six Python test modules, 13 preview HTML/txt/index assets, preview generator, manifest) from GitHub **at PR head SHA** and compared `git hash-object` for each: **27/27 identical**. Thus the local campaign source/tests are byte-identical to the tested R20 GitHub head, not merely logically equivalent.
- Executed `python -m unittest discover -s dispatch/campaign-2026-mind/tests -v` on that source: **74/74 PASSED, 0 failures**.
- Executed new `python -m unittest discover -s dispatch/campaign-2026-mind/native-delivery-proof-r21/tests -v` using fully **synthetic** RFC822 emails only: **41/41 PASSED, 0 failures**. Test covers subject parity, both content alternatives, `List-Unsubscribe` syntactic evidence vs user-visible opt-out, one-click *claim* vs real functionality, redacted report safety, simulated malformed/missing header/oversized sample, exact private postal substring, commercial disclosure, unresolved placeholders, all-six release hold and no network mailer code.
- Executed `node dispatch/campaign-2026-mind/tools/build_previews.cjs --check` on original output: **13/13 preview assets identical**.
- Verified no actual `.eml` or private postal address was read, no external links clicked, no WordPress or GitHub homepage data changed by this local test, no test email sent or scheduled, no subscribers imported/contacted.
- The native `local-content-safety` GitHub Actions workflow on the parent PR #307 had a **failed** run in earlier evidence; its root cause was not established. Local results are **not** hosted CI clearance. Investigate this R21 branch's run separately; neither edit nor pay for the shared runner without evidence and approval.

## Evidence limits

A synthetic MIME proves the parser's behavior, **not** that Jetpack creates this exact shape, preserves the planned preheader, populates source links or legal footer, delivers the welcome message, or correctly handles one-click unsubscribe. The real received MIME must be obtained only following a separately authorized test. Our own tools do not authenticate the actual sender, recipient consent, URL functionality or lawful postal address. For that reason every report **always remains HOLD_UNSENT_UNVERIFIED**.

Official references: [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC endorsement disclosure](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), [WordPress native emails](https://wordpress.com/support/newsletter/send-newsletter-emails/), [Zen12 About](https://zen12.com/about), [Zen12 checkout](https://zen12.com/getstarted), [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus).

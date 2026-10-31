# Dispatch R14 — real-browser signup acceptance instrument

**Scope:** Independent read-only browser acceptance tool, stacked on [draft PR #261](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/261), original [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), editorial [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) and Mind [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original six editions unchanged. All HOLD_UNSENT.

## Actual new capability, not a duplicate of R13

R13 established saved Jetpack subscriptions Gutenberg blocks on both live pages; the REST rendered response instead exposed self-link anchors and no email inputs. Neither observation is a real user-browser acceptance test. R14 uses Chromium/Playwright to inspect the public logged-out DOM, recognize a visible email field, activate ONLY an anchor or an explicitly non-submit button inside the subscription block, and classify a normal form, an opened modal, a suspected self-link loop, or lack of a safe signup control.

No email is entered. No form is submitted. No subscribers are added. No test-email is sent. No merchant or WordPress account settings are touched.

## Run instructions for a network-enabled authorized operator

Install Playwright and Chromium locally (no new newsletter service or subscription required):

~~~bash
python -m pip install playwright
python -m playwright install chromium
python dispatch/campaign-2026-mind/browser-proof-r14/no_submit_signup_probe.py --json signup-readonly-results.json
~~~

The only default sites are https://finalvestige.com/dispatch/ (published page ID 523) and https://finalvestige.com/focus/ (published page ID 1579). The probe creates a separate anonymous browser context for each, uses no saved subscriber data, strips URL querystrings, fragments and credentials from output, and omits screenshots unless the operator explicitly requests --screenshot-dir. Other production domains cannot be targeted through the custom URL override, which accepts only loopback fixture hosts.

### Result classification

- FORM_PRESENT_LABELLED: visible labelled email field; not evidence of subscription completion.
- FORM_ACCESSIBLE_AFTER_SAFE_CLICK: the subscribe link or non-submit button exposes a labelled field; not an actual opted-in subscriber.
- FORM_PRESENT_NEEDS_LABEL_REVIEW or FORM_AFTER_CLICK_NEEDS_LABEL_REVIEW: visible field exists but lacks a reliable programmatic name; a placeholder alone is not an accessible name.
- SUSPECT_SELF_LINK_LOOP_NO_FORM: clicked link returned to same path with no email field. Requires independent human confirmation, not proof the production page is broken.
- NAVIGATED_NO_FORM_NEEDS_HUMAN_REVIEW / NO_SAFE_CONTROL_OR_FORM / BROWSER_PROBE_ERROR: still blocked for acceptance.

## Tests actually run (2026-10-31)

Command: python -m unittest discover -s dispatch/campaign-2026-mind/browser-proof-r14 -p test_*.py -v

**8 of 8 passed** with actual Python and Chromium local synthetic DOM fixtures: standard labelled form, JS-revealed modal, safe-link-revealed form, same-page dead-end detection, submit-button avoidance, placeholder-only accessibility detection, URL query/token redaction, and URL credential redaction. Original source bytes were committed and Git blob hashes compared to locally tested bytes. These are offline fixtures using page.set_content, **not real public page navigation or Jetpack email rendering**.

The execution environment blocks navigation even to loopback URLs with ERR_BLOCKED_BY_ADMINISTRATOR, and cannot resolve production finalvestige.com. That limits live-browser observation; it does NOT establish a public signup failure.

## Independent new CI finding

Connected GitHub Actions inspection on parent R13 SHA f142e0a2f788ce41e23ca677819c142eab6bac58 found **Dispatch Campaign QA (draft safety) workflow run 41177595807 FAILED**, job 124468261871 local-content-safety. The job-log endpoint returned HTTP 404 BlobNotFound and detailed job-steps API returned an empty array. Therefore the exact failing command remains unknown. The workflow runs Python campaign tests, Node syntax checks and generated-preview snapshots. Do not claim green CI or alter the workflow based on speculation. R14 does not edit the workflow.

## Current live source-of-truth checks (read-only)

WordPress newsletter.status as of 2026-10-31 07:38:29 UTC: total=2, confirmed=2, unconfirmed=2, suppressed=0, site_can_send=true, recent_sends empty. This is a count inconsistency, not evidence of four distinct people. WordPress newsletter.get_settings as of 07:38:31 UTC: subscriptions enabled; automatic new-post sends OFF; excerpt email mode; no-reply sender Final Vestige; welcome message links the already-existing 52-page Focus Fieldbook. Received welcome and actual email MIME remain unverified.

Connected Gmail searches through Oct 31 returned consumer Inspire3 sales messages but no account-specific approval or written opted-in email marketing permission. The public [affiliate invitation](https://affiliates.inspire3.com/) is not proof of acceptance. [Zen12](https://zen12.com/about) advertises twelve-minute sessions, twelve levels and four styles, while [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus) advertises a 33-minute, 47 MB audio. Merchant efficacy claims, pricing and refund copy are not independently guaranteed. The original Issue 05 numeric refund/catalog wording needs founder/editorial approval before any proposed change; both first-party commercial guide CTAs are not published.

The [Editorial Standards](https://finalvestige.com/editorial-standards/) require visible uncertainty and source-grounded reporting. The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires appropriate truthful sender and subject, physical postal address, and opt-out for qualifying commercial messages. A 4:2 editorial/commercial content mix is not a categorical legal exemption.

## Strict release decision

All six original weekly drafts remain **HOLD_UNSENT**; issue 03 and 05 remain **HOLD_MERCHANT**. No newsletter send, test send, post publication, subscriber or WordPress write, affiliate activation, merchant inquiry, original issue substitution, or frozen homepage PR #49 change.

Next evidence is a separately authorized genuine public browser walkthrough without submitting, private subscriber/consent reconciliation, native no-send email preview, separately authorized received email/MIME, Final Vestige physical business address and unsubscribe rendering, published audited warm-up guides, merchant SKU/channel-specific written permissions and links, and explicit founder authorization for exact creative, audience, date and send.
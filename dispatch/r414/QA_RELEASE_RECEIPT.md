# R414 independent QA and release hold

**Timestamp:** November 17, 2026, 03:41 UTC. This receipt distinguishes tests of exact GitHub source from tests of a separate local draft.

## Exact latest master PR #175
- Read #174 latest comment, Mind #171, open draft PR #201 and latest prior Dispatch #2818. Master PR #175 remains at `d57ccdba3aee8f065e143e101c2945f4f3d01647`.
- All eight GitHub master blob SHAs matched the independently extracted local canonical source: `86df98ad...` manifest, `fd7f05e3...` test suite, and six original issue Git blobs.
- **Native Python 3.13.5, original canonical suite: 6/6 PASS** (`python -m unittest discover -s campaign-2026-mind/tests -v`). No original issue rewrites.

## New exact remote GitHub R414 specimen
- Fetched six committed files back from branch and checked their content: **40/40 V8 static assertions passed** including source links, single first-party editorial CTA, no merchant link, no tracking pixel, release hard-stop, HTML lang and heading, proposed subject/preheader lengths, disclosure/legal placeholders, unknown eligible inboxes, and unknown private merchant rights.
- Exact six GitHub blob SHA identities:
  - `ISSUE01_DOOR_STUDY_OPTIONAL.md` `306318732742b27a8b4860be368e7b3badbf40c8`
  - `ISSUE01_DOOR_STUDY_OFFLINE.txt` `0c23525eab97c72a78556c3e73f48f2ea447ccda`
  - `ISSUE01_DOOR_STUDY_OFFLINE.html` `07971d1290f4cc89080045aaecfd1d9122b3a103`
  - `CLAIM_AND_WITNESS_MANIFEST.json` `8f42326c2fc090d5db02ffc46ec84d4b1efad687`
  - `CONSENT_EMAIL_AND_REVENUE_DOCKET.md` `ff90f96720dcab37fb25881db375f955b659e620`
  - `test_release_gate.py` `f9b8a10efef82ba27bed33ee99219bea8136fd5a`.
- Committed new Python tests are available for reviewers, but **were not executed natively on the exact GitHub-produced R414 file bytes**. Do not cite the 40 V8 assertions as Python execution.

## Separate local draft — local tests, not exact same GitHub specimen
- Local independently authored door-study manuscript + offline HTML/plaintext + native read-only witness Python tool: **54/54 native Python tests PASS**.
- Actual installed Chromium, local offline HTML via memory injection, **7/7 viewports PASS**: 320, 360, 390, 768, 1024, 1440, 1920 px with CTA visible, zero horizontal overflow or page errors.
- First browser pass failed horizontal overflow at **320/360/390 px**, because long hard-stop placeholder words expanded the table to 450 px. After CSS `overflow-wrap:anywhere;word-break:break-word;table-layout:fixed`, all seven passed. Exact GitHub specimen has corresponding CSS and passed static inspection, but was **not independently rendered in Chromium**.
- Browser was installed at `/usr/bin/chromium`; Playwright's bundled binary was absent, and `file://` was browser-blocked, so HTML content was injected into isolated browser memory. This is offline rendering only.
- All screenshots/test logs are local reviewer artifacts; they are not provider inbox evidence.

## Hard stops: no release
- WordPress authoritative read: newsletter ON, automatic post email OFF, full content, no-reply sender, Fieldbook welcome configured. Status total3/confirmed3/unconfirmed2 and followers WPcom3/direct-email0 are **not additive**. Distinct eligible recipients unknown.
- No native WordPress email Preview, no authorized inbox receipt, no actual welcome witness, no real Final Vestige postal address/opt-out render/function evidence, no product SKU-specific affiliate email rights, no approved live warm-up guides and no settled affiliate purchase.
- Native Jetpack post title/subject behavior and custom preheader are NOT independently confirmed for this draft.
- No production WordPress changes, email/test email, subscriber contact, imports, affiliate links, scheduling, list modifications, PR merge, or spending.
- Revenue per 1,000 qualified human sessions **NOT_COMPUTABLE**, not zero. A setup click is not a paid order.
- **All six canonical issues HOLD_UNSENT**. Issue03/05 HOLD_MERCHANT; original Issue04 HOLD_COPY; new optional Issue01 NOT_ADOPTED. Final founder approval is required.

Sources: https://doi.org/10.3758/BF03208840 ; https://finalvestige.com/2026/11/02/change-blindness/ ; https://zen12.com/about ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://affiliates.inspire3.com/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

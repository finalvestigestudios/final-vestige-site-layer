# Dispatch R423 — independently repeatable execution and release receipt
**Run window:** 2026-11-17 12:28–12:45 UTC (authenticated WordPress status as of 12:30:38 UTC). **DRAFT, UNMERGED, UNSENT.**

## Independent original campaign test
The R422 QA archive available in this run includes the eight original master campaign files (six Markdown letters, manifest, Python tests). I independently extracted those bytes, ran \`python -m unittest discover -s tests -v\` against the exact bundled files: **6 tests, all PASS**. I separately called GitHub fetch_file for each of those eight file paths on original master PR #175's published head \`d57ccdba3aee8f065e143e101c2945f4f3d01647\`. All eight fetched Git blob IDs matched a locally computed \`sha1('blob '+byte_length+'\\0'+bytes)\` for the extracted files: 8/8 IDENTICAL. This proves the executed source is identical to original PR #175's specified commit, **not** that all stacked production branches or WordPress emails are tested. Master campaign remains unchanged.

Blob IDs:
- issues/01: \`039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8\`
- issues/02: \`faa207ab7deafd86460d36f8c17fe62d392d0e14\`
- issues/03: \`aeeef34efea0cc281f69901488e4501fea851245\`
- issues/04: \`89635bfb9c8d1ff17297a59b6b5b5b2a176934ca\`
- issues/05: \`a9dfaa450ba025a7b5113ade8a294d6dbad778dc\`
- issues/06: \`004d558df6376d2ad6f4f79a4581e8d2c444e355\`
- manifest: \`86df98ad8a84e583ff5df64ddbf8c0eaa1335b00\`
- tests/test_campaign.py: \`fd7f05e30092a7ec82090993dc5d7d0e23755c8e\`

## New R423 verification
The **exact GitHub-fetched content** of \`PROOF_BOUNDARY_LEDGER.json\`, \`assess_dispatch_proofs.mjs\`, \`test_assess_dispatch_proofs.mjs\` was evaluated in isolated V8: **31/31 assertions PASS**, covering false subscriber eligibility, fake commerce, missing legal/footer evidence, bad count provenance, duplicate/extra commercial slots, sender PII, raw affiliate/track links, sending-toggle drift and revenue misrepresentation. Git blob IDs were independently retrieved from GitHub:
- ledger \`d1cf4ddd1f82a63d648164084435d2530813fa4c\`
- validator \`8874f0e9802b50204f4af3f402aeba42d5c4fffa\`
- tests \`463883f605f2b636490475fd35bd56724be2e26c\`

These are **in-memory V8 checks**, not native Node, browser/mobile/email-client tests, not actual integrations, and **not legal clearance**. Ledger's real result: \`HOLD_UNSENT\`; ten independent missing blockers; unique eligible audience null; realized net revenue per thousand humans null. All 31 new test cases use **synthetic mutations**, never actual customer data or transactions.

## New read-only verification and limits
- Connector status: newsletter enabled, auto new-post emails OFF, FULL content, reply-to NO-REPLY; dashboard 3 total/3 confirmed/2 unconfirmed; separate follower diagnostic 3 WordPress Reader/0 direct email/partial false. Do not add them or claim three deliverable mailboxes. Most recent five post-notification attempts returned \`never_sent_opted_out\`, not a claim about all historical mail.
- WP authenticated read: original issue 04's destination post #434 is **published**, route \`https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/\`, modified 2026-11-15. A generic public web reader showed an internal error while opening that URL; authoritative WordPress post state and URL do not establish full anonymous cross-browser click success. Do not claim a broken public route without an independent network/UI reproduction.
- Public /dispatch/, /focus/, Editorial Standards inspected; the on-publish subscription promise differs from post auto-send OFF.
- Exact official NASA review/timeline and merchant sites referenced in the R423 adjudication were opened. Specific merchant permission remains missing.
- Connected Gmail search/read was limited to matching merchant messages; sampled Inspire3 marketing mail is **consumer promotion**, not documented Final Vestige affiliate EMAIL authorization. Search scope cannot establish universal absence of a contract. No email addresses, private track URLs or bodies are committed.

## Founder-release decision
**ALL SIX HOLD_UNSENT.** 03/05 HOLD_MERCHANT. Original 04 HOLD_COPY. All alternates NOT_ADOPTED. R423 only adds review evidence; no replacements to #175, no merchant link, no new subscriber platform, no WordPress changes, no mail or test mail, no live analytics, no post, no PR merge, no Grok queue change, no spending.

**Next external proof required:** Mind/Commerce gives authentic product-specific email-channel license and live reviewed guide/checkout; Focus/Claude privately resolves provider-eligible unique recipients and received welcome; Founder/Dispatch witnesses a native Jetpack preview with Final Vestige's valid address and unsubscribe. Explicit founder approval still required for edition, list, date, send even if every proof is later found. Net revenue per 1,000 independently qualified humans remains **NOT COMPUTABLE**.

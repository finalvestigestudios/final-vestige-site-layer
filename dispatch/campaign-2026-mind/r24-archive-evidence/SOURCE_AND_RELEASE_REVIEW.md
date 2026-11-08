# Dispatch R24 — historical evidence, conversion and release QA (2026-10-31)

**REVIEW-ONLY — NOT SENDABLE.** Master Issue #174, original draft PR #175, QA draft PR #201, stacked parent draft PR #324 at `fa83f645b2cc3beb56e526298d9afada77a1202d`, companion Mind owner Issue #171. Frozen homepage PR #49 untouched. All six emails `HOLD_UNSENT`; Issue 03/05 `HOLD_MERCHANT`. Original four editorial/two commercial mix unchanged.

## Substantive editorial correction

Issue 02's previous first paragraph was generic. The replacement leads with the reported **May 4, 1784** Buzancy encounter between the Marquis de Puységur and Victor Race, explicitly identifies a later account as the testimony source, explains what cannot be inferred from sleep/speech/amnesia, and distinguishes **the French royal commission's investigation of Mesmer from any test of Puységur's particular patient**. Reader value: practical `Recorded / Inferred / Unsettled` document-reading method. Exactly one primary CTA, to existing **published** CMS page 1377 at https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; public page rendering itself not browser-verified this run. Subject unchanged (26 characters), refreshed proposed preheader (78 characters). No commercial link or product pitch added to Issue 02.

## Inspectable source-to-claim ledger

| Supported statement | Verified source | Provenance / evidence boundary |
| --- | --- | --- |
| 1784 Soissons imprint of `Détail des cures` | https://wellcomecollection.org/works/es4ayp6q | **Archival catalogue record**, not original book scanned/read; institution says its listed copy is currently uncatalogued. |
| Puységur's description of Victor Race, May 4 at Buzancy, reported calm sleep/conversation/amnesia | https://www.circee.org/puysegur-memoires-pour-servir-a-l-histoire-du-magnetisme-animal-1784/ | Curatorial **secondary summary**, NOT an independently authenticated patient report or original French source inspected by this sprint. |
| Historical significance, unusual early circulation of 1784 `Mémoires` | https://pubmed.ncbi.nlm.nih.gov/31273811/ | Peer-reviewed **2019 abstract** inspected, DOI 10.1002/jhbs.21974; full article not inspected. |
| 1784 Franklin-era royal investigation of Mesmer | https://pubmed.ncbi.nlm.nih.gov/8209564/ | Peer-reviewed **1993 historical abstract**; NOT a direct test of Victor Race. |
| Contemporary printed accounts establish healing-fluid mechanism or therapeutic effectiveness | **UNPROVEN** | Newsletter expressly does not validate any magnetic fluid, cure or modern treatment outcome. |

Additional catalogue context: https://www.routledge.com/The-Marquis-de-Puysgur-Artificial-Somnambulism-and-the-Discovery-of/Crabtree-Osei-Bonsu/p/book/9781032292472 (modern translated edition *listed*, not reviewed in full).

## Actual engineering evidence

- Reconstructed six-source local baseline using prior R23 exported source; revised Issue 02 + manifest exact Git blob SHA matched local: `fb8cf1503acb2338a4884cac58b7c3b2cec95af7` and `79e9c4ed950d7466984ec1611faa00a5efdcab03`.
- Python suite after regenerated previews: **86/86 tests passed** (74 prior + 12 new). The new test file was uploaded separately; complete exact-remote-file Python execution has NOT been established.
- Local source preview generator `node dispatch/campaign-2026-mind/tools/build_previews.cjs --check` passed: 13 deterministic artifacts. Updated GitHub preview HTML, plaintext, and index were generated using **exact GitHub JS source** in isolated V8; original source and snapshot byte SHAs can be independently re-read.
- Regenerated the affected R23 WordPress Gutenberg candidate `issue-02.blocks.html`, consolidated compatibility ledger, and six-issue static reviewer board via exact GitHub R23 JS in isolated V8, preserving no-link commercial placeholders and release holds. This is **not full Node 20 hosted CI** and NOT a received WordPress email.
- **Six local Chromium viewport inspections** of revised email HTML, at 320/360/390/768/1024/1440px: all passed no-horizontal-overflow / CTA visible / UNSENT banner, with screenshots at 320 and 1440. Browser inspection used `page.set_content` on local preview, **not Jetpack outgoing HTML**.

## Operational and legal facts (authenticated WordPress read around 17:39 UTC, October 31)

Jetpack newsletter **ON**, new-post auto-send **OFF**, `email_content_format=excerpt`, no recent sends; configured welcome references the 52-page Focus Fieldbook but **receipt unverified**. Dashboard total=2, confirmed=2, unconfirmed=2, suppressed=0; unconfirmed may be excluded from total, but actual deliverable consented recipients unknown. `reply_to=no-reply`. Postal address, functional unsubscribe and real delivered email footer **UNVERIFIED**; a source-only preview cannot prove them. Native per-post send toggle and CMS drafts were not touched. The current excerpt delivery could omit the issue body CTA; no actual delivered issue or post exists.

**New cross-workflow GitHub CI evidence:** Dispatch Actions run [#41221012162](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41221012162) failed with `steps=[]`, `runner_id=0`. Unrelated Desktop suite run [#41224808061](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41224808061) had two such failed jobs; unrelated Preparedness run [#41224407992](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41224407992) likewise. A runner assignment/account-policy problem is **suspected, not proved**. Do NOT misrepresent locally green tests as green hosted CI, or alter shared workflows without administrative diagnostics.

Inspire3-specific email rights/approval, merchant SKUs and earning-link format, live vetted Zen12/Total Focus warm-up guides, current pricing/refund and creative permissions remain UNVERIFIED; seller assertions do not establish independent outcomes. Campaign legal footer must include a verified Final Vestige postal address and functional opt-out in actual commercial mail. Final founder approval of creative, consented audience and schedule is still REQUIRED.

**No emails or test emails, no WordPress writes/posts/settings changes, no subscriber contact/import, no affiliate activation, no new expense, no merges, no production or homepage edits.**

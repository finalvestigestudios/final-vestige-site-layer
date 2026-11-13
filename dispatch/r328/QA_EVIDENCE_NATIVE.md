# R328 — independently executed native/offline QA (2026-11-13)

Base: master draft PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. All original eight source files used in this sprint match the GitHub file blob SHAs on that exact head; original native Python **6/6 PASS**.

## Exact committed previews
- 12 HTML/plaintext preview Git blobs re-fetched on R328 commit `e3be18f42c558b9520e8e4b46b8d9aa87b6f052d`.
- A locally reconstructed functionally identical renderer generated all twelve previews from the original Markdown + manifest. **12/12 locally regenerated git hash-object SHAs exactly matched committed GitHub previews**. Local renderer source formatting differed from committed builder; generator-source byte identity is **NOT** claimed.
- The R328 `test_canonical_previews.mjs` local source Git blob equals exact remote SHA `e1ad980e9ed17b3e9d4fd3f74edc489a9d4f5ff8`. Native `node` execution: **6/6 editions PASS**, checking deterministic equality, 4 editorial/2 commercial pending, missing legal footer blockers, disclosure, no active merchant links and review-only labeling.

## Local offline Chromium
- The same twelve source-matched preview files used in 30 Chromium Playwright layout checks (six HTML × widths 320, 360, 390, 768, 1440). **30/30 PASS**: no horizontal document overflow, one H1, nonempty readable body and all active links first-party.
- Six 390 px full-page screenshots captured. Evidence zip available in the Dispatch automation response; full browser and source logs remain local. No real Jetpack preview, received message, email-client rendering, screen-reader validation, postal address or functional unsubscribe was tested.

## Live read-only site status (2026-11-13 11:39 UTC)
- Newsletter on, automatic new-post emails OFF, full email content, Fieldbook welcome configured but **actual delivery unverified**.
- Dashboard total/confirmed/unconfirmed **3/3/2 overlap**, cannot treat sum as people or three as verified reachable mailboxes. Five inspected recent post notifications marked `never_sent_opted_out`.
- Inspire3 account approval, authorized email channel, issued earning URL, final merchant checkout/refund, live first-party approved guide, confirmed eligible audience and independently paid conversion **NOT VERIFIED**.

## Blocking release states
Every original issue `HOLD_UNSENT`. #03/#05 additionally `HOLD_MERCHANT`. Offline previews `REVIEW_ONLY_NOT_ADOPTED`. No WordPress writes, emails or test emails, subscriber contacts, affiliate activation, social posts, spending, analytics deployment or merge. The six originals and PR #49 were not edited. KPI net realized revenue per 1,000 qualified human sessions **NOT COMPUTABLE**.

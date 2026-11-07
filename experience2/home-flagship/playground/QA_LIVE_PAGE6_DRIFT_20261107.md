# EX2 — Production Page 6 vs pinned candidate: read-only source drift admission
**Inspection:** 2026-11-07 UTC; no production mutation. **Gate:** RELEASE HOLD.  
**Parent base:** draft PR #1345, exact `0cff0dddf2d85a8cbb4150a6d2f2a8595daea688`.  
**Candidate Blueprint blob:** `137c74a476005684a28f5ff9a36e75c6b03268f7`.  
**Frozen PR #49:** unchanged. Preserve all existing acceptance/review gates.

## Material source finding

WordPress.com read-only `pages.get(id=6, site=256784396)` returned **published** homepage status and modified timestamp **2026-11-05T12:07:24**. The actual public Page 6 content already contains seven Experience 2.0 chapter IDs and 72 Hidden in the Margins records. It is therefore incorrect to describe the whole seven-chapter *concept* as absent from production. It is also incorrect to describe PR #1345's exact latest candidate as already deployed.

The present published document and the exact source-controlled Playground candidate **differ materially**. Source-derived observations:

| Check | Live WP Page 6 public content | Pinned candidate markup |
| --- | ---: | ---: |
| Seven required chapter anchors | 7 | 7 |
| Margins items | 72 | 72 |
| Margins appear **before** flagship hero | YES | NO |
| Links containing `/focus/` | 4 | 5 |
| `<img>` tags | 8 | 2 |
| Top-level image `src` on i0.wp.com | 8 | 0 (2 from finalvestige.com; responsive candidates include i0.wp.com) |
| NYPL `edit-017-v02-nypl-5003296-original.jpg` as image | 1 | 0 |

**Scope caveat:** The live counts scan the entire published Page 6 content, including sections outside the seven-chapter experience; the candidate counts the shortcode's seven-chapter HTML alone. They demonstrate source non-equivalence, **not** an isolated component-level performance comparison. WordPress may alter image URLs on render. The public HTML observation does not prove that all interactions run correctly or that a real visitor completed any conversion.

The currently published Page 6 retains the Margins-before-hero composition that the proposed draft moved after the hero. Earlier 118–220px mobile improvements were demonstrated only in isolated candidates; they cannot be asserted as live improvements.

## Archival-media rights and network status

The published Page 6 references an NYPL Brooklyn Rapid Transit / Malbone map image via `i0.wp.com`, which the unpublished candidate deliberately excludes pending rights review. Its appearance **does not establish infringement or the absence of permission**; the editorial team must resolve this specific rights/provenance item before promoting the candidate. WordPress media #473 is credited NASA S67-19766, and media #474 is catalogued as a public-domain Wikimedia scan of an 1869 printed reproduction of the 1847/1848 Victory Point note. Continue to distinguish the original museum object, the print reproduction and editorial typesetting.

The media registry reports 78,346 bytes for Apollo #473, 466,043 bytes for Franklin #474 and 5,553,669 bytes for the NYPL original #1258. Those are **registry metadata**, not observed browser network response bodies. Both actual bytes and selected CDN/first-party URLs remain unverified. No new image or license has been added.

## Reproduction and evidence

Run (on the exact parent checkout):
```sh
python -m unittest -v experience2/home-flagship/playground/test_verify_live_candidate_divergence.py
python experience2/home-flagship/playground/verify_live_candidate_divergence.py \
  --blueprint experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json \
  --live-manifest experience2/home-flagship/playground/LIVE_PAGE6_PUBLIC_MANIFEST_20261107.json
```
The six local synthetic/control tests passed; the second command **exits 2 intentionally**, with `RELEASE_HOLD_LIVE_CANDIDATE_DIFFER`, for the read-only manifest derived from WordPress. The manifest is a narrow evidence record, not a full production HTML export. The verifier also accepts `--live-json` with an authorized raw Page 6 read response for independent rescans; never commit subscribers, database backups, tokens, emails, or private content. Git blob validation rejects mismatched candidate Blueprints.

## Conversion and ownership

**OFFER:** Existing 52-page free Focus Fieldbook.  
**FUNNEL STEP:** Social entry → published homepage → visible Focus action → verified confirmed lead → independently verified paid order / affiliate sale → fees/refunds → net revenue.  
**BLOCKER:** Reviewers could mistake a published older seven-chapter composition for the new tested candidate, incorrectly credit draft improvements to live traffic, or overlook NYPL/first-party-source differences.  
**CHANGE:** Read-only source-drift gate with source-identified WP manifest, pinned candidate blob and negative controls.  
**PASS/FAIL:** Detection **PASS**; equivalence **FAIL** (intended release HOLD). No checkout, signup, attribution or paid-conversion evidence.  
**OWNER:** Interim homepage engineering / independent Site QA for release reconciliation; Claude owns analytics, Jetpack and commerce engineering; Grok/Praxxis own creator acquisition.

## Next required acceptance

1. Confirm editorial intent and provenance of what is **already** published before any migration. Never overwrite WordPress Page 6 without specific release approval.
2. Execute source-pinned `#1345` candidate in **isolated WordPress Playground/Assembler** (WordPress.com Personal has no native staging clone), using private Blueprint and existing bridge. Confirm exact source hashes, seven chapter content and 72 records.
3. Obtain real browser image response bytes, axe WCAG 2.2 AA testing plus manual keyboard/no-JS/reduced-motion/zoom, 320–1920px inspected layouts, Lighthouse lab metrics and independent rights review.
4. Obtain founder visual and release approval, CI/QD on exact head and WordPress.com/Jetpack acceptance before any production change. Do not sync subscriber records, change settings or run test opt-ins.

**Status:** BUILD + local unit TEST only. No integrated staging PASS, no WCAG certification, no measured CWV, no verified paid conversions, no deployment or spend.

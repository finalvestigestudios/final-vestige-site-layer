# R224 | Native test, source identity and official claim QA — 2026-11-09 UTC

## Exact source identity / native test
Native executable: Node `v22.16.0`; `node --test /mnt/data/dispatch_r224/test_verify_lineage.cjs`.
**15 tests / 15 PASS / 0 FAIL / exit 0**, executed locally on exact byte-identical copies of GitHub-committed sources. Native `git hash-object` of all three local files exactly matched GitHub connector `fetch_file` at R224 branch:

| New GitHub source | Verified Git blob sha1 |
|---|---|
| `dispatch/r224/LINEAGE_LEDGER.json` | `2c5074b25ccc6d9873415921f5c2167007c6b525` |
| `dispatch/r224/verify_lineage.cjs` | `3e782ace5a381bed3dd0ab4509b3544a2c294e3c` |
| `dispatch/r224/test_verify_lineage.cjs` | `0dcc509294678c8c01517788cadc89f839fc2122` |

Native suite checks genuine Git SHA-1 blob calculation; precise seven changed source paths; immutable #175 baseline identifier; even passing lineage never authorizes sending; invalid/short/misordered evidence; forged original/stacked hashes; 4:2 proportion tampering; activated affiliate URL; no-send flag tampering; missing manuscript; and altered release state.

**Material limitation:** Main CLI `node dispatch/r224/verify_lineage.cjs`, which requires a full checkout containing both original #175 and current R223 commits, was NOT executed. The container cannot resolve github.com for a private clone; the GitHub connector DID independently read each pinned exact blob at both SHA refs. Similarly, original PR #175's `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` was **not** natively executed against #175 this sprint. Do not substitute the 15-test source contract for that missing requirement. These distinctions remain hard review requirements.

## New official-source historical check
Original #175 issue 04 subject says `Fourteen seconds`, while stacked PR #178 revises it to `Seventeen seconds`. NASA's official Apollo 204 board report gives the first crew voice start `23:31:04.7 GMT` and end of second `23:31:21.8 GMT`, a **17.1-second elapsed window** containing **10.3 seconds of voice** and **6.8 seconds of silence**; it does NOT establish that the fire lasted only 17 seconds. This supports the revised carefully bounded headline over the original without proving all accompanying narrative. Source https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (section Voice Transmission, see `23:31:04.7` and `23:31:21.8`) and https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html .

The 1998 door-switch study is real, with the authors Daniel J. Simons and Daniel T. Levin and the first experiment finding about half failed to detect the change. DOI https://doi.org/10.3758/BF03208840 . These facts support copy review, not a global evidence signoff for six issues.

## Fresh external compliance context
- FTC commercial email rule and address/opt-out: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; commercial opt-out processing for >=30 days, honor requests within 10 business days. No Final Vestige publisher address or received unsubscribe proof found.
- Jetpack preview requires an individual post's subscriber-send toggle ON to show controls, which requires separately authorized safe editor review: https://wordpress.com/support/newsletter/email-appearance/ . No toggle changes/test sends made.
- Zen12 official exact seller page https://zen12.com/hnp publicly advertises 12 levels / 48 MP3s; 12-minute = 1-hour outcome claim remains vendor-only. The consumer-facing email must not present the claim as independently proven.
- Hypnosis Live Total Focus exact product page https://hypnosislive.com/mental-skills/total-focus identifies 33 minutes / 47 MB. Its FAQ https://hypnosislive.com/faq qualifies a fourteen-day guarantee with max five refunded sessions annually; publicly displayed prices differ between snapshots, so no checkout price was attested.
- The connected Gmail searches for explicit accepted publisher affiliate/email authorization and the actual final Fieldbook welcome yielded **no positive proof**, but this does not establish absence in other mailboxes or merchant systems.

## Outcome
**Built/Tested:** copy lineage audit, exact pinned source verifier, synthetic 15-test native suite, newsletter re-entry decision alternative. **Live/Verified:** Jetpack current configuration as recorded in the lineage ledger, and WordPress page/status by authenticated read-only checks; no actual recipient eligibility, welcome receipt, licensed merchant offer, email render, publisher postal, unsubscribe delivery or paid transactions verified. **Release:** all six `HOLD_UNSENT`; 03/05 additionally `HOLD_MERCHANT`. No PII accessed or subscriber contacted.

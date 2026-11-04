# Apollo R114 — printed photographic-rights custody (STAGING HOLD)

Parent: Issue #150. Commercial governance: #820 / #818. Stacked on R113 draft #921. Separate from frozen homepage PR #49, lead homepage engineering, Research Desk PR #158, Grok production and WordPress.com.

## Defect and change

A closed HTML `<details>` SourceDrawer shows its summary but **not** its detailed licensing caveats when Chromium prints. R113 restored all four evidence cards for print; a teacher could still distribute the source table with the rights warning absent. The source cards link to NASA pages but do not embed image binaries.

**R114** adds a screen-hidden, **print-visible**, text-only custody notice next to the six-record source register. It explicitly identifies **0/6** individual photographic reuse approvals, the **provisional S67-19766 portrait association**, the need to verify permissions before redistributing image copies, and no NASA endorsement. Screen and no-JS users retain the native expandable SourceDrawer; the notice does not become an extra CTA, popup or signup step.

The existing `qa_r113_print.py` now **fails** if the print notice is absent/incomplete or leaks into the normal screen experience at any of its 14 Chromium configurations (320/360/390/768/1024/1440/1920px × JS off/on). `test_r114_print_rights.py` adds ten standalone stdlib source contracts.

## Evidence distinctions (November 4, 2026)

- **BUILT:** actual GitHub staging source changes in `landing-preview.html`, Chromium runner, and executable source contracts.
- **TESTED — exact-source structural inspection:** 21/21 explicit invariants on retrieved GitHub blobs, including six pinned source links, original source/time separation, one free classroom CTA, zero forms, zero Payhip links, zero image binaries and no extra analytics.
- **TESTED — independent Chromium 144 representative fixture:** closed SourceDrawer rights caveat absent on print BEFORE; text-only notice present on print AFTER; 14/14 width/JS combinations passed; PDF text was actually extracted and checked for 0/6, provisional catalog ID, and NASA non-endorsement; 6 lab-only LCP/CLS observations, screenshots and a SHA-256 manifest. **Not an actual R114 page render.**
- **NOT TESTED:** exact-head actual full landing in Chromium, axe-core, authentic WordPress.com/Assembler, manual screen readers/physical touch, hosted field LCP/CLS and release approvals. No claim of field CWV from an offline fixture.
- **NOT VERIFIED:** individual NASA media reuse rights (0/6), S67-19766 catalog association, actual merchant SKU/Payhip fulfillment, any Grok Apollo publication, qualified referral cohort, confirmed orders/refunds/fees, or net revenue.
- **LIVE:** Existing WordPress Evidence Atlas page 2017 is a different artifact; its release approval remains to be reconciled. **R114 itself is not live.**

## Reproduce locally

```sh
python -I -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r114_print_rights.py' -v
python -I experience2/apollo-creator-bridge/qa_r113_print.py \
  --html experience2/apollo-creator-bridge/landing-preview.html \
  --out /tmp/apollo-r114-actual-chromium \
  --chromium /usr/bin/chromium
```

The second command requires `playwright`, Chromium and a suitable browser execution environment. Use `--axe /path/to/previously-approved/axe.min.js` if an approved local axe bundle is supplied. **Do not download new third-party bundles automatically** or mark axe as passing without execution. A real full-page PDF and screenshots are required before release; the synthetic-fixture archive is diagnostic only.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Priority | Offer → step | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Proposed educational casefile → paid order | No independently verified rights-cleared, currently sellable Apollo SKU and fulfillment | Audit merchant original, price, license, delivery, refunds before allowing checkout | **NOT VERIFIED** | Claude/Growth, founder |
| P1 | Future Grok long-form Apollo → evidence page → free classroom exercise | Classroom printouts could omit photograph rights caveat | R114 print custody notice, continued single optional free exercise CTA | **BUILT; fixture/browser and static checks, actual-page acceptance pending** | Apollo; Grok/Praxxis keep social ownership |
| P2 | Classroom exercise → product | No approved relevant SKU; cannot sell public-domain scans with uncertain rights | Gate paid integration on source-specific permissions and verified merchant path | **BLOCKED** | Claude/Site QA/founder |
| P3 | Verified order → net revenue/1,000 qualified human sessions | No approved asset_id campaign, qualified-session/checkout records, merchant confirmed orders/fees/refunds | Reuse #820's existing attribution contract; do not add analytics tags | **NOT COMPUTABLE** | Claude/Growth |

## Release governance

No merge, deployment, paid activation, CMS write, analytics install, social post, email or spending. Founder approval, QD/editorial checks, 0/6 media rights resolution, actual browser/axe/WordPress evidence, and publication-state reconciliation are still blocking. Original Research Desk #158 labels S67-19766 without the landing's provisional qualifier; coordinate a future independently reviewed correction, do not edit the frozen PR from this lane.

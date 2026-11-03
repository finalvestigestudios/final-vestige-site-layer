# R92 — Literal Shared-URL Source and Citation Custody (PRIVATE / HOLD)

**Issue:** #136 | **Ancestor:** R91 Draft PR #760, exact base f4e3577839cef3590f83fca90dca6ab165794bd3 | **Release:** HOLD, draft only.

R91 preserved 41 complete reviewer packets and 2,173 original citation occurrences. R92 binds the **30 original shared-URL collision groups** to the exact citation occurrences within the original release-candidate drafts. The repeated URL records are **not** merged, canonicalized, altered, equated, or automatically approved. The complete nested R91 -> R90 -> R89 -> R88 -> R80 original evidence remains present and digest-sealed.

## Safeguards introduced

1. Enumerate all original contributor-scoped source variants by their **literal unmodified HTTPS URL**. Prove the full observed collision-group set equals the documented crosswalk groups, compare every exact original source record, origin, identifier and reading-scope statement, and reject missing/extra/shared-URL groups or forged resolution status.
2. Independently scan the unchanged **35 article + six tool** body citation tokens; connect each exact (kind, slug, ordinal, literal source ID) to its immutable R91 record. Reject a replaced source identity, reordered or missing citation, out-of-scope contributor reading, duplicate article route, or published state.
3. Produce complete, ordered, **private reviewer dossiers per URL**, including all original unabridged source records, separate source-record hashes, each original cited document and citation rank, and lexical reading-scope differences. Repeated URL != identical claim support. A different contributor's source verification never propagates to another article.
4. Report all source/link/claim/qualified-safety/QD approvals as **zero**; keep each original review status NOT_REVIEWED and may_publish false. Review cues are not findings of factual inaccuracy, medical safety, or validation of a technique.
5. Optional metadata-only CSV, escaped for spreadsheet formula injection. CSV is **not an approval register, not a WordPress import**, and must remain private.

## Immutable expected census

| Quantity | Expected |
|---|---:|
| Article drafts / tool drafts / total | 35 / 6 / 41 |
| Unabridged original article DOM blocks, preserved in R91 | 4,070 |
| Original literal citation occurrences | 2,173 |
| Distinct original origin-scoped citation-to-source edges | 2,359 |
| Distinct cited source variants / unmatched historical rows | 242 / 11 |
| Original source records / literal distinct URL keys | 224 / 186 |
| Shared literal URL groups awaiting qualified scope review | **30** |
| Human source/claim/qualified safety/independent QD approvals | **0** |

The full-slate system separately preserves 244 research readings including two uncited readings. R92 reports actual (rather than invented) counts for citations associated with shared URLs and for cited collision groups. Each original source and claim record remains available for humans to inspect.

## Local reproducibility

Use a trusted checkout. Never publish or expose the private reviewer reports.

    python -I preparedness/tools/r92_collision_claim_source_crosswalk.py
    python -I -m unittest discover -s preparedness/tests -p test_r92_collision_claim_source_crosswalk.py -v
    python -I preparedness/tools/r92_collision_claim_source_crosswalk.py --private-csv-stdout > /tmp/r92-private.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    rm -f /tmp/r92-private.csv

The offline build is **WordPress-ready drafts only**; it cannot publish. Passing a validator or test suite does not substitute for the mandatory 13-stage release integrity, independent QD, human link/claim verification, qualified food/water/medical/fire safety review, live WordPress/browser accessibility inspection, or the founder's explicit publication authorization.

## Coordination and blockers: HARD HOLD

Recheck the exact seven Claude contributor head SHAs, standalone RC PR #584, independent QA PR #157, synthetic fixture PR #169, custody-repair/Hastings fixes, homepage PR #49 and flagship PR #604. Do not merge separate changes or force baseline parity. PR #169 remains separately unmerged even though the R91 integration ancestry itself contains an isolated duplicate-test fix.

Five advanced/frozen contributor provenance discrepancies, 30 unresolved URL groups, 15 safety exceptions, 22 editorial decisions, human external source and claim review, qualified medical and emergency safety assessment, real WordPress browser/a11y QA, independent QD, mandatory integrity and release authorization remain **OPEN**.

No article body, original source file, taxonomy, navigation, homepage, CMS, WordPress or public website changes. No published URLs, false source approvals, falsely claimed medical safety, QD PASS or automatic branch merging.

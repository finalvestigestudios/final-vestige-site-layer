# R35 — ProcureGuard source-bound, atomic review evidence

**Development-only.** ProcureGuard Studio Pro remains offline and review-only.
No new purchase authorization, payment approval, entitlement, download, website
publication or Windows release is implied.

## Change in evidence publication

Previously the procurement report could be published before its SHA-256
inventory was completed; a failed inventory left a convincing but orphaned
report. Moreover, the CSVs and optional price policy were read again during
inventory creation, allowing a changed source to be hashed without proving it
was the same source version that drove the reconciliation.

R35 parses **three bounded, descriptor-verified CSV snapshots** through
`engine.table(..., include_digest=True)`. The returned SHA-256 values describe
the precise bytes interpreted during the review, not a later opening of the
input filenames. An optional JSON price policy is also read as a single,
descriptor-verified, 8 KiB-max regular-file snapshot; the exact bytes are
hashed and the digest is printed in the report and checked in the inventory.
Symlink, replacement, and ordinary concurrent-modification checks apply to the
JSON policy, too. Invalid JSON and unapproved policy keys remain rejected.

During report generation, `engine.manifest(..., expected_inputs=...)`
checks **every** selected input's current SHA-256 against its parse-time or
policy-load snapshot. If the file changed, the review cannot be published.
The inventory includes the completed report and retains basename-only
evidence labels; it is not a digital signature or legally dispositive record.

The report and inventory are built in a private staging directory within the
selected output folder and published with **one directory rename**. Operators
see either the complete two-file bundle or no bundle. Paths returned by the
engine point inside `procurement-evidence-<UTC>-<random>/` rather than two
loose files in the selected folder. Repeated runs create separate bundles.

## Operator workflow

1. Use the normal offline ProcureGuard launcher to choose PO, invoice, and
   receipt CSVs. If needed, select an 8 KiB-max local `.json` price policy.
   Preserve immutable source copies and keep the output directory separate
   from source inputs.
2. Run the three-way review. A successful result contains exactly one
   `procurement-three-way-*.csv` and one `evidence-manifest-*.txt` in a
   newly named evidence subdirectory. Do not treat a missing bundle as a clean
   reconciliation.
3. Review **all** status flags (including linked credit/return, normalized
   identifiers, partial quantities and policy changes) and source line numbers.
   A string reading `matched` does not authorize purchases or payments.
4. If input files or policy can change after the review, archive independently
   retained trusted source copies. For long-term assurance, retain a separately
   controlled SHA-256 pin or a signed custody record: the text inventory alone
   cannot detect an attacker who rewrites the entire bundle together.
5. Keep both premium source data and the bundle local and access-restricted.
   Never put financial records in public GitHub CI logs or unrestricted links.

## Limitations and compatibility

- This change does not lock original files against edits after publication.
  A source edit **after** the last inventory recheck requires later independent
  verification; publication itself is not ongoing monitoring.
- Directory rename gives ordinary runtime all-or-nothing visibility, not
  power-loss durability or strong adversarial rename protection against a
  privileged process with write access to the output parent.
- The existing engine return value is still a two-element list of `Path`
  objects. The two paths now share a private evidence directory. Existing
  exception review operates on the first CSV path; no accounting thresholds,
  Decimal money calculations, scoring, or compliance determinations changed.
- Full-repository integration, Windows 11 x64 builds, installer scans, premium
  access enforcement and QD approval remain mandatory release gates.

## Development regression commands

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_procurement_bundle_r35.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_procurement_provenance_r35.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

The helper test suite exercises real private temporary files, symlinks,
hard-links, failed writes, failed rename, unexpected files and repeated runs.
The integration tests exercise real source imports, source edits after parsing,
same-size mutation, policy provenance and failure cleanup. Run both with
`python -OO` as well. A source-only Linux test run is **not** evidence of a
successful native Windows executable or a live-download approval.

# R13 — High-consequence action/evidence proximity queue (DRAFT / HOLD)

Issue #136. This addition is *not* a safety approval tool and must never be used to declare that any medical, food, water, fire, generator, infant or disability advice is safe. It cannot perform human source review. It does not fetch web URLs, change WordPress, alter navigation, publish articles or amend any source record. It preserves the original 35 articles, one water planner, seven contributor scopes and 30 unresolved URL overlaps.

## The gap it addresses

R8 enumerates 1,959 **existing** citation occurrences. R10 proves corpus-to-review-packet provenance. R11 proves a local WordPress draft export is byte-identical to the renderer. R12 independently compares original cite tokens to WordPress citation anchors. None of those checks can discover an **important instruction that has no citation token to begin with**. R13 supplies that missing editorial work queue. It does not claim that missing a same-block citation proves a statement wrong, nor that having a citation makes one right.

## Scope and behavior

- Read source article `_body` HTML, metadata and source-use map without changing any of them. Parse actual visible paragraph/list/table/caption content, excluding scripts, attributes, comments, templates and hidden sections. Maintain article, semantic-block ordinal, text excerpt, exact source-body SHA-256, and an independently calculated per-flag SHA-256.
- Heuristically mark blocks mentioning water treatment, food preservation, combustion/fire/CO, medical dependencies or vulnerable households **when they also contain action-oriented language or numeric instructions**. These are *review candidates*, not proof of danger or coverage; a high-consequence passage can evade simple word patterns. Historical reconstructions and quotations can be false positives and require human classification.
- Every candidate is `PENDING_HUMAN_EVIDENCE_AND_SAFETY_REVIEW`. Label `NO_SAME_BLOCK_CITATION` as a priority, and `SAME_VISIBLE_BLOCK` as cited-but-still-unverified. Preserve repeated citations and contributor source IDs without merging or treating source-use notes as actual verification.
- Detect unknown cited IDs, blank evidence-use descriptions, a changed article body, non-draft article status, hidden-citation count mismatches, malformed HTML, staleness against the canonical 1,959-occurrence ledger, and forged release status.
- Preserve full narrative drafts and all warnings; emit *private* JSON and spreadsheet-safe CSV review queues only, never a WordPress/public surface. The CSV protects formulas beginning with `=`, `+`, `-`, `@` or control characters. No autonomous positive review outcome exists.
- CLI **chains the original evidence freeze + native validator + R10 canonical corpus + R11 draft export custody + R12 actual rendered citation parity** before preparing an R13 triage. The corpus is still frozen at 36 draft items, 1,959 citation occurrences and 367 article–source pairs for this revision. Any source or structure changes must be assessed by human reviewers rather than silently updating the baseline.

## Trusted-checkout reproduction (read-only except optional local draft receipts)

```sh
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py                  # prepares LOCAL WP drafts only; does not publish
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/high_consequence_claim_triage.py \
  --json-out preparedness/build/r13-action-triage.json \
  --csv-out preparedness/build/r13-action-triage.csv
```

`build.py` is documented as a local draft builder; verify that claim and the exact checkout before execution. The CLI itself never calls WordPress. `preparedness/build/` must exist. If the native tests, preflights or source inventory fail, do not rely on a partially generated queue, do not normalize away discrepancies and do not publish. Store receipts privately. Document any human decisions in a separate reviewer-controlled process; no R13 output includes an approval field.

## Verified, and not verified

The R13 parser, deterministic queue and mutation safeguards have **92 isolated synthetic unit tests**. The previously local-tested R10, R11 and R12 fixture suites run alongside them for **369/369 synthetic tests** in the current local mirror. Neither test count means the repository-wide suite, real 35-article body scan, actual R13 action inventory, public source-link verification, source-claim substantiation, expert emergency safety review or independent QD has passed. Local authenticated GitHub checkout remained inaccessible during this session. Hold all drafts. Ask editors to prioritize uncited actions, and have qualified reviewers examine consequential advice in full context.

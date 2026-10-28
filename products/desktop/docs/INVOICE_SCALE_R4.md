# Invoice Twin Scout R4 — bounded candidate discovery and provenance

**Status:** development-only, not a fraud detector and not a public release. This change is stacked on the R3 financial integrity branch in issue #73.

## Problem and acceptance target

R3 rejected every input containing more than 200 invoices in the same vendor-and-amount group, regardless of dates. A business with monthly repeat payments could not safely scan a multi-year export. Comparing every pair across all time would also be quadratic.

R4 removes that arbitrary group ceiling. After parsing dates and money with the existing fail-closed CSV importer:

1. Group by normalized vendor and invoice number; for each group emit one stable source-row anchor to every other occurrence. Exact-key candidates are reported regardless of date or amount. This is a candidate set, not evidence that a payment was duplicated.
2. Group by normalized vendor and exact Decimal amount; sort each group chronologically (source row as a deterministic tie breaker).
3. For each invoice, compare only previous records within the past seven calendar days, inclusive, using a deque. When normalized invoice numbers are identical, skip because the exact-key phase already covers the group. This avoids an all-history pair scan.
4. Preserve both original vendor strings, both raw invoice numbers, amounts, dates, original CSV row numbers, explicit reason and review flags.
5. Exact-key candidates with mismatched amounts receive an amount_variance_review flag, with distant dates distant_dates_review; case/spacing/punctuation collisions receive normalization review flags. Rules never approve payments or assert fraud.
6. A dense cluster can legitimately produce quadratic output. Impose a 100,000 candidate cap, raising a clear ValueError before output is written; customers should filter a large export by vendor/date rather than use a silently partial report.
7. Retain legacy CSV output columns through reason and append vendor_b, date_a, date_b, and review_flags, avoiding unnecessary downstream breakage.

## Computational profile

- Preprocessing and grouping: O(n) records and storage.
- Date sorting: O(sum(m_i log m_i)) for same-vendor+same-amount groups.
- Windowed candidate scanning: O(n + w), where w is the number of pairs coexisting in the rolling window. In the worst case dense same-day inputs are inherently quadratic, and the tool fails rather than writes a truncated list.
- Exact-key anchored results: O(n) in total.
- Existing CSV input cap still applies (200,000 rows); the new result cap is distinct.

## Test acceptance

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v

Test scenarios include 300 same-vendor/same-amount invoices across consecutive dates (the formerly rejected group); inclusive seven-day boundary; unsorted source rows; distant exact-key occurrences; no duplicate near-key records; 100k-report overflow with no partial output; normalized source key ambiguity; case-only equivalence; amount disagreement; empty CSV; and NaN rejection.

Do not mark the entire suite green without executed tests. Windows binary smoke, clean Windows GUI testing, code signing, antivirus review, QD approval, and premium entitlements remain independent release gates.

## Explicit exclusions

This is deterministic local CSV review only, without OCR, bank integrations, multi-currency conversions, fuzzy vendor entities, machine learning, external API requests, legal/compliance conclusions, or a claim that vendor+amount+date proves a duplicate charge. Credit memos and legitimate recurring invoices may appear as candidates and require human judgment.

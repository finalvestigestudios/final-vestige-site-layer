# Apollo R350 — Reviewed source/record pairing gate (staging only)

**DRAFT / UNMERGED / NOT LIVE.** Successor to [R349 PR #2419](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2419); tracks [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and business [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## Defect addressed

An allowlisted NASA URL is not evidence that **the text placed beside it** is the reviewed description. R349 blocked spoofed/unreviewed URLs, but changing the claim beside an allowed URL still left a clickable, apparently endorsed source. R350 fingerprints all fields and the sequence of the existing six chronology rows, three Review Board finding rows and four NASA image-accession rows. A changed row, swapped allowed URL, missing source function, or missing integrity module causes all NASA source anchors across the evidence experience to be withheld with visible explanation. The existing free Apollo investigation continuation remains available. No assertion about NASA source bytes is made.

Digest format (PHP 7.4+): `sha256(json_encode(rows, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES))`. Three digests are embedded in `integrity.php`. Deliberate editorial changes require *human source review*, source-rights check where applicable, and a new source-controlled digest with tests. Do not automatically regenerate on unexpected changes. A change of **static template copy** outside the row-returning functions is not caught by this guard and still requires editorial review.

The R348 custody drawer also rejects caller-supplied forged records even when they borrow a previously reviewed NASA URL. Quarantine preserves historical text, disclosed limits, no-JS readability and print records. It is not a security boundary against an adversary who can modify both PHP modules and manifest together, nor is it a third-party rights certification.

## Reproducible QA

From repository root with PHP, Python Playwright and /usr/bin/chromium:

```bash
php -l experience2/apollo-r350/integrity.php
php -l experience2/apollo-r349/source-policy.php
php -l experience2/apollo-r348/source-custody.php
php experience2/apollo-r349/qa/preflight.php
python experience2/apollo-r350/qa/test.py
python experience2/apollo-r349/qa/browser.py
```

The R350 source-controlled QA injects changes to an event, finding, image limitation and an approved URL pairing in ephemeral copies; verifies no NASA source links survive without editorial pairing; checks no-JS, 320–1920 responsive Chromium, accessible link names via Chromium CDP, keyboard operation and a nonintrusive free continuation. Do not report CDP semantics as axe-core or actual screen-reader certification. Extended acceptance, source screenshots and deterministic SHA-256 evidence archive are in the corresponding task artifact.

## Conversion-first pathway, not an endorsed sales funnel

Grok Apollo history documentary (published `asset_id` and permitted URL **not verified**) → source-backed Atlas → one existing free investigation action → **only later**, a separately approved rights-cleared educator kit. The buyer-facing offer, merchant checkout/settlements and creator campaign attribution are **unverified**. This change is a trust and misattribution safeguard; revenue lift is a hypothesis, not a proven result. Claude owns website/analytics/commerce, Praxxis creator QA, Grok scripts and distribution, founder final approvals. No new script, payment link, affiliate CTA, mailing flow or analytics code.

## Hold gates

Actual installed WordPress/Assembler/CDN acceptance; genuine axe-core; Firefox/WebKit and independent screen reader; CSP/HTTP; hosted CI on exact HEAD; NASA source URLs/rights latest review; authenticated published Grok asset; payable offer; founder/QD release approval. Do not modify frozen homepage PR #49, Research Desk PR #158, production WP or Grok's task queue.

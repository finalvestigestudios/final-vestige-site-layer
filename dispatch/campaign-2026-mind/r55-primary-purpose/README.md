# Dispatch R55 · Mixed-purpose email and exact-merchant evidence

**Source-control-only HOLD.** This is a distinct additional QA layer on the existing unmerged Dispatch stack; it does not install a newsletter, write WordPress, create a subscriber list, message a partner, or activate tracking.

## Why this package was written

Prior R54 modeled the **first 55 words** of each canonical letter under the documented WordPress excerpt fallback. R55 independently evaluates the different, easily conflated questions: **(a)** what an actual recipient might perceive as the email's commercial primary purpose; **(b)** whether the source letter directs a reader to a verified first-party guide rather than a seller; and **(c)** whether claims about **named Zen12 and Total Focus SKUs** come from observable seller format descriptions or unsupported product benefit promises. It explicitly refuses to infer legal compliance from source files, keyword matches, affiliate recruitment pages, or simulated preheaders.

## Source-controlled deliverables

- `review.py`: standard-library, read-only code; loads **current stacked canonical** `../manifest.json` and all six `../issues/*.md`, models first-55-word plain text, counts original direct seller citations, checks precise editor-authored subject/preheader/CTA, detects dollar-price copy, validates release hard-stop placeholders, and generates an all-HOLD JSON report.
- `merchant_evidence.json`: dated, product-specific seller/public affiliate observations and **all false** proof flags for publisher acceptance, named SKU email permission, authorized earnings URL, applicable cart/refunds, rights to creatives, and a live approved first-party warm-up guide.
- `RELEASE_EVIDENCE_REVIEW.md`: hard editorial review of all six editions, mixed-purpose FTC analysis, 03/05 offer and copy gaps, captured promotional-price inconsistency and human evidence handoff.
- `review.html`: accessible, responsive, scripts-free internal reviewer board. **Not** a WordPress preview or published page.
- `../tests/test_r55_primary_purpose.py` and `../tests/test_r55_offline_review.py`: 54 committed Python checks, including hostile source mutations and static reviewer safety/accessibility assertions.

## Run it on the exact commit, not an older branch

```bash
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
python -I dispatch/campaign-2026-mind/r55-primary-purpose/review.py --strict
```

Expected by design: `send_allowed=false` for **every** edition; 03/05 have additional `HOLD_MERCHANT` dependencies. A passing test establishes only the version-controlled sources are internally consistent. It never approves publication or any email.

The local static HTML contains no JavaScript, forms, analytics pixels, affiliate links, or subscriber details. Human desktop/mobile review still matters; source-level CSS checks are not WCAG certification.

## What is real, what is uncertain

Authenticated live WordPress read on 2026-11-02 UTC: enabled/sendable, automatic per-new-post default **OFF**, actual selected content **excerpt**, welcome template contains 52-page Fieldbook, `recent_sends=[]`, counts `total=2;confirmed=2;unconfirmed=2`. The latter are **nonadditive diagnostics**, not three disjoint audiences, and the distinct eligible recipient count is **unknown**. The connected Gmail subscription confirmation from October 25 is **not proof** the final welcome email arrived.

The official current seller pages (URLs in evidence JSON) support specific file and format descriptions, not the sellers' stronger efficacy marketing claims. Hypnosis Live publicly displays prices that differed between a current direct page retrieval and an older indexed capture. That difference does not prove an A/B test or current cart eligibility: **no price appears in the proposed emails**. The public Inspire3 affiliate signup page references Zen12, but cannot substitute for Final Vestige-specific signed acceptance and EMAIL-channel promotion rights.

FTC and WordPress sources are linked in the human review file, along with dates and exact routes.

## Human release obligations: still outstanding

Distinct opted-in email audience; actual Final Vestige postal address, properly functioning unsub, separately authorized native preview (per-post send ON only if authorized, followed by OFF verification), separately authorized test recipient and original received MIME, welcome receipt, approved published first-party guides, written named-product email rights/earning links/checkout/refund terms, and **explicit final founder approval** for exact email creative, recipients and date. No source or machine test is a surrogate.

Keep original founder-approved allocation **4 editorial / 2 conditional commercial**. Existing R50/R51/R52 proposed alternative copy is not silently substituted. Homepage flagship work remains priority one, with frozen PR #49 unmodified. File evidence in [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) and merchant coordination [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).

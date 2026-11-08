# Dispatch R81 — native excerpt transport reality, not another six-script rewrite

**Status: HOLD_UNSENT / review only.** Master issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [original six #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [per-issue gates #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), parent [R80 #715](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/715); commercial owner [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). This directory adds no replacements to either original or optional full manuscripts. Homepage #49 untouched.

## What's new and why it matters

Six optional **editor-ready custom excerpt proposals** across the complete original 4-editorial / 2-commercial pilot are aligned by subject, topic, source file, intended editorial destination and verified merchant source. Previously, the repository held excellent full-length research letters and static previews, but the actual live Jetpack transport is set to **excerpt**, so the long preview is not necessarily an inbox experience. These six excerpts are deliberately **under 350 characters** and under 55 words where possible to reduce ambiguity across different documented WordPress/Jetpack fallback discussions. **Those limits are NOT claims about final rendering.** A custom excerpt entered on a future native post may render differently. WordPress docs: https://wordpress.com/support/newsletter/email-appearance/ ; https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ .

Commercial disclosure appears at the start of both reserved excerpt proposals, and adjacent to any future qualifying offer in the corresponding full manuscript. **No buying link, guide URL, payout, price, refund guarantee, creative permission or send approval is represented as verified.** Existing official sources are referenced but never used as direct active offer CTAs.

The package includes [ISSUE-CARDS.json](ISSUE-CARDS.json), [PREVIEW.html](PREVIEW.html), [PREVIEW.txt](PREVIEW.txt), [TRANSPORT-AND-LEGAL-AUDIT.md](TRANSPORT-AND-LEGAL-AUDIT.md), and [test_r81_excerpt_transport.py](../tests/test_r81_excerpt_transport.py). The source files remain master PR #175 and optional R79/R80 candidates as identified per issue, **not automatic replacements**. No developer should merge this branch without first reviewing stack ancestry and corresponding consent requirements.

## Inspect without sending

```bash
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r81_excerpt_transport.py' -v
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_campaign.py' -v
```

Open the static HTML reviewer in a browser without fetching remote assets; source URLs are displayed as evidence. Do not confuse this with WordPress's **Preview email** control. There are **no recipients, tracking parameters, pixels, forms, scripts, merchant links or send functions** in the package.

## Explicit gates

All six: HOLD_UNSENT — real publisher postal address, actual eligible mail audience, native preview / controlled received-email, effective recipient unsubscribe, full MIME comparison and final founder creative and SEND approval are not obtained. Issue 03/05: additionally HOLD_MERCHANT — approved paid affiliate relationship, **email channel permission**, privacy handling, live independently vetted guides and tracking-link terms absent. The historical 4:2 pilot is unchanged.

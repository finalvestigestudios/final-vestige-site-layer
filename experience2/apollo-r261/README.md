# Apollo R261 — Native SourceDrawer focus bridge (DRAFT / STAGING HOLD)

**Scope:** Apollo Atlas only; no homepage PR #49, original Research Desk #158, original NASA data, WordPress, analytics, checkout, social queue, or production changes.

R260's CSS-only `:target` orientation deliberately left `details#fv-apollo-source-drawer` unfocused after hash navigation. This tiny, optional JS enhancement opens the native SourceDrawer and places focus on its native `<summary>` after activation of its existing local link. Clicking the same hash twice works. Direct deep links open the drawer but do not steal initial page focus. Hashchange covers browser history. JS is not required for content, native hash navigation, summary keyboard use, or print.

Run exact sealed original PHP fixture locally:

```sh
python3 experience2/apollo-r261/qa/source_drawer_focus_qa.py \
  --atlas fixture/sealed-r238 --overlays experience2 --out dist/apollo-r261
```

The implementation does **not** instrument clicks, create commercial destinations, request network resources, rewrite history, or assert NASA endorsement. One free original investigation CTA remains unchanged. Optional educational commerce is on HOLD until the founder/Claude verify an existing eligible SKU, original-product rights, fulfillment, sales/refunds/fees, and transaction attribution (Issues #818/#820).

**Release blockers:** independently audited axe-core and manual screen-reader checks, installed WordPress/Assembler and actual CSP/HTTP integration, source media rights, hosted CI, independent review, inherited R198 ancestry discrepancy and founder authorization. `set_content` offline-browser acceptance is not a live/WordPress pass. No social posts or paid conversion claims are authorized by this PR.

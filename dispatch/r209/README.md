# Dispatch R209 — provider/merchant proof, not another email campaign

Source-only independent sprint on 2026-11-08 PT. This adds a release-witness module, synthetic regression tests, a sanitized real WP diagnostics snapshot, named proof docket and official-offer claim map. It DOES NOT duplicate original six editable email manuscripts (#175), 12 original HTML/text previews (R206), the R204 MIME inspector or the R208 campaign attribution guard. No mail, post, settings, recipient, affiliate, analytics or billing changes.

The native release witness deliberately **cannot authorize sends or publication**. Even its fully synthetic “all evidence” fixture returns `HUMAN_REVIEW_ONLY` and `send_authorized:false`, preventing a test harness from being mistaken for founder approval. Merchant identity documents are *private*. No real addresses, earning URLs or subscriber identifiers belong in public repo.

Run `node --test dispatch/r209/test_release_witness.cjs` from repository root (Node 18+). `release_witness.cjs` requires no packages and makes no network calls. Failing tests or actual delivered email QA block every release. Test suite is synthetic: does NOT prove real provider receipt, actual partner approval, 7/30-day revenue, live delivery, accessibility rendering or functional opt-out.

Parent: draft R208 PR #1576 at `38941f156d84dcfce08e847c8e2be6dcffaf31a2`. Evidence issue #174 and handoffs #171, #129 and #820. Founder controls release.

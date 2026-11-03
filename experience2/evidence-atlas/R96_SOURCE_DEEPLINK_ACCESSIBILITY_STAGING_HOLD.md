# Apollo R96 — source-identity deep-link navigation (STAGING HOLD)

**Scope:** Isolated curated, text-first NASA-source Atlas; no publication, plugin activation, WordPress write, homepage changes, new geography, invented source relationship, photographic reproduction, or paid service.

## Observed source behavior and resulting defect

R94/R95 Atlas optional filtering hides evidence `<article>` nodes using `hidden`. Its native jump links and inbound fragments point directly to those nodes. Clicking a source link that remains hidden under an active date-certainty/search filter can leave the visitor at an invisible source. A **same-fragment** link may not fire `hashchange`, so a hash-only listener cannot solve this problem. This is a staging UX/source-navigation defect, not evidence of a production defect.

## R96 implementation

- Preserve six individual source IDs (`#atlas-01` through `#atlas-06`) and links; source data/photographic rights and R95 sealed asset receipts remain unchanged.
- Make the six article destinations programmatically focusable with `tabindex="-1"` (not additional tab stops), with visible focus styling.
- For native source clicks, hash changes, direct hash loads and browser history: require one of the exact six registered identities, restore the full source index when the requested target would otherwise be hidden, clear both UI-only filters, then focus/scroll the exact requested source.
- Handle **same-fragment repeat clicks before native navigation**, not only `hashchange`.
- Do not alter URLs, source metadata, rights statuses or historical claims. Invalid fragments are ignored.
- Preserve six visible records and ordinary native anchor navigation with JavaScript disabled or partial markup. No network calls, client persistence or dependencies.

## Reproduction and acceptance

From repo root:

```sh
python -m unittest discover -s experience2/evidence-atlas/tests -p test_atlas_deeplinks_r96.py -v
python -m unittest discover -s experience2/evidence-atlas/tests -p test_asset_inventory_r95.py -v
python -m unittest discover -s experience2/evidence-atlas/tests -p test_curated_atlas_r94.py -v
node experience2/evidence-atlas/tests/node_atlas_nav_r96.cjs
```

Dedicated `.github/workflows/ex2-apollo-r96-fragment-navigation.yml` enforces exact-head checkout, generates twice-identical ZIPs, checks all 24 source/export hashes, runs source and JS regression suites, then uses real pinned Playwright Chromium / axe-core / PyMuPDF to exercise 320/390/768/1440/1920 with JS on/off, native same-hash clicks, hidden-source history, focus, touch, reduced motion, forced colors, PDF rights warnings and lab LCP/CLS. Browser acceptance is **PENDING until job steps execute and receipts are examined**.

## Independent local limitation

This runner can execute `node --check` and local deterministic JS-state assertions, but both `file://` and loopback `http://127.0.0.1` Chromium navigations returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`; do not claim local real-browser pass or exact-head axe data. Tests are committed so a functioning CI runner can prove or disprove them.

## Release gates

CI execution, independent QA, hosted WordPress.com validation, actual assistive-technology and physical-device testing, editorial verification, six separate photo-use reviews, and founder release approval are outstanding. Crew portrait `S67-19766` remains provisional and its photographic day unconfirmed. No geospatial pins or inferred links are authorized. **HOLD; no merge or deployment.**

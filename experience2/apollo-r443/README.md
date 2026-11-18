# Apollo R443 — Public Atlas Review-Truth Gate (isolated draft)

**Read-only finding, 2026-11-17 PT:** The published /apollo-1-evidence-atlas/ page (WordPress page 2017) shows TWO literal "Atlas review status: Not yet reviewed." labels alongside its separate source-crosswalk "verified" labels. This is an unresolved editorial-review status, not proof that the NASA history is false. The published page is not the uninstalled R438–R442 staging components. Do not silently change its editorial labels or WordPress content.

**Implementation** (qa/atlas_gate.py): A deterministic, no-network auditor of saved, provenance-labelled HTML snapshots. It detects unresolved review labels, verifies NASA Board and retrospective links, checks the original free investigation pathway, prohibits unapproved checkout links and speculative geo markers, and checks duplicate DOM IDs/image alt attributes. Staging mode additionally demands >=5 original R438 source cards, exactly one R440 educator preview and exactly one free investigation link. A published page must NOT be misrepresented as installed R438/R440 staging.

**Source tests:** Run python -m unittest discover -s experience2/apollo-r443/qa -p 'test_*.py' -v. Feed an authorized full HTML snapshot into python experience2/apollo-r443/qa/atlas_gate.py --html /path/to/snapshot.html --provenance published_wp_read_only --output /tmp/atlas-results.json. HOLD_REVIEW exits 3; a snapshot pass is not an independent editorial certification.

**Actual PHP fixture browser tests:** Materialize source-exact R440 PR #2925 files under experience2/apollo-r440/ and run python experience2/apollo-r443/qa/browser_offline.py. Tests 320–1920 at seven widths, JS and no-JS. Browser loads actual PHP-rendered HTML via set_content: NOT navigated WordPress staging, genuine axe-core or LCP/CLS acceptance.

No homepage PR #49 changes, no Research Desk PR #158 changes, no CMS writes, no media reuse, no extra analytics/lead form, no checkout, no Grok role changes or paid services. Based on R442 PR #2936.

**Production HARD HOLD:** R417 reconciliation, editorial status resolution, founder-approved staging URL and full vetted axe bundle, navigated source/keyboard/touch/reduced-motion/320-1920/axe/LCP/CLS results, QD review, verified sale-ready product/rights/fulfillment, green exact-head CI, founder authorization. No sale inferred from a click or unconfirmed lead.

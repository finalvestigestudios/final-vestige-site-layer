# Final Vestige Experience 2.0 (The Living Archive)

Isolated workstream. Separate from the homepage release (PR #49) and from the Site Layer plugin. **Integration candidate: not installed, not approved, not deployed.** See `../docs/experience-2.0/SPRINT-05.md` for status and `ARCHITECTURE-DECISION.md` for the placement decision.

## Layout

```
data/apollo1.json            canonical Apollo 1 records, image identity and rights fields, claim crosswalk, chronology
design-system/src/           css/*.css (tokens + components), js/fv-ex2.js
tools/                       builders, validators, verifiers (stdlib Python + Playwright/Pillow for tests)
wp-plugin/final-vestige-experience-2/   staging plugin; assets/ and templates/ are BUILT and committed (see below)
atlas/                       schema, curation + snapshot + assembled dataset, ingest/build/validate tools
tests/                       unittest suites (builders, atlas, plugin, browser)
prototypes/sprint-01-04/     the supplied prototype sources, verbatim, superseded (see its README)
dist/                        generated preview site (gitignored)
```

## Conventions

- CSS: every selector starts with `.fv-ex2` (or `:where(.fv-ex2)`); custom properties are `--fvx-*`; keyframes are `fvx-*`; behaviour hooks are `data-fvx-*`. A test enforces this.
- Content is complete HTML first. JavaScript only reveals optional controls (those start `hidden`) and fails open.
- No network, storage, `innerHTML` or third-party code in the shipped JS (a test enforces this).
- Never plot or imply what is not verified: places carry no geometry until a reviewer approves a coordinate with a source and precision.

## Commands

```bash
python experience-2.0/tools/build_all.py              # build dist/ and the plugin payload
python experience-2.0/tools/build_all.py --check      # fail if the committed plugin payload is stale
python experience-2.0/tools/run_all.py                # every check; needs network for the live-media stages
python experience-2.0/tools/run_all.py --offline      # live stages report NOT RUN (exit 3, not green)
python experience-2.0/tools/run_all.py --perf         # adds lab LCP/CLS/event timing
python experience-2.0/tools/capture_evidence.py       # screenshots at 360/390/768/1024/1440/1920 into dist/evidence
python experience-2.0/atlas/tools/ingest_wp.py --check   # does the live site still match the committed snapshot?
```

Requirements: Python 3.11+, `pip install playwright pillow`, a Chromium-family browser (set `FVX_BROWSER_CHANNEL` or `FVX_BROWSER_EXECUTABLE`; otherwise Edge, Chrome, then bundled Chromium are tried), and `php` on PATH (or `FVX_PHP`). axe-core 4.10.2 is fetched once into `tools/.cache/` and verified against a pinned SHA-256. A missing browser, PHP or axe is an error, never a skip.

## Editing data

Edit `data/apollo1.json` (or `atlas/data/curation.json`), then run `python experience-2.0/atlas/tools/build_dataset.py` and `python experience-2.0/tools/build_all.py`. The plugin payload and `atlas.json` are generated; CI fails if they are stale.

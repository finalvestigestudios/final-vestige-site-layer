# 2026-11-05 — EX2 guest browser admission and conversion QA

**Not a release approval. No deployment, WP writes, paid conversion claim or asset use rights granted.**

## Exact source and ownership

- Parent PR #1201 at `3ceb047e2ae8db101254c52c01cf84f16e00447a`; frozen PR #49 stays at `10495883299d53596992c26a8987f629b2904670`.
- Live WordPress.com Page 6 read-only edit-context at modified `2026-11-05T12:07:24`: 7 EX2 chapter anchors, 72 margin fragments, hero primary “Enter the evidence room”, hero secondary “Read the investigations” to /blog/, 1 Jetpack block. The candidate CTA change to /focus/ remains draft.
- Only WordPress site 256784396 is connected, production. The Personal plan does not support native WordPress.com staging. Local/Playground review must remain isolated. PR #158 Apollo and #171 Mind retain independent ownership.
- This code reads only visitor DOM/network, creates local screenshots and JSON. It is a supplement to the full WordPress/Assembler stage admission and does **not** replace native staging or issue #820 attribution engineering.

## Run reproducibly

Requires Python 3, Playwright, installed Chromium and a locally acquired **axe-core** JavaScript bundle for accessibility admission. Do not fetch a third-party script at page load; pass a verified local file.

```bash
python -m unittest qa/test_fv_ex2_guest_gate_20261105.py -v
python qa/fv_ex2_guest_fixture_20261105.py
python qa/fv_ex2_guest_browser_admission_20261105.py \
  --target file:///$PWD/qa/fixture.html --output /tmp/fv-fixture
# RELEASE-QUALIFYING: use the authorized isolated Wordpress Playground URL,
# plus --axe path/to/axe.min.js from a locally reviewed package.
python qa/fv_ex2_guest_browser_admission_20261105.py \
  --target http://127.0.0.1:PORT/ --axe /path/to/axe.min.js --output /tmp/fv-stage
```

Live production is guarded by explicit `--live-readonly`; the runner rejects POST and selected analytics requests in this mode. It never submits an email, checkout or affiliate action.

## Independently executed native local tests

- Python + Chromium fixtures: **6/6 unittest cases passed**, including invalid chapter ID, missing 1/72 Margins, removed /focus/ path, production opt-in refusal and missing axe rejection.
- Representative *synthetic* fixture: real Chromium screenshot capture at **320, 360, 390, 768, 1440, 1920**; two no-JS captures at 390/1440; four fixture interactions passed. The fixture is **not actual page 6 or WordPress**.
- The harness intentionally exits **2** without axe, with `BLOCKED_AXE_MISSING`, even when all synthetic interactions pass.
- Attempted direct browser navigation to https://finalvestige.com from this runtime: **BLOCKED**, Chromium `net::ERR_BLOCKED_BY_ADMINISTRATOR`. No live browser screenshots, image transfer bytes, real interactive results, Lighthouse or field CWV obtained; do not treat the fixture as such.
- No native 200% browser zoom, Safari/WebKit or WordPress/Assembler runtime qualified. Report must remain HOLD.
- The code collects image response status and actual body bytes when a network-capable environment runs it. Such data is not available for the current fixture.

## Conversion contract

**Offer → step → blocker → experiment → evidence → owner:**
free 52-page Focus Fieldbook → the first-screen secondary hero action → published hero currently points to the blog, and actual guest/mobile CTA performance unmeasured → test exact-source draft #1201 CTA to /focus/ against unchanged historical primary action → source checks and synthetic browser tooling pass, live visitor and paid metrics unknown → homepage engineering + independent Site QA; Claude owns analytics and merchant attribution; Grok/Praxxis own social source IDs and traffic.

For commercial acceptance separately require qualified human sessions by source/asset ID, confirmed leads, verified orders/affiliate conversions, fees/refunds and **net revenue per 1,000 qualified human sessions** with 7/30 day confidence flags. No paid sales assumed from outbound clicks or subscribers.

## Remaining blockers before release

Run this tool and the existing PR #250/#252 source-exact CSP/interaction and WordPress Playground/Assembler harness on a safe isolated clone; supply authentic axe; inspect physical mobile/touch and native zoom; check NYPL rights and NASA/Franklin transfer bytes; measure actual Lighthouse in a network-capable browser; confirm anonymous Jetpack signup and published-page rendering separately; require exact-head CI/QD and founder release approval. Playground cannot certify WordPress.com Atomic infrastructure, Jetpack delivery or production CWV.

Release decision: **HOLD**.

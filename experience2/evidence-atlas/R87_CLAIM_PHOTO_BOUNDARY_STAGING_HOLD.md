# Apollo R87 — Historical claim versus photograph custody (STAGING HOLD)

## Why
R86 proved six NASA photograph URLs/catalog identities match **both** the actual Research Desk and the generated Atlas. It did not ensure the actual Research Desk's separate historical-interpretation references remain intact. Without this gate, a photo of a 2017 exhibit could inadvertently appear to substantiate the 1967 hatch, cabin-pressure or ignition details. Photographic context does **not** establish those historical facts.

## What is new
R87 extracts the actual Research Desk's six article-scoped summaries, limitations and **two separate links**. It checks each link's full HTTPS host/path, its ordering and the exact institutional URL for the record. Record 01 uses NASA's institutional Apollo 1 historical account; records 02–06 point to the NASA Apollo 204 Review Board report. This validates the identity of the *reference link*, not the independent truth of every statement on the external page. The R86 three-register/two-component parity gate runs first. The uncertainty over probable versus proven ignition remains explicit.

R87 builds an independent no-JavaScript reviewer surface with six cards, separate documentary and photographic source panes, source limitations, disclosure drawers, responsive navigation, and print-visible NASA URLs. No photographs, geographic pins, scripts, speculative map edges or external assets are included. These are reference links, **not** rights-clearance decisions. The crew photo day and S67-19766 association remain unresolved.

## Repeatable commands

python -m unittest discover -s experience2/evidence-atlas/tests -p test_claim_boundary_r87.py -v
python experience2/evidence-atlas/tools/build_claim_boundary_r87.py /tmp/r87-build
python experience2/evidence-atlas/tests/package_claim_boundary_r87.py --built /tmp/r87-build --out /tmp/r87-A.zip
python experience2/evidence-atlas/tests/package_claim_boundary_r87.py --built /tmp/r87-build --out /tmp/r87-B.zip
cmp /tmp/r87-A.zip /tmp/r87-B.zip

CI tests real Chromium at 320, 390, 768, 1440 and 1920px, with/without JS, keyboard/touch, reduced motion and forced colors, pinned axe, LCP/CLS, screenshots and native PDF with source URLs and print contrast. These are offline laboratory tests, **not** WordPress.com or field-CWV certification. Inherited authentic local WordPress suite must also pass at the same head.

## HOLD, do not install or merge
- Zero of six photographic-rights assessments cleared; S67-19766 portrait association remains provisional.
- Independent historical/editorial review of primary institutional sources and exact claims is pending.
- Hosted WordPress.com isolated compatibility, manual NVDA/VoiceOver, physical-device acceptance, independent QD, founder art/release approval remain pending.
- No homepage PR #49 or homepage branch changes, original PR #158 edits, WordPress writes, external NASA image binaries, paid services, deployment or production changes.

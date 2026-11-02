# Apollo R67 — original Research Desk custody-gated Atlas shortcuts (STAGING_HOLD)

Scope: Issue #150, separate from frozen homepage PR #49 and Research Desk PR #158. Only `experience2/evidence-atlas/` changes; original R38 Research Desk files remain byte-identical. No WordPress installation, content or settings write, image embedding, map pins, or deployment.

## Reproduced gap and correction

The R66 Atlas verified all 54 of its own SourceDrawer values but admitted reciprocal shortcuts into the **original** R38 Research Desk after checking only each record's NASA URL/catalog. A changed Desk photo-rights disclaimer, catalog note, or photo-documentary boundary could still receive a source-verified Atlas shortcut. The underlying static Desk remained readable, so the observed problem concerns endorsement by optional cross-component navigation, not hostile-script security.

R67 verifies the five exact native `<dt>/<dd>` pairs for **each of the six original Desk records (30 custody fields)** before adding reciprocal links. This source snapshot is derived from R38 `templates/ledger.html` at Git blob SHA `4842afb84b4c993cfc4861ce7f5a7a4d7b451871`; it is not a fresh NASA rights finding. Validation runs before enhancement and immediately before Atlas→Desk, Desk→Atlas and Desk-hash navigation. An altered custody field, missing drawer, wrong record ID, duplicate drawer or changed label disables the optional Desk bridge while preserving the original Research Desk, Atlas, citations, and printable records. The Atlas's independently verified 54-field guard remains intact.

## Reproduce

- `python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q`
- `python experience2/evidence-atlas/tests/browser_r67_desk_custody.py --output qa-r67`
- `python experience2/evidence-atlas/tests/build_full_staging_r67.py --output staging-r67`
- `python experience2/evidence-atlas/tests/build_r67_bundle.py --qa qa-r67 --output Apollo-R67-STAGING_HOLD.zip`

Actual local run: **108 Python tests, 107 passed / one skipped** (legacy fixture-dependent check); **20 Playwright/Chromium responsive configurations** covering 320, 360, 390, 428, 768, 1024, 1440 and 1920 px with JavaScript on/off, forced-colors samples, reduced motion, keyboard and touch; **30/30 post-initialization Desk custody mutations** and **4/4 pre-initialization identity/label/date mutations** closed the optional bridge without hiding source records. Print checks preserve all six Desk + six Atlas records and 30+54 custody values. Screenshots and the manifest are SHA-256 recorded. Local LCP/CLS observations are fragment laboratory metrics only.

## RELEASE HOLD

The real PHP shortcode components were tested inside the local WordPress API simulator, **not authentic WordPress/Assembler**. Verified axe-core, NVDA/VoiceOver, hosted p75 LCP/CLS/INP, independent QD and exact-head green CI are outstanding. Six individual NASA image-use assessments remain pending; the S67-19766 attribution remains provisional. No rights clearance or permission to embed photographs is claimed. Do not merge, install or deploy this package without independent review and founder approval.

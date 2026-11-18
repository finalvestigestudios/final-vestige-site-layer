# R464 Shelter branch witness delta gate — DRAFT / HARD HOLD

Scope: finalvestigestudios/final-vestige-site-layer Issue #136 only. Depends on R463 PR #3020. Independent safety QA PR #157, fixture PR #169 and repair #2205 remain isolated.

## Purpose
R460/R461 catches whole-file changes, but an original Shelter article may differ from the integrated 35-article manuscript despite preserving citation counts. R464 compares body bytes, reader-visible words, ordered paragraph/list/heading/table text, ordered citation IDs, hyperlinks, and tag attributes. It blocks silently hidden warnings and changed outbound source targets. It never selects a winning variant or grants Qualified Desk approval.

## Authenticated input custody
The JSON at preparedness/audits/R464_SHELTER_WITNESS_PINS.json freezes four articles x four versions with exact Git blob identities. The three original contributor branches and exact commits:
- original: claude/prep-shelter-5e1e0e @ 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
- continuation: claude/prep-shelter-continuation @ ac8625faf30dd5538fadc31e06cb5a2cea1defae
- followup: claude/prep-shelter-followup-evidence @ 6a5998ead97eca997e573ce8d3ceacf1c6aabad4
- candidate: R463 PR #3020 @ b36f3134c66131acc2dad8af25d541e6dcbc3d15

Stage exact UTF-8 byte-for-byte original body witness files in a local, review-only uncommitted directory: preparedness/audits/r464_witnesses/{original,continuation,followup}/{slug}.body.html. Preserve all whitespace. Never generate substitute witnesses, overwrite candidates or commit private review exports.

Native authenticated checkout commands:
  python -m py_compile preparedness/tools/r464_shelter_witness_delta.py preparedness/tests/test_r464_shelter_witness_regression.py
  python -m unittest discover -s preparedness/tests -p 'test_r464_shelter_witness_regression.py' -v
  python preparedness/tools/r464_shelter_witness_delta.py --root preparedness --witness-root preparedness/audits/r464_witnesses
  python preparedness/validate.py
  python preparedness/build.py
If the project uses different original validate/build paths, find the existing reviewed equivalents. Never invent a substitute native build. The witness CLI intentionally exits 2 even with complete, structurally identical content; structural parity is NEVER safety or release approval.

## Qualified review required
1. Outage heat/cold/generator: carbon monoxide and combustion warnings, numerical thresholds, vulnerable populations.
2. Shelter or evacuate: hazard-specific exceptions, government alerts and evacuation vs shelter boundaries.
3. Home fire escape: smoke alarms and exits, children and accessibility.
4. Family communication: child/school reunification privacy, offline redundancy, emergency contacts.

Diff output shows short text samples and Git blobs, not automatic medical, fire, food or emergency clearance. Parser limitations and semantic-context uncertainty remain human-review blockers. The historical 17 divergent articles, five source disputes, nine manuscript forks, 32 URL/scope review groups and four source-fragment changes remain separately unresolved.

## Conversion first, without publishing or activating
ONE verified FREE destination candidate: https://finalvestige.com/preparedness/ for family contact/reunification readers. Actual already-published Grok asset ID, exact hook, permissible link rights and signed-out mobile click path still UNMATCHED. Article #15 and Tool #104 are UNPUBLISHED/SAFETY HOLD; Tool #102 is distinct. No authenticated FV-owned payable Preparedness SKU, purchase permissions, fulfillment, refunds or settlement. Therefore do not add a paid CTA or an unapproved product. Founder/Commerce owns offer validation; Claude owns any later approved site/analytics; Grok/Praxxis verifies actual media IDs without changing the production queue. Paid orders, confirmed leads and net revenue/1000 qualified human sessions are NOT COMPUTABLE. No merchant, affiliate, CMS, navigation, analytics, email, social or live-site changes.

Release state: DRAFT / HARD HOLD; 35-article native validation/build and WordPress/private-preview exports unverified.

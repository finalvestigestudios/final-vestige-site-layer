# R178 — Whole-slate safety-state admission and source custody (DRAFT / HARD HOLD)

## Admission decision

**No Preparedness article is approved for public release by this gate.** It distinguishes
historical metadata values from independent, scoped human medical/food/safety,
citation and QD sign-offs. A structurally intact result is `DRAFT_HARD_HOLD`,
never `PASS`; a missing/mutated record is `INVALID_HARD_HOLD`. The CLI ALWAYS
exits 2. Do not disable or invert this condition in release automation.

This isolated draft adds no CMS writes, publishing, navigation, analytics, merchant,
affiliate, email, or social changes. It does not change the 35 original bodies, 35
original metadata records, source inventories, or R161 custody file.

## Evidence and provenance

Metadata read independently via connected GitHub, R177 exact source commit
`cfb03d0860352884bb628c45d71364aa0dc02ee9`, 2026-11-06 PT.

* 35/35 distinct article numbers, slugs and draft statuses; 385 author-scoped
  source-use interpretations.
* 29 recorded `pending`, 4 recorded `not-required`, 2 recorded `approved`.
  These are unaltered *historical values*, not independent QA judgments.
* 2 ambiguous founder-chat `approved` labels: `making-water-safer` and
  `salt-beef-salt-pork-age-of-sail`. Their actual source metadata explicitly
  disclaims independent review, confirmed scope and QD. Treat as **unverified**.
* 4 `not-required` entries: `navigation-before-gps`,
  `pioneer-supply-chains-failed`, `root-cellars-cool-storage`,
  `sanitation-before-germ-theory`. Their editorial/read-through caveats
  remain; the last two include modern-day safety-related assertions.
* Original R161 immutable body custody blob `fede4222c796d92798eff7cf0dcb225c291f7d61`
  preserves the previously authenticated **35 complete bodies / 2,000 citation
  tokens / 385 article-specific source-use records**. R178 uses its full Git
  blob fingerprints to prevent unnoticed prose or safety-text replacement.
* R178 baseline SHA256 `0de619c749047cb3bac73e664df2b49d3b0ea8770ea00bef7a71ed6d1a9cd094`;
  pin each original metadata Git blob and article number. Any replacement
  requires a separately reviewed source change, not a silent manifest rewrite.

The gate also checks all original body/meta pair identities, draft statuses, routes,
citation tokens against author source-use, duplicate JSON keys and Symlink limits.
It does **not** adjudicate whether the source actually supports its claim.

## Independent, reproducible commands

On a trusted complete repository checkout (no publishing or online calls):

```sh
python -I preparedness/tools/r178_safety_state_admission_gate.py --repo .   # expected exit 2, inspect JSON HOLD state
python -I -m unittest discover -s preparedness/tests -p 'test_r178*.py' -v
python -I -m py_compile preparedness/tools/r178_safety_state_admission_gate.py preparedness/tests/test_r178_safety_state_admission_gate.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300
```

R178 local proof on synthetic 35-article fixtures: 81/81 Python tests PASS
(including 70 independent article-body and article-metadata mutations), Python
compile PASS. Incomplete native checkout returns `INVALID_HARD_HOLD`, exit 2.
**Authentic R178 Python execution, complete native validation/build and complete
repository suite were NOT executed** because local git clone DNS could not resolve
github.com. Synthetic tests do NOT establish authentic source or safety approval.

## Independent QA and release blockers

Independent safety PR #157 current pinned head
`7d1ae6b8ef93d10cfb6810987672360885e9c1aa` must be
compared for correctness, not blindly cherry-picked against the later original
wording; source fixture #169 pinned `e9cd7766dac59d47ab467d8945269b9146c2aef5`
and later isolation fix #973 pinned `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`
are separate and remain unmerged. R177 already guards specific Household Plan and
Three-Day Kit warnings. R178 protects all 35 metadata/body identities and prevents
the two legacy labels from being treated as independent approval.

Human source and safety adjudications remain open: 75 existing source decisions,
32 shared-URL interpretation groups, 11 Family Card decisions and ten jerky
claim anchors (categories overlap: do not total them). No food, medical, citation
or QD independent review is completed by R178. NCHFP jerky URL variation and
NCHFP-vs-USDA guidance remain held. Actual WordPress 360/390/768/1440 browser,
print, source-render and privacy checks remain pending.

## One audience / offer / measurement friction map

**Audience/topic:** caregiver preparing school pickup, emergency contacts, and
family reunification when phones fail. Proposed source-backed free entry is the
original, currently *unpublished* Household Emergency Plan; the optional free
Family Reunification Card is also held. The public /preparedness/ gateway that
currently exists must not be confused with the 35 unpublished original drafts.

**Draft CTA, not enabled:** "If phones and school schedules were disrupted,
would your household know how to reconnect? Explore the free Household
Emergency Plan and prepare a contact card together." No paywall on official
safety instructions, no newsletter requirement.

**Paid practical pack: UNVERIFIED / CTA DISABLED.** No existing matching FV-owned,
rights-cleared, genuinely purchasable Preparedness SKU has been independently
authenticated. Claude/Commerce must supply current merchant listing ID, public
seller-approved URL, scope/rights, price, successful checkout/fulfillment and
refund-policy evidence before an optional commercial follow-up can be proposed.
Do not substitute a competitor's product, invent a pack or resurrect the retired
Water Resilience Field Manual.

**Creator asset: UNVERIFIED.** Grok/Praxxis TASK-008 has no authenticated published
caregiver asset_id, platform post URL or allowed destination. Do not overwrite
Grok's queue. Proposed UTMs only after asset verification:
`utm_source=<verified_platform>`, `utm_medium=organic_social`,
`utm_campaign=preparedness_pilot_2026_11`,
`utm_content=<verified_immutable_asset_id>`.

**Pre-release funnel acceptance:** video/topic → permitted destination (mobile
360/390/768/1440) → authentic matching free guide → optional free tool →
consent-aware optional email (existing /focus/ only) → separately verified paid
pack link; preserve disclosures, identity/rights source trail and print privacy;
verify focus form delivery independently without duplicate tracking scripts.

**Commercial measurement:** only qualified human sessions from verified Grok
asset ID, source-tagged landing, CTA click, actual confirmed lead, merchant-
confirmed order, refunds, fees and settled net revenue support 7/30-day cohort
KPIs. Net revenue per 1,000 qualified humans is NOT COMPUTABLE without real
merchant orders and a defensible human-session denominator; clicks and leads
are not sales. Current merchant and asset proofs missing.

## Coordination

Owner: Preparedness #136; commercial attribution charter #820/#818. Claude
owns site/merchant/analytics production engineering, Grok owns content and
posting, Praxxis is Grok independent research QA, Site QA handles browser
release checking, founder controls production release and spending. No
changes to other agents' issues, branches, assets, CMS or publishing.

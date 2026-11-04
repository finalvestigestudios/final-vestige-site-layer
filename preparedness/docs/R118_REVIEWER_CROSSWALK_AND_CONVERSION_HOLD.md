# R118 | Frozen 35-article author/source decision docket — PRIVATE HOLD

**2026-11-04 PT — Preparedness engineering Issue #136; conversion coordination #820; business charter #818.**
**Draft-only. No safety, source, URL, publication, checkout, qualified-human, or QD approval.**

## Scope and verified provenance
The nine exact GitHub ref SHAs below were independently re-read on 2026-11-04. They matched R117's frozen refs. Evidence is Git-object identity, **not editorial or safety verification**.

| Role/cluster | Git ref | Exact head SHA |
|---|---|---|
| baseline | `review/preparedness-r116-exact-author-metadata-hold-20261104` | `980659031b0bd5787a326d38698138c1e8cad82d` |
| candidate | `integration/preparedness-release-candidate-20261101` | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| historical-field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| historical-food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| historical-home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| start-here | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |

The R117 immutable crosswalk includes **35 original paired article routes**, 24 divergent contributor observations, **18 distinct changed paths**, and 19 non-exact candidate observations. These are object comparisons, not claims of merged articles. This R118 docket is generated solely from those fixed records.

## P0/P1 per-path human decisions (18 unique paths, all UNREVIEWED)
P0 = changed source fragment or author metadata, where citation interpretation, source type, safety/review state or attribution could drift. P1 = changed article body requiring meaning, reading depth, safety caveats and citation-position review. A shared physical path is listed **once** even when multiple contributor heads share its exact blob.

| Risk | Distinct path | Contributor clusters | Frozen original blob | Candidate blob | Contributor blob variants | Candidate disposition | Decision |
|---|---|---|---|---|---|---|---|
| P0 | `content/articles/homemade-water-filters.meta.json` | food, health, historical-field, historical-food, historical-home, shelter, start-here | `91c730bd1c7a61fa3140a86245c9bc0c88160c29` | `91c730bd1c7a61fa3140a86245c9bc0c88160c29` | `33789d3db0ec06007deb50d0293361f07cea27ae` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P0 | `content/articles/pemmican-and-dried-meats.meta.json` | historical-food | `03d3824e07fe51931671d0ddc7aa8c85eda58435` | `03d3824e07fe51931671d0ddc7aa8c85eda58435` | `c19f68f2ac0988a8d0959e2d05b8ace8f9511348` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P0 | `content/articles/pickling-fermentation-old-recipes.meta.json` | historical-home | `4b955811459017df83a28704aaf1e69ddb036c29` | `da97f42fcabbd05dc513d26c6af289bbeb8816f3` | `da97f42fcabbd05dc513d26c6af289bbeb8816f3` | EXACT_IN_RELEASE_CANDIDATE | UNREVIEWED |
| P0 | `content/articles/pioneer-supply-chains-failed.meta.json` | historical-field | `fcb42c440e3b7aad5eeecfd4e0c974a5d04a9cec` | `4d2dc4958736e3c5257c65dda8ed016a473ac6be` | `8789c77dcc2be717f09ce0fbd340a04319aaf223` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |
| P0 | `content/articles/pioneer-travel-rations.meta.json` | historical-food | `7191acba55d63dc405ad9c2003d66193276da89f` | `7191acba55d63dc405ad9c2003d66193276da89f` | `521e56a3f18d8b211920529a88a3c3b86eb332d7` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P0 | `content/articles/preparedness-real-households.meta.json` | start-here | `ba840917f34634ccd634c488eeca4a8a6b3a8fe2` | `ba840917f34634ccd634c488eeca4a8a6b3a8fe2` | `a0c3a09143a825560b5a5ed79d857b7402bfa295` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P0 | `content/articles/root-cellars-cool-storage.meta.json` | historical-home | `705e1157f9394b615ecb74ffd25be8500453e18a` | `c3b7425711c3953c2d6cac9eb2aabe21a6717285` | `c3b7425711c3953c2d6cac9eb2aabe21a6717285` | EXACT_IN_RELEASE_CANDIDATE | UNREVIEWED |
| P0 | `content/articles/sanitation-before-germ-theory.meta.json` | historical-home | `0dad1731adc3c88aac65baceaa9aa09112e5eb5b` | `3294cd9fcf59496c9ece9342e67b0d57d2ed5523` | `3294cd9fcf59496c9ece9342e67b0d57d2ed5523` | EXACT_IN_RELEASE_CANDIDATE | UNREVIEWED |
| P0 | `sources/fragments/hist-field.json` | historical-field | `4f369122cc0e230ee39654c215f18ffc79b5cc85` | `3dafa9425f3829c0be2e6fea00889aff95124031` | `6b65e0aaa777b4c5ebc57fbeade0386b4ab6c32f` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |
| P0 | `sources/fragments/hist-food.json` | historical-food | `d10628342fea5f177a8d1be00dd906d0c9c7850e` | `d10628342fea5f177a8d1be00dd906d0c9c7850e` | `c1856c998c6c728f0de72221e5654a238df994a9` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P0 | `sources/fragments/hist-home.json` | historical-home | `6460d4b0734991675c889f28be2f73a19e3c42c0` | `8d85fd868508c5caba14a839d119d55f31f14f72` | `8d85fd868508c5caba14a839d119d55f31f14f72` | EXACT_IN_RELEASE_CANDIDATE | UNREVIEWED |
| P1 | `content/articles/navigation-before-gps.body.html` | historical-field | `64c6b2c7004bc5549eea5a47d9095183e7436750` | `3c02e58c30d1d608224944142f31fbead44a1252` | `49beb68339a6b85b07d686c0cfb9fe1d88b8de4f` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |
| P1 | `content/articles/pemmican-and-dried-meats.body.html` | historical-food | `0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5` | `0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5` | `1febc8929f8b90c81a3fcef1e46a2811778b7e06` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P1 | `content/articles/pickling-fermentation-old-recipes.body.html` | historical-home | `17f5da8a998e6b9b38695a2ef6716c6f336f31c4` | `1869e37626b7463da45763d60202bd5ac0bd7700` | `1869e37626b7463da45763d60202bd5ac0bd7700` | EXACT_IN_RELEASE_CANDIDATE | UNREVIEWED |
| P1 | `content/articles/pioneer-supply-chains-failed.body.html` | historical-field | `1332df3540a903fdecdb3527fb22347d57968fb0` | `ad158ee898f76d05bcb65c845b1e4a0e8103c660` | `3643c50b43ca7ba6c1d9bc439e7c78730503b80f` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |
| P1 | `content/articles/pioneer-travel-rations.body.html` | historical-food | `058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7` | `058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7` | `a658481d828dc4c5ba85f296adbfbee0514f0611` | RELEASE_CANDIDATE_RETAINS_BASELINE | UNREVIEWED |
| P1 | `content/articles/root-cellars-cool-storage.body.html` | historical-home | `e28548b4e5014f36ffd12becb9261ae696480efa` | `2ff8d029769aa9a97de6b1e388d937899f3af38c` | `7f375c32d74f2828b4912f5692abc44483e4629a` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |
| P1 | `content/articles/sanitation-before-germ-theory.body.html` | historical-home | `15852c158708270d72d5f9723d90e5cb6083a766` | `d56df76647d2598f35cfd4609f91649cef063f12` | `02090fc1b773fd79f08a7ba754b6125844c37eab` | RELEASE_CANDIDATE_DIFFERS_FROM_BOTH | UNREVIEWED |

**Explicit collision:** `homemade-water-filters.meta.json` appears on all seven contributor heads with one shared contributor object; the release candidate retains the older object. Count it as one unresolved physical source-use decision, not seven approved changes.

## Six body-level comparison flags
These are approximate token and citation-ID deltas from exact-SHA GitHub article-body comparisons. **Matching counts never proves matching meaning, warning visibility, or source adequacy.**

| Article | Candidate vs contributor approx words | Citation occurrences delta | Contributor IDs absent in candidate | Candidate IDs absent in contributor | Judgment |
|---|---:|---:|---|---|---|
| `navigation-before-gps` | 0 | 0 | — | — | HUMAN REVIEW |
| `pioneer-supply-chains-failed` | 0 | 0 | — | — | HUMAN REVIEW |
| `pemmican-and-dried-meats` | 0 | 0 | nchfp-jerky | hist-food-nchfp-jerky | HUMAN REVIEW |
| `pioneer-travel-rations` | 0 | 0 | nchfp-jerky | hist-food-nchfp-jerky | HUMAN REVIEW |
| `root-cellars-cool-storage` | 0 | 0 | — | — | HUMAN REVIEW |
| `sanitation-before-germ-theory` | 0 | 0 | — | — | HUMAN REVIEW |

**Priority source-ID conflict:** `pemmican-and-dried-meats` and `pioneer-travel-rations` carry `nchfp-jerky` vs `hist-food-nchfp-jerky` across contributor/candidate variants. Source equivalence, support for individual claims, and author-specific source-use descriptions are **not verified**. Never automatically retarget.

## Frozen 35-route body and author-metadata custody
Full exact SHA-1 Git blob OIDs. Any body/metadata mismatch triggers manual evidence review; all original metadata source-use notes and prior safety states are preserved rather than implicitly promoted.

| # | Slug | Frozen body Git blob | Frozen metadata Git blob | Candidate body vs frozen | Candidate metadata vs frozen | Safety status |
|---|---|---|---|---|---|---|
| 1 | `emergency-hygiene-sanitation` | `324eeafa4d48c3e83e88055c5f226645a8893b4a` | `e94ff9b33e6ced71dafcdcc4412ad687a503ccf6` | same | same | NOT REVIEWED |
| 2 | `family-communication-plan` | `16e2b1ec37fd6ea37f442d13e831180253c709b9` | `e63bbe70f5b93936da5cd71c030e33d82256d3ee` | DIFF | DIFF | NOT REVIEWED |
| 3 | `fire-making-across-time` | `ff1b5e2c91172925e1d75462da4b3e162399269f` | `ca9e2c84d825b5cd9e182dc9a4a381c8a6905884` | same | same | NOT REVIEWED |
| 4 | `food-safety-power-outage` | `70339ef60f3f7bf1bec26a0ca457b0438650163e` | `3283071134ba24490d47f5a0635836b6ed4f8965` | same | same | NOT REVIEWED |
| 5 | `go-bags` | `5135639786bbafa4e03939a74659cd0f31df3564` | `16cc5e91204a77486912444c6e516f5d5b48f567` | DIFF | same | NOT REVIEWED |
| 6 | `history-of-food-preservation` | `273b246a069e834d8476bfc2854308732f5137ab` | `907237e436b44a34f8d673ef9de3168d1e9ad517` | same | same | NOT REVIEWED |
| 7 | `home-fire-escape-plan` | `ba869874b5ee6ef85a7694e65a364e12f4aed873` | `6a54547ef1458b0b5b0464f95d735ff4653c8368` | DIFF | DIFF | NOT REVIEWED |
| 8 | `homemade-water-filters` | `67aa44e9a332f57fb70298a3867410d8f66c8c15` | `91c730bd1c7a61fa3140a86245c9bc0c88160c29` | same | same | NOT REVIEWED |
| 9 | `household-emergency-plan` | `8ca5c261dba56eeaf79c445332381a74867233de` | `0681d51e6e29166eaae27ac2b7f1fbde3f836787` | DIFF | same | NOT REVIEWED |
| 10 | `lewis-and-clark-salt-works` | `364152230a6956a4936fd4ec4bce6b1547fe2533` | `3a350aedac67ea89c6995831032367634248c9e9` | same | same | NOT REVIEWED |
| 11 | `making-water-safer` | `f85d158fc8752200a227282e640f6df48277daf5` | `bcb567905444687b5ae0a261cbbdb7a24a9e7870` | same | DIFF | NOT REVIEWED |
| 12 | `medication-and-devices` | `47bbfeefb5aca5f5a8d66ad8c66e2998e6caae5e` | `a49a6d42a3deb14acbe67e7cf636c23cdc5ec49c` | same | same | NOT REVIEWED |
| 13 | `navigation-before-gps` | `64c6b2c7004bc5549eea5a47d9095183e7436750` | `40c83419760bc7bd0c4c574304e65b773b4a8423` | DIFF | same | NOT REVIEWED |
| 14 | `outage-heat-cold-generators` | `47d949d97ddb15abc5fdc3b556f37aea5036ce29` | `77dd194b096bb60ea99728a5b0042adf016b905e` | DIFF | DIFF | NOT REVIEWED |
| 15 | `pantry-rotation` | `727a43eff8b30c0f68fb6695d76d63166eb51450` | `dfafbb77e076d6cab5aec8217f98d7fd20dbff1c` | same | same | NOT REVIEWED |
| 16 | `pemmican-and-dried-meats` | `0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5` | `03d3824e07fe51931671d0ddc7aa8c85eda58435` | same | same | NOT REVIEWED |
| 17 | `pickling-fermentation-old-recipes` | `17f5da8a998e6b9b38695a2ef6716c6f336f31c4` | `4b955811459017df83a28704aaf1e69ddb036c29` | DIFF | DIFF | NOT REVIEWED |
| 18 | `pioneer-supply-chains-failed` | `1332df3540a903fdecdb3527fb22347d57968fb0` | `fcb42c440e3b7aad5eeecfd4e0c974a5d04a9cec` | DIFF | DIFF | NOT REVIEWED |
| 19 | `pioneer-travel-rations` | `058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7` | `7191acba55d63dc405ad9c2003d66193276da89f` | same | same | NOT REVIEWED |
| 20 | `preparedness-real-households` | `70d03c366e10db623929f118501becfa26c48bab` | `ba840917f34634ccd634c488eeca4a8a6b3a8fe2` | DIFF | same | NOT REVIEWED |
| 21 | `pressure-canning-low-acid` | `c60d824c2f679fb7362b8523aec18110f8248290` | `4ab01d4aa566b8970351d8d8d43f7f85e8a04341` | same | same | NOT REVIEWED |
| 22 | `rain-barrels-and-cisterns` | `1454ab95bef4e54ae8992addf4f815fc8bf358b4` | `dc42694e842969624f24ab5edc9bff2497693e70` | same | same | NOT REVIEWED |
| 23 | `root-cellars-cool-storage` | `e28548b4e5014f36ffd12becb9261ae696480efa` | `705e1157f9394b615ecb74ffd25be8500453e18a` | DIFF | DIFF | NOT REVIEWED |
| 24 | `safe-jerky-dehydration` | `6fa55c397b161437e016d5d4a6c27da7ce3fa6bd` | `50b365e8109c14bdb9ce1a9365db88215a678ec5` | same | same | NOT REVIEWED |
| 25 | `salt-beef-salt-pork-age-of-sail` | `6539aafeca9bca67c96247c81a7412b117201b88` | `06b1cec809cb78a3315f7a7655b028c0a27dd642` | same | DIFF | NOT REVIEWED |
| 26 | `sanitation-before-germ-theory` | `15852c158708270d72d5f9723d90e5cb6083a766` | `0dad1731adc3c88aac65baceaa9aa09112e5eb5b` | DIFF | DIFF | NOT REVIEWED |
| 27 | `shelter-or-evacuate` | `b8acf07e533eea43795aa242f39fd926b080130f` | `fe90c9ef50e2cad5fd36f2a9c4e2edd70c424186` | DIFF | DIFF | NOT REVIEWED |
| 28 | `ships-biscuit-and-hardtack` | `f2ec2393819c26741f7ce77b7e0f0f893d1c33e4` | `2b2c3ce9472073df3d15e8befb39178d369632b1` | same | same | NOT REVIEWED |
| 29 | `smokehouses-salting-curing` | `e5f6241c1fa09fdbd684234317aa819ea4ef13a2` | `16223945e83f95b349acf09a2b684c09326550c0` | same | same | NOT REVIEWED |
| 30 | `three-day-kit` | `ef5463ca668166766ca3d868908bc0bcb6040a23` | `c830e4b8b0ee2890a8ddaf82273fdc25bd4b50f2` | DIFF | DIFF | NOT REVIEWED |
| 31 | `two-week-water-storage` | `24572839d79a3c3f78805f3fc6834b7ab6037768` | `76f317f047ed95c8b6c7ab130f44d79232e7a463` | same | same | NOT REVIEWED |
| 32 | `warnings-radios-offline-maps` | `fbc39101ba2c8378423ba9554aaf467ee3bc53b7` | `025ddac0f8c077f2a6fa17d7fcb746caa51234a7` | same | same | NOT REVIEWED |
| 33 | `water-advisories-explained` | `e96486d74731606fdd5a616030f146f66c59e2b0` | `4c88e747b46d9e95264ec3367911a5175baa6c31` | same | same | NOT REVIEWED |
| 34 | `water-math` | `e82ad3ab14acb23e1cb1d87e80fa2e5d60da6ae4` | `4b1c3cd7166afa03e56991f7de8af771828a6e54` | same | same | NOT REVIEWED |
| 35 | `water-purification-through-history` | `3c89d3041b170038c842dea1b4f943385b0c8a86` | `1d9b77aa4a4cdbf4f9a02fe6d1cf5d2691cc798e` | same | same | NOT REVIEWED |

## Reproducible read-only commands
In a **complete clean checkout** with both R117 JSON files:
```bash
python -I preparedness/tools/r118_review_crosswalk_gate.py --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --workorders preparedness/docs/R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json > /tmp/r118-reviewer-crosswalk-HOLD.json
python -I preparedness/tools/r118_review_crosswalk_gate.py --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --workorders preparedness/docs/R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json --verify-crosswalk /tmp/r118-reviewer-crosswalk-HOLD.json
python -I -m unittest discover -s preparedness/tests -p 'test_r118_*.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```
The machine-readable crosswalk emitted by R118 retains 35 route/body/meta custody rows and 18 human decision rows with a fixed UNREVIEWED state. It checks the input snapshot and workorder internal consistency, source-file identities, all seven contributor references, unchanged 35-route slate, overlap multiplicity, and fail-closed governance fields. It does **not** freshly fetch GitHub refs, prove source content truth, check published WordPress, or resolve safety review.

## Independent QA and release dependencies
* QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` remains draft/unmerged; re-adjudicate changed household-drill warnings against current candidate.
* Synthetic-fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` remains unmerged; a remaining `_dup_test.json` test writes inside shared source directory. Keep fixture isolation work in its own owner branch.
* Preparedness release-candidate PR #584 `ddb3528ba6494dada1fa1c3a142ce746e3a67706` is HOLD. Homepage PR #49 `10495883299d53596992c26a8987f629b2904670`; flagship PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` untouched.
* Human review of 30 shared-source URL groups, 15 safety exceptions, 22 editorial decisions, 5 unfinished tools, native validation, full repo Python regression, offline draft build, browser QA, CI integrity and independent QD required. Historical counts are not freshly re-audited in R118.

## Conversion-first scoped acceptance (TASK-008; no unverified sales)
**ONE intent:** household emergency contact/reunification planning → the existing authentic source-linked **household emergency plan** (free ungated safety guidance; currently DRAFT/HOLD) → *optional* FV-owned paid practical planning tool **only when an existing product is proven rights-cleared, buyable, deliverable and relevant**. No seller-origin Preparedness SKU/checkout evidence or matching Grok immutable asset_id has been received; no live paid CTA, speculative price, retired water product, or fake sale.

| OFFER | FUNNEL STEP | BLOCKER | PROPOSED CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing suitable FV digital pack | product → payment | SKU, ownership, pricing, rights, file delivery, terms unverified | Obtain seller-origin listing + completed fulfillment proof before any purchase CTA | UNVERIFIED / HOLD | Growth + Claude |
| Source-backed free household guide | social → landing | Source/qualified emergency review, URL and route not released | Review 35-route provenance + all source groups; no safety-content email gate | HOLD | Preparedness + independent QA |
| Grok/Praxxis TASK-008 asset | video → free guide | No validated social asset_id/post URL/destination | Request only existing asset inventory and stage `utm_source`, `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11`, `utm_content=asset_id`; do not publish | NOT TESTED | Grok + Praxxis |
| Paid optional download (only if verified) | CTA → merchant checkout | Unsupported URL, mobile, disclosure, delivery | Stage disclosure, 360/390px tap/keyboard test, exact merchant checkout, delivery, refunds | NOT TESTED | Claude + Site QA |
| Verified net revenue | qualified session → paid | No attributable human sessions and no seller-confirmed orders/fees | Privacy-safe 7/30d cohort ledger; use existing measurement; separate lead vs paid; no duplicated scripts | N/A | Growth + Claude |

Draft CTA copy only: **“Plan how your household would reconnect. Read the free, source-linked emergency planning guide.”** It is not an email gate. An optional paid button is **absent** until merchant rights and safety requirements pass. No live CMS, homepage, navigation, analytics, social, email or Payhip changes and no QD pass.

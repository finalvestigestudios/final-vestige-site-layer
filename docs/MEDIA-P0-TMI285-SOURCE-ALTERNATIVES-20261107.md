# Two P0 Three Mile Island sources: publisher and federal primary-document recovery (2026-11-07 PT)

**Status: QA-only draft, zero production edits.** Independent media provenance work; not homepage visual design, and not a duplicate of Site QA #154's guest-Chrome collector or Media Recovery #183's original six-slot adjudicator.

## Fresh published source confirmation

Authenticated, read-only WordPress post **285** ("The Light Said Closed"), modified **2026-11-02T21:39:59**, still has six stored inline images. This batch is limited to the existing P0 slots **285:2** and **285:5**, preserving both exact current URLs, ALT and captions in [the machine ledger](../qa/media-recovery/p0_tmi285_primary_alternatives_20261107.json). Guest HTTP/status, `currentSrc`, decoded pixels, CDP request ID, screenshot and transferred bytes remain **NULL**.

Fresh independent **text/image retrieval wrapper** attempts (November 7, 2026) showed **285:2: wrapper 500 on redirection to inaccessible blog.ucs.org** and **285:5: wrapper 404**. These are **NOT** visitor-browser nor origin HTTP findings. Container HEAD requests also failed DNS resolution, an environment limitation, not evidence of an outage.

## Two original source problems and three archival candidates

**285:2 — TMI control panel.** The stored image depends on a moved UCS blog host. A 1979 primary-document candidate exists: [TMI-2 control panel.png on Commons](https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png), extracted from the **President's Commission report** *The Need for Change: The Legacy of TMI*, **p.97**, with [Smithsonian catalog confirmation of the 1979 report](https://www.si.edu/object/report-presidents-commission-accident-three-mile-island-need-change-legacy-tmi:siris_sil_765655). Commons reports **604 × 590** pixels and a federal public-domain claim. The image describes maintenance tags obscuring emergency-feedwater valve status. It is an illustrative **subject-level alternative, not the proven same original UCS photograph**; Commons rendition was retouched. **Proposed safe no-upscale size: 604 × 590**, not 960 wide. Hold exact rights/modification check, caption and visual comparison.

**285:5 — Three Mile Island aerial view.** The Say Media image URL encodes a forced `ar_16:9,c_fill,w_1200` treatment, with no proved visitor image bytes. The [publisher article](https://discover.hubpages.com/entertainment/The-China-Syndrome-Blockbuster-Movie-Becomes-Eerie-Prophecy) credits a **June 6, 2010 Wikimedia public-domain image** of the plant. The likely original by caption is [Three mile island 062010.jpg](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg), **819 × 614** original, uploader Marque1313's express public-domain dedication. **Neither identical binary nor crop is proven.** The 16:9 publisher transformation is NOT the source's near-4:3 geometry; blindly matching the transformed picture would lose content. **Safe conditional copy: 819 × 614**, never upscale to 960.

A second, historically closer **1979 Department of Energy photo** [Three Mile Island (color).jpg](https://commons.wikimedia.org/wiki/File:Three_Mile_Island_(color).jpg) is identified in Commons as an official-duty federal public-domain image. Its master is **2592 × 2488**; conditional no-upscale rendition **960 × 921**. It is a **different image, not a like-for-like URL fix**. Selecting it requires explicit editorial approval and verified source rights. The Commons catalog's date **1979** is not proof of accident-day capture.

**Copyright / permissions:** Commons public-domain assertions support rights triage but do not prove the actual downloaded commercial images are identical, or resolve modifications/crop, institutional marks or attribution obligations. Do not scrape, mirror, cache, or republish the third-party binaries. Per-item rights and full image comparison are required even for purported government-origin candidates.

## Staged remedy (not performed)

1. Site QA #154 uses its **existing** logged-out Chrome + mobile full-scroll collection to capture final `currentSrc`, request ID/status, response type, failed/decoded natural dimensions, cache flags, cold encoded bytes, screenshot and user-visible breakage for 285:2/5. Remaining P0: **287:5, 418:1, 418:2, 407:1**.
2. If genuinely broken, compare original rendered pixels to each historical candidate. Match the specific scene, crop, angle, date and legibility; resolve item-specific rights/credit. Proposed derivative width is `min(native_width,960)`, height calculated by aspect ratio, with **no enlargement**. For the 604px control-panel scan, retain lossless PNG if labels become illegible in lossy output.
3. Only with separate publisher approval: prepare WordPress Media Library source, original catalog link, attribution, image checksum, responsive sizes and a reversible isolated block-change plan on **staging**. No live block rewrite by this PR. Check phone and desktop layout/CLS and preserve alt semantics.
4. Before claiming weight savings, compare **paired full-cold browser traces**, identical page/viewport/scroll/slots and unshared request cache, deduplicate request IDs, and calculate `100*(beforeImageEncodedBytes-afterImageEncodedBytes)/beforeImageEncodedBytes`. Record image decode failures and LCP/CLS. The prior **76%** saving is **unmeasured**. WordPress original storage bytes are **not network transfer**.

## Baseline / engineering validation

The worklist lives on [draft Media Recovery #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) at `docs/IMAGE-WEIGHT-WORKLIST.md`, not the current main branch (404 on main). The original frozen audit counted **61 articles / 355 stored image refs**. Separate later source audits found **66 / 361**; neither is a browser failure inventory. The reported **42** broken images remain unverified. Thirteen WordPress media originals over 1.5 MiB total **43,522,829 stored bytes**, not measured cold transfer. This batch does not redo the sitewide source census, image classifier, guest collector, or the wire-weight comparison tool.

The offline validator tests exact P0 source identifiers, input provenance, three distinct candidate roles and native geometry; it forbids fabricated browser values, unwarranted copyright clearance, upscaling, WordPress publication and measurement claims. Regression cases cover deliberate mutations. No code in this PR downloads or uploads images.

**Release disposition:** all replacement candidates **HOLD**. WP writes 0; binaries downloaded/cache 0; live repairs 0; subscriptions $0; guest confirmed failures 0; actual percent transferred-byte saving UNKNOWN.

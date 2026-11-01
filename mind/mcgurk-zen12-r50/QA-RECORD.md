# Mind R50 evidence and release-QA record — 2026-11-01
## Read-only checks completed
- GitHub Issue #171 opened and latest relevant comments reviewed, including Dispatch handoff. Canonical Mind hub PR #172 reserved; flagship homepage PR #49 and Issue #150 protected.
- WordPress.com authenticated **read-only** inventory: 61 published posts, 79 published pages; published Puységur page ID 1377 and Focus page ID 1579 both read as published. Did not write to CMS.
- Official seller reviewed: https://inspire3.com/ ; exact Zen12 offer https://zen12.com/hnp ; About https://zen12.com/about ; Research https://zen12.com/research ; public Premium order https://zen12.com/getstarted ; generic affiliate network https://affiliates.inspire3.com/ ; other-product public Limitless Labs material https://inspire3.com/ll/ .
- Independent science: https://doi.org/10.1038/264746a0 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4580505/ ; https://doi.org/10.1371/journal.pone.0207160 ; https://doi.org/10.3758/s13414-021-02265-6 ; https://pubmed.ncbi.nlm.nih.gov/31264598/ ; https://pubmed.ncbi.nlm.nih.gov/37205669/ ; https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
## Deliverables
- `investigation.md`: approximately 2,011-word new McGurk editorial research investigation, source notes, harmless honest observation exercise, historical methodology bridge, zero commercial recommendation.
- `guide-core.html`: ~1,453-word independent Zen12 buying guide, exact seller description vs evidence separation, buyer objections, 12-minute free exercise and no invented purchase result.
- `presell-A-text-only.html` and `presell-B-optional-film.html`: identical substantive guide; B optional film concept, accessible static poster/transcript with no pretend player; both offsite CTA disabled, nearby plain prospective commission disclosure, no merchant links.
- `mind-hub-alternative-unpublished.html`: polished alternative source-controlled archive proposal, explicitly NOT overwriting PR #172.
- `claims-matrix.csv`: 57 status-tagged seller, science, FTC, permissions, privacy and QA claims.
- `editor-source-register.md`: exact merchant pages and other URLs, editor-only.
- `navigation-search-plan.md`: organic/TikTok journey, original investigation vs commercial destination separation, no dead URLs.
- `privacy-attribution.mjs`: pure, hard-disabled telemetry spec; event allowlist and synthetic aggregate n>=20; no live collection or network.
- `privacy-attribution.test.mjs`, `commerce-contract.test.mjs`: source-controlled security/claims/disclosure tests.
- Original 40-second *conceptual* silent educational film: full renderer source `render_film.py`, six cues `mcgurk-40s.vtt`, `film-storyboard-and-release.md`; offline rendered MP4, poster, review ZIP. NOT a true McGurk stimulus, not an endorsed Zen12 product.
- `ab-test-protocol.md`: hypothesis, experiment ethics, primary metric, safeguards, privacy and no false results.
## Executed verification, no inflated test claim
- Authenticated committed GitHub source readback: 11 key files, including renderer (SHA verified via local `git hash-object`) and captions (SHA verified).
- Actual source bodies of both committed JS test suites run in isolated V8 with Node API compatibility shims: **59 assertions passed** across 8 commerce test cases and the privacy suite; 4 explicit commercial mutation failures, multiple privacy PII payload rejections. This is NOT native Node or hosted CI.
- The first ad-hoc validator attempt was corrected after an assertion incorrectly recognized `aria-disabled` as equivalent to native `disabled`; later source-controlled test uses whitespace-bound native disabled selector. False positives are unsafe: validator now tests concrete mutation.
- Local film Python/Pillow and ffmpeg succeeded: H.264 540x960, 12fps, 480 frames, exactly 40.000 s, 121054 bytes, SHA256 88f7e03e20ab9560ed972bdf31f0a802a32271cd10811f7c6bae04de6a868ee5. Six original stills plus contact sheet visually inspected. GitHub film renderer source blob `5ec302d7058beed1f6bc8df8ec29266647b7e4cb` matches locally executed source; VTT blob `416ff2972c542f6adee728901f9c4ba6b256846f` matches local VTT.
- Affiliate CTA is not enabled; film *only offline*, no hosted first-party MP4 or actual on-site video element in B.
## MUST NOT claim complete
Native Node repo tests and hosted CI not run; native browser/WordPress staging, responsive 360/390/768/1440/1920, screen reader, zoom, WCAG 2.2 AA, Lighthouse, server HTML sanitization, actual hosted VTT synchronization, affiliate approval, payment terms, real orders, and A/B lift NOT verified.
## HARD HOLD
No affiliate account-specific acceptance, product authorized URL, website/TikTok/email promotional terms, usable approval of any marketer-supplied creative, exact current checkout/refund verified, product-specific efficacy evidence, full accessibility/release QA or founder exact-HEAD written publication approval. NO CMS/settings/nav/Jetpack/subscriber/Dispatch change, no merge/deploy, no email send, no analytics activation.

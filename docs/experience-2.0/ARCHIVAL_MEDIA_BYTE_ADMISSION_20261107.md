# EX2 actual-image-byte admission — 2026-11-07

**Release: HOLD.** Companion to draft PR #1484 at base SHA `bc4180300059404aa6fbbfd39715af49ca795bad`. Never merge or publish without founder release approval. Frozen PR #49 unaffected.

## Evidence
Read-only WordPress metadata verifies Apollo media 473: 1041×810 WebP, reported original 78,346 bytes, NASA S67-19766; Franklin media 474: 960×1526 JPEG, reported original 466,043 bytes, a later printed reproduction of the 1847/48 Victory Point Note. NYPL 1258 remains excluded pending rights. **Metadata sizes are not actual HTTP transfer receipts.** Apollo is a crew photograph, not evidence of ignition; NASA does not endorse FV.

The original source-attested private PHP plugin SHA-256 is `91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04`, review ZIP SHA-256 `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`.

The existing browser smoke with all external requests blocked had 10/10 layout passes but **0 successful historical-image transfers**. This PR adds the missing `verify_image_bytes(response.body(), format)` implementation referenced by the existing `verify_receipt`: it decodes complete transferred image bytes with Pillow, rejects tiny, invalid, truncated, corrupt or wrong-format bodies, and returns pixel dimensions, byte count and SHA-256 for comparison with the chosen source URL.

### Executed offline, not real archival photographs
- **6/6 Python regression methods PASS**, including genuine image-decode synthetic controls and malformed/truncated/wrong-size/wrong-MIME/404 negative controls.
- A separate source-attested PHP-output Chromium study at 320/390/768/1440/1920 reported **5/5 correctly blocked/zero-image HOLD** and **5/5 synthetic fixture body-decode passes**, plus **2/2 correctly rejected invalid image scenarios**. Test fixtures are artificial color patterns, never historic media.
- The responsive browser selects `i0.wp.com` WordPress CDN derivatives rather than direct `finalvestige.com` origins at all five widths. Do **not** call this direct first-party origin transfer. Browser `naturalWidth` is responsive-density adjusted; verify decoded response-body pixel dimensions, not equality to `naturalWidth`.

Full locally executed receipt JSON, SHA manifest, alternate standalone admission harness and reproduction commands: downloadable run evidence supplied with the founder's status update. The new helper is committed to the isolated review branch; does not edit public media or staging.

### Still required for acceptance
Run genuine isolated WordPress core + pinned Assembler; capture `response.body()` for both media across responsive widths and run `classify_source` → `verify_image_bytes` → `verify_receipt` on real HTTP 200 responses. Record selected URL, content type, decoded pixels, byte length and SHA per transfer. Independently run axe/WCAG 2.2 AA, keyboard/no-JS and Lighthouse/CWV, plus real Jetpack and verified commercial conversion acceptance. WordPress.com Personal does not provide an isolated native staging clone. GitHub QD and CI remain independent, exact-head gates. **No sales, leads, subscriptions or revenue are established here.**

**Offer → Step → Blocker → Change → Evidence → Owner:** 52-page Focus Fieldbook → archival evidence trust before contextual CTA → HTML image presence falsely looks like genuine archival media success → fail-closed actual-byte decoder → local pass/hold/negative-control evidence above → homepage engineering and independent Site QA; Claude owns Jetpack and attribution; Grok/Praxxis own acquisition. No live writes, installs, posts or spending.

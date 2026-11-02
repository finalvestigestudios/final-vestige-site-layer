# NYPL 1903 map — capture-level image reuse custody
**2026-11-02 | Source-grounded correction | DRAFT / RELEASE HOLD**

## Decision / scope
The seven-chapter homepage candidate used the statement: “NYPL believes this item is in the public domain under United States law.” The evidence collected for *this exact digital capture* does not substantiate that assertion, notwithstanding the 1903 date and the general NYPL collection policy. Withdraw the item-specific claim, keep the original NYPL citation and honest contextual distinction, and **do not treat the visible credit notice as permission to reproduce the image**.

**Reviewed source:** Rand McNally/Brooklyn Rapid Transit system map dated 1903, credited to New York Public Library Digital Collections, image ID **5003296**; the homepage links to `https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0`. NYPL's own rail transit research guide references image ID 5003296; source link: `https://libguides.nypl.org/nyc-rail-transit/companies`. This establishes a route for catalog verification, **not capture-rights certification**.

## Primary institutional policy examined
- NYPL Digital Collections API documentation: `https://api.repo.nypl.org/`. It expressly describes *capture-level* rights statements: No Known U.S. Copyright, CC0, Copyright Held/Managed by NYPL, and Undetermined. The existence of a general public-domain collection does not determine the status of any unverified capture.
- NYPL Digital Collections public items/permissions guidance: `https://qa-digitalcollections.nypl.org/about`. For publicly cleared items, preferred courtesy credit is “From The New York Public Library” with a link to the exact item. Unmarked items are not permission grants, and third-party rights remain the publisher's responsibility.
- Exact original catalog URL for current candidate: `https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0`. Attempts to retrieve the specific capture's item rights through public search / direct web fetch did **not** provide an independently verifiable capture-level rights statement in this review. Do not substitute the similar Brooklyn map item 5003260 or a third-party reprint for image 5003296.
- Historical context is not spatial identity: the 1903 map predates the 1918 Malbone wreck; it is **system context**, not the later temporary curve's engineering plan. Existing story note already makes this distinction.

## Exact proposed editorial correction
**Before (unverified):** `From The New York Public Library. NYPL believes this item is in the public domain under United States law.`

**After (review-safe):** `From The New York Public Library. Reuse rights for this exact digital capture are pending verification; a 1903 map date alone does not establish image-use clearance.`

Apply the same text **once** inside both canonical `index.html` and the *offline proposed WordPress block fixture*, preserving all other 34,000+ characters of editorial chapters and the original catalog link. The fixture is NOT the live WordPress page and must not be described as independently approved production HTML. Do not change actual WordPress media or download/swap the map here.

## Automated custody controls and release criteria
1. Re-pin the exact Git content hashes for the two edited source blobs, compare complete seven-chapter interiors byte-for-byte and require unchanged NASA, Franklin and non-commercial Mind disclaimers.
2. Reject reintroduction of the old unsupported NYPL public-domain conclusion **even if it appears in both proposed and staging content**; reject removal of the original item link even if both source files drift together.
3. Require existing actual isolated WordPress/Assembler/Chromium five-width, image HTTP/MIME/body and axe gates plus mobile CPU/network lab on the *new exact branch*. Compare screenshots with previous staged first screen, but do not claim zero visual differences without a pixel comparison.
4. **Keep publication HOLD** until an independent reviewer obtains the item **5003296 capture's** authoritative NYPL rights label/correspondence, connects the tested WebP image payload's provenance with that capture, verifies any applicable jurisdictional/third-party restrictions, and signs off the exact intended use. A copyright officer/editorial owner must sign off; tests alone cannot.
5. Full manual WCAG 2.2 AA AT/keyboard/touch/200% zoom and WordPress.com Personal-host compatibility still unverified; current private Playground is not hosted certification. Independent QD and founder must explicitly approve production release.

## Unchanged safeguards
No production CMS writes, no subscriptions/users/database export, no new services, no merge/deploy, no change to frozen PR #49, Apollo Research Desk #158, or separate Mind & Perception editorial issue #171. Public WordPress page ID 6 retains 72 Margins entries, Jetpack signup and two Focus Fieldbook links (read-only confirmation earlier in this sprint).

**Editorial release gate: capture-specific rights NOT CLEARED.**

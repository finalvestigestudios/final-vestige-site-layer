# R323 — Print-safe Apollo campaign continuation and NASA PDF link custody

**Staging only · draft · NOT LIVE · HARD RELEASE HOLD.** Parent Issue #150, business gates #820/#818. Stacked on R322 PR #2272. Frozen homepage #49 and Research Desk #158 untouched.

## Reproduced browser defect and fix

R322 adds valid first-party Grok campaign labels to the existing single free Apollo investigation link on trusted click, auxclick or native context menu. When someone invokes Shift+F10 on that link but cancels the menu, its href remains annotated. Printing the research packet in real Chromium puts that campaign-tagged URL into the PDF hyperlink annotation. The exact original R322 JavaScript Git blob a3c858b51005495ebebb326086badc155c1b7e5a reproduces this defect: one contaminated URI in the printed PDF.

R323 adds a beforeprint handler, scoped to existing validated Apollo editorial CTA anchors, that strips query labels before the document becomes a printable PDF. A later actual link activation restores permitted labels for navigation. This does not make a network request or add a cookie, tracking script, additional CTA, product sale, media asset or new historical claim. The PHP enqueued-JS version is bumped. CSS is unchanged.

## Source-controlled actual browser replay

Run: python experience2/apollo-r323/qa/print_link_replay.py

Requirements: PHP CLI, Node, system Chromium at /usr/bin/chromium, Python Playwright and pypdf. The gate runs 8 genuine offline Chromium contexts (320, 390, 1440, 1920px with JS on/off), checks the 11 exact permitted printed HTTPS link destinations including official NASA source records and one free continuation, verifies absence of UTM parameters in actual PDF hyperlink annotations and reproduces the original R322 leak as a negative control. The HTML is emitted by the real staging PHP code through R320's WordPress lifecycle stub. This is NOT installed WordPress or an HTTP/CSP test.

Independent extended local QA: 28/28 genuine offline Chromium contexts from 320 to 1920 px across JS/no-JS/forced-colors/no-CSS, four inspected Chromium PDF outputs, two-instance print reset/reactivation, injected malicious PDF hyperlink rejection, reproducible PNG screenshots and JSON receipts. The complete local evidence archive contains this runner and checksum manifest. The committed gate is smaller; do not confuse the two suites.

Historical evidence remains source-linked: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/history/Apollo204/narr.html . Board authority on Jan 27, meeting on Jan 28, Jan 31 receipt and Feb 3 written confirmation remain distinct. NASA's commercial nonendorsement guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No photos, map pins or NASA product endorsement are added.

## Release blockers

Genuine axe-core; independent screen readers; Safari/Firefox print; actual WordPress/Assembler/shortcode install; native HTTP/CSP, CDN/caching and field CWV; hosted CI/QD; NASA individual media/editorial clearance; authenticated paid product and merchant settlements; verified published Grok asset ID/UTM placement; founder authorization are all unverified. Browser HTTP is blocked in this execution environment. Do not merge or deploy. No production WordPress, Grok/Praxxis TASK-008, merchant, email, affiliate, analytics or paid-services changes were made.

# Page 6 exact editor-source first-screen review (2026-11-06)

DRAFT / NOT LIVE / RELEASE HOLD. Independent of Apollo #158, Mind #171, Grok posting, Site QA and Claude's production/attribution lane. PR #49 remains frozen. No new chapters, assets, tracking, affiliate links, WordPress writes, plugins, purchases or spending.

## Reason

Existing PRs #1207/#1213/#1219 exercised synthetic HTML to test their browser admission logic. WordPress Page 6 already contains seven chapters, the Franklin folio, Jetpack and 72 Margins. Its real secondary hero CTA still links to the blog. PR #1201 proposes a contextual Fieldbook link, but its mobile position and touch target are unverified.

This new source-review command takes the ACTUAL raw UTF-8 WordPress editor content saved to a PRIVATE local file (not a full WordPress database export), verifies its SHA-256 and 72-record/seven-chapter/Jetpack/CTA structure, and creates twelve first-screen PNGs (320/360/390/768/1440/1920px, two variants) in offline Chromium with JavaScript disabled. It reports original-vs-Fieldbook CTA href, text, in-viewport visibility, 44px target, overflow and reduced-motion Margins visibility. Only the single PR #1201 secondary-CTA anchor changes in memory. It never writes raw content to GitHub or calls WordPress production.

## Connected WordPress source receipt

Read-only site ID 256784396; published Page 6; modified 2026-11-05T12:07:24. Exact raw editor content: 150,710 JS string characters / 150,939 UTF-8 bytes. SHA-256: 1188d32a101896f12af9823dd7ca4b8a12b0c36684e82c069f23855a698e5669 (pure JS digest checked against SHA-256 of abc standard vector). Seven chapter destinations exactly once; one exact flagship wrapper; 72 ordered Margins indices; one Jetpack subscriptions block; one hero blog CTA and an existing Focus URL. Source CSS continues to hide 71 Margins under reduced motion; the existing proposed remedy is PR #1062.

## Local reproduction (new private source export required)

Run in an exact GitHub checkout with native Python Playwright and /usr/bin/chromium:

    python -m unittest discover -s qa -p 'test_fv_page6_source_firstscreen_review.py' -v
    python qa/fv_page6_source_firstscreen_review.py --editor-source /private/page6-edit-content-utf8.html --expected-sha256 1188d32a101896f12af9823dd7ca4b8a12b0c36684e82c069f23855a698e5669 --output /private/new-fv-source-review

The export must be the raw content string, not rendered output, a JSON envelope, or subscriber/user records. Keep it outside the repository and do not upload it. Obtain and record a new independent digest after any WordPress edit; never bypass source drift. The output directory must not exist.

## Built vs tested vs live

BUILT: fail-closed source/CTA reviewer with six-width before/after first-screen image capture and redacted receipt. TESTED: 3 native unittest methods passed (including seven bad-source mutations); a synthetic no-JavaScript Chromium fixture generated 12/12 screenshots and detected missing reduced-motion Margins visibility. Separately, read-only connected WordPress source checks verified the current structure, date and digest. NOT TESTED: full actual 150,939-byte exported Page 6 in native Chromium (connector data cannot be mounted as a local file in this runtime); live WordPress/Assembler/Jetpack render; 200% native zoom; real archive image transfers; full axe/WCAG 2.2 AA; Safari; Lighthouse/CWV; real subscriptions or purchases. The review screenshots are NOT production screenshots.

## Offer → funnel step → blocker → change → evidence → owner

Offer: free 52-page Seven Day Focus Fieldbook. Step: high-intent visitor sees source evidence, then CTA, then confirmed lead, then independently verified purchase. Blocker: current hero blog CTA and unverified mobile CTA clarity. Change: source-identical current vs contextual Focus CTA offline browser comparison. Evidence: source contract verified, native test logic verified, live conversion lift UNKNOWN. Owners: homepage engineer and independent Site QA for UI; Claude for commercial attribution/checkout; Grok/Praxxis for social campaigns.

Release decision HOLD. No WordPress production changes, merge, deployment, plugin install, analytics modification, affiliate activation, email, posting or spending. Isolated WordPress Playground/Assembler admission, rights clearance and founder release approval remain mandatory.

# R81 precise review plan (all production gates CLOSED)

A = complete text guide; B = same byte-for-byte guide with 40-second original optional film poster/transcript. Hypothesis: B may aid comprehension/engagement, or may distract. No tested lift. Need preregister primary metric before any approved experiment; no individual/PII tracking; no unsupported conversion conclusions.

Video website playback intentionally absent: first-party hosted MP4, VTT captions, transcript, actual keyboard/a11y synchronization and performance tests mandatory before enabling. Offline film can be reviewed independently. No autoplay/third-party embeds.

Engineering tests: run `node --test mind/the-white-bear-r81/tests.mjs` after clone. Must verify exact committed files. Browser on WordPress staging at widths 360,390,768,1440,1920; keyboard, zoom 200%, contrast, screen reader, no-JS, reduced motion; WP HTML sanitizer; Lighthouse mobile. NONE verified in production. No CMS write.

Privacy: `attribution.mjs` is unimported disabled synthetic-only code; four categorical fields only; rejects identifiers, URL, timestamps; reports only groups n>=20. No site tracking and no actual sales feed.

FTC: disclosure visually beside native disabled button, not hidden on a disclosure page. Seller 12min=1hour and health outcomes omit from advocacy; claims matrix separately records prohibited representations. Terms page inaccessible November 2, 2026. Partner acceptance/link/channel rights unverified. No affiliate activation.

Coordination: Issue #150 homepage/PR #49 not modified; canonical Mind PR #172 untouched; Site QA #126 may independently review; Issue #174 Dispatch emails and Jetpack Focus welcome not edited. No merge/deploy/publish absent founder approval.

# Final Vestige Studios — Mind R51 (2026-11-01)
## The Second Number / Zen12 independent offer guide / optional original short

**Current state: UNPUBLISHED, DRAFT, COMMERCIAL & RELEASE HARD HOLD.** Scope is strictly Issue #171. No WordPress writes, homepage PR #49, canonical Mind PR #172, art Issue #150, Jetpack newsletter, existing Focus funnel, Dispatch Issue #174, merchant activation or tracking changes.

### Main outputs and responsibilities

- **Independent investigation:** investigation-wordpress-draft.html, "The Second Number Fell Between Frames" (over 2,100 words), primary attentional-blink experiments, methodological bridge to the real Puységur source archive, no commerce.
- **Verified independent Zen12 buyer guide source of truth:** zen12-guide-core.html, approximately 1,970 words, exact seller-described 12-min/12-level/4-format product, tier table, actual source links in editor register, free 12-minute format-preference practice, independent EEG/meditation research and rigorous unverified-claim boundaries, FAQs, prospective disclosure and genuinely disabled visit control. Do not use vendor testimony as scientific proof.
- **A/B WordPress drafts:** zen12-a-wordpress-draft.html text-only; zen12-b-wordpress-draft.html EXACT SAME guide content plus original static film-poster concept and complete readable transcript. These are source-controlled templates, not WordPress CMS drafts or published pages. No false play button.
- **Review-only functional video page:** offline-b-with-real-video.html uses optional 40-second native HTML5 video with controls, preload none, poster and timed VTT, same guide; locally works when film-40s.mp4 is next to HTML. Do not host in production yet.
- **Film reproducibility:** render_film.py draws six original scenes and renders silent H.264 via Pillow+ffmpeg, precisely 40 seconds (540×960; 12fps; 480 frames). Poster SVG and VTT included. Source film is an illustration, **NOT a scientifically valid RSVP test**, nor Zen12 endorsement or product test. First 1992 study was letter-based, not the film's indicative 7/4.
- **Attribution:** privacy-attribution.mjs is always OFF, accepts only synthetic four-key enumerated events and suppresses under-20 counts. Not imported by either WordPress candidate. No data collection.
- **Evidence:** claims-permissions-matrix.csv (50 claim/authorization decisions); sources-and-permissions.md (editor-only seller exact URLs + scientific/FTC evidence); navigation-experiment-QA.md; pilot.css; original standalone noncanonical mind-hub-alternative-draft.html expressly deferring to PR #172.
- **Tests:** verify.test.mjs validates generated parity, zero clickable merchant links, disabled button/disclosure, no scripts/forms/autoplay, original film captions/transcript, basic CSS/a11y static guards, article boundaries, 5 adversarial commerce mutants and pure synthetic privacy. No automated test claims WCAG or real browser acceptance.

### Reproduction (read-only, no website contact)

Node 20+ for text build and tests:
    cd mind/attentional-blink-zen12-r51
    node build.mjs
    node --test verify.test.mjs

Optional offline video rendering, requiring Python Pillow, DejaVu font and ffmpeg:
    python render_film.py
    ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,avg_frame_rate,nb_frames -show_entries format=duration,size -of json attentional-blink-evidence-40s.mp4
    cp attentional-blink-evidence-40s.mp4 film-40s.mp4
    # Open offline-b-with-real-video.html locally; ensure film-captions.vtt and film-poster.svg are alongside it.

Actual local H.264 rendered independently during this sprint. It is **not** uploaded to WordPress; binary not stored in this text-only GitHub PR. The user-facing offline review ZIP includes the MP4 and a functional minimal video player.

### Key safety and publication rules
- Actual official seller-specific page https://zen12.com/hnp and catalog https://inspire3.com/ examined; describe seller package specifications as seller reports. Current price and discount deliberately absent. Current checkout/refund and permissions **not** settled.
- Health/meditation benefits advertised on the sales page do not follow from the 2023 binaural-beat review or 2007 meditation training study; no "1 hour in 12 min" endorsement. See matrix and exact URLs in editor source register.
- Public affiliate network or Limitless Labs creative does not establish Final Vestige account-specific Zen12 rights, authorized earning URL, website/TikTok/EMAIL rights, or approved creative.
- No merchant link, script, form, iframe, tracking, consumer data, subscribers, campaign sends or new Jetpack signup.
- Publication requires active approved exact partner terms, independent claims/legal/UX review, full browser+WordPress staging and CI, caption sync, first-party hosting, Site QA, and **explicit founder approval of exact release SHA**. Do not merge/deploy/live write by default.

Reference canonical destinations already live: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ and https://finalvestige.com/focus/ .

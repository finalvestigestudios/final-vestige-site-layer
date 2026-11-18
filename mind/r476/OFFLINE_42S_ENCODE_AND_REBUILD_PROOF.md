# R476 reproducible offline film proof (post-initial QA supplement) — 18 Nov 2026
**Generated locally, NOT staged, NOT live, NOT embedded on WordPress and NOT a user A/B experiment.**

The source-controlled generator [build_optional_film.py](./build_optional_film.py) creates all six original title-card PNGs and joins them with gentle dissolves into one silent 42-second H.264 preview. No licensed third-party music, vendor assets, visible experimental participants or copied McGurk stimuli appear. The six separate captions are also in [ZEN12_OPTIONAL_42S_CAPTIONS.vtt](./ZEN12_OPTIONAL_42S_CAPTIONS.vtt); buyer-guide B provides the complete transcript. The standalone MP4 output exists in the working artifact container for founder review, **but binary media is not committed to this PR**. The site cannot play it from a GitHub media URL; safe hosting/encoding and controlled native video markup remain a separate approved release step.

## Actual executed commands and measurements
- Python program: python build_optional_film.py, using Pillow + NumPy and installed FFmpeg/libx264; six original PNG cards rendered successfully.
- FFmpeg generated 42-second video with five soft dissolves; **ffprobe measured H.264, 1280×720, yuv420p, 24/1 fps, 1,008 frames, duration 42.000000 s, 481,662 bytes** (below proposed 500 KB budget in this offline artifact).
- **SHA256 of output video:** 539e4a252d6d87b54af6f877fa4e0eae0248f25d6290ca85adda92dfae042b98.
- Program rerun under the same local environment. Second rendered output had the exact same SHA256, confirming **bitwise reproduction in that environment** (not yet tested across build systems).
- Frame at 19 seconds was extracted and visually inspected for legible card, contrast, margin and text placement. This is manual visual inspection of a frame, not a WCAG audit or evidence of every-frame accessibility.
- No audio track (intentional). Text is visible on screen; VTT captions and transcript are available separately. Any future hosted player must still provide a real control/track and transcript with keyboard/screen-reader/browser QA.
- Reviewed primary and vendor sources remain separate; no interpretation that McGurk speech perception establishes Zen12 efficacy.

## Remaining hard holds
Original exact media is available only as a review artifact; it has NOT been deployed to an asset host, added to WordPress, encoded as WebM, played under representative mobile browsers, checked for reduced motion/epilepsy concerns, or passed Lighthouse, CWV, WCAG 2.2 AA or actual A/B. No first-party analytics, affiliate URL, checkout, email or conversion event is live. Source-controlled A/B pages still contain only the original poster/transcript concept and no loaded media. All prior commercial gates, Refersion PENDING witness and founder/QA approvals remain unchanged.

# R82 Original 40-second film: actual rendered offline asset, NOT website media

**Title:** *The Color Was Always There*. **Format:** silent original six-scene H.264, 540×960, 12 fps, 480 frames, exactly **40.000 seconds**. Renderer **`render_film.py`** is committed to this PR; its Git blob SHA **`c8aaa39429020619fd687abe30f00334b52b8b13`** matches the locally executed renderer via native `git hash-object`. No copyrighted documentary footage or seller creative was used.

**Rendered artifacts are in a separate offline conversation review package**, not in GitHub or live WordPress. MP4 SHA-256: `90d915866d108e843207953833703a33e3ba685024bc18b62b318c3b25b1c83e`. Poster SHA-256: `8612261c6a9795082135b5b6e91efddceef722d26a1cfefb6236b33260e0fb5b`. Source renderer SHA-256: `ecab5d18af8434bf551c6ac54a877eadb99709da8d77deea4394a282ec5a3a8c`. VTT SHA-256 `ba561a110f96e4425cf3e087ae914be9c5e447633063b9d93084cbab05f13fa2`.

**Content integrity:** Film intentionally animates a colored patch fading, unlike the actual unchanged stimulus in a viewer's observation exercise. Narration/captions state this explicitly. It illustrates how changing perception and changing media are different; neither visually verifies Zen12, a treatment, or universal outcomes.

**Actually executed locally 2026-11-02:**
- Pillow + ffmpeg produced the final MP4, original poster and six-scene contact sheet. Contact sheet inspected and initial too-long heading corrected before final render. All 12 large title lines fit within video safe width.
- FFprobe verified H.264, resolution 540×960, 12fps, 480 frames, 40 seconds. Native VTT script checked six contiguous cues covering exactly 0–40 seconds; zip integrity passed.
- Native Chromium/Playwright offline HTML markup tested at 360, 390, 768, 1440, 1920 widths with JavaScript OFF: no horizontal overflow, one video with controls and no autoplay, one caption track, accessible transcript summary, no forms/scripts/iframes.
- Initial direct `file://` browser navigation was blocked by environment administrator. We transparently adapted to `page.set_content` and inserted the real MP4/VTT via base64 data URLs. Chromium decoded the real video at 40 sec/540×960, read six text-track cues and recognized expected text at 15sec. **This is local media QA, NOT testing WordPress staging or first-party hosting.** It did not establish audible content, since film intentionally silent; screen-reader acceptance not performed.
- Actual player screenshot saved only in offline review package, not a production destination.

**No website embedding**: R82 candidate B displays a clearly labeled storyboard poster + complete timed text transcript, with no `video src` until later hosting and release approval. Actual rendered film is available independently for review. Before any publication, obtain first-party media placement, captions, real mobile/browser test, proper audio descriptions if required, CWV measurements and final founder approval.

# R39 Actual Offline Film Rendering & QA Evidence — 2026-11-01

## Actual completed film
Original title: *The Word and the Ink* — six silent educational cards, no stock art, no music, no seller footage. This is a schematic educational explainer, **not an actual Stroop laboratory protocol** or product efficacy test.

The MP4 was actually rendered locally, with the exact Python source included in this branch at `render_stroop.py`. The source file Git blob SHA `13dc80b61c92544861a2c01df7f8282e156af43d` **matches the Git SHA of the locally executed renderer** (`git hash-object /mnt/data/fv_mind_r39/render_stroop.py`). Thus the committed source is byte-identical to the executed renderer.

- Offline review MP4: `/mnt/data/fv_mind_r39/stroop-suggestion-40s.mp4`
- Offline poster: `/mnt/data/fv_mind_r39/stroop-suggestion-poster.png`
- Offline visual six-scene contact sheet: `/mnt/data/fv_mind_r39/contact-sheet.png`
- FFprobe: H.264, 540x960, 12fps, 480 frames, **exactly 40.000000 seconds**, **145,932 bytes**.
- MP4 SHA256: `74d6ee39c333979e075f4fb062f8cfe3009ade16f5d138ee86fc6c801df55ce1`.
- Six representative frames independently extracted by FFmpeg and inspected on a contact sheet. A text-collision in the induction comparison (scene 4) was identified, the renderer corrected, and the film re-rendered and reinspected. Final inspection: no clipped/overlapping box text observed.
- On-frame educational summaries disclose study limitations, avoid unsupported medical or wealth effects, and do not promote a purchase. Four decades ago? No: studies cited are 2002, 2005, 2006 (not source footage). No flashing/strobing frames, moving subjects, autoplay, audio, licensed creative, external network or third-party calls.
- Captions / timed scene-description `video-captions.vtt` and a complete draft transcript are already source-controlled. They represent content cues, not recorded speech (film has no audio).
- **Not hosted on WordPress, not uploaded to media library, not running in page B.** The draft continues displaying a static poster/transcript without fake playback. Actual browser playback, poster sizing, caption synchronization, localization, Lighthouse/CWV, screen-reader and no-JS staging behavior are NOT yet verified.
- If approved for publication, first-party `<video controls preload="none" poster="...">` with a valid local VTT track and plain HTML transcript. No autoplay; tests at 360/390/768/1440/1920 and 200% zoom plus keyboard and reduced motion.

## Source/release separation
The video illustrates Stroop selection/suggestion research, not Zen12 itself. The independent product guide correctly states that no cited study establishes Zen12's hour-in-twelve claim, and no partner earning URL exists in any review page. No CMS writes, dispatch sends, affiliate activations or browser measurements were performed.

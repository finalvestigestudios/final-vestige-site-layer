# R377 original 42-second film: local render evidence and hard hold

**2026-11-14 PT**. This is a **developer-local demonstration**, **not a committed MP4**, WordPress attachment, published media, or deployed landing page. The source-controlled inputs are `render_film.py`, `ORIGINAL_42S_POSTER.svg` and `ORIGINAL_42S_CAPTIONS.vtt`, with the independent buyer-guide variant B in this folder.

## Actually executed in isolated local runtime

- `python /mnt/data/fv_mind_r377/render_film.py --output /mnt/data/fv_mind_r377/original_42s_preview.mp4` — **PASS**.
- `ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,avg_frame_rate -of json ...` — **PASS**, H.264, 640×360, 12 fps, **42.000000 seconds**, **88,523 bytes**, silent.
- Local file SHA-256: `b793e0c24130c8197c063c4e29b0c738da1f1eb1a6f86c39393d37d152a67ac2`.
- Source renderer SHA-256 from local runtime: `3e118d35659a693ddbe242e79efc14f459182e3efd5706ec59096f7462c4ef5f`. Local renderer length: 3,255 UTF-8 bytes. The connected GitHub file reported 3,255 characters when committed; do not represent this as an independent byte-for-byte digest comparison of the remote file.
- Six frames sampled at seconds 3.5, 10.5, 17.5, 24.5, 31.5 and 38.5. Visual spot-check showed original dark archival-style 2D graphics, legible text, no outside photography, clinical scan, third-party art, forced motion or sales CTA.
- The film is silent, uses no stock video, no voice clone, no third-party stream or licensed music. Its visual scene headings are not word-for-word narration; a later fully narrated version would require accurate corresponding captions. **Do not ship the current six-caption VTT as synchronized captions for a narration track that does not yet exist.** The full transcript and six draft timed cues in B are a storyboard for later audio production, not verified media captions.

**Availability:** The sample MP4 and six-frame contact sheet exist only as artifacts of the local assistant runtime. They are not stored in GitHub, not hosted on the FV website, and have no public URL. R377 buyer variant B explicitly says the branch itself has no playable media. The local rendition establishes that a lightweight original 42-second video is *technically renderable*, not that the end-to-end WordPress video component works.

## Remaining media acceptance (NOT PASS)

Review historical claim and graphic rights; correct any narration/caption mismatch; ensure on-demand native player controls with a local approved MP4, `preload=none`, original SVG poster, keyboard and screen-reader fallback, no-JS-readable transcript; demonstrate no autoplay and reduced-motion experience; stage and measure 360/390/768/1440 widths with Safari/Chromium/Firefox, real network 3G/4G transfer and Core Web Vitals. Confirm final HTML survives WordPress sanitization and does not introduce a new analytics library or consent violation. Record optional media exposure separately from independently confirmed paid outcomes.

**Release remains HARD HOLD for merchant approval, checkout/returns, media, QA and founder sign-off.** Do not merge, publish, run paid ads, edit Jetpack/Dispatch, or activate any external merchant CTA.

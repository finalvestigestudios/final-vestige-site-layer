# R31 — Original 40-second film identity, captions and approval gate
The only verified existing video master is the original offline R30 film, produced for [PR #374](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/374). It is not in the public GitHub repository, not served by WordPress and not embedded here. It is a silent 540×960 H.264 MP4, 12 fps, 40.000 seconds, 166697 bytes. Reported original SHA-256: 7a1cc8e4a0e0047bd2ea090b79785f9555a6a9e996d63345a54b918ff3a231ae. Verify SHA again before host upload. Working binary: /mnt/data/fv_mind_r30/zen12-evidence-40s.mp4.

The film actually opens with the chronostasis/clock-hand illusion, not the Shams sound-induced flash. That conceptual difference must be kept explicit: the sound-induced flash article is independent research, and the optional film is a general Zen12 evidence explainer, NOT a simulation of the article's experiment or proof of vendor efficacy. The R31 poster is original alternate artwork, not a frame from the R30 film.

The source-controlled zen12-40s.vtt is a verbatim copy of the R30 caption file. In the R31 version B guide, the optional transcript uses the exact same five time ranges:
00:00–00:08 second-hand / shifting gaze;
00:08–00:16 chronostasis and experience versus clock;
00:16–00:25 merchant 12-minute audio, three tiers, four styles;
00:25–00:34 not proven to deliver one hour's benefits;
00:34–00:40 free baseline, research guide, self-directed decision.

When authorized to host, validate the bytes with:
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate -of json zen12-evidence-40s.mp4
sha256sum zen12-evidence-40s.mp4

After first-party hosting and independent CMS/QA clearance, use HTML video controls, preload=none, playsinline, an actual MP4 source, a caption track kind=captions with English srclang, static poster and adjacent complete text transcript. DO NOT install a nonfunctional player now, autoplay, use Vimeo/YouTube, hide captions or require Javascript to read the page. Verify spoken-like timing of typographic frames to each caption line manually. Test keyboard pause/seek, fallback, caption contrast, motion sensitivity, 360/390 mobile overflow, CWV/LCP and browser media byte-range behavior. Separate founder approval needed for video upload, WordPress rendering and any launch.

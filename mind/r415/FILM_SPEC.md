# Original optional short-film specification — R415

Length: 42 seconds. Creative: original typography and metaphor illustration, no third-party photography, stock film, music, paid voice or copyrighted media. Audio: intentionally silent; transcript records on-screen text, NOT a spoken narration.

| Seconds | Image / caption |
|---|---|
| 0–7 | Your eyes move down the page |
| 7–14 | A different thought enters |
| 14–21 | The lines keep passing |
| 21–28 | Then you notice: what did I just read? |
| 28–35 | Notice the lapse. Return to the sentence |
| 35–42 | A useful experiment. Not a miracle |

build-film.sh generates offline H.264 640x360, 2fps, no audio. The MP4 is generated but NOT source-controlled; all reproducible source is committed. Variant B includes native video controls, preload=none, no autoplay, SVG poster, VTT captions and visible transcript. Run the build in a checkout and confirm file at the expected relative path before testing or release. No video file in GitHub means the B video element is not yet functional on github.com.

Acceptance: playable exactly 42 seconds, captions aligned, 360/390/768/1440 widths, keyboard, screenreader, reduced motion, no-JS, source integrity, first-party hosting and actual page performance. A and B differ only by the optional film module. No inferred conversion lift.
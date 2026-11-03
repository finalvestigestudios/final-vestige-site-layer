# R89 original educational film: actual local production receipt

**Topic:** *The Sound You Saw*, a McGurk and MacDonald 1976 **schematic** historical explainer, **not** experimental footage, a controlled lip-sync stimulus, an auditory illusion test, a Zen12 demonstration, or a merchant testimonial.

**Status:** Rendered offline and delivered as separate reviewer artifacts only. The source-controlled A/B web pages contain NO live video element, autoplay or merchant link. No WordPress upload, first-party media hosting, or live site/browser caption verification performed.

## Native production evidence

Executed locally with Python + Pillow and `ffmpeg`; `ffprobe` returned:
- Actual MP4: `the-sound-you-saw-40s.mp4` — **40.000000 seconds**, 540×960, **12 fps**, **480 frames**, H.264, 567,271 bytes.
- Poster PNG: `poster.png` — 22,205 bytes.
- Contact sheet: `contact-sheet.jpg` — 98,305 bytes.
- Six contiguous original WebVTT cues covering exactly **00:00:00.000–00:00:40.000**; timestamp validator PASS.
- Offline HTML5 local review `review.html`: native video controls, `preload=none`, poster, first-party relative local media links, `track kind=captions` (English, default), and always-visible transcript. This is only a static reviewer **concept** until actual browser playback is verified.

## Source and integrity verification

The **exact committed GitHub `render.py` blob** is `b67af8feeec2891a0b1a09e4b3e4fab4494cfdb9`, matching the **locally executed Python file** according to native `git hash-object`.

The **exact committed GitHub `40-second-film-captions.vtt` blob** is `aaae1a2be3c5359e7256a84f551cfd9998666dfb`, matching the **locally packaged VTT**.

SHA-256:
- MP4: `21c54438e3677bf5b50dbf8cbcdf673a74bfe73ee3cea447f7f3fdd49602be1b`
- Poster: `1ea464dd6860bb866df673a83c7e21d1ffad802d0701a5984db83445c4775534`
- Contact sheet: `8326c2ad2815bc2e15b1a9bd538fcfe7bf2f777010913b042dee20090cd71ebc`
- Offline ZIP: `7e4cae4b9fa76f8db4dcad6c317f1ac7aac8a2bc880a0a3e6af3790eccaa4ecb`
- VTT: `c3197ba0893da064ad48ad297b60d014c2dabf8d80528450b35d298a787d9fac`

Verified ZIP integrity using Python `zipfile.testzip()`: PASS. Film frames and poster are original programmatic illustrations; no borrowed image/video, remote media, voice imitation, paid services, or externally sourced assets. **No soundtrack**: intended as an accessible silent educational explainer. The VTT is a textual description of the concepts, not a transcript of audible speech.

## Reproduce / remaining release conditions

Run `python mind/the-sound-you-saw-mcgurk-r89/render.py` with Pillow and ffmpeg installed. Locally this produced the above metadata. Rendering may differ in binary hash on other FFmpeg builds; validate metadata, 40.0s and 480-frame count, source integrity and timing.

Before testing a hosted B variant, create a founder-approved first-party media location with an approved poster and WebVTT file. Verify relative URLs, manual playback, caption synchronization, transcript, keyboard and screen reader, page weight/Core Web Vitals and 360/390/768/1440/1920 display. Disclose that this illustration does not reproduce the actual McGurk illusion. Partner approval, published Zen12 guide and founder site/affiliate activation are separate hard holds.

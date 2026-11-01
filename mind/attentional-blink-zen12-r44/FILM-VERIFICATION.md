# R44 actual original film — offline production and verification

**Video production completed after the first R44 source-only QA record.** This addendum supersedes earlier statements that no MP4 existed; **the MP4 is an OFFLINE review asset**, not uploaded to GitHub binary storage, WordPress, or a public host, and is not wired into WordPress candidate B. Candidate B intentionally still displays only a self-contained original poster and transcript; it contains no fake play control or autoplay.

- File available in automation artifacts: `/mnt/data/fv_mind_r44/attentional-blink-40s.mp4` (non-public working artifact).
- Local original poster: `/mnt/data/fv_mind_r44/attentional-blink-poster.png`.
- Reproducible production source committed at `mind/attentional-blink-zen12-r44/render_attentional_blink.py`.
- Exact committed Git blob SHA **`8290a3fcce03a119346e609af4f5f744ede2e0b7`**, **identical to `git hash-object` of actually executed local Python file**.
- Video SHA-256: **`827921a4550c8004eef8784c780f6a305cd7ff6f991d89d0220177602b2244d2`**.
- FFprobe of actual rendered MP4: **H.264**, **40.000000 seconds**, **540x960 portrait**, **12 fps**, **480 frames**, **126,406 bytes**, no audio track.
- All **six** representative scenes were exported and visually inspected in a contact sheet; readable text remains inside frame and major headings/captions do not collide. Original text cards, number diagrams and graphics rendered using Pillow and FFmpeg; no copied footage, merchant graphics or music.
- It is a **silent text-card research explainer**, not an actual rapid-stream experimental demonstration and not a clinical/product experiment.
- Existing six-cue `film-captions.vtt` remains a **proposed accessible timed text narrative** and is **not yet validated against hosted playback and narration**. A proper released video should either ensure exact synchronized text alternatives to the final visual narrative or produce accessible captions for any subsequently recorded voiceover. Do not assume this VTT is already production synchronized.
- No third-party paid SaaS, no live media upload, no data collection, affiliate URLs or release action.

**Still required before B becomes a playable live page:** Founder-approved first-party media hosting, accurate timestamp/text review on the actual hosted asset, keyboard/AT/200%-zoom/responsive and no-JS verification, browser performance/CWV, FTC/partner approvals and founder CMS/release approval.

**Production command:** `python render_attentional_blink.py` with Pillow and installed FFmpeg. The script uses locally available DejaVu fonts for rendering and never copies font files into the repository or user bundle.

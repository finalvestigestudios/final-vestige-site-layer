# Zen12 / The Second Target — optional original 42-second film production card

Status: UNPUBLISHED / NOT ENCODED IN GITHUB / NO PLAYABLE FILM IN THE REVIEW HTML.

This is an original silent motion-graphic concept. It uses no licensed third-party stills, logos, voices, testimonials, seller creative, music or documentary imagery. Its six caption lines can be recorded as narration by an authorized voice artist later; silent playback with optional subtitles must remain comprehensible without voice.

## Timed storyboard
- **00–07 s**: deliberate motion of isolated letters and two gold-highlighted targets; narrator introduces failure to report T2. Do not claim this reproduces the experiment.
- **07–14 s**: dark cut; “The attentional blink” with tiny disclaimer “Not a literal blink”.
- **14–21 s**: two measured bars; label “3 months intensive training / Slagter et al. 2007”, avoid invented graph values.
- **21–28 s**: distinction “Product trial? Not conducted.” and “12 min = 1 hour? Seller claim, not independently verified.”
- **28–35 s**: original facsimile-style checklist, “Files / Evidence / Checkout terms”.
- **35–42 s**: Final Vestige brand neutral CTA “Try the free /focus/ Fieldbook, then decide”; no merchant hyperlink.

The SVG is a **poster concept**, not an experimental screenshot. `ZEN12_42S_CAPTIONS.vtt` contains six captions and is complete for the 42-second silent motion treatment. Any final encoded video needs independent capture and caption synchronization QA. No autoplay, default `preload=none`, no automatic video asset download on mobile, and a visible text transcript are mandatory. Only after film exists should a future review insert `<video controls preload="none" playsinline poster="..."><source src="..." type="video/mp4"><track kind="captions" ... default></video>`. No JS required. No speculative affiliate link.
  
## Hypothesis and controlled test

A: independent source guide. B: **the same substantive guide** plus a user-initiated 42-second film. A/B assignment must be done by Claude in a privacy-preserving manner through existing measurement infrastructure, without introducing a new script or email list, and only with release approval. Primary outcome is **independently verified paid orders/affiliate commissions net of fees and refunds per 1,000 qualified human sessions** (7/30-day cohorts), not play rate, clicks or unauthenticated checkout starts. This hypothesis can fail; small samples must be flagged.

## Performance and a11y acceptance

Poster 1200×630 original vector, lazy load. Video target 1280×720 at conservative bitrate, no music/external trackers. Verify on 360, 390, 768, 1440 px viewports; 200% text zoom, keyboard open/close/controls, contrast, focus outline, captions, correct reading order, reduced motion, muted/no-audio comprehension, failed-download and no-JS states. Reject any option requiring synchronous third-party player scripts.

## Rights and source notes

- Source experiment: https://pubmed.ncbi.nlm.nih.gov/1500880/
- Meditation intensive training: https://pubmed.ncbi.nlm.nih.gov/17488185/
- Current seller page: https://zen12.com/
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking

Built-in FFmpeg `drawtext` implementation may be created and tested off-line; do not assert production film is already encoded, hosted or viewable.
# R84 source-and-security QA review sheet — CLOSED

**No merge, CMS write, send or merchant activation authorized.** A and B embed the exact same substantive Zen12 guide. Their differences are confined to B's optional original-film preview/storyboard/transcript and variant labels. A is text only.

### Evidence
- 1999 Simons–Chabris journal primary DOI: https://doi.org/10.1068/p281059 ; author hosted full text https://www.chabris.com/Simons1999.pdf . 2010 Simons DOI: https://doi.org/10.1068/i0386 . Most et al. 2005 https://doi.org/10.1037/0033-295X.112.1.217 . None tests Zen12.
- Official sales source https://zen12.com/hnp ; About https://zen12.com/about ; Research https://zen12.com/research ; checkout https://zen12.com/getstarted ; privacy https://inspire3.com/privacy/ . All public seller claims; no vendor product use, price, commissions, funnel approval, private swipe or earned URL verified. **Terms https://inspire3.com/terms/ inaccessible**.
- Independent review https://pubmed.ncbi.nlm.nih.gov/37205669/ (14 EEG studies, 5 aligned, 8 contradictory, 1 mixed; NOT Zen12).
- FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . Near-link disclosure does not cure unsupported benefit claims.

### UX, commerce and accessibility
- Product links are disabled native HTML buttons; no merchant hyperlinks in landing page, no affiliate tracking. Existing Focus links are optional, no new form.
- No script, iframe, third-party video or autoplay in the reviewer blocks. B deliberately ships no live video source because first-party media hosting and caption synchronization are not approved.
- Poster is original schematic artwork, not research footage or a brainwave visualization. Offline MP4 is silent with 6 caption intervals, accessible text transcript and first-party local viewer. Do not treat animation as measured experiment.
- Scope CSS to .fvm84; headings and link focus indicators present; 44px navigation touch height; reduced motion stylesheet. Actual Gutenberg rendering and WCAG2.2 AA screen-reader assessment pending.
- A/B film benefit is hypothesis, not conversion evidence. No session or purchaser data collected; synthetic attribution code is unimported, rejects identifying fields and suppresses n<20.

### Testing checklist
- Source-controlled reproducible native Node command: `node --test mind/the-gorilla-that-vanished-r84/tests.mjs`.
- Film command: `python mind/the-gorilla-that-vanished-r84/render_film.py` with Pillow and ffmpeg. Document actual execution and build hash in #171; binary is in offline handoff, not in Git.
- `ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames -of default=noprint_wrappers=1 the-visitor-was-visible-40s.mp4` should show 40s, h264, 540x960, 12fps, 480 frames.
- Open local `offline-review.html` in browser to verify poster, native controls, play/pause, English VTT cues, visible transcript, mobile sizes and no horizontal overflow. A local file URL may block WebVTT; use an approved local HTTP server instead. This cannot replace staging site QA.
- No live test results or customer conversion results can be claimed.

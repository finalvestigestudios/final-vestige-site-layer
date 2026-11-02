# Final Vestige Mind & Perception — R78 Independent Draft

**November 2, 2026 · NEVER PUBLISH OR MERGE WITHOUT FOUNDER RELEASE APPROVAL**

This is a fully isolated development package under the Mind & Perception editorial + ethical Inspire3 presell workstream. It adds **no production WordPress content, navigation, email, tracking, or affiliate functionality**. It does not modify Issue #150, flagship homepage PR #49, Mind hub PR #172, or Dispatch #174 material.

## Files
- `investigation.md`: original 2,034-word investigation, *The Door That Hid a Stranger*, based on Simons and Levin's 1998 change-blindness field experiments, with earlier 1997 precedents, careful methodological limitations and a primary-source reading desk. **No merchant recommendations**.
- `zen12-guide-core.html`: approximately 1,484 visible words, a specific official-product purchasing guide with seven buyer questions, a free three-session listening-format diary, seller/independent evidence separation, checkout and privacy considerations, a near-CTA future-commission disclosure and native `disabled` CTA.
- `zen12-a-text.blocks.html`: complete WordPress Gutenberg custom-HTML **TEXT-ONLY** candidate. No external checkout.
- `zen12-b-original-film.blocks.html`: complete **IDENTICAL** substantive guide, prefaced by original 40-second educational film illustration and six timestamped full transcript cues. Film is educational, *not* a demonstration of Zen12. Embedded video intentionally NOT activated until media hosting/QA.
- `mind-hub-noncanonical.blocks.html`: four-stream archive prototype; not an alternative to canonical PR #172. Only live verified links (Puységur, Focus, editorial policy).
- `claim-source-matrix.json`: 22 exact source addresses, 39 granular claim/permission determinations, twelve fail-closed activation gates.
- `attribution.mjs`: entirely disabled; synthetic-only no-PII categorical validation and groups <20 suppressed. No real collector, sessions, identifiers, referrers or purchase claims.
- `tests.mjs`: 36 native Node test bodies covering permissions, source mapping, exact guide identity, native disabled controls, disclosure, unexpected outbound actions, data rejection and captions.
- `render_door_film.py`: **full exact executed local Python/Pillow/ffmpeg renderer**, SHA1 Git blob `f5801f4172a69559ce4bb029e5709b3c6a8d4c2e`. Local identical Git blob verified against GitHub.
- `film-captions.vtt`: actual exact local captions, Git blob `7d37c3319a517d0484e2181ba7f4e40c020c5027`, six contiguous cues covering 0–40.000 seconds.
- `AB-AND-QA-PLAN.md`: prespecified no-lift-claim A/B hypothesis, traffic measurement guardrails, staging checklists, lightweight hosting strategy and internal link/navigation plan.
- `VERIFICATION.md`: executions, source hashes, blockers and QA handoffs.

## Local reproducibility
```bash
node --test tests.mjs
python render_door_film.py
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames -of json the-person-behind-the-door-40s.mp4
```
The renderer requires Python 3, Pillow and ffmpeg/ffprobe. Film renders as offline files; the MP4 itself remains in the offline review package (conversation attachment), **not** on GitHub or WordPress. Re-running the script requires no network, API tokens, external imagery or licensed media. Locally tested film: exactly 40s, 540×960, 12fps, 480 frames, silent original schematic sequence.

## Disclosure and consumer protection
- “If you eventually purchase through an approved link on this page, Final Vestige may earn a commission at no additional cost to you.” appears immediately adjacent to the still-disabled CTA.
- The merchant's twelve minutes = hour equivalence, automatic entrainment and sweeping mental/health results are clearly described as **seller claims**, **not** established product-specific results.
- The purchaser-data-sharing possibility, checkout mobile field and unverified exact refund procedures are presented cautiously. No prices, commission rates, personal use, guarantee enforcement or authorized URL are invented.
- Limitless Labs creatives/swipe are not evidence of permission to use Zen12 creatives; no email channel activated. The existing single Focus/Jetpack funnel stays unchanged.
- All 12 activation gates are FALSE. Written FV-specific Inspire3 approval, product link/rights, independent FTC/privacy/source checks, staging a11y/performance, media+captions, and explicit founder publication approval remain required.

## Source trail
Historical research https://doi.org/10.3758/BF03208840 , https://doi.org/10.3758/BF03214339 , https://doi.org/10.1111/j.1467-9280.1997.tb00427.x and https://doi.org/10.1016/j.tics.2004.11.006 .
Scientific consumer evidence https://doi.org/10.1371/journal.pone.0286023 and https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .
Exact seller catalog and pages https://inspire3.com/ , https://zen12.com/hnp , https://zen12.com/about , https://zen12.com/research , https://zen12.com/getstarted , https://inspire3.com/privacy/ ; complete terms https://inspire3.com/terms/ was inaccessible on 2 November 2026, therefore precise refund mechanics remain UNVERIFIED. FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

**Review, do not release.**

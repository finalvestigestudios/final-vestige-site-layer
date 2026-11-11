# Apollo R280 — reviewed-source byte custody (isolated staging, HARD HOLD)

Parent: R279 draft PR #2010, `7fab8e189adf3d13ee2f48974501907fdf4aa961`. Coordination: #150 / #820 / #818. **Never modify homepage PR #49 or Research Desk PR #158. No site or WordPress changes authorized.**

## Verified defect and change

The R279 shortcode checks three fixed source anchors and a pending-review marker in rendered HTML. These anchors can survive accidental (or unauthorized) modifications to the same file's editorial language. In controlled PHP negative tests, R279 accepted five altered siblings that kept those anchors intact, including a false statement of NASA endorsement, a false review-completion label, an unwarranted assertion of independent corroboration, a changed free-investigation CTA, and an injected `onclick` attribute.

R280 pins the **complete, exact reviewed sibling renderer file** `experience2/apollo-r273/review-custody.php` to SHA-256 `3f3c5a01e64cbc68349dd20c3daceadb64bf8a2e68ec5a0a2ea4bb6a3eed9107` (Git blob `48dfb8b92323379342a9609b64b5ff25adabb6f5`). If the file is missing, partial, changed, or unreadable, the adapter returns the existing static NASA Report + free-investigation fallback rather than rendering otherwise credible-looking but unreviewed text. Valid, unmodified source continues to render normally. This is a *staging release integrity control*, **not** malicious-PHP sandboxing, editorial approval, a media licence, or permission to deploy. Updating the sibling legitimately requires a new reviewed hash and QA.

Primary source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Board judged an electrical arc the most probable initiator, not conclusively identifying a single ignition source.

Rights boundary: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . NASA historical documents and hyperlinks are not evidence of commercial endorsement or blanket rights clearance for agency marks or astronaut likenesses. No new media or products introduced.

## Reproduce QA

```bash
php -l experience2/apollo-r277/apollo-review-shortcode.php
python experience2/apollo-r280/qa/source_pin_gate.py /tmp/fv-r280-qa
python experience2/apollo-r279/qa/renderer_custody_gate.py /tmp/fv-r279-regression
```

`source_pin_gate.py` reconstructs the **exact R279 parent adapter** from the new staging patch and checks its Git blob SHA before running old-version negative controls. The expanded local QA ran 11/11 actual PHP sibling cases and 50/50 Chromium cases across 320, 390, 768, 1440 and 1920 px, JavaScript on/off, native keyboard disclosures, print-source visibility, touch and reduced motion; 2 independent runs reproduced identical receipt and screenshot checksums. The parent adapter demonstrably accepted 5 unreviewed textual/attribute changes; R280 correctly served static fallback for all 10 modified/missing candidates. Source-controlled exact-gate execution and its receipt are included in the evidence bundle.

**Not established:** installed WordPress/Assembler QA, true browser HTTP/CSP (local server blocked by administrator in prior sprint), genuine axe-core, NVDA/VoiceOver, browser UI zoom, field LCP/CLS, actual Grok asset attribution, payable Mini Museum eligibility, merchant-confirmed paid orders, refunds/fees, commercial conversion uplift, independent approval, hosted CI. Do not claim offline Chromium measurements as production CWV. This PR is **HARD HOLD**, draft only.

## Conversion-first contract

Candidate creator-led route: *verified published Grok Apollo video with `asset_id` and approved UTMs* → existing public Apollo Atlas → **free original Apollo investigation** (one in-context CTA) → separate, optional disclosed Mini Museum buying guide only after affiliate acceptance and founder approval → merchant-confirmed paid order, fees/refunds and realized net revenue. Grok owns scripts and posting; Praxxis reviews creator assets; Claude owns commerce/analytics and release engineering; founder owns spending and launch approval. **No direct commerce inserted into the historical evidence panel, no new tracking scripts, no live changes.** 7/30-day net revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE** without authenticated order and session records.

# R17 — Distinct first edition, primary experiment and live photographic field manual

**2026-10-31 — REVIEW ONLY. MASTER PR #175 / Issue #174; companion Mind Issue #171.**

## Identified editorial problem
The initial 01 and 02 drafts relied on the same Puységur account and sent readers to the **same** live Puységur page in consecutive weeks. That is weak differentiation for an evidence-first publication asking historical readers to consider a new Mind & Perception stream. It also made the first issue an introduction *about* perception, instead of an original lesson *from* a concrete experiment.

## Surgical change — first edition only
The first edition now starts with **Simons & Levin's 1998 real-world change-blindness field experiment**, distinguishes observed detection under experimental conditions from general claims about witness reliability, then turns to a fully verified existing Final Vestige asset: **The Missing Caption**, WordPress published page **1122**. This independent photographic-research field guide asks readers to distinguish image, object, catalog and neighboring records. The Issue 02 Puységur historical narrative and CTA remain intact. Subject, newsletter tone and six-issue 4:2 allocation stay intact; preheader is refreshed for the new story.

Source-of-truth links (checked October 31, 2026):
- Peer-reviewed original experiment, **Simons & Levin (1998)**, DOI https://doi.org/10.3758/BF03208840 ; publisher abstract says **only half** in the first pedestrian swap experiment detected a change, and cautions results depend on context/social group.
- Verified WordPress published **The Missing Caption** https://finalvestige.com/the-missing-caption/ (page 1122), with actual four-record image methodology.
- Peer-reviewed Puységur historical analysis (still uniquely used in 02): https://pubmed.ncbi.nlm.nih.gov/31273811/
- Legal email rule: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Official product claim context (not cited in editorial 01): https://zen12.com/about and https://hypnosislive.com/mental-skills/total-focus . Neither provides Final Vestige email-affiliate rights.

## Copy-conversion QA
This update replaces repetitive warm-up with a clear scene, one genuinely original and bounded research finding, a three-step takeaway, and **one primary onsite CTA** to a live photographic evidence manual. The peer-reviewed DOI is an evidence reference, **not** a second offer CTA. This increases theme continuity without a premature `/mind/` or merchant URL. No claim is made that research proves a product, that the experiment applies to all people, or that any Final Vestige reader has used a product.

## Delivery truth
The current authenticated Jetpack site has newsletters ON; `email_new_posts_by_default=false`; `email_content_format=excerpt`; `recent_sends=[]`; welcome message configured for a 52-page Fieldbook. **The generated HTML/text previews are only offline editorial previews**. WordPress will not necessarily send the full body or planned preheader. No WordPress post/preview/test email has been created or delivered. No postal address/unsubscribe proof exists. Total=2, confirmed=2, unconfirmed=2 are **not inherently contradictory** because WordPress excludes pending confirmations from overall total; email-eligible reachability is UNKNOWN. The manifest's stale contradictory-count phrase is removed.

## Required human release checks (all outstanding)
1. Founder final creative, audience, recipient, mode and schedule approval; no implied approval from this PR.
2. Actual opted-in email recipient category verification without exporting addresses.
3. Final Vestige physical address, sender fields and functioning opt-out on genuine received Jetpack MIME, plus excerpt/subject rendering.
4. For 03 and 05 only: reviewed published guide destinations and account-specific Inspire3/Zen12/Total Focus product/email rights and approved link format; current price, refund, audio and video representations independently checked.
5. Hosted Actions `local-content-safety` was failing on PR #280 (run 41189681092, no job-step logs); do not declare CI green because local tests pass.

## Local reproducibility
`python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`

`node dispatch/campaign-2026-mind/tools/build_previews.cjs --check`

No sends, CMS writes, subscriber changes, tracking activation, new email platform, merchant contact, or homepage PR #49 changes.

# R90 — Apollo 1 evidence-first editorial alternative (NOV 3 2026; NOT APPROVED)
Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · Merchant companion [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · Master [Draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · First release-gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) · Parent [R89 #775](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/775).

## Why this is substantive
Original Issue 04's subject “Fourteen seconds. A much longer explanation.” suggests an exact measured event pair without identifying which timestamps. NASA's published historical timeline describes **17 seconds between initial indication and last crew communication**, and the original Apollo 204 board report separately describes initial report, rupture, telemetry loss, and lethal-atmosphere *estimate*. Substituting “17 seconds” would still conflate those phases. R90 removes the numerical subject altogether.

Original Issue 04 was about 200 words; the new optional alternate contains an original narrative, evidence-vs-inference discrimination, six board-identified hazardous conditions, reason the hatch impeded egress, timeline caveats, a practical three-column safety investigation exercise, and one relevant live first-party CTA. Three official NASA source links appear in a separate citation section and are **not** sales CTAs.

## Source boundaries
- [1967 Apollo 204 Review Board report (NASA hosted transcript)](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — Board's specific findings and uncertainty; **preferred primary evidence**. Context: 100% O2 at 16.7psia, most-probable electrical arc, six conditions, five-minute hatch access, estimations.
- [NASA Safety's Apollo 1 summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) — hazard classification, 90-second hatch under ideal conditions, post-fire reform.
- [NASA GSFC historical timeline](https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo1info.html) — nuanced last-voice-transmission interval; cannot substitute arbitrary "14 seconds".

The HTML file is accessible offline **static email-style review**, not a Jetpack-rendered message. Actual Jetpack is configured **excerpt**, with no verified preheader control. The plaintext is draft content, **not** a received MIME part. Both retain physical-address and unsubscribe HARD STOP placeholders. No actual inbox preview is claimed.

## Conversion / sequence strategy
Issue #04 is deliberately the evidence-first "trust reset" between the two commercial-reserved issues #03 and #05, keeping the founder-approved 4:2 editorial-commercial **allocation**. It asks for exactly one editorial action: reading the live Apollo investigation. No affiliate link or recommendation. Other issues and original master are untouched. This proposed alternate is **not** an approved creative substitution.

## Current factual release blockers (connected WP at 12:37 UTC)
Jetpack on / site_can_send true; automatic new-post defaults OFF **but per-post sends are possible**; excerpt delivery; no-reply. Welcome 52-page Focus Fieldbook configured, actual receipt unknown. Subscriber counters total2/confirmed2/unconfirmed2, follower stats email0/wpcom2; actual eligible count UNKNOWN. Five recent posts marked never_sent_opted_out (not proof of lifetime zero sends). Dispatch/Focus commercial disclosure language differs, no updates approved. No qualifying Final Vestige postal address, received native Jetpack HTML+plain footer/unsubscribe, private list reconciliation or founder FINAL send/audience/timing approval. Commercial Issue 03/05 additional HOLD_MERCHANT: no named-account email promotion rights and no approved published buyer-guide destinations.

## QA
Native test file added under `dispatch/campaign-2026-mind/tests/test_r90_apollo_evidence.py`; GitHub Actions must independently run it on exact PR head before reporting a hosted pass. Python: `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`. Static HTML is accessible review only. No authoring/publication or email sends permitted.

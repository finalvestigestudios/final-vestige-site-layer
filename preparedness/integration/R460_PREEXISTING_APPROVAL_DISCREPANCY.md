# R460 safety-state discrepancy — PREEXISTING metadata, not qualified QD approval
Status: DRAFT / HARD HOLD. Preparedness Issue #136. This is a source-integrity finding, not medical, food, water-treatment or editorial approval.

Exact 2026-11-18 read of original R459 integrated GitHub metadata, parent SHA 9b4846d2b2a94f7aeee2689e9b738f94a9eab97a:

1. Article #6, making-water-safer, file preparedness/content/articles/making-water-safer.meta.json, Git blob 827d861eb3beebfd010ee98fcca764b23a2de90e: safety_review.state = approved, reviewer field records an unattributed founder chat reply, dated 2026-10-29. Critically the same existing scope field explicitly says this is NOT an independent safety, editorial or factual review, has no itemized checklist, approval scope unconfirmed, and QD has not occurred.
2. Article #21, salt-beef-salt-pork-age-of-sail, file preparedness/content/articles/salt-beef-salt-pork-age-of-sail.meta.json, Git blob 1c4c5396da703f3724b584c67e49e2128ab1f4c6: also safety_review.state = approved, with the same incomplete founder-chat provenance and explicit disclaimer that no independent review or QD occurred.

Both remain publish=draft. Exact 35 original article stable IDs 1–35 were inspected at the original frozen head; their number identities are distinct. Original tool IDs are not: 102 and 103 each occur twice. None of these findings alone establishes a duplicate public URL or a lost citation.

**Release decision:** DO NOT promote the historical approved string into QD PASS; it must be reconciled with the explicit scope before an allowed draft transport or release. R460 intentionally rejects a preexisting approved state as insufficient qualified safety proof. This does not erase a founder reply or imply the founder never reviewed anything; it preserves the documentary distinction between founder feedback and independently qualified safety adjudication. A human QD owner must record named reviewer, source set, reviewed passages, dates, explicit limitation and appropriate hazard-specific competency, with written founder release authorization where required.

Existing pending reviews include Article #15 family-communication-plan and original Tool #104 family-reunification-card. Their family, school, 911, communication and privacy claims remain withheld; Tool #102 ID ambiguity is separate. Leave every actual original metadata byte unchanged pending qualified reconciliation.

The current public https://finalvestige.com/preparedness/ describes free primary-agency resources and explicitly holds original hazardous guidance pending review. Do not link unpublished Article #15/Tool #104 as if live or infer a paid conversion.

Engineering execution: 56/56 new locally isolated synthetic Python tests PASS. Complete authenticated original native validation/build, 35 real article plus six tool exports, independent qualified QD and merchant proof NOT RUN/NOT APPROVED. No public, CMS, social, email, analytics, merchant or creator-task write.

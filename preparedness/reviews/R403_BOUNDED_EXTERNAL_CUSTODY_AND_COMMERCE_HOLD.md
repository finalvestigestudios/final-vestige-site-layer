# R403 — Original Article #11 custody: bounded reader and conversion HOLD

**Scope:** Preparedness Archive integration and citation/source safety only; Issues #136, #820 and business charter #818. DRAFT / HARD HOLD. No publication, CMS writes, navigation, checkout activation, new tracker, email, affiliate or creator posting.

## Security defect and repair

Parent R402 exact HEAD 06d6e201b83655e270ea668ad5b6c73742ea6114; source Git blob 3a665a768174672138dd61c014070db17d954389.

R402 used an unbounded local file read before applying its 32 MiB ZIP ceiling. An accidentally selected oversized/symlink/hardlinked path could consume memory before the post-read security gate rejected it. R403 introduces file-descriptor O_NOFOLLOW, single-link regular-file enforcement, metadata and size validation before bounded read, then before/after identity/length verification. Existing archive and HTML SHA-256 pins and in-memory ZIP checks remain unchanged. No file extraction or writing. No claim that synthetic evidence establishes food safety.

Editorial E396 independently reported an original-byte successful E395 R402 replay in its **separate** environment. Editorial expressly says its original ZIP and nested E396 handoff have NOT reached Integration. Receiver-side genuine ZIP validation is therefore NOT DONE. Expected E395 ZIP SHA-256 21a2142c6050eb3bae020c67744ee82439d854525ba63915ea9092a0b7bba46b; article HTML SHA-256 bc0537e611d35b195e10ee49ceb9772a904b7c8fea0749a6203da38e835f8184. Even a real matched pair returns exit 2, DRAFT_HARD_HOLD, and does not approve household jerky processing.

## Original evidence and independent QA

Preserve the seven Claude original contributor branches and two Shelter successors; 35 article identities, 203 original source IDs, 280 occurrences, 17 shared-URL review groups, five original source-scope disputes and nine unselected Shelter forks. Additional Article #11 NCHFP/UMN/FSIS conditions await human specialist review. Do not choose variants or collapse distinct reading scopes. QA #157, fixture #169, dependent fix #2205 and homepage lead #1689 remain untouched and unmerged.

## A single high-intent Preparedness acquisition path (draft only)

Audience: household family emergency communication and reunification planning. The already-public https://finalvestige.com/preparedness/ contains a free, source-linked "Create a household emergency plan" entry pointing to a Ready.gov emergency checklist. This is an external official resource link, NOT publication/approval of FV's held Article #15 or private Tool #104.

Unactivated free CTA: "Start With Trusted Preparedness Resources" → https://finalvestige.com/preparedness/. Nothing essential is email-gated or behind payment. Optional Tool #104 stays PRIVATE pending child privacy, reunification guidance, accessibility, print and emergency source reviews. Do not resurrect retired water freebies. Grok/Praxxis TASK-008 must independently establish a genuine already-published family-contact asset ID, creator link and mobile destination; no ID is verified and no production assignment is authorized.

## Offer → funnel → blocker → experiment → evidence → owner

| Offer | Funnel step | Blocker | Next experiment/evidence | Owner |
|---|---|---|---|---|
| Existing FV Preparedness paid pack (none authenticated) | Paid checkout and delivery | No verified rights-cleared payable, deliverable SKU, refund and fee terms | Founder/Commerce independently verifies merchant listing, rights, checkout, delivery, settlement before paid CTA. HOLD | Founder / Commerce |
| Free official-linked Archive | Actual Grok family-contact asset → qualified landing → free agency guide | Genuine asset ID, right to link and 360/390px route not verified | TASK-008 authentic asset inventory, signed-out mobile CTA and source-link checks. UNVERIFIED | Grok / Praxxis / Site QA |
| Private Tool #104 | Free guide → optional printable | Child privacy, emergency and accessibility signoff missing | Qualified privacy/subject reviews, offline no-JS print and screen reader acceptance. HARD HOLD | Preparedness / QD |
| Merchant-confirmed sale | 7/30-day campaign cohort → real order → fees/refunds → net | No qualified-human attribution, merchant receipts, fees/refunds | Reuse consent-safe #820 event spec; clicks, affiliate outbounds, checkout starts and signups are not sales. Net revenue per 1,000 qualified humans NOT COMPUTABLE | Claude / Commerce |

## Execution boundaries

Local R403 adversarial tests cover normal bounded files, missing files, directories, symlinks/hardlinks, empty and sparse oversized files, bounded limit, terminal exit 2, SHA hold and 35 hostile member names. Run native validate.py and build.py on an authenticated full original checkout and replay genuine private exports before recommending release. The full checkout and real original ZIP are unavailable in this integration runner. Tests of synthetic fixtures prove only program behavior, never Article #11 content correctness or independent qualified safety/QD approval.

All approval flags remain false. No merge or public/CMS/site, social, email, analytics, affiliate, merchant or spending action is authorized or performed.

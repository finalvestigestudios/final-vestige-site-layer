# R329 — Article 15 and Tool 104 source-preserving redline candidate gate

STATUS: DRAFT / HARD HOLD / NO RELEASE. Scope is Preparedness Archive issue #136, revenue acceptance issue #820 and charter #818. Nothing is merged, published, activated or sent.

The R328 witness gate pinned ten unresolved child privacy, reunification, emergency scope and texting claims. R329 adds a READ-ONLY review-candidate pathway: editors may prepare a correction in a physically separate tree and compare it with the original source without mutating the 35-article / six-tool source corpus.

Original Git blobs, authenticated on current integrated R328:
- Article #15 HTML: 8ac8bd7dba3be15d477c15737e54d83364d72527
- Article #15 metadata: dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3
- Tool #104 HTML: be8698ac5d020476ff649d85813810e2000c6f98
- Tool #104 metadata: 47da1e7e20e39f0ea85e26d54a8d58301f6e0a15

New candidate checks:
1. Original four source files must retain exact Git blob identity. Candidate tree must be separate and nonnested; no symlinked or missing source.
2. Protect manuscript numbers, slugs, section, track, tool kind, draft publication state, independent reviewer/date absence and pending safety state.
3. Preserve every cited source ID and at least its previous citation occurrence count, complete source-use declaration sets, internal link placeholders, explicit links, related resources, heading anchors and >=95% of visible reading depth. This is not evidence that citations support claims.
4. Hold changes to form submission, named form fields, event handlers, scripts, style rules, network-bearing attributes, embeds or external scripts until separate browser/privacy QA.
5. Reject still-present known over-narrow emergency, generalized SMS and unverified local-storage/privacy claims. Removing problematic text is necessary but never sufficient for safety or source clearance.
6. Even if structure is unchanged and known redline phrases removed, the strongest result is REVIEW_REQUIRED_HARD_HOLD. INVALID_HARD_HOLD is the error result. ALL release and QD flags stay false.
7. No original bodies, metadata or CMS records are modified by this PR. Existing Tool #102 plan builder and Tool #104 wallet card remain separately identified.

New regression file: preparedness/tests/test_r329_candidate_redline_preservation_hold.py. Contains dozens of generated adversarial fixtures for citation deletion, identity collision, fictional approvals, truncation, external scripts, malicious form actions, child-data fields, privacy promises and false release. Full exact-commit native test/build and authentic 41 WordPress + 41 preview HTML exports remain NOT VERIFIED; independent safety/privacy/QD review remains NOT APPROVED. Do not interpret a synthetic green test as approval. #157 and #169 are open independent drafts; #2205 is an unmerged separate remediation for the fixture source-write issue.

Use on a trusted fully authenticated repo checkout:
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/r329_candidate_redline_preservation_hold.py --root . --candidate-root /outside/review-candidate

OFFER -> STEP -> BLOCKER -> CHANGE/EXPERIMENT -> OWNER / EVIDENCE
- Existing official-source free Preparedness Archive -> Grok organic asset landing -> asset_id, exact permitted mobile link and published intent not verified -> research-only TASK-008 link acceptance -> Grok/Praxxis; NOT VERIFIED.
- Archive -> original Article #15 -> ten emergency, child/privacy claims unresolved -> qualified line-level review + source support -> Preparedness/QD; HARD HOLD.
- Article #15 -> optional free wallet card #104 -> form/printing/no-JS/child privacy and safety unresolved -> separate browser tests -> Preparedness/QD; HARD HOLD.
- Guide -> one FV-owned rights-cleared paid practical product -> no merchant-verified, appropriate purchasable/deliverable SKU -> audit seller, rights, checkout, refunds before CTA -> Founder/Commerce; NO APPROVED SKU.
- Human sessions -> paid order less fees/refunds -> no verified merchant orders or 7/30-day attribution -> independent payment reconciliation -> Claude/Commerce; NET REV PER 1,000 QUALIFIED HUMAN SESSIONS NOT COMPUTABLE.

No retired water freebie, new offer, affiliate activation, social post, campaign link deployment, email, analytics installation, navigation edit, CMS write, publication, merge or spending. Founder release approval remains mandatory.

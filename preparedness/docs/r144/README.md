# Preparedness R144 — bounded QA #157 correction intake (Issue #136)

**Draft/HOLD; no merge, publication, WordPress, navigation, email, affiliate, merchant, or social actions.**
Parent: R143 draft PR #1090, head \`a1dcbf98aec0f1ae07f83f590896603a995e2e99\`.
Frozen 35-article candidate: \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\`. QA #157: \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`. **These are source evidence pins, not an instruction to reset live content.**

## Narrow engineering gain

PR #157's older \`three-day-kit\` version drops approximately 913 words and 11 citation occurrences if blindly overlaid on the current richer candidate. The candidate now has a significant prescriber/pharmacist warning, competing FEMA medicine-guidance wordings, and additional references. PR #157's proposed language still deserves *qualified* review, not an automated full-file replacement. The candidate's household-plan breaker warning is already present. The best safe path is a **single-paragraph or list-item correction only if a qualified reviewer finds one needed**.

\`preparedness/tools/r144_surgical_source_preservation.py\` checks candidate changes **without writing any article**:
- Exact frozen Git blob identity for original article and metadata (CLI path); only \`three-day-kit\`/medicine or \`household-emergency-plan\`/practice.
- Original status must remain \`draft\` and human safety-review state \`pending\`.
- Exactly **one** \`<p>\` or \`<li>\` element changes in the proper heading; all other HTML bytes must remain identical.
- All author-scoped citation tokens remain in their exact global and changed-element order and count.
- Existing hazard-caution passages remain present; edited paragraph cannot be blank, less than half its prior word length, inject active markup, hidden elements, links, buttons or scripts.
- Deterministic report identifies proposed diff, original/candidate Git blobs, citation occurrences, section, and remaining review approvals. The output **never** grants editorial/medical safety, QD, publication or a merge.
- This is a *structural* guard only: it does **not** prove that changed medical language is clinically sound, that claims are supported by the citations, or that a link remains current. Specialist adjudication and independent source QA are required.

### Trusted checkout usage

\`\`\`sh
python -I preparedness/tools/r144_surgical_source_preservation.py \
  --slug three-day-kit \
  --baseline /trusted-frozen-RC/preparedness/content/articles/three-day-kit.body.html \
  --metadata /trusted-frozen-RC/preparedness/content/articles/three-day-kit.meta.json \
  --candidate /review-only/proposed-three-day-kit.body.html
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
\`\`\`

The CLI returns a JSON **DRAFT_HOLD** report and exit 0 only for structurally bounded edits; this **does not authorize the edit or release**. Any integrity mismatch returns exit 2 with QD NOT_APPROVED. Do not point it at mutable contributor heads without checking provenance or treat a successful validation as clinical approval.

Local isolated R144 tests: **92/92 Python unittest PASS**; \`python -I -m py_compile\` PASS. Those are synthetic fixtures; **full authentic R133–R144, native validate/build, full tests and independent browser/QD remain NOT EXECUTED** in the no-checkout runtime. GitHub-hosted CI has repeatedly failed before runner execution; don't consume Actions budget for reruns without a runner fix.

## Remaining cross-lane holds

- Preserve the 35 full-length articles, ~2,000 frozen citation occurrences, 32 unresolved shared-source groups and all safety/release states. R140–R143 discovered real citation and depth regressions; do not replay old branches or #157 wholesale.
- Seven contributor branches are independent; last exact pins (verify again before future integration): Start \`2122d856\`, Shelter \`5daeaf2d\`, Food \`f911ff7a\`, Health \`d5ef5baf\`, Historical Food \`67e116e5\`, Historical Home \`7504a5f0\`, Historical Field \`4e5caf81\`. Food divergence and eight jerky citation-ID retargets need human adjudication.
- Independent food fixture PR #169 \`e9cd7766\` has a remaining shared-directory write; separate draft #973 \`4d40996a\` isolates it. Neither is merged.
- Homepage #49 \`10495883\` / #604 \`bdf01b4a\` belong to other owners. Don't edit those.
- This PR adds **no** article rewrite, taxonomy/route/source changes, safety clearance or CMS code.

## One Preparedness conversion funnel (not a launch)

**Verified intent hypothesis:** parent/caregiver who needs a school-pickup and family-reunification plan.
**Proposed editorial destination:** existing *Household Emergency Plan* (unpublished instructional DRAFT/HOLD); optional existing family-reunification printable (download/mobile/printing QA still unverified).
**Paid offer gate:** no authenticated FV-owned, rights-cleared, **currently purchasable** matching Preparedness SKU, Payhip price, delivery, refund or confirmed merchant order. Therefore **NO paid CTA, merchant link, price, asserted sales or launch**. Third-party Payhip listings are not FV inventory. Grok's actual Preparedness asset ID and published platform URL remain NULL in TASK-008; no new content assignment.

Draft copy for review **only after the free guide is approved and published**: *“Make a household meeting-and-pickup plan you can actually practice. Read the sourced Household Emergency Plan; use the optional printable to record contacts and reunification steps.”* Do not require signup/payment for core safety guidance; secure any completed contact sheets locally.

**OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → PASS/FAIL EVIDENCE → OWNER:**
1. FV-owned Paid Preparedness Pack → order: SKU/rights/fulfillment/return status not verified → commerce audit first, not a speculative product → **FAIL/HOLD** → founder/Commerce/Claude.
2. Free Household Emergency Plan → guide visit: medical/source/QD HOLD → qualified review and complete native validation → **BUILT DRAFT, NOT RELEASED** → Preparedness/independent QA.
3. Guide → optional printable: mobile 360/390, keyboard, privacy, print, source citations and delivery untested → stage end-to-end → **NOT TESTED** → Site QA.
4. Grok social → guide: true asset ID, post URL, destination and UTM missing → reconcile existing TASK-008 with Praxxis and Grok before any creator posting/link edit → **UNVERIFIED** → Grok/Praxxis.
5. Qualified sessions → confirmed lead → paid order → refunds/fees → net revenue/1,000 qualified sessions (7/30d): source-of-truth reconciliation absent → count no purchase from click/checkout/Jetpack views → **NOT COMPUTABLE** → Claude analytics/Commerce.

No duplicate measurement tags, new email workflow, paid services, retired water freebie, advertising or fake scarcity.
Cross-references: #136 (custody/release), #820 (attribution), #818 (business charter).

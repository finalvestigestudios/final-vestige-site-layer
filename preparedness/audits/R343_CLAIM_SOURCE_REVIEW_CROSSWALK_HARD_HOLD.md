# R343 — source-to-claim review crosswalk (DRAFT / HARD HOLD)

**Ownership:** Preparedness Archive integration/citation safety, Issue #136. Commercial coordination #820; business charter #818. No publication or release request.

## Engineering intent

R336/R337 pin the entire 35-article, six-tool original corpus and measure total citation occurrences, while R338–R340 protect link topology and rendered exports. **A citation token next to a paragraph does not by itself prove that the cited page supports each assertion in that paragraph.** R343 produces deterministic human-review tickets, one per citation occurrence, with its source ID, section heading, HTML line, block ordinal, short text excerpt, SHA-256 of full normalized text, hash of the metadata source-use explanation, and non-authoritative risk hints. It flags tokens in comments/attributes/scripts/outside claim-bearing blocks, missing metadata source-use declarations, missing native source IDs and invalid draft state. Every ticket remains UNREVIEWED_REQUIRED. A source-register verified_on is not qualified emergency approval, a human link check, or claim support.

The read-only native CLI requires R337's authentic five measured source-witness parts and the original 41 Git-pinned body/metadata pairs before inspecting the corpus. If those are missing or changed it fails closed; it cannot generate a misleading release PASS. Invoke with:

    python -I preparedness/tools/r343_native_claim_review_run.py --repo-root .

The optional --output must point outside the repository. The CLI does not alter source files, CMS, navigation, analytics, social queue, email, product listings or merchants. Risk-hint pattern matches are not editorial verdicts.

## Verification / classifications (2026-11-13 PT)

- R343 **71 new** local Python unit tests (67 claim/source cases + four isolated -I CLI cases) PASS; combined local reconstructed R331–R343 test assembly **1,330/1,330 PASS** with Python compilation. The new committed R343 tests and CLI entrypoint were byte-matched locally; the primary locally exercised module was functionally equivalent but contains comment/docstring differences from the committed module, so **byte-identical execution of that committed module has NOT been established.**
- The missing-native-checkout control returned INVALID_HARD_HOLD, no citation review tickets, no false QD approval or source claim verification.
- Full authenticated native validate.py, build.py, 50 WordPress + 50 private preview outputs were NOT RUN (GitHub DNS prevents the complete local checkout); no hosted CI / qualified safety, privacy, QD / human link and claim review is asserted.
- Seven frozen Claude cluster refs and both Shelter descendants rechecked against exact SHAs (each GitHub compare: identical, 0 ahead / 0 behind). Homepage lead #1689 f55c36b6598eec558dd8bb24e4c8988becc51be0 untouched.
- Independent QA #157 7d1ae6b8ef93d10cfb6810987672360885e9c1aa, QA fixture #169 e9cd7766dac59d47ab467d8945269b9146c2aef5, dependent #2205 bbcf1859768624c611df4abadc564c18247cf32a all remain open/draft/unmerged; #169 still contains a canonical-source write of _dup_test.json. No cherry-pick, merge or publication.
- Original **15 editorial integration conflicts and 17 Article #15 / Tool #104 safety/child-privacy obligations** are outstanding. Additional animal access / local jurisdiction questions remain subject to qualified review. Tool #102 and #104 are separate private draft tools. No QD PASS.

## Conversion-first decision, held

One tentative high-intent audience: people seeking family emergency contacts/reunification. Candidate public free official-source Archive: https://finalvestige.com/preparedness/ . Existing detailed Article #15 and Tool #104 remain private; no unapproved tool CTA. Grok/Praxxis must independently verify an already-published genuinely intent-matched original asset ID, date, platform-allowed mobile destination and campaign tagging; none was authenticated here. Do not reuse unrelated videos.

No verified FV-owned, rights-cleared, genuinely payable and deliverable Preparedness SKU or order evidence, so **no paid CTA**. Keep the offer/friction matrix: existing pack [unverified] → relevant article/guide [held] → optional practical tool [held] → qualified-human campaign session [unattributed] → consented confirmed lead [unverified] → settled merchant order [unverified] → fees/refunds [unverified] → realized net revenue per 1,000 qualified sessions [not computable]. Use 7/30-day cohorts and tiny-sample warnings if valid data later exist. Founder approves commercial activation and release; Grok owns production/posts; Praxxis social QA; Claude core website/analytics.

**Disposition:** isolated draft branch, unmerged, HARD HOLD. No paid services, WordPress/CMS/nav changes, source edits, public publishing, social posts, marketing emails, analytics scripts, merchant/affiliate activation, spending or fabricated performance numbers.

# Preparedness Archive — hash-bound review requests (UNPUBLISHED)

**Issue:** [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136). **Parent draft:** [PR #193](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/193). This is a source/citation safety **review handoff**, not a content edit, expert review, medical endorsement, or WordPress release.

## Why this exists

The existing `source_review_queue.py` inventories **36 draft items (35 long-form articles plus the water planner), 367 article-source pairs, 224 physical source rows, 186 literal URLs and 30 unresolved shared-URL groups**. A shared URL can represent different contributors reading different passages. A copied source link cannot certify a claim in another contributor's work. The old queue makes that distinction visible; this new layer produces **fingerprint-bound, human-readable review requests** without altering any source or article.

## Use from the exact private repository checkout

Run existing gates first; none asserts that the external source is human checked:

```sh
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/source_review_queue.py --output preparedness/build/source-review-queue.json
python -I preparedness/tools/review_receipts.py --out-dir preparedness/build/source-review
```

The last command writes **only** `preparedness/build/source-review/review-requests.json` and `citation-review.csv`. Review receipts include the exact article + source reading-scope SHA-256 as established by `evidence_freeze.fingerprint`, the exact review queue digest, separate source-row keys, article-specific support notes, contributor reading limits, a review-request digest, and a separate packet for **every shared URL**, including its uncited contributor rows.

The CSV is spreadsheet-formula sanitized and retains full claim text; the JSON is stable and machine comparable. It carries no reviewer identities or automatic approvals, and all requests are explicitly `PENDING_HUMAN`. The export path is constrained to the **build** directory; input files and the live website are never written.

### Reviewer workflow

1. For each shared URL, open the primary source as it currently exists and record URL, redirects, document/version/date, actually examined portions, and any missing/disputed text.
2. Compare contributor reading scopes side-by-side. **Do not merge**, assume one contributor's source check validates another's claim, or discard uncited rows simply to reduce the conflict count.
3. For each article-source row, inspect the original supporting passage and separately check whether the **article's specific factual assertion** is warranted. Preserve uncertainty and document contradictory official instructions without silently choosing one.
4. Escalate water treatment, food preservation, refrigerated medicines, infant feeding/medication, carbon monoxide, generator operation, fire and evacuation instructions to qualified human safety review. Historical-source credibility does not prove a historical method is safe to try.
5. Recompute the packets on the final exact commit; if `review_request_sha256` changes, **invalidate prior review conclusions** and reread that claim/section. This export doesn't accept or persist reviewer approvals, and a forged SHA is not independent attestation.
6. Independent editorial/security/QD evidence, actual human link checks and founder publication approval remain mandatory. **Never import a CSV into the WordPress editor as a publish directive.**

### Safety failure modes tested

The additional 44 synthetic tests cover deterministic digests; altered queue/content fingerprints; source/citation count loss; duplicated row identities; sharing rows across contributor origins; incorrect group membership; blank/missing article and contributor reading scopes; illicit published status; human flags that do **not** imply approval; malicious CSV formulas; output path traversal and symlink redirection. They reuse the unchanged, byte-verified PR #193 `source_review_queue.py` module and its 18 original synthetic tests. **62/62 local Python tests passed on these exact four blob bytes** in the isolated test fixture. This is **not** an execution of the entire 35-article corpus, native `validate.py` / `build.py`, the other 118 existing Python tests, external URL checks or WordPress render.

### Independent QA reconciliation and branch ownership, October 30, 2026

- **PR #157:** `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; inspected Start Here safety patch. The integrated head already contains the no-main-breaker rehearsal warning, refrigerated-medication cautions, article gates and nonprofit Red Cross source classification. Do not cherry-pick over the current revisions.
- **PR #169:** `e9cd7766dac59d47ab467d8945269b9146c2aef5`; inspected food cluster synthetic-fixture patch. The integrated `test_preparedness.py` already contains isolated temporary-copy tests instead of writing into the real source fragment directory. Do not regress these safeguards.
- Contributor source branches (checked): `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`; `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; `claude/prep-food-ccdc55` `4b009361277ea1d4617b368f5d45104c7318b284`; `claude/prep-health-837444` `d2212d0ca0750817d3929865d3069835980faf20`; `claude/prep-hist-food-b81f19` `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`; `claude/prep-hist-home-0e0e38` `f654e600f89c321a480dd8f055be4d13d0673490`; `claude/prep-hist-field-9db767` `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.
- Homepage lead frozen PR #49 head `10495883299d53596992c26a8987f629b2904670` checked; no homepage, navigation, WordPress, production or marketing changes.

## Release blockers remain

**HOLD.** The prior integration lists 0/224 documented human link checks, 30 unresolved shared-URL scopes, 30 safety-pending draft items, and no independent clinical/food/water/CO/infant/medication qualified review. Hosted GitHub Actions CI has not demonstrated green exact-SHA results. The full local repository is not accessible to the test container (private GitHub DNS unavailable), so native article build, full 180-test discovery, browser screen-reader QA and final published-URL verification are not claimed. Even a later clean structural test does **not** waive independent QD or explicit authorization for content publication.

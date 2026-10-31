# R25 — Citation-to-source claim review packets · Issue #136

**Review status: DRAFT / RELEASE HOLD.** No WordPress CMS writes, public pages, sitewide navigation, safety approvals, or changes to the original 35 article bodies/metadata, water planner, taxonomy, source records, or contributor research.

## Independent facts checked 2026-10-31

The seven original Claude branches were compared against their pinned author commits (GitHub compare API, ahead=0, behind=0 for each): start `2122d856fce9f64887c16df3d52e64be9f59a55b`, shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, food `4b009361277ea1d4617b368f5d45104c7318b284`, health `d2212d0ca0750817d3929865d3069835980faf20`, historical food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`, historical home `f654e600f89c321a480dd8f055be4d13d0673490`, historical field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.

Independent safety QA PR #157 remains draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; it uses older article bodies and must not overwrite the newer integrated household-drill or medication wording. Synthetic-fixture PR #169 is draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; the food author's real SHA remains `4b009361277ea1d4617b368f5d45104c7318b284`. Separate homepage PR #49 is `10495883299d53596992c26a8987f629b2904670` and #254 is `8fa6fc52e034f511b96ae526f4a852e1bd76db04`. No changes to these branches.

## New compulsory 13th private preflight stage

The original 12 machine gates remain in their existing order. After **frozen_81_file_archive_custody**, the new `citation_fallback_human_review_queue` independently enumerates **every** citation token and source binding in the preserved unpublished archive. It requires the pinned baseline totals — **35 articles + one water planning tool, 1,959 citation occurrences, 367 article–source relationships, 43 base-source fallbacks, and 30 shared-source URL groups** — rather than accepting a changed count or a duplicate URL silently.

Each review row contains the article slug, contributor origin, specific source ID and source origin, full original source `supports` and `notes`, article-specific `source_use`, *all* local citation contexts, exact citation count, URL and machine-verification date, explicit base-fallback/shared-URL flags, and literal **human reviewed = false** states. The packet's canonical SHA-256 fingerprint is reproducible. These are **human-review work items**, not fact-check results; their source statements have not been independently verified by this gate.

The previous 12-stage machine receipt verifier now requires the exact 13-stage order and refuses absent, duplicated, reordered, or falsely approved queue execution. `private_release_preflight.py` still validates a clean exact HEAD before and after each gate; the new script is a fixed local Python command with no network/CMS/write operations. Machine success always emits `release_state: HOLD`, `may_publish: false`, `independent_QD_approval: false`.

## Verification

Local synthetic/adversarial R25 test suite: **63/63 passed**, including 50 explicit evidence-mutation tests. Locally reconstructed R15–R25 available tests (updated pipeline and receipt contract): **782 discovered; 780 passed, two explicitly skipped** for absent trusted checkout, zero failures. One older outbound-link test module was **excluded** from that reconstructed collection because its production implementation was not included in the downloaded prior engineering packages; the outcome is NOT a complete native repository suite pass. The committed R25 Python/test Git blobs were independently checked against the exactly locally tested bytes.

The environment still cannot resolve GitHub hosts from its container, and the complete private Git checkout is not mounted. Actual R25 corpus invocation exits 2 on missing taxonomy, and native validation/build cannot start because their original files are absent locally. This is a **hard HOLD**, not an implementation pass for the actual 35-article corpus. Prior GitHub Actions runs have failed before runner dispatch; no hosted R25 job success is asserted.

## Trusted-checkout commands / remaining human work

```bash
python -I -B preparedness/tools/validate.py
python -I -B preparedness/tools/build.py
python -I -B -m unittest discover -s preparedness/tests -v
python -I -B preparedness/tools/citation_fallback_review_gate.py --repo-root .
python -I -B preparedness/tools/private_release_preflight.py --repo-root . --expected-sha <EXACT_CURRENT_HEAD>
```

The new queue is intended to guide independent review of **43 fallback bindings and all 30 shared-URL groups**, followed by review of 1,959 concrete claim occurrences, qualified assessment of consequential emergency/medical/food/water guidance, source provenance reconciliation, hosted CI, and independent QD decision. No links were re-fetched for factual agreement and no human safety review was performed. **Never publish based on this packet or its fingerprint.**

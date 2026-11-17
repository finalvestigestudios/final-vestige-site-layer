# R420 independent native master execution — 2026-11-17

**Exact master:** [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647` (reconfirmed still HEAD this run). **Do not confuse with R419's newer extra Python test or GitHub Actions.**

Container executed `git hash-object` over the original eight source/test files recovered from the previously retained R414 canonical archive. All **8/8 source SHA-1 blob hashes** matched the HEAD verified by the authenticated GitHub connector:

```text
86df98ad8a84e583ff5df64ddbf8c0eaa1335b00  dispatch/campaign-2026-mind/manifest.json
fd7f05e30092a7ec82090993dc5d7d0e23755c8e  dispatch/campaign-2026-mind/tests/test_campaign.py
039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8  dispatch/campaign-2026-mind/issues/01-the-mind-is-not-a-camera.md
faa207ab7deafd86460d36f8c17fe62d392d0e14  dispatch/campaign-2026-mind/issues/02-before-hypnosis-had-a-name.md
aeeef34efea0cc281f69901488e4501fea851245  dispatch/campaign-2026-mind/issues/03-the-twelve-minute-question.md
89635bfb9c8d1ff17297a59b6b5b5b2a176934ca  dispatch/campaign-2026-mind/issues/04-the-hatch-and-the-spark.md
a9dfaa450ba025a7b5113ade8a294d6dbad778dc  dispatch/campaign-2026-mind/issues/05-before-you-press-play.md
004d558df6376d2ad6f4f79a4581e8d2c444e355  dispatch/campaign-2026-mind/issues/06-the-evidence-log.md
```

Executed on Python 3.13.5:

```sh
python -m unittest discover -s campaign-2026-mind/tests -p test_campaign.py -v
```

**6/6 native tests PASSED, 0 failures, exit code 0**: six unscheduled issues, 4/2 mix, no approved affiliate URLs, near-offer disclosures, placeholder postal/unsubscribe gates, blocked dangerous promises.

R420's **separate** committed JS parity engine was re-fetched from GitHub at blob `f3ffc6cdf55a97782f00d3e9f14205c0940efd2b` and run under V8 against original canonical content plus R419 HTML/TXT files: **141/141 source assertions passed**. Fourteen injected authoring mutations were caught **14/14**. Its source checks are more thorough than the original Python suite but **NOT native Jetpack Preview, inbox/MIME render, email eligibility or live legal/merchant authorization**.

**Important exclusion:** The newly authored `dispatch/r419/test_exact_cta_preview.py` from PR #2848 has not been natively executed against all exact R419 files in this run; R420 exercised equivalent and additional invariants with its separate 141-point V8 source gate. Do not claim the R419 Python suite or WordPress email transport has passed.

Neither the master Python pass nor source-parity pass clears any founder, compliance or commercial hold. **ALL SIX HOLD_UNSENT; issues 03/05 HOLD_MERCHANT, original 04 HOLD_COPY.** No email/test email, WP write, subscriber contact, paid offer activation, spending or merge.

# R237 current-run native recheck of ORIGINAL #175 master Python suite — 2026-11-09

**Execution occurred in actual Python 3.13.5** in the isolated working container, using the R236 evidence ZIP whose original master files were already matched against the PR #175 GitHub source. This R237 run independently recomputed the Git blob SHA-1 for every file and executed **the unchanged native** `tests/test_campaign.py` with:

`python -I -m unittest discover -s original_175_exact/tests -p test_campaign.py -v`

**Result: 6 tests passed, 0 errors, 0 failures (0.002s), exit code 0**.
- `test_commercial_copy_has_disclosure` OK
- `test_legal_gate_requires_footer_verification` OK
- `test_links_not_activated` OK
- `test_no_invented_commercial_promise` OK
- `test_primarily_editorial` OK
- `test_six_issues_not_scheduled` OK

**Original master blob identities reproduced in Python in THIS RUN**:
- issues/01-the-mind-is-not-a-camera.md `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`
- issues/02-before-hypnosis-had-a-name.md `faa207ab7deafd86460d36f8c17fe62d392d0e14`
- issues/03-the-twelve-minute-question.md `aeeef34efea0cc281f69901488e4501fea851245`
- issues/04-the-hatch-and-the-spark.md `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`
- issues/05-before-you-press-play.md `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`
- issues/06-the-evidence-log.md `004d558df6376d2ad6f4f79a4581e8d2c444e355`
- manifest.json `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`
- tests/test_campaign.py `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`

This verifies the current historical master #175 SHA (`d57ccdba3aee8f065e143e101c2945f4f3d01647`) test corpus by matching eight Git object identities and rerunning its Python suite. It is NOT a complete private Git repository checkout, an actual Jetpack test, recipient confirmation, website release, or commercial compliance approval. 4 editorial / 2 commercial master issues remain HOLD_UNSENT, with merchant 03/05 additional HARD_HOLD. New optional R237 issue 04 does NOT replace the master issue.

**Additional independent R237 draft-source testing:** committed V8 source mutation checks 27/27 (1 baseline + 26 unsafe variants rejected), documented in `R237_POSTCOMMIT_QA.md`; those are NOT native Node execution or received email QA. No send, WordPress write, list access, affiliate activation or spending.

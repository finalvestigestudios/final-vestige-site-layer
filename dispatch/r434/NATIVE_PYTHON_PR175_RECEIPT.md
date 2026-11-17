# R434 exact-source native Python acceptance receipt (2026-11-17 PT)

**Result: PASS, native Python 3.13.5, six of six tests, exit code 0.** The original source is from immutable [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`.

The seven manifest/issue files and the test source were independently read with the authenticated GitHub file API, reconstructed byte-for-byte into an isolated local test directory, and verified with Git's exact blob SHA-1 format `SHA1("blob " + byte_count + NUL + UTF8_bytes)`. All **8 of 8 Git blob identities matched** the GitHub-provided blob hashes before invoking native Python:

| Path | Expected = actual Git blob |
|--|--|
| `issues/01-the-mind-is-not-a-camera.md` | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| `issues/02-before-hypnosis-had-a-name.md` | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| `issues/03-the-twelve-minute-question.md` | `aeeef34efea0cc281f69901488e4501fea851245` |
| `issues/04-the-hatch-and-the-spark.md` | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| `issues/05-before-you-press-play.md` | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| `issues/06-the-evidence-log.md` | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |
| `manifest.json` | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| `tests/test_campaign.py` | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |

Command (from temporary reconstructed campaign root): `python -m unittest discover -s tests -v`.

Output (actual):
```
test_commercial_copy_has_disclosure ... ok
test_legal_gate_requires_footer_verification ... ok
test_links_not_activated ... ok
test_no_invented_commercial_promise ... ok
test_primarily_editorial ... ok
test_six_issues_not_scheduled ... ok
Ran 6 tests in 0.001s
OK
```

**Caveat:** This is not a full private-repository Git clone and does not test native Jetpack emails, real subscriber eligibility, deliverability, merchant rights, web checkout, GA4 instrumentation or net revenue. The R434 new JavaScript gate was separately executed in V8 against exact GitHub blobs (22/22 pass, including deliberate unsafe mutations) but **native Node execution remains outstanding**. Nothing was sent, published or activated. All six editions `HOLD_UNSENT` and alternatives unadopted.
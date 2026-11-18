# R448 — Native Python master campaign preflight: exact GitHub blobs

**Date:** 2026-11-18. **Scope:** read-only local execution, original master draft [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at exact current HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Coordination [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), safety [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), stacked baseline [#3000](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3000).

## Executed test, not a V8 reconstruction

1. Retrieved each of the six original Markdown issue files, original manifest.json, and test_campaign.py from the GitHub connector, pinned to master PR #175 current HEAD.
2. Reconstructed those files locally in their original relative paths, preserved exact UTF-8 bytes, and independently ran `git hash-object` for **all eight files**. Every calculated Git blob SHA exactly matches the GitHub-connected returned source blob SHA listed below.
3. From package root ran `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`. **Six tests ran; six passed; zero errors or failures; exit code 0.** This is real native Python execution of **byte-identical** files, not a JavaScript implementation of the assertions.

| File under dispatch/campaign-2026-mind/ | Verified Git blob SHA |
|---|---|
| tests/test_campaign.py | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |
| manifest.json | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| issues/01-the-mind-is-not-a-camera.md | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| issues/02-before-hypnosis-had-a-name.md | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| issues/03-the-twelve-minute-question.md | `aeeef34efea0cc281f69901488e4501fea851245` |
| issues/04-the-hatch-and-the-spark.md | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| issues/05-before-you-press-play.md | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| issues/06-the-evidence-log.md | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |

## What passed

- Exactly six UNSENT original issues and draft manifest; no schedule.
- Editorial/commercial allocation remains exactly 4:2.
- All merchant affiliate URLs are null; original issue subjects/preheaders match the manifest.
- Both commercial issues retain visible disclosure and inactive guide placeholder.
- All six retain their postal-address and unsubscribe **hard-stop** placeholders.
- Five known deceptive marketing phrase patterns are absent.

## What these six tests **do not** prove

They do not establish FTC compliance, external source validity, mobile mail-client rendering, real Jetpack Preview, postal address, a functional unsubscribe, user authorization to send, affiliate partner approval, merchant checkout status, subscriber consent transition, welcome delivery, qualified traffic, or a settled sale. `6/6 PASS` is **only source-level preflight**; it does not make the original drafts sendable. No upstream files were modified. All six remain `HOLD_UNSENT`.

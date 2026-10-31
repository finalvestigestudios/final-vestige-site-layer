# FV Focus Popup — independent artifact identity gate (review only)

This offline check pins the four reviewed source files from **draft PR #356** (`b80c5adfff647aaefa194ffee997399e382644b9`). It is a safe artifact-identity preflight for the review-candidate plugin **v0.1.1**, not a deployment tool or security audit. It never imports WordPress, visits the site, executes PHP/JS, handles subscriber data, or installs the plugin.

Run `python qa/focus_popup_supply_chain/check_zip.py PATH_TO_REVIEWED.zip` and `python -m unittest discover -s qa/focus_popup_supply_chain -p 'test_*.py' -v`. A zero exit status means **only** that the supplied ZIP's four expected files match the source blobs pinned below, with no extra code/unsafe archive entries. Every other result is HOLD. Zip rules are intentionally restrictive; a legitimate package with additional files requires explicit review before adjusting the allowlist.

| File | Pinned Git blob SHA-1 |
| --- | --- |
| `fv-focus-popup.php` | `19ca40e54cd3aae9e434a34f6f83f2dcb28039d6` |
| `focus-popup.html` | `81bb038297e53ce92f7b75bf9f348d71c06af5c5` |
| `focus-popup.css` | `ce8b5a9a6e3352281d8a1b6bd45b4b02dd655500` |
| `focus-popup.js` | `5fdd7bebbca75d3cf6b167f8d4070f6364c675e2` |

**Observed production context (2026-10-31 23:50 UTC):** Authenticated WordPress reports plugin `fv-focus-popup/fv-focus-popup` **active**, version `0.1.1`, installed 22:16:11 UTC and activated 22:16:28 UTC, but the provided API does not expose its installed PHP/JS bytes. Saved homepage, `/focus/`, `/dispatch/`, 14 templates and four template parts contained no `[fv_focus_popup]` shortcode. Therefore **do not claim the live plugin matches this source, renders a popup, or is ready for release**. Backup and scan remained earlier than activation. No staged WordPress/Jetpack, mobile, consent, confirmation/welcome or hosted-PDF checks are satisfied by this utility.

To clear the provenance gate, obtain the actual installed plugin files/ZIP through an authorized read-only export and compare them. Require subsequent independent WordPress/browser and QD acceptance. Do not use plugin upload, activation, merging or live page edits from this test lane.

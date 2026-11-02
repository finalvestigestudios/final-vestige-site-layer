# Final Vestige — Local WordPress Playground Admission

DRAFT / HOLD. No WordPress.com production writes, installs, publishing, merging or paid subscriptions.

This review-only launcher unifies existing seven-chapter homepage QA (PR #252) with the private WordPress staging builder (#265), sanitized Assembler presentation (#291), and subsequent stage custody fixes (#297, #303, #310 and #316). It does not alter design or history, and does not add chapters.

## Run on an isolated developer machine

Prerequisites: the exact complete Git checkout for THIS draft PR; official independently obtained Assembler 0.0.126 theme ZIP and out-of-band SHA-256; Python Playwright and Chromium; Node and WP Playground CLI. The installer archive is deliberately not bundled. Do not confuse the production WordPress.com Personal plan with a staging environment.

    HEAD=$(git rev-parse HEAD)
    python -m unittest discover -s experience2/home-flagship/qa/playground/parity -p 'test_run_local_staging_admission.py' -v
    python experience2/home-flagship/qa/playground/parity/run_local_staging_admission.py \
      --repo . --expected-head "$HEAD" \
      --assembler-zip "$HOME/Downloads/assembler.zip" \
      --assembler-sha256 '<independently observed 64-char checksum>' \
      --stage /tmp/fv-ex2-local-preview-NEW \
      --output /tmp/fv-ex2-admission-receipts-NEW

This validates exact committed homepage and QA bytes, the pinned Assembler ZIP, runs the committed offline seven-width/four-interaction/three-negative Chromium CSP gate, prepares the sealed private preview and Assembler parity, and audits the local Playground CLI/Blueprint contract. Without the explicit --launch flag it DOES NOT run WordPress and reports READY_TO_LAUNCH_NOT_STARTED; release remains HOLD.

An optional --launch requires a private Playwright editor storage-state JSON (mode 600), locally provided axe-core JS and a developer-controlled WordPress Playground process on port 9400. Credentials MUST never be committed, shipped in archives, or uploaded to reports. Production CMS must not be consulted for authentication. A fresh ephemeral Playground typically cannot reuse a storage state from another instance: operator must establish a valid local editor session; absent that, remain HOLD. Local network binding/host firewall must be inspected before --launch; this launcher only verifies outbound loopback probing, not a network firewall. This branch narrowly extends PR #250's staging URL gate for the one token-free local WordPress selector /?pagename=fv-ex2-playground-review while continuing to reject all remote query strings, userinfo, nonces and fragments; whether Playground actually serves that page and editor credentials work is still unverified. Do not interpret local HTTP readiness as integrated staging acceptance.

## Executed tests and limits

17/17 offline Python tests passed in isolated synthetic fixtures, including real temporary Git HEAD/dirty-byte comparisons, local HTTP 200 and blocked outbound redirect probes, malicious CLI options, forged Blueprint, tampered theme hash, permission checks, and HOLD receipts. The complete exact Git checkout, official Assembler archive, installed WP Playground CLI and a private local editor session are unavailable to this environment. Actual WordPress integration, all seven-width source Chromium results, axe, Lighthouse, Safari, 200% zoom, authentic archival-media transfer, historical image rights, CI, independent QD and founder visual preview remain NOT MEASURED.

This is an orchestrator, not a live-site deployer. Keep PR #49 frozen at 10495883299d53596992c26a8987f629b2904670. Preserve the production 72 Margins entries, both Focus Fieldbook links and Jetpack subscriptions. Coordinate Apollo PR #158 and Mind/Perception PR #171 independently. No merge, no plugin installation, no production content update without explicit release approval.

Known follow-up (not claimed fixed): The edited URL gate's default local WordPress query selector still needs real HTTP confirmation; the editor browser state needs a reproducible local login bootstrap; the CLI version uses latest and should be pinned for trustworthy replays; and network binding must be audited. Until those are closed this script is a source-controlled QA framework only and release remains HOLD.

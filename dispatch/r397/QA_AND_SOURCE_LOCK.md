# R397 QA log — reproducible evidence and known limits

**Immutable canonical master:** GitHub #175 HEAD d57ccdba3aee8f065e143e101c2945f4f3d01647 (still open, draft) containing 6 Markdown editions, manifest and Python tests; all 8 files were retrieved via connected GitHub and reconstructed byte-for-byte locally. Verified Git blob hashes: manifest `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`; Python tests `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`; editions: `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`, `faa207ab7deafd86460d36f8c17fe62d392d0e14`, `aeeef34efea0cc281f69901488e4501fea851245`, `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`, `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`, `004d558df6376d2ad6f4f79a4581e8d2c444e355`.

**Actual native run:** `cd campaign-2026-mind && python tests/test_campaign.py -v` using Python 3.13.5: **6/6 passed, exit 0** on all original exact GitHub-blob-identical source. An initial incorrect unittest invocation produced import-path error; invocation was corrected and the complete suite passed. Offline runner logs and exact reconstructed files are in the companion local QA archive.

**New optional Issue 06:** `ISSUE06_EBBINGHAUS_OPTIONAL.md`, plaintext and email-safe offline HTML source-control artifacts, separate from canonical #175. The primary source is Hermann Ebbinghaus (1885; trans. 1913) Chapter III and Chapter VII, York University archival transcription. Check that all claims refer to his methods and limitations, not universal proof of a productivity intervention.

**Source-specific review decisions:** Ebbinghaus used about 2,300 possible syllables; described confounding influences and self-experimentation; measured relearning savings under a narrow controlled memorization task. No quote reproduced longer than a brief phrase and no extrapolation from retention into Zen12 efficacy.

**HTML acceptance:** one email content column, semantic `h1`, inline styles and conservative Arial/Georgia fallback, one practical CTA to the existing free /focus/, full source links, all legal footer placeholders, no tracking pixels, scripts, live merchant links, or sending capability. HTML is **offline-only**. Native WordPress email preview, actual mail-client receipt, unsubscribe action, visual browser validation and deliverability remain **UNTESTED unless separately evidenced**. The first local HTML generator mistakenly expanded markup; it was rejected and replaced with a fixed short version before PR review; the current GitHub source is the corrected version.

**Merchant scope lock:** canonical 03 Zen12 and 05 Hypnosis Live; Total Focus is one nested Hypnosis Live SKU; unrelated promotional assets cannot authorize sending by email.

**Exactly no list work / no WordPress writes / no send.** Reported recipient count 3/3/2 is a diagnostic snapshot, not a recipient eligibility claim. Settled revenue unknown. All noncommercial and commercial release flags HOLD. PR stacked on #2723, no modification to frozen homepage PR #49.

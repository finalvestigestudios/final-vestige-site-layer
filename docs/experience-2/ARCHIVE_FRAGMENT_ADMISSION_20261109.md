# EX2 archive case fragment integrity — review-only

**Parent:** Draft PR #1810 exact HEAD `ee6e080d280b021306f2100741120807d0d510e3`. Frozen PR #49 at `10495883299d53596992c26a8987f629b2904670` is unchanged. No WordPress CMS, publishing, plugins, analytics or affiliate writes.

## Reproduced defect

The source-controlled seven-chapter homepage contains three individually addressable case records: `#fv-hf-apollo`, `#fv-hf-franklin`, `#fv-hf-malbone`. The optional JavaScript selector always initializes on Apollo and hides the other two cases. A human clicking a future deep link to Franklin or Malbone therefore receives **Apollo**, not the promised evidence. The mismatch is especially important for source-linked and creator-led high-intent destinations. No such new campaign URLs are authorized by this PR.

**Before, actual 11-source offline Chromium assembly:** 60 scenarios, 217 assertions, **204 pass / 13 fail**. Failures concentrate on Franklin/Malbone deep links and forward/back fragment navigation, including 320/390/768/1440/1920 CSS-pixel widths. In no-JavaScript conditions all three records remain visible.

## Isolated correction

- Recognize **only exact internal record fragments**; select their existing corresponding case before the enhanced archive initializes.
- On later `hashchange`, reveal and scroll to the requested existing case, with browser auto scrolling. Unrelated chapter fragments or unrecognized campaign fragments do not change the selected record.
- Do not move focus, rewrite the historical record, change URLs, touch analytics/UTMs, add imagery or external scripts. Native no-JS semantics remain: all three cases visible.

**After, exact 11-source offline Chromium assembly:** 60 scenarios, **217/217 assertions pass**, with Chromium requests for external media intentionally blocked; no claim of actual image delivery or production conversion uplift. The source patch is byte-identical to the locally tested patched `flagship.js` (Git blob `74ebffd83b6d394be8f0e323a1888b5d867bf4e0`).

Source-controlled verifier: `tests/experience-2/verify_archive_case_fragments.py`, which imports the existing 11-source assembly/HEAD-verification gate from PR #1810. Run in a **clean exact checkout**:

```bash
python tests/experience-2/verify_archive_case_fragments.py \
  --checkout . --expected-head <THIS_PR_EXACT_HEAD> \
  --out /tmp/fv-ex2-record-fragments.json
```

The new committed verifier is provided for exact-checkout reproducibility and still needs **independent execution against this PR's full checked-out HEAD** before stage admission; the 217-pass result comes from separately executed local equivalent logic using the 11 original GitHub source blobs and the exact patched JS.

## Conversion-first test contract

**Offer:** Existing free 52-page Seven Day Focus Fieldbook, unchanged.
**Entry intent:** Evidence-specific reader enters via a fully declared URL fragment. If the requested record is hidden, the archive breaks campaign-to-page continuity.
**Change/hypothesis:** Reveal the matching record immediately, preserving source links and visitor trust. **No claims of measured commercial lift.**
**Primary acceptance:** Franklin/Malbone deep links land on the correct visible evidence; back/forward preserve selection; no-JS retains all records; three negative controls reject unknown and unrelated fragments. Original Focus destination and Jetpack remain untouched.
**Commercial success measure (Claude's lane):** verified orders and net revenue per 1,000 qualified human sessions, with separate confirmed Jetpack signup and real paid conversion, not clicks.

## Unresolved release gates

- Isolated WordPress Playground/Assembler environment (WordPress.com Personal does **not** include hosted staging clone).
- Genuine page render/first-party media transfers, anonymous-source denial and editor-only preview; PHP/plugin activation not performed.
- Independent WCAG 2.2 AA axe + manual screen-reader/keyboard/touch/reduced-motion/200% zoom, Safari, Lighthouse/CWV lab and later field data.
- Primary source/territory image-rights review (#1730), genuine Jetpack confirmation (#1681), no invented affiliate permission, protected production URL validation.
- GitHub CI/QD on exact head, founder visual review and **explicit release approval**. No merge/deploy/publish.

**Release decision: HOLD.** No production changes or spending.

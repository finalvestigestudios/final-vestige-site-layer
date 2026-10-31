# R30 QA provenance — draft-only, no native mail

**Review scope:** Six optional custom excerpts in `delivery/wordpress_excerpt_copy.json` and repaired legacy `tests/test_excerpt_copy.py`; new source-specific crosschecks. No edits to the six original email manuscripts, their HTML/plain previews, or Gutenberg post candidates. Base is existing draft PR #364 at `a78110837924a7e1b1fb3ecae012d14360155617`.

## Independently performed checks

- Authenticated WordPress read **2026-10-31 23:35:11–14 UTC**: newsletter enabled; default post sends OFF; excerpt; zero recent sends; 52-page Focus Fieldbook welcome configured, receipt unverified; subscriber counters total=2, confirmed=2, unconfirmed=2 (not additive, not audience consent proof). Published /dispatch/, /focus/, Editorial Standards consulted by ID. No addresses or consent details exported.
- Connected Gmail read-only searches: Inspire3 consumer promotions appear, but no account-specific acceptance or **email** promotion permission; the only matching WordPress subscription-related message since October 20 was an October 25 **confirmation**, not a received campaign or Fieldbook welcome. No contact details or message tokens copied into source control.
- Exact current parent SHA confirmed via GitHub PR metadata and Git compare: R29 added seven isolated files since R28; existing campaign source unchanged. Archived R28 local reconstructed source and its test suite were checked against **ten** current GitHub blob SHA identifiers for core manuscripts/manifest/previews. The exact current revised optional excerpt copy and new audit/test files were re-fetched from the working GitHub branch for independent JavaScript execution.
- **134/134 baseline Python** passed on locally reconstructed archive source after restoring the known historical Gutenberg #03 fixture.
- A fresh local reconstruction including optional excerpt test and corrected legacy compensation test: **138/138 Python passed**. A test first failed because it mistakenly treated the historical *royal commission* as commercial affiliate compensation; the source-controlled legacy test was improved to match **'may earn a commission'** or **'affiliate'** rather than the generic noun *commission*. The corrected final run is the 138-pass result. The local runner is an archived-source reconstruction, **not a native GitHub clone or GitHub Actions run**.
- New **exact committed JavaScript V8** auditor and test executed against GitHub-fetched working-branch content: **48 assertions passed, including 16 adversarial modifications rejected**. It rejects wrong historical period, fire-timing overstatement, unapproved merchant link, absent disclosure, prohibited overclaims, changed subject/ratio and unverified send state. No network, mail or CMS access.
- Chromium was run with `/usr/bin/chromium` against a distinct locally reconstructed excerpt-review HTML (not exact committed GitHub board or received Jetpack email). **6/6 viewport checks passed:** 320/360/390/768/1024/1440px, six article/heading elements, HOLD warning, no horizontal overflow. Initial attempt with Playwright's absent bundled browser and a blocked file:// navigation failed; using installed Chromium and `set_content` resolved local offline review. This does **not** prove Gmail/Outlook/Jetpack email rendering.
- All six excerpts are **<=350 characters** (a conservative offline layout budget, not evidence of actual custom-excerpt truncation). The two commercial possible-commission disclosures finish within those first 350 characters. All six remain HOLD_UNSENT, #03/#05 additionally HOLD_MERCHANT. No A/B data or fabricated metrics.

## Remaining release evidence

Current merchant affiliate acceptance, allowed promotion via email, exact earning-link format and SKU, published vetted product guides, approved creative and up-to-date checkout/refund evidence. A valid Final Vestige postal address and **working** unsubscribe in an authorized received email; exact title, full/excerpt delivery, preheader/snippet, recipient eligibility/consent, and founder final approval. Hosted GitHub Actions may still fail independent of locally passing tests; check the new PR workflow before declaring CI success.

## Sources
- [Jetpack newsletter customization](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/)
- [WordPress newsletter settings](https://wordpress.com/support/newsletter-settings/)
- [FTC CAN-SPAM Guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Zen12 About](https://zen12.com/about)
- [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus)
- [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/)

No sends, test sends, WordPress writes, merchant contact, subscriber exports/imports, analytics insertion, platform expense, production publication or homepage changes.

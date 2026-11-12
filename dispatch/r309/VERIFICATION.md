# R309 — Executed verification record (2026-11-12 UTC; no send)

## Source integrity
Original six issue Markdown blobs + manifest + native Python test file (8 files) were read from immutable canonical PR #175 commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`; their local Git object IDs matched all eight exact GitHub blob IDs. Thus the six original Python unit tests ran on byte-identical source, not edited approximations.

**Native original suite:** `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` → 6/6 PASSED.

**R309 QA source:** `dispatch/r309/tests/test_r309_artifacts.py` local Git blob `68c1552f64dc526a048701d24f7d339957efc72d` matched GitHub. `dispatch/r309/provenance.json` local blob `4049db5452aede607da6109e548947db2582b0a5` matched GitHub. Twelve source-derived HTML/text files were generated locally from the exact eight master inputs; their local Git blob IDs matched the committed GitHub documents, including post-fix commercial HTML revisions.

**Native R309 suite:** `python -I -m unittest discover -s dispatch/r309/tests -v` → 7/7 PASSED. Checks included subject/preheader fidelity, 4:2 mix, hard-stop postal/unsubscribe tokens, inert commercial guide URLs, first-party href restriction, email-safe forbidden tag exclusions, HTML table semantics, declared holds and original Apollo subject defect.

## Genuine offline browser QA (not inbox rendering)
Six GitHub-byte-identical HTML specimens rendered using local headless Chromium via Playwright at viewport widths 360, 390, 768, 1440 pixels. Initial viewport check **FAILED for Issue 03** because the pending Zen12 guide token was an unbreakable word (360px document scrollWidth 520px). Issue 03 and Issue 05 HTML table content cells were corrected with `overflow-wrap:anywhere;word-break:break-word;`. Their two committed HTML files were re-read and local SHA IDs matched. Final `24/24` viewport checks PASS: no horizontal overflow; one H1; two presentation tables; required visible HOLD footer; no disallowed foreign links. Three 390px screenshots (03/04/05) and JSON browser record are in local offline reviewer bundle.

The HTML is still **not actual Jetpack output** and has NOT been tested in actual email clients or via a received-email preview. Hidden preheader display is speculative. This review system cannot verify a true platform unsubscribe or physically valid Final Vestige mailing address. No test email was sent.

## Source- and legal-led redline
- Original 01/02 duplicate the Puységur guide, editorial progression issue; compare prior R301/R300 alternatives only, neither adopted.
- Original 04 subject alleges 'Fourteen seconds' without a defensible interval; **cannot pass truthful-subject release gate**. R302 alternative exists; not adopted.
- Original 06 sends existing subscribers to signup rather than direct Fieldbook, friction; compare R299 alternative; not adopted.
- Original 03 and 05 have **no live vetted guide CTA, account-specific Inspire3 email permission, affiliate earning link, verified checkout/refund/price or proven effectiveness**. Seller pages are https://zen12.com/about and https://hypnosislive.com/mental-skills/total-focus. The former promotes 12 levels/four styles; the latter displays a 33-minute, 47-MB MP3. Efficacy and offer terms are seller claims, not established endorsements.
- FTC business CAN-SPAM guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business; disclosed publisher postal address, functional unsub and marketing identity remain hard holds. Existing WordPress Jetpack post-based mechanism cannot be represented as signup-relative drip.
- The WordPress authenticated read-only snapshot at 16:36 UTC: subscriptions=true, site_can_send=true, default auto-email=false, content=full, sender=Final Vestige Studios, email category segmentation disabled, active configured Focus PDF welcome. Diagnostics total=3 confirmed=3 unconfirmed=2; these are not additive and do not establish 3 email recipients, because email subscription state is separate. No subscriber PII read/exported. Five latest displayed post notices were `never_sent_opted_out`, not evidence about all time.
- Source for provider semantics: https://wordpress.com/support/subscribers/ (reviewed 2026-11-04) and https://wordpress.com/support/newsletter/send-newsletter-emails/.

## Accepted evidence classes and remaining hard holds
BUILT = six HTML + six plaintext review specimens, integrity ledger and tests.
TESTED = 6/6 native original, 7/7 native new, 24/24 Chromium viewport checks and committed SHA parity.
LIVE = none of these campaign assets.
VERIFIED = only the read-only site status and seller-page *descriptions*; not purchased outcomes, partner email rights, consent eligibility or received mail.

HOLD_UNSENT = ALL SIX. HOLD_MERCHANT = ISSUES 03, 05. ALTERNATIVES NOT_ADOPTED.
No sends / test sends / schedules, WordPress posts or settings writes, affiliate activations, tracking scripts, list imports, social posts or spending.

## Conversion-first ownership
**OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → PASS/FAIL EVIDENCE → OWNER**
* Zen12 → reader guide → paid conversion → blocked by email permission, live guide and valid URL → first obtain merchant-specific proof, then independent guide acceptance → FAIL/UNKNOWN / Mind/Commerce.
* Focus Fieldbook → confirmed lead → provider Email Subscription status not reconciled and `?subscribe=` is a visual state only → privately count eligible consent transitions and dedup → UNKNOWN / Claude/Focus.
* Dispatch edition → compliant received inbox → actual postal/unsubscribe and native preview absent → founder-approved no-send preview first, no real email unless separately approved → UNKNOWN / Dispatch/Founder.
* Grok asset → qualified-human session → real asset-key attribution absent → coordinate unique source/medium/campaign/content mapping without new scripts → UNKNOWN / Grok/Praxxis/Claude.
* Paid checkout → realized net revenue → settled paid orders and refund/fee evidence absent → only count verified transactions, 7/30-day cohort with tiny-sample warning → NOT COMPUTABLE / Commerce.

Final founder review of exact copy, audience and publication/email schedule separately required; no acceptance inferred from this source PR.

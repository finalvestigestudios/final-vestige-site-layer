# R242 — HTML Attribute Grammar and Claim Visibility Custody (DRAFT / HARD HOLD)

**Scope:** Issue #136 Preparedness integration source/citation safety only; founder conversion charter #818, coordination #820. This is source-code review and synthetic test evidence, not publishing or an independent QD PASS.

## Material reproduced defect
R241 tokenizes actual attribute names and rejects entity-encoded `aria-hidden`/`style`/`class`/`id` values, but it can **accept adjacent quoted attributes without required separating whitespace**: `<p title="ordinary"aria-hidden="false">{{cite:source}}</p>`. Python HTMLParser parses both names and they agree with the old lexer's names; thus name parity alone does not reject this HTML parse-error condition. This matters in a chain that asserts browser-readable source placement and must fail closed on ambiguous markup.

## Bounded correction
In existing authenticated `tools/r240_html_attribute_entity_custody_hold.py` (no new duplicate loader), R242 now:
1. Requires HTML ASCII whitespace between consecutive attributes, while accepting legitimate `>` and `/>` endings.
2. Rejects control-character and raw less-than-in-quoted-value markup that can create browser-grammar ambiguity, while allowing `&lt;` descriptions.
3. Compares **decoded attribute values** to HTMLParser's values in addition to ordered name parity; retains all R240/R241 encoded-sensitive-value, duplicate-sensitive-attribute, UTF-8, original-roster and 35/2000 source fingerprint requirements.
4. Keeps protected R220 import-by-checked-bytes and postflight identity, now pinning R242's exact module Git object.
5. Does not alter a manuscript, source row, canonical URL, verification state, tool, WordPress HTML, commerce offer, or approved safety language.

## Test and evidence boundary
- Original bypass was reproduced with the exact original R241 module Git blob `bfffb168a236abc4b4923e5113c362e36e30bf76`: missing-separator citation produced a HOLD receipt instead of rejecting the markup.
- Locally executed: `python -I -m unittest discover -s preparedness/tests -p 'test_r242*.py' -q`: **95 / 95 PASS**, including 44 individually distinct bad separators, 44 distinct paired legitimate source-markup controls, C0 / entity / valid SVG / source-roster custody / encoded-hidden controls. `python -I -m py_compile` PASS.
- The R242 source and test file Git object identities were independently checked after GitHub write. The full authentic 35-article Python suite, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, 41-tool WordPress/preview replay, browser semantics and human source/medical QD remain **NOT EXECUTED / NOT VERIFIED**. Local `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` fails: `Could not resolve host: github.com`.
- All seven frozen Claude contributor heads compared to current branch refs **identical** at this run: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
- Independently checked draft QA PR #157, isolated synthetic fixture PR #169, and homepage lead #1689. **Nothing merged; all remain under their original owners.**
- Historical release holds persist: 32 unadjudicated shared-source-scope groups, three held original citation occurrences (two in Article #7, one in Article #20), medical/utility/water safety review, independent QD approval, authentic build, founder release.

## Conversion-only handoff (NO offer activation)
One high-intent hypothesis: existing Grok post, **only if authenticated**, about emergency contacts and household document organization → public free `/preparedness/` → relevant free source-backed communication/household guide **after independent approval** → optional existing Legacy Triage paid PDF **only if rights, safety/privacy, precise audience fit, buyer disclosures and completed delivery/refund acceptance are separately verified**. The current PDF is primarily an estate/incapacity product, not an approved disaster toolkit. Don't reuse retired water freebies or gate essentials.

**Prioritized offer → step → blocker → change/test → evidence → owner:**

| Offer | Funnel step | Blocker | Change / acceptance check | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| Free Archive | Published Grok asset → landing | asset_id, post hook/link/rights, mobile bio target and UTM permission missing | Read-only TASK-008 match of actually published media | UNVERIFIED | Grok/Praxxis |
| Source-backed free guide | Landing → relevant article | original review, genuine build and mobile/a11y missing | Verify one authentic free guide, warning/source visibility and 320/390/768/1440 widths; never gate safety | HARD HOLD | Preparedness/independent QA |
| Legacy Triage PDF (PROVISIONAL) | Free guide → optional paid CTA | complete content/rights, security of passwords and intended audience not authenticated | Review complete original PDF, actual Payhip listing/fulfillment, FTC/affiliate disclosure if applicable; draft CTA **disabled** until founder approval | NOT APPROVED | Founder/Commerce |
| Provisional paid pack | Checkout → fulfilled order | checkout/delivery/refund proof absent | Authorized real merchant acceptance and delivery check; no unapproved test purchase | NOT TESTED | Commerce |
| Orders | Qualified sessions → net | Grok attribution, settled orders/fees/refunds missing | 7/30-day consent/privacy-safe cohort, no duplicate analytics scripts | NOT COMPUTABLE | Claude/Analytics/Commerce |

KPI = 1,000 × (merchant-settled gross orders minus refunds, fees and actual incremental attributable costs) / qualified-human sessions, with 7/30-day cohort and tiny-sample warnings. Never call a pageview, signup, CTA click, merchant outbound click or checkout start a sale. **No verified denominator/settlements, so KPI NOT COMPUTABLE.**

**No merge, public publishing, navigation, CMS, product, affiliate, emails, social posts, tracking scripts or spend.**

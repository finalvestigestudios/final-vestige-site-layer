# EX2 / real seven-chapter observer → Focus conversion integration — DRAFT / HOLD
**November 3, 2026 PT · source-controlled candidate ONLY. No WordPress production change.**

## Founder conversion priority, expressed as a measurable decision
- **Offer:** published free 52-page Seven Day Focus Fieldbook at `https://finalvestige.com/focus/`. This is a *lead-pathway offer*, not paid revenue. A verified, rights-cleared, presently purchasable Mind SKU or approved Inspire3 affiliate relationship has **NOT** been established.
- **Audience:** change-blindness / perception readers arriving from Grok's relevant social asset, *only after* the asset ID and platform destination are actually recorded by Grok/Praxxis in TASK-008. No fabricated asset IDs or UTM links.
- **Funnel step:** complete chapter 06 observation exercise → inspect source limitations → optional free Focus resource → existing Jetpack confirmation/delivery → separately approved paid offer (UNVERIFIED).
- **Observed barrier in previous source:** observer-exit has a historical source link but no directly adjacent Focus choice. The free Focus link does exist elsewhere (masthead, chapter 07, exit); proposal addresses a *contextual* choice, not a false claim that there is no homepage CTA.
- **Change:** add one distinct canonical Focus link beside the original historical link within the *actual* `experience2/home-flagship/index.html`, not just an invented fixture. Source keeps the disclaimer that a studio demonstration is not an attention test or health assessment. Existing seven chapters, article links, archive imagery, 72 published Margins in the synthetic Gutenberg wrapper, and free Jetpack stub remain.
- **Experiment:** compare consented, qualified human visitors who reach observer-exit and then go to Focus, with evidence-trail activity as a guardrail. Hypothesis: a clearly labeled free next action increases confirmed Focus interest **without reducing evidence-source inspections**. No uplift or paid-order claim until data exists.
- **Ownership:** Homepage engineering owns only source-native layout + QA; Claude owns nonduplicative analytics, attribution and commerce; Grok owns content + immutable asset IDs, Praxxis audits creative and demand; Dispatch owns existing welcome/nurture; founder approves release/spend/merchant terms. See #150, #820, #818, #171, Drive TASK-008.

## Actual changes / source custody
New branch stacks on draft #894 at exact parent `df1793fa8504fcfd7f18d6842c9c689d5c71f6c3` (which itself stacks on #888). **Frozen PR #49 remains at `10495883299d53596992c26a8987f629b2904670` and is NOT edited.** Exactly two flagship source files are modified:
1. `index.html`: one existing `fv-hf__observer-exit` is enhanced. Original history/Puységur link remains, canonical Focus path added, no new chapter, scripture, image, library or misleading science claim.
2. `observer-lab.css`: appended *scoped* CTA treatment, 48px link minimum, 900px reflow, focus-visible inherited from source, reduced motion and forced-color parity. No new JS/fonts/media/network requests.
3. `conversion/test_native_observer_focus.py`: source + actual Gutenberg assembly conservation and **12 adversarial invalidations** (including changed domain, deleted evidence link, tracked/merchant copy, CTA size regressions).
4. `conversion/browser_native_source_review.py`: executable optional offline full-seven-chapter source + all six actual CSS, JS disabled and all external requests blocked, screenshot and keyboard/44px/5-width/semantic `<details>` receipt. It does **not** claim hosted media/WP/Lighthouse/WCAG signoff.
5. Existing `.github/workflows/ex2-assembler-front-render-HOLD.yml`: add the Python regression gate before test candidate Save. This DOES NOT approve merge, and tests must run on exact SHA.

## Verification ledger
- **PASS — independently observed read-only source consistency:** 18/18 assertions against the new GitHub branch compared with parent SHA. The entire `index.html` outside the observer exit was byte-identical; `observer-lab.css` only appended a scoped rule set. The canonical Focus link appears once *within* that exit; original historical URL retained. Existing 7-chapter links and all 4 original JS references retained. No tracking/UTM/merchant URL in the modified exit.
- **NOT YET EXECUTED:** committed Python unittest/12 adversarial mutations on full checkout; actual WordPress/PHP/Gutenberg Save and saved-layout browser execution; optional real-source offline Chromium script. Source tests are written and CI-wired, *not counted as passing until executed*.
- **NOT QUALIFIED:** live visitor behavior, real Jetpack confirmation, actual Grok campaign matching, Payhip orders/fees/refunds, source-confirmed affiliate commissions, Lighthouse/CWV, full-document axe/WCAG 2.2 AA, 200% physical zoom and media rights.
- **KNOWN RELEASE BLOCKER:** serious default Assembler navigation-list violation at desktop from prior isolated real browser evidence. Native header correction currently unverified due GitHub runner pre-execution failures. Do not suppress axe or treat the component-only pass as whole-page compliance.
- **Environment:** WordPress.com Personal plan has no native staging clone. An isolated Playground is NOT WordPress.com Atomic/Jetpack parity; no user/subscriber/export data may be imported. No official hosting upgrade proposed.

## Reproducible checks on exact checkout
```sh
python -I -m unittest discover -s experience2/home-flagship/conversion -p test_native_observer_focus.py -v
python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_source_flagship_playground_candidate.py -v
# Optional developer Chromium with Python Playwright + local Chrome; all network blocked:
python experience2/home-flagship/conversion/browser_native_source_review.py --out /tmp/fv-ex2-native-focus
```
A source-only pass is not a WordPress test. The existing full Assembler exact-source pipeline must produce saved-layout 320/390/768/1440/1920 screenshots, keyboard/touch/no-JS evidence, genuine image transfer/decode and full-document axe (fail closed), followed by physical zoom, manual accessibility and lab Lighthouse. Preserve a clear preview for founder selection; no other art direction selected here.

## Measurement contract after separately approved implementation
Qualified human sessions indexed by real Grok `utm_content=asset_id` and `utm_campaign` → observer exit exposure (if consented/observable) → source click **or** Focus CTA click → confirmed Jetpack subscriber (not form submit alone) → merchant-confirmed paid order **or** partner-confirmed commission → refunds/fees → **realized net revenue per 1,000 qualified human sessions** for 7/30-day cohorts. Tiny samples require warnings. Data absent or inaccessible must be **UNKNOWN**, never `0` unless independently verified.

No custom tracking script, cookies, pixel, platform API, extra form, duplicated UTM implementation, popup, affiliate URL, product benefit promise, payment checkout or external subscription was added. Historical archives remain the primary mission and accessible without purchase.

**RELEASE DECISION: HOLD. No CMS writes, merges, publication, production theme/navigation changes, plugin activation, affiliate activation, emails, paid service or Grok queue edits.**

# Apollo R281 — Source-first EvidencePlate / SourceDrawer / ChronologyRail

**STAGING ONLY / DRAFT / HARD HOLD.** Stack on R280 draft PR #2019; inherit its Apollo source-custody lane without changing homepage PR #49, Research Desk PR #158, existing WordPress content, analytics or production settings. Coordination: #150 and conversion charter #820/#818.

## Implementation

`apollo-source-experience.php` is a separate WordPress shortcode candidate: `[fv_apollo_source_experience]`. It outputs three **curated** Apollo chronology plates, each with a dated, sourced claim, an explicit limitation, a native keyboard/no-JS `<details>` SourceDrawer, and one accessible chronology jump link. IDs are unique across shortcode instances. Styling is scoped to `.fv-r281`, responsive at 320–1920, forced colors and reduced motion, with print CSS that exposes the closed drawers and complete source URLs. The document gallery deliberately contains **no unreviewed photographic media** or invented geographic pins. A text-only fallback remains useful without CSS/JS.

The original WordPress-ready Research Desk in PR #158 and the R280 review adapter are not replaced or modified. This is a **separate pilot component**, not proof that the public Atlas has been updated. Dynamic/template shortcode asset discovery and exact installed WordPress/Assembler acceptance remain release blockers.

## Historical provenance (checked November 11, 2026)

- 1967-01-27 pad test/fire: [NASA mission history](https://www.nasa.gov/mission/apollo-1/).
- 1967-01-28 Board established/first met: [NASA Safety and Mission Assurance Apollo 1 account](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1).
- April 1967 Review Board findings: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); most probable electrical arc **does not mean a conclusive precise ignition source**.

These are three editorial chronology categories, **not three independent eyewitness corroborations**. The latter two NASA summaries and the original report are not independent archives. Research/external hyperlinks do not imply NASA endorsement.

NASA [media guidance](https://www.nasa.gov/nasa-brand-center/) and [advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) impose restrictions on official branding, promotion and recognizable people; **no NASA media, logos or paid placements** were included. Rights clearance for later gallery photographs is NOT established.

## Reproduction

```bash
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r281/qa/committed_gate.py /tmp/fv-r281-qa
```

Committed acceptance executes **real PHP and real Chromium/Playwright**, not a synthetic screenshot-only fixture: 10 combinations of 320/390/768/1440/1920 × JS enabled/disabled, touch, forced-colors, reduced-motion, native keyboard disclosures, anchor navigation, print-source/URL preservation, two-instance unique IDs and no external requests. Negative PHP tests reject changed NASA destinations, duplicate dates and missing custody fields. Local preview and receipts are stored in the reproducible evidence ZIP.

Reviewed source blob identities:
- PHP: `256c52b8a63354c68dcef62ffe81501917ed09b0`
- CSS: `144bec0940af3e9c50778450e27d825f89984c16`
- executable browser QA: `8f80c9361bd4c2b19d173de2fe84560d0beadd7d`

**Not tested:** installed WordPress/Assembler, actual browser-over-HTTP/CSP, genuine axe-core (offline dependency absent), NVDA/VoiceOver, native browser UI zoom, field LCP/CLS, hosted CI, approved image rights, verified creator Apollo asset, merchant acceptance, confirmed paid orders or founder production authorization. Local screenshots/performance observations are not production CWV.

## One conversion hypothesis, not a live sales claim

**Audience:** viewers of a *verified/published* Grok Apollo long-form episode who want to inspect the evidence before committing to an FV relationship. **Route:** Grok asset with actual `asset_id` and approved social UTM → existing public Evidence Atlas → one native R281 CTA to the **free original Apollo 1 investigation** → optional separate **clearly disclosed Mini Museum buying guide** only after merchant eligibility, permitted commercial linking, rights and founder signoff are proven → independently verified paid merchant conversion. No commerce in historical prose; no newsletter/signup inserted before evidence access. Grok creates/posts; Praxxis reviews; Claude owns commerce measurement; founder approves release.

**Hypothesis:** chronological clarity and explicit custody boundaries increase qualified Atlas→free-investigation continuation and downstream buyer trust, without misleading sales claims. Existing measurement should count actual qualified-human sessions and confirmed leads/paid orders/fees/refunds; use 7/30-day cohorts and compute realized net revenue per 1,000 qualified human sessions **only when source-confirmed data exists**. Counts and uplift are currently **UNOBSERVABLE**. No new tracking scripts or merchant activations.

**Release:** HARD HOLD. Draft code may be reviewed; no production deployment, WordPress writes, social publishing, email sends or paid services.

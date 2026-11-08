# R53 — Dispatch attribution and decision-quality metrics contract (PROPOSAL; INACTIVE)

Owner: **Dispatch #174**; coordinate on-site events and buyer-guide attribution with **Mind #171**, including Mind R56's **separate** privacy-first categorization prototype. Canonical PR #175 remains four historical/editorial and two optional disclosed commercial editions. **No tracking code, UTM change, email provider, analytics account, pixel, affiliate link or subscriber export is created/activated by this sprint.** There are no Dispatch sends or real pilot results to analyze.

## Minimum unit: an issue, not a subscriber profile

Each of the six eventual newsletters has a nonpersonal edition label (01..06), variant fixed to “canonical” unless the founder later approves a copy candidate, and one editorial CTA identity from the original manifest. On any *future* fully approved message, an internal first-party landing URL **may** be given an approved fixed campaign token (e.g., source=dispatch, edition=01, no unique token). Do **not** generate personal subscriber parameters, open-tracking pixels, IP fingerprints, direct merchant links, or cross-site audience joins. Do not claim a proposed query string is implemented or supported by Jetpack.

Attribution stages and evidence types:

| Stage | Acceptable proof | What cannot be inferred |
|---|---|---|
| Newsletter delivered | Actual provider aggregate delivered count, with delivery definition and date | Dashboard “total=2” does not equal delivered audience or unique people |
| Opened | Only if the provider actually supplies the statistic, labeled an unreliable proxy | No inference that non-open means unread, or that open represents a person |
| CTA interacted | Instrumented first-party aggregate event only after privacy/consent approval; or an explicitly sourced provider count | No actual visit/sale from a button existing in offline HTML |
| Landed on guide | Page analytics from approved first-party source with clear same-period attribution definitions | Referrer/UTM alone does not demonstrate email identity or intent |
| Clicked merchant outbound | Only an approved guide outbound event when eligible live link actually exists | No purchase or commission claim from a click |
| Purchase/commission | Actual named affiliate program report and permitted attribution reconciliation; avoid PII | Never assume conversion, payout or terms from offer page or estimated EPC |
| Unsubscribe/complaint | Provider aggregate with explicit time window and unique definitions | Not proof a link functioned in a specific unreceived message |

Reporting record is evidence-first: campaign version, edition, event, source system, ISO date window, denominator definition, record_count if truly supplied, proof reference, uncertainty note, effective privacy scope. Any value not measured is **null / NOT_MEASURED**, never zero. **Zero** is allowed only with an authoritative source confirming zero over a specified period; “recent_sends=[]” means no *reported recent sends*, not lifetime zero. Current subscriber total/confirmed/unconfirmed counters **2/2/2** are nonadditive and **cannot** supply the unique delivered denominator.

## Tiny-list and experimentation rule

With this currently ambiguous two-person-sized audience, **no statistical A/B claim**, no conversion lift, no open-rate ranking and no significance language. WordPress platform aggregate counts can be reviewed internally without publishing user-level data. For any future shared aggregate segments, apply privacy suppression for tiny groups (suggested minimum n=20 for external-facing segmentation, subject to actual privacy policy) and avoid reporting a percentage when denominators are unknown or too small to be meaningful. The n=20 threshold is a privacy **proposal**, not an assertion that n=20 permits reliable statistical inference.

The exact metric plan requires founder and privacy approval **before implementation**. Do not add a new SaaS platform or duplicate signup list to support metrics. Retain only the minimum event/aggregate fields actually needed, with a retention and deletion schedule. Do not expose subscribers' email addresses in GitHub, test fixtures, screenshots or event names.

## Release readiness vs measurement

The commercial release gate is **not** a traffic goal. Named partner approval, product-specific email permission, approved first-party guide, exact authorized earning links, current terms, real newsletter MIME footer/opt-out, unique consenting audience, and final founder creative/audience/date authorization remain independent blockers. Until then an analytics dashboard would be an attractive empty shell—not evidence of success.

**Status:** proposed analytics specification only. ALL SIX HOLD_UNSENT; 03/05 HOLD_MERCHANT.

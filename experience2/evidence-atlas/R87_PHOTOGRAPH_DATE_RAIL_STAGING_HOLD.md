# Apollo R87 — verified photograph-date rail (STAGING HOLD)

This is a **new, isolated source-controlled staging component**, not a WordPress publication, theme edit, gallery of NASA images, accident/fire chronology, or geographic map. It builds on R86 actual Research Desk + generated Atlas concordance and immutable R37, R79, R55 source registers. No changes to homepage PR #49, homepage branches, or original Research Desk PR #158.

**Why:** Source custody was verified in R86, but readers still need an explicit way to explore **when photographs were actually taken**, with no invented order for a day-unknown portrait or same-day tribute images. R87 adds a four-milestone photograph-date rail (October 18, 1966; January 3, 1967; January 28, 1967; January 24, 2017), groups two January 24 photographs in a single milestone **without an implied sequence**, and places the month-only January 1967 portrait separately outside the dated order. These photographic dates never imply the accident's fire sequence.

The rail offers six source-bound EvidencePlate articles, native no-JS SourceDrawer HTML <details> disclosures, NASA outbound links, accessible in-page chapter navigation, six evidence limitations, visible rights HOLD, complete URL in print, reduced-motion/forced-color behavior, and responsive 320–1920 styling. It downloads or embeds no photographs, infers no pins/edges, uses no network or JS, and never changes WordPress content/settings.

## Reproduce offline

Run these commands from the repository root:

    python -m unittest discover -s experience2/evidence-atlas/tests -p test_chronology_r87.py -v
    python experience2/evidence-atlas/tools/build_chronology_r87.py /tmp/r87-stage /tmp/R87_A.zip
    python experience2/evidence-atlas/tools/build_chronology_r87.py /tmp/r87-stage /tmp/R87_B.zip
    cmp /tmp/R87_A.zip /tmp/R87_B.zip

The dedicated GitHub workflow also runs pinned Playwright+Chromium+axe-core across 320/390/768/1440/1920, JS-on and JS-off, native keyboard, touch targets, forced colors, no remote requests, horizontal overflow, lab LCP/CLS, screenshots and native print PDF. Browser results are **local staging measurements**, not hosted WordPress CWV, and do not replace physical-device or screen-reader acceptance.

## Release gate: HOLD

- NASA metadata is previously source-page audited; **individual media reuse review remains 0/6**, not approved, and no NASA photograph is embedded.
- The crew portrait's proposed S67-19766 association is **provisional**; its exact photographic day is unverified.
- Hosted WordPress.com isolated compatibility testing, independent QD, NVDA/VoiceOver, real devices, founder visual selection and publication approval are pending.
- No production merge/deploy, WordPress writes, paid SaaS, or edits to frozen homepage PR #49 permitted.

This artifact is for editorial/engineering inspection only. See Issue #150 and stacked R86 draft PR #742.

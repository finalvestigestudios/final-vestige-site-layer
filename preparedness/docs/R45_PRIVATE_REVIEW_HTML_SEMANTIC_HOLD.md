# R45 — Private offline review HTML and navigation safety (Issue #136)

**RELEASE HOLD — DRAFT ONLY.** This change is an additive engineering safeguard for the already-unpublished Preparedness Archive. It is **not** a source-accuracy determination, safety finding, qualified medical approval, independent QD PASS, or authorization to publish.

## Threat addressed

R44 checks the exact R43 38-page private review bundle against separately supplied R42/R43 fingerprints and canonical ZIP metadata. An independently sourced trusted fingerprint is necessary but not sufficient to establish that the rendered offline reviewer experience contains no active links, hidden safety warnings, executable content or omissions in its local navigation. Even correctly hashed HTML can be unsafe if the HTML renderer itself changes.

R45 runs a **second, semantic examination of the actual HTML bytes** after R44 verification, enforcing the frozen R43 presentation contract:

- Exactly 35 original draft article pages + one original water-tool page, plus one index and one cited/uncited shared-source-variant page. Their preserved contents remain validated through R37/R42/R43/R44, including the **1,959** individual citation occurrences, **367** source-reading relationships, **43** cross-cluster fallbacks and **30** original repeated-URL groups. No URL deduplication or source-depth reduction is introduced.
- Strictly bounded allowed HTML elements and attributes; no scripts, forms, images, embeds, frames, SVG, external stylesheets, base tags, refresh tags, inline event handlers, hidden overlays, HTML comments or processing instructions. Literal source URLs and markup in source notes remain escaped and **non-clickable**.
- Requires the original exact restrictive CSP and static, network-free CSS, and the visibly marked **PRIVATE / UNVERIFIED / HOLD** safety banner on *every* page.
- Each article/tool links back **only** to the local index. The shared-source page links back only to the index. The index has **exactly one valid local link to every one of the 36 article/tool pages**, and exactly one to the global shared-source page: **74 local links in all**. Extra, missing, repeated or outbound links fail closed.
- Immutable in-memory verification report is SHA-256 fingerprinted, records the R44/R43/R42 provenance chain, and leaves all human, clinical, editorial, identity, QD and publishing flags **false**.

R45 is run by the **existing required stage-13 preflight**, using the private transient R44 ZIP in memory. It does not persist or distribute HTML, install software, create navigation, modify any source, call WordPress or change public pages.

## Adversarial QA

The dedicated Python unittest module exercises many independently named negative mutations: dangerous HTML tags, tags with executable/hidden attributes, external or encoded navigation targets, weakened CSP, modified CSS, missing hold banners, malformed document structure, duplicate or omitted index entries, and **synthetically re-pinned forged ZIPs that still pass R44 byte verification but must fail R45's semantic audit**.

Run from exact checkout:

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The original 13-stage private suite remains mandatory. Native hosted CI must be verified **against the exact PR checkout/merge SHA**; until then test status is *unverified*, not PASS. Ordinary synthetic tests and self-derived machine pins are not independently established third-party source or reviewer trust.

## Remaining external gates

Independent source/claim review of every citation, original reading-scope confirmation, reconciliation of all shared URLs and cross-cluster fallbacks, qualified assessment of consequential water/food/fire/medical/emergency guidance, current live source checks, rendered-browser accessibility/mobile/print QA and independently recorded QD clearance are all still pending. Historical taxonomy labels, including `safety-approved-draft`, are merely unreviewed contributor metadata. An external durable receipt ledger and separately verified reviewer identities/qualifications remain unimplemented.

**No PR merge, public release, CMS/WordPress writes, navigation changes, reviewer approval, safety clearance, or false QD PASS.**

# EX2 published Page 6 versus source candidate — release-parity finding (2026-11-04)

**RELEASE HOLD. Read-only WordPress.com connector inspection + exact GitHub blob inspection.** This is not an anonymous-browser pass, production deployment, QD certification, marketing experiment, or proof of unauthorized publication.

## Critical correction to earlier release descriptions
The connected WordPress production site ID `256784396` reports **published homepage Page 6 last modified 2026-11-02T17:48:13**. Its editor-view HTML already includes `data-fv-home-flagship`, **all seven source-matching chapter targets**, the Franklin folio, **72 sequential public Margins entries (0–71)**, four `/focus/` links and subscription-block markup. Therefore the statement “the seven-chapter experience is wholly unpublished” would be misleading. The existing live CMS page is a WordPress-integrated **variant** of the flagship; the ongoing GitHub seven-chapter candidate and its new admission fixes remain **unmerged/unreleased**. No inference is made about the approval or route by which Page 6 was updated.

## Source identities and comparison
- CMS: WordPress read-only `wpcom_mcp_pages_get(id=6, context=view)`; status `publish`; modified `2026-11-02T17:48:13`. This is CMS markup, NOT a verified anonymous HTTP response.
- Source: PR #992 exact HEAD `bcc984575979c8a7abef833b4dea1eda657b2f14`; `experience2/home-flagship/index.html` Git blob `71511fec93f724a3a2123cd863d654014f030d7e`.
- Freeze: PR #49 remains untouched at `10495883299d53596992c26a8987f629b2904670`.
- Both variants: seven linked chapter IDs present and resolved; Franklin folio present; four Focus hyperlinks in editor/candidate source.
- Published CMS: 72 public Margins entries, native Assembler-integrated chrome and Jetpack subscription markup. Candidate standalone HTML has no embedded Margins/Jetpack, by design: those are composed in the controlled WordPress fixture.
- **Source parity differences:** candidate contains mobile native `<details class="fv-hf__mobile-explore">` plus a dedicated masthead `<a class="fv-hf__mast-cta">`; **neither appears as an element** in published Page 6 editor markup. This is NOT proof of inaccessible mobile nav or missing CTA, because Assembler may own and render the equivalent navigation/CTA outside Page 6. Only a full anonymous browser audit can settle parity.
- WordPress read-only active theme check: stylesheet `assembler`. WordPress screenshot facility returned a public mshots link/status ready for homepage and Focus, but tool limitations prevented independent inspection of screenshot pixels. No mobile image QA, asset-byte measurements or Lighthouse values are claimed.
- Official WordPress.com Assembler theme is downloadable for self-hosted use without a new subscription; the free isolated Playground path remains possible, but it cannot certify WordPress.com Atomic/Jetpack parity.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
**Offer:** already published free 52-page Seven Day Focus Fieldbook; not a paid order.

**Step:** Grok asset → published homepage → source-backed evidence → relevant Focus link → confirmed Jetpack signup → separately verified merchant order/net revenue.

**Blocker:** the live Page 6 implementation and the unmerged branch are *not the same document*. A source-only candidate test cannot certify the existing production variant. On mobile, missing candidate-specific Explore and top Focus elements require review of the separate Assembler template and physical CTA hit-testing, not a blind copy/paste “fix”.

**Change:** this PR adds a no-network, no-write, credential-free **read-only parity audit** consuming an explicitly provided Page 6 editor-view JSON and the exact checkout `index.html`. It refuses unknown page IDs and reports metadata/feature counts only. It never uploads CMS content, subscribers, credentials, source HTML or tracking. The audit makes the source/live divergence explicit before the next release decision.

**Pass evidence:** actual connector/GitHub source inspection: seven linked chapters, 72 sequential live Margins, four Focus hrefs, WordPress subscription-block marker, and exact candidate masthead/mobile differences. Built-in Node self-tests are committed but must be executed in a real checkout; this report does not claim they ran.

**Owner:** homepage QA for anonymous mobile/browser parity; Claude for candidate/editorial integration and approved attribution; Grok/Praxxis for acquisition. No production writes. No paid conversion or net revenue evidence.

## Next must-pass checks, without publishing
1. Anonymous **production read-only** screenshot/DOM test at 320/390/768/1440/1920, verifying Assembler menu, Focus CTA hit-testing, seven chapters, 72 Margins, actual media bytes and accessibility without ever attempting a CMS write.
2. Separate **local Playground/Assembler** candidate qualification with the actual PR #992 stack and genuine Gutenberg saved page; test JS/no-JS, axe, mobile, keyboard/200% zoom, and Chrome Lighthouse. Never silently equate this with production parity.
3. Confirm corresponding Focus signup, consent and merchant order attribution with separately authorized read-only evidence; never infer paid conversion from a link or a subscriber.
4. Keep release HOLD until independent QD, exact CI, founder visual review and controlled release approval.

No affiliate activation, new scripts, production publication, payment or subscription has occurred in this audit.

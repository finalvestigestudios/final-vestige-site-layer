# Seven real chapter anchors: source-grounded release admission (2026-11-04)

**Governance:** isolated companion stacked on draft #1036 at `ba0d7656e9845c7483d1d5305d24c1c550203cfa`. Frozen #49 unchanged. This does not publish, deploy, install, merge, measure visitors or modify WordPress. No paid tooling.

## Reproduced source-check bug
The live browser gate's `CHAPTERS` previously counted `fv-hf-apollo`, `fv-hf-franklin` and `fv-hf-malbone` as three of seven chapters. These are **archive cases within chapter 03**, not destinations in the visible seven-link chapter rail. It therefore failed to require chapter 01, chapter 05 ('Our method'), or chapter 07 ('The observer'). A missing conversion/context chapter could have gone undetected while the test passed. This is a release-harness defect; **not** evidence that the published homepage is missing chapters.

## Read-only published-source evidence
WordPress.com production page ID 6, last-modified value **2026-11-04T14:39:24**. All seven visible rail destinations, in order:

1. `#fv-hf-title` — The find.
2. `#fv-hf-chronicle` — A document changed.
3. `#fv-hf-evidence` — Inspect the evidence.
4. `#fv-hf-inquiry` — Test a claim.
5. `#fv-hf-method-title` — Our method.
6. `#fv-hf-observer` — Test your observation.
7. `#fv-hf-mind-title` — The observer.

Each had one matching `id` and one canonical rail link in raw published page content on this read. **Static content counts alone do not establish browser visibility or usable interaction.** The source preserves all 72 Margins and the separate Fieldbook/Jetpack lead path.

## Change and QA contract
- `CHAPTERS` now holds exactly these seven source-grounded rail destinations; archive images/cases remain audited independently.
- The public anonymous browser gate now rejects missing, duplicated, reordered or incorrectly mapped chapter links; missing or duplicated targets; unlabeled/hidden headings; and empty chapter content, **both with JS and without**.
- A separate real-Chromium representative test uses the committed exported helper at 320/390/768/1279/1280/1440/1920, with JS and no-JS, exercises ordinary hash navigation, and includes twelve explicit negative mutations.
- Never equate fixture results with WordPress/Assembler integration, authenticated staging, axe, CWV or sales.

## Conversion-first decision
**Offer:** free 52-page Focus Fieldbook (lead capture, not a paid order). **Funnel:** Grok social asset → evidence chapter and source proof → existing /focus/ link → confirmed subscription → separately verified paid offer. **Blocker:** an erroneously green chapter test could miss method/observer chapters that establish editorial trust and a relevant next action. **Experiment:** use the revised exact seven-chapter reading/anchor admission across seven widths before considering any new CTA or tracking. **Owner:** homepage engineering (navigation), Claude (analytics/merchant outcomes), Grok/Praxxis (asset IDs and distribution). **Evidence:** source-audited live markup; executable fixture test added; hosted browser and revenue evidence outstanding.

## Remaining HOLD
Native exact-checkout Node Playwright/axe execution, separate private WordPress Playground + Assembler render acceptance, actual anonymous production browser and screenshot inspection, archive-byte transfers, 200% zoom, Lighthouse and field CWV, final asset rights, founder art-direction decision and independent QD/CI. WordPress.com Personal has no native staging clone; free isolated Playground is not host-parity proof. Production, subscribers, and frozen PR #49 remain untouched.

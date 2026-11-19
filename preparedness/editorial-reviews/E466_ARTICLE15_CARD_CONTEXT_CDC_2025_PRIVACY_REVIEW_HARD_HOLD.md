# E466 — Article #15 / Tool #104: child-backpack card is not the same as a minimal public-carry card

**2026-11-18 PT | REVIEW ONLY | HARD HOLD | no publication**  
**US jurisdiction; actual school/childcare, local, state and tribal instructions control.**  
**Sources accessed 2026-11-18; next review 2026-12-18 or sooner upon source change.**

## Authenticated original source and integration

Directly inspected GitHub integration R473 [draft PR #3063](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3063) at head `42f3cfc57b5bd6f065980d40236a42fe1ac4b4a0`, original Article #15 `preparedness/content/articles/family-communication-plan.body.html` blob `8ac8bd7dba3be15d477c15737e54d83364d72527`, metadata `dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3`, original Tool #104 `preparedness/content/tools/family-reunification-card.body.html` blob `be8698ac5d020476ff649d85813810e2000c6f98`, metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`. Both remain drafted, publication draft, human review pending. The 35-original slate and issue #136 source/safety governance remain authoritative. No original file was edited.

## New substantive editorial risk — P1, not a release authorization

Original Tool #104's `A printed card can be lost` warning tells readers **not to put a child's full name or medical diagnosis on a printed card**, without distinguishing a minimal general-carry contact card from a child-backpack/caregiver emergency-information card. Article #15's `Step 2: What the plan should hold` similarly favors minimal content in a children's carry card.

But [CDC's updated Dec. 16, 2025 guidance](https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html), directly opened today, advises a child's backpack and adult wallet card that includes the **child's name, date of birth, relevant medical conditions/allergies, school/caregiver details, parent/guardian and alternate emergency contacts**. [CDC's Dec. 24, 2025 guidance](https://www.cdc.gov/children-and-school-preparedness/before-during-after/index.html), also directly inspected, reinforces that a backpack card can make contact, medication and allergy details available during emergencies and states that parents should not travel to an active school incident until authorities say it is safe. [CDC's 2020 public-domain Backpack Emergency Card](https://stacks.cdc.gov/view/cdc/139829) explicitly distinguishes a child's backpack card and guardian's wallet card; only its catalog record was inspected, not its linked PDF. [FEMA P-1095 Family Emergency Communication Plan](https://www.ready.gov/sites/default/files/2025-06/family-communication-plan_fillable-card.pdf) first page was directly viewed as a PDF screenshot; it contains household/medical and school pickup fields. Its **publication is July 2017**, not June 2025 merely because hosted in a 2025 URL folder. PDF second page was not retrieved; do not make a claim from it.

This is a **purpose/context mismatch**, not evidence CDC mandates public disclosure of every diagnosis. The existing privacy worry is a reasonable editorial concern, but a blanket prohibition can deprive a school/caregiver of useful emergency information. A child-specific backpack card and a casual public-carry wallet card can contain different details. Actual contents, disclosure/access, and school pickup rules are individual/local decisions; involve the child's clinician and school staff where care or communication needs require it.

## Exact editor proposals — all UNAPPROVED

**Tool #104: replace blanket prohibition box, not the underlying form, with:**

> A printed card can be lost. For a general contact card kept in an adult's wallet, a phone number and meeting place may be enough. A child’s backpack card has a different purpose. CDC suggests a child’s name, date of birth, relevant medical/allergy information and parent, school and emergency contacts. Ask the school or childcare provider what needs to be immediately available, how information is protected, and what belongs in its official records. Do not print passwords, government identification numbers or legal custody documents on a casual contact card. No card can authorize pickup.

**Article #15 `Step 2` replace `Keep it on paper, too` editor note with:**

> Keep a paper plan where it can be reached without a charged phone. But use the right version for the right reader. A minimal contact card in an adult’s wallet is not the same as a child’s school-bag emergency card. CDC recommends including child identification and relevant medical/allergy and contact details for the latter. Balance the risk of a lost card with what an authorized caregiver must know, and ask the school where protected records should be kept. A card does not change school-authorized pickup rules.

**Existing tool version selector / nearby copy:**

> Minimal mode is for general public carry. This tool currently has no reviewed child-specific medical/DOB fields; it is not a full implementation of CDC's child-card suggestions. Consult CDC and your school before deciding what to carry.

**Add school-pickup instruction:**

> During an active school emergency follow school and emergency officials, not a card's meeting place. CDC advises waiting until pickup is declared safe. The school determines authorized adults under its policy and applicable law.

## Required gates / conflicts

- E466 proposes **no JS or canonical article/tool mutation**, no substitute child-care product and no unapproved source tokens. Source registry `preparedness/sources/fragments/shelter.json` currently uses older `shelter-cdc-reunification` and `shelter-ready-plan-form` scopes; do **not** silently reuse those to cite the new 2025 CDC pages. Register exact current URLs and reading-scope crosswalk only when editorial copy is accepted.
- Tool #104 claims data remains local, is not transmitted/stored and clears on tab close. Even if its embedded JS appears DOM-only, production WordPress/site-wide injected scripts and privacy claims are **not independently audited** here. Keep separate human privacy/security verification.
- Qualified editor/childcare/accessibility/privacy reviewers determine whether and how to revise the original. A blank, original-design no-JS two-card printable is included in the **local** E466 package as a review proof, not a new or published production tool. It deliberately requests no online personal data.
- Require all original/native build, exact source link/citation, accessibility, mobile/print, production WordPress, hosted CI, independent release checks and human authorization; R473 and editorial branch remain draft / HARD HOLD. No homepage, Investigations, public Preparedness or navigation modifications.

**Media:** original FV HTML/CSS/card layout only, no copied agency graphics, third-party photography or AI documentary images. **Public changes 0; WordPress saves 0; merges 0; no email or commerce.**

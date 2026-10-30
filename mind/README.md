# The Mind & Perception Archive — draft staging package

**Founder direction:** The historical/evidence-first identity of Final Vestige remains canonical. Mind & Perception is a **new complementary editorial pillar**, not a rebrand of the website around an affiliate catalog.

**Current release state:** source-controlled proposal and WordPress HTML-block staging markup only. Not published. No existing navigation, subscriber setting, homepage PR #49, WordPress page, or plugin has been changed by this package.

## Why this belongs

The existing Final Vestige site has 61 published historical investigations; the existing `/free-resources/puysegurs-animal-magnetism-files/` archival research is a real bridge to the psychology/suggestion theme. The 52-page Complete Edition of the `/focus/` Fieldbook is a live, established free resource and uses the existing Jetpack list. The potential partner Inspire3 describes meditation, hypnosis, brainwave and subliminal products. **A seller's description is not evidence that a commercial product works.**

The concept: **The mind is a witness. Not a camera.** Place perception and suggestion among the larger subjects of how humans evaluate evidence, then give visitors an appropriately disclosed optional route to useful resources.

## Proposed page / integration hierarchy

- `/mind/` — The Mind & Perception Archive, proposed new destination; initial page candidate in `page-mind-hub.blocks.html`.
- Perception & attention — sourced, reproducible explainers: change blindness; inattentional blindness; attentional blink; the Thatcher illusion. Unpublished until independently sourced and tested. Promote via relevant TikTok topics.
- History of suggestion — Mesmer; Puységur; the documented history of hypnosis and autosuggestion; documented attempts at mind influence (including declassified records) with explicit proof boundaries.
- Practice & reflection — grounded, optional focus/meditation content. Link to the existing `/focus/` lead magnet rather than adding a second email list.
- Tools under review — product-specific, evidence-qualified guides for relevant Inspire3 offerings; *seller claims* prominently distinguished from independently substantiated effects; commissions disclosed immediately next to earning links.

The existing six editorial post categories remain unchanged. Mind is a new curated **page-level hub** with its own deep-dive routes; any new category, global menu or website publish requires separate approval. The flagship homepage can link to the Mind Archive via a single tasteful experiential module after its historical evidence sequence rather than replacing the central Apollo 1, Archive, Public Record or Focus CTA paths.

## Verified published links used in first hub draft

- Historical source-trail: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- Free fieldbook: https://finalvestige.com/focus/
- Editorial Standards: https://finalvestige.com/editorial-standards/
- Affiliate Disclosure: https://finalvestige.com/affiliate-disclosure/

## Affiliate candidate review, NOT endorsements

See `affiliate-offers.json`. Entries identify only official Inspire3 catalog categories and are **not** product evaluations. Do not fabricate prices, sales, affiliate acceptance, commission rates, product results, testimonial experiences, guarantees or proprietary claims; do not create a cloaked checkout or purchase CTA. Verify each product's approved landing page, exact affiliate URL/terms, price policy, refund policy, independent substantiation and on-page claim scope first.

Editorial/commercial separation: a historically documented claim, a participant's subjective experience, a study result and a seller's product claim are different evidence types. No page may call a specific audio product clinically proven without relevant independent product-level evidence. Medical/mental health or wealth outcomes cannot be guaranteed or implied through testimonials.

Suggested FTC-compliant near-link disclosure for **when an actual earning link exists**: "If you buy through this link, Final Vestige may earn a commission. It doesn't increase your price." Keep the disclosure in the same visual vicinity as the CTA, not only the site's disclosure page.

## Analytics and privacy

- Intended track: visit to Mind hub → topic read → outbound product-guide view → product-page affiliate click. Track Focus CTA separately; a signup is optional, never a purchase prerequisite.
- Add UTM metadata to inbound TikTok links where compatible; keep analytic event names such as `mind_topic_open`, `mind_focus_click`, `mind_offer_outbound` as proposed event identifiers only. No service installation or live tracking changes yet.
- No personally identifying data in events; no click=commission assumption; compare conversion using actual partner reports only if available. Verify applicable partner link-parameter policy before using it.

## QA and safe release

`python -I -m unittest discover -s mind/tests -v` runs basic offline assertions. Run actual WordPress-rendered screenshot/keyboard/320-1920px/reduced-motion checks in a staging environment, source audit and independent QD before making a WordPress page or adding navigation. Keep the published homepage and frozen PR #49 unchanged. After approval, a WordPress *draft* can be created through a separately approved CMS action; publication is a distinct sign-off.

**Owner:** Mind & Affiliate Studio, with homepage art lead and Site QA as independent reviewers. **Tracking:** Issue #171. 

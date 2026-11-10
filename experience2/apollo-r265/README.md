# R265 Apollo: staging-only consent-safe campaign handoff contract

**Source of truth:** Experience 2.0 #150, conversion #820, charter #818. **DRAFT / HARD HOLD.** Does not modify homepage PR #49, Research Desk PR #158, historical NASA evidence, WordPress settings, merchant destinations, social posts or live analytics.

## Risk discovered and corrected during review

An initial test-only approach copied inbound Grok `utm_*` fields onto an *internal* Apollo article link. **This approach was rejected before release**: official GA4 guidance says campaign fields can affect event-scoped attribution even when they do not start a new session. The current code **never modifies any href**. It validates the inbound standard Grok campaign quartet and sets optional **DOM-only `data-fv-apollo-campaign-*` hints** on the existing free-article CTA for future integration review by Claude. No beacons, cookies, network requests, storage or event handlers, and no purchaser attribution claims. These DOM hints do NOT establish a qualified visitor, a click, a signup, a purchase or revenue. Claude must review current analytics/consent and prefer native session-scoped campaign measurement and already-approved CTA event hooks.

## Scope and fail-open contract

Only one original link is eligible: `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/` under `#fv-apollo-reading-bridge` within a single `.fv-apollo-atlas`. `utm_source` must be youtube/tiktok/instagram/facebook/pinterest/x/bluesky, `utm_medium=organic_social`, lowercase `utm_campaign` token length 3–64, and case-sensitive `utm_content` asset ID length 3–80. Unknown or duplicate UTM keys fail closed for optional metadata; the original link **always works** with and without JS. Mixed-case IDs from Grok's actual TASK-008 are supported, though no Apollo video asset is verified. Source-pinned PHP uses WP hook 30 and checks real R224/R262 preflight before optionally enqueuing the JS. Extra HTML uses no NASA endorsements or invented geography.

## Local source-proven QA

The code in `qa/committed_smoke.py` executed with 20/20 Chromium checks. An extended separate test in the evidence bundle executed twice, 37/37 cases each, with byte-identical receipts and four screenshot pairs. Tested widths 320, 390, 768, 1440, 1920, JS on/off, keyboard SourceDrawer, native no-JS disclosure, valid/rejected campaign inputs, repeated injection, tampered optional JS integrity and intentionally bypassed allowlist. Every test retained 55 NASA source hyperlinks, 31 internal fragments, one unchanged free investigation CTA, zero merchant links, zero observed external requests and no detected horizontal overflow. Protected R238 manifest SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`; original generated HTML SHA-256 `50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6`. Extended stable receipt SHA-256 `8a1b51d9580827e9fd858f7748004f0150d5083f0e9f3848f544fccb114d0a99`.

Run: `python experience2/apollo-r265/qa/committed_smoke.py fixture/sealed-r238 experience2/apollo-r262 experience2/apollo-r263/qa/wp-real-source-sequence.php`. The extended bundle includes its own executable runner and screenshots.

**Not tested:** real signed-out HTTP/CSP (browser localhost/navigation admin-blocked), installed WordPress/Assembler, verified axe-core, screen readers, browser UI zoom, actual field LCP/CLS, hosted CI/independent QD, actual merchant settlement or paid conversions. A browser `set_content` PASS is not a production acceptance result.

## Commercial bridge (proposal only)

High-intent Grok Apollo long-form visitor → source-verified Atlas → free original investigation → *after the article only*, optional relevant Final Vestige [Mini Museum guide](https://finalvestige.com/mini-museum-history-collectibles/). TASK-008 describes a publicly posted guide with proximate disclosure, but current Awin Mini Museum acceptance, authorized payable tracking, merchant settlement, refunds/fees and verified net revenue remain unconfirmed. Do not imply Mini Museum objects are Apollo flown artifacts. NASA imagery/branding and deceased astronauts' likenesses need independent promotional-rights review; source links alone do not grant endorsement. Never add the paid continuation until authorized.

**HARD RELEASE HOLD:** verify actual Apollo Grok asset ID and landing route; Claude analytics/consent and merchant audit; installed WP, verified axe and independent screen-reader acceptance; actual browser zoom; HTTP/CSP, field CWV, hosted CI/QD; inherited R198 discrepancy; rights; founder release authorization. Never merge/deploy on this evidence alone.

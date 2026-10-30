# Conversion and privacy instrumentation — no tracking active in this draft

## Funnel and hypotheses
- `mind-article` → `zen12-guide` → `qualified merchant outbound` → merchant-confirmed purchase, if/when partner attribution reporting becomes accessible.
- A: the fully sourced guide without film. B: same page + optional click-to-play 40-second film, accessible transcript. No claim that B converts better before randomized measurement.
- Do not show variant B until the 40-second video is actually produced, rights-cleared, hosted, captioned and performance-tested. Never auto-play, load third-party players before user consent or with sensitive tracking.
- Both variants must have identical source text, offer, disclosures and accessible navigation, so the video is the main manipulated feature.

## Proposed event schema (not installed)
```json
{"event":"fv_offer_outbound","page":"zen12-guide","slot":"zen12-primary","channel":"tiktok","variant":"text","consent":"site-approved","ts_bucket":"2026-10-30"}
```
- Approved `page` enum: `zen12-guide` only; `slot` enum: `zen12-primary`, `zen12-secondary`.
- Approved `channel` enum: `tiktok`, `youtube`, `email`, `organic`, `direct`, `other`; no raw referrer URL, query strings, names, emails, IPs, user-agent fingerprint, cookies or hashed unique identifiers.
- Click events should be best-effort and never delay navigation. Client-side collection should only be enabled with legal/privacy review and an endpoint that discards transport IPs in persistence/logs; otherwise use aggregate privacy-preserving site analytics and merchant aggregate reports.
- Avoid cross-domain fingerprinting, PII forwarding and link cloaking. Do not use raw individualized outbound click IDs unless partner terms, law and privacy notice explicitly permit it.
- Do NOT use URL parameters that could leak customer identity or sensitive content.
- Confirm the publisher's privacy policy accurately describes analytics before activating instrumentation.

## Quality metrics and caveats
- Primary: eligible affiliate outbound CTA clicks divided by guide sessions once links are legitimately active.
- Business outcome: actual merchant-confirmed purchases and net commission (if reported), never imputed from outbound clicks.
- Guardrails: guide performance, free-fieldbook clicks, bounces, scrolling, accessibility, user complaints and editorial credibility.
- Do not run a statistical A/B claim with two subscribers. Decide sample size and stopping rule before exposure; optimize for practical lift only after enough qualified traffic arrives.
- Static `data-fv-offer-slot` and `data-fv-offer-state` markers assist QA without tracking people.

## Review checklist
Approval from partner confirmed; exact allowed deep-link destination known; terms allow pre-sell and newsletter marketing; explicit commercial disclosure; accessible tap targets; price not hard-coded; preview at 360/390/768/1440/1920; network weight and CWV measured; no external SDK; no third-party media embed; no broken product links; official checkout privacy and newsletter opt-in explained if linked as a free-offer path.

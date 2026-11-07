# Dispatch R176 — an honest Zen12 offer email and the WordPress transport proof gap
**Date:** 2026-11-06 PT (source observations as of 2026-11-07T03:28:57Z)  
**Owner:** Dispatch Campaign Studio, Issue #174. Companion: Mind & Affiliate #171, Focus #129, conversion #820.  
**Status:** SOURCE-CONTROLLED REVIEW DRAFT. NO SEND, NO WORDPRESS WRITE, NO APPROVED AFFILIATE LINK, NO AUDIENCE CONTACT.

## Why this work is different from earlier sprints
PR #175 already established the original six newsletters; PR #201 created independent per-edition gates; PRs #1290/#1296/#1328 implemented received-message safety and disclosure checks; PRs #1315/#1322 address cross-route subscriber status and replay-safe transitions; PR #1334 covers proof-grade paid attribution; PR #1341 source-locked all six original manuscripts and finally executed the original Python suite. **Do not build duplicate trackers, change those originals, or substitute this optional Issue 03 without founder selection.**

R176 changes the conversion proposition *in the copy itself*: it separates a feasible twelve-minute habit from Zen12's much stronger advertised time-equivalence claim; provides a free three-day observation exercise with no fake clinical results; names the seller's exact Premium file inventory; asks for actual buyer-relevant checkout and refund evidence; and places a commission disclosure immediately beside a visibly inactive single guide CTA. The practical alternative is credible even if no affiliate contract ever materializes.

This is not proof of customer demand, partner acceptance or expected earnings.

## Three observed distinctions that determine whether the funnel is trustworthy
1. **Stored subscription blocks ≠ guest experience.** Read-only WordPress page #523 (/dispatch/) contains the Jetpack Subscribe block in edit markup. Its view-context API output has a Subscribe link but no `type="email"` input. Page #1579 (/focus/) has an email input in view output, but its edit source still contains `if(q){if(bad.indexOf(q)<0){show();}}`: query-string-driven gift display, not provider-backed confirmation. Neither API representation is a signed-out browser test. Claude/Site QA must compare the actual visitor flow and fix the false-success treatment before reporting confirmed_signup.
2. **WordPress subscriber totals ≠ eligible inboxes.** At 2026-11-07T03:28:57Z Jetpack reports total 3, confirmed 3, unconfirmed 2, suppressed 0; **do not add these categories** or assert 3 reachable email recipients. Welcome text contains the 52-page PDF link, but no received welcome proof was found by a bounded search of the linked mailbox. Absence of a match cannot show delivery failure to every subscriber.
3. **HTML prototype ≠ Jetpack message.** The existing newsletter is ON, default new-post emails OFF, content FULL, sender display Final Vestige Studios and no recent dispatched sends. Jetpack documentation says it emails **newly published posts**, not pages or Markdown files. An offline HTML reviewer in GitHub does not acquire a publishable Jetpack email subject, inbox preheader, unsubscribe footer or mailing address by itself. A native `Preview email` inside an unpublished **post editor**, with send-toggle OFF and without publishing or using `Send test email`, is the minimum non-sending visual QA. Actual email MIME, true inbox preheader and functional unsubscribe remain unverified. We will not create even a draft WordPress post in this workstream without the required separate authorization.

## Exact seller/source claim audit (not an endorsement)
| Statement | Provenance | Newsletter treatment |
| --- | --- | --- |
| Premium lists 12 levels, 48 MP3s, four styles | Seller's sales page, live review November 6 | Attributable inventory description; verify again before release |
| A twelve-minute track provides the benefits of an hour of meditation | Seller's prominent opening claim | Explicitly **not independently established**; do not reproduce as FV fact |
| Specific brainwave entrainment, health, attention and creativity effects | Seller's marketing descriptions | No causal/effectiveness assertion by FV; product-specific adequate substantiation not established |
| One-year refund guarantee and public $87.99 Premium price | Seller display, not authenticated checkout or executed refund | Omitted from reader email until total cost/refund terms verified; no artificial deadline |
| NIH/NCCIH evidence for meditation generally | US federal research summary; outcomes vary by practice and study | The research does not validate Zen12 specifically |
| Named FV approved as Inspire3 affiliate, permitted to promote by email, approved tracking URL or creatives | Public affiliate portal is not account-specific | **UNKNOWN/NOT VERIFIED**. Leave the offer CTA inactive |
| FV independent Zen12 buyer guide is live and founder-approved | Mind Studio draft work remains unpublished | **NOT LIVE**, no active guide link |
| Affiliate click, checkout, verified affiliate commission | No independently documented paid settlement | **NOT REVENUE** |

Official seller: https://zen12.com/  
Official partner program: https://affiliates.inspire3.com/  
NIH/NCCIH general research: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety/  
FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business  
Jetpack native preview and POST-only sending: https://jetpack.com/support/newsletter/  
Jetpack subscription confirmation: https://jetpack.com/support/subscribe-to-a-site/

## Reviewer's checklist: legally fail closed
- Four editorial vs two reserved commercial issues remains unchanged. This Issue 03 variant is a **candidate**, not an approved replacement.
- **All six emails require legal primary-purpose classification before release**. An editorial wrapper or newsletter membership alone does not establish exemption from CAN-SPAM: the FTC describes coverage of promotions on commercial sites and recognizes that a message's primary purpose controls. Treat physical publisher postal address, truthful headers/subjects and effective opt-out as campaign-wide release proof, with extra affiliate disclosures in issues 03 and 05. Legal review is not automated legal advice.
- Final Vestige-specific valid address (street, registered PO box or qualified private mailbox) is not established. The postal address of Automattic or Inspire3 **cannot** substitute for FV's. Confirm proper site publisher identity without showing subscribers' addresses.
- Native email preview must show exact visual footer and no hidden disclosure. Real received message and unsub functionality still unknown. Visual previews cannot prove backend processing.
- A true preheader field in a Markdown draft is not evidence that an inbox will show that text. Only a future authorized provider/client preview can validate it.
- Commission disclosures immediately adjacent to commercial guide CTAs. A general affiliate disclosure page alone is insufficient. Disallow hidden, remote and color-invisible disclosures.
- No active affiliate links, no price assertions from incomplete checkout, no unsupported medical performance claims, no test sends, no new mailing list, no CRM exports, no production analytics script.

## Campaign attribution and consent contract (documentation only)
When approval and real reporting exist, track qualified unique social **asset IDs** via Grok's `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=asset_id`. Landing visits and CTA clicks are diagnostic. Provider-authoritative confirmation is the only acceptable `confirmed_signup` source; deduplicate its stable opaque proof ID across batches and do not publish personal identifiers. Welcome receipt requires delivery evidence separate from the configured text.

For future first-party newsletter guide clicks, propose `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_mind_2026_11&utm_content=issue_03` only on a **verified live first-party guide after founder approval**. Do not add subscriber-specific parameters or assume the original Grok asset can be joined across devices. The guide may offer one permitted direct earning link after Mind verifies merchant terms. Count a *customer* and realized net revenue only from verified paid order/partner settlement with fees and refunds; 7/30-day cohorts and small-N caveats. The key revenue-per-1000-qualified-session KPI is currently **NOT COMPUTABLE**.

## Prioritized OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER
| Offer/funnel | Blocker | Change and pass condition | Current status | Owner |
| --- | --- | --- | --- | --- |
| Fieldbook → confirmed lead | `?subscribe` success UI not authoritative | Signed-out human-visible /focus/ and provider confirmation, with invalid-query adversarial case | FAIL risk observed / real visitor UNKNOWN | Claude / Site QA |
| Dispatch → new lead | API view differs from stored native Subscribe block | Guest/browser 320/390/768/1440 and keyboard test, verified provider transition | NOT TESTED live | Claude / Site QA |
| Confirmed signup → PDF | Configured welcome not received/checked | Permissioned provider-state and pre-existing received-message evidence; download valid PDF | UNKNOWN | Dispatch / Site QA |
| Existing subscriber → editorial reply | Native email rendering/footer/preheader unverified | WordPress unpublished-post **non-sending preview**, valid FV address and native opt-out | HOLD | Dispatch / Founder |
| Zen12 → qualified buyer | Named merchant acceptance, email marketing and guide unknown | Written permissions, current merchant terms, LIVE independently sourced guide, no unsupported claims | HOLD_MERCHANT | Mind / Founder |
| Buyer → paid customer | Transaction/fees/settlement attribution absent | Independently confirmed paid orders + refunds/fees + qualified denominator | NOT COMPUTABLE | Commerce / Praxxis |

## Verification performed
- Native CPython campaign baseline re-executed locally from the earlier exact source-lock QA bundle: **6/6 passed** on this run (original #175 source files and tests; package was previously byte-matched against GitHub).
- Native Node reference board regression from prior local R175 bundle: **12/12 passed** when invoked from its documented working directory. Initial attempt from the wrong current directory produced two fixture path errors; rerunning correctly passed. This proves nothing about native Jetpack.
- New R176 `test_r176.cjs` syntax parsed in a V8 function, then **32/32 original and new committed-source checks passed with Node-like filesystem/assertion compatibility shims** against live connected GitHub-read file content at the branch head. This is *not* a claim of native Node or browser execution of committed R176 artifacts.
- R176 source files are **GitHub draft-branch only**. No merged/published site change; no contact with subscribers, test emails, or merchant login.

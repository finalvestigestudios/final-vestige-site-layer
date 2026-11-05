# Dispatch R144 — consent to settled revenue (DRAFT / UNSENT)

**2026-11-05 | Issue #174, Mind #171, Focus #129, Conversion #820**. Stacked only on Dispatch R143 #1132 at 13ed8e8d889579c1363591fc717affae59250d33. Do not modify master campaign #175, per-edition preflight #201, frozen homepage #49, or any production site.

## Read-only WordPress findings: updated at 2026-11-05 19:32 UTC

- Jetpack Newsletter ON, new-post automatic email OFF; mode **FULL**, sender Final Vestige Studios, reply-to no-reply. Five recent published posts are **never_sent_opted_out**.
- Dashboard: total 3, confirmed 3, unconfirmed 2, suppressed 0, paid 0. **Nonadditive categories**, no person-level recipient or consent proof.
- Rolling **imported_last_24h = 0**, compared with R143's 1 just an hour earlier. This is NOT evidence someone deleted a subscriber or the previous metric was false: it is a rolling-period counter and needs independent history/status reconciliation. No import performed by Dispatch.
- Different WordPress followers feed: 3 WordPress.com followers, 0 email followers, 0 comment followers. These are not extra people to add to the 3 reported newsletter subscribers.
- The 52-page Focus Fieldbook URL is configured in welcome, not proof it was received or the file accessed. Signed-out form/modal, final native preheader, actual commercial footer, unsubscribe and welcome receipt are **UNVERIFIED**. Current FULL mode invalidates assumption that older excerpt mocks reflect actual emails.
- WordPress /dispatch/ and /focus/ pages and Editorial Standards were inspected read-only. Anonymous public web fetch was unavailable; no actual signup was tested.

## One high-intent audience, one *conditional* offer

Audience hypothesis: a viewer from a specific, actually published Grok perception/attention video who independently confirms signup to receive the free Fieldbook and then wants to compare a meditation-audio product. **Zen12 Premium** is the only conditional product candidate for this pilot. Separate commercial Issue 05 reserves Hypnosis Live **Total Focus**; it is not swapped into this one-offer pilot. Four of the six original letters stay editorial, two commercial slots still blocked.

Non-sending progression for eligible consented readers (NOT scheduled/automated):
1. Existing native Jetpack opt-in → existing Fieldbook welcome. A signup success page, follower count or email-open is **not confirmed consent**. Do not duplicate confirmation or resubscribe readers.
2. Optional Issue 01 perception experiment → a published first-party change-blindness article, not a second Puységur link. R142 draft remains an OPTIONAL alternative awaiting editorial approval.
3. Issue 03 only AFTER named merchant and founder permission → original free 12-minute routine/evaluation guidance and ONE approved, live FV Zen12 Premium buyer guide CTA. Adjacent disclosure: “If you buy through a link on the linked guide, Final Vestige may earn a commission.” Do not claim seller's 12-min = 1-hour equivalence has independent scientific support; not a product endorsement until rights and claims checked.
4. Issue 06 log/reflection → direct Fieldbook PDF for returning readers, avoiding a second signup. R142 alternative NOT yet the canonical six letters.

No inferred native Jetpack segmentation, test emails, email trigger automation or separate subscriber platform.

## Evidence-first 7/30-day cohort audit: new source file, not new site instrumentation

The Python audit is offline READ-ONLY. It does not call the web, WordPress, email or merchant systems. It requires source-linked **reviewed bot-filtered qualified human session exports**, Grok asset IDs and agreed UTMs (utm_source actual platform; utm_medium organic_social; utm_campaign mind_pilot_2026_11; utm_content immutable Grok asset_id). Links must be QA'd before any public posting by Grok/Claude. Subscriber-level record matching must respect consent and privacy; no subscriber addresses, IPs, cookie IDs, usernames or raw tracking links are accepted.

A true confirmed_signup requires native provider evidence, not button click/success screen. A true paid_order requires independent purchase report, not CTA/affiliate click. Actual **net realized revenue** requires an independently reported settlement for the order minus documented fees/refunds. If qualified sessions, orders, or settlement evidence is incomplete, report NULL/NOT COMPUTABLE, **never $0 or a fake conversion rate**. Only synthetic tests contain example revenue; no real customer data or payment IDs in this branch. Distinguish separate 7-day and 30-day cohorts, tiny-sample caution, unverified affiliate account and prior fulfillment. Do not create a duplicate measurement script; Claude keeps production instrumentation and Grok keeps creative and platform inventory (Drive TASK-008).

Run: python -I -m unittest discover -s dispatch/campaign-2026-mind/r144 -p test_settlement_truth.py -v
Run: python dispatch/campaign-2026-mind/r144/settlement_truth.py dispatch/campaign-2026-mind/r144/current-nonmeasurement.json 2026-11-05T19:32:10Z

## OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER

| Offer and step | Blocker | Candidate test | Required pass proof | Owner / gate |
| --- | --- | --- | --- | --- |
| Free Focus Fieldbook → confirmed lead | native provider consent, import provenance, signed-out form unknown | read-only native statuses + real signed-out browser | genuine eligible opt-in + actual form accessibility, no PII leaked | Dispatch / Claude / QA — HOLD |
| Welcome → Fieldbook | configured ≠ delivered | authorized already-received email + PDF check | received welcome and usable PDF | Dispatch — HOLD |
| Newsletter → relevant story/guide | FULL email rendering, preheader and footer unknown | native **non-sending** WordPress preview | subject, primary CTA, near-disclosure, valid FV physical address + functional unsubscribe and no placeholders | Dispatch / Claude — HOLD |
| Zen12 Premium → paid customer | named FV affiliate approval, email permission, approved live guide, earnings URL and checkout unknown | Mind owner obtains private permission and exact buyer terms | written channel-specific permission, links, guide and signed-off release | Mind #171 — HOLD_MERCHANT |
| Verified source → net revenue | no human sessions/settled merchant payments/fees/refunds provided | privacy-safe report reconciliation | source-linked settled orders, refunds and qualified denominator | Praxxis / Claude / Commerce — UNKNOWN |

Sources: https://finalvestige.com/editorial-standards/ ; https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus (33 minutes / 47MB distinct from Hypnotize Yourself); https://affiliates.inspire3.com/ (public program is **not** named FV acceptance); https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

FTC commercial mail requirements include accurate sender/header and nondeceptive subject, appropriately identified ad, **valid publisher postal address** (not Automattic's or Inspire3's address), and a functioning clear opt-out mechanism. Subscriber permissions and commercial primary-purpose status also require review. None has been verified in a genuine Jetpack received FV commercial email. **ALL SIX HOLD_UNSENT, COMMERCIAL #03/#05 HOLD_MERCHANT**. No emails/test emails, publishes, subscriber imports, settings writes, merchant activations, social posts, spending or unapproved release.
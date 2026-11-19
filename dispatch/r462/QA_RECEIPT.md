# R462 QA receipt — exact GitHub files, provider observations, and release holds
**Execution:** November 18, 2026 Pacific. New files restricted to `dispatch/r462/`; stacked parent PR #3076 at `d9fa7a7b6985c5905b66d70da07dccf7d7a90de3`. All original Issue #174/PR #175 manuscripts and the original tests retained unchanged.

## Actual validation performed, with honest limits
1. **Original master suite reviewed at immutable PR #175 head** `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Exact `test_campaign.py` Git blob `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`, manifest blob `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`, and all six original manuscripts independently fetched via GitHub connector. **6/6 original Python test CONDITIONS ported and checked in V8 passed. This is NOT native Python execution; native container GitHub DNS failed.** Do not claim `python -m unittest` was executed this run.
2. **12/12 local precommit editorial-asset assertions passed:** one principal CTA, 4+ references, exact subject/preheader, email-safe structural table, legal placeholders, no remote pixels/scripts, no affiliate URLs, no false approval. Original book/consent logic sanity checked.
3. **24/24 V8 classifier behavior/adversarial assertions passed** before commit, including PII input rejection, duplicate-category prevention, partial provider results, invalid counts and unresolved lead status. Subsequent typo correction fixed `COHORT` token consistently in code + tests.
4. **34/34 postcommit exact-GitHub-source static assertions passed** using all six R462 initially committed files; their supplied GitHub blob identities were:
   - `ISSUE02_RESEARCH_OPTION.md`: `46a6f2c02a0cfc5263b968aecbad6609b5646922`
   - `ISSUE02_OFFLINE_REVIEW.html`: `6d3210fbbbc76210d6bffe98f86a9e6f13325f30`
   - `ISSUE02_OFFLINE_REVIEW.txt`: `0192041ca077dcb4cb7ecb6ede623587066c171f`
   - `provider_crosswalk.mjs`: `cf224c33c7bcbfb4748f2c7a3b7139d6c70179f4`
   - `provider_observations.json`: `928816931dbf7bf023522004e4407916bb52aed4`
   - `test_provider_crosswalk.mjs`: `8d67a7a9d6b14c4a0aff641fe1c449b0c4286711`
5. **200/200 additional deterministic V8 property checks passed on the independently fetched exact committed `provider_crosswalk.mjs` source**, dynamically executed from the fetched text. Cases: 100 count combinations never manufacture leads; 50 category contradictions detected; 50 unsafe PII fields rejected. The committed nine-case `node:test` file has NOT been executed using native Node. V8 checks are not a replacement for `node --test` in a repository checkout.
6. **Authenticated WordPress and Gmail READ-ONLY:** WordPress exact news settings `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `from_name=Final Vestige Studios`, `reply_to=no-reply`, five `never_sent_opted_out` posts. Three `Subscribed` email-subscriber rows; two separate `Not confirmed` rows; 0 Reader under `Stats Subscribers`. `Stats Followers` reports email0/Reader3, `partial=false`. Source inconsistency is **not resolved** by our classifier. Targeted Gmail search found one old Refersion pending notice, no genuine welcome or partner approval in the inspected search results.
7. **Research checks:** BnF original edition (1784 + 1785); CIRCEE 1784 primary context; 2019 Crabtree paper; 1784 commission report; official Zen12 /about and separate promo funnel; official Hypnosis Live FAQ and Be More Centered SKU. The newsletter copy treats seller assertions as unproven product-specific benefits; no prices, refunds, paid links, or invented efficacy in subscriber artifact.

## NOT verified / requires explicit owner action
- **Native Python at PR #175 exact head:** Not run this sprint due inaccessible GitHub raw/clone from container; latest master code unchanged, but this run's mirrored checks alone do not satisfy native execution.
- **Native Node at R462 exact head:** Not run (committed `node:test` file needs real Node execution on a checkout).
- **Browser/email accessibility:** Source-oriented HTML checked for tables/alt issues/no remote images; neither browser multi-viewport tests, real email client, screen-reader audit nor actual Jetpack non-sending Preview run. No assertion of WCAG certification or delivery.
- **Publisher postal address / unsubscribe:** placeholders intentionally retain `HOLD_UNSENT`. No proof that WordPress appends a legally adequate address or allows working opt-out in the final actual email.
- **Marketing authorization:** no accepted named partner, email-specific terms, issued earning URL, live approved warm-up guides or final checkout proof.
- **Monetization:** no independently documented settled orders and no verified qualified-human-session denominator. KPI net revenue per 1,000 qualified humans is **NOT COMPUTABLE** (not zero).
- **Consent:** no new external human confirmed_signup transition or delivered welcome established. Provider categories remain inconsistent.
- **Original founder copy:** not modified. R462 Issue 02 optional candidate is not licensed for production without founder approval.

## Release decision
**HOLD_UNSENT for all six original editions and the optional Issue 02.** No emails, including test sends; no WordPress posting/settings/list imports; no subscriber contact or PII export; no Grok content edits/posts; no affiliate activation; no PR merge; no spending. Homepage PR #49 preserved. Record final draft PR HEAD and this QA receipt in Issue #174; aggregate, non-PII handoff to Issues #171, #129, and #820.

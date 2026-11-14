# Dispatch R343 — canonical six-issue offline email rendition (NO SEND)

**Scope:** Source-faithful, non-sending reviewer of the founder's ORIGINAL six manuscripts in [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at original head `d57ccdba3aee8f065e143e101c2945f4f3d01647`. This branch is stacked on [draft PR #2408](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2408) @ `2c012a9db0fbf58852d0a9733dd45061a2d6c61b`. Companion independent gating branch [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) is NOT merged or duplicated. Canonical work item [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), commerce ownership [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), business #820.

## What this adds, and what it does NOT add

- **Twelve new source-preserving assets**: six self-contained, table-based, inline-styled, responsive-width *static offline* HTML reviewer files and six accessible plaintext companions; [reviewer index](preview/reviewer-index.html). All six are `HOLD_UNSENT`; #03 and #05 additionally `HOLD_MERCHANT`.
- Original manuscript bodies, subject and proposed preheader strings **not rewritten, chosen, scheduled, adopted or made into WordPress drafts**. Review preview HTML is an interpretive rendering of Markdown, not the provider's actual email. It has conspicuous offline warnings and explicit unavailable legal placeholders. It is **not valid send-ready HTML**.
- Source blob identities and explicit, false-by-default release gates in [source_and_gates.json](source_and_gates.json). No email addresses, affiliate tokens, tracking credentials, real visitor details or invented revenue values.
- 64 structural/safety assertions performed in an isolated JS environment before commit (not an email client or WCAG certification). Original native Python PR #175 suite independently rerun **6/6** after its 8 Git blob SHAs were checked against exact `d57ccd...` originals. Separate reproducible offline-generation QA has **32 native Python tests**, independently **not** a source-identical test of the JS generated GitHub previews. Review both separately.
- No WordPress edits, email/test send, subscriber import, social post, affiliate link, new platform/paid service or merge.

## Preview limitations

Open `preview/reviewer-index.html` locally or inspect the repository's six HTML/text pairs. Browser HTML is **not** proof of Jetpack rendering. WordPress's **Preview email** is a native UI feature distinct from **Send test email**. Actual header/preheader rendering, footer, unsubscribe, recipient eligibility and welcome delivery remain unknown. The `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` strings are *unacceptable for sending*. The merchant-guide destination in issues 03/05 is explicitly disabled, not a link. The website-native public URL /focus/ does not prove signup or welcome delivery.

## Hard-hitting source-copy decisions

| Original issue | Strong element | Conversion/trust risk | Founder-pending decision |
|---|---|---|---|
| 01 Perception | Historical identity and careful skepticism | 01 and 02 share same Puységur guide CTA; opening does not offer a specific study | Compare optional 01 change-blindness source draft from R340, preserve original until approval |
| 02 Puységur | Sources-over-certainty framework | Duplicates 01 destination, less reason to click | Consider R332 Franklin orchard source-centered draft, source-check carefully |
| 03 Zen12 | Free routine before asking for money | Main guide URL NOT LIVE, affiliate acceptance/email channel missing, seller meditation equivalence unsupported | Merchant HOLD; single product-specific Zen12 guide only after Mind clearance |
| 04 Apollo 1 | Genuine historical counterweight | Subject "Fourteen seconds" is ambiguous/insufficiently sourced against precise event timestamps | Prefer source-checked R337 alternative for founder review; do NOT auto-adopt |
| 05 Hypnosis | Useful buyer checklist, clear commission warning | Names entire Hypnosis Live catalogue rather than individual Total Focus SKU; missing refund qualification | Compare R336 Total Focus alternative, verify updated FAQ and precise terms |
| 06 Fieldbook | Teaches evidence logging | Emails existing subscribers back to acquisition page with a downloadable PDF; avoid counting re-signup as new lead | Consider R340 source-research guide alternative; keep original until approval |

**Editorial preservation:** Four non-commercial issues / two commercial candidates, historical evidence identity maintained. These are editorial recommendations only; none adopted.

## Actual production constraints as of 2026-11-14 01:36 UTC (read-only)

Newsletter ON; new-post default email OFF; **full** content; sender display Final Vestige Studios; reply-to no-reply; Fieldbook link configured in welcome. Counts total=3, confirmed=3, unconfirmed=2 are overlapping; separately WordPress.com followers=3, direct-email followers=0. **Actual send-eligible recipients unknown.** Recent five published posts explicitly opted out of email; `site_can_send=true` is infrastructure capability, not campaign authorization. Never add the counts or equate PDF access with confirmed_signup.

Published [Dispatch](https://finalvestige.com/dispatch/) and [Focus](https://finalvestige.com/focus/) remain on the existing signup stack. The Focus page exposes the PDF directly and asks for confirmation after the form; the completed welcome in any inbox is NOT verified. No live rendering/sending was performed.

## Applicable external references (not account-specific authorization)

- [WordPress native email appearance / preview](https://wordpress.com/support/newsletter/email-appearance/); sender remains donotreply@wordpress.com, preheader independent control not verified.
- [FTC CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business); valid actual publisher physical address, conspicuous identification when commercial, and functioning unsubscribe are essential. Automattic/Inspire3's postal address is not Final Vestige's.
- [Zen12 official seller page](https://zen12.com/): “an hour in 12 minutes” and health/focus benefits are SELLER claims, not independently validated effects for that product.
- [Hypnosis Live Total Focus official page](https://hypnosislive.com/mental-skills/total-focus): 33-minute, 47 MB seller-described recording, currently displays $17.95 as seller price (**not** locked/recommended pricing).
- [Hypnosis Live FAQ](https://hypnosislive.com/faq): 14-day refund language includes a maximum five sessions per year; terms may change.
- [Public Inspire3 affiliate portal](https://affiliates.inspire3.com/): marketing and commission pitch **does not** establish an FV affiliate account, issued earning link or permission to promote via email.
- [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/).

**Required before any future sending:** explicit final founder campaign sign-off; authentic provider-recipient consent/eligibility; actual Jetpack preview and authorized received-email/opt-out/postal proof; merchant-specific rights and live guides for 03/05; audited subject/claim/CTA; verified event and independently settled order evidence for commercial KPI. Until then every send is **HOLD**.

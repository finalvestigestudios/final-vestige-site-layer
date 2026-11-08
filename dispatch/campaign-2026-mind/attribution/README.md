# The Dispatch — offline aggregate attribution (UNSENT)

**Status: isolated draft, no network, no sender, no tracking, no publication or product link activation.** Parent PR #201, companion issues #174 and #171. The original six-edition (4 editorial / 2 commercial-review-pending) campaign, existing Jetpack list, 52-page Focus Fieldbook and homepage PR #49 are unchanged.

## Motivation
A dashboard can easily misrepresent newsletter recipients as delivered emails or total link clicks as unique clickers. It can also infer affiliate purchases from mere product clicks. This tool refuses these shortcuts and treats every metric as unobserved until an independently approved, verified, aggregate-only export is entered. The current WordPress site reports zero sends and contradictory subscriber summary total=2/confirmed=2/unconfirmed=2. **No real sales or click rates have been measured.**

## Operator instructions
Use only AFTER the owner has explicitly approved a real email and its audience, preview, legal footer and opt-out; after a qualifying merchant offer also requires email-channel partner authorization and a published evaluated guide. Run the following offline (no WordPress/GitHub API writes):

    python -I -m unittest discover -s dispatch/campaign-2026-mind/attribution/tests -v
    python -I dispatch/campaign-2026-mind/attribution/attribution.py --html /tmp/dispatch-report.html
    python -I dispatch/campaign-2026-mind/attribution/attribution.py --proposed-urls
    python -I dispatch/campaign-2026-mind/attribution/attribution.py --aggregate-csv /private/verified-aggregates.csv --html /private/dispatch-report.html

The default report states "Not measured" for all six draft editions, without invented zeros. The CSV template contains only a header, not synthetic recipient records or customer data. Never upload observed reports, addresses, raw exports, IDs, IPs, tokens, receipts, or personal data to GitHub.

### Source-of-truth mapping
- wp_recipients: actual Jetpack Stats > Subscribers > Emails recipient count; NOT delivery confirmation. https://wordpress.com/support/stats/view-subscriber-stats/
- wp_unique_email_clickers: **uniquely identified email clickers** if available in a specific send's first-party report; if only total clicks are shown, DO NOT mislabel them and leave this number unreported.
- first_party_page_views: WordPress page visit totals across all referrers, not necessarily this email's readers.
- outbound_merchant_clicks: only from an approved future first-party aggregate (currently NOT installed).
- verified_merchant_purchases: only independently reconciled merchant affiliate reporting, never inferred from email/site clicks. A private opaque proof reference is required.
- send_approval_ref: external founder approval record. A string in this CSV does not grant approval; a reviewer must verify it.
- Opens are deliberately excluded; their measurement is not reliable enough to substantiate conversion in this tiny audience.
- Percentages are descriptive only at N >= 20. That threshold is NOT a claim of statistical significance.

### Proposed first-party UTM URLs
Public editorial routes only, using utm_source=the_dispatch, utm_medium=email, utm_campaign=mind_archive_pilot, utm_content=issue_XX. These are PROPOSED ONLY and are not embedded in any sent content. Issues 03 and 05 generate null URL while their first-party guides remain unpublished, and **all affiliate merchant URLs remain null**. No tracking pixels, unique subscriber tags, or seller redirects.

### Product and legal boundaries
Zen12's seller describes a 12-minute meditation audio format (https://zen12.com/about); "meditates for you" is a marketing claim. The Hypnosis Live Total Focus seller describes a 33-minute, 47 MB audio (https://hypnosislive.com/mental-skills/total-focus); its perfect-focus/reprogramming claims are not independently substantiated. General research is not product proof: https://www.nccih.nih.gov/health/hypnosis ; https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety . No live affiliate acceptance, permitted email-promotion channel, price or tracking format was authenticated. Consumer marketing messages and an unrelated Refersion application-in-review notice are NOT approval.

Current WordPress: existing newsletter enabled; new post auto-email OFF; excerpt mode; welcome message points to 52-page Focus Fieldbook; zero observed sends, contradictory counts. Full vs excerpt delivery and actual received preview remain unknown. Before any commercial email, require a valid Final Vestige postal address, functional opt-out and near-offer affiliate disclosure, and founder approval. FTC source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

This is an offline measurement workbench, NOT an approved/sendable newsletter, actual Jetpack preview, a claim of merchant account acceptance, or a substitute for PR #201's independent release gates.
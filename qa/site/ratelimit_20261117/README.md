# FV independent site QA: rate-limit visibility (offline)

Independent, add-only companion to existing Site QA issue #126 / draft PR #127 and conversion coordination issue #820. This is NOT a fix for hosting rate limits, a browser test or a deployed production change.

## Usage

Run from this folder:

    python -m unittest -v test_landing_rate_limit_audit.py
    python landing_rate_limit_audit.py < sanitized_wpcom_web_log_response.json

Python standard library only. The program only reads standard input and writes an aggregate JSON report to standard output. No website requests, plugin activity, cloud services, CRM/subscriber changes, filesystem writes, extra tracking tags, or firewall changes.

Input is an authorized, SANITIZED WordPress wpcom_site_logs_list(type="web") response, either its structuredContent, one response object or an array of consecutive pages. Remove IPs, individual identifiers, cookies, sensitive tokens, full URLs with query strings, email addresses and referers BEFORE passing it to this program. Never commit real request-level access logs to GitHub. User agents are untrusted, spoofable claims, not verified identities.

## Evidence boundaries

- A logged HTTP 429 for /focus/, /dispatch/, /collection/ or the homepage requires REVIEW of the policy decision, not a conclusion that a customer was blocked.
- HTTP 429 for robots.txt or a sitemap flags discovery-path REVIEW, not established SEO damage.
- Apparent configuration-file probes are classified separately. Even a 2xx for one such path triggers manual inspection, not an automatic vulnerability assertion.
- Partial lists, inconsistent pagination and changing time windows cannot be certified as exhaustive. Do not equate rolling access-log windows with dashboard time-bucket totals.
- No result is a verified human session, true bot, email-delivery receipt, merchant-confirmed paid order, affiliate payout, or realized net revenue.
- Never whitelist crawler names or change live security/crawler settings from a user-agent string.
- Claude/Security owns policy correlation; Claude/Focus owns actual welcome/PDF delivery; Commerce/Claude owns Payhip/affiliate settlements; Grok/Praxxis owns existing creator-task attribution; founder retains production and spending approvals.

Relevant existing evidence: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820#issuecomment-6971537992

## Tests

24 synthetic local unittest assertions passed on the authoring bytes before GitHub upload, and py_compile passed. The test suite checks path categories, incomplete pagination, fake crawler-identity limits, privacy-safe aggregate output and negative cases. It does NOT test live mobile UX, real browser behavior, security, a confirmed signup, merchant checkout, or server-side production readiness.

This branch is DRAFT-only and must not be merged, deployed or adopted without QD and founder approval.

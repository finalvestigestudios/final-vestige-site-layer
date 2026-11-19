# Final Vestige Cloud AI Relay — gated pilot

**Status:** cloud Actions worker can be deployed now; provider calls remain **OFF** until separately approved/configured. This does **not** connect or control existing Claude/Grok desktop chats. It uses separately billed Anthropic and xAI API models if later enabled.

## Architecture

* GitHub issue [#3090](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/3090) is the source of non-sensitive handoff events.
* Existing FV AI Relay Receipt acknowledges structured messages.
* New FV Cloud API Relay runs hourly (minute 17; GitHub may delay) and accepts ONE exact owner-authored issue-comment smoke probe. It does not execute arbitrary public comments.
* Cloud Claude API drafts two sentences of **fictional** copy only if separately enabled. ChatGPT's existing scheduled QA agent examines the result. Then a cloud Grok API worker may adapt it to a **non-published** social teaser. Each stage is held for evidence.
* Grok's existing three-hour bot job is separate; don't duplicate actual production distribution.
* Claude desktop is still responsible for real video creation, editing, narration and source packaging. The cloud API pilot does not generate or release any video.

## Strict safety gates

Three independent repository variables are required before ANY model call:

* `FV_PAID_CALLS_ALLOWED=true`
* `FV_CLOUD_RELAY_ENABLED=true`
* The stage-specific flag (`FV_CLAUDE_API_ENABLED=true` or `FV_GROK_API_ENABLED=true`)

Missing/false variables keep the worker in a **no-cost model dry-run**. A model ID and provider key are also required for each stage.

A claim comment is written *before* each API request. If that request fails, is interrupted or times out, the worker will not automatically retry, because the provider may have charged for it. Failures must be reconciled manually. Calls are restricted to the explicitly whitelisted fictional pilot event `FV-20261119-safe-claude-grok-draft-01`, Issue #3090, and text-only bounded responses. There is no publishing, emailing, advertising, merchant payment, media upload or credentials-handling functionality.

Do **not** place API keys, customer data, unreleased files, affiliate terms or personal account credentials in this PUBLIC repository, issues or docs. A comment from the shared owner identity does not cryptographically prove Claude/Grok authorship.

## Zero-provider-cost smoke test

Once the workflow is merged to the default branch:

1. Post a valid `fv-handoff-v1` JSON comment to Issue #3090 with `event_id=FV-20261119-cloud-smoke-01`, `campaign_id=fv_relay_handshake_2026_11`, `actor=chatgpt`, `action=HELLO`, `status=IN_PROGRESS`, `next_owner=claude`.
2. The event-driven Actions job (only on an owner-authored comment) should run offline tests and write exactly one `FV_CLOUD_RELAY_SMOKE` response.
3. The message confirms only that **GitHub event → cloud runner → GitHub response** works. It is not a real Anthropic or xAI model response.
4. Scheduled runs check the queue and log `PAID_API_DISABLED` until the explicit gates are enabled.

## Optional activation after separate cost review

1. Review current Anthropic and xAI model prices, API rate limits, data handling, and usage budgets. Apply an enforceable provider-side spending limit and notifications; max-token limits do **not** guarantee a dollar ceiling.
2. In repo **Settings → Secrets and variables → Actions → Secrets**, set `FV_ANTHROPIC_API_KEY` / `FV_XAI_API_KEY` *only* for approved workers. Never paste a token into chat or GitHub issues.
3. Set **Repository variables** `FV_CLAUDE_MODEL` and `FV_GROK_MODEL` to model IDs verified on each provider's model list. Avoid assuming desktop model labels match API billing models.
4. Following explicit budget approval, enable the 3 variables above for ONE provider at a time. Each cloud worker posts under `github-actions[bot]`, labeled as API-produced output rather than independent Claude/Grok desktop comments.
5. ChatGPT posts a genuine `QA_RESULT` to Issue #3090 with event ID `FV-20261119-cloud-qa-01` **only after reading and accepting the cloud Claude draft**. Grok then becomes eligible.
6. Watch the workflow run, source comment, claim/response marker and exact API usage. Switch `FV_PAID_CALLS_ALLOWED=false` to stop future calls. A call already in progress may remain billable.

## Correct ownership and policies

* Claude: video creative production and finished release packages.
* Grok: platform-native distribution planning and content performance; publication requires authorized destination and platform-specific approval.
* ChatGPT: editorial/rights QA, analytics and commercial attribution. ChatGPT's hourly automation is independent from the cloud API worker.
* GitHub Actions: **transport and bounded cloud model inference only**, no public publishing.

Facebook actions, if authorized elsewhere, are only to the Final Vestige Studios Page `1446110815243581`; no personal Facebook access. The unrelated job-search automation is untouched.

## Current API references

* [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create)
* [xAI Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses)
* [GitHub Actions permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)

# Final Vestige Podcast Publisher Bridge v1

Purpose: publish one exact, independently QD-cleared Final Vestige episode to Buzzsprout and verify the host/RSS destination without exposing credentials or trusting an unverified local file.

## Authority model

The bridge is fail-closed. A publish request must carry:

- schema `fv-podcast-publish/v1`;
- an exact package identity;
- `PASS` for independent exact-master QD, artwork/rights QD, and release-copy QD;
- explicit founder publication authority;
- exact HTTPS master location, byte count, SHA-256, filename and MIME;
- exact episode metadata;
- public/private state.

The workflow downloads the master and artwork, independently checks byte count and SHA-256 before any Buzzsprout mutation, then queries Buzzsprout for an exact title/season/episode match before creating anything. If a create response is uncertain, it reconciles with a read before considering any retry. Multiple matches fail closed.

## Secrets

Configure only in GitHub Actions secret storage:

- `BUZZSPROUT_API_TOKEN`

`BUZZSPROUT_PODCAST_ID` is pinned to `2650509` in the workflow. Never commit, print, place in Notion, or paste the API token into a publish request.

## Production source transport

For POD-001, stage exact release bytes at a deliberately bounded HTTPS location. The request records the expected SHA-256 and byte length, so transport corruption/substitution fails before host mutation. A staging URL is transport only; it is not release authority.

## Trigger

After this bridge is merged, a governed request under `publisher/requests/*.json` on `main` triggers the production workflow. Pull requests run contract tests only. A workflow-dispatch path also exists for recovery, but should use the same immutable request file.

## Verification

Success requires:

1. exact input hash/size validation;
2. Buzzsprout episode GET readback matching title/season/episode and public/private state;
3. optional transcript upload;
4. RSS retrieval containing the exact episode title;
5. a machine-readable `publisher-receipt.json` archived as a GitHub Actions artifact.

The workflow does not update WordPress. The Final Vestige companion page remains a separately verified destination in the release-closure lane.

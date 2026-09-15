# Final Vestige Podcast Publisher Bridge v1.1

Purpose: publish one exact, independently QD-cleared Final Vestige episode to Buzzsprout podcast `2650509` and verify the host/RSS destination without exposing credentials, trusting caller-asserted approval strings, or silently accepting host audio degradation.

## Release authority

Release mode requires all of the following:

- schema `fv-podcast-publish/v1` and `mode=release`;
- exact package identity;
- exact master SHA-256 + byte count + HTTPS transport;
- exact artwork SHA-256 + byte count when artwork is supplied;
- exact release-payload SHA-256;
- request evidence showing independent PASS for exact-master, artwork/rights and release-copy QD;
- explicit founder publication-authority evidence;
- **runtime-owned authorization values** matching package ID, master SHA, artwork SHA and release-payload SHA.

The runtime bindings are configured only in the protected `podcast-production` Actions environment:

- `PODCAST_AUTH_PACKAGE_ID`
- `PODCAST_AUTH_MASTER_SHA256`
- `PODCAST_AUTH_ARTWORK_SHA256`
- `PODCAST_AUTH_RELEASE_SHA256`

Caller-provided `PASS` strings alone can never authorize a release.

## Buzzsprout secret

Configure only in the protected Actions environment:

- `BUZZSPROUT_API_TOKEN`

`BUZZSPROUT_PODCAST_ID=2650509` is pinned in the workflow. Never commit, print, place in Notion, or paste the token into a request.

## Private canary

Issue #46 requires a private host-write canary before the real release. Canary mode generates a deterministic one-second 48 kHz stereo WAV inside the runner, creates a namespaced **private** Buzzsprout episode, waits for processing, verifies the exact private destination, and stops. It never appears in RSS. Canary execution additionally requires runtime control `PODCAST_CANARY_ENABLED=1`.

## Real episode sequence

1. Validate the request and runtime-owned authorization bindings.
2. Download master/artwork and independently verify byte count + SHA-256 before host mutation.
3. Reconcile by exact title/episode/optional-season identity; multiple matches fail closed.
4. Create the real episode **private first**. On uncertain POST outcome, read/reconcile before any retry; the bridge never blindly retries create.
5. Poll GET until audio processing yields an `audio_url`.
6. Require Buzzsprout `hq=true` and reject `magic_mastering=true` for this already-mastered exact release.
7. Optionally upload a governed transcript using Buzzsprout multipart `transcript_file` + `transcript_format`.
8. PUT the verified private episode public; reconcile an uncertain update by readback.
9. Verify public GET state and poll RSS until the exact title appears.
10. Archive `publisher-receipt.json` with episode ID, host audio URL, HQ/Magic-Mastering state, exact input identities and verification timestamp.

## Metadata safeguards

- Season number is optional; the bridge never invents one when canonical metadata has no season.
- Description is rejected before mutation when it exceeds Buzzsprout's current 4,000-character ceiling.
- A push must contain exactly one changed `publisher/requests/*.json` file or the workflow fails before mutation.
- GET polling uses ETags when available.

## Transport

The production request must point to deliberately staged HTTPS copies of the exact release bytes. Transport is not authority: the bridge re-hashes every byte. Do not commit expiring signed download URLs or credentials to source, logs or Notion.

## Current POD-001 gates

Before the real request may run:

1. exact-master audible QD PASS on the frozen MP3;
2. artwork/rights QD PASS;
3. final-bound release-copy QD PASS;
4. bridge exact-head CI + independent QD PASS and merge;
5. private canary PASS;
6. protected Actions environment contains Buzzsprout token + exact runtime release-authority bindings;
7. exact master/artwork staging URLs are reachable by the runner without exposing credentials.

The bridge does not update WordPress. The Final Vestige companion page remains a separately confirmed and destination-verified release step.

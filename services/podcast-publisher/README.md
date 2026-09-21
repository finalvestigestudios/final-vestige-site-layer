# Final Vestige Podcast Publisher Bridge v1.4

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

## Buzzsprout host identity

Buzzsprout owns the episode GUID. The publisher never invents or sends a client GUID. A deterministic internal `package_key` is retained for Final Vestige receipts, while host verification records the Buzzsprout-assigned episode ID and `Buzzsprout...` GUID returned by the API.

Reconciliation uses exact governed metadata identity: title, episode number, optional season, description, artist and explicit flag. Multiple exact matches or a visible title/number/season collision with different governed metadata fail closed.

## Private canary

Issue #46 requires a private host-write canary before the real release. Canary mode generates a deterministic one-second 48 kHz stereo WAV inside the runner, creates or safely reconciles a namespaced **private** Buzzsprout episode, waits for processing, verifies the exact private destination, and stops. It never appears in RSS. Canary execution additionally requires runtime control `PODCAST_CANARY_ENABLED=1`.

## Real episode sequence

1. Validate the request and runtime-owned authorization bindings.
2. Download master/artwork and independently verify byte count + SHA-256 before host mutation.
3. Reconcile by exact governed metadata identity; ambiguous or conflicting matches fail closed.
4. Create the real episode **private first**, metadata/artwork only. On uncertain POST outcome, read/reconcile before any retry; the bridge never blindly retries create.
5. Start a Buzzsprout media upload, PUT the exact bytes to the returned upload URL without the Buzzsprout Authorization header, then call the upload `complete` endpoint.
6. Poll the private episode until media processing completes and an `audio_url` is present.
7. If an exact private episode must be reprocessed after a host-setting correction, `replace_media=true` replaces only that exact private episode's media with the runtime-authorized frozen master; it never creates a second release episode.
8. Arm a one-hour future publication window solely so Buzzsprout's hosted media becomes readable. Immediately verify the episode is absent from RSS; if RSS appears early or the verification window becomes unsafe, force the episode back to private.
9. Independently probe the governed source and Buzzsprout derivative with ffprobe, then require the host to remain MP3, stereo, >=44.1 kHz and ~192 kbps. Decode both through ffmpeg and require an exact SHA-256 match of the decoded PCM before final publication; metadata/container rewrites are allowed, audio-sample changes are not.
10. Replace and read back the governed Buzzsprout chapter list when chapters are supplied.
11. Optionally upload a governed custom public transcript. Buzzsprout's current custom-transcript API accepts SRT or JSON only.
12. PATCH the verified scheduled episode to publish immediately, probe the final public audio again, and poll RSS until the exact title appears.
13. Archive `publisher-receipt.json` with package key, Buzzsprout episode ID/GUID, source/scheduled/final PCM fingerprints, chapter/transcript receipts, provider flags, exact input identities and verification timestamp.

## Resume safety

Canary runs may safely reconcile an already-created private canary with exact governed metadata, which is required for failed verification retries such as POD-001 R4.

For a real release, if a resumed run encounters an already-existing release episode that already has media, the bridge fails closed rather than assuming that media belongs to the currently authorized package. This deliberately favors exact-master safety over blind idempotent continuation.

## Metadata safeguards

- Season number is optional; the bridge never invents one when canonical metadata has no season.
- Description is rejected before mutation when it exceeds Buzzsprout's current 4,000-character ceiling.
- A push must contain exactly one changed `publisher/requests/*.json` file or the workflow fails before mutation.
- GET polling uses ETags when available.
- Client-supplied Buzzsprout GUIDs are not used.
- Provider-specific `hq` or `magic_mastering` fields are not assumed to exist. If returned, they are recorded as observations only; release integrity is enforced against the actual hosted audio derivative.
- Governed chapters must be strictly increasing and are destination-read-back before public publication.
- Custom public transcripts, when supplied, must use Buzzsprout-supported SRT or JSON format.

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

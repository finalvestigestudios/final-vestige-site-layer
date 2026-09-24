# Final Vestige Podcast Publisher Bridge v2.4

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

1. Validate the episode-neutral request and protected runtime authorization bindings.
2. Resolve Buzzsprout's canonical RSS URL from the authenticated podcast record.
3. Download the exact master/artwork and independently verify byte count + SHA-256 before any host mutation.
4. Reconcile exact governed metadata identity. Ambiguous or conflicting matches fail closed.
5. Create the episode private. The normal path uses Buzzsprout's upload resource; the governed compatibility path may attach the exact master on episode creation when host processing requires it.
6. Wait for private media processing. Release readiness requires a real processed duration plus the expected host/provider state.
7. Require HQ when Buzzsprout reports the flag and reject Magic Mastering when it is reported active.
8. Upload and read back governed chapters; optionally upload a governed SRT/JSON transcript.
9. Publish the exact verified episode.
10. Locate the exact episode in the canonical RSS feed and extract its listener-facing enclosure.
11. Verify the hosted enclosure remains MP3, stereo, >=44.1 kHz, ~192 kbps and duration-aligned with the frozen master. Exact decoded PCM is accepted when possible; otherwise the host's lossy re-encode must pass governed waveform-equivalence and gain checks.
12. Fail closed and force-unpublish on destination/audio verification failure.
13. Archive `publisher-receipt.json` containing exact input identities, Buzzsprout episode ID/GUID, provider flags, host-audio measurements, chapter/transcript receipts and RSS evidence.

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

## Per-episode release gates

Every episode gets its own package ID, frozen master, artwork identity, release-copy identity and protected runtime authorization values. Episode 1's hashes or package ID are never reused for a later episode. A new episode cannot publish until its exact master, artwork/rights and release copy have independent PASS dispositions and the protected environment is rebound to those exact identities.

The bridge does not update WordPress. The Final Vestige companion page remains a separately confirmed and destination-verified release step.

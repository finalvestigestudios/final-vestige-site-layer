import assert from 'node:assert/strict';
import { validateRequest } from './publisher-v3.mjs';

const base = {
  schema_version: 'fv-podcast-publish/v1',
  mode: 'release',
  package_id: 'POD-001-FINAL-V1.2',
  release_payload_sha256: 'c'.repeat(64),
  publication_authority: 'FOUNDER_EXPLICIT_PUBLISH_2026-09-15',
  qd: { exact_master: 'PASS', artwork_rights: 'PASS', release_copy: 'PASS' },
  master: {
    url: 'https://example.com/master.mp3', sha256: 'a'.repeat(64), bytes: 40771052,
    filename: 'episode.mp3', mime: 'audio/mpeg'
  },
  artwork: {
    url: 'https://example.com/art.png', sha256: 'b'.repeat(64), bytes: 536879,
    filename: 'art.png', mime: 'image/png'
  },
  metadata: {
    title: 'The Textbook Found Open in the Ruins | New London, 1937',
    description: 'description', summary: 'summary', artist: 'Final Vestige Studios',
    explicit: false, private: false, episode_number: 1, tags: 'New London, Texas, 1937'
  }
};

const validated = validateRequest(base);
assert.equal(validated.metadata.episode_number, 1);
assert.equal(validated.metadata.season_number, null, 'season must remain absent when canonical metadata has no season');
assert.match(validated.package_key, /^FVPKG-[0-9a-f]{40}$/);
assert.equal(validated.package_key, validateRequest(structuredClone(base)).package_key, 'package key must be deterministic');
assert.equal(validated.guid, undefined, 'client must not invent a Buzzsprout GUID');

for (const gate of ['exact_master', 'artwork_rights', 'release_copy']) {
  const mutant = structuredClone(base); mutant.qd[gate] = 'PENDING';
  assert.throws(() => validateRequest(mutant), /not PASS/);
}
{
  const mutant = structuredClone(base); mutant.metadata.private = true;
  assert.throws(() => validateRequest(mutant), /private/);
}
{
  const mutant = structuredClone(base); mutant.publication_authority = 'AUTO';
  assert.throws(() => validateRequest(mutant), /authority/);
}
{
  const mutant = structuredClone(base); mutant.master.sha256 = 'xyz';
  assert.throws(() => validateRequest(mutant), /SHA-256/);
}
{
  const mutant = structuredClone(base); mutant.master.url = 'http://example.com/master.mp3';
  assert.throws(() => validateRequest(mutant), /HTTPS/);
}
{
  const mutant = structuredClone(base); mutant.metadata.description = 'x'.repeat(4001);
  assert.throws(() => validateRequest(mutant), /4,000-character/);
}
{
  const mutant = structuredClone(base); mutant.transcript = { content: 'hello', format: 'PDF', filename: 'x.txt' };
  assert.throws(() => validateRequest(mutant), /transcript.format/);
}
{
  const canary = validateRequest({
    schema_version: 'fv-podcast-publish/v1', mode: 'canary', package_id: 'CANARY-001',
    metadata: { title: 'FINAL VESTIGE PUBLISHER CANARY 001', private: true }
  });
  assert.equal(canary.mode, 'canary');
  assert.equal(canary.metadata.private, true);
  assert.match(canary.package_key, /^FVPKG-[0-9a-f]{40}$/);
  assert.equal(canary.guid, undefined);
}
{
  const canary = { schema_version: 'fv-podcast-publish/v1', mode: 'canary', package_id: 'CANARY-001', metadata: { title: 'FINAL VESTIGE PUBLISHER CANARY 001', private: false } };
  assert.throws(() => validateRequest(canary), /canary must remain private/);
}

console.log('publisher request fail-closed tests: PASS');

import assert from 'node:assert/strict';
import { validateRequest } from './publisher-v3.mjs';

const base = {
  schema_version: 'fv-podcast-publish/v1',
  mode: 'release',
  package_id: 'FV-POD-TEST-0001',
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
  chapters: [
    { title: 'Cold open', start_time: '00:00' },
    { title: 'Story proper', start_time: '02:06' }
  ],
  metadata: {
    title: 'Example Final Vestige Episode',
    description: 'description', summary: 'summary', artist: 'Final Vestige Studios',
    explicit: false, private: false, episode_number: 1, episode_type: 'full',
    custom_url: 'https://finalvestige.com/podcast/example-episode/',
    tags: 'example, history'
  }
};

const validated = validateRequest(base);
assert.equal(validated.metadata.episode_number, 1);
assert.equal(validated.metadata.season_number, null, 'season must remain absent when canonical metadata has no season');
assert.equal(validated.metadata.episode_type, 'full');
assert.equal(validated.metadata.custom_url, 'https://finalvestige.com/podcast/example-episode/');
assert.equal(validated.chapters.length, 2);
assert.equal(validated.chapters[1].start_seconds, 126);
assert.equal(validated.replace_media, false);
assert.equal(validated.supersede_existing_private, false);
assert.equal(validated.create_with_media_legacy, false);
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
  const mutant = structuredClone(base); mutant.transcript = { content: 'hello', format: 'TXT', filename: 'x.txt' };
  assert.throws(() => validateRequest(mutant), /transcript.format/);
}
{
  const mutant = structuredClone(base); mutant.transcript = { content: '1\n00:00:00,000 --> 00:00:01,000\nHello\n', format: 'SRT', filename: 'episode.srt' };
  assert.equal(validateRequest(mutant).transcript.format, 'SRT');
}
{
  const mutant = structuredClone(base); mutant.transcript = { content: '1\n00:00:00,000 --> 00:00:01,000\nHello\n', format: 'SRT' };
  assert.equal(validateRequest(mutant).transcript.filename, 'FV-POD-TEST-0001-transcript.srt');
}
{
  const mutant = structuredClone(base); mutant.chapters = [
    { title: 'First', start_time: '02:00' },
    { title: 'Second', start_time: '01:00' }
  ];
  assert.throws(() => validateRequest(mutant), /strictly increasing/);
}
{
  const mutant = structuredClone(base); mutant.metadata.episode_type = 'unknown';
  assert.throws(() => validateRequest(mutant), /episode_type/);
}
{
  const mutant = structuredClone(base); mutant.metadata.custom_url = 'http://example.com';
  assert.throws(() => validateRequest(mutant), /custom_url/);
}
{
  const mutant = structuredClone(base); mutant.replace_media = true;
  assert.equal(validateRequest(mutant).replace_media, true);
}
{
  const mutant = structuredClone(base); mutant.supersede_existing_private = true;
  assert.equal(validateRequest(mutant).supersede_existing_private, true);
}
{
  const mutant = structuredClone(base); mutant.create_with_media_legacy = true;
  assert.equal(validateRequest(mutant).create_with_media_legacy, true);
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


if (process.env.GITHUB_HEAD_REF === 'release/pod-001-final-v1.3') {
  const crypto = await import('node:crypto');
  const fs = await import('node:fs/promises');
  const release = JSON.parse(await fs.readFile('publisher/requests/POD-001.json', 'utf8'));
  for (const [label, spec] of [['master', release.master], ['artwork', release.artwork]]) {
    const res = await fetch(spec.url, { redirect: 'follow', headers: { 'User-Agent': 'FinalVestigeReleasePreflight/1.0' } });
    assert.equal(res.ok, true, `${label} staging transport must be unauthenticated HTTP 2xx`);
    const bytes = Buffer.from(await res.arrayBuffer());
    assert.equal(bytes.length, spec.bytes, `${label} staging byte count must match governed release`);
    const got = crypto.createHash('sha256').update(bytes).digest('hex');
    assert.equal(got, spec.sha256, `${label} staging SHA-256 must match governed release`);
    console.log(`POD-001 public staging preflight PASS: ${label} ${bytes.length} bytes ${got}`);
  }
}

console.log('publisher request fail-closed tests: PASS');

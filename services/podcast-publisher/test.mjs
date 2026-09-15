import assert from 'node:assert/strict';
import { validateRequest } from './publisher.mjs';

const base = {
  schema_version: 'fv-podcast-publish/v1',
  package_id: 'POD-001-FINAL-V1.2',
  publication_authority: 'FOUNDER_EXPLICIT_PUBLISH_2026-09-15',
  qd: { exact_master: 'PASS', artwork_rights: 'PASS', release_copy: 'PASS' },
  master: {
    url: 'https://example.com/master.mp3',
    sha256: 'a'.repeat(64),
    bytes: 40771052,
    filename: 'episode.mp3',
    mime: 'audio/mpeg'
  },
  artwork: {
    url: 'https://example.com/art.png',
    sha256: 'b'.repeat(64),
    bytes: 536879,
    filename: 'art.png',
    mime: 'image/png'
  },
  metadata: {
    title: 'The Textbook Found Open in the Ruins | New London, 1937',
    description: 'description',
    summary: 'summary',
    artist: 'Final Vestige Studios',
    explicit: false,
    private: false,
    episode_number: 1,
    season_number: 1,
    tags: 'New London, Texas, 1937'
  }
};

assert.equal(validateRequest(base).metadata.episode_number, 1);

for (const gate of ['exact_master', 'artwork_rights', 'release_copy']) {
  const mutant = structuredClone(base);
  mutant.qd[gate] = 'PENDING';
  assert.throws(() => validateRequest(mutant), /not PASS/);
}

{
  const mutant = structuredClone(base);
  mutant.metadata.private = true;
  assert.throws(() => validateRequest(mutant), /private/);
}

{
  const mutant = structuredClone(base);
  mutant.publication_authority = 'AUTO';
  assert.throws(() => validateRequest(mutant), /authority/);
}

{
  const mutant = structuredClone(base);
  mutant.master.sha256 = 'xyz';
  assert.throws(() => validateRequest(mutant), /SHA-256/);
}

{
  const mutant = structuredClone(base);
  mutant.master.url = 'http://example.com/master.mp3';
  assert.throws(() => validateRequest(mutant), /HTTPS/);
}

console.log('publisher request fail-closed tests: PASS');

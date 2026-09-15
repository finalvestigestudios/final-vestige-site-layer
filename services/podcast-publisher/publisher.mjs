import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const API_TOKEN = process.env.BUZZSPROUT_API_TOKEN;
const PODCAST_ID = process.env.BUZZSPROUT_PODCAST_ID || '2650509';
const REQUEST_FILE = process.env.PUBLISH_REQUEST_FILE;
const USER_AGENT = 'FinalVestigePodcastPublisher/1.1 (+https://finalvestige.com)';
const cache = new Map();

function fail(message) { throw new Error(message); }
function requireString(value, label) {
  if (typeof value !== 'string' || !value.trim()) fail(`${label} is required`);
  return value.trim();
}
function requireBool(value, label) {
  if (typeof value !== 'boolean') fail(`${label} must be boolean`);
  return value;
}
function requireInt(value, label) {
  if (!Number.isInteger(value)) fail(`${label} must be an integer`);
  return value;
}
function optionalInt(value, label) {
  if (value === null || value === undefined || value === '') return null;
  return requireInt(value, label);
}
function validateSha(value, label) {
  const s = requireString(value, label).toLowerCase();
  if (!/^[a-f0-9]{64}$/.test(s)) fail(`${label} must be SHA-256 hex`);
  return s;
}
function sha256Bytes(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}
function eqSecret(actual, expected, label) {
  if (!actual || !expected) fail(`${label} runtime authorization is not configured`);
  const a = Buffer.from(String(actual));
  const b = Buffer.from(String(expected));
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) fail(`${label} does not match runtime authorization`);
}

export function validateRequest(r) {
  if (!r || typeof r !== 'object' || Array.isArray(r)) fail('request must be an object');
  const mode = r.mode === 'canary' ? 'canary' : 'release';
  const m = r.metadata || {};

  if (mode === 'canary') {
    const title = requireString(m.title, 'metadata.title');
    if (!title.startsWith('FINAL VESTIGE PUBLISHER CANARY')) fail('canary title is not namespaced');
    if (!requireBool(m.private, 'metadata.private')) fail('canary must remain private');
    return {
      schema_version: requireString(r.schema_version, 'schema_version'),
      mode,
      package_id: requireString(r.package_id, 'package_id'),
      metadata: {
        title,
        description: typeof m.description === 'string' ? m.description : 'Private Final Vestige publisher canary.',
        summary: '', artist: 'Final Vestige Studios', explicit: false, private: true,
        episode_number: optionalInt(m.episode_number, 'metadata.episode_number'),
        season_number: optionalInt(m.season_number, 'metadata.season_number'),
        tags: 'publisher-canary', published_at: null,
      },
      rss_url: null,
    };
  }

  const qd = r.qd || {};
  const master = r.master || {};
  const artwork = r.artwork || null;
  const description = requireString(m.description, 'metadata.description');
  if ([...description].length > 4000) fail('metadata.description exceeds Buzzsprout 4,000-character ceiling');

  const transcript = r.transcript && typeof r.transcript === 'object' ? {
    content: requireString(r.transcript.content, 'transcript.content'),
    format: requireString(r.transcript.format || 'TXT', 'transcript.format').toUpperCase(),
    filename: requireString(r.transcript.filename || 'POD-001-transcript.txt', 'transcript.filename'),
  } : null;
  if (transcript && !['TXT', 'SRT', 'VTT'].includes(transcript.format)) fail('unsupported transcript.format');

  const out = {
    schema_version: requireString(r.schema_version, 'schema_version'),
    mode,
    package_id: requireString(r.package_id, 'package_id'),
    release_payload_sha256: validateSha(r.release_payload_sha256, 'release_payload_sha256'),
    publication_authority: requireString(r.publication_authority, 'publication_authority'),
    qd: {
      exact_master: requireString(qd.exact_master, 'qd.exact_master'),
      artwork_rights: requireString(qd.artwork_rights, 'qd.artwork_rights'),
      release_copy: requireString(qd.release_copy, 'qd.release_copy'),
    },
    master: {
      url: requireString(master.url, 'master.url'), sha256: validateSha(master.sha256, 'master.sha256'),
      bytes: requireInt(master.bytes, 'master.bytes'), filename: requireString(master.filename || 'episode.mp3', 'master.filename'),
      mime: requireString(master.mime || 'audio/mpeg', 'master.mime'),
    },
    artwork: artwork ? {
      url: requireString(artwork.url, 'artwork.url'), sha256: validateSha(artwork.sha256, 'artwork.sha256'),
      bytes: requireInt(artwork.bytes, 'artwork.bytes'), filename: requireString(artwork.filename || 'artwork.png', 'artwork.filename'),
      mime: requireString(artwork.mime || 'image/png', 'artwork.mime'),
    } : null,
    transcript,
    metadata: {
      title: requireString(m.title, 'metadata.title'), description,
      summary: typeof m.summary === 'string' ? m.summary : '',
      artist: typeof m.artist === 'string' && m.artist.trim() ? m.artist.trim() : 'Final Vestige Studios',
      explicit: requireBool(m.explicit, 'metadata.explicit'), private: requireBool(m.private, 'metadata.private'),
      episode_number: optionalInt(m.episode_number, 'metadata.episode_number'),
      season_number: optionalInt(m.season_number, 'metadata.season_number'),
      tags: typeof m.tags === 'string' ? m.tags : '',
      published_at: typeof m.published_at === 'string' && m.published_at.trim() ? m.published_at.trim() : null,
    },
    rss_url: typeof r.rss_url === 'string' && r.rss_url.trim() ? r.rss_url.trim() : `https://feeds.buzzsprout.com/${PODCAST_ID}.rss`,
  };

  if (out.schema_version !== 'fv-podcast-publish/v1') fail('unsupported schema_version');
  for (const [name, disposition] of Object.entries(out.qd)) if (disposition !== 'PASS') fail(`independent QD gate ${name} is not PASS`);
  if (!out.publication_authority.startsWith('FOUNDER_EXPLICIT_PUBLISH_')) fail('public publication authority evidence is missing');
  if (out.metadata.private) fail('release mode requires desired final private=false');
  if (!out.master.url.startsWith('https://')) fail('master.url must be HTTPS');
  if (out.artwork && !out.artwork.url.startsWith('https://')) fail('artwork.url must be HTTPS');
  return out;
}

function verifyRuntimeAuthority(r) {
  if (r.mode === 'canary') {
    if (process.env.PODCAST_CANARY_ENABLED !== '1') fail('private canary is not enabled by runtime control');
    return;
  }
  eqSecret(r.package_id, process.env.PODCAST_AUTH_PACKAGE_ID, 'package id');
  eqSecret(r.master.sha256, process.env.PODCAST_AUTH_MASTER_SHA256, 'master QD identity');
  if (r.artwork) eqSecret(r.artwork.sha256, process.env.PODCAST_AUTH_ARTWORK_SHA256, 'artwork QD identity');
  eqSecret(r.release_payload_sha256, process.env.PODCAST_AUTH_RELEASE_SHA256, 'release-copy QD identity');
}

async function downloadAndVerify(spec, label) {
  const response = await fetch(spec.url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT } });
  if (!response.ok) fail(`${label} download failed: HTTP ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  if (bytes.length !== spec.bytes) fail(`${label} byte mismatch: expected ${spec.bytes}, got ${bytes.length}`);
  if (sha256Bytes(bytes) !== spec.sha256) fail(`${label} SHA-256 mismatch`);
  return bytes;
}

function authHeaders(extra = {}) {
  if (!API_TOKEN) fail('BUZZSPROUT_API_TOKEN is not configured');
  return { Authorization: `Token token=${API_TOKEN}`, 'User-Agent': USER_AGENT, Accept: 'application/json', ...extra };
}

async function apiJson(path, options = {}) {
  const url = `https://www.buzzsprout.com/api/${PODCAST_ID}${path}`;
  const prior = cache.get(path);
  const headers = authHeaders(options.headers || {});
  if ((!options.method || options.method === 'GET') && prior?.etag) headers['If-None-Match'] = prior.etag;
  const response = await fetch(url, { ...options, headers });
  if (response.status === 304 && prior) return prior.json;
  const text = await response.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch {}
  if (!response.ok) fail(`Buzzsprout ${options.method || 'GET'} ${path} failed: HTTP ${response.status}${json?.error ? ` ${json.error}` : ''}`);
  if (!options.method || options.method === 'GET') cache.set(path, { etag: response.headers.get('etag'), json });
  return json;
}

function normalizeEpisodes(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.episodes)) return payload.episodes;
  return [];
}
function sameNullableNumber(a, b) {
  if (b === null) return a === null || a === undefined || a === '';
  return Number(a) === b;
}
function episodeMatchesRequest(ep, r) {
  if (String(ep.title || '').trim() !== r.metadata.title) return false;
  if (r.metadata.episode_number !== null && Number(ep.episode_number ?? ep.episodeNumber) !== r.metadata.episode_number) return false;
  return sameNullableNumber(ep.season_number ?? ep.seasonNumber, r.metadata.season_number);
}
async function listMatching(r) {
  cache.delete('/episodes.json');
  return normalizeEpisodes(await apiJson('/episodes.json')).filter(ep => episodeMatchesRequest(ep, r));
}

function deterministicCanaryWav() {
  const sampleRate = 48000, channels = 2, bits = 16, frames = sampleRate;
  const dataSize = frames * channels * (bits / 8);
  const out = Buffer.alloc(44 + dataSize);
  out.write('RIFF', 0); out.writeUInt32LE(36 + dataSize, 4); out.write('WAVE', 8);
  out.write('fmt ', 12); out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(channels, 22);
  out.writeUInt32LE(sampleRate, 24); out.writeUInt32LE(sampleRate * channels * bits / 8, 28);
  out.writeUInt16LE(channels * bits / 8, 32); out.writeUInt16LE(bits, 34); out.write('data', 36); out.writeUInt32LE(dataSize, 40);
  return out;
}

async function createEpisode(r, audioBytes, artworkBytes, forcePrivate = true) {
  const form = new FormData();
  form.append('title', r.metadata.title); form.append('description', r.metadata.description);
  if (r.metadata.summary) form.append('summary', r.metadata.summary);
  form.append('artist', r.metadata.artist); form.append('explicit', String(r.metadata.explicit));
  form.append('private', String(forcePrivate ? true : r.metadata.private));
  if (r.metadata.episode_number !== null) form.append('episode_number', String(r.metadata.episode_number));
  if (r.metadata.season_number !== null) form.append('season_number', String(r.metadata.season_number));
  if (r.metadata.tags) form.append('tags', r.metadata.tags);
  if (!forcePrivate && r.metadata.published_at) form.append('published_at', r.metadata.published_at);
  const filename = r.mode === 'canary' ? 'fv-publisher-canary.wav' : r.master.filename;
  const mime = r.mode === 'canary' ? 'audio/wav' : r.master.mime;
  form.append('audio_file', new Blob([audioBytes], { type: mime }), filename);
  if (r.artwork && artworkBytes) form.append('artwork_file', new Blob([artworkBytes], { type: r.artwork.mime }), r.artwork.filename);
  const response = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes.json`, { method: 'POST', headers: authHeaders(), body: form });
  const text = await response.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!response.ok) fail(`Buzzsprout POST /episodes.json failed: HTTP ${response.status}${json?.error ? ` ${json.error}` : ''}`);
  return json;
}

async function getEpisode(id) { cache.delete(`/episodes/${encodeURIComponent(id)}.json`); return apiJson(`/episodes/${encodeURIComponent(id)}.json`); }
function verifyIdentity(ep, r, expectedPrivate) {
  if (!ep || typeof ep !== 'object') fail('Buzzsprout episode readback missing');
  if (String(ep.title || '').trim() !== r.metadata.title) fail('Buzzsprout title readback mismatch');
  if (r.metadata.episode_number !== null && Number(ep.episode_number ?? ep.episodeNumber) !== r.metadata.episode_number) fail('Buzzsprout episode number mismatch');
  if (!sameNullableNumber(ep.season_number ?? ep.seasonNumber, r.metadata.season_number)) fail('Buzzsprout season number mismatch');
  if (Boolean(ep.private) !== expectedPrivate) fail('Buzzsprout private/public state mismatch');
}
function verifyHostAudioIntegrity(ep, r) {
  if (r.mode !== 'release') return;
  if (ep.hq !== true) fail('Buzzsprout host readback is not HQ; exact 192 kbps stereo release policy is not satisfied');
  if (ep.magic_mastering === true) fail('Buzzsprout Magic Mastering altered/reprocessed the governed master');
  if (!ep.audio_url) fail('Buzzsprout audio_url not ready');
}

async function pollPrivateProcessed(id, r) {
  let ep;
  for (let i = 0; i < 36; i++) {
    ep = await getEpisode(id); verifyIdentity(ep, r, true);
    if (ep.audio_url) { verifyHostAudioIntegrity(ep, r); return ep; }
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  fail('Buzzsprout audio did not finish processing within bounded verification window');
}

async function uploadTranscript(id, transcript) {
  if (!transcript) return { skipped: true };
  const form = new FormData();
  form.append('transcript_file', new Blob([Buffer.from(transcript.content, 'utf8')], { type: 'text/plain' }), transcript.filename);
  form.append('transcript_format', transcript.format);
  const response = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes/${encodeURIComponent(id)}/transcript`, { method: 'POST', headers: authHeaders(), body: form });
  if (!response.ok) fail(`Buzzsprout transcript upload failed: HTTP ${response.status}`);
  return { skipped: false };
}

async function publishEpisode(id, r) {
  const body = { private: false };
  if (r.metadata.published_at) body.published_at = r.metadata.published_at;
  try {
    await apiJson(`/episodes/${encodeURIComponent(id)}.json`, { method: 'PUT', headers: { 'Content-Type': 'application/json; charset=utf-8' }, body: JSON.stringify(body) });
  } catch (error) {
    const observed = await getEpisode(id);
    if (Boolean(observed?.private) !== false) throw error;
  }
  for (let i = 0; i < 18; i++) {
    const ep = await getEpisode(id); verifyIdentity(ep, r, false); verifyHostAudioIntegrity(ep, r); return ep;
  }
  fail('Buzzsprout episode did not reach public state');
}

async function verifyRss(r) {
  for (let i = 0; i < 24; i++) {
    const response = await fetch(r.rss_url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT, 'Cache-Control': 'no-cache' } });
    if (response.ok) {
      const xml = await response.text();
      if (xml.includes(r.metadata.title)) return { url: response.url, title_found: true };
    }
    await new Promise(resolve => setTimeout(resolve, 15000));
  }
  fail('RSS did not contain exact episode title within bounded propagation window');
}

async function main() {
  if (!REQUEST_FILE) fail('PUBLISH_REQUEST_FILE is not configured');
  const raw = await fs.readFile(REQUEST_FILE, 'utf8');
  const request = validateRequest(JSON.parse(raw));
  verifyRuntimeAuthority(request);
  console.log(`Validated ${request.mode} request ${request.package_id}`);

  const audioBytes = request.mode === 'canary' ? deterministicCanaryWav() : await downloadAndVerify(request.master, 'master audio');
  const artworkBytes = request.mode === 'release' && request.artwork ? await downloadAndVerify(request.artwork, 'artwork') : null;
  if (request.mode === 'release') console.log('Exact master/artwork bytes verified before host mutation');

  let matches = await listMatching(request);
  if (matches.length > 1) fail('multiple existing Buzzsprout episodes match the governed identity');
  let episode = matches[0] || null; let created = false;
  if (!episode) {
    try { episode = await createEpisode(request, audioBytes, artworkBytes, true); created = true; }
    catch (error) {
      console.warn('Create outcome uncertain/failed; reconciling by read before any retry.');
      matches = await listMatching(request); if (matches.length !== 1) throw error; episode = matches[0];
    }
  }
  const episodeId = episode?.id ?? episode?.episode_id;
  if (!episodeId) fail('Buzzsprout response did not expose an episode id');

  const privateReadback = await pollPrivateProcessed(episodeId, request);
  if (request.mode === 'canary') {
    await fs.writeFile('publisher-receipt.json', JSON.stringify({ schema_version:'fv-podcast-publish-receipt/v1', mode:'canary', package_id:request.package_id, buzzsprout_episode_id:String(episodeId), private:true, created, verified_at:new Date().toISOString() }, null, 2));
    console.log(`PRIVATE CANARY VERIFIED episode_id=${episodeId}`); return;
  }

  await uploadTranscript(episodeId, request.transcript);
  const finalReadback = await publishEpisode(episodeId, request);
  const rss = await verifyRss(request);
  const receipt = {
    schema_version:'fv-podcast-publish-receipt/v1', mode:'release', package_id:request.package_id,
    buzzsprout_podcast_id:PODCAST_ID, buzzsprout_episode_id:String(episodeId), created,
    private:Boolean(finalReadback.private), title:finalReadback.title,
    published_at:finalReadback.published_at ?? finalReadback.publishedAt ?? null,
    audio_sha256:request.master.sha256, audio_bytes:request.master.bytes,
    artwork_sha256:request.artwork?.sha256 ?? null, hq:finalReadback.hq === true,
    magic_mastering:finalReadback.magic_mastering === true, audio_url:finalReadback.audio_url ?? null,
    rss, verified_at:new Date().toISOString(),
  };
  await fs.writeFile('publisher-receipt.json', JSON.stringify(receipt, null, 2));
  console.log(`PUBLISHED + HOST/RSS VERIFIED episode_id=${episodeId}`);
}

if (import.meta.url === `file://${process.argv[1]}`) main().catch(error => { console.error(`Publisher failed closed: ${error.message}`); process.exitCode = 1; });

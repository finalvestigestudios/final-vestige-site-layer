import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const API_TOKEN = process.env.BUZZSPROUT_API_TOKEN;
const PODCAST_ID = process.env.BUZZSPROUT_PODCAST_ID || '2650509';
const REQUEST_FILE = process.env.PUBLISH_REQUEST_FILE;
const USER_AGENT = 'FinalVestigePodcastPublisher/1.2 (+https://finalvestige.com)';
const cache = new Map();

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const fail = message => { throw new Error(message); };
const str = (v, label) => {
  if (typeof v !== 'string' || !v.trim()) fail(`${label} is required`);
  return v.trim();
};
const bool = (v, label) => {
  if (typeof v !== 'boolean') fail(`${label} must be boolean`);
  return v;
};
const integer = (v, label) => {
  if (!Number.isInteger(v)) fail(`${label} must be integer`);
  return v;
};
const optionalInt = (v, label) => (v === null || v === undefined || v === '') ? null : integer(v, label);
const sha = (v, label) => {
  const s = str(v, label).toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(s)) fail(`${label} must be SHA-256 hex`);
  return s;
};
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function runtimeEquals(actual, expected, label) {
  if (!actual || !expected) fail(`${label} runtime authorization is not configured`);
  const a = Buffer.from(String(actual));
  const b = Buffer.from(String(expected));
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) fail(`${label} does not match runtime authorization`);
}

export function validateRequest(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('request must be an object');
  if (str(input.schema_version, 'schema_version') !== 'fv-podcast-publish/v1') fail('unsupported schema_version');
  const mode = input.mode === 'canary' ? 'canary' : 'release';
  const m = input.metadata || {};

  if (mode === 'canary') {
    const title = str(m.title, 'metadata.title');
    if (!title.startsWith('FINAL VESTIGE PUBLISHER CANARY')) fail('canary title is not namespaced');
    if (!bool(m.private, 'metadata.private')) fail('canary must remain private');
    return {
      schema_version: 'fv-podcast-publish/v1', mode,
      package_id: str(input.package_id, 'package_id'),
      metadata: {
        title,
        description: typeof m.description === 'string' && m.description ? m.description : 'Private Final Vestige publisher canary.',
        summary: '', artist: 'Final Vestige Studios', explicit: false, private: true,
        episode_number: optionalInt(m.episode_number, 'metadata.episode_number'),
        season_number: optionalInt(m.season_number, 'metadata.season_number'),
        tags: 'publisher-canary', published_at: null,
      },
      rss_url: null,
    };
  }

  const qd = input.qd || {};
  const master = input.master || {};
  const artwork = input.artwork || null;
  const description = str(m.description, 'metadata.description');
  if ([...description].length > 4000) fail('metadata.description exceeds Buzzsprout 4,000-character ceiling');

  const transcript = input.transcript && typeof input.transcript === 'object' ? {
    content: str(input.transcript.content, 'transcript.content'),
    format: str(input.transcript.format || 'TXT', 'transcript.format').toUpperCase(),
    filename: str(input.transcript.filename || 'POD-001-transcript.txt', 'transcript.filename'),
  } : null;
  if (transcript && !['TXT', 'SRT', 'VTT'].includes(transcript.format)) fail('unsupported transcript.format');

  const request = {
    schema_version: 'fv-podcast-publish/v1', mode,
    package_id: str(input.package_id, 'package_id'),
    release_payload_sha256: sha(input.release_payload_sha256, 'release_payload_sha256'),
    publication_authority: str(input.publication_authority, 'publication_authority'),
    qd: {
      exact_master: str(qd.exact_master, 'qd.exact_master'),
      artwork_rights: str(qd.artwork_rights, 'qd.artwork_rights'),
      release_copy: str(qd.release_copy, 'qd.release_copy'),
    },
    master: {
      url: str(master.url, 'master.url'), sha256: sha(master.sha256, 'master.sha256'),
      bytes: integer(master.bytes, 'master.bytes'), filename: str(master.filename || 'episode.mp3', 'master.filename'),
      mime: str(master.mime || 'audio/mpeg', 'master.mime'),
    },
    artwork: artwork ? {
      url: str(artwork.url, 'artwork.url'), sha256: sha(artwork.sha256, 'artwork.sha256'),
      bytes: integer(artwork.bytes, 'artwork.bytes'), filename: str(artwork.filename || 'artwork.png', 'artwork.filename'),
      mime: str(artwork.mime || 'image/png', 'artwork.mime'),
    } : null,
    transcript,
    metadata: {
      title: str(m.title, 'metadata.title'), description,
      summary: typeof m.summary === 'string' ? m.summary : '',
      artist: typeof m.artist === 'string' && m.artist.trim() ? m.artist.trim() : 'Final Vestige Studios',
      explicit: bool(m.explicit, 'metadata.explicit'), private: bool(m.private, 'metadata.private'),
      episode_number: optionalInt(m.episode_number, 'metadata.episode_number'),
      season_number: optionalInt(m.season_number, 'metadata.season_number'),
      tags: typeof m.tags === 'string' ? m.tags : '',
      published_at: typeof m.published_at === 'string' && m.published_at.trim() ? m.published_at.trim() : null,
    },
    rss_url: typeof input.rss_url === 'string' && input.rss_url.trim() ? input.rss_url.trim() : `https://feeds.buzzsprout.com/${PODCAST_ID}.rss`,
  };

  for (const [name, disposition] of Object.entries(request.qd)) if (disposition !== 'PASS') fail(`independent QD gate ${name} is not PASS`);
  if (!request.publication_authority.startsWith('FOUNDER_EXPLICIT_PUBLISH_')) fail('founder publication-authority evidence is missing');
  if (request.metadata.private) fail('release mode requires desired final private=false');
  if (!request.master.url.startsWith('https://')) fail('master.url must be HTTPS');
  if (request.artwork && !request.artwork.url.startsWith('https://')) fail('artwork.url must be HTTPS');
  return request;
}

function verifyRuntimeAuthority(r) {
  if (r.mode === 'canary') {
    if (process.env.PODCAST_CANARY_ENABLED !== '1') fail('private canary is not enabled by runtime control');
    return;
  }
  runtimeEquals(r.package_id, process.env.PODCAST_AUTH_PACKAGE_ID, 'package id');
  runtimeEquals(r.master.sha256, process.env.PODCAST_AUTH_MASTER_SHA256, 'master QD identity');
  if (r.artwork) runtimeEquals(r.artwork.sha256, process.env.PODCAST_AUTH_ARTWORK_SHA256, 'artwork QD identity');
  runtimeEquals(r.release_payload_sha256, process.env.PODCAST_AUTH_RELEASE_SHA256, 'release-copy QD identity');
}

async function downloadAndVerify(spec, label) {
  const res = await fetch(spec.url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT } });
  if (!res.ok) fail(`${label} download failed: HTTP ${res.status}`);
  const bytes = Buffer.from(await res.arrayBuffer());
  if (bytes.length !== spec.bytes) fail(`${label} byte mismatch: expected ${spec.bytes}, got ${bytes.length}`);
  if (digest(bytes) !== spec.sha256) fail(`${label} SHA-256 mismatch`);
  return bytes;
}

function authHeaders(extra = {}) {
  if (!API_TOKEN) fail('BUZZSPROUT_API_TOKEN is not configured');
  return { Authorization: `Token token=${API_TOKEN}`, 'User-Agent': USER_AGENT, Accept: 'application/json', ...extra };
}
function clear(path) { cache.delete(path); }
async function apiJson(path, options = {}) {
  const method = options.method || 'GET';
  const prior = cache.get(path);
  const headers = authHeaders(options.headers || {});
  if (method === 'GET' && prior?.etag) headers['If-None-Match'] = prior.etag;
  const res = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}${path}`, { ...options, method, headers });
  if (res.status === 304 && prior) return prior.json;
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) fail(`Buzzsprout ${method} ${path} failed: HTTP ${res.status}${json?.error ? ` ${json.error}` : ''}`);
  if (method === 'GET') cache.set(path, { etag: res.headers.get('etag'), json });
  else clear(path);
  return json;
}

function episodes(payload) { return Array.isArray(payload) ? payload : (Array.isArray(payload?.episodes) ? payload.episodes : []); }
function sameSeason(observed, governed) {
  if (governed === null) return observed === null || observed === undefined || observed === '';
  return Number(observed) === governed;
}
function matches(ep, r) {
  if (String(ep?.title || '').trim() !== r.metadata.title) return false;
  if (r.metadata.episode_number !== null && Number(ep.episode_number ?? ep.episodeNumber) !== r.metadata.episode_number) return false;
  return sameSeason(ep.season_number ?? ep.seasonNumber, r.metadata.season_number);
}
async function listMatching(r, fresh = false) {
  if (fresh) clear('/episodes.json');
  return episodes(await apiJson('/episodes.json')).filter(ep => matches(ep, r));
}

function canaryWav() {
  const sampleRate = 48000, channels = 2, bits = 16, frames = sampleRate;
  const dataSize = frames * channels * 2;
  const out = Buffer.alloc(44 + dataSize);
  out.write('RIFF', 0); out.writeUInt32LE(36 + dataSize, 4); out.write('WAVE', 8);
  out.write('fmt ', 12); out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(channels, 22);
  out.writeUInt32LE(sampleRate, 24); out.writeUInt32LE(sampleRate * channels * bits / 8, 28);
  out.writeUInt16LE(channels * bits / 8, 32); out.writeUInt16LE(bits, 34); out.write('data', 36); out.writeUInt32LE(dataSize, 40);
  for (let i = 0; i < frames; i++) {
    const sample = Math.round(Math.sin(2 * Math.PI * 440 * i / sampleRate) * 1500);
    const offset = 44 + i * 4; out.writeInt16LE(sample, offset); out.writeInt16LE(sample, offset + 2);
  }
  return out;
}

async function createPrivate(r, audioBytes, artworkBytes) {
  const form = new FormData();
  form.append('title', r.metadata.title); form.append('description', r.metadata.description);
  if (r.metadata.summary) form.append('summary', r.metadata.summary);
  form.append('artist', r.metadata.artist); form.append('explicit', String(r.metadata.explicit)); form.append('private', 'true');
  if (r.metadata.episode_number !== null) form.append('episode_number', String(r.metadata.episode_number));
  if (r.metadata.season_number !== null) form.append('season_number', String(r.metadata.season_number));
  if (r.metadata.tags) form.append('tags', r.metadata.tags);
  const filename = r.mode === 'canary' ? 'fv-publisher-canary.wav' : r.master.filename;
  const mime = r.mode === 'canary' ? 'audio/wav' : r.master.mime;
  form.append('audio_file', new Blob([audioBytes], { type: mime }), filename);
  if (r.artwork && artworkBytes) form.append('artwork_file', new Blob([artworkBytes], { type: r.artwork.mime }), r.artwork.filename);
  const res = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes.json`, { method: 'POST', headers: authHeaders(), body: form });
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) fail(`Buzzsprout POST /episodes.json failed: HTTP ${res.status}${json?.error ? ` ${json.error}` : ''}`);
  clear('/episodes.json');
  return json;
}

async function getEpisode(id, fresh = false) {
  const path = `/episodes/${encodeURIComponent(id)}.json`;
  if (fresh) clear(path);
  return apiJson(path);
}
function verifyCore(ep, r) {
  if (!ep || typeof ep !== 'object') fail('Buzzsprout episode readback missing');
  if (!matches(ep, r)) fail('Buzzsprout episode identity readback mismatch');
}
function verifyAudioPolicy(ep, r) {
  if (r.mode !== 'release') return;
  if (ep.hq !== true) fail('Buzzsprout host state is not HQ; governed 192 kbps stereo policy is not satisfied');
  if (ep.magic_mastering === true) fail('Buzzsprout Magic Mastering reprocessed the governed master');
  if (!ep.audio_url) fail('Buzzsprout audio_url is not ready');
}
async function waitForProcessedPrivate(id, r) {
  for (let i = 0; i < 36; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    if (Boolean(ep.private) !== true) fail('episode became public before private-stage verification completed');
    if (ep.audio_url) { verifyAudioPolicy(ep, r); return ep; }
    await sleep(10000);
  }
  fail('Buzzsprout audio did not finish processing within bounded verification window');
}

async function uploadTranscript(id, transcript) {
  if (!transcript) return { skipped: true };
  const form = new FormData();
  form.append('transcript_file', new Blob([Buffer.from(transcript.content, 'utf8')], { type: 'text/plain' }), transcript.filename);
  form.append('transcript_format', transcript.format);
  const res = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes/${encodeURIComponent(id)}/transcript`, { method: 'POST', headers: authHeaders(), body: form });
  if (!res.ok) fail(`Buzzsprout transcript upload failed: HTTP ${res.status}`);
  return { skipped: false };
}

async function makePublic(id, r) {
  const path = `/episodes/${encodeURIComponent(id)}.json`;
  const body = { private: false };
  if (r.metadata.published_at) body.published_at = r.metadata.published_at;
  try {
    await apiJson(path, { method: 'PUT', headers: { 'Content-Type': 'application/json; charset=utf-8' }, body: JSON.stringify(body) });
  } catch (error) {
    const observed = await getEpisode(id, true);
    verifyCore(observed, r);
    if (Boolean(observed.private) !== false) throw error;
  }
  for (let i = 0; i < 18; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    if (Boolean(ep.private) === false) { verifyAudioPolicy(ep, r); return ep; }
    await sleep(10000);
  }
  fail('Buzzsprout episode did not reach public state within bounded verification window');
}

async function verifyRss(r) {
  for (let i = 0; i < 24; i++) {
    const res = await fetch(r.rss_url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT, 'Cache-Control': 'no-cache' } });
    if (res.ok && (await res.text()).includes(r.metadata.title)) return { url: res.url, title_found: true };
    await sleep(15000);
  }
  fail('RSS did not contain exact episode title within bounded propagation window');
}

async function writeReceipt(data) {
  await fs.writeFile('publisher-receipt.json', JSON.stringify({ schema_version: 'fv-podcast-publish-receipt/v1', ...data, verified_at: new Date().toISOString() }, null, 2));
}

async function main() {
  if (!REQUEST_FILE) fail('PUBLISH_REQUEST_FILE is not configured');
  const raw = await fs.readFile(REQUEST_FILE, 'utf8');
  const r = validateRequest(JSON.parse(raw));
  verifyRuntimeAuthority(r);
  console.log(`Validated ${r.mode} request ${r.package_id}`);

  const audio = r.mode === 'canary' ? canaryWav() : await downloadAndVerify(r.master, 'master audio');
  const art = r.mode === 'release' && r.artwork ? await downloadAndVerify(r.artwork, 'artwork') : null;
  if (r.mode === 'release') console.log('Exact master/artwork bytes verified before host mutation');

  let found = await listMatching(r, true);
  if (found.length > 1) fail('multiple existing Buzzsprout episodes match the governed identity');
  let ep = found[0] || null, created = false;
  if (!ep) {
    try { ep = await createPrivate(r, audio, art); created = true; }
    catch (error) {
      console.warn('Create outcome uncertain/failed; reconciling by read before any retry.');
      found = await listMatching(r, true); if (found.length !== 1) throw error; ep = found[0];
    }
  }
  const id = ep?.id ?? ep?.episode_id;
  if (!id) fail('Buzzsprout response did not expose an episode id');

  // Idempotent re-entry after an already-successful public release.
  ep = await getEpisode(id, true); verifyCore(ep, r);
  if (r.mode === 'release' && Boolean(ep.private) === false) {
    verifyAudioPolicy(ep, r);
    const rss = await verifyRss(r);
    await writeReceipt({ mode: 'release', package_id: r.package_id, buzzsprout_podcast_id: PODCAST_ID, buzzsprout_episode_id: String(id), created: false, private: false, title: ep.title, published_at: ep.published_at ?? null, audio_sha256: r.master.sha256, audio_bytes: r.master.bytes, artwork_sha256: r.artwork?.sha256 ?? null, hq: ep.hq === true, magic_mastering: ep.magic_mastering === true, audio_url: ep.audio_url ?? null, rss });
    console.log(`PUBLISHED + HOST/RSS VERIFIED episode_id=${id}`); return;
  }

  const privateEp = await waitForProcessedPrivate(id, r);
  if (r.mode === 'canary') {
    await writeReceipt({ mode: 'canary', package_id: r.package_id, buzzsprout_podcast_id: PODCAST_ID, buzzsprout_episode_id: String(id), created, private: true, title: privateEp.title });
    console.log(`PRIVATE CANARY VERIFIED episode_id=${id}`); return;
  }

  await uploadTranscript(id, r.transcript);
  const publicEp = await makePublic(id, r);
  const rss = await verifyRss(r);
  await writeReceipt({ mode: 'release', package_id: r.package_id, buzzsprout_podcast_id: PODCAST_ID, buzzsprout_episode_id: String(id), created, private: false, title: publicEp.title, published_at: publicEp.published_at ?? null, audio_sha256: r.master.sha256, audio_bytes: r.master.bytes, artwork_sha256: r.artwork?.sha256 ?? null, hq: publicEp.hq === true, magic_mastering: publicEp.magic_mastering === true, audio_url: publicEp.audio_url ?? null, rss });
  console.log(`PUBLISHED + HOST/RSS VERIFIED episode_id=${id}`);
}

if (import.meta.url === `file://${process.argv[1]}`) main().catch(error => { console.error(`Publisher failed closed: ${error.message}`); process.exitCode = 1; });

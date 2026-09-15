import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const API_TOKEN = process.env.BUZZSPROUT_API_TOKEN;
const PODCAST_ID = process.env.BUZZSPROUT_PODCAST_ID || '2650509';
const REQUEST_FILE = process.env.PUBLISH_REQUEST_FILE;
const USER_AGENT = 'FinalVestigePodcastPublisher/1.0 (+https://finalvestige.com)';

function fail(message) {
  throw new Error(message);
}

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

function validateSha(value, label) {
  const s = requireString(value, label).toLowerCase();
  if (!/^[a-f0-9]{64}$/.test(s)) fail(`${label} must be SHA-256 hex`);
  return s;
}

export function validateRequest(r) {
  if (!r || typeof r !== 'object' || Array.isArray(r)) fail('request must be an object');
  const qd = r.qd || {};
  const master = r.master || {};
  const artwork = r.artwork || null;
  const m = r.metadata || {};

  const out = {
    schema_version: requireString(r.schema_version, 'schema_version'),
    package_id: requireString(r.package_id, 'package_id'),
    publication_authority: requireString(r.publication_authority, 'publication_authority'),
    qd: {
      exact_master: requireString(qd.exact_master, 'qd.exact_master'),
      artwork_rights: requireString(qd.artwork_rights, 'qd.artwork_rights'),
      release_copy: requireString(qd.release_copy, 'qd.release_copy'),
    },
    master: {
      url: requireString(master.url, 'master.url'),
      sha256: validateSha(master.sha256, 'master.sha256'),
      bytes: requireInt(master.bytes, 'master.bytes'),
      filename: requireString(master.filename || 'episode.mp3', 'master.filename'),
      mime: requireString(master.mime || 'audio/mpeg', 'master.mime'),
    },
    artwork: artwork ? {
      url: requireString(artwork.url, 'artwork.url'),
      sha256: validateSha(artwork.sha256, 'artwork.sha256'),
      bytes: requireInt(artwork.bytes, 'artwork.bytes'),
      filename: requireString(artwork.filename || 'artwork.png', 'artwork.filename'),
      mime: requireString(artwork.mime || 'image/png', 'artwork.mime'),
    } : null,
    transcript: typeof r.transcript === 'string' ? r.transcript : null,
    metadata: {
      title: requireString(m.title, 'metadata.title'),
      description: requireString(m.description, 'metadata.description'),
      summary: typeof m.summary === 'string' ? m.summary : '',
      artist: typeof m.artist === 'string' && m.artist.trim() ? m.artist.trim() : 'Final Vestige Studios',
      explicit: requireBool(m.explicit, 'metadata.explicit'),
      private: requireBool(m.private, 'metadata.private'),
      episode_number: requireInt(m.episode_number, 'metadata.episode_number'),
      season_number: requireInt(m.season_number, 'metadata.season_number'),
      tags: typeof m.tags === 'string' ? m.tags : '',
      published_at: typeof m.published_at === 'string' && m.published_at.trim() ? m.published_at.trim() : null,
    },
    rss_url: typeof r.rss_url === 'string' && r.rss_url.trim() ? r.rss_url.trim() : `https://feeds.buzzsprout.com/${PODCAST_ID}.rss`,
  };

  if (out.schema_version !== 'fv-podcast-publish/v1') fail('unsupported schema_version');
  for (const [name, disposition] of Object.entries(out.qd)) {
    if (disposition !== 'PASS') fail(`independent QD gate ${name} is not PASS`);
  }
  if (!out.publication_authority.startsWith('FOUNDER_EXPLICIT_PUBLISH_')) fail('public publication authority is missing');
  if (out.metadata.private) fail('this release request is private; public publication was explicitly requested');
  if (!out.master.url.startsWith('https://')) fail('master.url must be HTTPS');
  if (out.artwork && !out.artwork.url.startsWith('https://')) fail('artwork.url must be HTTPS');
  return out;
}

async function downloadAndVerify(spec, label) {
  const response = await fetch(spec.url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT } });
  if (!response.ok) fail(`${label} download failed: HTTP ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  if (bytes.length !== spec.bytes) fail(`${label} byte mismatch: expected ${spec.bytes}, got ${bytes.length}`);
  const sha = crypto.createHash('sha256').update(bytes).digest('hex');
  if (sha !== spec.sha256) fail(`${label} SHA-256 mismatch`);
  return bytes;
}

function authHeaders(extra = {}) {
  if (!API_TOKEN) fail('BUZZSPROUT_API_TOKEN is not configured');
  return {
    Authorization: `Token token=${API_TOKEN}`,
    'User-Agent': USER_AGENT,
    Accept: 'application/json',
    ...extra,
  };
}

async function apiJson(path, options = {}) {
  const url = `https://www.buzzsprout.com/api/${PODCAST_ID}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: authHeaders(options.headers || {}),
  });
  const text = await response.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch {}
  if (!response.ok) fail(`Buzzsprout ${options.method || 'GET'} ${path} failed: HTTP ${response.status}${json?.error ? ` ${json.error}` : ''}`);
  return json;
}

function normalizeEpisodes(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.episodes)) return payload.episodes;
  return [];
}

function episodeMatchesRequest(ep, r) {
  const num = Number(ep.episode_number ?? ep.episodeNumber ?? 0);
  const season = Number(ep.season_number ?? ep.seasonNumber ?? 0);
  return String(ep.title || '').trim() === r.metadata.title && num === r.metadata.episode_number && season === r.metadata.season_number;
}

async function listMatching(r) {
  const episodes = normalizeEpisodes(await apiJson('/episodes.json'));
  return episodes.filter(ep => episodeMatchesRequest(ep, r));
}

async function createEpisode(r, audioBytes, artworkBytes) {
  const form = new FormData();
  form.append('title', r.metadata.title);
  form.append('description', r.metadata.description);
  if (r.metadata.summary) form.append('summary', r.metadata.summary);
  form.append('artist', r.metadata.artist);
  form.append('explicit', String(r.metadata.explicit));
  form.append('private', String(r.metadata.private));
  form.append('episode_number', String(r.metadata.episode_number));
  form.append('season_number', String(r.metadata.season_number));
  if (r.metadata.tags) form.append('tags', r.metadata.tags);
  if (r.metadata.published_at) form.append('published_at', r.metadata.published_at);
  form.append('audio_file', new Blob([audioBytes], { type: r.master.mime }), r.master.filename);
  if (r.artwork && artworkBytes) {
    form.append('artwork_file', new Blob([artworkBytes], { type: r.artwork.mime }), r.artwork.filename);
  }

  const url = `https://www.buzzsprout.com/api/${PODCAST_ID}/episodes.json`;
  const response = await fetch(url, { method: 'POST', headers: authHeaders(), body: form });
  const text = await response.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch {}
  if (!response.ok) fail(`Buzzsprout POST /episodes.json failed: HTTP ${response.status}${json?.error ? ` ${json.error}` : ''}`);
  return json;
}

async function getEpisode(id) {
  return apiJson(`/episodes/${encodeURIComponent(id)}.json`);
}

async function uploadTranscript(id, transcript) {
  if (!transcript) return { skipped: true };
  const form = new FormData();
  form.append('transcript', new Blob([Buffer.from(transcript, 'utf8')], { type: 'text/plain' }), 'POD-001-transcript.txt');
  form.append('transcript_format', 'text/plain');
  const url = `https://www.buzzsprout.com/api/${PODCAST_ID}/episodes/${encodeURIComponent(id)}/transcript`;
  const response = await fetch(url, { method: 'POST', headers: authHeaders(), body: form });
  if (!response.ok) fail(`Buzzsprout transcript upload failed: HTTP ${response.status}`);
  return { skipped: false };
}

function verifyEpisode(ep, r) {
  if (!ep || typeof ep !== 'object') fail('Buzzsprout episode readback missing');
  if (String(ep.title || '').trim() !== r.metadata.title) fail('Buzzsprout title readback mismatch');
  if (Number(ep.episode_number ?? ep.episodeNumber ?? 0) !== r.metadata.episode_number) fail('Buzzsprout episode number mismatch');
  if (Number(ep.season_number ?? ep.seasonNumber ?? 0) !== r.metadata.season_number) fail('Buzzsprout season number mismatch');
  if (Boolean(ep.private) !== r.metadata.private) fail('Buzzsprout private/public state mismatch');
}

async function verifyRss(r) {
  const response = await fetch(r.rss_url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT } });
  if (!response.ok) fail(`RSS verification failed: HTTP ${response.status}`);
  const xml = await response.text();
  if (!xml.includes(r.metadata.title)) fail('RSS does not yet contain exact episode title');
  return { url: response.url, title_found: true };
}

async function main() {
  if (!REQUEST_FILE) fail('PUBLISH_REQUEST_FILE is not configured');
  const raw = await fs.readFile(REQUEST_FILE, 'utf8');
  const request = validateRequest(JSON.parse(raw));

  console.log(`Validated publish request ${request.package_id}`);
  const audioBytes = await downloadAndVerify(request.master, 'master audio');
  const artworkBytes = request.artwork ? await downloadAndVerify(request.artwork, 'artwork') : null;
  console.log('Exact master/artwork bytes verified before host mutation');

  let matches = await listMatching(request);
  if (matches.length > 1) fail('multiple existing Buzzsprout episodes match the exact title/season/episode identity');

  let episode = matches[0] || null;
  let created = false;
  if (!episode) {
    try {
      episode = await createEpisode(request, audioBytes, artworkBytes);
      created = true;
    } catch (error) {
      console.warn('Episode create did not return a verified success; reconciling before any retry.');
      matches = await listMatching(request);
      if (matches.length !== 1) throw error;
      episode = matches[0];
    }
  }

  const episodeId = episode?.id ?? episode?.episode_id;
  if (!episodeId) fail('Buzzsprout response did not expose an episode id');

  const readback = await getEpisode(episodeId);
  verifyEpisode(readback, request);
  await uploadTranscript(episodeId, request.transcript);

  // Processing can be eventually consistent. Poll only GETs; never blindly retry creation.
  let finalReadback = readback;
  for (let i = 0; i < 12; i++) {
    finalReadback = await getEpisode(episodeId);
    verifyEpisode(finalReadback, request);
    const status = String(finalReadback.processing_status ?? finalReadback.processingStatus ?? finalReadback.status ?? '').toLowerCase();
    if (!status || ['complete', 'completed', 'processed', 'published', 'ready'].includes(status)) break;
    await new Promise(resolve => setTimeout(resolve, 10000));
  }

  const rss = await verifyRss(request);
  const receipt = {
    schema_version: 'fv-podcast-publish-receipt/v1',
    package_id: request.package_id,
    buzzsprout_podcast_id: PODCAST_ID,
    buzzsprout_episode_id: String(episodeId),
    created,
    private: Boolean(finalReadback.private),
    title: finalReadback.title,
    published_at: finalReadback.published_at ?? finalReadback.publishedAt ?? null,
    audio_sha256: request.master.sha256,
    audio_bytes: request.master.bytes,
    artwork_sha256: request.artwork?.sha256 ?? null,
    rss,
    verified_at: new Date().toISOString(),
  };
  await fs.writeFile('publisher-receipt.json', JSON.stringify(receipt, null, 2));
  console.log(`PUBLISHED + HOST READBACK VERIFIED episode_id=${episodeId}`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error(`Publisher failed closed: ${error.message}`);
    process.exitCode = 1;
  });
}

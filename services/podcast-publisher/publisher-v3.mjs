import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileP = promisify(execFile);
const API_TOKEN = process.env.BUZZSPROUT_API_TOKEN;
const PODCAST_ID = process.env.BUZZSPROUT_PODCAST_ID || '2650509';
const REQUEST_FILE = process.env.PUBLISH_REQUEST_FILE;
const USER_AGENT = 'FinalVestigePodcastPublisher/2.4 (+https://finalvestige.com)';
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
const packageKeyFor = packageId => `FVPKG-${digest(Buffer.from(packageId, 'utf8')).slice(0, 40)}`;

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
  const packageId = str(input.package_id, 'package_id');
  const packageKey = packageKeyFor(packageId);

  if (mode === 'canary') {
    const title = str(m.title, 'metadata.title');
    if (!title.startsWith('FINAL VESTIGE PUBLISHER CANARY')) fail('canary title is not namespaced');
    if (!bool(m.private, 'metadata.private')) fail('canary must remain private');
    return {
      schema_version: 'fv-podcast-publish/v1', mode, package_id: packageId, package_key: packageKey,
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
    format: str(input.transcript.format || 'SRT', 'transcript.format').toUpperCase(),
    filename: str(input.transcript.filename || `${packageId}-transcript.srt`, 'transcript.filename'),
  } : null;
  if (transcript && !['SRT', 'JSON'].includes(transcript.format)) fail('unsupported transcript.format');
  const chapters = Array.isArray(input.chapters) ? input.chapters.map((chapter, index) => {
    if (!chapter || typeof chapter !== 'object' || Array.isArray(chapter)) fail(`chapters[${index}] must be an object`);
    const startTime = chapter.start_time;
    const seconds = chapterStartSeconds(startTime, `chapters[${index}].start_time`);
    const url = typeof chapter.url === 'string' && chapter.url.trim() ? chapter.url.trim() : null;
    if (url && !url.startsWith('https://')) fail(`chapters[${index}].url must be HTTPS`);
    return { title: str(chapter.title, `chapters[${index}].title`), start_time: startTime, start_seconds: seconds, url };
  }) : [];
  for (let i = 1; i < chapters.length; i++) {
    if (chapters[i].start_seconds <= chapters[i - 1].start_seconds) fail('chapters must be strictly increasing');
  }

  const request = {
    schema_version: 'fv-podcast-publish/v1', mode, package_id: packageId, package_key: packageKey,
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
    chapters,
    replace_media: input.replace_media === true,
    supersede_existing_private: input.supersede_existing_private === true,
    create_with_media_legacy: input.create_with_media_legacy === true,
    metadata: {
      title: str(m.title, 'metadata.title'), description,
      summary: typeof m.summary === 'string' ? m.summary : '',
      artist: typeof m.artist === 'string' && m.artist.trim() ? m.artist.trim() : 'Final Vestige Studios',
      explicit: bool(m.explicit, 'metadata.explicit'), private: bool(m.private, 'metadata.private'),
      episode_number: optionalInt(m.episode_number, 'metadata.episode_number'),
      season_number: optionalInt(m.season_number, 'metadata.season_number'),
      episode_type: typeof m.episode_type === 'string' && m.episode_type.trim() ? m.episode_type.trim().toLowerCase() : 'full',
      custom_url: typeof m.custom_url === 'string' && m.custom_url.trim() ? m.custom_url.trim() : null,
      tags: typeof m.tags === 'string' ? m.tags : '',
      published_at: typeof m.published_at === 'string' && m.published_at.trim() ? m.published_at.trim() : null,
    },
    rss_url: typeof input.rss_url === 'string' && input.rss_url.trim() ? input.rss_url.trim() : `https://feeds.buzzsprout.com/${PODCAST_ID}.rss`,
  };
  for (const [name, disposition] of Object.entries(request.qd)) if (disposition !== 'PASS') fail(`independent QD gate ${name} is not PASS`);
  if (!request.publication_authority.startsWith('FOUNDER_EXPLICIT_PUBLISH_')) fail('founder publication-authority evidence is missing');
  if (request.metadata.private) fail('release mode requires desired final private=false');
  if (!['full', 'trailer', 'bonus'].includes(request.metadata.episode_type)) fail('unsupported metadata.episode_type');
  if (request.metadata.custom_url && !request.metadata.custom_url.startsWith('https://')) fail('metadata.custom_url must be HTTPS');
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

function apiErrorText(json, text) {
  if (typeof json?.error === 'string') return json.error;
  if (json?.error?.message) return json.error.message;
  if (json && typeof json === 'object') {
    const fields = Object.entries(json).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : String(v)}`);
    if (fields.length) return fields.join('; ');
  }
  return text?.trim() || '';
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
  if (!res.ok) {
    const detail = apiErrorText(json, text);
    fail(`Buzzsprout ${method} ${path} failed: HTTP ${res.status}${detail ? ` ${detail}` : ''}`);
  }
  if (method === 'GET') cache.set(path, { etag: res.headers.get('etag'), json }); else clear(path);
  return json;
}

function chapterStartSeconds(value, label = 'chapter start_time') {
  if (typeof value === 'number' && Number.isFinite(value) && value >= 0) return value;
  if (typeof value !== 'string' || !value.trim()) fail(`${label} must be non-negative seconds, MM:SS, or HH:MM:SS`);
  const parts = value.trim().split(':').map(Number);
  if ((parts.length !== 2 && parts.length !== 3) || parts.some(v => !Number.isFinite(v) || v < 0)) fail(`${label} is invalid`);
  const [h, m, s] = parts.length === 3 ? parts : [0, parts[0], parts[1]];
  if (m >= 60 || s >= 60) fail(`${label} is invalid`);
  return h * 3600 + m * 60 + s;
}
function episodes(payload) { return Array.isArray(payload) ? payload : (Array.isArray(payload?.episodes) ? payload.episodes : []); }
function sameSeason(observed, governed) {
  if (governed === null) return observed === null || observed === undefined || observed === '';
  return Number(observed) === governed;
}
function sameVisibleIdentity(ep, r) {
  if (String(ep?.title || '').trim() !== r.metadata.title) return false;
  if (r.metadata.episode_number !== null && Number(ep.episode_number ?? ep.episodeNumber) !== r.metadata.episode_number) return false;
  return sameSeason(ep.season_number ?? ep.seasonNumber, r.metadata.season_number);
}
function sameGovernedMetadata(ep, r) {
  if (!sameVisibleIdentity(ep, r)) return false;
  if (String(ep?.description ?? '') !== r.metadata.description) return false;
  if (String(ep?.artist ?? '').trim() !== r.metadata.artist) return false;
  if (Boolean(ep?.explicit) !== r.metadata.explicit) return false;
  if (String(ep?.episode_type || 'full').toLowerCase() !== r.metadata.episode_type) return false;
  if (r.metadata.custom_url && String(ep?.custom_url || '').trim() !== r.metadata.custom_url) return false;
  return true;
}
async function resolveExisting(r, fresh = false) {
  if (fresh) clear('/episodes');
  const all = episodes(await apiJson('/episodes'));
  const exact = all.filter(ep => sameGovernedMetadata(ep, r));
  if (exact.length > 1) fail('multiple Buzzsprout episodes match the exact governed metadata identity');
  const visible = all.filter(ep => sameVisibleIdentity(ep, r));
  if (!exact.length && visible.length) fail('episode title/number/season identity collision exists with nonmatching governed metadata');
  return exact[0] || null;
}

function canaryWav() {
  const sampleRate = 48000, channels = 2, frames = sampleRate, dataSize = frames * channels * 2;
  const out = Buffer.alloc(44 + dataSize);
  out.write('RIFF', 0); out.writeUInt32LE(36 + dataSize, 4); out.write('WAVE', 8);
  out.write('fmt ', 12); out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(channels, 22);
  out.writeUInt32LE(sampleRate, 24); out.writeUInt32LE(sampleRate * channels * 2, 28);
  out.writeUInt16LE(channels * 2, 32); out.writeUInt16LE(16, 34); out.write('data', 36); out.writeUInt32LE(dataSize, 40);
  for (let i = 0; i < frames; i++) {
    const sample = Math.round(Math.sin(2 * Math.PI * 440 * i / sampleRate) * 1500);
    const off = 44 + i * 4; out.writeInt16LE(sample, off); out.writeInt16LE(sample, off + 2);
  }
  return out;
}

function privateMetadata(r) {
  const body = {
    title: r.metadata.title,
    description: r.metadata.description,
    artist: r.metadata.artist,
    explicit: r.metadata.explicit,
    private: true,
  };
  if (r.metadata.episode_number !== null) body.episode_number = r.metadata.episode_number;
  if (r.metadata.season_number !== null) body.season_number = r.metadata.season_number;
  if (r.metadata.tags) body.tags = r.metadata.tags;
  if (r.metadata.episode_type) body.episode_type = r.metadata.episode_type;
  if (r.metadata.custom_url) body.custom_url = r.metadata.custom_url;
  return body;
}

async function createPrivate(r, artworkBytes) {
  const endpoint = `https://www.buzzsprout.com/api/${PODCAST_ID}/episodes`;
  let res;
  if (r.artwork && artworkBytes) {
    const form = new FormData();
    const metadata = privateMetadata(r);
    for (const [key, value] of Object.entries(metadata)) form.append(key, String(value));
    form.append('artwork_file', new Blob([artworkBytes], { type: r.artwork.mime }), r.artwork.filename);
    res = await fetch(endpoint, { method: 'POST', headers: authHeaders(), body: form });
  } else {
    res = await fetch(endpoint, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json; charset=utf-8' }),
      body: JSON.stringify(privateMetadata(r)),
    });
  }
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) {
    const detail = apiErrorText(json, text);
    fail(`Buzzsprout POST /episodes failed: HTTP ${res.status}${detail ? ` ${detail}` : ''}`);
  }
  clear('/episodes');
  return json;
}

async function createPrivateWithMediaLegacy(r, artworkBytes, audioBytes) {
  const endpoint = `https://www.buzzsprout.com/api/${PODCAST_ID}/episodes`;
  const form = new FormData();
  const metadata = privateMetadata(r);
  for (const [key, value] of Object.entries(metadata)) form.append(key, String(value));
  if (r.artwork && artworkBytes) {
    form.append('artwork_file', new Blob([artworkBytes], { type: r.artwork.mime }), r.artwork.filename);
  }
  form.append('audio_file', new Blob([audioBytes], { type: r.master.mime }), r.master.filename);
  form.append('email_user_after_audio_processed', 'false');
  const res = await fetch(endpoint, { method: 'POST', headers: authHeaders(), body: form });
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) {
    const detail = apiErrorText(json, text);
    fail(`Buzzsprout legacy create-with-media failed: HTTP ${res.status}${detail ? ` ${detail}` : ''}`);
  }
  if (res.headers.get('deprecation')) console.log('Buzzsprout legacy create audio_file path acknowledged deprecation');
  clear('/episodes');
  return json;
}

async function uploadMedia(id, bytes, filename, mime) {
  const episodeId = encodeURIComponent(id);
  const startPath = `/episodes/${episodeId}/uploads`;
  const started = await apiJson(startPath, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ filename, type: mime, byte_size: bytes.length }),
  });
  const upload = started?.upload ?? started;
  if (!upload?.id) fail('Buzzsprout upload start did not return an upload id');
  if (upload.multipart === true) fail('unexpected multipart upload response for governed audio');
  if (!upload.upload_url) fail('Buzzsprout upload start did not return an upload URL');

  const put = await fetch(upload.upload_url, {
    method: 'PUT',
    headers: { 'Content-Length': String(bytes.length) },
    body: bytes,
  });
  if (!put.ok) fail(`Buzzsprout media object PUT failed: HTTP ${put.status}`);

  const uploadId = encodeURIComponent(upload.id);
  await apiJson(`/episodes/${episodeId}/uploads/${uploadId}/complete`, { method: 'POST' });
  clear(`/episodes/${episodeId}`);
  clear('/episodes');
}

async function replaceMediaLegacy(id, bytes, filename, mime) {
  const episodeId = encodeURIComponent(id);
  const form = new FormData();
  form.append('audio_file', new Blob([bytes], { type: mime }), filename);
  form.append('email_user_after_audio_processed', 'false');
  const res = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes/${episodeId}`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: form,
  });
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) {
    const detail = apiErrorText(json, text);
    fail(`Buzzsprout legacy media replacement failed: HTTP ${res.status}${detail ? ` ${detail}` : ''}`);
  }
  if (res.headers.get('deprecation')) console.log('Buzzsprout legacy audio_file replacement path acknowledged deprecation');
  clear(`/episodes/${episodeId}`);
  clear('/episodes');
  return json;
}

async function retirePrivateEpisode(id, r) {
  const observed = await getEpisode(id, true);
  verifyCore(observed, r);
  if (Boolean(observed.private) !== true) fail('supersede_existing_private requires the exact existing episode to remain private');
  const path = `/episodes/${encodeURIComponent(id)}`;
  const retiredTitle = `FINAL VESTIGE RETIRED PRIVATE BUILD — ${r.package_id} — ${id}`;
  await apiJson(path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({
      title: retiredTitle,
      description: 'Retired private pre-HQ processing build. Not for publication.',
      private: true,
      custom_url: null,
    }),
  });
  clear('/episodes');
  const retired = await getEpisode(id, true);
  if (String(retired?.title || '') !== retiredTitle || Boolean(retired?.private) !== true) {
    fail('retired private episode readback mismatch');
  }
  console.log(`Retired prior private release build episode_id=${id}`);
  return String(id);
}

async function getEpisode(id, fresh = false) {
  const path = `/episodes/${encodeURIComponent(id)}`;
  if (fresh) clear(path);
  return apiJson(path);
}
function verifyCore(ep, r) {
  if (!ep || typeof ep !== 'object') fail('Buzzsprout episode readback missing');
  if (!sameGovernedMetadata(ep, r)) fail('Buzzsprout episode governed metadata identity mismatch');
  if (r.artwork && !ep.artwork_url) fail('Buzzsprout episode artwork is missing');
  if (!ep.guid || !String(ep.guid).startsWith('Buzzsprout')) fail('Buzzsprout host-assigned episode GUID is missing or unexpected');
}

async function probeAudioFile(path, label) {
  let stdout, hashOut;
  try {
    ({ stdout } = await execFileP('ffprobe', ['-v','error','-show_entries','stream=codec_name,sample_rate,channels,bit_rate:format=bit_rate,duration','-of','json',path], { maxBuffer: 1024 * 1024 }));
    ({ stdout: hashOut } = await execFileP('ffmpeg', ['-v','error','-i',path,'-map','0:a:0','-f','hash','-hash','sha256','-'], { maxBuffer: 1024 * 1024 }));
  } catch { fail(`${label} audio probe runtime is unavailable`); }
  const probe = JSON.parse(stdout);
  const audio = (probe.streams || []).find(s => s.codec_name);
  if (!audio) fail(`${label} has no audio stream`);
  const hashMatch = String(hashOut || '').match(/SHA256=([0-9a-f]{64})/i);
  if (!hashMatch) fail(`${label} decoded-PCM fingerprint is unavailable`);
  return {
    codec: String(audio.codec_name || ''),
    sample_rate: Number(audio.sample_rate || 0),
    channels: Number(audio.channels || 0),
    bit_rate: Number(audio.bit_rate || probe.format?.bit_rate || 0),
    duration: Number(probe.format?.duration || 0),
    pcm_sha256: hashMatch[1].toLowerCase(),
  };
}
async function probeSourceAudio(audioBytes, packageKey) {
  const path = `/tmp/fv-source-${packageKey}.mp3`;
  await fs.writeFile(path, audioBytes);
  const probe = await probeAudioFile(path, 'governed source master');
  if (probe.codec !== 'mp3') fail(`governed source codec is ${probe.codec}, expected mp3`);
  if (probe.channels !== 2) fail(`governed source channels=${probe.channels}, expected stereo`);
  if (probe.sample_rate < 44100) fail(`governed source sample_rate=${probe.sample_rate}, below release floor`);
  if (probe.bit_rate < 190000) fail(`governed source bitrate=${probe.bit_rate}, below ~192 kbps release floor`);
  return { ...probe, bytes: audioBytes.length, path };
}

async function renderVerificationPcm(inputPath, label) {
  const key = digest(Buffer.from(`${label}:${inputPath}`, 'utf8')).slice(0, 16);
  const outPath = `/tmp/fv-verify-${key}.s16le`;
  try {
    await execFileP('ffmpeg', [
      '-v','error','-y','-i',inputPath,'-map','0:a:0','-ac','1','-ar','8000','-f','s16le',outPath
    ], { maxBuffer: 1024 * 1024 });
  } catch {
    fail(`${label} verification PCM render failed`);
  }
  return fs.readFile(outPath);
}
function pcmSample(buf, index) {
  if (index < 0 || index * 2 + 1 >= buf.length) return null;
  return buf.readInt16LE(index * 2) / 32768;
}
function correlationAtLag(source, host, starts, windowSamples, lag, step = 8) {
  let n = 0, sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
  for (const start of starts) {
    for (let i = 0; i < windowSamples; i += step) {
      const x = pcmSample(source, start + i);
      const y = pcmSample(host, start + i + lag);
      if (x === null || y === null) continue;
      n++; sx += x; sy += y; sxx += x*x; syy += y*y; sxy += x*y;
    }
  }
  if (n < 1000) return null;
  const cov = sxy - (sx * sy / n);
  const vx = sxx - (sx * sx / n);
  const vy = syy - (sy * sy / n);
  if (vx <= 0 || vy <= 0) return null;
  return {
    correlation: cov / Math.sqrt(vx * vy),
    rms_ratio: Math.sqrt(syy / Math.max(sxx, Number.EPSILON)),
    points: n,
  };
}
async function verifyLossyAudioEquivalence(sourcePath, hostPath) {
  const [source, host] = await Promise.all([
    renderVerificationPcm(sourcePath, 'governed source master'),
    renderVerificationPcm(hostPath, 'host derivative')
  ]);
  const sourceSamples = Math.floor(source.length / 2);
  const hostSamples = Math.floor(host.length / 2);
  const minSamples = Math.min(sourceSamples, hostSamples);
  const windowSamples = 5 * 8000;
  if (minSamples < windowSamples * 2) fail('audio is too short for equivalence verification');

  const candidateStarts = [];
  for (let k = 1; k <= 12; k++) {
    const start = Math.floor((minSamples - windowSamples) * k / 13);
    candidateStarts.push(start);
  }
  let energyStart = candidateStarts[0], bestEnergy = -1;
  for (const start of candidateStarts) {
    let e = 0, n = 0;
    for (let i = 0; i < windowSamples; i += 16) {
      const x = pcmSample(source, start + i);
      if (x === null) continue;
      e += x*x; n++;
    }
    const mean = n ? e / n : 0;
    if (mean > bestEnergy) { bestEnergy = mean; energyStart = start; }
  }

  let bestLag = 0, best = { correlation: -2, rms_ratio: 0, points: 0 };
  for (let lag = -800; lag <= 800; lag += 4) {
    const result = correlationAtLag(source, host, [energyStart], windowSamples, lag, 8);
    if (result && result.correlation > best.correlation) { best = result; bestLag = lag; }
  }
  for (let lag = bestLag - 6; lag <= bestLag + 6; lag++) {
    const result = correlationAtLag(source, host, [energyStart], windowSamples, lag, 4);
    if (result && result.correlation > best.correlation) { best = result; bestLag = lag; }
  }

  const finalWindow = 3 * 8000;
  const finalStarts = [];
  for (let k = 1; k <= 16; k++) {
    finalStarts.push(Math.floor((minSamples - finalWindow) * k / 17));
  }
  const final = correlationAtLag(source, host, finalStarts, finalWindow, bestLag, 8);
  if (!final) fail('host derivative waveform equivalence could not be measured');
  console.log(`HOST AUDIO EQUIVALENCE MEASURED correlation=${final.correlation.toFixed(8)} rms_ratio=${final.rms_ratio.toFixed(8)} lag_samples=${bestLag}`);
  if (final.correlation < 0.99) {
    fail(`host derivative waveform similarity=${final.correlation.toFixed(6)}, below governed 0.99 floor`);
  }
  if (final.rms_ratio < 0.95 || final.rms_ratio > 1.05) {
    fail(`host derivative RMS ratio=${final.rms_ratio.toFixed(6)}, outside governed 0.95-1.05 window`);
  }
  return {
    method: 'aligned_mono_8khz_waveform_correlation',
    correlation: Number(final.correlation.toFixed(8)),
    rms_ratio: Number(final.rms_ratio.toFixed(8)),
    lag_samples_8khz: bestLag,
    lag_ms: Number((bestLag / 8).toFixed(3)),
    points: final.points,
  };
}
async function probeHostAudio(audioUrl, episodeId, sourceProbe, { allowNotReady = false } = {}) {
  let res = await fetch(audioUrl, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT } });
  if (res.status === 404) {
    res = await fetch(audioUrl, { redirect: 'follow', headers: authHeaders() });
  }
  if (res.status === 404 && allowNotReady) return null;
  if (!res.ok) fail(`host audio download failed: HTTP ${res.status}`);
  const bytes = Buffer.from(await res.arrayBuffer());
  const path = `/tmp/fv-buzzsprout-${episodeId}.mp3`;
  await fs.writeFile(path, bytes);
  const probe = await probeAudioFile(path, 'host derivative');
  if (probe.codec !== 'mp3') fail(`host derivative codec is ${probe.codec}, expected mp3`);
  if (probe.channels !== 2) fail(`host derivative channels=${probe.channels}, expected stereo`);
  if (probe.sample_rate < 44100) fail(`host derivative sample_rate=${probe.sample_rate}, below governed release floor`);
  if (probe.bit_rate < 190000) fail(`host derivative bitrate=${probe.bit_rate}, below governed ~192 kbps release floor`);
  if (sourceProbe) {
    if (probe.codec !== sourceProbe.codec || probe.channels !== sourceProbe.channels || probe.sample_rate !== sourceProbe.sample_rate) {
      fail('host derivative stream format differs from governed source master');
    }
    if (sourceProbe.duration > 0 && probe.duration > 0 && Math.abs(probe.duration - sourceProbe.duration) > 0.1) {
      fail(`host derivative duration differs from governed source by ${Math.abs(probe.duration - sourceProbe.duration).toFixed(3)}s`);
    }
    let equivalence = null;
    const pcmExact = probe.pcm_sha256 === sourceProbe.pcm_sha256;
    if (!pcmExact) {
      equivalence = await verifyLossyAudioEquivalence(sourceProbe.path, path);
      console.log(`HOST AUDIO WAVEFORM EQUIVALENCE PASS correlation=${equivalence.correlation} rms_ratio=${equivalence.rms_ratio} lag_ms=${equivalence.lag_ms}`);
    }
    return {
      ...probe,
      bytes: bytes.length,
      pcm_exact_match: pcmExact,
      waveform_equivalence: equivalence,
      governed_source_pcm_sha256: sourceProbe.pcm_sha256,
    };
  }
  return { ...probe, bytes: bytes.length, pcm_exact_match: null, waveform_equivalence: null };
}
function providerFlags(ep) {
  return {
    hq: typeof ep?.hq === 'boolean' ? ep.hq : null,
    magic_mastering: typeof ep?.magic_mastering === 'boolean' ? ep.magic_mastering : null,
  };
}
function verifyAudioReady(ep, r) {
  if (r.mode !== 'release') return;
  if (!ep.audio_url) fail('Buzzsprout audio_url is not ready');
}
async function waitForProcessedPrivate(id, r) {
  for (let i = 0; i < 120; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    if (Boolean(ep.private) !== true) fail('episode became public before private-stage verification completed');
    const duration = Number(ep.duration);
    if (r.mode === 'release' && r.create_with_media_legacy) {
      if (ep.audio_url && Number.isFinite(duration) && duration > 0) {
        console.log(`PRIVATE MEDIA PROCESSING COMPLETE episode_id=${id} duration=${duration} hq=${JSON.stringify(ep.hq)} magic_mastering=${JSON.stringify(ep.magic_mastering)}`);
        return { ep };
      }
    } else if (ep.audio_url) {
      return { ep };
    }
    if (i % 6 === 0) console.log(`PRIVATE MEDIA WAIT episode_id=${id} duration=${JSON.stringify(ep.duration)} audio_url=${Boolean(ep.audio_url)}`);
    await sleep(10000);
  }
  fail('Buzzsprout audio did not finish private processing within bounded verification window');
}

async function rssContainsTitle(r) {
  const res = await fetch(r.rss_url, { redirect: 'follow', headers: { 'User-Agent': USER_AGENT, 'Cache-Control': 'no-cache' } });
  if (!res.ok) return false;
  return (await res.text()).includes(r.metadata.title);
}
async function unpublishImmediately(id, r, reason) {
  const path = `/episodes/${encodeURIComponent(id)}`;
  try {
    await apiJson(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json; charset=utf-8' }, body: JSON.stringify({ private: true }) });
  } catch (error) {
    console.error(`Emergency unpublish failed after ${reason}: ${error.message}`);
  }
}
async function scheduleForPrivateVerification(id, r) {
  const path = `/episodes/${encodeURIComponent(id)}`;
  const verifyAt = new Date(Date.now() + 60 * 60 * 1000).toISOString();
  await apiJson(path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ private: false, published_at: verifyAt }),
  });
  const ep = await getEpisode(id, true); verifyCore(ep, r);
  const scheduled = Date.parse(ep.published_at || '');
  if (!Number.isFinite(scheduled) || scheduled < Date.now() + 30 * 60 * 1000) {
    await unpublishImmediately(id, r, 'invalid verification schedule');
    fail('Buzzsprout did not preserve the future verification schedule');
  }
  if (await rssContainsTitle(r)) {
    await unpublishImmediately(id, r, 'premature RSS appearance');
    fail('scheduled verification episode appeared in RSS before final publication');
  }
  console.log(`Future verification window armed episode_id=${id} published_at=${ep.published_at}`);
  return ep;
}
async function verifyScheduledHostAudio(id, r, sourceProbe) {
  for (let i = 0; i < 90; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    const scheduled = Date.parse(ep.published_at || '');
    if (!Number.isFinite(scheduled) || scheduled <= Date.now() + 5 * 60 * 1000) {
      await unpublishImmediately(id, r, 'verification window too close to publication');
      fail('host verification window expired before audio verification completed');
    }
    if (await rssContainsTitle(r)) {
      await unpublishImmediately(id, r, 'premature RSS appearance');
      fail('scheduled verification episode appeared in RSS before final publication');
    }
    if (ep.audio_url) {
      try {
        const host_probe = await probeHostAudio(ep.audio_url, id, sourceProbe, { allowNotReady: true });
        if (host_probe) return { ep, host_probe };
      } catch (error) {
        await unpublishImmediately(id, r, 'host derivative verification failure');
        throw error;
      }
    }
    await sleep(10000);
  }
  await unpublishImmediately(id, r, 'host derivative timeout');
  fail('host derivative was not readable within the bounded verification window');
}

async function uploadTranscript(id, transcript) {
  if (!transcript) return { skipped: true };
  const form = new FormData();
  const mime = transcript.format === 'JSON' ? 'application/json' : 'application/x-subrip';
  form.append('transcript_file', new Blob([Buffer.from(transcript.content, 'utf8')], { type: mime }), transcript.filename);
  form.append('transcript_format', transcript.format.toLowerCase());
  const res = await fetch(`https://www.buzzsprout.com/api/${PODCAST_ID}/episodes/${encodeURIComponent(id)}/transcript`, { method: 'POST', headers: authHeaders(), body: form });
  if (!res.ok) fail(`Buzzsprout transcript upload failed: HTTP ${res.status}`);
  return { skipped: false, format: transcript.format };
}
async function uploadAndVerifyChapters(id, chapters) {
  if (!chapters.length) return { skipped: true, count: 0 };
  const path = `/episodes/${encodeURIComponent(id)}/chapters`;
  const payload = chapters.map(({ title, start_time, url }) => ({ title, start_time, ...(url ? { url } : {}) }));
  await apiJson(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ chapters: payload }),
  });
  clear(path);
  const observed = await apiJson(path);
  if (!Array.isArray(observed) || observed.length !== chapters.length) fail('Buzzsprout chapter readback count mismatch');
  for (let i = 0; i < chapters.length; i++) {
    if (String(observed[i]?.title || '').trim() !== chapters[i].title) fail(`Buzzsprout chapter ${i + 1} title mismatch`);
    const observedSeconds = chapterStartSeconds(observed[i]?.start_time, `Buzzsprout chapter ${i + 1} start_time`);
    if (Math.abs(observedSeconds - chapters[i].start_seconds) > 0.01) fail(`Buzzsprout chapter ${i + 1} start_time mismatch`);
  }
  return { skipped: false, count: chapters.length, verified: true };
}

async function makePublic(id, r) {
  const path = `/episodes/${encodeURIComponent(id)}`;
  const body = { private: false };
  if (r.metadata.published_at) body.published_at = r.metadata.published_at;
  try {
    await apiJson(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json; charset=utf-8' }, body: JSON.stringify(body) });
  } catch (error) {
    const observed = await getEpisode(id, true); verifyCore(observed, r);
    if (Boolean(observed.private) !== false) throw error;
  }
  for (let i = 0; i < 18; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    if (Boolean(ep.private) === false) {
      verifyAudioReady(ep, r);
      console.log(
        `PUBLIC STATE VERIFIED episode_id=${id} private=${Boolean(ep.private)} published_at=${String(ep.published_at || '')} inactive_at=${String(ep.inactive_at || '')} duration=${String(ep.duration ?? '')} audio_url=${Boolean(ep.audio_url)} hq=${JSON.stringify(ep.hq)} magic_mastering=${JSON.stringify(ep.magic_mastering)}`
      );
      return ep;
    }
    await sleep(10000);
  }
  fail('Buzzsprout episode did not reach public state within bounded verification window');
}

async function bindCanonicalRssUrl(r) {
  if (r.mode !== 'release') return r;
  const res = await fetch(`https://www.buzzsprout.com/api/podcasts/${encodeURIComponent(PODCAST_ID)}`, {
    headers: authHeaders()
  });
  const text = await res.text(); let json = null; try { json = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) {
    const detail = apiErrorText(json, text);
    fail(`Buzzsprout podcast readback failed: HTTP ${res.status}${detail ? ` ${detail}` : ''}`);
  }
  const rss = str(json?.rss_url, 'Buzzsprout podcast.rss_url');
  if (!rss.startsWith('https://')) fail('Buzzsprout canonical RSS URL is not HTTPS');
  r.rss_url = rss;
  const u = new URL(rss);
  console.log(`CANONICAL RSS BOUND ${u.hostname}${u.pathname}`);
  return r;
}

function decodeXmlEntities(value) {
  return String(value)
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}
async function fetchRssEpisodeEntry(r, expectedGuid = null) {
  const feedUrl = new URL(r.rss_url);
  feedUrl.searchParams.set('_fv', String(Date.now()));
  const res = await fetch(feedUrl, {
    redirect: 'follow',
    headers: {
      'User-Agent': USER_AGENT,
      'Cache-Control': 'no-cache, no-store, max-age=0',
      Pragma: 'no-cache'
    }
  });
  if (!res.ok) return { found: false, status: res.status, item_count: 0 };
  const xml = await res.text();
  const items = xml.match(/<item\b[\s\S]*?<\/item>/gi) || [];
  let item = null;
  if (expectedGuid) {
    item = items.find(candidate => {
      const match = candidate.match(/<guid\b[^>]*>([\s\S]*?)<\/guid>/i);
      return match && decodeXmlEntities(match[1].replace(/<!\[CDATA\[|\]\]>/g, '').trim()) === expectedGuid;
    }) || null;
  }
  if (!item) {
    item = items.find(candidate => decodeXmlEntities(candidate).includes(r.metadata.title)) || null;
  }
  if (!item) return { found: false, status: res.status, item_count: items.length };
  const match = item.match(/<enclosure\b[^>]*\burl=(["'])(.*?)\1/i);
  if (!match) fail('RSS episode item is missing an enclosure URL');
  return {
    found: true,
    url: res.url,
    title_found: true,
    enclosure_url: decodeXmlEntities(match[2]),
    item_sha256: digest(Buffer.from(item, 'utf8')),
    item_count: items.length,
  };
}
async function verifyRssEnclosureAndAudio(id, r, sourceProbe) {
  let lastStatus = null, lastItemCount = null;
  for (let i = 0; i < 180; i++) {
    const ep = await getEpisode(id, true); verifyCore(ep, r);
    if (Boolean(ep.private) !== false) fail('episode left public state during RSS/audio verification');
    const rss = await fetchRssEpisodeEntry(r, String(ep.guid || ''));
    lastStatus = rss?.status ?? 200;
    lastItemCount = rss?.item_count ?? null;
    if (!rss?.found) {
      if (i % 12 === 0) console.log(`RSS WAIT episode_id=${id} status=${lastStatus} items=${lastItemCount}`);
      await sleep(5000);
      continue;
    }
    console.log(`RSS EPISODE LOCATED episode_id=${id} items=${rss.item_count}`);
    for (let j = 0; j < 20; j++) {
      try {
        const probe = await probeHostAudio(rss.enclosure_url, id, sourceProbe, { allowNotReady: true });
        if (probe) return { ep, probe, rss };
      } catch (error) {
        await unpublishImmediately(id, r, 'RSS enclosure audio verification failure');
        throw error;
      }
      await sleep(3000);
    }
    await unpublishImmediately(id, r, 'RSS enclosure remained unreadable');
    fail('RSS enclosure was published but its hosted audio remained unreadable');
  }
  await unpublishImmediately(id, r, 'RSS propagation timeout');
  fail(`RSS did not contain the exact episode within the bounded propagation window (status=${lastStatus}, items=${lastItemCount})`);
}
async function writeReceipt(data) {
  await fs.writeFile('publisher-receipt.json', JSON.stringify({ schema_version:'fv-podcast-publish-receipt/v1', ...data, verified_at:new Date().toISOString() }, null, 2));
}

async function main() {
  if (!REQUEST_FILE) fail('PUBLISH_REQUEST_FILE is not configured');
  const r = validateRequest(JSON.parse(await fs.readFile(REQUEST_FILE, 'utf8')));
  verifyRuntimeAuthority(r);
  await bindCanonicalRssUrl(r);
  console.log(`Validated ${r.mode} request ${r.package_id}`);

  const sourceAudio = r.mode === 'canary' ? canaryWav() : await downloadAndVerify(r.master, 'master audio');
  const sourceArt = r.mode === 'release' && r.artwork ? await downloadAndVerify(r.artwork, 'artwork') : null;
  const source_probe = r.mode === 'release' ? await probeSourceAudio(sourceAudio, r.package_key) : null;
  if (r.mode === 'release') console.log('Exact master/artwork bytes + source PCM fingerprint verified before host mutation');

  let ep = await resolveExisting(r, true), created = false, retiredEpisodeId = null;
  if (r.mode === 'release' && r.supersede_existing_private && ep) {
    const existingId = ep?.id ?? ep?.episode_id;
    if (!existingId) fail('existing Buzzsprout episode did not expose an episode id');
    retiredEpisodeId = await retirePrivateEpisode(existingId, r);
    ep = null;
  }
  if (!ep) {
    try {
      ep = r.mode === 'release' && r.create_with_media_legacy
        ? await createPrivateWithMediaLegacy(r, sourceArt, sourceAudio)
        : await createPrivate(r, sourceArt);
      created = true;
    } catch (error) {
      console.warn('Create outcome uncertain/failed; reconciling by exact governed metadata before any retry.');
      ep = await resolveExisting(r, true); if (!ep) throw error;
    }
  }
  const id = ep?.id ?? ep?.episode_id;
  if (!id) fail('Buzzsprout response did not expose an episode id');

  ep = await getEpisode(id, true); verifyCore(ep, r);

  const observedDuration = Number(ep.duration);
  if (r.mode === 'release' && !created) {
    const mediaLocator = ep.audio_url ? (() => { try { const u = new URL(ep.audio_url); return `${u.hostname}${u.pathname}`; } catch { return 'invalid-url'; } })() : '';
    console.log(`Observed exact private release state episode_id=${id} private=${Boolean(ep.private)} duration_raw=${JSON.stringify(ep.duration)} duration_num=${observedDuration} audio_url=${Boolean(ep.audio_url)} media_locator=${mediaLocator} artwork_url=${Boolean(ep.artwork_url)} hq=${JSON.stringify(ep.hq)} magic_mastering=${JSON.stringify(ep.magic_mastering)} guid=${String(ep.guid || '')} published_at=${String(ep.published_at || '')}`);
  }
  const releaseResumeProcessing = r.mode === 'release' && !created && observedDuration === -1;
  const releaseResumeProcessed = r.mode === 'release' && !created && Boolean(ep.audio_url);

  if (r.mode === 'release' && !created && !releaseResumeProcessing && !releaseResumeProcessed && !r.replace_media) {
    fail('existing release episode has no package-verifiable media state; refusing to attach or replace media');
  }

  if (r.mode === 'release' && r.replace_media) {
    if (created) fail('replace_media is valid only for an existing exact private release episode');
    if (Boolean(ep.private) !== true) fail('replace_media requires the exact existing episode to remain private');
    console.log(`Replacing private release media with exact governed master through dashboard-compatible audio_file path episode_id=${id}`);
    await replaceMediaLegacy(id, sourceAudio, r.master.filename, r.master.mime);
    ep = await getEpisode(id, true); verifyCore(ep, r);
  } else if (r.mode === 'release' && r.create_with_media_legacy && created) {
    console.log(`Fresh private release episode created with exact governed media episode_id=${id}`);
  } else if (!ep.audio_url && !releaseResumeProcessing) {
    const filename = r.mode === 'canary' ? 'fv-publisher-canary.wav' : r.master.filename;
    const mime = r.mode === 'canary' ? 'audio/wav' : r.master.mime;
    await uploadMedia(id, sourceAudio, filename, mime);
  } else if (releaseResumeProcessing || releaseResumeProcessed) {
    console.log(`Resuming exact private release episode_id=${id} without re-uploading media`);
  }

  const { ep: privateEp } = await waitForProcessedPrivate(id, r);
  if (r.mode === 'canary') {
    await writeReceipt({ mode:'canary', package_id:r.package_id, package_key:r.package_key, buzzsprout_podcast_id:PODCAST_ID, buzzsprout_episode_id:String(id), buzzsprout_guid:String(privateEp.guid), created, private:true, title:privateEp.title });
    console.log(`PRIVATE CANARY VERIFIED episode_id=${id}`); return;
  }

  const prePublic = await getEpisode(id, true); verifyCore(prePublic, r);
  if (Boolean(prePublic.private) !== true) fail('release episode is not private immediately before final publication');
  if (prePublic.hq === false) fail('Buzzsprout reports the fresh release episode is not HQ; refusing public publication');
  if (prePublic.magic_mastering === true) fail('Buzzsprout reports Magic Mastering processing on the fresh release episode; refusing public publication');

  const chapter_receipt = await uploadAndVerifyChapters(id, r.chapters);
  const transcript_receipt = await uploadTranscript(id, r.transcript);

  let publicEp;
  let final_host_probe;
  let rss;
  try {
    publicEp = await makePublic(id, r);
    const verified = await verifyRssEnclosureAndAudio(id, r, source_probe);
    publicEp = verified.ep;
    final_host_probe = verified.probe;
    rss = verified.rss;
  } catch (error) {
    await unpublishImmediately(id, r, 'post-publication RSS/audio verification failure');
    throw error;
  }
  console.log(`PUBLISHED + RSS ENCLOSURE EXACT-PCM VERIFIED episode_id=${id}`);
  await writeReceipt({
    mode:'release', package_id:r.package_id, package_key:r.package_key,
    buzzsprout_podcast_id:PODCAST_ID, buzzsprout_episode_id:String(id), buzzsprout_guid:String(publicEp.guid),
    created, private:false, title:publicEp.title, published_at:publicEp.published_at ?? null,
    audio_sha256:r.master.sha256, audio_bytes:r.master.bytes, artwork_sha256:r.artwork?.sha256 ?? null,
    source_audio_probe:source_probe, final_host_audio_probe:final_host_probe, provider_flags:providerFlags(publicEp),
    retired_private_episode_id:retiredEpisodeId,
    chapters:chapter_receipt, transcript:transcript_receipt, audio_url:publicEp.audio_url, rss
  });
  console.log(`PUBLISHED + HOST/RSS VERIFIED episode_id=${id}`);
}

if (import.meta.url === `file://${process.argv[1]}`) main().catch(error => { console.error(`Publisher failed closed: ${error.message}`); process.exitCode = 1; });

const REQUIRED_QD = ['exact_master', 'visual_rights', 'release_copy'];

export function stableGuid(pkg) {
  const digest = String(pkg.audio?.sha256 || '').slice(0, 16);
  if (!/^POD-[0-9]{3}$/.test(pkg.package_id || '') || !/^[a-f0-9]{16}$/.test(digest)) {
    throw new Error('INVALID_PACKAGE_IDENTITY');
  }
  return `FinalVestige-${pkg.package_id}-${digest}`;
}

export function validatePackage(pkg) {
  if (!pkg || typeof pkg !== 'object') throw new Error('INVALID_PACKAGE');
  for (const gate of REQUIRED_QD) {
    if (pkg.qd?.[gate] !== 'PASS') throw new Error(`QD_GATE_NOT_PASS:${gate}`);
  }
  if (!pkg.audio?.url || !/^https:\/\//.test(pkg.audio.url)) throw new Error('AUDIO_URL_REQUIRED');
  if (!/^[a-f0-9]{64}$/.test(pkg.audio.sha256 || '')) throw new Error('AUDIO_SHA256_REQUIRED');
  if (!pkg.title || !pkg.description) throw new Error('METADATA_REQUIRED');
  if (pkg.artwork?.url && !/^https:\/\//.test(pkg.artwork.url)) throw new Error('INVALID_ARTWORK_URL');
  return true;
}

function headers(token) {
  return {
    Authorization: `Token token=${token}`,
    'User-Agent': 'FinalVestigePodcastPublisher/1.0 (+https://finalvestige.com)',
    'Content-Type': 'application/json; charset=utf-8',
    Accept: 'application/json'
  };
}

async function jsonOrText(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {raw: text.slice(0, 1000)}; }
}

export async function listEpisodes({fetchImpl = fetch, token, podcastId}) {
  const res = await fetchImpl(`https://www.buzzsprout.com/api/${podcastId}/episodes.json`, {headers: headers(token)});
  if (!res.ok) throw new Error(`BUZZSPROUT_LIST_${res.status}`);
  return jsonOrText(res);
}

export async function findByGuid(opts, guid) {
  const episodes = await listEpisodes(opts);
  return Array.isArray(episodes) ? episodes.find(e => e.guid === guid) || null : null;
}

export async function createPrivateEpisode({fetchImpl = fetch, token, podcastId, pkg}) {
  validatePackage(pkg);
  const guid = stableGuid(pkg);
  const existing = await findByGuid({fetchImpl, token, podcastId}, guid);
  if (existing) return {created: false, reconciled: true, episode: existing, guid};

  const payload = {
    title: pkg.title,
    description: pkg.description,
    summary: pkg.summary || '',
    artist: pkg.artist || 'Final Vestige',
    guid,
    episode_number: pkg.episode_number ?? 1,
    season_number: pkg.season_number ?? null,
    explicit: Boolean(pkg.explicit),
    private: true,
    email_user_after_audio_processed: false,
    audio_url: pkg.audio.url,
    ...(pkg.artwork?.url ? {artwork_url: pkg.artwork.url} : {})
  };

  let res;
  try {
    res = await fetchImpl(`https://www.buzzsprout.com/api/${podcastId}/episodes.json`, {
      method: 'POST', headers: headers(token), body: JSON.stringify(payload)
    });
  } catch (err) {
    const reconciled = await findByGuid({fetchImpl, token, podcastId}, guid);
    if (reconciled) return {created: false, reconciled: true, episode: reconciled, guid};
    throw new Error(`AMBIGUOUS_CREATE_NO_RECONCILIATION:${err?.message || 'network'}`);
  }
  if (res.status !== 201) {
    const body = await jsonOrText(res);
    if (res.status >= 500) {
      const reconciled = await findByGuid({fetchImpl, token, podcastId}, guid);
      if (reconciled) return {created: false, reconciled: true, episode: reconciled, guid};
    }
    throw new Error(`BUZZSPROUT_CREATE_${res.status}:${JSON.stringify(body).slice(0, 500)}`);
  }
  return {created: true, reconciled: false, episode: await jsonOrText(res), guid};
}

export async function verifyEpisode({fetchImpl = fetch, token, podcastId, episodeId, pkg}) {
  const res = await fetchImpl(`https://www.buzzsprout.com/api/${podcastId}/episodes/${episodeId}.json`, {headers: headers(token)});
  if (!res.ok) throw new Error(`BUZZSPROUT_VERIFY_${res.status}`);
  const episode = await jsonOrText(res);
  const expectedGuid = stableGuid(pkg);
  if (episode.guid !== expectedGuid || episode.title !== pkg.title || episode.private !== true) {
    throw new Error('DESTINATION_MISMATCH');
  }
  return episode;
}

export async function makePublic({fetchImpl = fetch, token, podcastId, episodeId, pkg}) {
  if (pkg.public_release_authorized !== true) throw new Error('PUBLIC_RELEASE_NOT_AUTHORIZED');
  const res = await fetchImpl(`https://www.buzzsprout.com/api/${podcastId}/episodes/${episodeId}.json`, {
    method: 'PUT', headers: headers(token), body: JSON.stringify({private: false, published_at: pkg.published_at || new Date().toISOString()})
  });
  if (!res.ok) throw new Error(`BUZZSPROUT_PUBLISH_${res.status}`);
  const episode = await jsonOrText(res);
  if (episode.private !== false) throw new Error('PUBLIC_READBACK_FAILED');
  return episode;
}

import {createPrivateEpisode, verifyEpisode, makePublic} from '../lib/publisher.mjs';

function reply(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}

function safeError(err) {
  return String(err?.message || 'UNKNOWN').replace(/token=[^\s&]+/gi, 'token=[REDACTED]').slice(0, 800);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return reply(res, 405, {error: 'METHOD_NOT_ALLOWED'});
  const token = process.env.BUZZSPROUT_API_TOKEN;
  const podcastId = process.env.BUZZSPROUT_PODCAST_ID || '2650509';
  const auth = process.env.PODCAST_PUBLISHER_AUTH_SECRET;
  if (!token || !auth) return reply(res, 503, {error: 'PUBLISHER_NOT_CONFIGURED'});
  if (req.headers.authorization !== `Bearer ${auth}`) return reply(res, 401, {error: 'UNAUTHORIZED'});

  try {
    const pkg = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    const staged = await createPrivateEpisode({token, podcastId, pkg});
    const verifiedPrivate = await verifyEpisode({token, podcastId, episodeId: staged.episode.id, pkg});
    if (pkg.publish_now === true) {
      const published = await makePublic({token, podcastId, episodeId: staged.episode.id, pkg});
      return reply(res, 200, {
        status: 'PUBLISHED', package_id: pkg.package_id, episode_id: published.id,
        guid: published.guid, private: published.private, audio_url: published.audio_url,
        published_at: published.published_at
      });
    }
    return reply(res, 200, {
      status: 'PRIVATE_VERIFIED', package_id: pkg.package_id, episode_id: verifiedPrivate.id,
      guid: verifiedPrivate.guid, private: verifiedPrivate.private, audio_url: verifiedPrivate.audio_url
    });
  } catch (err) {
    return reply(res, 409, {error: safeError(err)});
  }
}

import test from 'node:test';
import assert from 'node:assert/strict';
import {validatePackage, stableGuid, createPrivateEpisode, makePublic} from '../lib/publisher.mjs';

const pkg = {
  package_id: 'POD-001', title: 'The Textbook Found Open in the Ruins | New London, 1937',
  description: 'd', episode_number: 1, explicit: false,
  qd: {exact_master:'PASS', visual_rights:'PASS', release_copy:'PASS'},
  audio: {url:'https://example.test/pod001.mp3', sha256:'3a922c33a02731689670e9253a25e187098b2a3792036d0103011b5ce705741a'}
};

function response(status, body) {
  return {ok: status >= 200 && status < 300, status, text: async () => JSON.stringify(body)};
}

test('requires every independent QD gate', () => {
  const bad = structuredClone(pkg); bad.qd.exact_master = 'PENDING';
  assert.throws(() => validatePackage(bad), /QD_GATE_NOT_PASS/);
});

test('stable guid binds package to exact audio digest', () => {
  assert.equal(stableGuid(pkg), 'FinalVestige-POD-001-3a922c33a0273168');
});

test('reconciles an existing episode instead of duplicate POST', async () => {
  let posts = 0;
  const existing = {id:123, guid:stableGuid(pkg), title:pkg.title, private:true};
  const fetchImpl = async (url, init={}) => {
    if (!init.method) return response(200, [existing]);
    posts++; return response(201, existing);
  };
  const result = await createPrivateEpisode({fetchImpl, token:'secret', podcastId:'2650509', pkg});
  assert.equal(result.reconciled, true); assert.equal(posts, 0);
});

test('ambiguous create reconciles by stable guid before failing', async () => {
  let lists = 0; let posts = 0;
  const existing = {id:456, guid:stableGuid(pkg), title:pkg.title, private:true};
  const fetchImpl = async (url, init={}) => {
    if (!init.method) { lists++; return response(200, lists === 1 ? [] : [existing]); }
    posts++; throw new Error('timeout');
  };
  const result = await createPrivateEpisode({fetchImpl, token:'secret', podcastId:'2650509', pkg});
  assert.equal(posts, 1); assert.equal(result.reconciled, true);
});

test('public mutation requires explicit package authority', async () => {
  await assert.rejects(() => makePublic({fetchImpl:async()=>response(200,{}), token:'s', podcastId:'2650509', episodeId:1, pkg}), /PUBLIC_RELEASE_NOT_AUTHORIZED/);
});

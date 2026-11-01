import test from 'node:test';
import assert from 'node:assert/strict';
import {ENABLE_REAL_COLLECTION,normalizeSynthetic,aggregateSynthetic,collectRealVisitorEvent} from './privacy-synthetic.mjs';
const valid={topic:'zen12',variant:'text',sourceBucket:'internal',action:'guide-view'};
test('live event capture is hard disabled',()=>assert.equal(ENABLE_REAL_COLLECTION,false));
test('live event collection raises an error',()=>assert.throws(()=>collectRealVisitorEvent(valid),/HARD OFF/));
test('valid categorical event normalizes',()=>assert.equal(normalizeSynthetic(valid).topic,'zen12'));
test('normalized event is immutable',()=>assert.ok(Object.isFrozen(normalizeSynthetic(valid))));
for(const extra of ['email','ip','referrer','sessionId','cookie','userAgent','deviceId','orderId','utm_campaign','mobile','url','auth','other']){
 test('rejects extra field '+extra,()=>assert.throws(()=>normalizeSynthetic({...valid,[extra]:'not-allowed'})));
}
for(const bad of [null,[],42,'not-an-object',Object.create({topic:'zen12'}),{...valid,topic:'invalid'},{...valid,variant:'purchase'},{...valid,sourceBucket:'url'},{...valid,action:'sale'}]){
 test('rejects malformed event',()=>assert.throws(()=>normalizeSynthetic(bad)));
}
test('synthetic group of 19 suppressed',()=>assert.equal(aggregateSynthetic(Array(19).fill(valid)).length,0));
test('synthetic group of 20 visible',()=>assert.equal(aggregateSynthetic(Array(20).fill(valid))[0].count,20));
test('distinct low-count variant remains suppressed',()=>assert.equal(aggregateSynthetic([...Array(20).fill(valid),...Array(19).fill({...valid,variant:'film'})]).length,1));
test('reports contain only group and count',()=>assert.deepEqual(Object.keys(aggregateSynthetic(Array(20).fill(valid))[0]).sort(),['count','key']));

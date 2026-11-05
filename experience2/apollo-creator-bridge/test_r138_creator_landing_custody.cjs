'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {inspectBoundCampaign:bind,reviewedRoute,STATUS}=
 require('./r138_creator_landing_custody.cjs');
// SYNTHETIC URLs: do not infer that this is the real live Apollo permalink or a Grok post.
const reviewed='https://finalvestige.com/investigations/apollo-1/';
const asset='apollo_fall_2026_v001';
const youtubeId='abcdefghijk';
const destination=reviewed+'?utm_source=youtube&utm_medium=organic_social'+
 '&utm_campaign=history_pilot_2026_11&utm_content='+asset;
const c={asset_id:asset,public_url:'https://www.youtube.com/watch?v='+youtubeId,
 youtube_video_id:youtubeId,destination_url:destination};
test('only explicit, clean, first-party non-homepage reviewed routes qualify',()=>{
 assert.equal(reviewedRoute(reviewed),reviewed);
 for(const s of [null,undefined,'https://finalvestige.com/',
  'http://finalvestige.com/investigations/apollo-1/',
  'https://www.finalvestige.com/investigations/apollo-1/',
  'https://finalvestige.com/investigations/apollo-1/?preview=true',
  'https://finalvestige.com/investigations/apollo-1/#classroom-preview',
  'https://finalvestige.com/investigations//apollo-1/',
  'https://finalvestige.com@evil.test/investigations/apollo-1/'])
  assert.equal(reviewedRoute(s),null,String(s));
});
test('one internally consistent proposed video + exact route is only a candidate',()=>{
 const r=bind(c,reviewed);assert.equal(r.status,STATUS);
 assert.equal(r.independently_verified,false);
 assert.equal(r.publication_confirmed,false);
 assert.equal(r.human_sessions_observed,false);
 assert.equal(r.paid_orders_observed,false);
});
test('no reviewed WordPress permalink means fail closed; campaign cannot self-approve',()=>{
 const r=bind({...c,approved_landing_url:reviewed},null);
 assert.equal(r.status,'INVALID');
 assert.ok(r.errors.includes('REVIEWED_APOLLO_WORDPRESS_ROUTE_NOT_SUPPLIED'));
});
test('reject same-site alternate article despite valid campaign parameters',()=>{
 const r=bind(c,'https://finalvestige.com/investigations/crystal-skulls/');
 assert.ok(r.errors.includes('DESTINATION_DIFFERS_FROM_REVIEWED_APOLLO_ROUTE'));
});
test('reject video ID misbound to unrelated URL',()=>{
 const r=bind({...c,youtube_video_id:'xxxxxxxxxxx'},reviewed);
 assert.ok(r.errors.includes('VIDEO_ID_NOT_BOUND_TO_PUBLIC_URL'));
});
test('reject supported-looking but invalid or unrelated creator links',()=>{
 for(const public_url of ['https://www.youtube.com/shorts/123',
   'https://evil.test/watch?v=abcdefghijk',
   'https://www.youtube.com/watch?v=zyxwvutsrqp']) {
  const r=bind({...c,public_url},reviewed);
  assert.equal(r.status,'INVALID',public_url);
 }
});
test('actual YouTube Shorts URL with matching ID remains syntactic only',()=>{
 const r=bind({...c,public_url:'https://www.youtube.com/shorts/'+youtubeId},reviewed);
 assert.equal(r.status,STATUS);assert.equal(r.publication_confirmed,false);
});
test('shortlink with matching video ID is also only a candidate',()=>{
 assert.equal(bind({...c,public_url:'https://youtu.be/'+youtubeId},reviewed).status,STATUS);
});
test('missing destination, query values, extra PII, and malformed URLs fail',()=>{
 for(const destination_url of [null,undefined,
  reviewed, destination+'&email=user%40example.test',
  destination+'&utm_content='+asset,
  destination.replace('organic_social','paid'),
  destination.replace('history_pilot_2026_11','history_pilot_2026_12'),
  destination.replace(asset,'another_asset'),
  destination.replace('finalvestige.com','payhip.com')]){
  const r=bind({...c,destination_url},reviewed);
  assert.equal(r.status,'INVALID',String(destination_url));
  assert.ok(r.errors.includes('GROK_UTM_DESTINATION_INVALID'));
 }
});
test('candidate destination must not become a live redirect',()=>{
 const r=bind({...c,destination_url:destination.replace('/apollo-1/','/apollo-1-redirect/')},reviewed);
 assert.ok(r.errors.includes('DESTINATION_DIFFERS_FROM_REVIEWED_APOLLO_ROUTE'));
});
test('coercion and non-object submissions fail without throwing',()=>{
 for(const bad of [null,[],1,'campaign',false]){
  const r=bind(bad,reviewed);assert.equal(r.status,'INVALID');
 }
});
test('no telemetry, cookies, commercial activation or external calls in review receipt',()=>{
 const receipt=bind(c,reviewed);
 const serialized=JSON.stringify(receipt);
 assert.ok(!serialized.includes('email'));
 assert.equal('net_revenue' in receipt,false);
 assert.equal('checkout_approved' in receipt,false);
 assert.deepEqual(bind(c,reviewed),receipt);
});

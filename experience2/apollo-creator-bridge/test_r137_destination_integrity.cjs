'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {inspectCreatorUrl:creator,inspectMerchantUrl:merchant,inspectReferralDestination:ref}=require('./r137_destination_integrity.cjs');
const id='AbcDeFGH12_';
const pay='https://payhip.com/b/a1B2c';
const path='https://finalvestige.com/apollo-1/?utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_video_001';
test('long-form supports exact watch page and does not assert publication',()=>{
 const r=creator('https://www.youtube.com/watch?v='+id);
 assert.equal(r.status,'SYNTAX_ONLY_NOT_PUBLICATION_PROOF'); assert.equal(r.kind,'LONG_FORM'); assert.equal(r.independently_published,false);
});
test('YouTube Shorts are accepted as candidates, never verified posts',()=>{
 const r=creator('https://www.youtube.com/shorts/'+id);
 assert.equal(r.kind,'SHORT');assert.equal(r.independently_published,false);
});
test('youtu.be shortlinks retain unknown form until independent audit',()=>{
 assert.equal(creator('https://youtu.be/'+id).kind,'YOUTUBE_SHORTLINK_UNTYPED');
});
test('reject off-host spoof, http, userinfo, embeds and extra query params',()=>{
 for(const s of ['http://youtube.com/watch?v='+id,'https://youtube.com.evil.test/watch?v='+id,
  'https://youtube.com@evil.test/watch?v='+id,'https://youtube.com/embed/'+id,
  'https://www.youtube.com/watch?v='+id+'&redirect=https://evil.test',
  'https://www.youtube.com/watch?v=short','https://www.youtube.com/watch?v='+id+'#frag'])
  assert.equal(creator(s).status,'INVALID',s);
});
test('reject deceptive URL repairs and whitespace',()=>{
 for(const s of [' https://payhip.com/b/a1B2c','https://payhip.com/b/a1B2c ','https://payhip.com/b/%2fa1B2c',
  'https://payhip.com:443/b/a1B2c','https://payhip.com/b/a1B2c#sale'])
  assert.equal(merchant(s).status,'INVALID',s);
});
test('permit only canonical Payhip /b/ products as review candidates',()=>{
 const r=merchant(pay);assert.equal(r.status,'DOCUMENT_ONLY_NOT_MERCHANT_PROOF');
 assert.equal(r.verified_product,false);assert.equal(r.founder_approved,false);
});
test('refuse phishing lookalikes, empty store, custom domain, redirects and tokens',()=>{
 for(const s of ['https://evil.test/b/a1B2c','https://payhip.com.evil.test/b/a1B2c',
 'https://payhip.com/','https://payhip.com/checkout/abc',
 'https://payhip.com/b/a1B2c?redirect=https://evil.test',
 'https://payhip.com/b/a1B2c?email=user%40mail.test',
 'https://payhip.com:8443/b/a1B2c'])assert.equal(merchant(s).status,'INVALID',s);
});
test('exact UTM landing candidate is NOT evidence of a session or sale',()=>{
 const r=ref(path,'apollo_video_001');assert.equal(r.status,'CANDIDATE_ONLY_NOT_CLICK_ATTRIBUTION');
 assert.equal(r.qualified_sessions,'UNOBSERVABLE');assert.equal(r.confirmed_orders,'UNOBSERVABLE');
});
test('mismatched asset IDs and noncanonical query routes fail',()=>{
 for(const s of [path.replace('apollo_video_001','another_asset'),path+'&ref=buyer',
 path.replace('finalvestige.com','fake-finalvestige.com'),
 path.replace('/apollo-1/','/'),path.replace('organic_social','paid')])
  assert.equal(ref(s,'apollo_video_001').status,'INVALID',s);
});
test('UTM route cannot claim a confirmed signup or conversion',()=>{
 const r=ref(path,'apollo_video_001'); assert.equal('confirmed_leads' in r,false);
 assert.equal('net_revenue' in r,false);
});

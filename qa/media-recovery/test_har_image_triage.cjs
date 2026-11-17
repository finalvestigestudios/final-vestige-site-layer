'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {reconcileHar, classifyObservation, scrubQuerySecrets, buildSiteQueue} = require('./har_image_triage.cjs');
const article = 'https://finalvestige.com/2026/08/18/they-painted-over-archimedes/';
const u = 'https://archimedespalimpsest.org/assets/img/imaging_x8.jpg';
const v = 'https://archimedespalimpsest.org/assets/img/imaging_x9.jpg';
const queue = {date: '2026-10-30', rows: [
 {post_id:268,image_key:'268:1',slot:1,article_url:article,exact_stored_url:u,source_host:'archimedespalimpsest.org'},
 {post_id:268,image_key:'268:8',slot:8,article_url:article,exact_stored_url:v,source_host:'archimedespalimpsest.org'},
 {post_id:432,image_key:'432:0',slot:0,article_url:'https://finalvestige.com/abc/',exact_stored_url:'https://floridamemory.com/a.jpg',source_host:'floridamemory.com'}]};
const entry=(url,status=404,resource='image',mime='text/html',transfer=101)=>({_resourceType:resource,request:{method:'GET',url},response:{status,content:{mimeType:mime},_transferSize:transfer,bodySize:90,headers:[{name:'Set-Cookie',value:'password-secret'}]},requestHeaders:[{name:'Cookie',value:'secret'}]});
const har=entries=>({log:{version:'1.2',entries}});
test('real HAR Image 404 observed but not a verified visual failure',()=>{const r=reconcileHar(har([entry(u)]),queue,268);assert.equal(r.findings[0].har_observations[0].http_status,404);assert.equal(r.findings[0].har_observations[0].observation,'HAR_IMAGE_HTTP_ERROR_OBSERVED');assert.equal(r.findings[0].verified_broken_in_browser,null);assert.equal(r.reported_42_broken_images_verified,false)});
test('XHR 200 on same URL cannot suppress Image 403',()=>{const r=reconcileHar(har([entry(u,403,'image'),entry(u,200,'xmlhttprequest','image/jpeg')]),queue,268);assert.equal(r.excluded_same_source_nonimage_requests,1);assert.equal(r.findings[0].har_observations.length,1);assert.equal(r.findings[0].har_observations[0].http_status,403)});
test('GET Image 200 JPEG remains only response evidence',()=>{const r=reconcileHar(har([entry(u,200,'image','image/jpeg')]),queue,268);assert.match(r.findings[0].har_observations[0].observation,/NOT_VISUAL_PROOF/);assert.equal(r.findings[0].har_observations[0].image_visible_to_visitor,null)});
test('200 HTML returns nonimage response even when GET image',()=>assert.equal(classifyObservation(entry(u,200,'image','text/html')).observation,'HAR_IMAGE_NONIMAGE_RESPONSE_OBSERVED'));
test('302 image redirects are incomplete without final identity',()=>assert.equal(classifyObservation(entry(u,302,'image','text/html')).observation,'HAR_IMAGE_REDIRECT_INCOMPLETE'));
test('no resourceType remains unknown instead of guessed from .jpg',()=>{const r=reconcileHar(har([entry(u,404,null)]),queue,268);assert.equal(r.matching_image_requests,0);assert.equal(r.findings[0].result,'NO_MATCHING_IMAGE_REQUEST_IN_HAR')});
test('HEAD probe is not a decoded image request',()=>{const e=entry(u);e.request.method='HEAD';const r=reconcileHar(har([e]),queue,268);assert.equal(r.matching_image_requests,0)});
test('multiple Image requests cannot collapse different HTTP statuses',()=>{const r=reconcileHar(har([entry(u,404),entry(u,200,'image','image/jpeg')]),queue,268);assert.equal(r.findings[0].result,'MULTIPLE_HAR_IMAGE_REQUESTS_REVIEW');assert.deepEqual(r.findings[0].har_observations.map(x=>x.http_status),[404,200])});
test('missing transfer bytes remain unknown rather than body-size savings',()=>{const e=entry(u);delete e.response._transferSize;const r=reconcileHar(har([e]),queue,268);assert.equal(r.findings[0].har_observations[0].har_reported_transfer_size_bytes,null);assert.equal(r.findings[0].har_observations[0].har_reported_body_size_bytes,90)});
test('never leak HAR headers, cookies or response bodies',()=>{const r=reconcileHar(har([entry(u)]),queue,268);assert.ok(!JSON.stringify(r).includes('password-secret'));assert.ok(!JSON.stringify(r).includes('Set-Cookie'));assert.ok(!JSON.stringify(r).includes('"value":"secret"'))});
test('redact token query params from output URL',()=>{const x=scrubQuerySecrets('https://photos.example/a.jpg?width=960&token=hello&X-Amz-Signature=abc');assert.equal(x.query_secrets_redacted,true);assert.ok(!x.url.includes('hello'));assert.ok(!x.url.includes('abc'));assert.ok(x.url.includes('width=960'))});
test('offsite misidentified host not matched',()=>{const r=reconcileHar(har([entry('https://evil.example/assets/img/imaging_x8.jpg')]),queue,268);assert.equal(r.matching_image_requests,0)});
test('different photo on same origin does not count as slot',()=>{const r=reconcileHar(har([entry('https://archimedespalimpsest.org/assets/img/unrelated.jpg')]),queue,268);assert.equal(r.matching_image_requests,0)});
test('source redirects to CDN cannot assert original identity from HAR',()=>{const r=reconcileHar(har([entry(u,301)]),queue,268);assert.equal(r.findings[0].image_identity_after_redirect_verified,false)});
test('rejects unknown post and forged/malformed queue',()=>{assert.throws(()=>reconcileHar(har([]),queue,999));assert.throws(()=>reconcileHar(har([]),{rows:[{...queue.rows[0],exact_stored_url:'file:///secret'}]},268))});
test('shared source URL in multiple slots is not uniquely attributed',()=>{const q={...queue,rows:[...queue.rows,{...queue.rows[0],image_key:'268:9',slot:9}]};const r=reconcileHar(har([entry(u)]),q,268);assert.equal(r.findings[0].result,'SHARED_IMAGE_URL_SLOT_ATTRIBUTION_UNVERIFIED');assert.equal(r.findings[2].har_request_identity_ambiguous_across_slots,true)});
test('no verified 76% savings or permissions ever emitted',()=>{const r=reconcileHar(har([entry(u)]),queue,268);assert.equal(r.reported_76_percent_saving_verified,false);assert.ok(r.findings.every(x=>x.wordpress_write_authorized===false&&x.rights_cleared===false&&x.measured_article_wire_savings_percent===null))});
test('all-post census adapter enforces 61/355 and unchanged P0 URLs',()=>{
 const posts = Array.from({length:61},(_,i)=>({id:i+1,url:'https://finalvestige.com/article-'+(i+1)+'/'}));
 const images = Array.from({length:355},(_,i)=>({key:((i%61)+1)+':'+Math.floor(i/61),post_id:(i%61)+1,post_url:posts[i%61].url,source_url:'https://example.org/'+i+'.jpg',source_host:'example.org',slot:Math.floor(i/61)}));
 const parts = Array.from({length:8},(_,i)=>({date:'2026-10-30',posts:i===0?posts:[],images:images.filter((_,j)=>j%8===i)}));
 const q = buildSiteQueue(parts,{rows:[{image_key:images[0].key,exact_stored_url:images[0].source_url,official_record_url:'https://usgs.gov/test'}]});
 assert.equal(q.census_posts,61);assert.equal(q.census_slots,355);assert.equal(q.rows[0].official_record_url,'https://usgs.gov/test');
 assert.throws(()=>buildSiteQueue(parts,{rows:[{image_key:images[0].key,exact_stored_url:'https://evil.org/a.jpg'}]}),/drift/);
 assert.throws(()=>buildSiteQueue(parts.slice(0,7)));
});

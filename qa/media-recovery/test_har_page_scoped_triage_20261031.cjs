'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {reconcilePageScopedHar} = require('./har_image_triage.cjs');
const article = 'https://finalvestige.com/2026/08/18/they-painted-over-archimedes/';
const other = 'https://finalvestige.com/2026/08/18/other-article/';
const image = 'https://archimedespalimpsest.org/assets/img/imaging_x8.jpg';
const queue = {date:'2026-10-30',rows:[{
  post_id:268,image_key:'268:1',slot:1,article_url:article,
  exact_stored_url:image,source_host:'archimedespalimpsest.org'
}]};
const page=(id,url)=>({id,title:url});
const doc=(id,url,status=200,type='document')=>({
  pageref:id,_resourceType:type,request:{method:'GET',url},
  response:{status,content:{mimeType:'text/html; charset=utf-8'}}});
const img=(id,status=404)=>({
  pageref:id,_resourceType:'image',request:{method:'GET',url:image},
  response:{status,content:{mimeType:status===200?'image/jpeg':'text/html'},_transferSize:150}});
const har=(pages,entries)=>({log:{pages,entries}});
test('foreign-tab 404 cannot override article Image 200',()=>{
 const r=reconcilePageScopedHar(har([page('p1',article),page('p2',other)],
  [doc('p1',article),img('p1',200),doc('p2',other),img('p2',404)]),queue,268);
 assert.equal(r.har_declared_article_scope_consistent,true);
 assert.equal(r.excluded_unscoped_har_entries,2);
 assert.equal(r.findings[0].har_observations.length,1);
 assert.equal(r.findings[0].har_observations[0].http_status,200);
 assert.equal(r.har_page_identity_verified,false);
 assert.equal(r.findings[0].verified_broken_in_browser,null);
});
test('foreign-tab 200 cannot override article Image 403',()=>{
 const r=reconcilePageScopedHar(har([page('p1',article),page('p2',other)],
  [doc('p1',article),img('p1',403),doc('p2',other),img('p2',200)]),queue,268);
 assert.equal(r.findings[0].har_observations[0].http_status,403);
 assert.equal(r.findings[0].har_observations.length,1);
});
test('missing HAR page metadata withholds image status',()=>{
 const r=reconcilePageScopedHar({log:{entries:[doc('p1',article),img('p1',403)]}},queue,268);
 assert.equal(r.har_scope_status,'MISSING_HAR_PAGE_METADATA');
 assert.equal(r.matching_image_requests,0);
 assert.equal(r.findings[0].har_observations.length,0);
});
test('document 404 prevents a false article-image attribution',()=>{
 const r=reconcilePageScopedHar(har([page('p1',article)],[doc('p1',article,404),img('p1',403)]),queue,268);
 assert.equal(r.har_scope_status,'MATCHING_SUCCESSFUL_DOCUMENT_REQUEST_MISSING');
 assert.equal(r.matching_image_requests,0);
});
test('a matching URL with no pageref is not attributable to post',()=>{
 const orphan=img('p1',404);delete orphan.pageref;
 const r=reconcilePageScopedHar(har([page('p1',article)],[doc('p1',article),orphan]),queue,268);
 assert.equal(r.har_declared_article_scope_consistent,true);
 assert.equal(r.matching_image_requests,0);
});
test('XHR 200 document mimic fails page verification',()=>{
 const r=reconcilePageScopedHar(har([page('p1',article)],[doc('p1',article,200,'xmlhttprequest'),img('p1',404)]),queue,268);
 assert.equal(r.har_declared_article_scope_consistent,false);
 assert.equal(r.matching_image_requests,0);
});
test('redacts HAR headers and never infers rights or weight reduction',()=>{
 const im=img('p1',403);
 im.response.headers=[{name:'Set-Cookie',value:'secret-cookie'}];
 const r=reconcilePageScopedHar(har([page('p1',article)],[doc('p1',article),im]),queue,268);
 assert.equal(r.reported_42_broken_images_verified,false);
 assert.equal(r.reported_76_percent_saving_verified,false);
 assert.equal(r.findings[0].rights_cleared,false);
 assert.equal(r.findings[0].measured_article_wire_savings_percent,null);
 assert.ok(!JSON.stringify(r).includes('secret-cookie'));
});


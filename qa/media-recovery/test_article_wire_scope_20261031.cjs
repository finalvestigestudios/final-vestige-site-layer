'use strict';
/** Synthetic transfer-scope tests; never report these fixtures as live website measurements. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {scopeArticleImageWire}=require('./browser_probe_core.cjs');
const original='https://archive.example.gov/photo.jpg';
const slot=(override={})=>({current_src:original,request_url:original,...override});
const request=(url=original,bytes=5000,aliases=[])=>({
 url,encoded_data_length:bytes,url_aliases:aliases,status:200,mime_type:'image/jpeg'
});
test('one verified article photo is attributed and page chrome is excluded',()=>{
 const s=scopeArticleImageWire([slot()],[request(),request('https://finalvestige.com/logo.png',12000)]);
 assert.equal(s.article_bytes,5000);
 assert.equal(s.unattributed_bytes,12000);
 assert.equal(s.matched_request_count,1);
});
test('two visible article slots sharing one fetched URL do not double-count request bytes',()=>{
 const s=scopeArticleImageWire([slot(),slot()],[request()]);
 assert.equal(s.article_bytes,5000);
 assert.equal(s.matched_request_count,1);
});
test('two real network requests to same visible asset count twice',()=>{
 const s=scopeArticleImageWire([slot()],[request(),request()]);
 assert.equal(s.article_bytes,10000);
 assert.equal(s.matched_request_count,2);
});
test('a redirected final URL representing unrelated historical content is not an article byte',()=>{
 const s=scopeArticleImageWire([slot()],
  [request('https://cdn.example.net/unrelated-disaster.jpg',5000,[original])]);
 assert.equal(s.article_bytes,0);
 assert.equal(s.unattributed_bytes,5000);
 assert.equal(s.matched_request_count,0);
});
test('Commons archival file redirect to its own hashed original counts as article content',()=>{
 const from='https://commons.wikimedia.org/wiki/Special:Redirect/file/Archive_photo.jpg';
 const final='https://upload.wikimedia.org/wikipedia/commons/a/ab/Archive_photo.jpg';
 const s=scopeArticleImageWire([slot({current_src:from,request_url:final})],[request(final,5000,[from])]);
 assert.equal(s.article_bytes,5000);
 assert.equal(s.matched_request_count,1);
});
test('Jetpack same-photo first-party resizing retains article attribution',()=>{
 const src='https://finalvestige.com/wp-content/uploads/2026/09/photo.jpg';
 const final='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/09/photo.jpg?resize=960%2C540';
 const s=scopeArticleImageWire([slot({current_src:final,request_url:final})],[request(final,1200,[src])]);
 assert.equal(s.article_bytes,1200);
});
test('null image request byte measurement forces unknown, not an invented zero',()=>{
 const s=scopeArticleImageWire([slot()],[request(original,null)]);
 assert.equal(s.article_bytes,null);
 assert.equal(s.unmeasured_article_requests,1);
});
test('unmeasured unrelated image does not fabricate article transfer byte totals',()=>{
 const s=scopeArticleImageWire([slot()],[request(),request('https://finalvestige.com/icon.png',null)]);
 assert.equal(s.article_bytes,5000);
 assert.equal(s.unattributed_bytes,0);
});
test('unknown decoded currentSrc cannot attribute a matching stale request URL',()=>{
 const s=scopeArticleImageWire([slot({current_src:'https://another.example.org/not-the-photo.jpg'})],
  [request(original,5000)]);
 assert.equal(s.article_bytes,0);
});
test('malformed input has no savings-grade article byte evidence',()=>{
 const s=scopeArticleImageWire(null,[request()]);
 assert.equal(s.article_bytes,null);
});

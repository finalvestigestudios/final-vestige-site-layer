'use strict';
/** Synthetic adversarial CDP logs, never visitor HTTP or a claimed 76% saving. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const img='https://archive.example.gov/1946-debris.jpg';
const slot=(over={})=>({
 image_key:'418:2',stored_url:img,current_src:img,request_url:img,request_id:'33.1',
 result:'loaded_in_probe_browser',match:'exact_url_or_jetpack_origin',
 current_src_identity_verified:true,network_final_identity_verified:true,
 loaded_network_proof_verified:true,redirected_image_identity_unverified:false,
 natural_width:600,natural_height:450,http_status:200,response_mime_type:'image/jpeg',transfer_bytes:5000,
 verified_broken_in_browser:false,...over});
const net=(over={})=>({
 request_id:'33.1',url:img,url_aliases:[],status:200,
 mime_type:'image/jpeg',encoded_data_length:5000,error:null,
 was_cached:false,from_disk_cache:false,from_service_worker:false,...over});
const result=(slots=[slot()],network=[net()])=>scopeByRequestId(slots,network);
test('one bound photo counts exactly once; chrome logo excluded',()=>{
 const x=result([slot()],[net(),net({request_id:'ui.1',url:'https://finalvestige.com/logo.png',encoded_data_length:11000})]);
 assert.equal(x.article_bytes,5000);assert.equal(x.unattributed_bytes,11000);
 assert.equal(x.matched_request_count,1);assert.deepEqual(x.reasons,[]);
});
test('two DOM slots sharing the SAME CDP request do not double count bytes',()=>{
 const x=result([slot(),slot({image_key:'418:4'})],[net()]);
 assert.equal(x.article_bytes,5000);assert.equal(x.matched_request_count,1);
});
test('two different visible photos bound to distinct CDP IDs count twice',()=>{
 const two='https://archive.example.gov/other.jpg';
 const x=result([slot(),slot({image_key:'418:3',stored_url:two,current_src:two,request_url:two,
   request_id:'33.2',transfer_bytes:7000})],
 [net(),net({request_id:'33.2',url:two,encoded_data_length:7000})]);
 assert.equal(x.article_bytes,12000);assert.equal(x.matched_request_count,2);
});
test('extra normalized-size request with NO DOM binding is NOT article-only savings evidence',()=>{
 const x=result([slot()],[net(),net({request_id:'33.2',url:img+'?width=1200',encoded_data_length:31000})]);
 assert.equal(x.article_bytes,null);
 assert.ok(x.reasons.includes('unbound_same_photo_request'));
});
test('different historical crop is distinct, not falsely attributed to article',()=>{
 const top=img+'?crop=top',bottom=img+'?crop=bottom';
 const x=result([slot({stored_url:top,current_src:top,request_url:top})],
  [net({url:top}),net({request_id:'33.2',url:bottom,encoded_data_length:2500})]);
 assert.equal(x.article_bytes,5000);assert.equal(x.unattributed_bytes,2500);
});
test('CDP request ID pointing at a different photograph fails closed',()=>{
 const x=result([slot()],[net({url:'https://archive.example.gov/another.jpg'})]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.some(x=>x.startsWith('slot_cdp_response_mismatch')));
});
test('URL-only matching WITHOUT CDP IDs cannot certify article transfer',()=>{
 const x=result([slot({request_id:null})],[net({request_id:null})]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.includes('network_request_id_missing'));
});
test('claimed slot request ID must exist in actual network records',()=>{
 const x=result([slot({request_id:'made-up'})],[net()]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.includes('slot_request_id_not_found:418:2'));
});
test('duplicate CDP request IDs in network rows must not count twice',()=>{
 const x=result([slot()],[net(),net({encoded_data_length:1234})]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.includes('duplicate_network_request_id'));
});
test('wrong slot byte count cannot be silently reconciled by matching URLs',()=>{
 const x=result([slot({transfer_bytes:4999})],[net()]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.includes('slot_cdp_response_mismatch:418:2'));
});
test('original Commons redirect to same hashed file retains request identity',()=>{
 const src='https://commons.wikimedia.org/wiki/Special:Redirect/file/Scotch_cap.jpg';
 const dst='https://upload.wikimedia.org/wikipedia/commons/1/12/Scotch_cap.jpg';
 const x=result([slot({stored_url:src,current_src:src,request_url:dst})],
  [net({url:dst,url_aliases:[src]})]);
 assert.equal(x.article_bytes,5000);assert.equal(x.complete,true);
});
test('Jetpack resizing of the same photo is permitted with CDP ID match',()=>{
 const src='https://finalvestige.com/wp-content/uploads/2026/08/historical.jpg';
 const jet='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/historical.jpg?fit=960%2C540&ssl=1';
 const x=result([slot({stored_url:src,current_src:jet,request_url:jet})],[net({url:jet})]);
 assert.equal(x.article_bytes,5000);
});
test('dynamic query selecting a different photo remains a mismatch',()=>{
 const src='https://www.history.navy.mil/bin/imageDownload?image=NH43900';
 const wrong='https://www.history.navy.mil/bin/imageDownload?image=NH98039';
 const x=result([slot({stored_url:src,current_src:src,request_url:src})],[net({url:wrong})]);
 assert.equal(x.article_bytes,null);
});
for(const [label,bad] of [
 ['404',{status:404}],['HTML disguised as image',{mime_type:'text/html'}],
 ['zero transfer',{encoded_data_length:0}],['disk cache',{from_disk_cache:true}],
 ['service worker',{from_service_worker:true}],['reused browser cache',{was_cached:true}],
 ['transport error',{error:'net::ERR_ABORTED'}]
])test('invalid CDP Image response ('+label+') fails closed',()=>{
 assert.equal(result([slot()],[net(bad)]).article_bytes,null,label);
});
test('missing confirmed visual image proof cannot measure page',()=>{
 for(const change of [{result:'pending_lazy_or_incomplete'},{loaded_network_proof_verified:false},
  {verified_broken_in_browser:true},{natural_width:0},{match:'alt_only_unverified'}]){
  assert.equal(result([slot(change)],[net()]).article_bytes,null,JSON.stringify(change));
 }
});
test('duplicate stored image keys fail closed',()=>{
 const x=result([slot(),slot()],[net()]);
 assert.equal(x.article_bytes,null);assert.ok(x.reasons.includes('duplicate_or_missing_image_key'));
});
test('empty inputs return unknown, never zero bytes',()=>{
 assert.equal(result([],[]).article_bytes,null);
});

// An absent CDP cache flag is UNKNOWN, not proof of an uncached transfer.
// A mismatched decoded-image MIME and intrinsic height also fails closed.
for (const [name,networkChange] of [
 ['missing was_cached flag',{was_cached:undefined}],
 ['missing disk-cache flag',{from_disk_cache:undefined}],
 ['missing service-worker flag',{from_service_worker:undefined}],
 ['network JPEG vs decoded PNG',{mime_type:'image/png'}]
])test('fail closed on '+name,()=>{
 const v=result([slot()],[net(networkChange)]);
 assert.equal(v.article_bytes,null,name);
 assert.equal(v.complete,false,name);
 assert.ok(v.reasons.some(s=>s.startsWith('slot_cdp_response_mismatch')),name);
});
for (const [name,slotChange] of [
 ['missing intrinsic height',{natural_height:undefined}],
 ['zero intrinsic height',{natural_height:0}],
 ['missing DOM MIME',{response_mime_type:undefined}],
 ['DOM JPEG vs CDP PNG',{response_mime_type:'image/png'}]
])test('fail closed on '+name,()=>{
 const v=result([slot(slotChange)],[net()]);
 assert.equal(v.article_bytes,null,name);
 assert.equal(v.complete,false,name);
 assert.ok(v.reasons.some(s=>s.startsWith('slot_not_network_verified')||s.startsWith('slot_cdp_response_mismatch')),name);
});

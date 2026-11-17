'use strict';
/** Synthetic CDP monitor-to-classifier-to-wire tests. No real browser traffic. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {monitor}=require('./browser_probe_chrome.cjs');
const {classifyImages}=require('./browser_probe_core.cjs');
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const {selectCdpImageRequests}=require('./cdp_image_request_scope.cjs');
const src='https://archive.example.gov/photograph.jpg';
const stored=[{key:'418:2',source_url:src,alt:'Historical image'}];
const dom=(url=src,w=960)=>[{index:0,src:url,currentSrc:url,alt:'Historical image',
 complete:true,naturalWidth:w,naturalHeight:650}];
function fake(){
 let event;
 const cdp={on(fn){event=fn;return()=>{event=null}}};
 const live=monitor(cdp);
 const emit=(method,params)=>event({method,params});
 const begin=(id,url=src)=>emit('Network.requestWillBeSent',
  {requestId:id,request:{url},type:'Image'});
 const response=(id,url=src,status=200,mime='image/jpeg')=>emit('Network.responseReceived',
  {requestId:id,response:{url,status,mimeType:mime},type:'Image'});
 const finish=(id,bytes=5000)=>emit('Network.loadingFinished',{requestId:id,encodedDataLength:bytes});
 const network=()=>selectCdpImageRequests(live.records());
 const wire=()=>network().map(x=>({request_id:x.request_id,url:x.url,url_aliases:x.url_aliases,
  status:x.status,mime_type:x.mime_type,encoded_data_length:x.encodedDataLength,
  error:x.failed_error||null,was_cached:x.was_cached===true,
  from_disk_cache:x.from_disk_cache===true,from_service_worker:x.from_service_worker===true}));
 const classify=(url=src,w=960)=>classifyImages(stored,dom(url,w),network(),true)[0];
 return{begin,response,finish,emit,live,network,wire,classify};
}
test('realistic CDP event flow retains request ID through image classification',()=>{
 const x=fake();x.begin('120.1');x.response('120.1');x.finish('120.1');
 const record=x.network()[0],slot=x.classify();
 assert.equal(record.request_id,'120.1');assert.equal(slot.request_id,'120.1');
 assert.equal(slot.result,'loaded_in_probe_browser');
 const bytes=scopeByRequestId([slot],x.wire());
 assert.equal(bytes.article_bytes,5000);assert.equal(bytes.complete,true);x.live.close();
});
test('redirect chain keeps one request ID, alias and exact Commons photo identity',()=>{
 const from='https://commons.wikimedia.org/wiki/Special:Redirect/file/Scotch_Cap.jpg';
 const to='https://upload.wikimedia.org/wikipedia/commons/1/12/Scotch_Cap.jpg';
 const x=fake();x.begin('140.2',from);
 x.emit('Network.requestWillBeSent',{requestId:'140.2',request:{url:to},type:'Image',
  redirectResponse:{url:from,status:302}});
 x.response('140.2',to);x.finish('140.2',1200);
 const row=x.network()[0];
 assert.equal(x.network().length,1);assert.equal(row.request_id,'140.2');
 assert.ok(row.url_aliases.includes(from));
 const d=classifyImages([{key:'1:0',source_url:from,alt:'Historical image'}],
  dom(from,960),x.network(),true)[0];
 assert.equal(d.request_id,'140.2');assert.equal(d.result,'loaded_in_probe_browser');
 assert.equal(scopeByRequestId([d],x.wire()).article_bytes,1200);x.live.close();
});
test('two CDP requests to the same photo cannot be resolved by findLast',()=>{
 const x=fake();x.begin('150.1');x.response('150.1');x.finish('150.1');
 x.begin('150.2');x.response('150.2',src,404);x.finish('150.2',0);
 const d=x.classify(src,0);
 assert.equal(d.result,'ambiguous_network_request_identity');
 assert.equal(d.verified_broken_in_browser,null);
 assert.equal(scopeByRequestId([d],x.wire()).article_bytes,null);x.live.close();
});
test('page-chrome request is excluded when article CDP ID remains unique',()=>{
 const x=fake();x.begin('160.1');x.response('160.1');x.finish('160.1',4400);
 x.begin('160.logo','https://finalvestige.com/logo.png');
 x.response('160.logo','https://finalvestige.com/logo.png');x.finish('160.logo',9000);
 const d=x.classify();const scoped=scopeByRequestId([d],x.wire());
 assert.equal(scoped.article_bytes,4400);assert.equal(scoped.unattributed_bytes,9000);x.live.close();
});
test('cache-served CDP response cannot become a weight saving',()=>{
 const x=fake();x.begin('170.1');
 x.emit('Network.requestServedFromCache',{requestId:'170.1'});
 x.response('170.1');x.finish('170.1',1000);
 const d=x.classify();
 assert.equal(d.loaded_network_proof_verified,false);
 assert.equal(scopeByRequestId([d],x.wire()).article_bytes,null);x.live.close();
});
test('failed Image transport with zero decoded width remains broken but not a saving',()=>{
 const x=fake();x.begin('180.1');
 x.emit('Network.loadingFailed',{requestId:'180.1',type:'Image',errorText:'net::ERR_CONNECTION_RESET'});
 const d=x.classify(src,0);
 assert.equal(d.verified_broken_in_browser,true);
 assert.equal(d.visual_failure_kind,'network_error');
 assert.equal(d.request_id,'180.1');
 assert.equal(scopeByRequestId([d],x.wire()).article_bytes,null);x.live.close();
});

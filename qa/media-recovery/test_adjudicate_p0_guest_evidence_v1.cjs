'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {adjudicate,sourceRows,ORDER}=require('./adjudicate_p0_guest_evidence_v1.cjs');
const copy=x=>JSON.parse(JSON.stringify(x));
const link=k=>'https://example.org/historic-'+k.replace(':','-')+'.jpg';
function sources(){
 const early={schema:'fv-p0-retriever-source-recheck-v1',source_count:6,rows:ORDER.map(k=>({
  image_key:k,post_id:Number(k.split(':')[0]),published_source_read_back_from_wp:true,
  exact_published_original_url:link(k),retriever:{wrapper_error_code:k==='287:5'?404:null,tool_result:'WRAPPER_ONLY',guest_browser_http_status:null,visitor_broken:null},
  production_write_authorized:false,archival_candidate:{archive_record_url:'https://www.archives.gov/',rights_review:'HOLD',source_authorization_to_cache:false}
 }))};
 const later={schema:'fv-media-p0-retriever-two-source-20261105-v1',rows:['285:5','418:1'].map(k=>({
  image_key:k,post_id:Number(k.split(':')[0]),published_url:link(k),current_published_url_unchanged:true,
  wrapper_observation:{wrapper_status:k==='285:5'?404:403,result:'WRAPPER_ONLY',guest_browser_http_status:null,guest_broken:null},
  actions:{wp_upload:false,publish:false},primary_catalog:{cache_authorized_by_workflow:false}
 }))};
 return [early,later];
}
function loadedSlot(k){let u=link(k);return {
 image_key:k,stored_url:u,current_src:u,request_url:u,request_id:'req'+k,
 result:'loaded_in_probe_browser',match:'exact_url_or_jetpack_origin',complete:true,
 current_src_identity_verified:true,network_final_identity_verified:true,loaded_network_proof_verified:true,
 redirected_image_identity_unverified:false,verified_broken_in_browser:false,
 natural_width:960,natural_height:540,http_status:200,response_mime_type:'image/jpeg',transfer_bytes:700
};}
function netLoaded(k){return {request_id:'req'+k,url:link(k),status:200,mime_type:'image/jpeg',encoded_data_length:700,
 was_cached:false,from_disk_cache:false,from_service_worker:false,error:null};}
function browser(){
 const ids=[...new Set(ORDER.map(k=>Number(k.split(':')[0])))];
 return {schema_version:1,probe_version:4,mode:'priority',viewport:'390x844',
 requested_pages:ids.length,run_profile:{cache_disabled:true,service_worker_bypassed:true},
 image_census_coverage:{complete:true},pages:ids.map(id=>{
  const keys=ORDER.filter(k=>Number(k.split(':')[0])===id);
  return {post_id:id,url:'https://finalvestige.com/p/'+id,page_result:'inspected_browser',
  scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:keys.length,
  stored_images:keys.map(loadedSlot),network_images:keys.map(netLoaded),screenshots:[]};
 })};
}
function bork(run,k,kind='http'){
 const p=run.pages.find(p=>p.post_id===Number(k.split(':')[0])),s=p.stored_images.find(x=>x.image_key===k),
 n=p.network_images.find(x=>x.request_id===s.request_id);
 s.result='confirmed_broken_in_probe_browser';s.verified_broken_in_browser=true;s.natural_width=0;s.natural_height=0;
 s.loaded_network_proof_verified=false;
 if(kind==='http'){s.http_status=404;n.status=404;s.visual_failure_kind='http_error';}
 if(kind==='network'){s.http_status=null;n.status=null;n.error='net::ERR_CONNECTION_RESET';s.network_failure=n.error;s.visual_failure_kind='network_error';}
 if(kind==='decode'){s.http_status=200;n.status=200;s.loaded_network_proof_verified=true;s.visual_failure_kind='image_decode_failure';}
}
function runTest(mutEarly,mutLater,mutRun){let [a,b]=sources(),r=browser();mutEarly?.(a);mutLater?.(b);mutRun?.(r);return adjudicate(a,b,r);}
test('without guest probe: six exact URLs + rights HOLD + null browser statuses',()=>{
 const [a,b]=sources(),r=adjudicate(a,b);
 assert.equal(r.guest_capture_present,false);assert.equal(r.known_broken_slots,0);
 assert.equal(r.confirmed_broken_count,null);assert.equal(r.rows.length,6);
 assert.ok(r.rows.every(x=>x.visitor_http_status===null&&x.replacement_authorized===false));
 assert.equal(r.rows.find(x=>x.image_key==='285:5').retriever_wrapper_code,404);
});
test('six valid browser loaded images => zero verified broken, no release',()=>{
 const r=runTest();assert.equal(r.p0_census_complete,true);assert.equal(r.confirmed_broken_count,0);
 assert.equal(r.known_loaded_slots,6);assert.equal(r.replacement_release_authorized,false);
});
test('one actual browser 404 + zero pixels is confirmed broken (not wrapper evidence)',()=>{
 const r=runTest(null,null,p=>bork(p,'287:5'));
 assert.equal(r.p0_census_complete,true);assert.equal(r.confirmed_broken_count,1);
 const x=r.rows.find(v=>v.image_key==='287:5');assert.equal(x.visitor_classification,'BROWSER_CONFIRMED_BROKEN');
 assert.equal(x.visitor_http_status,404);assert.equal(x.replacement_authorized,false);
});
test('network failure with request-id proof and zero natural width confirmed',()=>{
 const r=runTest(null,null,p=>bork(p,'285:5','network'));
 assert.equal(r.known_broken_slots,1);assert.equal(r.rows[0].visitor_http_status,null);
});
test('decoded failed 200 bytes are a broken image, not successfully loaded',()=>{
 const r=runTest(null,null,p=>bork(p,'418:2','decode'));
 assert.equal(r.known_broken_slots,1);assert.equal(r.rows.find(x=>x.image_key==='418:2').visitor_classification,'BROWSER_CONFIRMED_BROKEN');
});
test('wrapper errors alone never create browser failures',()=>{
 const [a,b]=sources(),r=adjudicate(a,b);assert.equal(r.known_broken_slots,0);
 assert.equal(r.rows.find(x=>x.image_key==='418:1').visitor_http_status,null);
});
for(const [name,mut,reason] of [
 ['partial scroll',r=>r.pages[0].scroll_coverage.complete=false,'page_unverified_or_partial'],
 ['wrong page origin',r=>r.pages[0].url='https://attacker.example/post','page_unverified_or_partial'],
 ['uncached proof missing',r=>delete r.pages[0].network_images[0].was_cached,'cdp_network_proof_incomplete_or_conflicted'],
 ['request ID mismatch',r=>r.pages[0].stored_images[0].request_id='bogus','cdp_network_proof_incomplete_or_conflicted'],
 ['network status disagreement',r=>r.pages[0].network_images[0].status=404,'cdp_network_proof_incomplete_or_conflicted'],
 ['network byte mismatch',r=>r.pages[0].network_images[0].encoded_data_length=250,'cdp_network_proof_incomplete_or_conflicted'],
 ['visitor supplied stored URL mismatch',r=>r.pages[0].stored_images[0].stored_url='https://another.example/historic.jpg','image_identity_or_decode_unresolved'],
 ['DOM src mismatch',r=>r.pages[0].stored_images[0].current_src='https://another.example/historic.jpg','image_identity_or_decode_unresolved'],
 ['unknown intrinsically decoded status',r=>r.pages[0].stored_images[0].result='decoded_without_verified_response','image_identity_or_decode_unresolved'],
 ['duplicate slot',r=>r.pages[0].stored_images.push(copy(r.pages[0].stored_images[0])),'page_unverified_or_partial']
])test(name+' fails closed',()=>{
 const result=runTest(null,null,mut);assert.equal(result.p0_census_complete,false);assert.equal(result.confirmed_broken_count,null);
 assert.equal(result.rows[0].visitor_classification,'PENDING_GUEST_BROWSER');assert.equal(result.rows[0].reason,reason);
});
test('browser environment absent never masquerades as broken',()=>{
 const r=runTest(null,null,x=>{x.run_profile.cache_disabled=false});
 assert.equal(r.guest_capture_valid,false);assert.equal(r.confirmed_broken_count,null);
});
test('source ledger falsified guest HTTP rejected',()=>{
 const [a,b]=sources();a.rows[0].retriever.guest_browser_http_status=404;
 assert.throws(()=>sourceRows(a,b),/fabricated visitor evidence/);
});
test('source ledger changed original rejects',()=>{
 const [a,b]=sources();b.rows[0].published_url='https://elsewhere.example/unmatched.jpg';
 assert.throws(()=>adjudicate(a,b),/Follow-up drift/);
});
test('source ledger changed rights rejects',()=>{
 const [a,b]=sources();a.rows[0].archival_candidate.source_authorization_to_cache=true;
 assert.throws(()=>adjudicate(a,b),/Unsafe original source/);
});
test('a captured screenshot alone cannot force a release',()=>{
 const r=runTest(null,null,p=>{bork(p,'285:5');p.pages[0].screenshots=[{image_key:'285:5',result:'captured',filename:'broken-285-285-5.png',current_src:link('285:5')}];});
 assert.equal(r.rows[0].screenshot_proven,true);assert.equal(r.rows[0].replacement_authorized,false);
});
test('only a different same-subject photograph is not a proven replacement',()=>{
 const r=runTest();assert.ok(r.rows.every(x=>x.rights_release==='HOLD'));
});

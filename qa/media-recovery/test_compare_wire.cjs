'use strict';
const{test}=require('node:test'),assert=require('node:assert/strict');
const{inspectRun,compareWireRuns}=require('./compare_wire_core.cjs');
function fixture(t='2026-10-30T18:00:00.000Z',numbers=[5000,5000]){
 const url='https://finalvestige.com/example/';
 return{schema_version:1,probe_version:4,created:t,mode:'priority',viewport:'390x844',
 probe:'logged-out Chrome CDP, no npm dependencies or WordPress writes',
 browser_product:'Chrome/142.0.1.0',
 run_profile:{cache_disabled:true,service_worker_bypassed:true,scroll_step_px:720,scroll_wait_ms:220,settle_wait_ms:1000},
 requested_pages:1,verified_pages:1,pages:[{post_id:123,url,document_url:url,page_result:'inspected_browser',
 document_network_failures:[],stored_image_count:2,rendered_image_count:2,
 scroll_coverage:{complete:true,state:'full_height_scanned',reason:null},
 stored_images:numbers.map((n,i)=>({image_key:'123:'+i,request_id:'req.'+i,result:'loaded_in_probe_browser',
 verified_broken_in_browser:false,current_src_identity_verified:true,
 match:'exact_url_or_jetpack_origin',network_final_identity_verified:true,loaded_network_proof_verified:true,
 stored_url:'https://example.edu/img'+i+'.jpg',current_src:'https://example.edu/img'+i+'.jpg',natural_width:960,request_url:'https://example.edu/img'+i+'.jpg',http_status:200,transfer_bytes:n})),
 network_images:numbers.map((n,i)=>({request_id:'req.'+i,url:'https://example.edu/img'+i+'.jpg',status:200,mime_type:'image/jpeg',
 encoded_data_length:n,error:null,from_disk_cache:false,from_service_worker:false,was_cached:false})),
 image_wire_bytes_total:numbers.reduce((a,b)=>a+b,0),
 article_image_wire_bytes_total:numbers.reduce((a,b)=>a+b,0),
 article_wire_attribution_mode:'strict_cdp_request_id',
 article_wire_evidence_complete:true,article_wire_evidence_errors:[]} ]};
}
const a=()=>fixture(),b=()=>fixture('2026-10-30T19:00:00.000Z',[1200,1200]);
test('SYNTHETIC 10000 to 2400 bytes is 76%, not a live observation',()=>{const r=compareWireRuns(a(),b());assert.equal(r.reduction_percent,76);assert.equal(r.comparable,true)});
test('reject unversioned run',()=>{let r=a();delete r.probe_version;assert.equal(inspectRun(r).ok,false)});
test('reject missing cache policy',()=>{let r=a();delete r.run_profile;assert.equal(inspectRun(r).ok,false)});
test('reject changed viewport',()=>{let r=b();r.viewport='1440x900';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject changed post',()=>{let r=b();r.pages[0].url='https://finalvestige.com/other/';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject changed image slot',()=>{let r=b();r.pages[0].stored_images[0].image_key='123:99';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject lazy incomplete image',()=>{let r=a();r.pages[0].stored_images[0].result='pending_lazy_or_incomplete';assert.equal(inspectRun(r).ok,false)});
test('reject broken baseline',()=>{let r=a();r.pages[0].stored_images[0].result='confirmed_broken_in_probe_browser';assert.equal(compareWireRuns(r,b()).comparable,false)});
test('reject invented total',()=>{let r=a();r.pages[0].image_wire_bytes_total=1;assert.equal(inspectRun(r).ok,false)});
test('reject 404',()=>{let r=b();r.pages[0].network_images[0].status=404;assert.equal(inspectRun(r).ok,false)});
test('reject cache hit',()=>{let r=b();r.pages[0].network_images[0].was_cached=true;assert.equal(inspectRun(r).ok,false)});
test('reject MIME mismatch',()=>{let r=b();r.pages[0].network_images[0].mime_type='text/html';assert.equal(inspectRun(r).ok,false)});
test('reject zero bytes',()=>{let r=b();r.pages[0].network_images[0].encoded_data_length=0;assert.equal(inspectRun(r).ok,false)});
test('reject browser version drift',()=>{let r=b();r.browser_product='Chrome/143.0.0.0';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject incomplete page set',()=>{let r=a();r.requested_pages=2;assert.equal(inspectRun(r).ok,false)});
test('reject backward run chronology',()=>{let r=fixture('2026-10-30T17:00:00.000Z',[1200,1200]);assert.equal(compareWireRuns(a(),r).comparable,false)});
test('negative saving means heavier page',()=>{let r=fixture('2026-10-30T19:00:00.000Z',[7500,7500]);assert.equal(compareWireRuns(a(),r).reduction_percent,-50)});


test('reject legacy v2 without currentSrc proof',()=>{
 const r=a();r.probe_version=2;
 assert.equal(inspectRun(r).ok,false);
});
test('reject unverified decoded identity even when image visually loads',()=>{
 const r=a();r.pages[0].stored_images[0].current_src_identity_verified=false;
 assert.equal(inspectRun(r).ok,false);
});
test('reject missing decoded currentSrc',()=>{
 const r=a();r.pages[0].stored_images[0].current_src=null;
 assert.equal(inspectRun(r).ok,false);
});
test('reject fabricated slot URL with unrelated network event but matching aggregate total',()=>{
 const r=a();r.pages[0].network_images[0].url='https://unrelated.example.org/other.jpg';
 assert.equal(inspectRun(r).ok,false);
 assert.ok(inspectRun(r).errors.some(x=>x.startsWith('slot_network_evidence_missing')));
});
test('reject invented per-slot wire bytes even with matching aggregate total',()=>{
 const r=a();r.pages[0].stored_images[0].transfer_bytes=4000;
 assert.equal(inspectRun(r).ok,false);
});
test('reject currentSrc that differs from matched network source',()=>{
 const r=a();r.pages[0].stored_images[0].current_src='https://other.example.org/other.jpg';
 assert.equal(inspectRun(r).ok,false);
});
test('redirect alias alone cannot prove historical identity when final URL differs',()=>{
 const r=a(),n=r.pages[0].network_images[0],old=n.url;
 n.url='https://cdn.example.edu/optimized.jpg';n.url_aliases=[old];
 assert.equal(inspectRun(r).ok,false);
 assert.ok(inspectRun(r).errors.includes('article_wire_scope_mismatch:123'));
});
test('multiple visible uses of one URL can share one actual network request without double-counting bytes',()=>{
 const r=a(),p=r.pages[0],url='https://example.edu/shared.jpg';
 p.stored_images.forEach(v=>{v.stored_url=url;v.current_src=url;v.request_url=url;v.transfer_bytes=5000;v.request_id='req.shared';});
 p.network_images=[{request_id:'req.shared',url,status:200,mime_type:'image/jpeg',encoded_data_length:5000,
  error:null,from_disk_cache:false,from_service_worker:false,was_cached:false}];
 p.image_wire_bytes_total=5000;p.article_image_wire_bytes_total=5000;
 assert.equal(inspectRun(r).ok,true);
});

test('reject truncated document scan before calculating claimed savings',()=>{
 const r=a();r.pages[0].scroll_coverage={complete:false,state:'incomplete_scan',reason:'bottom_not_reached'};
 assert.equal(inspectRun(r).ok,false);
 assert.ok(inspectRun(r).errors.includes('incomplete_viewport_scroll_coverage:123'));
});
test('reject missing scan-coverage evidence',()=>{
 const r=a();delete r.pages[0].scroll_coverage;
 assert.equal(compareWireRuns(r,b()).comparable,false);
});


test('reject source swap masquerading as a 76% compression saving',()=>{
 const r=b(),p=r.pages[0],v=p.stored_images[0];
 const wrong='https://example.edu/completely-different-historical-event.jpg';
 v.stored_url=wrong;v.current_src=wrong;v.request_url=wrong;
 p.network_images[0].url=wrong;
 assert.equal(inspectRun(r).ok,true,'both individual runs have internally valid network evidence');
 const pair=compareWireRuns(a(),r);
 assert.equal(pair.comparable,false);
 assert.equal(pair.status,'NOT_COMPARABLE');
 assert.ok(pair.reasons.some(x=>x==='stored_asset_changed:123:123:0'));
 assert.equal(Object.hasOwn(pair,'reduction_percent'),false);
});
test('reject visible historical-description drift between before and after runs',()=>{
 const earlier=a(),later=b();
 earlier.pages[0].stored_images[0].rendered_alt='The original historical subject';
 later.pages[0].stored_images[0].rendered_alt='A different historical subject';
 assert.equal(inspectRun(earlier).ok,true);
 assert.equal(inspectRun(later).ok,true);
 const pair=compareWireRuns(earlier,later);
 assert.equal(pair.comparable,false);
 assert.ok(pair.reasons.includes('historical_alt_changed:123:123:0'));
});
test('accept identical stored sources and descriptions with different encoded bytes',()=>{
 const earlier=a(),later=b();
 for(const r of [earlier,later])r.pages[0].stored_images.forEach((v,i)=>v.rendered_alt='Historical photograph '+i);
 const pair=compareWireRuns(earlier,later);
 assert.equal(pair.comparable,true);
 assert.equal(pair.reduction_percent,76);
});

test('unrelated page-chrome image cannot masquerade as article-image savings',()=>{
 const before=a(),after=fixture('2026-10-30T19:00:00.000Z',[5000,5000]);
 const extra={request_id:'ui.extra',url:'https://finalvestige.com/logo-huge.png',status:200,mime_type:'image/png',
  encoded_data_length:50000,error:null,from_disk_cache:false,from_service_worker:false,was_cached:false};
 before.pages[0].network_images.push(extra);
 before.pages[0].image_wire_bytes_total=60000;
 assert.equal(inspectRun(before).ok,true);
 assert.equal(inspectRun(after).ok,true);
 const paired=compareWireRuns(before,after);
 assert.equal(paired.comparable,true);
 assert.equal(paired.reduction_percent,0);
 assert.equal(paired.before_image_wire_bytes,10000);
 assert.equal(paired.per_post[0].before_unattributed_image_bytes,50000);
});
test('reject a fabricated article-only total even when all-image total is correct',()=>{
 const r=a();r.pages[0].article_image_wire_bytes_total=7600;
 assert.equal(inspectRun(r).ok,false);
 assert.ok(inspectRun(r).errors.includes('article_wire_scope_mismatch:123'));
});
test('reject purported article bytes from a redirect to unrelated final media',()=>{
 const r=a(),n=r.pages[0].network_images[0],old=n.url;
 n.url='https://other.example.org/different-historical-subject.jpg';n.url_aliases=[old];
 // Deliberately retains old request URL, as a raw alias alone is not image identity.
 assert.equal(inspectRun(r).ok,false);
 assert.ok(inspectRun(r).errors.includes('article_wire_scope_mismatch:123'));
});

test('reject article byte claim without independent successful CDP proof',()=>{
 const r=a();r.pages[0].stored_images[0].loaded_network_proof_verified=false;
 assert.equal(inspectRun(r).ok,false);
});
test('reject article byte claim from CDN redirect identity uncertainty',()=>{
 const r=a();r.pages[0].stored_images[0].network_final_identity_verified=false;
 assert.equal(inspectRun(r).ok,false);
});
test('reject article byte claim from ALT-only DOM identity guess',()=>{
 const r=a();r.pages[0].stored_images[0].match='alt_only_unverified';
 assert.equal(inspectRun(r).ok,false);
});

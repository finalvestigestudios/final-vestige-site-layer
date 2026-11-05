'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {census,reconcile}=require('./reconcile_all61_guest_inventory_v1.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
const P='https://finalvestige.com/2026/08/synthetic-test/';
const U='https://images.example.org/photo.jpg';
const limits={parts:1,posts:1,images:1};
function fixture(){
 const i={key:'7:0',post_id:7,slot:0,post_url:P,source_url:U,
  source_host:'images.example.org',source_kind:'external',actual_http_status:null,
  broken_in_browser:null,allowed_to_localize:false,target_max_width_px:960};
 const parts=[{batch:1,post_count:1,image_count:1,posts:[{id:7,url:P,images:1}],images:[i]}];
 const v={image_key:'7:0',stored_url:U,current_src:U,request_url:U,
  request_id:'image-001',complete:true,current_src_identity_verified:true,
  network_final_identity_verified:true,redirected_image_identity_unverified:false,
  natural_width:400,natural_height:300,http_status:200,response_mime_type:'image/jpeg',
  transfer_bytes:301,result:'loaded_in_probe_browser',loaded_network_proof_verified:true,
  verified_broken_in_browser:false};
 const n={request_id:'image-001',url:U,status:200,mime_type:'image/jpeg',
  encoded_data_length:301,error:null,was_cached:false,from_disk_cache:false,
  from_service_worker:false};
 const page={post_id:7,url:P,page_result:'inspected_browser',
  scroll_coverage:{complete:true,state:'full_height_scanned'},
  stored_image_count:1,stored_images:[v],network_images:[n],screenshots:[]};
 const run={probe_version:3,mode:'all',viewport:'390x844',
  run_profile:{cache_disabled:true,service_worker_bypassed:true},
  requested_pages:1,pages:[page]};
 return {parts,run};
}
test('no browser run never invents a broken count, status, or transferred bytes',()=>{
 const x=reconcile(fixture().parts,null,limits);
 assert.equal(x.totals.sitewide_confirmed_broken,null);
 assert.equal(x.rows[0].actual_browser_http_status,null);
 assert.equal(x.totals.cold_article_image_encoded_bytes,null);
 assert.equal(x.totals.unverified,1);
});
test('a valid cold guest probe can verify exactly one loaded image',()=>{
 const {parts,run}=fixture(),x=reconcile(parts,run,limits);
 assert.equal(x.sitewide_browser_verification_complete,true);
 assert.equal(x.totals.verified_loaded,1);
 assert.equal(x.totals.sitewide_confirmed_broken,0);
 assert.equal(x.totals.cold_article_image_encoded_bytes,301);
 assert.equal(x.rows[0].actual_browser_http_status,200);
});
test('never grant media caching or a WordPress write from network proof',()=>{
 const {parts,run}=fixture(),x=reconcile(parts,run,limits);
 assert.equal(x.rows[0].caching_authorized,false);
 assert.equal(x.rows[0].wp_edit_authorized,false);
 assert.equal(x.rows[0].archival_rights,'HOLD');
 assert.equal(x.totals.reported_76_pct_reduction_verified,false);
});
const bads=[
 ['HTTP response mismatch',x=>x.run.pages[0].network_images[0].status=404],
 ['MIME contradiction',x=>x.run.pages[0].network_images[0].mime_type='text/html'],
 ['encoded byte contradiction',x=>x.run.pages[0].network_images[0].encoded_data_length=25],
 ['missing cache flag',x=>delete x.run.pages[0].network_images[0].was_cached],
 ['disk-cache flag',x=>x.run.pages[0].network_images[0].from_disk_cache=true],
 ['service-worker cache',x=>x.run.pages[0].network_images[0].from_service_worker=true],
 ['missing decoded height',x=>x.run.pages[0].stored_images[0].natural_height=null],
 ['zero decoded width',x=>x.run.pages[0].stored_images[0].natural_width=0],
 ['wrong CDP request ID',x=>x.run.pages[0].network_images[0].request_id='other'],
 ['duplicate CDP request',x=>x.run.pages[0].network_images.push(clone(x.run.pages[0].network_images[0]))],
 ['false source match',x=>x.run.pages[0].stored_images[0].stored_url='https://images.example.org/other.jpg'],
 ['incomplete scroll',x=>x.run.pages[0].scroll_coverage.complete=false],
 ['other post URL',x=>x.run.pages[0].url='https://finalvestige.com/other/'],
 ['post number drift',x=>x.run.pages[0].post_id=70],
 ['not a cold probe',x=>x.run.run_profile.cache_disabled=false],
 ['service worker not bypassed',x=>x.run.run_profile.service_worker_bypassed=false],
 ['invalid viewport',x=>x.run.viewport='800x800'],
 ['requested count mismatch',x=>x.run.requested_pages=2],
 ['missing DOM slot',x=>x.run.pages[0].stored_images=[]],
 ['extra DOM slot',x=>x.run.pages[0].stored_images.push(clone(x.run.pages[0].stored_images[0]))]
];
for(const [label,change] of bads)test('fail closed: '+label,()=>{
 const x=fixture();change(x);
 const result=reconcile(x.parts,x.run,limits);
 assert.equal(result.sitewide_browser_verification_complete,false);
 assert.equal(result.totals.sitewide_confirmed_broken,null);
});
test('a claimed 404 without captured matching screenshot cannot prove a missing image',()=>{
 const x=fixture(),v=x.run.pages[0].stored_images[0],n=x.run.pages[0].network_images[0];
 Object.assign(v,{result:'confirmed_broken_in_probe_browser',verified_broken_in_browser:true,
  natural_width:0,natural_height:0,http_status:404,response_mime_type:'text/html',
  transfer_bytes:39,visual_failure_kind:'http_error'});
 Object.assign(n,{status:404,mime_type:'text/html',encoded_data_length:39});
 assert.equal(reconcile(x.parts,x.run,limits).totals.sitewide_confirmed_broken,null);
 x.run.pages[0].screenshots=[{image_key:'7:0',result:'captured',current_src:U,filename:'broken-7-0-1.png'}];
 assert.equal(reconcile(x.parts,x.run,limits).totals.sitewide_confirmed_broken,1);
});
test('duplicate DOM use of one verified CDP request is charged only once',()=>{
 const x=fixture(),p=x.run.pages[0],i=clone(x.parts[0].images[0]);
 i.key='7:1';i.slot=1;x.parts[0].images.push(i);
 x.parts[0].image_count=2;x.parts[0].posts[0].images=2;
 p.stored_image_count=2;const v=clone(p.stored_images[0]);v.image_key='7:1';
 p.stored_images.push(v);
 const result=reconcile(x.parts,x.run,{parts:1,posts:1,images:2});
 assert.equal(result.totals.verified_loaded,2);
 assert.equal(result.totals.cold_article_image_encoded_bytes,301);
});
test('rejects fabricated visitor status in the frozen CMS source audit',()=>{
 const x=fixture();x.parts[0].images[0].actual_http_status=404;
 assert.throws(()=>census(x.parts,limits));
});
test('rejects auto-authorized third-party media caching',()=>{
 const x=fixture();x.parts[0].images[0].allowed_to_localize=true;
 assert.throws(()=>census(x.parts,limits));
});
test('rejects changed WordPress image source host',()=>{
 const x=fixture();x.parts[0].images[0].source_host='attacker.example';
 assert.throws(()=>census(x.parts,limits));
});
test('rejects missing frozen image slots',()=>{
 const x=fixture();x.parts[0].images=[];
 assert.throws(()=>census(x.parts,limits));
});

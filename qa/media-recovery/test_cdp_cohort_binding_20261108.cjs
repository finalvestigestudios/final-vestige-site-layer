'use strict';
const assert=require('node:assert/strict'),test=require('node:test');
const {audit,sources}=require('./validate_cdp_cohort_binding_20261108.cjs');
const cp=x=>JSON.parse(JSON.stringify(x));
function sample(){
 const rows=[];
 for(let i=0;i<66;i++){
  const id=1000+i,n=i===0?295:i===65?0:1,slots=[];
  for(let j=0;j<n;j++)slots.push({key:id+':'+j,source_url:'https://example.org/'+id+'/'+j+'.jpg'});
  rows.push({id,post_url:'https://finalvestige.com/article/'+id+'/',slots});
 }
 rows[61].slots.push({key:'1061:1',source_url:'https://example.org/1061/1.jpg'});
 rows[61].slots.push({key:'1061:2',source_url:'https://example.org/1061/2.jpg'});
 assert.equal(rows.slice(0,61).reduce((n,r)=>n+r.slots.length,0),355);
 assert.equal(rows.reduce((n,r)=>n+r.slots.length,0),361);
 return {schema:'fv-sitewide-wire-cohort-manifest-v1',data_cohorts_not_interchangeable:true,
 rights_and_post_edits_authorized:false,legacy:{expected_posts:61,expected_slots:355,post_ids:rows.slice(0,61).map(r=>r.id)},
 expanded:{expected_posts:66,expected_slots:361,post_ids:rows.map(r=>r.id)},rows};
}
function run(m,c='expanded'){
 const ids=new Set(m[c].post_ids);
 return {status:'complete_browser_image_census',mode:'all',viewport:'390x844',browser_product:'Chrome/140',
 requested_pages:ids.size,verified_pages:ids.size,confirmed_broken_count:0,
 image_census_coverage:{complete:true,confirmed_broken_count:0},
 run_profile:{cache_disabled:true,service_worker_bypassed:true},
 pages:m.rows.filter(r=>ids.has(r.id)).map(r=>({post_id:r.id,url:r.post_url,
 page_result:'inspected_browser',scroll_coverage:{complete:true,state:'full_height_scanned'},
 image_census:{complete:true},confirmed_broken_count:0,stored_image_count:r.slots.length,
 stored_images:r.slots.map(s=>({image_key:s.key,stored_url:s.source_url})),
 matched_article_network_requests:r.slots.length?1:0,
 article_image_wire_bytes_total:r.slots.length?100:0}))};
}
const cmp=()=>({state:'LAB_PAIR_MEASURED',post_count:66,baseline_cdp_bytes:1000,candidate_cdp_bytes:240,reduction_percent:76});
function neg(name,mut,needle){test(name,()=>{const m=sample(),b=run(m),a=cp(b);mut(m,b,a);const x=audit(m,b,a,'expanded',cmp);
 assert.equal(x.state,'HOLD');assert.equal(x.sitewide_76_percent_claim_permitted,false);
 assert.ok(x.reasons.some(s=>s.includes(needle)),JSON.stringify(x.reasons.slice(0,4)))});}
test('66 posts / 361 slots including zero-image article gate passes as LAB ONLY',()=>{
 const m=sample(),b=run(m),r=audit(m,b,cp(b),'expanded',cmp);
 assert.equal(r.state,'BOUND_LAB_PAIR_ONLY');assert.equal(r.expected_slots,361);
 assert.equal(r.sitewide_76_percent_claim_permitted,false);assert.equal(r.wp_write_authorized,false);
});
test('frozen 61 posts / 355 slots remains a separate comparable cohort',()=>{
 const m=sample(),b=run(m,'legacy');
 assert.equal(audit(m,b,cp(b),'legacy',cmp).state,'BOUND_LAB_PAIR_ONLY');
});
test('no comparator means source bound but byte savings unknown',()=>{
 const m=sample(),b=run(m);
 assert.equal(audit(m,b,cp(b)).state,'BOUND_AWAITING_CDP');
});
neg('two 66-post reports can silently remove the same 295 images unless bound',(m,b,a)=>{
 for(const x of [b.pages[0],a.pages[0]]){x.stored_images=[];x.stored_image_count=0;x.matched_article_network_requests=0;x.article_image_wire_bytes_total=0}
},'missing_or_extra_image_slots');
neg('one missing post cannot prove full 66',(m,b,a)=>{a.pages.pop();a.requested_pages--;a.verified_pages--},'incomplete_or_unsafe_collector');
neg('duplicate post refused',(m,b,a)=>{a.pages[2]=cp(a.pages[1])},'duplicate_or_unknown_post');
neg('published original changed without authorization',(m,b,a)=>{a.pages[0].stored_images[0].stored_url='https://example.org/replacement.jpg'},'missing_or_drifted_source');
neg('zero-image page cannot contain invented image transfer',(m,b,a)=>{a.pages.at(-1).article_image_wire_bytes_total=8},'invented_zero_image_bytes');
neg('partial scroll rejected',(m,b,a)=>{a.pages[2].scroll_coverage.complete=false},'incomplete_article');
neg('different article canonical URL rejected',(m,b,a)=>{a.pages[2].url='https://finalvestige.com/other'},'post_url_drift');
neg('prioritized mode cannot masquerade as all 66',(m,b,a)=>{a.mode='priority'},'incomplete_or_unsafe_collector');
neg('failed image census rejected',(m,b,a)=>{a.image_census_coverage.complete=false},'incomplete_or_unsafe_collector');
neg('dissimilar device viewport rejected',(m,b,a)=>{a.viewport='1440x900'},'unpaired_browser_or_cache_configuration');
neg('wrong 66-post expected count rejected',(m,b,a)=>{m.expanded.expected_slots=42},'manifest_schema_counts_or_cohort_drift');
neg('altered original in source manifest caught',(m,b,a)=>{m.rows[0].slots[0].source_url='https://example.org/altered.jpg'},'missing_or_drifted_source');
neg('duplicate manifest slot caught',(m,b,a)=>{m.rows[0].slots[1].key=m.rows[0].slots[0].key},'invalid_manifest_slot');
neg('missing source manifest article caught',(m,b,a)=>{m.rows.pop()},'manifest_schema_counts_or_cohort_drift');
neg('forged claims of broken image count cannot pass',(m,b,a)=>{a.confirmed_broken_count=1},'incomplete_or_unsafe_collector');
neg('cache-enabled browser excluded',(m,b,a)=>{a.run_profile.cache_disabled=false},'incomplete_or_unsafe_collector');
test('existing cold comparator HOLD is not elevated to LAB',()=>{
 const m=sample(),b=run(m);
 assert.equal(audit(m,b,cp(b),'expanded',()=>({state:'HOLD'})).state,'HOLD')
});

'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {evaluateTotalImageWire:evaluate}=require('./full_image_request_census_20261118.cjs');
function fixture(extraBefore=0,extraAfter=0,cohort='historic-61'){
 const count=cohort==='historic-61'?61:66;
 const mk=(phase,device)=>({trace_sha256:'a'.repeat(64),trace_evidence_url:'https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154',pages:Array.from({length:count},(_,i)=>{
   const post_id=i+1,url='https://finalvestige.com/example-'+(i+1)+'/',id=phase+'-'+device+'-'+(i+1);
   const base={request_id:id,final_url:'https://i0.wp.com/archives.gov/photo.jpg?w=960',http_status:200,mime:'image/jpeg',decoded:true,from_cache:false,from_service_worker:false,transfer_bytes:phase==='before'?100:20};
   return {post_id,url,images:[{...base,asset_id:post_id+':0'}]};
 })});
 const inline={schema:'fv-image-wire-parity-v1',cohort:{id:cohort},manifest_sha256:'b'.repeat(64),before:{},after:{}};
 const full={schema:'fv-cdp-all-image-requests-v1',cohort_id:cohort,manifest_sha256:inline.manifest_sha256,before:{},after:{}};
 for(const phase of ['before','after'])for(const device of ['desktop','mobile']){
   inline[phase][device]=mk(phase,device);
   full[phase][device]={trace_sha256:'a'.repeat(64),trace_evidence_url:inline[phase][device].trace_evidence_url,
      pages:inline[phase][device].pages.map((p,i)=>{
        const requests=p.images.map(m=>({...m,resource_type:'Image'}));
        if(i===0&&(phase==='before'?extraBefore:extraAfter)>0)requests.push({request_id:'extra-'+phase+'-'+device,resource_type:'Image',final_url:'https://finalvestige.com/css/background.png',http_status:200,mime:'image/png',decoded:true,from_cache:false,from_service_worker:false,transfer_metric:'CDP_ENCODED_DATALENGTH',transfer_bytes:phase==='before'?extraBefore:extraAfter});
        for(const r of requests)r.transfer_metric='CDP_ENCODED_DATALENGTH';
        return {post_id:p.post_id,url:p.url,complete_image_requests:true,cdp_image_events_complete:true,cdp_image_request_count:requests.length,image_requests:requests};
      })};
 }
 return {inline,full};
}
test('complete-61 census verifies total image bytes',()=>{const x=fixture();assert.equal(evaluate(x.inline,x.full).threshold_met,true);});
test('complete-66 remains independent',()=>{const x=fixture(0,0,'current-66');assert.equal(evaluate(x.inline,x.full).threshold_met,true);});
test('untracked CSS background invalidates inflated inline savings',()=>{const x=fixture(10000,10000);const y=evaluate(x.inline,x.full);assert.equal(y.threshold_met,false);assert.equal(y.totals.desktop.other_image_requests_before,1);});
test('other assets may improve and still pass total gate',()=>{const x=fixture(100,10);assert.equal(evaluate(x.inline,x.full).threshold_met,true);});
test('missing CDP image event counts HOLD',()=>{const x=fixture();x.full.before.desktop.pages[0].cdp_image_request_count=0;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('page_or_event_coverage')));});
test('missing image in all-request stream HOLD',()=>{const x=fixture();x.full.after.mobile.pages[0].image_requests=[];x.full.after.mobile.pages[0].cdp_image_request_count=0;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('inline_to_cdp_mismatch')));});
test('same request duplicate cannot reduce measured bytes',()=>{const x=fixture();x.full.before.desktop.pages[0].image_requests.push({...x.full.before.desktop.pages[0].image_requests[0]});x.full.before.desktop.pages[0].cdp_image_request_count=2;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('invalid_or_duplicate_image_event')));});
test('trace mismatch cannot be treated as same capture',()=>{const x=fixture();x.full.after.desktop.trace_sha256='c'.repeat(64);assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('capture_or_trace')));});
test('bytes mismatch between inline and CDP is rejected',()=>{const x=fixture();x.full.after.mobile.pages[0].image_requests[0].transfer_bytes=1;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('inline_to_cdp_mismatch')));});
test('different final URL is rejected',()=>{const x=fixture();x.full.before.mobile.pages[0].image_requests[0].final_url='https://elsewhere.example/photo.jpg';assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('inline_to_cdp_mismatch')));});
test('guest cache hit HOLD',()=>{const x=fixture();x.full.before.desktop.pages[0].image_requests[0].from_cache=true;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('invalid_or_duplicate_image_event')));});
test('broken noninline image after HOLD',()=>{const x=fixture(100,10);const r=x.full.after.mobile.pages[0].image_requests[1];r.http_status=404;r.mime='text/html';r.decoded=false;assert.ok(evaluate(x.inline,x.full).errors.some(s=>s.includes('unusable_image_event')));});
test('baseline 404 HTML excludes error body from image bytes',()=>{const x=fixture(100,10);const r=x.full.before.desktop.pages[0].image_requests[1];r.http_status=404;r.mime='text/html';r.decoded=false;assert.equal(evaluate(x.inline,x.full).totals.desktop.before_bytes,6100);});
test('near-76 percent rounding still HOLD',()=>{const x=fixture();for(const d of ['desktop','mobile'])for(const p of x.full.after[d].pages)p.image_requests[0].transfer_bytes=24;for(const d of ['desktop','mobile'])for(const p of x.inline.after[d].pages)p.images[0].transfer_bytes=24;x.full.after.desktop.pages[0].image_requests[0].transfer_bytes=25;x.inline.after.desktop.pages[0].images[0].transfer_bytes=25;const y=evaluate(x.inline,x.full);assert.equal(y.threshold_met,false);});
test('public validation always requires independent visual and trace evidence',()=>{const x=fixture();assert.equal(evaluate(x.inline,x.full).claim_publicly_verified,false);});
test('targeted test is never called a sitewide result',()=>{const x=fixture();x.inline.cohort.id=x.full.cohort_id='targeted';assert.equal(evaluate(x.inline,x.full).threshold_met,false);});

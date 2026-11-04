'use strict';
// Adversarial, synthetic-only tests. These fixture numbers are never site evidence.
const {evaluate,SOURCE}=require('./evaluate_image_wire_20261103.cjs');
let passed=0;
const check=(x,s)=>{if(!x)throw Error(s||'failed assertion');};
const eq=(a,b,s)=>check(Object.is(a,b),(s||'not equal')+': '+JSON.stringify(a)+' != '+JSON.stringify(b));
const copy=x=>JSON.parse(JSON.stringify(x));
const conditions={browser:'Chrome',browser_version:'142',viewport_width:1280,viewport_height:800,
 device_scale_factor:1,network_profile:'unthrottled',cache_mode:'cold',locale:'en-US'};
function run(slots,bytes){return {method:SOURCE,all_inline_images_loaded:true,all_image_requests_captured:true,
 cache_disabled:true,capture_unmodified:true,conditions:copy(conditions),
 requests:[{request_id:'CDP-1',resource_type:'Image',slot_keys:slots.slice(),request_url:'https://finalvestige.com/a.png',
 final_url:'https://finalvestige.com/a.png',http_status:200,mime_type:'image/png',
 encoded_data_length:bytes,decode_ok:true,natural_width:960,natural_height:540,
 from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
 from_prefetch_cache:false,loading_finished:true,terminal_response:true,retry:false}]};}
function pair(id,slots,repeats=1){return{post_id:id,page_url:'https://finalvestige.com/article-'+id+'/',
 expected_slots:slots,before:Array.from({length:repeats},()=>run(slots,1000)),
 after:Array.from({length:repeats},()=>run(slots,240))};}
const basic=()=>({schema_version:1,source_inventory_id:'SYNTHETIC-NOT-LIVE',pairs:[pair(34,['34:0'])]});
function invalid(label,mutate,fragment){const d=basic();mutate(d);const result=evaluate(d);
 eq(result.status,'INSUFFICIENT_DATA',label);
 check(result.reason_codes.some(x=>x.includes(fragment)),label+': '+result.reason_codes.join('; '));passed++;}
function runTests(){
 let result=evaluate(basic());
 eq(result.status,'LIMITED_SAMPLE_MEASURED');eq(result.measured_reduction_percent,76);
 eq(result.sitewide_76_percent_verified,false);eq(result.can_claim_total_page_savings,false);passed++;
 let d=basic();d.pairs[0].expected_slots=['34:0','34:1'];
 for(const k of ['before','after'])d.pairs[0][k][0].requests[0].slot_keys=['34:0','34:1'];
 result=evaluate(d);eq(result.observed_slot_count,2);eq(result.baseline_bytes_by_repeat[0],1000);passed++;
 invalid('no slots',x=>x.pairs[0].before[0].requests[0].slot_keys=[],'no mapped slots');
 invalid('cache',x=>x.pairs[0].after[0].requests[0].from_disk_cache=true,'cached/unknown');
 invalid('service worker',x=>x.pairs[0].before[0].requests[0].from_service_worker=true,'cached/unknown');
 invalid('prefetch',x=>x.pairs[0].after[0].requests[0].from_prefetch_cache=true,'cached/unknown');
 invalid('real HTTP failure',x=>x.pairs[0].after[0].requests[0].http_status=404,'not successful');
 invalid('bad MIME',x=>x.pairs[0].after[0].requests[0].mime_type='text/html','wrong MIME');
 invalid('XHR spoof',x=>x.pairs[0].after[0].requests[0].resource_type='Fetch','not CDP Image');
 invalid('missing CDP type',x=>delete x.pairs[0].before[0].requests[0].resource_type,'not CDP Image');
 invalid('decode failed',x=>x.pairs[0].before[0].requests[0].decode_ok=false,'decode/dimensions');
 invalid('unknown bytes',x=>x.pairs[0].before[0].requests[0].encoded_data_length=null,'unknown actual CDP');
 invalid('zero bytes',x=>x.pairs[0].before[0].requests[0].encoded_data_length=0,'unknown actual CDP');
 invalid('original file size not method',x=>x.pairs[0].before[0].method='WordPress original metadata','invalid CDP');
 invalid('not cold',x=>x.pairs[0].before[0].cache_disabled=false,'invalid CDP');
 invalid('lazy image not loaded',x=>x.pairs[0].before[0].all_inline_images_loaded=false,'invalid CDP');
 invalid('wrong DPR',x=>x.pairs[0].after[0].conditions.device_scale_factor=2,'unequal browser');
 invalid('wrong network',x=>x.pairs[0].after[0].conditions.network_profile='Slow 4G','unequal browser');
 invalid('retry',x=>x.pairs[0].before[0].requests[0].retry=true,'incomplete or retried');
 invalid('intermediate redirect',x=>x.pairs[0].before[0].requests[0].terminal_response=false,'incomplete or retried');
 invalid('wrong site',x=>x.pairs[0].page_url='https://example.com/article','non-FinalVestige');
 invalid('slot not in post',x=>x.pairs[0].expected_slots=['99:0'],'invalid slot');
 invalid('slot not found',x=>x.pairs[0].expected_slots=['34:1'],'unknown/duplicate slot');
 invalid('missing after',x=>x.pairs[0].after=[],'unpaired runs');
 invalid('no inventory',x=>x.source_inventory_id='','source inventory');
 invalid('duplicate request',x=>x.pairs[0].before[0].requests.push(copy(x.pairs[0].before[0].requests[0])),'duplicate/missing request');
 const inventory=require('./wire_source_inventory_20261030.json');
 const parts=require('./validate_inventory.cjs').loadSnapshot().parts;
 const originals=new Map(parts.flatMap(p=>p.images.map(im=>[im.key,im.source_url])));
 d={schema_version:1,source_inventory_id:inventory.inventory_id,pairs:[]};
 for(const row of inventory.posts){
   const p=pair(row.post_id,row.expected_slots,3);p.page_url=row.page_url;
   for(const phase of ['before','after'])for(const run of p[phase]){
    const orig=run.requests[0],len=row.expected_slots.length,size=orig.encoded_data_length;
    run.requests=row.expected_slots.map((s,i)=>{const u=originals.get(s);
     return {...orig,request_id:'CDP-'+i,slot_keys:[s],request_url:u,final_url:u,
      encoded_data_length:Math.floor(size/len)+(i<size%len?1:0),
      dom_stored_sources:{[s]:u},dom_current_sources:{[s]:u}};
    });
   }
   d.pairs.push(p);
 }
 result=evaluate(d,inventory,parts);eq(result.status,'SITEWIDE_IMAGE_TRANSFER_MEASURED');
 const unbound=evaluate(d,inventory);eq(unbound.status,'LIMITED_SAMPLE_MEASURED');eq(unbound.sitewide_76_percent_verified,false);passed++;
 const swapped=copy(d);swapped.pairs[0].after[0].requests[0].dom_stored_sources[swapped.pairs[0].expected_slots[0]]='https://finalvestige.com/decoy.png';
 const rejected=evaluate(swapped,inventory,parts);eq(rejected.sitewide_76_percent_verified,false);eq(rejected.status,'LIMITED_SAMPLE_MEASURED');
 check(rejected.source_binding_reason_codes.some(x=>x.includes('frozen stored URL drift')),'source swap must block the sitewide claim');passed++;
 const mixed=copy(d);
 for(const phase of ['before','after'])for(const run of mixed.pairs[1][phase])run.conditions.viewport_width=1920;
 const mixedResult=evaluate(mixed,inventory,parts);
 eq(mixedResult.status,'INSUFFICIENT_DATA');
 check(mixedResult.reason_codes.some(x=>x.includes('unequal cross-post browser conditions')),'cross-post mixed viewport not blocked');passed++;
 eq(result.observed_post_count,61);eq(result.observed_slot_count,355);
 eq(result.sitewide_76_percent_verified,true);eq(result.repetitions,3);passed++;
 d.pairs[0].after[0].requests[0].encoded_data_length=800;
 result=evaluate(d,inventory,parts);eq(result.status,'SITEWIDE_IMAGE_TRANSFER_MEASURED');
 eq(result.sitewide_76_percent_verified,false);
 check(result.measured_reduction_percent<76,'one repeat below threshold must block 76 claim');passed++;
 // Median-run 76% is misleading when the heaviest run saves zero actual bytes.
 const skew=copy(d);skew.pairs[0].after[0].requests[0].encoded_data_length=240;
 for(const p of skew.pairs){
  for(const req of p.before[2].requests)req.encoded_data_length=100000;
  for(const req of p.after[2].requests)req.encoded_data_length=100000;
 }
 result=evaluate(skew,inventory,parts);eq(result.status,'SITEWIDE_IMAGE_TRANSFER_MEASURED');
 eq(result.median_repeat_reduction_percent,76);
 check(result.measured_reduction_percent<2,'pooled byte weighting must expose skew');
 eq(result.sitewide_76_percent_verified,false);passed++;
 const pooledCheck=copy(d);pooledCheck.pairs[0].after[0].requests[0].encoded_data_length=240;
 result=evaluate(pooledCheck,inventory,parts);
 eq(result.measured_reduction_percent,76);
 eq(result.pooled_baseline_bytes,183000);eq(result.pooled_candidate_bytes,43920);passed++;
 const overflow=copy(pooledCheck);
 for(const p of overflow.pairs){
  for(const run of p.before)run.requests[0].encoded_data_length=100000000000000;
  for(const run of p.after)run.requests[0].encoded_data_length=24000000000000;
 }
 result=evaluate(overflow,inventory,parts);eq(result.status,'INSUFFICIENT_DATA');
 check(result.reason_codes.some(x=>x.includes('unsafe pooled transfer bytes')),'unsafe pooled integer should fail closed');passed++;
 d.pairs[0].before[1].conditions.viewport_width=1234;
 result=evaluate(d,inventory,parts);eq(result.status,'INSUFFICIENT_DATA');passed++;
 const frozen=copy(d);frozen.pairs[0].before[1].conditions.viewport_width=1280;
 result=evaluate(frozen);eq(result.status,'LIMITED_SAMPLE_MEASURED');eq(result.sitewide_76_percent_verified,false);passed++;
 const altered=copy(frozen);altered.pairs[0].page_url='https://finalvestige.com/another-article/';
 result=evaluate(altered,inventory,parts);eq(result.status,'LIMITED_SAMPLE_MEASURED');passed++;
 const altInventory=copy(inventory);altInventory.inventory_id='wrong-fingerprint';
 result=evaluate(frozen,altInventory);eq(result.status,'LIMITED_SAMPLE_MEASURED');passed++;
 return {passed,source:'synthetic mutations only',real_guest_http_tests:0,real_wire_bytes_measured:false};
}
module.exports={runTests};
if(require.main===module)process.stdout.write(JSON.stringify(runTests())+'\n');

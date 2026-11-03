'use strict';
// Pure, read-only CDP evidence aggregator. It neither probes image hosts nor edits WordPress.
const SOURCE='CDP Network.loadingFinished.encodedDataLength';
const url=s=>typeof s==='string'&&/^https?:\/\/[^\s/?#]+/i.test(s);
const host=s=>(url(s)?s.match(/^https?:\/\/([^/?#]+)/i)[1].toLowerCase():'');
const okConditions=c=>c&&typeof c==='object'&&typeof c.browser==='string'&&c.browser.length>0&&
 typeof c.browser_version==='string'&&c.browser_version.length>0&&
 Number.isInteger(c.viewport_width)&&c.viewport_width>0&&Number.isInteger(c.viewport_height)&&c.viewport_height>0&&
 typeof c.device_scale_factor==='number'&&c.device_scale_factor>0&&
 typeof c.network_profile==='string'&&c.network_profile.length>0&&
 c.cache_mode==='cold'&&typeof c.locale==='string'&&c.locale.length>0;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const median=vals=>{const v=vals.slice().sort((a,b)=>a-b),i=Math.floor(v.length/2);return v.length%2?v[i]:(v[i-1]+v[i])/2;};
function checkRun(run,expected,path,errors){
 if(!run||typeof run!=='object'){errors.push(path+': missing CDP run');return 0;}
 if(run.method!==SOURCE||run.all_inline_images_loaded!==true||run.all_image_requests_captured!==true||
   run.cache_disabled!==true||run.capture_unmodified!==true)errors.push(path+': invalid CDP provenance/coverage');
 if(!okConditions(run.conditions))errors.push(path+': invalid conditions');
 if(!Array.isArray(run.requests)){errors.push(path+': missing requests');return 0;}
 const ids=new Set(),slots=new Set();let bytes=0;
 run.requests.forEach((r,i)=>{
  const p=path+'.request['+i+']';
  if(!r||typeof r!=='object'){errors.push(p+': missing image request');return;}
  if(typeof r.request_id!=='string'||!r.request_id||ids.has(r.request_id))
    errors.push(p+': duplicate/missing request id');
  ids.add(r.request_id);
  if(!Array.isArray(r.slot_keys)||!r.slot_keys.length)errors.push(p+': no mapped slots');
  else for(const s of r.slot_keys){
   if(!expected.has(s)||slots.has(s))errors.push(p+': unknown/duplicate slot '+s);
   slots.add(s);
  }
  if(!url(r.request_url)||!url(r.final_url))errors.push(p+': invalid URL');
  if(r.http_status!==200&&r.http_status!==206)errors.push(p+': not successful image response');
  if(typeof r.mime_type!=='string'||!/^image\//i.test(r.mime_type))errors.push(p+': wrong MIME');
  if(!Number.isSafeInteger(r.encoded_data_length)||r.encoded_data_length<=0)errors.push(p+': unknown actual CDP wire bytes');
  else bytes+=r.encoded_data_length;
  if(r.decode_ok!==true||!Number.isInteger(r.natural_width)||r.natural_width<1||
    !Number.isInteger(r.natural_height)||r.natural_height<1)errors.push(p+': decode/dimensions missing');
  if(r.from_disk_cache!==false||r.from_memory_cache!==false||r.from_service_worker!==false||
    r.from_prefetch_cache!==false)errors.push(p+': cached/unknown transport');
  if(r.loading_finished!==true||r.terminal_response!==true||r.retry!==false)
    errors.push(p+': incomplete or retried request');
 });
 const missing=[...expected].filter(s=>!slots.has(s));
 if(missing.length)errors.push(path+': missing '+missing.length+' inline slots');
 return bytes;
}
function exactFrozenCensus(data,inventory){
 if(!inventory||inventory.schema_version!==1||inventory.inventory_id!==data.source_inventory_id||
    inventory.posts_count!==61||inventory.image_slot_count!==355||
    !Array.isArray(inventory.posts)||inventory.posts.length!==61)return false;
 const got=new Map(data.pairs.map(p=>[p.post_id,p]));
 if(got.size!==61)return false;
 for(const p of inventory.posts){
  const observed=got.get(p.post_id);
  if(!observed||observed.page_url!==p.page_url||
    !Array.isArray(observed.expected_slots)||
    observed.expected_slots.length!==p.expected_slots.length||
    !p.expected_slots.every(slot=>observed.expected_slots.includes(slot)))return false;
 }
 return true;
}
function evaluate(data,verifiedSourceInventory){
 const errors=[],base={status:'INSUFFICIENT_DATA',reason_codes:errors,
  observed_post_count:0,observed_slot_count:0,measured_reduction_percent:null,
  sitewide_76_percent_verified:false,can_claim_total_page_savings:false};
 if(!data||data.schema_version!==1||!Array.isArray(data.pairs)||!data.pairs.length){
  errors.push('no paired versioned evidence');return base;
 }
 if(typeof data.source_inventory_id!=='string'||!data.source_inventory_id.trim())
   errors.push('missing source inventory identity');
 const posts=new Set(),slots=new Set(),beforeTotals=[],afterTotals=[];
 let repeats=null;
 data.pairs.forEach((pair,n)=>{
  const p='pairs['+n+']';
  if(!pair||!Number.isInteger(pair.post_id)||pair.post_id<1||posts.has(pair.post_id)){
   errors.push(p+': missing/duplicate post');return;
  }
  posts.add(pair.post_id);
  const h=host(pair.page_url);
  if(h!=='finalvestige.com'&&!h.endsWith('.finalvestige.com'))errors.push(p+': non-FinalVestige page URL');
  if(!Array.isArray(pair.expected_slots)||!pair.expected_slots.length){
   errors.push(p+': missing expected slots');return;
  }
  const expected=new Set(pair.expected_slots);
  if(expected.size!==pair.expected_slots.length)errors.push(p+': duplicate expected slots');
  expected.forEach(s=>{
   if(typeof s!=='string'||!new RegExp('^'+pair.post_id+':\\d+$').test(s))errors.push(p+': invalid slot '+s);
   if(slots.has(s))errors.push(p+': repeated global slot '+s);slots.add(s);
  });
  if(!Array.isArray(pair.before)||!Array.isArray(pair.after)||!pair.before.length||
      pair.before.length!==pair.after.length){errors.push(p+': unpaired runs');return;}
  if(repeats===null)repeats=pair.before.length;
  if(repeats!==pair.before.length||repeats>10)errors.push(p+': inconsistent repetitions');
  pair.before.forEach((b,i)=>{
   const a=pair.after[i];
   const bb=checkRun(b,expected,p+'.before['+i+']',errors);
   const ab=checkRun(a,expected,p+'.after['+i+']',errors);
   if(b&&a&&(!same(b.conditions,a.conditions)||!same(b.conditions,pair.before[0]?.conditions)||
       !same(a.conditions,pair.after[0]?.conditions)))errors.push(p+': unequal browser conditions');
   beforeTotals[i]=(beforeTotals[i]||0)+bb;afterTotals[i]=(afterTotals[i]||0)+ab;
  });
 });
 base.observed_post_count=posts.size;base.observed_slot_count=slots.size;
 if(beforeTotals.some(x=>!Number.isSafeInteger(x)||x<1)||afterTotals.some(x=>!Number.isSafeInteger(x)||x<1))
   errors.push('bad aggregate transfer bytes');
 if(errors.length)return base;
 const reductions=beforeTotals.map((x,i)=>100*(x-afterTotals[i])/x);
 const pct=Number(median(reductions).toFixed(3));
 const wide=posts.size===61&&slots.size===355&&repeats>=3&&exactFrozenCensus(data,verifiedSourceInventory);
 return {status:wide?'SITEWIDE_IMAGE_TRANSFER_MEASURED':'LIMITED_SAMPLE_MEASURED',
   source_inventory_id:data.source_inventory_id,observed_post_count:posts.size,observed_slot_count:slots.size,
   repetitions:repeats,baseline_bytes_by_repeat:beforeTotals,candidate_bytes_by_repeat:afterTotals,
   reductions_percent_by_repeat:reductions.map(x=>Number(x.toFixed(3))),
   measured_reduction_percent:pct,sitewide_76_percent_verified:wide&&pct>=76,
   scope:'stored inline img slots only; not total page weight, CSS backgrounds, or visitor-weighted traffic',
   can_claim_total_page_savings:false,production_replacement_approved:false,reason_codes:[]};
}
module.exports={evaluate,SOURCE};
if(require.main===module){
 const fs=require('node:fs');
 if(!process.argv[2]){process.stderr.write('Usage: node evaluate_image_wire_20261103.cjs paired-cdp.json\n');process.exitCode=2;}
 else try{const inventory=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'wire_source_inventory_20261030.json'),'utf8'));
 const result=evaluate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')),inventory);
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
  if(result.status==='INSUFFICIENT_DATA')process.exitCode=1;
 }catch(e){process.stderr.write('Invalid input: '+e.message+'\n');process.exitCode=2;}
}

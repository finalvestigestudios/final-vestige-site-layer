'use strict';
// Offline, pure validation and calculation. No fetching, HTML writes, image copying, or WordPress access.
const P0 = ['285:5','285:2','287:5','418:1','418:2','407:1'];
const isUrl = s => typeof s === 'string' && /^https:\/\/[^/\s]+\/.+/i.test(s);
const px = a => Array.isArray(a) && a.length === 2 && a.every(n=>Number.isInteger(n) && n>0);
const uniq = a => new Set(a).size === a.length;
function inspectManifest(m) {
  const errors=[];
  const bad=(why)=>errors.push(why);
  if(!m||m.schema!=='fv-media-p0-evidence-acceptance-v1')bad('schema');
  if(!Array.isArray(m?.rows)||m.rows.length!==6)return {ok:false,errors:[...errors,'six_rows_required']};
  if(!uniq(m.rows.map(x=>x.slot))||P0.some(k=>!m.rows.some(x=>x.slot===k)))bad('p0_slots');
  if(m.legacy_42_broken!=='UNVERIFIED'||m.claimed_76pct_wire_savings!=='UNMEASURED')bad('unverified_claims');
  if(m.big_wordpress_originals?.stored_bytes!==43522829||m.big_wordpress_originals?.browser_bytes!==null)bad('storage_not_network');
  if(m.wordpress_writes!==0||m.image_downloads!==0||m.rights_approved!==0)bad('no_production_operations');
  for(const r of m.rows){
    if(!P0.includes(r.slot)||r.post_id!==Number(r.slot.split(':')[0])||!isUrl(r.page_url)||!isUrl(r.published_src))bad(r.slot+':source');
    if(!/^\d{4}-\d\d-\d\dT/.test(r.wp_modified||''))bad(r.slot+':wp_modified');
    if(r.browser_http_status!==null||r.visitor_broken!==null||r.visitor_current_src!==null||r.visitor_natural_px!==null||r.visitor_transfer_bytes!==null)bad(r.slot+':invented_browser_evidence');
    if(r.rights_clearance!=='HOLD'||r.production_action!=='HOLD'||!Array.isArray(r.candidates)||r.candidates.length<1)bad(r.slot+':release_hold');
    for(const q of r.candidates||[]){
      if(!isUrl(q.catalog_url)||!q.relationship||q.rights_review!=='HOLD'||q.rehosting_authorized!==false||q.binary_identity_verified!==false)bad(r.slot+':candidate_provenance');
      const a=q.master_px,b=q.conditional_preview_px;
      if((a===null)!==(b===null))bad(r.slot+':unproven_geometry');
      if(a!==null){
        if(!px(a)||!px(b)||b[0]>960||b[0]>a[0]||b[1]>a[1]||Math.abs(b[1]-Math.round(a[1]*b[0]/a[0]))>1)bad(r.slot+':unsafe_geometry');
      }
    }
  }
  return {ok:errors.length===0,errors};
}
function inspectGuestEvidence(m,capture){
  const mv=inspectManifest(m);
  if(!mv.ok)return {ok:false,errors:mv.errors,sitewide_weight_reduction_pct:null};
  if(capture==null)return {ok:true,state:'AWAITING_SITE_QA_GUEST_CDP',unverified_slots:P0,confirmed_broken_count:null,sitewide_weight_reduction_pct:null,page_pairs:[],errors:[]};
  const errors=[], observations=[], validRuns=[];
  const bad=s=>errors.push(s);
  if(capture.schema!=='fv-guest-cdp-image-capture-v1'||capture.capture_method!=='chromium-cdp'||capture.real_capture!==true||!Array.isArray(capture.runs))bad('capture_provenance');
  const runs=Array.isArray(capture.runs)?capture.runs:[];
  if(!uniq(runs.map(r=>r.id)))bad('duplicate_runs');
  const pageByUrl=new Map(m.rows.map(x=>[x.page_url,x.post_id]));
  for(const run of runs){
    const prefix=String(run.id||'unknown');
    if(!run.id||!['before','after'].includes(run.phase)||!pageByUrl.has(run.page_url)||typeof run.user_agent!=='string'||!run.user_agent||!run.browser_version||!run.network_profile)bad(prefix+':run_identity');
    const v=run.viewport;
    if(!v||!Number.isInteger(v.width)||!Number.isInteger(v.height)||v.width<=0||v.height<=0||!(v.dpr>0))bad(prefix+':viewport');
    if(run.cache_disabled!==true||run.full_scroll!==true||run.lazy_settled!==true||run.requests_complete!==true)bad(prefix+':cold_complete_gate');
    if(!Array.isArray(run.image_requests)||!Array.isArray(run.dom_images)||run.dom_image_count!==run.dom_images?.length)bad(prefix+':exhaustive_images');
    if(!Array.isArray(run.image_requests)||!Array.isArray(run.dom_images))continue;
    const reqById=new Map();
    for(const q of run.image_requests){
      if(!q.id||reqById.has(q.id)||q.resource_type!=='image'||!isUrl(q.url)||!Number.isInteger(q.encoded_bytes)||q.encoded_bytes<0||q.from_cache!==false||!Number.isInteger(q.http_status)||q.http_status<0||q.http_status>599||typeof q.mime!=='string'||(q.http_status===0&&!q.network_error))bad(prefix+':invalid_network_request');
      reqById.set(q.id,q);
    }
    const pageSlots=m.rows.filter(s=>s.page_url===run.page_url).map(s=>s.slot);
    for(const img of run.dom_images){
      if(!img.slot||typeof img.current_src!=='string'||!isUrl(img.current_src)||!Number.isInteger(img.natural_width)||!Number.isInteger(img.natural_height)||img.natural_width<0||img.natural_height<0||typeof img.complete!=='boolean'||typeof img.visible!=='boolean') {bad(prefix+':invalid_dom_image');continue;}
      const q=reqById.get(img.request_id);
      if(!q||!(q.url===img.current_src||q.final_url===img.current_src)){bad(prefix+':missing_matched_request');continue;}
      if(!pageSlots.includes(img.slot))continue; // Other DOM images are counted for whole-page weight but not P0 restoration.
      let status='INCONCLUSIVE';
      if(img.complete&&img.natural_width>0&&img.natural_height>0&&q.http_status>=200&&q.http_status<300&&q.mime.toLowerCase().startsWith('image/'))status='DECODED';
      else if(img.visible&&img.complete&&img.natural_width===0&&img.natural_height===0&&typeof img.screenshot_ref==='string'&&img.screenshot_ref.length>0&&(q.http_status>=400||q.http_status===0||!q.mime.toLowerCase().startsWith('image/')))status='BROWSER_FAILURE_CANDIDATE_REVIEW_SCREENSHOT';
      observations.push({run_id:prefix,phase:run.phase,slot:img.slot,current_src:img.current_src,origin_http_status:q.http_status,natural_px:[img.natural_width,img.natural_height],encoded_bytes:q.encoded_bytes,status,rights_release:false});
    }
    validRuns.push(run);
  }
  if(errors.length)return {ok:false,errors,confirmed_broken_count:null,sitewide_weight_reduction_pct:null};
  const pairs=[];
  for(const base of validRuns.filter(r=>r.phase==='before')){
    const compatible=validRuns.filter(r=>r.phase==='after'&&r.page_url===base.page_url&&JSON.stringify(r.viewport)===JSON.stringify(base.viewport)&&r.user_agent===base.user_agent&&r.browser_version===base.browser_version&&r.network_profile===base.network_profile);
    if(compatible.length!==1)continue;
    const after=compatible[0];
    const bytes=x=>x.image_requests.reduce((s,q)=>s+q.encoded_bytes,0);
    const old=bytes(base),now=bytes(after);
    if(!old)continue;
    pairs.push({page_url:base.page_url,viewport:base.viewport,before_run:base.id,after_run:after.id,baseline_image_encoded_bytes:old,after_image_encoded_bytes:now,sample_reduction_pct:Math.round((old-now)/old*10000)/100,sitewide_claim:false});
  }
  return {ok:true,state:'GUEST_CAPTURE_PROVIDED_REQUIRES_HUMAN_EVIDENCE_REVIEW',errors:[],observations,page_pairs:pairs,review_candidate_count:observations.filter(x=>x.status==='BROWSER_FAILURE_CANDIDATE_REVIEW_SCREENSHOT').length,confirmed_broken_count:null,sitewide_weight_reduction_pct:null,metric_note:'Image CDP encodedDataLength samples, not CMS original bytes; site-wide reduction requires a complete, identical pre/post published-article cohort. No rights clearance or publication inferred.',production_release_authorized:false};
}
module.exports={inspectManifest,inspectGuestEvidence};
if(require.main===module){
 const fs=require('node:fs');
 const m=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const c=process.argv[3]?JSON.parse(fs.readFileSync(process.argv[3],'utf8')):null;
 const result=inspectGuestEvidence(m,c);
 process.stdout.write(JSON.stringify(result,null,2)+'\n');
 if(!result.ok)process.exitCode=1;
}

'use strict';
/**
 * Offline 61/355 vs 66/361 image-slot cohort manifest validation.
 * Structural/provenance check ONLY: not a current-image crawl or measured
 * browser response, and never a 76% transfer-reduction certification.
 */
const fs=require('node:fs');
const path=require('node:path');
const validSha=x=>typeof x==='string' && /^[0-9a-f]{40}$/.test(x);
const sourceUrl=s=>{try{const u=new URL(s);return u.protocol==='https:' && !!u.hostname;}catch{return false}};
function validateManifest(m){
 const errors=[],check=(b,s)=>{if(!b)errors.push(s)};
 if(!m||typeof m!=='object'||Array.isArray(m))return {ok:false,errors:['missing_manifest']};
 check(m.schema==='fv-sitewide-wire-cohort-manifest-v1','wrong_schema');
 check(m.data_cohorts_not_interchangeable===true,'cohorts_not_distinct');
 check(m.requires_guest_chrome_and_raw_cdp_before_after===true,'browser_evidence_claim');
 check(m.rights_and_post_edits_authorized===false,'unauthorized_publication');
 check(Array.isArray(m.provenance)&&m.provenance.length===9,'provenance_count');
 const expectedPaths=[...Array.from({length:8},(_,i)=>'qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json'),
   'qa/media-recovery/new_five_posts_six_commons_20261107.json'];
 for(let i=0;i<9;i++)check(m.provenance?.[i]?.path===expectedPaths[i]&&validSha(m.provenance?.[i]?.git_blob_sha),'source_blob_'+i);
 check(m.legacy?.id==='61-post-20261030'&&m.legacy?.expected_posts===61&&m.legacy?.expected_slots===355,'legacy_header');
 check(m.expanded?.id==='66-post-20261107-mixed-sources'&&m.expanded?.expected_posts===66&&m.expanded?.expected_slots===361,'expanded_header');
 if(!Array.isArray(m.rows))return {ok:false,errors:[...errors,'missing_rows']};
 const all=new Map(),hist=new Set(m.legacy?.post_ids||[]), expanded=m.expanded?.post_ids||[];
 check(m.rows.length===66,'row_count');
 check(hist.size===61&&(m.legacy?.post_ids||[]).length===61,'legacy_ids');
 check(Array.isArray(expanded)&&expanded.length===66&&new Set(expanded).size===66,'expanded_ids');
 const added=[1917,1920,1922,1924,1926],counts={1917:2,1920:2,1922:0,1924:1,1926:1};
 const newSet=new Set(added);
 let slots=0,oldSlots=0;
 for(const r of m.rows){
  const id=r?.id;
  if(!Number.isSafeInteger(id)||id<=0||all.has(id)){check(false,'duplicate_or_invalid_post_'+id);continue;}
  all.set(id,r);
  check(typeof r.capture_date==='string'&&r.capture_date===(newSet.has(id)?'2026-11-07':'2026-10-30'),'source_date_'+id);
  check(newSet.has(id)?r.post_url===null:sourceUrl(r.post_url)&&new URL(r.post_url).hostname==='finalvestige.com','post_url_'+id);
  if(!Array.isArray(r.slots)){check(false,'missing_slots_'+id);continue;}
  if(newSet.has(id))check(r.slots.length===counts[id],'new_post_slots_'+id);
  else check(r.slots.length>0,'older_post_unexpected_zero_'+id);
  for(let j=0;j<r.slots.length;j++){
    const s=r.slots[j];
    check(s?.key===id+':'+j&&sourceUrl(s.source_url),'slot_identity_or_source_'+id+':'+j);
  }
  slots+=r.slots.length;
  if(hist.has(id))oldSlots+=r.slots.length;
 }
 check([...all.keys()].every(id=>expanded.includes(id)),'expanded_post_missing');
 check(expanded.every(id=>all.has(id)),'expanded_post_not_covered');
 check([...hist].every(id=>all.has(id)&&!newSet.has(id)),'legacy_post_not_covered');
 check(expanded.filter(id=>!hist.has(id)).sort((a,b)=>a-b).join(',')===added.join(','),'cohort_delta_post_ids');
 check(slots===361&&oldSlots===355,'slot_totals');
 check(all.get(1922)?.slots?.length===0,'zero_image_post_absent');
 return {ok:errors.length===0,errors,metrics:{old_posts:hist.size,old_slots:oldSlots,expanded_posts:all.size,expanded_slots:slots,delta_posts:expanded.length-hist.size,delta_slots:slots-oldSlots,zero_inline_image_post_id:1922},not_guest_browser_verified:true,not_a_76_percent_measurement:true,wordpress_write_authorized:false};
}
function loadManifest(){return JSON.parse(fs.readFileSync(path.join(__dirname,'sitewide_wire_cohort_manifest_20261107.json'),'utf8'));}
if(require.main===module){try{const r=validateManifest(loadManifest());console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}catch(e){console.error('AUDIT_INPUT_ERROR '+String(e.message||e));process.exitCode=2;}}
module.exports={validateManifest,loadManifest};

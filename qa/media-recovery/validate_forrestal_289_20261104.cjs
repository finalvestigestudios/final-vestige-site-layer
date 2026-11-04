'use strict';
/** Offline fail-closed provenance validator. Does NOT perform HTTP or permit publication. */
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED = {
  '289:0':['upload.wikimedia.org','USS_Forrestal_A-4_Skyhawk_burning.png'],
  '289:1':['specials-images.forbesimg.com','USN 1126565'],
  '289:2':['k.sinaimg.cn','USN 1124808'],
  '289:3':['k-static.appmobile.cn','USN 1126644'],
  '289:4':['media.defense.gov','210811-N-SG189-1105'],
  '289:5':['d1ldvf68ux039x.cloudfront.net','130726-N-ST310-007'],
};
const OUTCOMES=new Set(['displayed_by_independent_image_retriever','retriever_wrapper_403_not_origin_status']);
function validate(data,part){
  const e=[],bad=(s)=>e.push(s);
  const records=data?.records,images=part?.images?.filter(x=>x.post_id===289);
  if(data?.schema_version!==1||data?.post?.id!==289||data?.publication_state!=='HOLD')bad('schema/post/HOLD');
  if(data?.frozen_source_inventory?.blob_sha!=='49183f66f880f7c4dfd363acca906876877f2e5e')bad('snapshot blob');
  if(data?.frozen_source_inventory?.fresh_wordpress_read_this_sprint!==false)bad('unverified WP read');
  if(!Array.isArray(records)||records.length!==6||!Array.isArray(images)||images.length!==6)return [...e,'six records and six frozen images required'];
  if(new Set(records.map(x=>x.image_key)).size!==6)bad('duplicate/missing image key');
  let displayed=0,blocked=0;
  for(let i=0;i<6;i++){
    const a=records.find(r=>r.image_key==='289:'+i),b=images.find(x=>x.key==='289:'+i);
    if(!a||!b){bad('slot missing '+i);continue}
    if(a.post_id!==289||a.slot!==i||a.original_source_url!==b.source_url||a.original_alt!==b.alt||a.frozen_snapshot_original_http_status!==null)bad('immutable slot '+i);
    let u;try{u=new URL(a.original_source_url)}catch{bad('bad source URL '+i);continue}
    if(u.hostname!==EXPECTED[a.image_key][0]||u.protocol!=='https:')bad('wrong source origin '+i);
    const o=a.source_observation,c=a.candidate;
    if(o?.observed_url!==b.source_url||o.method!=='independent_web_image_retriever'||o.observed_date!=='2026-11-04'||!OUTCOMES.has(o.tool_outcome))bad('unverified observation '+i);
    if(o?.origin_http_status!==null||o?.guest_browser_http_status!==null||o?.guest_browser_current_src!==null||o?.guest_browser_decode!==null||o?.guest_browser_natural_width!==null||o?.cold_cdp_transfer_bytes!==null)bad('fabricated browser or origin evidence '+i);
    if(o.tool_outcome==='displayed_by_independent_image_retriever')displayed++;else blocked++;
    if(!c||c.catalog_identifier!==EXPECTED[a.image_key][1])bad('catalog identity '+i);
    if(!c||typeof c.record_url!=='string'||!/^https:\/\/(www\.history\.navy\.mil|www\.dvidshub\.net|commons\.wikimedia\.org)\//.test(c.record_url))bad('catalog host '+i);
    if(!c||c.geometry_basis!=='catalog_metadata_only_not_binary_decode'||!Number.isSafeInteger(c.catalog_master_width_px)||c.catalog_master_width_px<1||!Number.isSafeInteger(c.catalog_master_height_px)||c.catalog_master_height_px<1)bad('catalog dimensions '+i);
    const width=Math.min(960,c.catalog_master_width_px),height=Math.round(c.catalog_master_height_px*width/c.catalog_master_width_px);
    if(c.max_output_width_px!==960||c.conditional_max_derived_width_px!==width||c.conditional_max_derived_height_px!==height||c.no_upscale!==true)bad('incorrect no-upscale geometry '+i);
    if(c.rights_status!=='HOLD'||c.rights_cleared!==false||c.local_cache_authorized!==false||c.wp_media_upload_authorized!==false||c.post_block_rewrite_authorized!==false)bad('unsupported rights/publication approval '+i);
    if(i>=1&&i<=3&&!c.identity_class?.startsWith('different_'))bad('third-party alternative overclaims exact photo '+i);
    if(i===4&&c.identity_class!=='exact_virin_matches_original_url_binary_unhashed')bad('VIRIN match overstated '+i);
    if(i===5&&c.identity_class!=='same_dvids_photo_id_in_source_url_binary_unhashed')bad('DVIDS photo hash overstated '+i);
    if((i===4||i===5)&&!a.editorial_note?.includes(i===4?'2021':'2013'))bad('training/memorial chronology '+i);
  }
  if(displayed!==5||blocked!==1||records[4]?.source_observation?.tool_outcome!=='retriever_wrapper_403_not_origin_status')bad('retriever tally');
  const s=data?.observed_summary;
  if(s?.independently_displayed!==5||s?.retriever_wrapper_403!==1||s?.confirmed_guest_browser_broken!==0||s?.guest_browser_verified!==0||s?.measured_weight_reduction_percent!==null)bad('unsupported summary claim');
  const g=data?.constraints;
  if(g?.max_derivative_width_px!==960||g?.never_upscale!==true||g?.browser_evidence_required_before_replacement!==true||g?.item_rights_required_before_download_or_republication!==true||g?.cache_or_wp_write_authorized!==false||g?.additional_spend_authorized!==false)bad('release gate');
  return e;
}
if(require.main===module){
  const root=path.join(__dirname);
  const a=JSON.parse(fs.readFileSync(path.join(root,'forrestal_289_nhhc_dvids_20261104.json'),'utf8'));
  const b=JSON.parse(fs.readFileSync(path.join(root,'parts','03.json'),'utf8'));
  const errors=validate(a,b);
  console.log(JSON.stringify({ok:errors.length===0,errors,image_count:a.records?.length||null,guest_http_verified:false},null,2));
  if(errors.length)process.exitCode=1;
}
module.exports={validate};

'use strict';
/** Read-only USS Tang follow-up: exact snapshot + archival custody + fail-closed browser/rights gates. */
const snapshot=require('./parts/04.json');
const expectedIds=["NH 42273","80-G-227987","NH 84498","NH 45641","80-G-344565","80-G-227991","80-G-227989"];
const allowedRetrieval=["independent_image_viewer_displayed","web_retriever_inaccessible_no_origin_status","web_retriever_inaccessible_no_origin_status","web_retriever_inaccessible_no_origin_status","web_retriever_inaccessible_no_origin_status","independent_image_viewer_displayed","web_retriever_inaccessible_no_origin_status"];
function validate(x) {
 const errors=[],add=x=>errors.push(x);
 if(!x||typeof x!=='object'||Array.isArray(x))return ['invalid_object'];
 if(x.schema!=='fv.media-recovery.tang274.v1'||x.post_id!==274||x.total_source_slots!==7||
 x.nhhc_catalog_mapped_slots!==7||x.snapshot_blob_sha!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96')add('wrong_census_or_blob');
 if(x.fresh_production_post_read!==false||x.production_write_authorized!==false||
 x.confirmed_guest_browser_broken_count!==null||x.sitewide_42_image_claim_verified!==false||
 x.weight_reduction_76_percent_measured!==false||x.production_media_repaired!==0)add('unverified_claim');
 if(!Array.isArray(x.records)||x.records.length!==7)return [...new Set([...errors,'wrong_row_count'])];
 const originals=snapshot.images.filter(s=>s.post_id===274).sort((a,b)=>a.slot-b.slot);
 const seen=new Set();
 for(let i=0;i<7;i++){
  const r=x.records[i],s=originals[i],cat=r?.authority,e=r?.independent_source_retrieval,d=r?.transform,rights=r?.rights,release=r?.release;
  if(!s||!r||seen.has(r.key)||r.key!==s.key||r.published_source_url!==s.source_url||
   r.published_alt!==s.alt||r.source_snapshot_blob_sha!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96')add('source_url_or_alt_'+i);
  if(r)seen.add(r.key);
  if(!cat||cat.archive!=='Naval History and Heritage Command'||cat.catalog_id!==expectedIds[i]||
   !cat.catalog_url?.startsWith('https://www.history.navy.mil/')||
   !Number.isSafeInteger(cat.official_catalog_master_dimensions_px?.width)||
   !Number.isSafeInteger(cat.official_catalog_master_dimensions_px?.height)||
   cat.official_catalog_master_dimensions_px.width<1||cat.official_catalog_master_dimensions_px.height<1)add('catalog_'+i);
  if(!e||e.method!=='web_image_renderer_2026-11-02'||e.result!==allowedRetrieval[i]||
   e.origin_http_status!==null||e.guest_browser_status!==null||
   e.decoded_pixels!==null||e.transfer_bytes!==null)add('invented_http_or_pixels_'+i);
  if(!rights||rights.review_status!=='HOLD_ITEM_SPECIFIC'||rights.wp_rehost_authorized!==false||
   rights.download_authorized!==false)add('rights_'+i);
  if(!d||d.max_width_px!==960||d.no_upscale!==true||d.actual_source_dimensions_verified!==false||
   d.derivative_height_px!==null||d.original_binary_sha256!==null)add('hypothetical_derivative_'+i);
  if(!release||Object.values(release).length!==6||Object.values(release).some(v=>v!==false))add('early_release_'+i);
 }
 for(const [i,w,h] of [[0,5019,3070],[5,5670,4150],[6,1910,1288]]){
 const c=x.records[i]?.authority,z=i===6?c?.commons_scene_copy_px:c?.commons_current_original_px;
 const m=c?.official_catalog_master_dimensions_px;
 if(!z||z.width!==w||z.height!==h||!m||Math.abs(m.width/m.height-w/h)<0.03)add('frame_conflict_'+i);
 }
 return [...new Set(errors)];
}
module.exports={validate};
if(require.main===module) {
 const errs=validate(require('./tang_274_nhhc_20261102.json'));
 if(errs.length){console.error(errs);process.exitCode=1}else console.log('TANG274_CROP_RIGHTS_CHECK_PASS');
}

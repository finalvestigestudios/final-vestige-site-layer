'use strict';
// Offline-only, read-only verification of a PINNED observation. No HTTP, image bytes, WordPress writes or deployment.
const EXPECTED = ['S67-15717','S66-58038','KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090'];
const COMMONS = {
  'KSC-20170124-PH_KLS01_0164':{w:6720,h:4480,hh:640},
  'KSC-20170124-PH_KLS01_0090':{w:4480,h:6720,hh:1440}
};
const ERR = (errors, condition, code) => { if (!condition) errors.push(code); };
function assess(m) {
  const errors=[];
  ERR(errors,m?.schema==='fv-media-apollo1-five-slot-source-custody-v1','schema');
  ERR(errors,m?.post_id===434&&m?.post_modified==='2026-11-15T12:58:22','wordpress_source_revision');
  ERR(errors,m?.post_url==='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/','post_url');
  ERR(errors,m?.browser_observation==='INDEPENDENT_WEB_IMAGE_READER_NOT_COLD_VISITOR_BROWSER','method');
  ERR(errors,m?.historical_census?.posts===61&&m?.historical_census?.images===355&&m?.historical_census?.qa_offsite===286&&m?.historical_census?.media_offsite===288&&m?.historical_census?.source_only===true,'cohort');
  ERR(errors,m?.reported_broken_42_guest_confirmed===false&&m?.claimed_76_percent_wire_savings_measured===false,'unproven_claim');
  ERR(errors,m?.large_wp_originals?.count===20&&m?.large_wp_originals?.stored_bytes===64385752&&m?.large_wp_originals?.measured_wire_bytes===null,'stored_not_wire');
  ERR(errors,m?.production_writes===0&&m?.downloads===0&&m?.source_replacements===0&&m?.paid_actions===0,'no_side_effects');
  ERR(errors,typeof m?.release_gate==='string'&&m.release_gate.startsWith('DO_NOT_REPLACE:'),'release_hold');
  ERR(errors,Array.isArray(m?.image_rows)&&m.image_rows.length===5,'five_nasa_slots');
  for(let i=0;i<EXPECTED.length;i++){
    const id=EXPECTED[i],r=m?.image_rows?.[i],g=COMMONS[id];
    if(!r){errors.push('missing_row_'+i);continue;}
    ERR(errors,r.slot==='434:'+(i+1)&&r.accession===id,'slot_accession_'+i);
    ERR(errors,r.original_edit_src===`https://images-assets.nasa.gov/image/${id}/${id}~large.jpg`,'original_exact_'+i);
    ERR(errors,r.rendered_view_src===`https://i0.wp.com/images-assets.nasa.gov/image/${id}/${id}~large.jpg?ssl=1`,'proxy_exact_'+i);
    ERR(errors,r.agency_catalog_url===`https://images.nasa.gov/details/${id}`,'catalog_exact_'+i);
    ERR(errors,r.independent_original_reader===(i===0?'IMAGE_RENDERED':'TOOL_INACCESSIBLE')&&r.independent_proxy_reader==='TOOL_INACCESSIBLE','reader_semantics_'+i);
    ERR(errors,r.original_http_get_status===null&&r.proxy_http_get_status===null&&r.guest_http_get_status===null&&r.guest_current_src===null&&r.guest_image_decoded===null&&r.guest_transfer_bytes===null,'not_guest_or_http_'+i);
    ERR(errors,r.item_rights==='HOLD_ITEM_LEVEL_CHECK'&&r.rights_policy_url==='https://www.nasa.gov/nasa-brand-center/images-and-media/','copyright_hold_'+i);
    ERR(errors,r.source_binary_sha256===null&&r.source_binary_dimensions_px===null,'binary_unverified_'+i);
    ERR(errors,r.max_derivative_width_px===960&&r.upscaling_allowed===false&&r.same_pixels_crop_verified===false&&r.wp_cached===false&&r.wp_upload_authorized===false,'resize_and_cache_hold_'+i);
    ERR(errors,r.catalog_dimension_source===(g?'WIKIMEDIA_COMMONS_NASA_ACCESSION_CROSSREFERENCE':'UNKNOWN'),'catalog_source_'+i);
    ERR(errors,JSON.stringify(r.catalog_dimensions_px)===(g?JSON.stringify({width:g.w,height:g.h}):'null'),'catalog_geometry_'+i);
    ERR(errors,JSON.stringify(r.conditional_960px_geometry)===(g?JSON.stringify({width:960,height:g.hh}):'null'),'derivative_geometry_'+i);
    ERR(errors,r.source_evidence===(g?'NASA_ACCESSION_WITH_COMMONS_CROSSREFERENCE':'NASA_APOLLO_1_GALLERY'),'provenance_'+i);
    ERR(errors,r.support_record_url===(id==='KSC-20170124-PH_KLS01_0164'?'https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG':id==='KSC-20170124-PH_KLS01_0090'?'https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_Block_II_hatch.JPG':'https://www.nasa.gov/gallery/apollo-1/'),'support_record_'+i);
  }
  return {ok:errors.length===0,decision:'HOLD_BROWSER_RIGHTS_FRAME',errors};
}
module.exports={assess};
if(require.main===module){
  const fs=require('node:fs');
  const path=require('node:path');
  try{
    const file=process.argv[2]||path.join(__dirname,'apollo1_nasa_five_slot_custody_20261116.json');
    if(fs.statSync(file).size>1024*1024)throw Error('audit exceeds 1 MiB');
    const r=assess(JSON.parse(fs.readFileSync(file,'utf8')));
    console.log(JSON.stringify(r,null,2));
    if(!r.ok)process.exitCode=2;
  }catch(e){console.error('MEDIA_APOLLO1_HOLD: '+e.message);process.exitCode=2;}
}

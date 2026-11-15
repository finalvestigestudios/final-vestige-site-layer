'use strict';
const EXPECTED_IDS=[1257,1258,1259,1260,1261,1262];
const EXACT_NAMES=[
'edit-017-v01-malbone-tunnel-generalpunger-original.jpg',
'edit-017-v02-nypl-5003296-original.jpg',
'edit-017-v03r2-six-mph-curve-responsive.png',
'edit-017-v04r2-five-car-consist-responsive.png',
'edit-017-v05r2-rescue-power-sequence-responsive.png',
'edit-017-v06r2-evidence-not-blame-responsive.png'];
function auditErrors(d){
  const err=[];
  if(d?.schema!=='fv.media_recovery.malbone_621.v1')err.push('schema');
  if(d?.article!=='https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/')err.push('article');
  if(d?.release_state!=='HOLD_FOR_COLD_BROWSER_AND_EDITORIAL_RIGHTS_AND_LEGIBILITY')err.push('release_state');
  if(!Array.isArray(d?.images)||d.images.length!==6)return err.concat('row_count');
  let total=0,large=0,big=0;const seen=new Set();
  for(let i=0;i<6;i++){
    const x=d.images[i],m=x?.wordpress_media||{},p=x?.plan||{},o=x?.observations||{},g=x?.stored_gutenberg||{};
    if(x?.media_id!==EXPECTED_IDS[i]||x?.slot!=='621:'+i||x?.post_id!==621||seen.has(x?.media_id))err.push('identity:'+i);
    seen.add(x?.media_id);
    if(x?.source_url!=='https://finalvestige.com/wp-content/uploads/2026/08/'+EXACT_NAMES[i])err.push('source:'+i);
    if(!Number.isInteger(m.original_width)||m.original_width<=0||!Number.isInteger(m.original_height)||m.original_height<=0||!Number.isInteger(m.stored_original_bytes)||m.stored_original_bytes<=0)err.push('media_geometry:'+i);
    const width=Math.min(960,m.original_width),height=Math.round(width*m.original_height/m.original_width);
    if(p.max_width!==width||p.max_height!==height||p.resizing_kind!=='CONDITIONAL_NO_UPSCALE')err.push('resize:'+i);
    if(i===1&&!p.legibility_review_required)err.push('map_legibility_gate');
    if(p.rights_review_required!==true||typeof p.credit_note!=='string'||p.credit_note.length<24||typeof p.rights_note!=='string'||p.rights_note.length<15)err.push('rights:'+i);
    if(p.approved_for_cache!==false||p.approved_for_upload!==false||p.approved_for_publication!==false)err.push('unsafe_release:'+i);
    if(g.size_slug!=='large'||g.img_src_original!==true||g.img_width_attribute!==null||g.img_height_attribute!==null||g.img_srcset_attribute!==null||g.img_sizes_attribute!==null)err.push('source_markup:'+i);
    if(m.virtual_large_advertised!==true||typeof m.virtual_large_url!=='string'||!m.virtual_large_url.startsWith('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/'+EXACT_NAMES[i]+'?fit=1024%2C'))err.push('virtual_rendition:'+i);
    if(o.live_cms_source_present!==true||o.origin_http_status!==null||o.guest_browser_status!==null||o.browser_current_src!==null||o.wire_bytes!==null||o.rendered_intrinsic_width!==null||o.rendered_intrinsic_height!==null)err.push('unverified_status:'+i);
    total+=m.stored_original_bytes;if(m.stored_original_bytes>1500000){big++;large+=m.stored_original_bytes}
  }
  const s=d.summary||{};
  if(s.images!==6||s.original_stored_bytes!==total||s.over_decimal_1_5_MB_count!==big||s.over_decimal_1_5_MB_bytes!==large||Math.abs(s.over_decimal_1_5_MB_percent_of_six_original_bytes-100*large/total)>0.0001)err.push('aggregate');
  if(s.markup_width_height_srcset_six_missing!==6||s.virtual_large_six_advertised!==6||s.unverified_broken_total!==null||s.verified_visitor_transfer_reduction_pct!==null)err.push('unsupported_performance_claim');
  const b=d.site_baselines||{};
  if(b.broken_external_reported!==42||b.broken_external_guest_verified!==null||b.proposed_weight_reduction_percent!==76||b.weight_reduction_wire_measured!==null)err.push('historical_unverified_baseline');
  if(!Array.isArray(d.required_checks)||d.required_checks.length<4)err.push('stage_requirements');
  return err;
}
module.exports={auditErrors};
if(require.main===module){const d=require('./malbone_621_six_image_rendition_audit_20261114.json');const e=auditErrors(d);console.log(JSON.stringify({pass:e.length===0,errors:e}));if(e.length)process.exitCode=1;}

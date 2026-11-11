'use strict';
// Standalone, offline, read-only decision gate. No network, downloads, WordPress or production modifications.
const frozen=Object.freeze({
'621:0':Object.freeze({url:'https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg',id:1257,bytes:4798395,native:[4000,3000],thumb:[960,720],kind:'PHOTOGRAPH'}),
'621:1':Object.freeze({url:'https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg',id:1258,bytes:5553669,native:[5667,3831],thumb:[960,649],kind:'FINE_DETAIL_MAP'})
});
const validHttps=u=>{try{const p=new URL(u);return p.protocol==='https:'&&!!p.hostname&&!p.username&&!p.password}catch{return false}};
function audit(x){
const reasons=[];if(!x||!Array.isArray(x.rows)||x.rows.length!==2)return {state:'HOLD',reasons:['exactly_two_rows']};
if(new Set(x.rows.map(r=>r.slot)).size!==2)reasons.push('duplicate_slot');
let sum=0;
for(const r of x.rows){
 const c=frozen[r.slot];if(!c){reasons.push('unknown_slot');continue}
 if(r.post_id!==621||r.wp_media_id!==c.id||r.original_url!==c.url)reasons.push(r.slot+':source_identity');
 if(r.stored_bytes!==c.bytes)reasons.push(r.slot+':stored_bytes');
 if(JSON.stringify(r.original_native_px)!==JSON.stringify(c.native)||JSON.stringify(r.conditional_960_px)!==JSON.stringify(c.thumb))reasons.push(r.slot+':geometry');
 if(r.kind!==c.kind)reasons.push(r.slot+':visual_role');
 if(r.rights_cleared!==false||r.production_write_approved!==false)reasons.push(r.slot+':rights_or_publication_self_approval');
 if(r.guest_current_src!==null||r.guest_wire_bytes!==null||r.retriever?.origin_http_status!==null||r.retriever?.guest_browser_http_status!==null)reasons.push(r.slot+':unverified_http_or_browser_claim');
 if(r.slot==='621:0'&&(!/GeneralPunger/.test(r.published_caption_credit||'')||!/CC BY-SA 4.0/.test(r.published_caption_credit||'')||r.catalog_item_identity_proven!==false))reasons.push(r.slot+':license_provenance');
 if(r.slot==='621:1'&&(!/1903/.test(r.visual_role||'')||!/not 1918/.test(r.visual_role||'')||r.catalog_image_id!=='5003296'||r.catalog_url!=='https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0'))reasons.push(r.slot+':historical_map_provenance');
 sum+=r.stored_bytes;
}
if(sum!==10352064||x.original_stored_bytes_total!==sum)reasons.push('stored_total');
if(x.measured_browser_http_statuses!==null||x.measured_browser_transfer_bytes!==null||x.measured_sitewide_transfer_reduction_pct!==null)reasons.push('fabricated_measurement');
if(x.safeguards?.require_same_map_accessible_full_detail!==true||x.safeguards?.map_960_only_thumbnail!==true||x.safeguards?.wp_writes!==false||x.safeguards?.binary_download!==false||x.safeguards?.sitewide_savings_claim!==false)reasons.push('unsafe_policy');
return {state:reasons.length?'HOLD':'RECORD_VERIFIED_NOT_PUBLISHABLE',reasons,original_stored_bytes:sum};
}
function proposal(slot,p){
 const c=frozen[slot];if(!c)return {state:'HOLD',reason:'UNKNOWN_SLOT'};
 if(!p||p.source_url!==c.url||p.original_bytes!==c.bytes)return {state:'HOLD',reason:'CHANGED_SOURCE'};
 const d=p.output_px;
 if(!Array.isArray(d)||d.length!==2||d.some(v=>!Number.isInteger(v)||v<1)||d[0]>960||d[0]>c.native[0]||d[1]>c.native[1]||Math.abs((d[0]/d[1])/(c.native[0]/c.native[1])-1)>0.003)return {state:'HOLD',reason:'BAD_GEOMETRY'};
 if(p.production_write===true||p.browser_success_claim===true||p.percent_savings_claim!==undefined||p.replaced_subject===true)return {state:'HOLD',reason:'UNSUPPORTED_ACTION_OR_CLAIM'};
 if(p.editor_visual_review!==true||p.editor_rights_review!==true||!validHttps(p.credit_link))return {state:'HOLD',reason:'EDITORIAL_RIGHTS'};
 if(slot==='621:0'&&(p.author!=='GeneralPunger'||p.license!=='CC-BY-SA-4.0'||p.license_url!=='https://creativecommons.org/licenses/by-sa/4.0/'||p.catalog_photo_identity_verified!==true||p.edit_notice_recorded!==true))return {state:'HOLD',reason:'PHOTO_ATTRIBUTION'};
 if(slot==='621:1'&&(p.map_date!==1903||p.asserts_1918_curve===true||p.nypl_catalog_url!=='https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0'||p.same_map_full_detail_verified!==true||!validHttps(p.full_detail_url)||p.full_detail_width<5667||p.full_detail_height<3831||p.full_detail_guest_accessible!==true))return {state:'HOLD',reason:'MAP_CONTEXT_OR_LEGIBILITY'};
 return {state:'ISOLATED_STAGING_CANDIDATE_ONLY',reason:'EDITOR_APPROVAL_NOT_PRODUCTION_PERMISSION'};
}
module.exports={frozen,audit,proposal};

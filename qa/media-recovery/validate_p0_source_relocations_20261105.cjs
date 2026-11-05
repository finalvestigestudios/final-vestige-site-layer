'use strict';
const expected=[
 ['287:5',287,'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg','https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg',404,'1980-05-09',null],
 ['418:2',418,'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg','https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg',403,'1946-04-01',[600,463]]
];
function die(why){throw Error(why)}
function eql(a,b){return JSON.stringify(a)===JSON.stringify(b)}
function validate(d){
 if(d?.schema!=='fv-two-p0-publisher-relocations-v1'||d.audit_date!=='2026-11-05')die('schema');
 if(!eql(d.frozen_inventory_git_blobs,['49183f66f880f7c4dfd363acca906876877f2e5e','948bc1b65b42799aa40cfdb810ddf6ffd80886b6']))die('snapshot_blob');
 const b=d.sitewide_baseline;
 if(!b||b.posts!==61||b.image_references!==355||b.external_origin_references!==288||b.oversized_wordpress_originals!==13||
 b.oversized_stored_bytes!==43522829||b.alleged_broken_42!=='UNVERIFIED'||b.claimed_weight_reduction_76!=='UNMEASURED'||
 d.completed_site_repairs!==0||d.measured_wire_savings_pct!==null)die('fabricated_sitewide_measurement');
 if(!Array.isArray(d.rows)||d.rows.length!==2)die('row_count');
 for(let i=0;i<2;i++){
 const r=d.rows[i],e=expected[i];
 if(!r||!eql([r.key,r.post_id,r.published_original,r.proposed_source,r.wrapper_error,r.historical_event_date,r.catalog_dimensions_px],e))die('url_date_geometry_or_key');
 if(!eql(r.proposed_derivative_dimensions_px,e[6])||r.max_width_px!==960||r.no_upscale!==true)die('unsafe_derivative');
 for(const k of ['published_original','proposed_source','parent_catalog','article_url']){
  if(typeof r[k]!=='string'||!r[k].startsWith('https://')||r[k].includes(' '))die('invalid_url_'+k);
 }
 if(r.source_error_is_origin_http!==false||r.source_error_is_guest_http!==false||
 r.candidate_origin_http_status!==null||r.candidate_guest_http_status!==null||
 r.guest_broken!==null||r.guest_transfer_bytes!==null)die('unverified_browser_status');
 if(r.candidate_original_binary_sha256!==null||r.pixel_identity_verified!==false||
 r.rights_review_complete!==false||!r.rights.startsWith('HOLD_'))die('unverified_rights_or_binary_identity');
 if(r.caching_authorized!==false||r.external_hotlink_permission_verified!==false||
 r.wordpress_upload_authorized!==false||r.wordpress_post_edit_authorized!==false||r.production_repair!==false)die('production_write_or_cache');
 if(typeof r.published_alt!=='string'||typeof r.visual_integrity_issue!=='string'||!r.visual_integrity_issue.trim()||
 typeof r.publisher_credit!=='string'||!r.publisher_credit.trim()||!r.evidence.includes('IMAGE_RENDERED_IN_WEB_RETRIEVER'))die('provenance');
 if(i===0&&!r.visual_integrity_issue.includes('later replacement bridge'))die('skyway_alt_caveat');
 if(i===1&&!r.visual_integrity_issue.includes('1964'))die('scotch_date_caveat');
 }
 return {status:'SOURCE_RELOCATION_LEADS_VALIDATED',rows:2,visitor_failures_confirmed:0,media_changes:0,release:'HOLD'};
}
module.exports={validate};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');
 console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))),null,2));
}

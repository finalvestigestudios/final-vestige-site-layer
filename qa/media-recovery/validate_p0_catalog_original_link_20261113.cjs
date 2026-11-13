'use strict';
/**
 * Offline P0 official-catalog source provenance guard. Never infers visitor
 * status from the web retriever, invents native pixels, or approves caching.
 */
const {P0}=require('./p0_guest_evidence_release_gate_20261112.cjs');
const ORDER=['285:5','285:2','287:5','418:1','418:2','407:1'];
const WRAPPERS=[[404,'NOT_FOUND_WRAPPER'],[500,'INACCESSIBLE_MIGRATED_REDIRECT_WRAPPER'],
 [404,'NOT_FOUND_WRAPPER'],[403,'FORBIDDEN_WRAPPER'],[403,'FORBIDDEN_WRAPPER'],
 [400,'UNSUPPORTED_OCTET_STREAM_WRAPPER']];
const SECONDARY_418='https://www.lighthousefriends.com/light.asp?ID=1780';
const ORIGINAL_USGS='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg';
const MEDIUM_USGS='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/medium/public/img7535.jpg?itok=q8Hes32z';
function audit(doc){
 const errors=[],check=(v,label)=>{if(!v)errors.push(label);};
 check(doc?.schema==='fv-p0-catalog-original-link-custody-v1','schema');
 check(doc?.checked_utc_date==='2026-11-13','date');
 check(doc?.source_inventory==='61_posts_355_stored_image_slots_frozen','frozen_inventory');
 check(doc?.reported_broken_originals_unconfirmed===42,'broken_unconfirmed');
 check(doc?.proposed_transfer_reduction_76pct_measured===false,'76pct_not_measured');
 check(doc?.oversized_wordpress_originals_decimal_mb===15&&doc?.oversized_original_stored_bytes===47096779,'stored_original_bytes');
 check(doc?.method==='WEB_RETRIEVER_AND_OFFICIAL_PUBLISHER_CATALOG_LINK_INSPECTION_NOT_GUEST_CDP','method');
 check(doc?.browser_http_statuses_measured===false&&doc?.wordpress_changes_authorized===false&&doc?.local_caching_authorized===false,'write_or_network_claim');
 check(doc?.conditional_derivative_max_width_px===960,'width_limit');
 check(Array.isArray(doc?.rows)&&doc.rows.length===6,'six_sources');
 if(!Array.isArray(doc?.rows))return {pass:false,errors};
 for(let i=0;i<6&&i<doc.rows.length;i++){
  const name=ORDER[i],r=doc.rows[i],source=P0[name];
  check(r?.slot===name,'slot_'+i);
  check(r?.original===source.src,'published_source_'+name);
  check(r?.catalog===(name==='418:2'?SECONDARY_418:source.catalog),'candidate_catalog_'+name);
  check(r?.retriever_code===WRAPPERS[i][0]&&r?.retriever_outcome===WRAPPERS[i][1],'wrapper_only_'+name);
  check(r?.guest_http_status===null&&r?.item_rights_for_rehosting_verified===false,'no_guest_or_rights_claim_'+name);
  check(r?.source_native_dimensions_px===null&&r?.proposed_derivative_dimensions_px===null,'no_invented_pixels_'+name);
  const exact=name==='407:1';
  check(r?.catalog_original_same_url===exact,'exact_official_link_'+name);
  check(r?.decision===(exact?'PRESERVE_SOURCE_UNTIL_COLD_GUEST_FAILURE_PROVEN':'HOLD_COLD_GUEST_AND_RIGHTS'),'no_release_'+name);
  if(exact){
   check(r?.original===ORIGINAL_USGS&&r?.catalog_original_link===ORIGINAL_USGS,'usgs_original_link');
   check(r?.catalog_medium_link===MEDIUM_USGS,'usgs_medium_link');
   check(r?.catalog_asserted_rights==='PUBLIC_DOMAIN_USGS_J_R_STACY','usgs_pd_assertion');
   check(r?.candidate_scene==='EXACT_OFFICIAL_USGS_CATALOG_ORIGINAL_LINK_NOT_BINARY_HASH_VERIFIED','no_binary_identity_claim');
  }else{
   check(r?.catalog_original_link===undefined&&r?.catalog_medium_link===undefined&&r?.catalog_asserted_rights===undefined,'not_exact_catalog_link_'+name);
  }
 }
 return {pass:errors.length===0,errors,rows:doc.rows.length,
  direct_official_original_link_matches:doc.rows.filter(x=>x.catalog_original_same_url===true).length,
  confirmed_browser_broken:0,production_write_allowed:false};
}
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const file=path.join(__dirname,'p0_catalog_original_link_custody_20261113.json');
 const result=audit(JSON.parse(fs.readFileSync(file,'utf8')));
 console.log(JSON.stringify(result));if(!result.pass)process.exitCode=1;
}
module.exports={audit};

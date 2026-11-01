'use strict';
/* Evidence-only Florida Memory recovery gate. No HTTP, CMS, image copying or writes. */
const EXPECTED = [
  ['432:0','PR04493','4144','/fpc/prints/pr04493.jpg','1928'],
  ['432:1','RC17068','38362','/fpc/reference/rc17068.jpg','1928-09'],
  ['432:2','RC10673','33289','/fpc/reference/rc10673.jpg','1928'],
  ['432:3','N031889','141398','/fpc/general/n031889.jpg','1928'],
  ['432:4','RC04344','27848','/fpc/reference/rc04344.jpg','1928'],
  ['432:5','RC07668','30741','/fpc/reference/rc07668.jpg','1928'],
  ['432:6','MSF-PB11548-001','340182','/fpc/msf/MSF-PB11548-001.jpg','2001']
];
function requireValid(condition, why) {
  if (!condition) throw new Error('FL432_INVALID:' + why);
}
function emptyProperties(o, fields, why) {
  requireValid(o && typeof o === 'object', why + '_object');
  for (const f of fields) requireValid(o[f] === null, why + '_' + f);
}
function validateFlorida432(d, sourceCensus) {
  requireValid(d && d.schema_version === 1, 'schema');
  requireValid(d.audit_kind === 'PRIMARY_SOURCE_CATALOG_AND_LIVE_CMS_STORED_SOURCE_ONLY','scope');
  requireValid(d.article && d.article.post_id === 432 && d.article.image_slots === 7 && d.article.read_only_editor_image_source_and_alt_matches === 7,'article');
  requireValid(Array.isArray(d.images) && d.images.length === 7,'images');
  requireValid(d.official_rights_policy && d.official_rights_policy.source === 'https://floridamemory.com/share/order-info/faq.php' && d.official_rights_policy.mark === 'PDM-1.0' && d.official_rights_policy.final_editorial_release === false && d.official_rights_policy.attribution_required === true,'publisher_rights');
  requireValid(d.inventory_scope && d.inventory_scope.reported_broken_count_unverified === 42 && d.inventory_scope.reported_weight_reduction_percent_unverified === 76,'not_proven');
  requireValid(sourceCensus && Array.isArray(sourceCensus.observations),'source_census');
  const historical = sourceCensus.observations.filter(o=>o.post_id === 432);
  requireValid(historical.length === 7,'historical_rows');
  const seen = new Set();
  for(let i=0;i<7;i++){
    const x=d.images[i], f=historical[i], [key,id,item,path,date]=EXPECTED[i];
    requireValid(x && x.image_key===key && x.post_id===432 && x.slot===i && !seen.has(key),'slot_' + i);
    seen.add(key);
    requireValid(x.stored_source_url===f.exact_stored_url && x.stored_alt===f.stored_alt && x.cms_src_and_alt_match_frozen_inventory===true,'cms_identity_'+i);
    const c=x.primary_catalog;
    requireValid(c && c.identifier===id && c.item_url==='https://floridamemory.com/items/show/'+item && c.date===date && c.catalog_path===path,'catalog_identity_'+i);
    requireValid(c.publisher_canonical_image_url==='https://floridamemory.com'+path && x.stored_source_url==='https://www.floridamemory.com'+path,'exact_source_path_'+i);
    requireValid(typeof c.title==='string' && c.title.length>15 && typeof c.subject_notes==='string' && c.subject_notes.length>15,'catalog_description_'+i);
    const v=x.third_party_viewer_observation;
    requireValid(v && v.result===f.viewer_result && v.redirect_destination_url===f.viewer_redirect_destination_url,'viewer_observation_'+i);
    emptyProperties(v,['original_image_http_status','visitor_browser_result'],'viewer_http_unknown_'+i);
    emptyProperties(x.visitor_browser,['current_src','final_image_request_url','http_status','mime','encoded_bytes','natural_width','natural_height','decoded','screenshot_path'],'guest_browser_unknown_'+i);
    requireValid(x.original_binary_sha256===null && x.original_dimensions_px===null,'not_downloaded_'+i);
    const t=x.proposed_derivative;
    requireValid(t && t.max_width_px===960 && t.dimensions_px===null && t.upscaling_allowed===false && t.preserve_aspect_ratio===true,'max960_no_upscale_'+i);
    const r=x.copyright;
    requireValid(r && r.source_mark==='PDM-1.0' && r.archive_claim_verified===true && r.individual_reuse_review==='HOLD' && r.credit.includes('State Archives of Florida') && r.credit.includes(id),'individual_rights_'+i);
    const s=x.staging;
    requireValid(s && s.downloaded===false && s.first_party_asset_created===false && s.wordpress_media_uploaded===false && s.article_rewritten===false && s.approved===false,'no_production_write_'+i);
    requireValid(x.verified_broken_for_visitors===null && x.visitor_weight_savings_bytes===null,'no_fabricated_impact_'+i);
  }
  return {valid:true,verified_catalog_rows:7,guest_http_statuses:0,production_repairs:0};
}
module.exports={validateFlorida432,EXPECTED};

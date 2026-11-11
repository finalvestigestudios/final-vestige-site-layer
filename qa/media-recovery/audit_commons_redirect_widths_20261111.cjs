'use strict';
// No network or CMS side effects. Pinned historical source-only width request audit.
const SOURCE_SHA='4965a862f7de7de46c1f4a1e26f3ca70a8c38805';
const prefix='https://commons.wikimedia.org/wiki/Special:Redirect/file/';
function widthOf(u){
 if(typeof u!=='string'||!u.startsWith(prefix))return 'not_commons_redirect';
 const qs=u.includes('?')?u.split('?').slice(1).join('?').split('#')[0]:'';
 const w=qs.split('&').filter(x=>x.startsWith('width='));
 if(w.length>1)throw Error('multiple width parameters');
 if(!w.length)return 'no_width';
 const raw=w[0].slice(6);
 if(!/^[1-9][0-9]{0,4}$/.test(raw))throw Error('malformed width');
 return Number(raw);
}
function build(rows){
 if(!Array.isArray(rows)||rows.length!==288)throw Error('frozen row count changed');
 const seen=new Set(),widths={at1280:0,at960:0,noWidth:0,other:0},entries=[];
 for(const row of rows){
  if(!row||typeof row.slot!=='string'||!(/^[0-9]+:[0-9]+$/).test(row.slot)||seen.has(row.slot))throw Error('invalid slot or duplicate');
  seen.add(row.slot);
  if(row.guest_http_status!==null||row.guest_wire_bytes!==null||row.guest_broken!==null)throw Error('browser evidence unexpectedly present');
  const w=widthOf(row.stored_url);
  if(w==='not_commons_redirect')continue;
  if(w===1280)widths.at1280++;
  else if(w===960)widths.at960++;
  else if(w==='no_width')widths.noWidth++;
  else widths.other++;
  if(w!==1280)continue;
  const c=row.candidate_sources?.[0]||{};
  const d=Array.isArray(c.conditional_960px)&&c.conditional_960px.length===2&&c.conditional_960px.every(x=>Number.isInteger(x)&&x>0)?c.conditional_960px:null;
  entries.push({
   slot:row.slot,post_id:row.post_id,article_url:row.post_url,exact_stored_src:row.stored_url,source_host:row.origin_host,
   source_requested_width_px:1280,
   candidate_catalog_url:c.catalog_url||null,
   candidate_primary_url:c.authoritative_primary_url||null,
   catalog_rights_observation:c.rights_observation||null,
   catalog_conditional_dimensions_not_verified_native:d,
   advisory_no_upscale_max_width_if_catalog_correct:d?Math.min(960,d[0]):null,
   flagged_previously_catalogued_width_below_960:!!d&&d[0]<960,
   visitor_http_status:null,origin_http_status:null,guest_current_src:null,guest_encoded_wire_bytes:null,guest_natural_px:null,
   exact_photo_match_verified:false,item_specific_rights_cleared:false,editor_approved:false,
   binary_download_permitted:false,wordpress_write_permitted:false,caching_permitted:false,homepage_write_permitted:false,
   decision:'P1_STORED_WIDTH_ONLY_NO_AUTOMATIC_REPLACEMENT'
  });
 }
 if(widths.at1280!==75||widths.at960!==17||widths.noWidth!==26||widths.other!==0)throw Error('Commons width census drift');
 const articleSet=new Set(entries.map(x=>x.post_id));
 if(articleSet.size!==16)throw Error('16 article coverage drift');
 return {
  schema:'fv-commons-width-1280-offline-audit-v1',as_of_utc:'2026-11-11',
  provenance:{frozen_288_path:'qa/media-recovery/coverage_288_exact_pr1703_20261110.json',frozen_288_blob:SOURCE_SHA,worklist_pr:183,worklist_blob:'2acd06a4ca4317646006eb6591face3fe76fedec',site_qa_pr:154,media_pr:1703},
  historical:{posts:61,inline_sources:355,external_positions:288,reported_broken_unverified:42,guest_broken_confirmed:0,claimed_transfer_reduction_pct:76,measured_transfer_reduction_pct:null,wp_originals_over_1500000_bytes:15,total_stored_original_bytes:47096779},
  counts:{commons_redirects:widths.at1280+widths.at960+widths.noWidth,requested_width_1280:widths.at1280,requested_width_960:widths.at960,without_width_query:widths.noWidth,affected_posts:articleSet.size,catalog_urls:entries.filter(x=>x.candidate_catalog_url!==null).length,advisory_dimensions:entries.filter(x=>x.catalog_conditional_dimensions_not_verified_native!==null).length,advisory_under_960:entries.filter(x=>x.flagged_previously_catalogued_width_below_960).length},
  required_first_p0:['285:5','285:2','287:5','418:1','418:2','407:1'],
  measured_cold_wire_savings:false,
  binary_downloads:0,wordpress_writes:0,production_rewrites:0,homepage_edits:0,spend_usd:0,
  caveat:'Width=1280 in WordPress src is not a measured visitor request or transfer; 960px is an unapproved cap, not universal correct size or native master geometry. Historical maps and diagrams may need full-resolution viewing.',
  entries
 };
}
function verify(r,rows){
 try{return {pass:JSON.stringify(r)===JSON.stringify(build(rows)),status:'SOURCE_ONLY'};}
 catch(e){return {pass:false,status:String(e.message||e)};}
}
module.exports={SOURCE_SHA,widthOf,build,verify};

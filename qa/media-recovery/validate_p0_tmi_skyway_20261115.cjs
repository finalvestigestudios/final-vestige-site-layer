'use strict';
const fs = require('node:fs');
const path = require('node:path');
const DEFAULT = path.join(__dirname, 'p0_tmi_skyway_lineage_20261115.json');
function check(data) {
  const errors=[];
  const fail=(predicate,label)=>{if(!predicate)errors.push(label);};
  fail(data?.schema==='fv-media-p0-publisher-lineage-v1','schema');
  fail(data?.historical_baseline?.published_posts===61 && data?.historical_baseline?.inline_image_references===355,'frozen_census');
  fail(data?.historical_baseline?.reported_broken_42_browser_confirmed===false,'no_invented_42');
  fail(data?.historical_baseline?.claimed_76_percent_wire_reduction_measured===false,'no_invented_76');
  fail(Array.isArray(data?.rows) && data.rows.length===2,'exact_two_rows');
  fail(data?.methodology?.guest_browser_observation===false && data?.methodology?.binary_download_or_hash===false,'method_boundaries');
  for (const key of ['285:5','287:5']) {
    const r=data?.rows?.find(x=>x.key===key);
    fail(Boolean(r),'missing_'+key);
    if(!r) continue;
    fail(r.post_id===Number(key.split(':')[0]) && /^2026-11-02T/.test(r.post_modified),'cms_provenance_'+key);
    fail(r.published_post.startsWith('https://finalvestige.com/') && /^https:\/\//.test(r.published_url),'source_urls_'+key);
    fail(typeof r.published_alt==='string' && r.published_alt.length>25 && r.published_caption.length>20,'alt_caption_'+key);
    const s=r.source_observation;
    fail(s.method==='web.open' && s.tool_wrapper_status===404 && s.tool_outcome==='NOT_FOUND','retriever_wrapper_'+key);
    fail(['origin_http_status','guest_browser_http_status','guest_current_src','guest_natural_width','guest_transferred_bytes','confirmed_visually_broken'].every(k=>s[k]===null),'not_guest_http_'+key);
    const c=r.candidate;
    fail(c.replacement_approved===false && c.asset_identity_hash===null && c.published_transform_crop_verified===false,'candidate_unverified_'+key);
    fail(c.license_review.startsWith('HOLD_') && c.license_evidence.length>25,'rights_review_'+key);
    fail(r.rights_cleared_for_cache===false && r.wordpress_production_write_allowed===false,'rights_write_hold_'+key);
    if(c.original_width!==null || c.original_height!==null) {
      fail(Number.isInteger(c.original_width)&&Number.isInteger(c.original_height)&&c.original_width>0&&c.original_height>0,'valid_geometry_'+key);
      fail(Number.isInteger(c.proposed_no_upscale_max_width)&&c.proposed_no_upscale_max_width<=960&&c.proposed_no_upscale_max_width<=c.original_width,'no_upscale_'+key);
      fail(c.proposed_full_frame_height===Math.round(c.original_height*c.proposed_no_upscale_max_width/c.original_width),'aspect_'+key);
    } else fail(c.proposed_no_upscale_max_width===null&&c.proposed_full_frame_height===null,'unknown_geometry_'+key);
  }
  const t=data?.rows?.find(r=>r.key==='285:5');
  if(t) {
    fail(t.published_url.includes('ar_16:9,c_fill')&&t.candidate.published_transform==='ar_16:9,c_fill,w_1200','tmi_transform');
    fail(t.candidate.catalog==='https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg'&&t.candidate.publisher_linked_asset.endsWith('/Three_mile_island_062010.jpg'),'tmi_original_chain');
    fail(t.candidate.original_width===819&&t.candidate.original_height===614&&t.candidate.proposed_no_upscale_max_width===819,'tmi_source_pixels');
    fail(t.candidate.catalog_subject.includes('2010')&&t.candidate.catalog_subject.includes('NOT'),'tmi_chronology');
  }
  const s=data?.rows?.find(r=>r.key==='287:5');
  if(s) {
    fail(s.published_url==='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg'&&s.candidate.catalog==='https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg','skyway_same_publisher_moved_path');
    fail(s.candidate.catalog_subject.includes('no later cable-stayed replacement visible')&&s.published_alt.includes('later bridge replacement'),'skyway_alt_overclaim_review');
    fail(s.candidate.original_width===null&&s.candidate.original_height===null,'skyway_no_invented_dimensions');
  }
  const rel=data?.release;
  fail(rel?.source_only_not_visitors===true&&rel?.site_qa_pr_154_owns_browser===true&&rel?.homepage_out_of_scope===true,'scope');
  fail(rel?.media_downloads===0&&rel?.wordpress_uploads===0&&rel?.wordpress_post_edits===0&&rel?.spend_usd===0&&rel?.all_replacements_on_hold===true,'release_hold');
  return {ok:errors.length===0,errors};
}
if(require.main===module){const f=process.argv[2]||DEFAULT;const result=check(JSON.parse(fs.readFileSync(f,'utf8')));console.log(JSON.stringify(result));process.exitCode=result.ok?0:1;}
module.exports={check};

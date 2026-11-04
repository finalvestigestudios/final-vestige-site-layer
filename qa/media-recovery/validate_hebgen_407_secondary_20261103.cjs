'use strict';
/** Safe offline validation of the USGS primary / Commons secondary recovery path for post 407:1. */
const ROOT='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/';
const PIN='48e1ebf07207e948ba5802e714eb39659d2e1c1d';
const COMMONS='https://upload.wikimedia.org/wikipedia/commons/b/b7/Red_Canyon_fault_scarp_sjr00100.jpg';
function validateHebgenSecondary(a,part){
 const e=[],yes=(v,msg)=>{if(!v)e.push(msg)};
 const src=(part?.images||[]).find(x=>x.key==='407:1');
 const other=(part?.images||[]).filter(x=>x.post_id===407);
 yes(a?.schema_version===1&&a?.post_id===407&&a?.image_key==='407:1','identity');
 yes(a?.frozen_source_part==='qa/media-recovery/parts/02.json'&&a?.frozen_source_part_git_blob_sha===PIN,'pinned census');
 yes(other.length===8&&!!src&&a?.source_url===src?.source_url&&a?.source_alt===src?.alt,'exact historic src/alt');
 yes(a?.source_url===ROOT+'img7535.jpg','published link');
 const obs=a?.source_observation||{};
 yes(obs.method==='independent_web_text_retriever'&&obs.result==='UNSUPPORTED_BINARY_OCTET_STREAM'&&obs.wrapper_status===400,'wrapper is not origin');
 yes(obs.origin_http_status===null&&obs.guest_http_status===null&&obs.guest_image_decodes===null&&obs.visitor_current_src===null&&obs.wire_bytes===null&&obs.visitor_broken_confirmed===false,'do not invent visitor outcome');
 const u=a?.official_usgs||{};
 yes(u.catalog_url==='https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959'&&u.credit==='J. R. Stacy / U.S. Geological Survey'&&u.catalog_rights_label==='Public Domain','primary archive');
 yes(JSON.stringify(u.official_link_labels)===JSON.stringify(['Original','Thumbnail','Medium']),'USGS caption links');
 yes(u.original_link_url===ROOT+'thumbnails/image/img7535.jpg'&&u.original_link_url!==a?.source_url,'official original is different path');
 yes(u.thumbnail_url===ROOT+'styles/thumbnail/public/thumbnails/image/img7535.jpg?itok=97xFa4s9'&&u.medium_url===ROOT+'styles/medium/public/thumbnails/image/img7535.jpg?itok=BwZ2ZSkM'&&u.page_display_url===ROOT+'styles/full_width/public/thumbnails/image/img7535.jpg?itok=C0bw-HP5','official rendition identities');
 yes(u.original_viewer_displayed===true&&u.original_intrinsic_dimensions_binary_verified===false&&u.original_binary_sha256===null&&u.proposed_960_derivative===null,'no invented full-master size');
 const c=a?.verified_secondary_archive||{};
 yes(c.catalog_url==='https://commons.wikimedia.org/wiki/File:Red_Canyon_fault_scarp_sjr00100.jpg'&&c.original_file_url===COMMONS&&c.photo_credit==='J. R. Stacy (USGS)','secondary attribution');
 yes(c.catalog_dimensions_px?.width===698&&c.catalog_dimensions_px?.height===700&&c.catalog_original_file_bytes===461875,'catalog dimensions and byte size');
 yes(c.rights_label==='Public domain — USGS (per Commons)'&&c.image_viewer_displayed===true,'archival metadata not legal clearance');
 yes(c.relationship_to_usgs==='SAME_HISTORICAL_PHOTOGRAPH_VISUAL_MATCH_CROP_OR_RENDITION_DIFFERS'&&c.binary_identical_to_usgs===false&&c.source_binary_hash_match_verified===false,'no identity or crop fabrication');
 yes(c.conditional_no_upscale_derivative_px?.width===698&&c.conditional_no_upscale_derivative_px?.height===700,'must not enlarge 698px');
 const v=a?.visitor_verification||{},g=a?.publication_safeguards||{},t=a?.totals_context||{};
 yes(v.confirmed_404===false&&v.existing_src_change_proposed_only===true&&String(v.needed||'').includes('Site QA #154'),'guest proof gate');
 yes(g.rights_item_review==='HOLD'&&g.same_crop_visual_comparison==='HOLD'&&g.first_party_localization_approved===false&&g.wordpress_upload_approved===false&&g.post_block_rewrite_approved===false&&g.homepage_changes_approved===false&&g.binary_asset_downloaded===false&&g.production_repairs===0,'publish/rights hold');
 yes(t.published_posts===61&&t.image_references===355&&t.external_origin_references===288&&t.oversized_wp_originals===13&&t.reported_42_broken_browser_verified===false&&t.reported_76_percent_reduction_measured===false,'baseline');
 return{ok:e.length===0,errors:e};
}
module.exports={validateHebgenSecondary};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const file=fs.readFileSync(path.join(__dirname,'parts/02.json'));
 const sha=crypto.createHash('sha1').update('blob '+file.length+'\0').update(file).digest('hex');
 if(sha!==PIN)throw Error('Frozen census Git blob mismatch: '+sha);
 const a=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_407_secondary_same_photo_20261103.json'),'utf8'));
 const out=validateHebgenSecondary(a,JSON.parse(file.toString('utf8')));console.log(JSON.stringify(out));if(!out.ok)process.exitCode=1;
}

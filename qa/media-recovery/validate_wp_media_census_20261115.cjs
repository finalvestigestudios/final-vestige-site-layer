'use strict';
/** Read-only verifier for a frozen WordPress media/featured-image audit. */
const fs = require('node:fs');
const good = n => Number.isSafeInteger(n) && n > 0;
const bool = v => v === true || v === false;
function validate(doc) {
  const errors=[];
  const add = s => errors.push(s);
  if (!doc || typeof doc!=='object' || Array.isArray(doc)) return {ok:false,errors:['missing_document']};
  if (doc.schema!=='fv-wp-media-featured-oversize-20261115-v1') add('wrong_schema');
  if (doc.source?.kind!=='authenticated_wordpress_media_list_read_only' ||
      doc.source?.page_count!==2 || doc.source?.per_page!==100) add('uncertain_source_provenance');
  const media=doc.media;
  if (!Array.isArray(media) || media.length!==doc.census?.image_count || media.length!==132)
    return {ok:false,errors:[...errors,'media_count_mismatch']};
  const ids=new Set();let allBytes=0,oversizeBytes=0;const oversized=[];
  for (const m of media) {
    if (!good(m?.id) || ids.has(m.id)) add('duplicate_or_bad_id:'+m?.id);
    ids.add(m.id);
    if (!good(m?.stored_original_bytes)) add('invalid_original_bytes:'+m?.id);
    if (!good(m?.native_width_px) || !good(m?.native_height_px)) add('invalid_geometry:'+m?.id);
    let u;try {u=new URL(m?.source_url);} catch {add('bad_url:'+m?.id);continue;}
    if (u.protocol!=='https:' || u.hostname!=='finalvestige.com' ||
        !u.pathname.startsWith('/wp-content/uploads/')) add('non_first_party_media_url:'+m?.id);
    allBytes+=Number(m.stored_original_bytes)||0;
    if (m.stored_original_bytes > 1500000) {oversized.push(m);oversizeBytes+=m.stored_original_bytes;}
  }
  if (allBytes!==doc.census?.stored_original_bytes) add('stored_original_total_mismatch');
  if (oversized.length!==20 || doc.census?.oversize_count_decimal_1500000!==20)
    add('oversize_count_mismatch');
  if (oversizeBytes!==doc.census?.oversize_stored_original_bytes) add('oversize_bytes_mismatch');
  if (!Array.isArray(doc.published_post_ids) || doc.published_post_ids.length!==66 ||
      new Set(doc.published_post_ids).size!==66 || doc.published_post_ids.some(x=>!good(x)))
    add('published_post_census_mismatch');
  const newids=[1917,1920,1924,1926],newmedia=[2640,2638,2636,2637];
  const feature=doc.new_oversized_featured_media;
  if (!Array.isArray(feature) || feature.length!==4) add('new_featured_count_mismatch');
  else {
    const seen=new Set();let freshBytes=0;
    for(const f of feature){
      if (!newids.includes(f.post_id) || !newmedia.includes(f.media_id) || seen.has(f.media_id)) add('unexpected_featured_id');
      seen.add(f.media_id);
      const m=oversized.find(x=>x.id===f.media_id);
      if (!m || m.parent_post_id!==f.post_id || m.source_url!==f.wp_original_url ||
          m.stored_original_bytes!==f.stored_original_bytes) add('featured_wp_join_mismatch:'+f.media_id);
      if(f.featured_media_id_from_post!==f.media_id || f.inline_contains_wp_original!==false ||
         !good(f.inline_external_image_count) || f.placement!=='featured_media_not_inline') add('featured_vs_inline_claim_unverified:'+f.media_id);
      if(!f.source_catalog_url?.startsWith('https://commons.wikimedia.org/wiki/File:') ||
         !['CC0-1.0','CC-BY-4.0','PD-Art'].includes(f.catalog_rights_claim) ||
         !['review_required','source_rights_conflict'].includes(f.rights_review)) add('missing_catalog_custody_or_rights:'+f.media_id);
      const width=Math.min(960,m?.native_width_px||0);
      if(f.review_width_px!==width || f.review_height_px!==Math.round(width*(m?.native_height_px||0)/(m?.native_width_px||1)))
         add('unverified_960px_geometry:'+f.media_id);
      if (f.rehost_or_resize_authorized!==false || f.wordpress_write_authorized!==false ||
          f.actual_guest_http_status!==null || f.actual_guest_transfer_bytes!==null ||
          f.binary_sha256_verified!==false || f.current_src_verified!==false)
         add('premature_optimization_or_repair_claim:'+f.media_id);
      freshBytes+=f.stored_original_bytes;
    }
    if(freshBytes!==15278087 || doc.census?.new_oversized_featured_bytes!==freshBytes) add('new_featured_bytes_mismatch');
  }
  if (doc.census?.historical_oct_30_published_posts!==61 ||
      doc.census?.historical_oct_30_inline_images!==355 ||
      doc.census?.reported_broken_unverified!==42 ||
      doc.census?.claim_76_percent_guest_transfer_measured!==false ||
      doc.census?.guest_broken_confirmed_count!==null ||
      doc.census?.production_changes_this_audit!==0) add('forbidden_or_inferred_outcome_claim');
  return {ok:errors.length===0,errors,summary:{media_count:media.length,oversized_count:oversized.length,stored_original_bytes:allBytes,oversized_stored_original_bytes:oversizeBytes}};
}
if(require.main===module){
 try{const r=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=2;}
 catch(e){console.error('AUDIT_INPUT_ERROR',e.message);process.exitCode=2;}
}
module.exports={validate};

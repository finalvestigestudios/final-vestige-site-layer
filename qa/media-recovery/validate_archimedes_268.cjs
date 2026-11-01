'use strict';
/** Offline, read-only Archimedes post-268 image custody and safety validator. */
const fs = require('node:fs');
const path = require('node:path');

const SLOTS = 10;
const COMMONS = new Set([0, 2, 3, 5, 6, 9]);
const RENDERED = new Set([1, 7]);
const VALID_RETRIEVER = new Set([
  'RENDERED', 'UNAVAILABLE', 'UNAVAILABLE_OR_REDIRECT_NOT_FOLLOWED',
  'APEX_REDIRECT_TARGET_UNAVAILABLE'
]);
const good = v => Number.isSafeInteger(v) && v > 0;
const isHttps = v => typeof v === 'string' && /^https:\/\/[a-z0-9.-]+\//i.test(v);
function exactCommonsFilePage(stored, record) {
  try {
    const src=new URL(stored), cat=new URL(record);
    if (src.hostname!=='commons.wikimedia.org' || cat.hostname!=='commons.wikimedia.org') return false;
    const prefix='/wiki/Special:Redirect/file/', catalogPrefix='/wiki/File:';
    if (!src.pathname.startsWith(prefix) || !cat.pathname.startsWith(catalogPrefix)) return false;
    return decodeURIComponent(src.pathname.slice(prefix.length)).replace(/_/g,' ') ===
      decodeURIComponent(cat.pathname.slice(catalogPrefix.length)).replace(/_/g,' ');
  } catch { return false; }
}
function validate(doc, census) {
  const errors = [];
  if (!doc || typeof doc !== 'object' || Array.isArray(doc))
    return {ok:false, errors:['invalid_manifest']};
  if (doc.schema_version !== 1 || doc.cms?.post_id !== 268 ||
      doc.cms?.status !== 'publish' || !isHttps(doc.cms?.url) ||
      doc.cms?.live_exact_source_url_matches !== 10 ||
      doc.cms?.live_exact_alt_matches !== 10)
    errors.push('cms_identity_or_readback_unverified');
  const observed = Array.isArray(doc.rows) ? doc.rows : [];
  const expected = Array.isArray(census?.images) ?
    census.images.filter(x => x.post_id === 268).sort((a,b)=>a.slot-b.slot) : [];
  if (observed.length !== SLOTS || expected.length !== SLOTS)
    errors.push('expected_ten_images');
  if (new Set(observed.map(x=>x?.image_key)).size !== observed.length)
    errors.push('duplicate_image_key');
  for (let i=0;i<SLOTS;i++) {
    const r=observed[i], e=expected[i];
    if (!r || !e) { errors.push(`missing_or_null_image_slot:${i}`); continue; }
    if (r.image_key !== `268:${i}` || r.post_id !== 268 || r.slot !== i ||
        r.exact_stored_url !== e.source_url || r.alt_text !== e.alt ||
        r.article_url !== e.post_url || !isHttps(r.exact_stored_url))
      errors.push(`source_or_alt_mismatch:${i}`);
    if (r.source_kind !== (COMMONS.has(i)?'wikimedia_redirect':'external'))
      errors.push(`source_kind_mismatch:${i}`);
    const v=r.source_viewer;
    if (!v || !VALID_RETRIEVER.has(v.result) ||
        v.result !== (RENDERED.has(i) ? 'RENDERED' : i===4 ? 'APEX_REDIRECT_TARGET_UNAVAILABLE' : i===8 ? 'UNAVAILABLE' : 'UNAVAILABLE_OR_REDIRECT_NOT_FOLLOWED') ||
        v.method !== 'independent_web_retriever_2026_11_01' ||
        v.http_status !== null || v.decoded_dimensions_px !== null ||
        v.is_guest_browser_proof !== false)
      errors.push(`web_retriever_evidence_is_not_browser:${i}`);
    if (!r.visitor_browser || Object.values(r.visitor_browser).some(v=>v!==null))
      errors.push(`invented_browser_http_or_weight:${i}`);
    const rights=r.rights;
    if (!rights || rights.license_decision!=='HOLD' ||
        rights.item_permission_verified!==false || rights.rights_review_done!==false ||
        !rights.recorded_claim || !rights.credit_to_preserve ||
        r.wordpress_media_upload_authorized!==false || r.wordpress_post_edit_authorized!==false)
      errors.push(`rights_or_production_gate_open:${i}`);
    const c=r.catalog, o=r.optimization;
    if (!c || !o || !rights) { errors.push(`missing_required_custody_object:${i}`); continue; }
    if ( c.original_sha256!==null || !isHttps(c.source_record_url ?? 'https://none.invalid/') ||
        o.maximum_width_px!==960 || o.no_upscale!==true ||
        o.preserve_aspect_ratio!==true || o.source_material_not_downloaded!==true ||
        o.original_master_hash_verified!==false || o.derivative_quality_qa_complete!==false ||
        o.local_cached_media_id!==null)
      errors.push(`custody_or_derivative_gate:${i}`);
    if (COMMONS.has(i)) {
      if (!isHttps(c?.source_record_url) || !exactCommonsFilePage(r.exact_stored_url, c.source_record_url) ||
          c.record_type!=='exact_commons_filename_record' ||
          !good(c.original_width_px) || !good(c.original_height_px))
        errors.push(`commons_catalog_missing:${i}`);
      const tw=Math.min(960,c.original_width_px), th=Math.round(c.original_height_px*tw/c.original_width_px);
      if (o.proposed_width_px!==tw || o.proposed_height_px!==th ||
          tw>c.original_width_px || th>c.original_height_px ||
          (i===0?rights.recorded_claim!=='commons_us_public_domain_claim_unevaluated':rights.recorded_claim!=='commons_cc_by_2_0_vs_project_data_cc_by_3_0'))
        errors.push(`commons_dimensions_or_rights:${i}`);
    } else {
      if (c.source_record_url!==null || c.original_width_px!==null ||
          c.original_height_px!==null || o.proposed_width_px!==null ||
          o.proposed_height_px!==null ||
          rights.recorded_claim!=='no_item_specific_reuse_permission_verified_for_project_website_presentation_photo')
        errors.push(`publisher_photo_scope_or_dimensions:${i}`);
    }
  }
  const s=doc.summary || {};
  if (s.image_slots!==10 || s.commons_file_records!==6 || s.publisher_hosted_jpegs!==4 ||
      s.web_retriever_rendered!==2 || s.web_retriever_inconclusive!==8 ||
      s.visitor_broken_confirmed!==null || s.measured_weight_reduction_percent!==null ||
      s.production_replacements!==0 ||
      typeof doc.publisher_license_scope_warning!=='string' ||
      !doc.publisher_license_scope_warning.includes('CC BY 3.0'))
    errors.push('summary_or_license_scope_invalid');
  return {ok:errors.length===0, errors};
}
if (require.main === module) {
  const root=__dirname;
  const doc=JSON.parse(fs.readFileSync(path.join(root,'archimedes_268_source_rights_20261101.json'),'utf8'));
  const census=JSON.parse(fs.readFileSync(path.join(root,'parts','04.json'),'utf8'));
  const result=validate(doc,census);
  process.stdout.write(JSON.stringify(result)+'\n');
  if (!result.ok) process.exitCode=1;
}
module.exports={validate};

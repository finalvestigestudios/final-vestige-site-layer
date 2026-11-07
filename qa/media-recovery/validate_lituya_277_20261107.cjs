'use strict';
// Offline, read-only source/candidate integrity gate. Does NOT make HTTP requests or write WordPress.
const fs = require('node:fs');
const EXPECTED = Object.freeze({
  '277:0': 'https://www.datosfreak.org/wp-content/uploads/2019/01/Tsunami-maremoto-Lituya-Alaska-1958-1.jpg',
  '277:1': 'https://www.researchgate.net/profile/Tim-Davies-4/publication/258771194/figure/fig10/AS:669504034914309@1536632655693/Lituya-Bay-following-the-1958-tsunami-a-NW-panoramic-view-of-Lituya-Bay-and-Centoaph.png',
  '277:2': 'https://indomgb.s3.amazonaws.com/wp-content/uploads/2025/10/29031840/gigantesca-cicatriz-en-el-acantilado-que-se-ID7X2VZ6AZGR5EAPSHH3IDCIUQ.jpg',
  '277:3': 'https://imagerenderer.com/images/rendered/default/greeting-card/images-medium-5/4-damage-from-1958-lituya-bay-tsunami-us-geological-surveyscience-photo-library.jpg',
  '277:4': 'https://miro.medium.com/v2/resize:fit:1400/1*NtiMuQy8rJhpG_xg-nv92g.png',
  '277:5': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Lituyabay_Earth_Observatory_image_2020.jpg'
});
const EXPECTED_KIND = Object.freeze({
  '277:0':'composite',
  '277:1':'unknown',
  '277:2':'historical_photo_unverified_identity',
  '277:3':'unknown',
  '277:4':'annotated_derivative',
  '277:5':'annotated_false_color_2020'
});
const EXPECTED_CANDIDATES = Object.freeze({
  'COMMONS-LITUYA-OVERVIEW': [750,580],
  'COMMONS-LITUYA-ARROWS': [750,580],
  'COMMONS-LITUYA-SPUR': [750,576],
  'COMMONS-LITUYA-TRIMLINE': [700,440],
  'NASA-LITUYA-2020': [720,480],
  'USGS-LITUYA-1958-AERIAL': null
});
function validate(a) {
  const errors=[];
  const bad=(name)=>errors.push(name);
  if (!a || typeof a !== 'object') return ['invalid-audit'];
  if (a.schema_version!=='fv.media-source-v1'||a.batch_id!=='lituya-277-20261107'||a.post_id!==277) bad('scope');
  const b=a.original_census||{};
  if (b.ref!=='f69a12cd9241ea0f39cfcb74c669bb6f7fb10357' || b.path!=='qa/media-recovery/parts/04.json' || b.baseline_posts!==61 || b.baseline_image_refs!==355 || b.baseline_offsite_refs!==288 || b.site_qa_offsite_refs!==286 || b.delta_unreconciled!==true) bad('baseline');
  if (a.actual_browser_failure_count!==null || a.reported_42_browser_confirmed!==false || a.reported_76_percent_transfer_reduction_measured!==false || a.transfer_bytes_from_browser!==null) bad('unverified-claims');
  if (a.oversize_wp_originals_count_from_other_inventory!==13 || a.oversize_wp_originals_stored_bytes_from_other_inventory!==43522829) bad('storage-baseline');
  if (!Array.isArray(a.slots) || a.slots.length!==6) bad('slot-count');
  const seen=new Set(), candidatesSeen=new Set();
  for(const s of (Array.isArray(a.slots)?a.slots:[])) {
    if (seen.has(s.key)) bad('duplicate-slot:'+s.key); seen.add(s.key);
    if (!(s.key in EXPECTED) || s.post_id!==277 || s.source_url!==EXPECTED[s.key] || s.source_snapshot_date!=='2026-10-30') bad('source:'+s.key);
    if (!s.stored_alt || s.stored_alt.length<20) bad('alt:'+s.key);
    if (s.visual_class!==EXPECTED_KIND[s.key] || !s.visual_observation) bad('visual:'+s.key);
    if (!s.web_viewer || !['rendered','viewer_disabled','viewer_inaccessible'].includes(s.web_viewer.observation)) bad('retriever:'+s.key);
    if (s.web_viewer && (s.web_viewer.origin_http_status!==null||s.web_viewer.final_response_headers!==null)) bad('invented-http:'+s.key);
    const v=s.visitor_browser||{};
    if (v.verified!==false || ['origin_http_status','content_type','decode_ok','natural_width','natural_height','transferred_bytes','rendered_current_src'].some(k=>v[k]!==null)) bad('browser-unproven:'+s.key);
    if (s.rights_to_cache!==false||s.exact_replacement_approved!==false||s.wp_media_item!==null) bad('no-publish:'+s.key);
    if (!Array.isArray(s.candidate_ids)||s.candidate_ids.length<1) bad('missing-candidate:'+s.key);
    if (['277:0','277:4','277:5'].includes(s.key) && !s.recommended_alt_unpublished) bad('integrity-alt:'+s.key);
    if (s.key==='277:5' && !/false-color/i.test(s.recommended_alt_unpublished||'')) bad('NASA-false-color');
    if (s.key==='277:0' && !/two-panel/i.test(s.recommended_alt_unpublished||'')) bad('composite-label');
    if (s.key==='277:4' && !/arrows/i.test(s.recommended_alt_unpublished||'')) bad('overlay-label');
  }
  for(const key of Object.keys(EXPECTED)) if(!seen.has(key)) bad('missing-slot:'+key);
  if (!Array.isArray(a.candidates) || a.candidates.length!==6) bad('candidate-count');
  for(const c of (Array.isArray(a.candidates)?a.candidates:[])) {
    if (candidatesSeen.has(c.candidate_id)) bad('duplicate-candidate:'+c.candidate_id); candidatesSeen.add(c.candidate_id);
    if (!(c.candidate_id in EXPECTED_CANDIDATES)) {bad('unknown-candidate:'+c.candidate_id);continue;}
    if (!/^https:\/\//.test(c.catalog_url||'')|| !c.authority || !c.creator_credit || !c.catalog_rights || !c.rights_review || !c.relationship) bad('candidate-evidence:'+c.candidate_id);
    if (c.identity_verified!==false) bad('unproven-match:'+c.candidate_id);
    const px=EXPECTED_CANDIDATES[c.candidate_id];
    if (!px) {
      if (c.native_px!==null || c.preview_max_px!==null) bad('unknown-dimensions:'+c.candidate_id);
    } else {
      if (!c.native_px||c.native_px.width!==px[0]||c.native_px.height!==px[1]) bad('native-dimensions:'+c.candidate_id);
      const width=Math.min(960,px[0]),height=Math.round(px[1]*width/px[0]);
      if (!c.preview_max_px||c.preview_max_px.width!==width||c.preview_max_px.height!==height||c.preview_max_px.width>px[0]||c.preview_max_px.height>px[1]) bad('no-upscale:'+c.candidate_id);
    }
  }
  for(const s of (Array.isArray(a.slots)?a.slots:[])) for(const id of (Array.isArray(s.candidate_ids)?s.candidate_ids:[])) if (!candidatesSeen.has(id)) bad('unresolved-candidate:'+id);
  const m=a.media_staging_plan||{};
  if (m.stage!=='HOLD'||m.authorized_to_download!==false||m.authorized_to_upload!==false||m.authorized_to_publish!==false||m.word_press_changes!==0 || !/SHA-256/.test(m.when_approved||'')) bad('staging-safety');
  return errors;
}
module.exports = {validate,EXPECTED};
if (require.main === module) {
  const data = JSON.parse(fs.readFileSync(process.argv[2] || __dirname+'/lituya_277_six_sources_20261107.json','utf8'));
  const errors = validate(data);
  if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
  else console.log('PASS Lituya 277: six sources, rights, archival geometry, no fabricated browser evidence');
}

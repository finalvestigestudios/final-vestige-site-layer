'use strict';
/**
 * Read-only Lituya Bay 277 media evidence gate. Refuse to infer guest HTTP or rights
 * from independent image viewer data. Do not fetch network or modify WordPress.
 */
const EXPECTED_SHA = '6df3251e5a67a971d87a516a1ba4a0cc32f51f96';
const outcomes = new Set([
  'IMAGE_RENDERED_IN_INDEPENDENT_VIEWER',
  'RETRIEVAL_DISABLED_NO_HTTP',
  'VIEWER_URL_INACCESSIBLE_NO_HTTP'
]);
const expectedOutcomes = [
  'IMAGE_RENDERED_IN_INDEPENDENT_VIEWER','RETRIEVAL_DISABLED_NO_HTTP',
  'IMAGE_RENDERED_IN_INDEPENDENT_VIEWER','VIEWER_URL_INACCESSIBLE_NO_HTTP',
  'IMAGE_RENDERED_IN_INDEPENDENT_VIEWER','IMAGE_RENDERED_IN_INDEPENDENT_VIEWER'
];
const expectedFindings = [
  'MISLEADING_IMAGE_TYPE','UNVERIFIED','NO_VISUAL_MISMATCH_OBSERVED',
  'UNVERIFIED','OMITS_MODERN_ANNOTATION','OMITS_FALSE_COLOR_AND_ANNOTATIONS'
];
const nil = value => value === null;
function validate(document, frozen) {
  const errors = [];
  const check = (yes, reason) => { if (!yes) errors.push(reason); };
  if (!document || typeof document !== 'object' || !frozen || typeof frozen !== 'object')
    return {ok:false, errors:['document and frozen source required']};
  const s=document.snapshot||{}, stats=document.result||{}, gates=document.release_gates||{}, rows=document.images;
  check(document.schema==='fv.media.lituya277.provenance.v1','schema');
  check(s.path==='qa/media-recovery/parts/04.json' && s.git_blob_sha===EXPECTED_SHA,'frozen source pointer');
  const published=(frozen.posts||[]).find(p=>p.id===277);
  const originals=(frozen.images||[]).filter(i=>i.post_id===277).sort((a,b)=>a.slot-b.slot);
  check(!!published && published.url===s.post_url && published.modified===s.post_modified_at_snapshot,'post source identity');
  check(originals.length===6 && s.post_id===277 && s.expected_slots===6,'source slots');
  check(Array.isArray(rows) && rows.length===6,'six audit rows');
  check(stats.source_slots===6 && stats.independent_viewer_displayed===4 && stats.independent_viewer_unresolved===2,'source-only counts');
  for(const n of ['confirmed_visitor_broken','verified_visitor_wire_bytes','percent_weight_reduction'])
    check(nil(stats[n]),'unmeasured must be null: '+n);
  check(stats.production_repairs===0,'no production repairs');
  if(!Array.isArray(rows)) return {ok:false, errors};
  let rendered=0;
  rows.forEach((r,i)=>{
    const o=originals[i],v=r.independent_viewer||{},guest=r.guest_browser||{},edit=r.editorial||{},rights=r.rights_review||{},opt=r.optimization||{},pub=r.publication||{};
    check(!!o && r.image_key==='277:'+i && r.slot===i && r.post_id===277,'slot identity '+i);
    check(!!o && r.original_src===o.source_url && r.original_alt===o.alt && r.original_kind===o.source_kind,'frozen exact URL/ALT '+i);
    check(typeof r.original_src==='string' && r.original_src.startsWith('https://'),'original HTTPS '+i);
    check(v.date_local==='2026-11-02' && outcomes.has(v.result) && v.result===expectedOutcomes[i],'retriever result '+i);
    check(nil(v.numeric_origin_http_status),'retriever numeric status not established '+i);
    if(v.result==='IMAGE_RENDERED_IN_INDEPENDENT_VIEWER')rendered++;
    for(const n of ['actual_http_status','final_url','current_src','decode_success','natural_width_px','natural_height_px','encoded_data_length_bytes','desktop_screenshot','mobile_screenshot'])
      check(nil(guest[n]),'fabricated visitor browser evidence '+i+':'+n);
    check(edit.finding===expectedFindings[i],'editorial observed finding '+i);
    check(i===0 || i===4 || i===5 ? typeof edit.proposed_alt_not_published==='string' && edit.proposed_alt_not_published.length>35 : nil(edit.proposed_alt_not_published),'ALT proposal '+i);
    check(rights.status==='HOLD' && typeof rights.note==='string' && rights.note.length>24,'rights HOLD '+i);
    check(opt.hard_max_width_px===960 && opt.no_upscale===true && opt.crop_requires_approval===true,'no upscaling/crop '+i);
    check(pub.wordpress_upload_approved===false && pub.source_rewrite_approved===false && pub.cache_approved===false && nil(pub.binary_sha256),'no production or binary identity grant '+i);
    const candidate=r.primary_source_candidate;
    if(candidate!==null) {
      check(typeof candidate.url==='string' && candidate.url.startsWith('https://'),'official URL '+i);
      check(typeof candidate.credit==='string' && !!candidate.credit,'candidate credit '+i);
      check(typeof candidate.relation==='string' && candidate.relation.length>48,'candidate scene relationship '+i);
    }
    if(i===5) {
      check(candidate && candidate.custodian==='NASA Earth Observatory' && candidate.master_width_px===720 && candidate.master_height_px===480,'NASA Commons master 720x480');
      check(opt.verified_original_width_px===720 && opt.verified_original_height_px===480 && opt.conditional_width_px===720 && opt.conditional_height_px===480,'do not upscale 720px NASA file');
    } else {
      check(nil(opt.verified_original_width_px) && nil(opt.verified_original_height_px) && nil(opt.conditional_width_px) && nil(opt.conditional_height_px),'do not invent geometry '+i);
      if(candidate)check(nil(candidate.conditional_width_px) && nil(candidate.conditional_height_px),'do not invent candidate dimensions '+i);
    }
  });
  check(rendered===4,'four viewer displays');
  for(const n of ['site_qa_guest_chrome_evidence_required','item_rights_review_required','binary_and_crop_review_required','editorial_alt_approval_required','production_changes_forbidden','site_qa_pr154_unchanged','homepage_design_unchanged'])
    check(gates[n]===true,'release gate '+n);
  check(gates.subscription_spend_usd===0,'no subscription spend');
  return {ok:errors.length===0,errors};
}
module.exports={validate,EXPECTED_SHA};

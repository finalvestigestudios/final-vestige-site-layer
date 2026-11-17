'use strict';
/** Source-only supersession validator. No network, image copying or WordPress writes. */
const parse=u=>{const m=typeof u==='string'&&u.match(/^https:\/\/([^/?#]+)(\/[^?#]*)(?:\?([^#]*))?$/);return m?{host:m[1],path:m[2],query:m[3]||''}:null};
const kind=(original,stored)=>{
 const a=parse(original),b=parse(stored);
 if(!a||!b||a.host!=='finalvestige.com')return null;
 if(b.host===a.host&&b.path===a.path&&!b.query)return 'direct_first_party';
 if(b.host==='i0.wp.com'&&b.path==='/'+a.host+a.path&&b.query&&
   b.query.split('&').every(k=>/^(?:fit|ssl)=/.test(k))&&
   b.query.split('&').some(k=>/^fit=/.test(k))&&b.query.split('&').some(k=>/^ssl=1$/.test(k)))
  return 'first_party_jetpack_proxy';
 return null;
};
function validate(a,old,direct,part,part01,part08){
 const e=[],fail=s=>e.push(s),sum=v=>v.reduce((n,x)=>n+x.original_storage_bytes,0);
 if(!a||a.schema_version!==1||!Array.isArray(a.rows)||a.rows.length!==13)return{ok:false,errors:['invalid_rows_or_schema']};
 if(a.supersedes_direct_only_inference!=='qa/media-recovery/oversized_inline_exposure_20261102.json')fail('superseded_artifact_missing');
 const refs=[['reconciled_oct31','8388236ca03c283da3f72354bdc3f7ca9913e440'],
 ['direct_only_nov02','f8207544a0d11823b6e10cb500bc9f3abbc009ed'],
 ['vasa_post_census','48e1ebf07207e948ba5802e714eb39659d2e1c1d'],
 ['malbone_post_census','948bc1b65b42799aa40cfdb810ddf6ffd80886b6'],
 ['five_png_post_census','5659ec243c188928be3f89c0f96354b660608ca2']];
 for(const [k,sha]of refs)if(a.frozen_inputs?.[k]?.blob_sha!==sha)fail('unpinned_source:'+k);
 if(a.frozen_inputs?.full_inventory_post_count!==61||a.frozen_inputs?.full_inventory_stored_images!==355)fail('census_unpinned');
 if(old?.summary?.inline_media_records!==10||old?.rows?.length!==13||
  direct?.summary?.oversized_originals_with_inline_reference!==7||direct?.rows?.length!==13)
  fail('prior_evidence_invalid');
 const seenIds=new Set(),seenKeys=new Set(),byOld=new Map(old.rows.map(x=>[x.media_id,x])),
  byDirect=new Map(direct.rows.map(x=>[x.media_id,x]));
 const corpus=[part,part01,part08];
 if(corpus.some(p=>!p||!Array.isArray(p.images)))fail('missing_source_parts');
 const source=new Map(corpus.flatMap(p=>p?.images||[]).map(x=>[x.key,x]));
 const classified={INLINE_DIRECT_FIRST_PARTY:[],INLINE_FIRST_PARTY_JETPACK_PROXY:[],NOT_MATCHED_INLINE_IN_FROZEN_61_POSTS:[]};
 for(const row of a.rows){
  const id=row.media_id,origin=byOld.get(id),legacy=byDirect.get(id);
  if(!Number.isSafeInteger(id)||seenIds.has(id)||!origin||!legacy){fail('missing_or_repeated_original:'+id);continue}
  seenIds.add(id);
  if(row.original_source_url!==origin.original_url||row.original_source_url!==legacy.original_url||
    row.original_storage_bytes!==origin.original_storage_bytes||
    row.original_storage_bytes!==legacy.original_bytes||
    row.original_geometry_px?.width!==origin.original_width_px||
    row.original_geometry_px?.height!==origin.original_height_px)fail('original_identity_changed:'+id);
  const matches=row.inline_slot_matches;
  if(!Array.isArray(matches)||matches.length!==origin.inline_matches.length){fail('inline_match_count_changed:'+id);continue}
  for(let i=0;i<matches.length;i++){
   const m=matches[i],original=origin.inline_matches[i];
   if(seenKeys.has(m.image_key))fail('repeated_slot:'+m.image_key);
   seenKeys.add(m.image_key);
   if(m.image_key!==original.image_key||m.post_id!==original.post_id||
      m.post_url!==original.post_url||m.stored_source_url!==original.stored_url)
      fail('historical_slot_identity_changed:'+id);
   const actualKind=kind(row.original_source_url,m.stored_source_url);
   if(actualKind!==m.origin_match_kind)fail('origin_not_verified:'+id);
   const frozen=source.get(m.image_key);
   if(!frozen||frozen.source_url!==m.stored_source_url||frozen.alt!==m.alt||
      !frozen.alt||frozen.post_id!==m.post_id||frozen.post_url!==m.post_url||
      frozen.width_px!==m.stored_html_geometry_px?.width||
      frozen.height_px!==m.stored_html_geometry_px?.height)
    fail('inline_alt_or_html_geometry_mismatch:'+m.image_key);
  }
  let expected=!matches.length?'NOT_MATCHED_INLINE_IN_FROZEN_61_POSTS':
   matches.some(m=>m.origin_match_kind==='first_party_jetpack_proxy')?
   'INLINE_FIRST_PARTY_JETPACK_PROXY':'INLINE_DIRECT_FIRST_PARTY';
  if(expected!==row.inline_class||!classified[expected])fail('false_inline_class:'+id);
  else classified[expected].push(row);
  const legacyMatches=(legacy.inline_references||[]).map(x=>x.image_key).sort();
  if(expected==='INLINE_FIRST_PARTY_JETPACK_PROXY'&&legacyMatches.length)fail('not_a_direct_only_undercount:'+id);
  if(expected!=='INLINE_FIRST_PARTY_JETPACK_PROXY'&&
    JSON.stringify(legacyMatches)!==JSON.stringify(matches.map(x=>x.image_key).sort()))
    fail('previous_direct_matches_changed:'+id);
  if(row.recorded_responsive_variant_url!==origin.known_1024_variant_url||
      row.has_registered_subsizes!==origin.wordpress_registered_subsizes)
    fail('responsive_metadata_changed:'+id);
  const w=Math.min(960,origin.original_width_px),h=Math.round(w*origin.original_height_px/origin.original_width_px);
  if(row.conditional_derivative_px?.width!==w||row.conditional_derivative_px?.height!==h||
      row.conditional_derivative_px?.no_upscale!==true||
      row.conditional_derivative_px?.source_dimensions_only!==true)
    fail('unsafe_derivative_geometry:'+id);
  if(row.guest_http_status!==null||row.guest_current_src!==null||
      row.guest_encoded_wire_bytes!==null||row.guest_visual_decode!==null||
      row.measured_savings_bytes!==null||row.rights_cleared_for_derivative!==false||
      row.wordpress_production_write_authorized!==false)
    fail('unsupported_browser_rights_or_wp_claim:'+id);
 }
 if(seenIds.size!==13||seenKeys.size!==10)fail('incomplete_media_or_slots');
 const directRows=classified.INLINE_DIRECT_FIRST_PARTY,proxy=classified.INLINE_FIRST_PARTY_JETPACK_PROXY,
   unmatched=classified.NOT_MATCHED_INLINE_IN_FROZEN_61_POSTS;
 const expected={oversized_original_count:13,original_storage_bytes:43522829,
  inline_original_count:10,inline_original_storage_bytes:36937913,
  direct_inline_count:7,direct_inline_storage_bytes:23619602,
  first_party_jetpack_inline_count:3,first_party_jetpack_inline_storage_bytes:13318311,
  not_matched_inline_count:3,not_matched_inline_storage_bytes:6584916,
  five_unvarianted_png_original_storage_bytes:13267538,
  reported_broken_42_guest_verified:false,claimed_76_percent_wire_savings_measured:false,production_repairs:0,
  previously_omitted_snapshot_alts_recovered:7,source_snapshot_nonempty_alts_for_inline_originals:10,
  five_unvarianted_png_html_geometry_verified:5};
 for(const [k,v]of Object.entries(expected))if(a.summary?.[k]!==v)fail('summary_mismatch:'+k);
 const pngs=directRows.filter(r=>r.original_source_url.endsWith('.png')&&!r.has_registered_subsizes);
 const expectedRetriever={observed_date:'2026-11-02',method:'web_open_exact_published_original_binary_url',
  outcome:'TOOL_INACCESSIBLE_NO_HTTP_STATUS',wrapper_http_status:null,origin_http_status:null,
  guest_browser_http_status:null,image_decode_verified:false};
 if(pngs.some(r=>JSON.stringify(r.independent_source_retriever_check)!==JSON.stringify(expectedRetriever))||
    a.rows.filter(r=>!pngs.includes(r)).some(r=>r.independent_source_retriever_check!==null))
  fail('unsupported_png_origin_status_assertion');
 if(pngs.length!==5||pngs.some(r=>r.original_geometry_px?.width!==1672||
    r.original_geometry_px?.height!==941||r.inline_slot_matches[0]?.stored_html_geometry_px?.width!==1024||
    r.inline_slot_matches[0]?.stored_html_geometry_px?.height!==576)||sum(pngs)!==13267538)
  fail('five_png_source_metadata_mismatch');
 if(sum(directRows)!==23619602||sum(proxy)!==13318311||sum(unmatched)!==6584916)
  fail('category_sum_mismatch');
 if(JSON.stringify(proxy.map(r=>r.media_id).sort((x,y)=>x-y))!=='[382,388,389]')
  fail('vasa_match_membership_changed');
 const gates=a.rights_and_implementation_gates;
 if(!gates||gates.no_third_party_images_downloaded!==true||
    gates.rights_review_required!==true||gates.visual_integrity_review_required!==true||
    gates.each_derivative_max_width_px!==960||gates.never_upscale!==true||
    gates.wordpress_media_upload_authorized!==false||
    gates.wordpress_post_edit_authorized!==false||
    gates.homepage_visual_design_changed!==false||
    gates.site_qa_pr_154_modified!==false||gates.subscription_spend!==false)
  fail('safety_gate_weakened');
 return{ok:e.length===0,errors:[...new Set(e)],summary:a.summary};
}
module.exports={validate,kind};

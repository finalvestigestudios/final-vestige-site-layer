'use strict';
/** Fail-closed offline audit. Source original sizes are NOT browser transfer bytes. */
const HERO={39:34,40:35,41:36,42:37,43:38};
const okInt=x=>Number.isSafeInteger(x)&&x>0;
function validate(ledger,baseline){
 const errors=[];
 if(!ledger||typeof ledger!=='object'||!Array.isArray(ledger.rows)||!Array.isArray(baseline))return {ok:false,errors:['invalid_input']};
 if(ledger.schema_version!==1||ledger.review_date!=='2026-11-01'||ledger.post_count!==61||
    ledger.image_slot_count!==355||ledger.rows.length!==13||baseline.length!==13)errors.push('invalid_inventory_scope');
 if(ledger.source_baseline_blob_sha!=='9cafdd8f326316b8622b4069fcdfe0f2dc3966d5')errors.push('baseline_source_changed');
 if(ledger.broken_42_visitor_verified!==false||ledger.reduction_76pct_measured!==false||
    ledger.production_replacements!==0)errors.push('fabricated_performance_or_recovery_claim');
 const base=new Map(baseline.map(r=>[r.media_id,r])),ids=new Set();
 for(const r of ledger.rows){
  if(!r||typeof r!=='object'){errors.push('invalid_row');continue}
  const b=base.get(r.media_id),id=r.media_id;
  if(ids.has(id)||!b)errors.push('wrong_or_duplicate_media_id:'+id);
  ids.add(id);
  if(!b)continue;
  if(r.original_url!==b.url||!/^https:\/\/finalvestige\.com\/wp-content\/uploads\//.test(r.original_url||''))
   errors.push('original_url_changed:'+id);
  if(r.original_bytes!==b.original_bytes||!okInt(r.original_bytes)||r.original_bytes<=1572864||
     r.dimensions_px?.width!==b.original_width_px||r.dimensions_px?.height!==b.original_height_px)
   errors.push('original_metadata_changed:'+id);
  const width=Math.min(960,b.original_width_px),height=Math.round(width*b.original_height_px/b.original_width_px);
  if(r.proposed_max_width_px!==960||r.conditional_dimensions_px?.width!==width||
     r.conditional_dimensions_px?.height!==height||r.no_upscale!==true||r.preserve_aspect_ratio!==true)
   errors.push('unsafe_conditional_geometry:'+id);
  if(!Array.isArray(r.stored_inline_positions)||JSON.stringify(r.stored_inline_positions)!==JSON.stringify(b.referenced_inline_positions)||
    r.referenced_inline_61_post_census!==(b.referenced_inline_positions.length>0))
    errors.push('inline_census_mismatch:'+id);
  if(r.actual_browser_status!==null||r.actual_browser_current_src!==null||r.actual_browser_encoded_bytes!==null||
     r.verified_savings_percent!==null)errors.push('invented_browser_evidence:'+id);
  if(r.master_sha256!==null||r.rights_review!=='HOLD'||r.approved_for_localization!==false||
     r.approved_to_edit_post!==false)errors.push('rights_or_production_gate_opened:'+id);
  if(typeof r.wp_media_details_subsizes_present!=='boolean')errors.push('missing_live_metadata_state:'+id);
  if(Object.hasOwn(HERO,id)){
   if(r.mime_type!=='image/png'||r.dimensions_px?.width!==1672||r.dimensions_px?.height!==941||
      r.wp_media_details_subsizes_present!==false||r.featured_on_checked_published_post_id!==HERO[id]||
      r.stored_inline_positions.length!==1||r.stored_inline_positions[0]!==HERO[id]+':0'||
      !/^https:\/\/finalvestige\.com\//.test(r.published_post_url_checked||'')||
      !String(r.verified_alt_text||'').startsWith('AI-assisted historical reconstruction'))
    errors.push('featured_png_findings_changed:'+id);
  }else if(r.wp_media_details_subsizes_present!==true)errors.push('existing_subsize_metadata_changed:'+id);
 }
 if(ids.size!==13)errors.push('missing_media_id');
 const c=ledger.counts||{},hs=ledger.rows.filter(r=>Object.hasOwn(HERO,r.media_id));
 const total=ledger.rows.reduce((n,r)=>n+(Number(r?.original_bytes)||0),0);
 if(c.oversized_originals!==13||c.source_library_original_bytes!==total||
    c.inline_items_in_61_posts!==ledger.rows.filter(r=>r.referenced_inline_61_post_census).length||
    c.not_inline_items_in_61_posts!==ledger.rows.filter(r=>!r.referenced_inline_61_post_census).length||
    c.wp_metadata_without_subsizes!==ledger.rows.filter(r=>!r.wp_media_details_subsizes_present).length||
    c.inline_and_featured_png_no_subsizes!==5||
    c.inline_and_featured_png_original_bytes!==hs.reduce((n,r)=>n+r.original_bytes,0)||
    c.actual_guest_transfer_bytes!==null)errors.push('aggregate_originals_not_wire_bytes');
 return{ok:!errors.length,errors};
}
module.exports={validate};

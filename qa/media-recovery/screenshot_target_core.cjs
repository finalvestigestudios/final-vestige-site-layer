'use strict';
/** Conservative screenshot selection: evidence must belong to the exact DOM slot. */
function selectScreenshotTarget(row,domImages){
 if(!Array.isArray(domImages))return {ok:false,reason:'missing_dom_snapshot'};
 if(!row||row.verified_broken_in_browser!==true||row.result!=='confirmed_broken_in_probe_browser'||row.current_src_identity_verified!==true)
  return {ok:false,reason:'not_a_confirmed_identity_bound_failure'};
 const i=row.rendered_index;
 if(!Number.isSafeInteger(i)||i<0||i>=domImages.length)return {ok:false,reason:'missing_or_out_of_bounds_dom_index'};
 const el=domImages[i];
 if(!el||el.index!==i)return {ok:false,reason:'dom_index_changed'};
 if(!row.current_src||el.currentSrc!==row.current_src||el.src!==row.rendered_src||el.alt!==row.rendered_alt)
  return {ok:false,reason:'active_image_identity_or_alt_changed'};
 if(el.complete!==true||el.naturalWidth!==0)return {ok:false,reason:'image_no_longer_visibly_broken'};
 return {ok:true,index:i,reason:'exact_dom_slot_verified'};
}
module.exports={selectScreenshotTarget};

'use strict';
const CANONICAL=[
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Herculaneum%20papyri.jpg?width=960","Carbonized Herculaneum papyrus fragments PHerc. 1103 and PHerc. 110, showing the dark brittle surfaces created by the AD 79 eruption.","https://commons.wikimedia.org/wiki/File:Herculaneum_papyri.jpg",2006,1740],
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Herculaneum%2C%20past%2C%20present%20and%20future%20%281908%29%20%2814596218878%29.jpg","Historic view of Herculaneum papyrus rolls and early work associated with the collection.","https://commons.wikimedia.org/wiki/File:Herculaneum,_past,_present_and_future_(1908)_(14596218878).jpg",3334,948],
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Abbot-Piaggio-machine-Herculaneum-papyri.jpg","Wooden mechanical apparatus developed from Antonio Piaggio's eighteenth-century machine for slowly unrolling carbonized Herculaneum papyri.","https://commons.wikimedia.org/wiki/File:Abbot-Piaggio-machine-Herculaneum-papyri.jpg",876,552],
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Heruclaneum%20Papyrus%201521%20f001r%2C%20British%20Library%2001.jpg?width=960","Charred and physically opened Herculaneum papyrus fragment preserving ancient writing.","https://commons.wikimedia.org/wiki/File:Heruclaneum_Papyrus_1521_f001r,_British_Library_01.jpg",2000,1432],
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Herculaneum%20papyrus%201425.png?width=960","Herculaneum papyrus fragment showing preserved Greek writing on carbonized material.","https://commons.wikimedia.org/wiki/File:Herculaneum_papyrus_1425.png",500,740],
  ["https://commons.wikimedia.org/wiki/Special:Redirect/file/Tetrapharmakos%20PHerc%201005%20col%205.png","Digitized text from Herculaneum papyrus PHerc. 1005 showing the kind of ancient writing scholars work to recover.","https://commons.wikimedia.org/wiki/File:Tetrapharmakos_PHerc_1005_col_5.png",467,179]
];
const SHASOURCE="9b16b828342a9ac338f3e65610fd3d8d508355e9";
function validate(a){
const e=[];const bad=(flag,msg)=>{if(flag)e.push(msg);};
bad(a?.schema!=='fv-herculaneum-252-exact-source-v1','schema');
bad(a?.post?.id!==252||a?.post?.status!=='publish'||a?.post?.url!=='https://finalvestige.com/2026/08/18/they-thought-the-books-were-charcoal/','post');
bad(a?.frozen_inventory?.blob_sha!==SHASOURCE,'immutable_source_blob');
bad(a?.live_wordpress_readback?.read_only!==true||a?.live_wordpress_readback?.exact_matches!==6||a?.live_wordpress_readback?.image_slot_count!==6,'live_cms');
bad(a?.measurement?.reported_broken_42_unverified!==true||a?.measurement?.confirmed_guest_browser_broken!==0||a?.measurement?.measured_image_wire_reduction_pct!==null||a?.measurement?.claimed_76_pct_wire_reduction_verified!==false,'unmeasured_claims');
bad(a?.measurement?.wp_large_original_count_decimal_1_5_mb!==15||a?.measurement?.wp_large_stored_original_bytes!==47096779,'oversize_storage_not_wire');
bad(!Array.isArray(a?.rows)||a.rows.length!==6,'six_rows');
if(Array.isArray(a?.rows))a.rows.forEach((r,i)=>{
  const ref=CANONICAL[i];if(!ref){e.push('excess_row');return;}
  bad(r?.slot!==`252:${i}`||r?.post_id!==252||r?.live_cms_exact_match!==true,'source_slot_'+i);
  bad(r?.published_src!==ref[0]||r?.published_alt!==ref[1],'exact_published_src_alt_'+i);
  bad(r?.host!=='commons.wikimedia.org','host_'+i);
  bad(r?.catalog?.url!==ref[2]||r?.catalog?.original_width_px!==ref[3]||r?.catalog?.original_height_px!==ref[4]||r?.catalog?.record_page_accessible!==true||r?.catalog?.verified_binary_identity!==false,'catalog_'+i);
  bad(!r?.catalog?.rights_statement||!r?.catalog?.creator_credit,'catalog_rights_credit_'+i);
  const w=Math.min(960,ref[3]),h=Math.round(w*ref[4]/ref[3]);
  bad(r?.derivative?.conditional_max_width_px!==w||r?.derivative?.conditional_height_px!==h||r?.derivative?.no_upscale!==true||r?.derivative?.image_binary_downloaded!==false||r?.derivative?.derivative_rendered!==false,'960px_no_upscale_'+i);
  bad(r?.viewer?.method!=='web_open_literal_source_url'||r?.viewer?.result!=='tool_url_inaccessible','tool_observation_'+i);
  for(const key of ['origin_http_status','guest_browser_status','final_current_src','guest_natural_width','guest_natural_height','guest_encoded_bytes','definitively_broken'])
    bad(r?.viewer?.[key]!==null,'fabricated_browser_evidence_'+i+'_'+key);
  bad(r?.permissions?.rights_review!=='HOLD'||r?.permissions?.download!==false||r?.permissions?.cache!==false||r?.permissions?.wordpress_upload!==false||r?.permissions?.publish!==false||r?.permissions?.post_block_rewrite!==false,'unapproved_actions_'+i);
  if([1,4,5].includes(i)){
    bad(r?.fidelity?.issue!=='clear_mismatch'||r?.fidelity?.editor_review_required!==true,'mismatch_flag_'+i);
    bad(!r?.fidelity?.proposed_alt_for_editor_only,'missing_editorial_recommendation_'+i);
  }else bad(r?.fidelity?.issue!==null||r?.fidelity?.proposed_alt_for_editor_only!==null,'unsupported_mismatch_'+i);
});
bad(a?.release_policy!=='HOLD_ALL; each proposed caption requires separate editor authorization; no media copying or upload.','release_policy');
return {ok:e.length===0,errors:e};
}
module.exports={validate,CANONICAL};

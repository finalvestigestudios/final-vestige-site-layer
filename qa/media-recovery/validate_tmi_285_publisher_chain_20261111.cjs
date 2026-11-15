'use strict';
const SRC={
'285:5':'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg',
'285:2':'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg'
};
function verify(x){
const e=[],assert=(p,s)=>{if(!p)e.push(s)};
assert(x?.schema==='fv-tmi-p0-publisher-chain-v1','schema');
assert(x?.site_qa_pr===154&&x?.media_recovery_draft_pr===1703,'pr_ownership');
assert(x?.reference_bridge_blob_sha==='d1a9c7a499510ec37bcdba5858d45165752587e0','bridge_sha');
assert(Array.isArray(x?.originals)&&x.originals.length===2,'two_originals');
const seen=new Set();
for(const row of (Array.isArray(x?.originals)?x.originals:[])){
const k=row?.slot||'?';assert(!seen.has(k),'duplicate_'+k);seen.add(k);
assert(SRC[k]===row?.stored_src,'stored_src_'+k);
assert(row?.retriever?.observed_original_url===row?.stored_src,'wrapper_url_'+k);
assert(row?.retriever?.method==='WEB_WRAPPER_NOT_GUEST_OR_ORIGIN','wrapper_method_'+k);
assert(row?.retriever?.wrapper_code===({'285:5':404,'285:2':500})[k],'wrapper_code_'+k);
assert(row?.priority===({'285:5':1,'285:2':2})[k],'order_'+k);
assert(row?.post_id===285&&typeof row?.alt==='string'&&row.alt.length>20&&typeof row?.caption==='string','post_alt_caption_'+k);
for(const f of ['guest_http_status','origin_http_status','guest_current_src','guest_natural_px','cold_encoded_transfer_bytes'])assert(row?.[f]===null,'unmeasured_'+k+'_'+f);
for(const f of ['guest_failure_confirmed','rights_clearance_verified','scene_crop_approved','caching_approved','wordpress_staging_media_upload_approved','wordpress_production_write_approved'])assert(row?.[f]===false,'false_approval_'+k+'_'+f);
assert(row?.decision==='HOLD','hold_'+k);
if(k==='285:5'){
assert(row?.publisher?.image_credit_url===row?.candidate?.file_url,'publisher_link_to_candidate');
assert(row?.candidate?.rights==='COMMONS_PD_SELF_UPLOADER_ASSERTION_ITEM_REVIEW','self_license_scope');
assert(row?.candidate?.native_px?.join('x')==='819x614','true_native');
assert(row?.candidate?.conditional_no_upscale_output_px?.join('x')==='819x614'&&row?.candidate?.max_width_px===819,'no_upscale');
assert(row?.candidate?.original_derivative_crop_match_verified===false,'binary_not_proven');
assert(row?.historical_alternative?.same_photo===false&&row?.historical_alternative?.year===1979,'1979_not_same');
assert(row?.historical_alternative?.conditional_no_upscale_output_px?.join('x')==='960x921','historic_alt_geom');
}
if(k==='285:2'){
assert(row?.publisher?.figure_index===4&&row?.publisher?.figure_href===row?.stored_src,'figure4_href');
assert(row?.publisher?.figure_credit==='Nuclear Regulatory Commission','nrc_credit');
assert(row?.candidate?.catalog_url===null&&row?.candidate?.native_px===null&&row?.candidate?.conditional_no_upscale_output_px===null,'no_invented_nrc_item');
assert(row?.candidate?.original_derivative_crop_match_verified===false,'no_fig_binary_match');
}
}
assert(seen.size===2&&seen.has('285:2')&&seen.has('285:5'),'completeness');
const b=x?.baseline||{};
assert(b.historical_posts===61&&b.historical_external_refs===288&&b.external_researched===288,'frozen_cohort');
assert(b.expanded_posts===66&&b.expanded_inline_refs===361,'expanded_cohort');
assert(b.reported_broken_unverified===42&&b.guest_verified_broken===0,'no_guest_claim');
assert(b.claimed_wire_saving_pct===76&&b.measured_wire_saving_pct===null,'no_76_claim');
assert(b.originals_over_1500000_bytes===15&&b.oversized_stored_original_bytes===47096779,'stored_bytes');
const r=x?.release||{};
assert(r.siteqa_guest_browser_collector_owner===154,'no_duplicate_collector');
assert(r.original_priority_order?.join('|')==='285:5|285:2|287:5|418:1|418:2|407:1','p0_queue');
assert(r.no_upscale_max_width_px===960,'width_bound');
for(const k of ['wordpress_writes','homepage_writes','third_party_binary_downloads','subscription_spend_usd'])assert(r[k]===0,'no_change_'+k);
assert(r.any_live_change===false,'no_live_change');
return e;
}
module.exports={verify};

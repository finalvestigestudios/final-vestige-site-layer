'use strict';
const IDS=['RC09236','DGM0236','PR01070','K894127','K894293'];
const original='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg';
const isHttps=x=>typeof x==='string'&&/^https:\/\/[^/]+\/.+/.test(x);
function validate(a){
 const errors=[];
 const add=(ok,msg)=>{if(!ok)errors.push(msg);};
 add(a?.schema==='fv-fm-candidate-rights-and-retriever-separation-v1','schema');
 add(a?.published_original?.slot==='287:5'&&a.published_original.url===original,'original_custody');
 add(a?.published_original?.web_retriever_status_kind==='TOOL_WRAPPER_NOT_ORIGIN_HTTP'&&a.published_original.actual_guest_http_status===null&&a.published_original.actually_broken_in_guest_browser===false,'original_not_guest_confirmed');
 add(a?.policy?.source==='https://floridamemory.com/share/order-info/faq.php'&&a.policy.classification==='PUBLIC_DOMAIN_MARK_NOT_LICENSE','policy_provenance');
 add(a?.policy?.credit_source?.includes('257.35(6)')===true,'mandatory_credit');
 add(a?.same_publisher_moved_image?.rehosting_permission_verified===false&&a.same_publisher_moved_image.automatic_swap_allowed===false,'moved_image_not_cleared');
 const c=a?.official_catalog_candidates;
 add(Array.isArray(c)&&c.length===5,'five_candidates');
 if(Array.isArray(c)){
  add(new Set(c.map(x=>x?.id)).size===5&&IDS.every((id,i)=>c[i]?.id===id),'id_order_unique');
  for(const x of c){
   add(isHttps(x.catalog_url)&&isHttps(x.documented_image_url)&&x.documented_image_url.includes('floridamemory.com/'),'official_urls_'+x.id);
   add(x.latest_catalog_open_wrapper_code===403&&x.catalog_open_kind==='WEB_RETRIEVER_ERROR_NOT_GUEST_ORIGIN_HTTP'&&x.guest_http_status===null&&x.origin_http_status===null,'wrapper_not_http_'+x.id);
   add(x.policy_mark==='PDM_1_0_DECLARED_SITEWIDE'&&x.item_rights_review_needed_before_rehosting===true&&x.rehosting_authorized_by_this_audit===false,'rights_hold_'+x.id);
   add(x.photo_identity_same_as_original===false&&x.editorial_use==='DISCLOSED_DIFFERENT_PHOTO_ONLY_AFTER_REVIEW','scene_hold_'+x.id);
   add(x.conditional_max_output_width_px===960&&x.no_upscale===true&&x.derivative_dimensions_px===null&&x.official_image_native_width_px===null,'geometry_hold_'+x.id);
   add(x.download_performed===false&&x.visitor_wire_bytes===null,'no_binary_or_wire_'+x.id);
  }
 }
 add(a?.cohort?.historical_posts===61&&a.cohort.historical_image_slots===355&&a.cohort.historic_alleged_broken===42,'historical_cohort');
 add(a?.cohort?.large_original_count===15&&a.cohort.large_original_stored_bytes===47096779&&a.cohort.large_originals_inline_matched===11,'oversize_baseline');
 add(a?.cohort?.actual_wire_reduction_confirmed===false&&a.cohort.measured_cold_baseline_transfer_bytes===null&&a.cohort.measured_cold_candidate_transfer_bytes===null,'76_unverified');
 add(Object.entries(a?.disposition||{}).filter(([k])=>k.startsWith('no_')).every(([,v])=>v===true)&&a?.disposition?.staging_eligible===false&&a.disposition.site_qa_154_owns_guest_chrome===true,'no_write_qa_owned');
 return {ok:errors.length===0,errors};
}
module.exports={validate};

'use strict';
// Evidence lock: P0 publisher credit and official catalog are NOT guest browser proof.
const validate = function validate(x){
const errors=[],add=(c,e)=>{if(!c)errors.push(e)};
add(x?.schema==="fv-p0-2855-4181-publisher-to-primary-custody-v1","schema");
add(x?.observed_date==="2026-11-13","audit_date");
add(Array.isArray(x?.records)&&x.records.length===2,"two_records");
const r=Array.isArray(x?.records)?x.records:[];
const expected=[
{slot:"285:5",post_id:285,src:"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",wrapper:404,catalog:"https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg"},
{slot:"418:1",post_id:418,src:"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",wrapper:403,catalog:"https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/"}];
for(let i=0;i<expected.length;i++){
let e=expected[i],v=r[i];add(v?.slot===e.slot&&v?.post_id===e.post_id,`identity_${i}`);add(v?.published_src===e.src&&v?.retriever?.url===e.src,`published_src_${i}`);
add(v?.retriever?.tool_wrapper_code===e.wrapper&&v?.retriever?.date==="2026-11-13",`wrapper_${i}`);
add(v?.retriever?.origin_status===null&&v?.retriever?.guest_status===null,`unverified_http_${i}`);
add(v?.primary_credited_source?.catalog===e.catalog,`catalog_${i}`);
add(v?.published_source_last_wp_readback==="2026-11-08",`wp_readback_${i}`);
add(v?.derivative_plan?.max_width_px===960&&v?.derivative_plan?.no_upscale===true,`dimensions_gate_${i}`);
add(v?.derivative_plan?.allowed_to_render_or_upload===false&&v?.derivative_plan?.requires_crop_review===true,`image_hold_${i}`);
for(let field of ["browser_failure_confirmed","binary_match_confirmed","crop_parity_confirmed","rehost_cleared_for_this_change","downloaded","cache_written","wp_media_written","wp_post_written"])add(v?.release?.[field]===false,`${field}_${i}`);
}
const t=r[0]?.primary_credited_source,u=r[1]?.primary_credited_source;
add(t?.publisher_url==="https://discover.hubpages.com/entertainment/The-China-Syndrome-Blockbuster-Movie-Becomes-Eerie-Prophecy","publisher");
add(t?.publisher_credit_direct_file==="https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg","direct_credit");
add(t?.catalog_license==="PD-self"&&t?.catalog_author==="Marque1313","commons_rights");
add(t?.catalog_description_photo_date==="2010-06-06"&&t?.catalog_date_field==="2010-06-16","date_field_difference");
add(t?.subject==="2010_aerial_power_station_not_1979_accident_or_film_still","historical_subject");
add(JSON.stringify(t?.catalog_dimensions_px)==="[819,614]"&&t?.catalog_size_display==="235 KB","catalog_dims");
add(t?.same_underlying_image==="PUBLISHER_DIRECT_CREDIT_LINK_ESTABLISHED_BINARY_ORIGINAL_CROP_NOT_PROVEN","tmi_not_binary");
add(JSON.stringify(r[0]?.derivative_plan?.uncropped_possible_px)==="[819,614]"&&JSON.stringify(r[0]?.derivative_plan?.exact_sixteen_nine_crop_example_px)==="[816,459]","no_upscale_16_9");
add(r[0]?.derivative_plan?.published_transformation==="ar_16:9,c_fill,w_1200","published_transformation");
add(u?.virin==="210330-G-DE713-0002.JPG"&&u?.catalog_attribution==="U.S. Coast Guard","uscg_virin");
add(u?.catalog_rights==="PHOTO_PUBLIC_DOMAIN_CLEARED_FOR_RELEASE_CREDIT_AND_DOD_LIMITATIONS_APPLY"&&u?.catalog_download_size_display==="0.04 MB","uscg_item_release");
add(u?.subject==="USCG_service_portrait_Anthony_Pettit_not_lighthouse_wreckage","uscg_scene");
add(u?.catalog_dimensions_px===null&&r[1]?.derivative_plan?.uncropped_possible_px===null,"uscg_no_invented_dims");
add(u?.same_underlying_image==="VIRIN_AND_SOURCE_MATCH_CATALOG_ITEM_BINARY_NOT_PROVEN","uscg_not_binary");
const c=x?.controls;add(c?.siteqa_owner_pr===154&&c?.max_derivative_width_px===960&&c?.no_upscale===true,"ownership_and_sizing");
add(JSON.stringify(c?.p0_queue)==='["285:5","285:2","287:5","418:1","418:2","407:1"]',"original_priority");
add(c?.guest_broken_total===null&&c?.reported_broken_unconfirmed===42,"broken_claim_hold");
add(c?.proposed_wire_savings_percent===76&&c?.measured_wire_savings_percent===null,"wire_savings_not_measured");
add(c?.frozen_posts===61&&c?.frozen_inline_images===355&&c?.current_posts_last_census===66&&c?.current_inline_images_last_census===361,"source_denominator");
add(c?.oversized_originals_last_census===16&&c?.oversized_stored_bytes_last_census===49107665,"stored_bytes_not_wire");
add(c?.stage==="HOLD_BROWSER_VISUAL_RIGHTS"&&c?.third_party_downloads===0&&c?.wp_production_writes===0&&c?.homepage_changes===0&&c?.subscription_spend_usd===0,"no_public_write");
return {ok:errors.length===0,errors};
};
module.exports = { validate };

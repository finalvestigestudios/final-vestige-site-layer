'use strict';
/** Fail-closed source/rights custody guard. Offline, no downloads or WP calls. */
function validate(d){
 const errors=[];
 const fail=(code,test)=>{if(!test)errors.push(code);};
 const s=d?.sources;
 fail("schema",d?.schema==="fv-uscg-scotch-cap-p0-primary-custody-v1");
 fail("post_identity",d?.post?.id===418&&d?.post?.status==="publish"&&d?.post?.modified==="2026-08-28T03:11:08"&&d?.post?.url==="https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/");
 fail("two_unique_slots",Array.isArray(s)&&s.length===2&&new Set(s.map(x=>x?.slot)).size===2&&s[0]?.slot==="418:1"&&s[1]?.slot==="418:2");
 if(!Array.isArray(s)||s.length!==2) return {state:"INVALID",errors};
 const [p,debris]=s;
 fail("portrait_published_url",p?.published_source==="https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG");
 fail("portrait_published_copy",p?.published_alt==="Chief Boatswain’s Mate Anthony L. Petit, officer in charge of Scotch Cap Lighthouse when the 1946 tsunami killed its five-man crew."&&p?.published_caption==="Chief Boatswain’s Mate Anthony L. Petit. U.S. Coast Guard.");
 fail("portrait_primary_catalog",p?.archival_candidate?.catalog_url==="https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/"&&p?.archival_candidate?.identifier==="210330-G-DE713-0002.JPG");
 fail("portrait_exact_VIRIN_not_binary",p?.archival_candidate?.relation==="exact-VIRIN-filename-catalog-match-NOT-byte-or-crop-equality"&&p?.archival_candidate?.binary_hash_verified===false&&p?.archival_candidate?.exact_visual_parity_verified===false);
 fail("portrait_item_PD_assertion",p?.archival_candidate?.publisher_item_public_domain_assertion===true&&p?.archival_candidate?.publisher_item_cleared_for_release_assertion===true&&p?.archival_candidate?.publisher_republish_requires_credit_and_dod_guidance===true&&p?.archival_candidate?.rights_guidance_url==="https://www.dma.mil/Services/Visual-Information/References/Limitations/");
 fail("portrait_name_ambiguity",typeof p?.archival_candidate?.editorial_name_review==="string"&&p.archival_candidate.editorial_name_review.includes("both spellings")&&p.archival_candidate.editorial_name_review.startsWith("HOLD:")&&p.archival_candidate.catalog_description==="Service portrait of Anthony Pettit, Scotch Cap station chief");
 fail("debris_published_url",debris?.published_source==="https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg");
 fail("debris_published_copy",debris?.published_alt==="Broken concrete and debris where Scotch Cap Lighthouse stood after the April 1, 1946 tsunami."&&debris?.published_caption==="What remained at Scotch Cap after the tsunami. U.S. Coast Guard.");
 fail("debris_museum_catalog",debris?.archival_candidate?.catalog_url==="https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/"&&debris?.archival_candidate?.candidate_image_url==="https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg");
 fail("debris_cannot_inherit_PD",debris?.archival_candidate?.publisher_item_public_domain_assertion===false&&debris?.archival_candidate?.publisher_item_cleared_for_release_assertion===false&&debris?.archival_candidate?.rights_guidance_url===null);
 fail("debris_nominal_600px_not_native",JSON.stringify(debris?.archival_candidate?.advertised_rendition_px)==="[600,463]"&&debris?.archival_candidate?.actual_native_px===null);
 fail("debris_identity_HOLD",debris?.archival_candidate?.relation==="same-scene-and-filename-stem-not-pixel-or-licensing-proof"&&debris?.archival_candidate?.binary_hash_verified===false&&debris?.archival_candidate?.exact_visual_parity_verified===false);
 for(const o of s){
  const key=o?.slot||"unknown";
  fail("visitor_status_unknown:"+key,o?.origin_http_status===null&&o?.guest_http_status===null&&o?.guest_current_src===null&&o?.guest_natural_px===null&&o?.guest_encoded_transfer_bytes===null&&o?.verified_guest_broken===null);
  fail("wrapper_not_guest:"+key,o?.external_retriever?.date==="2026-11-14"&&o?.external_retriever?.method==="web.open"&&o?.external_retriever?.wrapper_status===403&&String(o?.external_retriever?.meaning).includes("NOT guest/origin"));
  fail("no_unapproved_localization:"+key,o?.archival_candidate?.derivative_max_width_px===960&&o?.archival_candidate?.conditional_output_px===null&&o?.archival_candidate?.actual_native_px===null&&o?.archival_candidate?.wp_localization_authorized===false);
 }
 const h=d?.historical_baseline;
 fail("baseline_not_visitors",h?.posts===61&&h?.inline_images===355&&h?.reported_broken_external===42&&h?.confirmed_guest_broken===null&&h?.claimed_visitor_wire_reduction_pct===76&&h?.actual_visitor_wire_reduction_pct===null&&h?.oversized_wordpress_origins===16&&h?.oversized_stored_original_bytes===49107665&&h?.oversize_threshold_decimal_bytes===1500000);
 const q=d?.qa_release;
 fail("all_release_holds",q?.state==="HOLD"&&q?.site_qa_owner_pr===154&&q?.await_guest_cdp_full_scroll===true&&q?.await_final_url_status_mime_cache_bytes===true&&q?.await_nat_css_px_and_dpr===true&&q?.await_exact_asset_hash_or_visual_comparison===true&&q?.await_item_rights_editorial_signoff===true&&q?.allow_image_download===false&&q?.allow_image_cache===false&&q?.allow_wordpress_write===false&&q?.allow_block_rewrite===false&&q?.allow_homepage_change===false&&q?.allow_merge===false&&q?.allow_paid_subscription===false&&q?.production_repairs===0);
 return {state:errors.length?"INVALID":"VALIDATED_HOLD",errors};
}
module.exports={validate};
if(require.main===module){
 const fs=require('node:fs');
 try{const q=JSON.parse(fs.readFileSync(process.argv[2]||require('node:path').join(__dirname,'uscg_scotch_cap_418_primary_custody_20261114.json'),'utf8'));
 const out=validate(q);process.stdout.write(JSON.stringify(out,null,2)+'\n');if(out.state!=='VALIDATED_HOLD')process.exitCode=2;}
 catch(e){console.error('INPUT_ERROR '+String(e.message||e));process.exitCode=2;}
}

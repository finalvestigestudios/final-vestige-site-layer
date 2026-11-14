'use strict';
// Read-only immutable audit validator. This does not probe visitor image HTTP or modify WordPress.
const fs=require('node:fs');
const path=require('node:path');
function verify(now,oldSix,oldMedia){
 const ok=(cond,msg)=>{if(!cond)throw Error(msg);};
 const keys=(obj,allowed,path)=>ok(Object.keys(obj).every(k=>allowed.includes(k)),path+": unexpected field");
 const M=now.metrics,P=now.policy;
 ok(now.schema==="fv-media-p0-p1-live-drift-readback-v1"&&now.observed_local_date==="2026-11-14","schema/date drift");
 ok(now.method==="READ_ONLY_WORDPRESS_EDIT_AND_MEDIA_LIST; NOT GUEST BROWSER OR ORIGIN HTTP","method");
 ok(now.source_evidence.previous_p0_git_blob==="04df35ce25f99626c7b754c1d7eed0f3f006e3f4"&&now.source_evidence.previous_media_git_blob==="689b7a4e3746f2c772058240bad7529223227c9a","prior committed evidence identity");
 ok(JSON.stringify(now.source_evidence.wordpress_posts_rechecked)==='[34,35,36,37,38,269,285,287,299,407,418,621]',"12 post readbacks");
 ok(M.historic_posts===61&&M.historic_inline_images===355&&M.previous_expanded_published_posts===66&&M.previous_expanded_inline_images===361,"cohorts");
 ok(Array.isArray(now.p0)&&now.p0.length===6&&M.p0_wp_sources_exactly_reconfirmed===6,"six source rows");
 const cats={"285:5":"https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg","285:2":"https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/","287:5":"https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/","418:1":"https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/","418:2":"https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/","407:1":"https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959"};
 let seen=new Set();
 for(let i=0;i<6;i++){
  const r=now.p0[i],o=oldSix.rows[i],c=r.candidate;
  ok(r.slot===o.slot&&r.post_id===o.post_id&&r.stored_src===o.published_src&&r.source_method==="authenticated_wordpress_edit_read","p0 source identity "+i);
  ok(r.slot.split(":")[0]===String(r.post_id)&&r.post_url===o.post_url&&r.raw_img_count>0&&r.post_modified&&typeof r.post_modified==="string","p0 post metadata "+i);
  ok(!seen.has(r.slot),"duplicate p0");seen.add(r.slot);
  ok(r.prior_web_wrapper.date==="2026-11-08"&&r.prior_web_wrapper.tool_status===o.wrapper.tool_status&&r.prior_web_wrapper.interpretation==="NOT_ORIGIN_OR_GUEST_BROWSER_HTTP","p0 wrapper provenance");
  ok(r.guest_http_status===null&&r.guest_natural_px===null&&r.guest_encoded_transfer_bytes===null&&r.guest_broken===null,"fabricated visitor status");
  ok(c.catalog_url===cats[r.slot]&&c.rights_to_rehost_verified===false&&c.exact_binary_and_crop_proven===false&&c.cache_approved===false&&c.wp_replacement_approved===false,"p0 rights and source gate");
  ok(c.native_width_px===null||Number.isInteger(c.native_width_px)&&c.native_width_px>0,"candidate dimensions");
  ok(c.conditional_max_width_px===(c.native_width_px===null?null:Math.min(960,c.native_width_px)),"p0 derivative no upscale");
  keys(c,["catalog_url","candidate_url","classification","native_width_px","conditional_max_width_px","rights_to_rehost_verified","exact_binary_and_crop_proven","cache_approved","wp_replacement_approved"],"p0 candidate");
 }
 ok(M.live_wp_image_library_items===123&&Array.isArray(now.oversized_originals)&&now.oversized_originals.length===16&&M.oversized_originals_gt_1500000===16,"16 large originals");
 const frozen=new Map(oldMedia.oversized_media.map(x=>[x.media_id,x])); let largeIDs=new Set(),sum=0,empty=[];
 for(let r of now.oversized_originals){
  const orig=frozen.get(r.media_id);ok(orig&&!largeIDs.has(r.media_id),"16 exact media IDs");largeIDs.add(r.media_id);
  ok(r.source_url===orig.source_url&&r.media_parent===orig.parent_content_id&&r.original_bytes===orig.original_stored_bytes,"media exact URL/bytes/parent "+r.media_id);
  ok(JSON.stringify(r.native_px)===JSON.stringify([orig.native_dimensions_px.width,orig.native_dimensions_px.height])&&r.wordpress_size_count===orig.wordpress_size_descriptors.length,"media dimensions/derivatives "+r.media_id);
  ok(r.original_bytes>1500000&&r.guest_http_status===null&&r.guest_encoded_transfer_bytes===null,"oversize not browser/wire measurement");
  ok(r.rights_reviewed===false&&r.approved_for_derivative===false&&r.no_upscale===true&&r.conditional_max_width_px===Math.min(960,r.native_px[0]),"oversize rights/no-upscale");
  ok((r.published_inline_post===null)||Number.isInteger(r.published_inline_post),"published link");
  sum+=r.original_bytes;if(r.wordpress_size_count===0)empty.push(r);
  keys(r,["media_id","source_url","media_parent","original_bytes","native_px","wordpress_size_count","published_inline_post","guest_http_status","guest_encoded_transfer_bytes","rights_reviewed","approved_for_derivative","conditional_max_width_px","no_upscale"],"oversize media");
 }
 ok(sum===49107665&&M.oversized_stored_original_bytes===sum,"storage totals not visitor bytes");
 ok(JSON.stringify(empty.map(r=>r.media_id))==="[39,40,41,42,43]"&&M.no_subsize_large_png_count===5&&M.no_subsize_large_png_original_stored_bytes===empty.reduce((a,r)=>a+r.original_bytes,0),"no subsize png");
 const postIDs=new Map([[39,34],[40,35],[41,36],[42,37],[43,38],[1714,269],[382,299],[388,299],[389,299],[1257,621],[1258,621]]);
 ok(now.published_inline_uses.length===11&&M.published_inline_oversized_refs===11,"published use count");
 let uIDs=new Set(),pageIDs=new Set(),inlineStored=0;
 for(let u of now.published_inline_uses){
  const m=now.oversized_originals.find(x=>x.media_id===u.media_id);
  ok(m&&postIDs.get(u.media_id)===u.post_id&&m.published_inline_post===u.post_id&&!uIDs.has(u.media_id),"published use asset/post binding");
  uIDs.add(u.media_id);pageIDs.add(u.post_id);
  ok(u.slot.startsWith(u.post_id+":")&&u.source_url===m.source_url&&typeof u.post_modified==="string","published use slot/meta");
  const direct=u.stored_img_src===m.source_url;
  const proxy=u.stored_img_src.startsWith("https://i0.wp.com/finalvestige.com"+m.source_url.replace("https://finalvestige.com","")+"?")&&u.stored_img_src.includes("fit=1024");
  ok(direct!==proxy&&u.src_method===(proxy?"FIRST_PARTY_JETPACK_FIT_1024":"DIRECT_ORIGINAL"),"exact src vs proxy");
  ok((u.post_id===299)===proxy,"Jetpack use limited to Vasa");
  inlineStored+=m.original_bytes;
 }
 ok(pageIDs.size===8&&M.published_inline_oversized_post_count===8&&M.published_inline_original_stored_bytes===inlineStored&&inlineStored===38480915,"published storage exposure");
 ok(now.oversized_originals.find(x=>x.media_id===2432).published_inline_post===null&&M.draft_media_id===2432&&M.draft_media_original_bytes===2010886,"draft not published article");
 ok(M.reported_42_broken_guest_confirmed===null&&M.claimed_76_pct_network_reduction_measured===null&&M.measured_guest_wire_bytes===null,"42/76 unmeasured");
 ok(P.max_conditional_derivative_width_px===960&&P.no_upscale===true&&P.source_scene_crop_review_required===true&&P.item_rights_and_credit_required===true&&P.cold_uncached_guest_browser_required===true&&P.css_width_dpr_and_maps_legibility_required===true,"quality gate");
 ok(P.media_download_cache_authorized===false&&P.wordpress_production_write_authorized===false&&P.homepage_design_write_authorized===false&&P.merge_deploy_authorized===false&&P.subscription_spend_usd===0&&P.site_qa_browser_collector_pr===154,"release and Site QA custody gate");
 keys(P,["max_conditional_derivative_width_px","no_upscale","source_scene_crop_review_required","item_rights_and_credit_required","cold_uncached_guest_browser_required","css_width_dpr_and_maps_legibility_required","media_download_cache_authorized","wordpress_production_write_authorized","homepage_design_write_authorized","merge_deploy_authorized","subscription_spend_usd","site_qa_browser_collector_pr"],"policy");
 return {ok:true,p0:6,oversized:16,published:11,stored_bytes:sum,inline_stored_bytes:inlineStored};
}
module.exports={verify};
if(require.main===module){
 try{
 const here=__dirname;
 const audit=JSON.parse(fs.readFileSync(path.join(here,'p0_p1_wp_live_readback_20261114.json'),'utf8'));
 const p0=JSON.parse(fs.readFileSync(path.join(here,'p0_six_live_source_retriever_20261108.json'),'utf8'));
 const large=JSON.parse(fs.readFileSync(path.join(here,'wp_123_media_16_draft_20261113.json'),'utf8'));
 console.log(JSON.stringify(verify(audit,p0,large)));
 }catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}
}

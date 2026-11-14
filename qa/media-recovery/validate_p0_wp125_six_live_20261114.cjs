'use strict';
// Read-only frozen-source audit. No WordPress writes, network requests, or asset copying.
const fs=require('node:fs');
const path=require('node:path');
function validate(d){
 const errs=[],bad=(x)=>errs.push(x);const expected={"285:5":"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg","285:2":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","287:5":"https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg","418:1":"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG","418:2":"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg","407:1":"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg"};
 const sizes={"39":2892087,"40":2552136,"41":2498247,"42":2488823,"43":2836245,"293":2090327,"382":2318980,"388":8176362,"389":2822969,"405":2201573,"482":2293016,"1257":4798395,"1258":5553669,"1714":1543002,"2148":2030948,"2432":2010886};
 if(d?.schema!=="fv-live-wp125-p0-six-recovery-readback-v1")bad("schema");
 if(d?.method?.includes("read-only")!==true)bad("source_method");
 if(Object.keys(d?.posts||{}).sort().join()!=="285,287,407,418")bad("post_list");
 for(const [id,expectedN] of [["285",6],["287",6],["407",8],["418",6]]){
  const p=d.posts?.[id];if(!p||p.status!=="publish"||p.inline_images!==expectedN||!/^https:\/\/finalvestige\.com\//.test(p.url||"")||!p.modified)bad("post_custody:"+id);
 }
 const rows=d?.source_slots||[];if(rows.length!==6||new Set(rows.map(x=>x.slot)).size!==6)bad("six_unique_slots");
 for(const [slot,url] of Object.entries(expected)){
  const x=rows.find(r=>r.slot===slot);if(!x||x.published_source!==url||x.post_id!==Number(slot.split(":")[0])||!x.alt?.length||!x.caption?.length)bad("published_image_drift:"+slot);
  const s=x?.source_status;if(!s||s.retriever_method!=="web.open"||s.retriever_date!=="2026-11-14"||![400,403,404,500].includes(s.retriever_wrapper_code)||["origin_http_status","guest_http_status","guest_current_src","guest_transfer_bytes","guest_intrinsic_dimensions","guest_broken"].some(k=>s[k]!==null))bad("unverified_evidence_promoted:"+slot);
 }
 const c=d?.asset_candidates||[];if(c.length!==7||new Set(c.map(x=>x.slot)).size!==6)bad("candidate_inventory");
 for(const x of c){if(!expected[x.slot]||!x.catalog_url?.startsWith("https://")||x.reuse_approved!==false||typeof x.relationship!=="string"||x.relationship.length<20||typeof x.rights!=="string")bad("candidate_custody:"+x.slot);if(x.native_px!==null){const [w,h]=x.native_px||[],[rw,rh]=x.max_960_no_upscale_px||[];if(!(w>0&&h>0&&rw>0&&rh>0&&rw<=Math.min(w,960)&&rh<=h&&Math.abs(rh/rw-h/w)<.004))bad("illegal_960_geometry:"+x.slot);}}
 const mm=d?.wp_media||{},os=mm.oversized_origins||[];
 if(mm.image_attachments_total!==125||mm.strict_decimal_gt_bytes!==1500000||mm.oversized_count!==16||os.length!==16||new Set(os.map(x=>x.id)).size!==16||mm.visitor_network_bytes!==null)bad("media_census");
 let total=0;for(const x of os){if(sizes[String(x.id)]!==x.bytes||x.bytes<=1500000||x.dimensions_px?.length!==2||x.dimensions_px.some(v=>v<=0)||!x.url?.startsWith("https://finalvestige.com/wp-content/uploads/"))bad("oversize_drift:"+x.id);total+=x.bytes;}
 if(total!==49107665||mm.oversized_stored_bytes!==total)bad("stored_byte_total");
 const h=d?.historical_baseline||{};if(h.frozen_published_posts!==61||h.frozen_inline_images!==355||h.reported_broken_originals!==42||h.confirmed_guest_broken!==null||h.claimed_76_percent_wire_savings_measured!==false||h.measured_savings_percent!==null)bad("historical_vs_measured");
 const g=d?.release||{};if(g.all_candidates_hold!==true||g.source_identity_verified!==false||g.item_rights_cleared!==false||g.editorial_approval!==false||g.guest_browser_test_required!==true||g.qa_owner_pr!==154||g.maximum_derivative_width!==960||g.no_upscale!==true||g.cache_or_download_allowed!==false||g.wp_production_write_allowed!==false||g.homepage_changes_allowed!==false||g.merges_allowed!==false||g.subscriptions_usd!==0)bad("release_gate");
 return {ok:errs.length===0,errors:errs};
}
module.exports={validate};
if(require.main===module){const src=process.argv[2]||path.join(__dirname,'p0_wp125_six_live_20261114.json');const out=validate(JSON.parse(fs.readFileSync(src,'utf8')));console.log(JSON.stringify(out,null,2));if(!out.ok)process.exitCode=1;}

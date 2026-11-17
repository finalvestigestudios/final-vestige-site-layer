'use strict';
// Read-only custody gate; no network fetch, WordPress writes or file conversion.
function validate(doc,part,viewer){
 const errors=[],check=(v,m)=>{if(!v)errors.push(m)};
 try{
 const originals=part.images.filter(x=>x.post_id===407).sort((a,b)=>a.slot-b.slot);
 const observations=viewer.observations.filter(x=>x.post_id===407);
 const s=doc.summary||{};
 check(doc.schema_version===1&&doc.post.id===407&&doc.post.status==='publish'&&doc.post.source_and_alt_matches===8&&doc.post.url===originals[0]?.post_url,'post');
 check(doc.source_ledger.path==='qa/media-recovery/parts/02.json'&&doc.viewer_ledger.path==='qa/media-recovery/source_viewer_25slot_20261031.json','sources');
 check(originals.length===8&&observations.length===8&&Array.isArray(doc.images)&&doc.images.length===8,'counts');
 check(s.slots===8&&s.external===8&&s.usgs_records===8&&s.exact_usgs_original_url_matches===3&&s.official_alternative_image_url_candidates===1&&s.viewer_rendered_current_url===6&&s.viewer_inconclusive_current_url===2&&s.confirmed_visitor_broken===null&&s.claimed_42_broken_proven===false&&s.measured_image_weight_reduction_percent===null&&s.claimed_76_percent_proven===false&&s.production_repaired===0&&s.site_posts===61&&s.site_image_refs===355&&s.site_external_refs===288&&s.oversized_wp_media_originals===13,'no_unverified_42_or_76_or_wire_weight');
 const slugs=["earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau","hebgen-lake-fault-scarp-1959","view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake","dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959","rockslide-damage-golden-gate-area-near-mammoth-hot-springs","sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg","seismic-geyser-eruption-1970","earthquake-lake-and-madison-slide"];
 const alt="https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg";
 for(let i=0;i<8;i++){
 const x=doc.images[i]||{},b=originals[i]||{},v=observations.find(z=>z.image_key===b.key)||{};
 check(x.key===b.key&&x.slot===i&&x.exact_url===b.source_url&&x.exact_alt===b.alt&&x.source_kind===b.source_kind,'identity_'+i);
 const a=x.archive||{},c=x.candidate||{},w=x.viewer||{},q=x.browser||{},g=x.geometry||{},r=x.release||{};
 check(a.record_url==='https://www.usgs.gov/media/images/'+slugs[i]&&a.credit===r.credit&&typeof a.note==='string'&&a.note.length>15&&a.public_domain_mark_on_record===true&&a.exact_original_link_matches_published_url===[4,5,6].includes(i)&&a.binary_match_verified===false&&a.master_sha256===null,'catalog_'+i);
 check(c.url===(i===1?alt:b.source_url)&&c.is_alternative===(i===1)&&c.official_original_viewer_rendered===(i===1?true:null)&&c.identity_verified_by_hash===false,'candidate_'+i);
 check(w.method==='independent_web_retriever_not_guest_browser'&&w.result===v.viewer_result&&w.reported_mime===(v.viewer_reported_content_type||null)&&w.http_status===null,'viewer_'+i);
 check(Object.keys(q).sort().join(',')==='broken,content_type,encoded_image_bytes,final_current_src,http_status,natural_height,natural_width'&&Object.values(q).every(z=>z===null),'guest_http_and_wire_'+i);
 const tw=b.width_px?Math.min(960,b.width_px):null;
 const expected=tw?{width:tw,height:Math.round(b.height_px*tw/b.width_px)}:null;
 check(g.html_stored_width===b.width_px&&g.html_stored_height===b.height_px&&g.verified_binary_width===null&&g.verified_binary_height===null&&JSON.stringify(g.conditional_960_dimensions)===JSON.stringify(expected)&&g.max_width===960&&g.never_upscale===true&&g.preserve_aspect_ratio===true,'geometry_'+i);
 check(r.item_specific_rights==='HOLD'&&r.binary_match_required===true&&r.wp_media_id===null&&r.wordpress_upload_authorized===false&&r.wordpress_post_edit_authorized===false&&r.visual_QA_complete===false,'rights_'+i);
 }
 check(doc.images[2]?.archive.credit.includes('William B. Hall')&&doc.images[3]?.archive.credit.includes('Mrs. Steven W. Nile')&&doc.images[6]?.archive.photograph_date==='1970'&&doc.images[7]?.archive.photograph_date==='2023-06-27','chronology_credit');
 const p=doc.cache_plan||{};
 check(p.status==='HOLD'&&p.auto_scraping===false&&p.production_wp_writes===false&&p.subscription_spend_usd===0&&p.steps?.length>=5,'release_gate');
 }catch(e){errors.push('malformed:'+e.message)}
 return {ok:errors.length===0,errors};
}
module.exports={validate};

'use strict';
const fs=require('node:fs');
const expectedIds=["PR04493","RC17068","RC10673","N031889","RC04344","RC07668","MSF-PB11548-001"];
const expectedCatalogs=["https://floridamemory.com/items/show/4144","https://www.floridamemory.com/items/show/38362","https://www.floridamemory.com/items/show/33289","https://floridamemory.com/items/show/141398","https://floridamemory.com/items/show/27848","https://floridamemory.com/items/show/30741","https://floridamemory.com/items/show/340182"];
const expectedUrls=["https://www.floridamemory.com/fpc/prints/pr04493.jpg","https://www.floridamemory.com/fpc/reference/rc17068.jpg","https://www.floridamemory.com/fpc/reference/rc10673.jpg","https://www.floridamemory.com/fpc/general/n031889.jpg","https://www.floridamemory.com/fpc/reference/rc04344.jpg","https://www.floridamemory.com/fpc/reference/rc07668.jpg","https://www.floridamemory.com/fpc/msf/MSF-PB11548-001.jpg"];
const expectedViews=["https://i0.wp.com/www.floridamemory.com/fpc/prints/pr04493.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/reference/rc17068.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/reference/rc10673.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/general/n031889.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/reference/rc04344.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/reference/rc07668.jpg?ssl=1","https://i0.wp.com/www.floridamemory.com/fpc/msf/MSF-PB11548-001.jpg?ssl=1"];
function validate(d){
 let errors=[],bad=(x)=>errors.push(x);
 if(d?.schema!=="fv-media-okeechobee432-seven-primary-v1"||d.captured_on!=="2026-11-17")bad("schema/date");
 const p=d?.provenance||{};
 if(p.source_ledger_path!=="qa/media-recovery/primary_rights_11slot_crosscheck_20261116.json"||p.source_ledger_blob_sha!=="c6f34b00e4173d7ce2247b351695ed1ff39688f5"||!p.source_method?.includes("EDIT/VIEW")||!p.catalog_method?.includes("search-index")||p.guest_browser_method!==null||p.site_qa_owner!=="PR #154 existing guest Chrome collector")bad("provenance/method");
 const b=d?.baselines||{};
 if(b.historical_posts!==61||b.historical_images!==355||b.reported_broken!==42||b.confirmed_broken!==null||b.claimed_savings_percent!==76||b.measured_savings_percent!==null||b.oversized_wordpress_original_count!==20||b.oversized_original_stored_bytes!==64385752||b.guest_transferred_bytes!==null)bad("false census/network assertion");
 const rights=d?.rights||{};
 if(rights.primary_collection!=="State Archives of Florida / Florida Memory"||rights.policy_url!=="https://floridamemory.com/share/order-info/faq.php"||!rights.mark?.includes("not a new license")||rights.credit!=="State Archives of Florida, Florida Memory; individual creator where supplied"||rights.review_required!==true)bad("rights");
 if(!Array.isArray(d?.items)||d.items.length!==7)bad("seven slots");
 else for(let i=0;i<7;i++){
  const a=d.items[i],k=`432:${i}`;
  if(a.key!==k||a.wp_modified!=="2026-08-28T03:07:30"||a.post_url!=="https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/")bad("slot/revision "+k);
  if(a.authored_url!==expectedUrls[i]||a.primary_original_route!==expectedUrls[i]||a.published_view_url!==expectedViews[i]||!a.published_view_url.startsWith("https://i0.wp.com/"))bad("source/view route "+k);
  if(a.primary_accession!==expectedIds[i]||a.primary_catalog_url!==expectedCatalogs[i]||a.original_route_relation!=="EXACT_CATALOG_IMAGE_PATH_STRING_NO_BINARY_HASH"||a.identity!=="MATCHED_ARCHIVAL_CATALOG")bad("catalog identity "+k);
  if(!a.stored_alt||!a.catalog_scene||!a.editorial_note||a.catalog_date!==(i===1?"1928-09":i===6?"2001":"1928"))bad("caption/chronology "+k);
  if(i===3&&!a.editorial_note.includes("not evidenced"))bad("health chronology overclaim");if(i===6&&!a.editorial_note.includes("2001"))bad("2001 photo chronology");
  if(a.catalog_observation!=="INDEXED_OFFICIAL_TEXT_NOT_HTTP_IMAGE"||a.catalog_http_status!==null||a.origin_http_status!==null)bad("unsupported HTTP "+k);
  if(!a.guest||Object.values(a.guest).some(v=>v!==null))bad("fabricated visitor observations "+k);
  const g=a.geometry||{};
  if(g.native_width!==null||g.native_height!==null||g.proposed_width!==null||g.proposed_height!==null||g.max_width!==960||g.no_upscale!==true)bad("fabricated image dimensions "+k);
  const c=a.clearance||{};
  if(c.item_rights_approved!==false||c.credit_review_approved!==false||c.same_frame_verified!==false||c.binary_sha256!==null||c.wordpress_rehost_approved!==false||a.decision!=="HOLD_GUEST_RIGHTS_BINARY_AND_CROP")bad("unsafe clearance "+k);
 }
 const s=d?.safeguards||{};
 if(s.browser_collector_duplicated!==false||s.wordpress_production_writes!==0||s.image_binary_downloads!==0||s.media_rehosts!==0||s.homepage_design_changes!==0||s.gutenberg_rewrites!==0||s.subscription_spend_usd!==0||s.merge_or_deploy!==false||s.decision!=="HOLD")bad("unsafe operations");
 return {ok:errors.length===0,errors,release:"HOLD",slots:d?.items?.length??null};
}
module.exports={validate};
if(require.main===module){const data=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/'+"okeechobee432_seven_catalog_crosswalk_20261117_0033pt.json",'utf8'));const result=validate(data);console.log(JSON.stringify(result,null,2));process.exitCode=result.ok?0:1;}

"use strict";
const ids=["PR04493","RC17068","RC10673","N031889","RC04344","RC07668","MSF-PB11548-001"];
const paths=["/fpc/prints/pr04493.jpg","/fpc/reference/rc17068.jpg","/fpc/reference/rc10673.jpg","/fpc/general/n031889.jpg","/fpc/reference/rc04344.jpg","/fpc/reference/rc07668.jpg","/fpc/msf/MSF-PB11548-001.jpg"];
const nums=[4144,38362,33289,141398,27848,30741,340182],dates=["1928","1928-09","1928","1928","1928","1928","2001"];
function pathOf(s){let a=String(s).split("://");return a.length===2?"/"+a[1].split("/").slice(1).join("/").split("?")[0]:"";}
function validate(x){
 let errors=[],bad=s=>errors.push(s);
 if(!x||x.schema!=="fv-florida-seven-link-audit-v1")return ["schema"];
 if(x.post?.id!==432||x.post?.status!=="publish"||x.post?.url!=="https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/"||x.previous_manifest_sha!=="948bc1b65b42799aa40cfdb810ddf6ffd80886b6")bad("baseline");
 let m=x.summary||{},policy=x.policy||{};
 if(m.slots!==7||m.exact_catalog_paths!==7||m.legacy_link_targets!==3||m.editorial_alt_issue!==1||m.dated_2001_photo!==1||x.rows?.length!==7||m.visitor_broken_total!==null||m.image_transfer_savings_percent!==null)bad("metrics");
 if(policy.wp_writes!==false||policy.third_party_caching!==false||policy.third_party_downloads!==false||policy.rights_review_required!==true||policy.preview_max_width!==960||policy.no_upscale!==true)bad("policy");
 let legacy=0;
 for(let i=0;i<(x.rows||[]).length;i++){
  const r=x.rows[i],tag="slot"+i;if(!r){bad(tag);continue}
  if(r.slot!=="432:"+i||r.article_url!==x.post.url||r.published_alt!==undefined&&!r.published_alt)bad(tag+":identity");
  if(r.published_source_url!=="https://www.floridamemory.com"+paths[i])bad(tag+":src");
  let c=r.official_catalog||{};
  if(c.id!==ids[i]||c.url!=="https://floridamemory.com/items/show/"+nums[i]||c.title?.length<8||c.date!==dates[i]||c.record_image_path!==paths[i]||c.catalog_search_verified!==true||c.catalog_http_status!==null||c.original_binary_match!==null)bad(tag+":catalog");
  const exact=pathOf(r.published_anchor_url)==="/items/show/"+nums[i];
  if(r.deep_link_status!==(exact?"EXACT_ITEM_LINK":"LEGACY_GENERIC_LINK"))bad(tag+":anchor");
  if(!exact)legacy++;
  if(r.editorial_review!==(i===3?"REMOVE_UNSUPPORTED_HURRICANE_RESPONSE_TIMING":i===6?"2001_SITE_PHOTO_NOT_1928_EVENT":"NONE"))bad(tag+":editorial");
  for(let key of ["guest_http_status","guest_natural_width","guest_current_src","visitor_broken","origin_http_status","transfer_bytes"])if(r.evidence?.[key]!==null)bad(tag+":fabricated:"+key);
  const g=r.geometry||{},rights=r.rights||{},act=r.actions||{};
  if(g.native_width!==null||g.native_height!==null||g.target_max_width!==960||g.output_dimensions!==null||g.no_upscale!==true)bad(tag+":dimensions");
  if(rights.status!=="REVIEW_ITEM_LEVEL"||rights.may_cache!==false||rights.may_rehost!==false||!rights.credit?.includes(ids[i]))bad(tag+":rights");
  for(let key of ["image_downloaded","wordpress_written","third_party_cached","publication","paid"])if(act[key]!==false)bad(tag+":writes");
 }
 if(legacy!==3)bad("link-count");
 return errors;
}
module.exports={validate};

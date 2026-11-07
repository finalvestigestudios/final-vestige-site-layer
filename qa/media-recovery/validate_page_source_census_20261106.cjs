"use strict";
// Offline, fail-closed WordPress source-markup census. Never probes, uploads or rewrites images.
const expected={pages:83,images:20,distinct:17,external:8,withoutDimensions:10};
function classifyOrigin(src){
 const m=typeof src==="string"&&src.match(/^https?:\/\/([^/?#]+)(\/[^?#]*)?/i);
 if(!m)return src?"non_http":"missing_src";
 const h=m[1].toLowerCase(),p=m[2]||"";
 if(h==="finalvestige.com"||h==="www.finalvestige.com")return"first_party";
 if(h.endsWith(".wp.com")&&p.startsWith("/finalvestige.com/"))return"first_party_jetpack";
 if(h==="commons.wikimedia.org")return"commons_redirect";
 if(h==="upload.wikimedia.org")return"commons_direct";
 if(h==="awin1.com"||h==="www.awin1.com")return"affiliate_dynamic";
 if(h==="drive.google.com")return"google_drive_thumbnail";
 return"external_origin";
}
function validatePages(shards){
 const errors=[],pages=[],images=[],seenPages=new Set(),seenSlots=new Set();
 if(!Array.isArray(shards)||shards.length!==7)return{ok:false,errors:["Require exactly seven census shards"]};
 shards.forEach((sh,s)=>{
  const offset=12*s,size=s===6?11:12;
  if(sh?.schema!=="fv-page-source-image-shard-v1")errors.push("Invalid shard schema "+s);
  if(sh?.page_list_count!==83||sh?.offset!==offset||sh?.page_rows!==size)errors.push("Incomplete/shifted shard "+s);
  if(!Array.isArray(sh?.rows)||sh.rows.length!==size||!Array.isArray(sh?.errors)||sh.errors.length!==0)errors.push("Missing/error page rows "+s);
  if(sh?.reported_42_broken_browser_verified!==null||sh?.measured_76_percent_saving!==null||sh?.production_writes!==0)errors.push("Unsupported claim/write "+s);
  for(const p of sh?.rows||[]){
   if(!Number.isInteger(p.id)||seenPages.has(p.id))errors.push("Duplicate or invalid page ID");
   seenPages.add(p.id);
   if(p.error||p.status!=="publish"||typeof p.url!=="string"||!/^https:\/\/finalvestige\.com\//.test(p.url)||!Array.isArray(p.images))errors.push("Invalid publication "+p.id);
   pages.push(p);
   (p.images||[]).forEach((im,i)=>{
    const slot=p.id+":"+i;
    if(im.slot!==slot||seenSlots.has(slot))errors.push("Invalid image slot "+slot);
    seenSlots.add(slot);
    if(typeof im.src!=="string"||!/^https:\/\//.test(im.src)||classifyOrigin(im.src)!==im.source_class)errors.push("Unverifiable source URL/class "+slot);
    for(const dim of ["width","height"])if(im[dim]!==null&&(!Number.isInteger(im[dim])||im[dim]<=0))errors.push("Invalid stored dimension "+slot);
    if(im.browser_status!==null||im.natural_width!==null||im.wire_bytes!==null)errors.push("Invented browser observation "+slot);
    if(im.reuse_rights!=="HOLD"||im.wp_write_authorized!==false)errors.push("Premature publishing/rights "+slot);
    images.push(im);
   });
  }
 });
 const distinct=new Set(images.map(x=>x.src)).size, external=images.filter(x=>!["first_party","first_party_jetpack"].includes(x.source_class)).length, withoutDimensions=images.filter(x=>x.width===null||x.height===null).length;
 if(pages.length!==expected.pages||seenPages.size!==expected.pages)errors.push("Page cohort incomplete");
 if(images.length!==expected.images||distinct!==expected.distinct||external!==expected.external||withoutDimensions!==expected.withoutDimensions)errors.push("Image count/source coverage drift");
 return{ok:errors.length===0,errors,summary:{pages:pages.length,pages_with_inline:pages.filter(p=>p.images.length).length,images:images.length,distinct_src:distinct,offsite_sources:external,without_declared_dimensions:withoutDimensions}};
}
module.exports={validatePages,classifyOrigin};

#!/usr/bin/env node
'use strict';
// Offline audit consumer only; no site requests, downloads, publishing, or rights inference.
function validateAudit(a){
 const fail=s=>{throw new Error(s)};
 const obj=x=>!!x&&typeof x==="object"&&!Array.isArray(x);
 const positiveOrNull=x=>x===null||(Number.isSafeInteger(x)&&x>0);
 if(!obj(a)||a.schema!=="fv-media-twelve-post-live-view-crosswalk-v1"||a.audit_date!=="2026-11-17"||!obj(a.summary)||!obj(a.site_publish_inventory))fail("schema");
 const s=a.summary, inv=a.site_publish_inventory;
 if(s.current_published_posts!==66||s.full_view_posts!==12||s.selected_view_images!==77||inv.published_posts!==66||inv.complete_page!==true)fail("coverage");
 if(!Array.isArray(inv.ids_and_modified)||inv.ids_and_modified.length!==66||new Set(inv.ids_and_modified.map(p=>p.id)).size!==66||inv.ids_and_modified.some(p=>!Number.isSafeInteger(p.id)||!/^https:\/\//.test(p.link)||!p.modified))fail("post metadata");
 if(!Array.isArray(a.posts)||a.posts.length!==12||new Set(a.posts.map(p=>p.id)).size!==12)fail("selected posts");
 const expectedIds=[213,268,285,287,291,292,299,407,418,432,434,1926];
 if(expectedIds.some(id=>!a.posts.some(p=>p.id===id)))fail("post identity");
 const byId=new Map(inv.ids_and_modified.map(p=>[p.id,p])),seen=new Set(),kinds={},hosts=new Set();let count=0,missing=0;
 for(const p of a.posts){
  if(!byId.has(p.id)||p.modified!==byId.get(p.id).modified||p.url!==byId.get(p.id).link||!Array.isArray(p.images))fail("live revision/link");
  for(let slot=0;slot<p.images.length;slot++){
   const x=p.images[slot];if(!obj(x)||x.key!==`${p.id}:${slot}`||seen.has(x.key))fail("slot key");seen.add(x.key);count++;
   if(typeof x.published_src!=="string"||!/^https:\/\//.test(x.published_src)||/[<>]/.test(x.published_src))fail("source URL");
   const m=x.published_src.match(/^https:\/\/([^/?#]+)(\/[^?#]*)?/i);
   if(!m||m[1].includes("@"))fail("URL authority");
   const h=m[1].toLowerCase(),path=m[2]||"/";let family,host,hint;
   if(/^i[0-3]\.wp\.com$/.test(h)){
    const z=path.match(/^\/([^/]+)(\/.*)?$/);if(!z)fail("Jetpack path");host=z[1].toLowerCase();
    family=/^(www\.)?finalvestige\.com$/.test(host)?"first_party_jetpack":"external_jetpack";
    hint=`https://${host}${z[2]||"/"}`;
   }else {host=h;family=/^(www\.)?finalvestige\.com$/.test(host)?"first_party":"external_direct";hint=x.published_src}
   if(x.delivery_family!==family||x.underlying_host!==host||x.inferred_origin_url_not_verified!==hint)fail("proxy attribution");
   if(x.guest_http_status!==null||x.guest_decoded!==null||x.guest_natural_size!==null||x.guest_transferred_bytes!==null)fail("fabricated browser evidence");
   if(x.rights_for_copying_approved!==false||x.allowed_max_derivative_width_px!==960)fail("rights/no-upscale");
   if(!positiveOrNull(x.width_attribute_px)||!positiveOrNull(x.height_attribute_px)||typeof x.has_srcset!=="boolean"||typeof x.has_sizes!=="boolean")fail("markup geometry");
   if(x.width_attribute_px===null||x.height_attribute_px===null)missing++;
   kinds[family]=(kinds[family]||0)+1;hosts.add(host);
  }
 }
 if(count!==77||missing!==s.missing_explicit_width_or_height||missing!==61)fail("image counts");
 for(const [k,v] of Object.entries({external_jetpack:57,external_direct:11,first_party_jetpack:9}))if(kinds[k]!==v||s.image_families[k]!==v)fail("source family count");
 if(Object.keys(kinds).length!==3||s.distinct_underlying_hosts!==hosts.size||hosts.size!==35)fail("host count");
 const p0=["285:5","285:2","287:5","418:1","418:2","407:1"];
 if(!Array.isArray(s.p0_keys)||s.p0_keys.length!==6||p0.some(k=>!s.p0_keys.includes(k)||!seen.has(k)))fail("P0 identity");
 if(s.guest_broken_42_confirmed!==null||s.sitewide_76_percent_verified!==false||s.originals_over_1_5m_historical!==20||s.stored_bytes_over_1_5m_historical!==64385752)fail("historical claim gate");
 return {status:"HOLD_GUEST_BROWSER_AND_RIGHTS",posts:12,images:77,external:68,missing_markup_dimensions:61,hosts:35,confirmed_broken_images:null,measured_bandwidth_savings:null};
}
module.exports={validateAudit};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 try {const x=JSON.parse(fs.readFileSync(path.join(__dirname,'live_twelve_post_view_crosswalk_20261117_1026pt.json'),'utf8'));process.stdout.write(JSON.stringify(validateAudit(x),null,2)+'\n');}
 catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}
}

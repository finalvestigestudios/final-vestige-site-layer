'use strict';
function origin(src){if(typeof src!=="string")return"missing";const m=/^https?:\/\/([^/:?#]+)/i.exec(src);if(!m)return"non_http";const h=m[1].toLowerCase();if(h==="finalvestige.com"||h==="www.finalvestige.com")return"first_party";if(/^i[0-3]\.wp\.com$/.test(h)&&/^https?:\/\/[^/]+\/finalvestige.com\//i.test(src))return"first_party_proxy";if(h==="i.ytimg.com")return"youtube";if(h.endsWith("wikimedia.org"))return"wikimedia";if(h==="www.awin1.com")return"affiliate";if(h==="drive.google.com")return"google_drive";return"other_external";}
function verify(d){
 const errors=[],ids=new Set(),slots=new Set(),imgs=[],groups={};const bad=x=>errors.push(x);
 if(!Array.isArray(d)||d.length!==7)return{ok:false,errors:["missing_7_source_files"]};
 const locked={"78:2":"https://us.suunto.com/cdn/shop/files/SS014891000-Suunto-MC-2-G-USGS-MIRROR-COMPASS-perspective-view-01_297f0046-bf9a-4f3c-893c-ad50a6346ef9.png?v=1778238838&width=1390","78:3":"https://www.awin1.com/cshow.php?s=4959313&v=46005&q=620613&r=3055117"};
 for(let k=0;k<6;k++){
  const b=d[k],n=k===5?4:15;
  if(b.schema!=="fv-published-pages-79-complement-v1"||b.batch!==k+1||b.checked!==n||b.expected!==n||b.rows.length!==n||b.errors.length)bad("batch_"+(k+1));
  if(b.guest_http_verified!==false||b.claimed_42_broken_verified!==false||b.claimed_76_percent_wire_savings_verified!==false||b.rights_and_cache_hold!==true)bad("batch_unverified_"+(k+1));
  for(const p of b.rows){
   if(ids.has(p.id)||p.id===6||p.status!=="publish")bad("page_identity_"+p.id);ids.add(p.id);
   if(p.inline_images!==p.images.length)bad("page_count_"+p.id);
   for(let j=0;j<p.images.length;j++){
    const x=p.images[j],key=p.id+":"+j,kind=origin(x.src);
    if(x.slot!==key||slots.has(key))bad("slot_"+key);slots.add(key);
    if(x.origin!==kind||Object.prototype.hasOwnProperty.call(locked,key)&&x.src!==locked[key])bad("source_custody_"+key);
    if(x.guest_status!==null||x.guest_current_src!==null||x.guest_bytes!==null||x.guest_decoded_px!==null)bad("invented_browser_"+key);
    if(x.rights_cleared!==false||x.cache_authorized!==false||x.wp_write_authorized!==false)bad("unsafe_action_"+key);
    imgs.push(x);groups[kind]=(groups[kind]||0)+1;
   }
  }
 }
 const pilot=d[6];
 if(pilot.schema!=="fv-published-pages-media-source-pilot-v1"||pilot.pages_scanned!==12||pilot.images_found!==49||pilot.guest_browser_tested!==false||pilot.confirmed_browser_broken_images!==null||pilot.visitor_wire_bytes!==null||pilot.claimed_76_percent_wire_reduction_not_measured!==true)bad("pilot_claim");
 for(const p of pilot.rows){
  if(ids.has(p.id)||p.id===6)bad("pilot_overlap_"+p.id);ids.add(p.id);
  if(p.image_count!==p.images.length)bad("pilot_count_"+p.id);
  for(const x of p.images){
   const c=origin(x.src),kind=c==="youtube"?"youtube_thumbnail":c==="affiliate"?"affiliate_dynamic_banner":c==="wikimedia"?"wikimedia_binary":c==="google_drive"?"google_drive_thumbnail":c;
   if(slots.has(x.slot))bad("duplicate_slot_"+x.slot);slots.add(x.slot);
   if(x.origin_group!==kind)bad("pilot_origin_"+x.slot);
   if(x.guest_http_status!==null||x.guest_current_src!==null||x.guest_transfer_bytes!==null||x.guest_natural_px!==null||x.guest_broken!==null||x.rehost_authorized!==false)bad("pilot_guest_or_rights_"+x.slot);
   imgs.push(x);groups[c]=(groups[c]||0)+1;
  }
 }
 const third=imgs.filter(x=>!["first_party","first_party_proxy"].includes(origin(x.src))).length;
 if(ids.size!==91||imgs.length!==56||third!==48)bad("global_count");
 if(groups.youtube!==40||groups.affiliate!==3||groups.wikimedia!==3||groups.google_drive!==1||groups.other_external!==1||groups.first_party!==8)bad("groups");
 return{ok:!errors.length,errors,summary:{pages:ids.size,images:imgs.length,external:third,groups,guest_verified:false}};
}
const fs=require('node:fs'),path=require('node:path');
const files=["published_pages_remaining_batch_01_20261114.json","published_pages_remaining_batch_02_20261114.json","published_pages_remaining_batch_03_20261114.json","published_pages_remaining_batch_04_20261114.json","published_pages_remaining_batch_05_20261114.json","published_pages_remaining_batch_06_20261114.json","published_pages_media_pilot_12_20261114.json"];
const load=()=>files.map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8')));
if(require.main===module){const r=verify(load());console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}
module.exports={origin,verify,load};

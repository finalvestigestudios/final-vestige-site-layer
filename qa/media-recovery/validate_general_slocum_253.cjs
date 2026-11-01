"use strict";
// Exact frozen post-253 source identity and conservative rights/960px gate; no network requests.
const loc={2:["2009632218","LC-USZ62-138401"],3:["2009632220","LC-USZ62-138403"],4:["2009632224","LC-USZ62-138407"],5:["2009632223","LC-USZ62-138406"]};
const dims={0:[800,800,800,800],1:[542,347,542,347],6:[2304,3072,960,1280]};
const caveats={0:"1891 and 1904",1:"June 15, 1904",2:"August 13",3:"August 1904",4:"resurfacing",5:"September 1904",6:"2007"};
function validate(d,census){
 const e=[],bad=x=>e.push(x);
 if(!d||d.schema_version!==1||d.post_id!==253||!Array.isArray(d.records)||d.records.length!==7)return ["batch_invalid"];
 const a=(census?.images||[]).filter(x=>x.post_id===253).sort((x,y)=>x.slot-y.slot);
 if(a.length!==7)bad("no_census");
 if(d.wordpress_readback?.status!=="publish"||d.wordpress_readback?.images!==7||d.wordpress_readback?.exact_source_urls!==7||d.wordpress_readback?.exact_alt_texts!==7)bad("cms_readback");
 if(d.source_counts?.all_offsite!==7||d.source_counts?.loc_lccn_records!==4||d.source_counts?.commons_only_records!==3)bad("source_counts");
 if(d.reported_breakages_42_browser_verified!==false||d.claimed_weight_reduction_76_percent_measured!==false)bad("false_42_or_76");
 const s=d.sitewide_inventory||{};
 if(s.published_posts!==61||s.stored_image_slots!==355||s.external_source_slots!==288||s.oversize_wp_originals!==13)bad("sitewide");
 const keys=new Set();
 for(let i=0;i<7;i++){
  const r=d.records[i],c=a[i],id="253:"+i;
  if(!r||r.key!==id||r.post_id!==253||r.slot!==i||keys.has(r?.key)){bad("slot_"+i);continue}keys.add(r.key);
  for(const k of ["post_url","source_url","source_host","source_kind","alt"])if(r[k]!==c?.[k])bad("census_"+i+"_"+k);
  if(r.source_kind!=="wikimedia_redirect"||r.source_host!=="commons.wikimedia.org"||!r.source_url.endsWith("?width=1280"))bad("source_type_"+i);
  let file="";try{file=decodeURIComponent(r.source_url.split("/file/")[1].split("?")[0])}catch(_){bad("file_invalid_"+i)}
  if(loc[i]){
   const [number,repro]=loc[i];
   if(r.catalog_id!==number||r.catalog_repro_id!==repro||r.catalog_url!=="https://www.loc.gov/item/"+number+"/"||r.match_method!=="lccn_embedded_in_commons_filename_and_loc_title"||!file.includes("LCCN"+number+".jpg"))bad("loc_identity_"+i);
   if(r.rights_signal!=="LOC_no_known_restrictions_not_a_license"||!r.rights_policy_urls?.includes("https://wwws.loc.gov/rr/print/res/493_ster.html"))bad("loc_rights_"+i);
  }else{
   const archiveName=r.catalog_url?.split("File:")[1];
   if(r.catalog_id!==null||r.catalog_repro_id!==null||r.match_method!=="exact_commons_file_title"||!archiveName||archiveName.replaceAll("_"," ").toLowerCase()!==file.replaceAll("_"," ").toLowerCase())bad("commons_identity_"+i);
   if(!r.rights_signal?.startsWith("Commons_")||r.rights_policy_urls?.[0]!==r.catalog_url)bad("commons_rights_"+i);
  }
  if(!r.date_caveat?.includes(caveats[i]))bad("history_"+i);
  if(r.rights_review!=="HOLD_item_level"||r.binary_identity_verified!==false||r.master_sha256!==null||r.asset_copied!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false)bad("rights_hold_"+i);
  if(r.max_width_px!==960||r.actual_derivative_px!==null)bad("unreleased_derivative_"+i);
  for(const k of ["visitor_current_src","visitor_http_status","visitor_content_type","visitor_encoded_bytes","visitor_natural_width","visitor_broken"])if(r[k]!==null)bad("invented_"+i+"_"+k);
  const z=dims[i],p=r.proposed_derivative_px;
  if(!z){
   if(r.source_w!==null||r.source_h!==null||r.source_size_basis!==null||p!==null)bad("invented_loc_dimensions_"+i);
  }else{
   if(r.source_w!==z[0]||r.source_h!==z[1]||r.source_size_basis!=="Commons_file_metadata"||p?.width!==z[2]||p?.height!==z[3]||p?.basis!=="Commons_file_metadata"||p.width>960||p.width>r.source_w||p.height!==Math.round(r.source_h*p.width/r.source_w))bad("dimension_"+i);
  }
 }
 return e;
}
module.exports={validate};

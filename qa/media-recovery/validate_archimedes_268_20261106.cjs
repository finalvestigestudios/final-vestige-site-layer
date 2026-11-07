"use strict";
/* Zero-network, fail-closed audit of exact live WordPress source URLs. */
const expectedSrcs=[
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/Archimedes%20Palimpsest.jpg?width=1280",
  "https://archimedespalimpsest.org/assets/img/imaging_x8.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/002r-001v%20Arch13r%20Sinar%20uvblue%20norm8%20Euchologion%20up%20%289737603804%29.jpg?width=960",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Heiberg-UV-blue%20%289737623542%29.jpg?width=960",
  "https://www.archimedespalimpsest.org/assets/img/imagecapture-capture2b.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Arch07r%20Sinar%20pseudo%20no-veil%20%289734386225%29.jpg?width=960",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/028v-021r%20Arch08r%20XRF%20FeFront%20registered%20%289734104759%29.jpg?width=1280",
  "https://archimedespalimpsest.org/assets/img/imaging_x12.jpg",
  "https://archimedespalimpsest.org/assets/img/imaging_x9.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/176r-173v%20Hype03r%20Sinar%20LED445-735%20pseudo%20%289734660151%29.jpg?width=960"
];
function validate(a) {
 const errors=[], need=(test,msg)=>{if(!test)errors.push(msg)};
 need(a?.schema==="fv.media.archimedes_rights_geometry.v1","schema");
 need(a?.post?.id===268&&a?.post?.status==="publish","post");
 need(a?.counts?.slots===10&&a?.counts?.commons===6&&a?.counts?.project_assets===4&&a?.counts?.stored_images_missing_dimensions===10&&a?.counts?.requests_above_960px===2,"counts");
 if(!Array.isArray(a?.images)||a.images.length!==10){errors.push("images");return errors;}
 let nCommons=0,nProject=0,over=0;
 for(let idx=0;idx<10;idx++){
  const x=a.images[idx],isCommons=[0,2,3,5,6,9].includes(idx);
  need(x.slot===idx,"slot"+idx);
  need(x.stored_src===expectedSrcs[idx],"exact_url"+idx);
  need(typeof x.stored_alt==="string"&&x.stored_alt.length>=20,"alt"+idx);
  need(x.stored_html_width===null&&x.stored_html_height===null,"stored_dims"+idx);
  need(x.source_class===(isCommons?"commons_redirect":"project_website_asset"),"class"+idx);
  const found=expectedSrcs[idx].match(/[?&]width=(\d+)/);
  need(x.requested_width_parameter===(found?Number(found[1]):null),"query_width"+idx);
  if(x.requested_width_parameter>960)over++;
  if(isCommons){
   nCommons++;
   need(x.catalog_page_url?.startsWith("https://commons.wikimedia.org/wiki/File:"),"catalog"+idx);
   need(x.catalog_page_url===a.catalog_evidence.commons_canonical_by_slot[idx],"catalog_anchor"+idx);
   const p=x.catalog_original_pixels,d=x.conditional_max_960px_no_upscale;
   need(!!p&&Number.isInteger(p.width)&&p.width>0&&Number.isInteger(p.height)&&p.height>0,"catalog_px"+idx);
   need(!!d&&Number.isInteger(d.width)&&Number.isInteger(d.height),"derivative_px"+idx);
   if(p&&d) need(d.width===Math.min(p.width,960)&&d.height===Math.round(Math.min(p.width,960)*p.height/p.width)&&d.height<=p.height,"no_upscale_aspect"+idx);
   if(idx===0)need(x.documented_license_assertions?.some(y=>y.includes("US public domain")),"pd_us"+idx);
   else need(x.documented_license_assertions?.some(y=>y.includes("CC BY 2.0"))&&x.documented_license_assertions?.some(y=>y.includes("CC BY 3.0")),"dual_rights"+idx);
  }else{
   nProject++;
   need(x.catalog_page_url===null&&x.catalog_original_pixels===null&&x.conditional_max_960px_no_upscale===null,"unknown_asset_dims"+idx);
  }
  need(typeof x.rights_review_flag==="string"&&x.rights_review_flag.length>30,"rights_notes"+idx);
  need(x.rights_cleared===false&&x.rehost_approved===false&&x.image_exact_binary_matched===false,"rights_hold"+idx);
  for(const k of ["actual_origin_http_status","guest_browser_http_status","guest_natural_width","guest_natural_height","guest_encoded_bytes"])need(x[k]===null,"no_fabrication_"+k+"_"+idx);
  need(x.web_retriever?.method==="text-media-wrapper"&&["not_tested","retriever_unavailable","retriever_forbidden"].includes(x.web_retriever?.outcome),"wrapper_method"+idx);
 }
 need(nCommons===6&&nProject===4&&over===2,"rollup");
 need(a?.source_limitations?.broken_42_guest_confirmed===false&&a?.source_limitations?.percent_76_savings_measured===false&&a?.source_limitations?.observed_retriever_403_not_visitor_http===true,"measurement_limits");
 for(const k of ["wordpress_writes","image_downloads","caching","homepage_changes","subscriptions"])need(a?.production_actions?.[k]===0,"no_prod_"+k);
 return errors;
}
module.exports={validate};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,"archimedes_268_primary_rights_geometry_20261106.json"),"utf8"));
 const errors=validate(data);
 if(errors.length){console.error(errors.join("\n"));process.exitCode=1;}
 else console.log("PASS: 10 exact live image refs, source-specific rights, geometry and visitor-evidence holds");
}

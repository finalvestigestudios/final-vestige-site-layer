'use strict';
const url=u=>typeof u==='string'&&/^https:\/\/(?:[a-z0-9-]+\.)+[a-z]{2,}\/[^\s]*$/i.test(u)&&!u.includes('@');
const uint=n=>Number.isSafeInteger(n)&&n>=0;
function checks(a){
 const e=[];
 if(a?.schema!=='fv-vasa-primary-press-and-wire-gate-v1')return ['BAD_SCHEMA'];
 if(a.post?.wp_id!==299||!url(a.post?.url)||!a.post?.wp_revision)e.push('POST_NOT_PINNED');
 if(a.source_oversized_exposure?.git_blob_sha!=='cd3af158a6cf4c197704be0527882bb4666f9156')e.push('SOURCE_BLOB_MISMATCH');
 if(a.official_press?.permission_scope!=='EDITORIAL_ONLY_WITH_ATTRIBUTION_NOT_A_BLANKET_COPYRIGHT_LICENSE')e.push('PRESS_SCOPE_INCORRECT');
 if(!Array.isArray(a.images)||a.images.length!==3)return [...e,'IMAGE_COUNT'];
 let sum=0,exact=0;const ids=new Set();
 for(const x of a.images){
   if(![388,389,382].includes(x.media_id)||ids.has(x.media_id))e.push('INVALID_OR_DUPLICATE_MEDIA_ID');
   ids.add(x.media_id);
   if(!url(x.original_wp_url)||!x.original_wp_url.startsWith('https://finalvestige.com/wp-content/uploads/'))e.push('INVALID_ORIGINAL_URL');
   if(!url(x.published_img_src)||!x.published_img_src.startsWith('https://i0.wp.com/finalvestige.com/wp-content/uploads/'))e.push('INVALID_PUBLISHED_URL');
   if(!uint(x.original_stored_bytes)||x.original_stored_bytes<=1500000)e.push('ORIGINAL_SIZE_INVALID');
   sum+=x.original_stored_bytes||0;
   const w=x.wp_original_dimensions?.width,h=x.wp_original_dimensions?.height;
   if(!uint(w)||!uint(h)||w===0||h===0||x.proposed_geometry_only?.width!==Math.min(960,w)||x.proposed_geometry_only?.height!==Math.round(h*Math.min(960,w)/w))e.push('DISTORTED_OR_UPSCALED_DIMENSIONS');
   const c=x.official_candidate;
   if(!url(c?.url)||!c.url.startsWith('https://www.vasamuseet.se/globalassets/')||c?.press_page!=='https://www.vasamuseet.se/en/about-the-vasa-museum/press/press-images')e.push('OFFICIAL_PROVENANCE_INVALID');
   if(!c?.photographer||!c?.credit?.includes(c.photographer)||!c?.credit.includes('Vasa Museum'))e.push('CREDIT_MISSING');
   if(c?.match_basis==='EXACT_FILENAME_AND_DESCRIPTION'){exact++;if(c.url.split('/').pop()!==x.original_wp_url.split('/').pop())e.push('EXACT_FILENAME_DISAGREES');}
   else if(c?.match_basis!=='RELATED_SCENE_FILENAME_DIFFERS')e.push('MATCH_CLASS_UNKNOWN');
   if(x.media_id===389&&c?.match_basis!=='RELATED_SCENE_FILENAME_DIFFERS')e.push('RELATED_CANDIDATE_OVERSOLD');
   if(c?.numeric_http_status!==null||c?.official_master_sha256!==null||c?.official_master_dimensions!==null||c?.pixel_crop_match!==false)e.push('UNVERIFIED_MASTER_CLAIM');
   if(x.browser?.http_status!==null||x.browser?.current_src!==null||x.browser?.decoded!==null||x.browser?.transfer_bytes!==null)e.push('FABRICATED_VISITOR_OBSERVATION');
   if(x.publish_authorized!==false||x.cache_authorized!==false)e.push('UNAUTHORIZED_MEDIA_ACTION');
 }
 if(ids.size!==3||sum!==13318311||a.summary?.original_stored_bytes!==sum||a.summary?.n_media!==3||a.summary?.official_exact_filename_leads!==2||a.summary?.official_related_only_leads!==1||exact!==2)e.push('TOTALS_OR_RIGHTS_MISMATCH');
 if(a.summary?.sitewide_reported_broken_42_verified!==false||a.summary?.claimed_76_percent_wire_saving_verified!==false||a.summary?.real_guest_http_checks!==0||a.summary?.measured_wire_before_bytes!==null||a.summary?.measured_wire_after_bytes!==null)e.push('UNMEASURED_ASSERTION');
 if(!a.safety||Object.values(a.safety).some(v=>v!==false))e.push('UNAUTHORIZED_SCOPE');
 return [...new Set(e)];
}
function assessWirePair(pair){
 const errors=[];if(pair?.schema!=='fv-cold-image-transfer-pair-v1')return {status:'HOLD',errors:['BAD_WIRE_SCHEMA'],before_bytes:null,after_bytes:null,reduction_percent:null};
 let before=null,after=null;
 for(const [name,p] of [['before',pair.before],['after',pair.after]]){
   const N=name.toUpperCase();
   if(!p){errors.push(N+'_NOT_COLLECTED');continue;}
   if(p.origin!=='SITE_QA_154_LOGGED_OUT_CDP'||p.cache!=='cold'||p.page_status!==200||p.post_url!==pair.expected_post_url||p.revision!==pair.expected_revision||p.complete_image_waterfall!==true)errors.push(N+'_UNVERIFIED_CAPTURE');
   if(!uint(p.viewport_width)||!p.viewport_width||!uint(p.viewport_height)||!p.viewport_height||!(Number.isFinite(p.dpr)&&p.dpr>0)||!p.user_agent)errors.push(N+'_MISSING_DEVICE');
   if(!/^[a-f0-9]{64}$/i.test(p.screenshot_sha256||'')||p.visual_review_approved!==true)errors.push(N+'_VISUAL_UNREVIEWED');
   if(!Array.isArray(p.images)||!p.images.length){errors.push(N+'_MISSING_IMAGES');continue;}
   let bytes=0;const ids=new Set(),slots=new Set();
   for(const x of p.images){
     if(typeof x.slot!=='string'||!x.slot||slots.has(x.slot)||typeof x.request_id!=='string'||!x.request_id||ids.has(x.request_id))errors.push(N+'_DUPLICATE_OR_BAD_IMAGE');
     ids.add(x.request_id);slots.add(x.slot);
     if(!url(x.current_src)||x.status!==200||typeof x.mime!=='string'||!x.mime.startsWith('image/')||x.decoded!==true||!uint(x.natural_width)||!x.natural_width||!uint(x.natural_height)||!x.natural_height)errors.push(N+'_FAILED_IMAGE_OR_STATUS');
     if(!uint(x.encoded_transfer_bytes)||!x.encoded_transfer_bytes||x.byte_source!=='CDP.Network.loadingFinished.encodedDataLength'||x.from_cache!==false||x.from_service_worker!==false)errors.push(N+'_TRANSFER_UNVERIFIED');
     bytes+=x.encoded_transfer_bytes||0;
   }
   if(name==='before')before={p,slots,bytes};else after={p,slots,bytes};
 }
 if(before&&after){
   for(const k of ['viewport_width','viewport_height','dpr','user_agent','post_url','revision'])if(before.p[k]!==after.p[k])errors.push('DEVICE_OR_REVISION_MISMATCH');
   if(before.slots.size!==after.slots.size||[...before.slots].some(v=>!after.slots.has(v)))errors.push('IMAGE_SLOT_PARITY_FAILED');
 }
 if(!url(pair.expected_post_url)||!pair.expected_revision)errors.push('PAIR_UNPINNED');
 if(errors.length)return {status:'HOLD',errors:[...new Set(errors)],before_bytes:null,after_bytes:null,reduction_percent:null};
 const pct=100*(before.bytes-after.bytes)/before.bytes;
 return {status:'MEASURED_PAGE_ONLY',errors:[],before_bytes:before.bytes,after_bytes:after.bytes,reduction_percent:Math.round(pct*100)/100,meets_76_percent_page_target:pct>=76,sitewide_claim_authorized:false,wordpress_write_authorized:false};
}
module.exports={checks,assessWirePair};

'use strict';
function validate(a){
 const errors=[],bad=(ok,n)=>{if(!ok)errors.push(n)};
 bad(a?.schema==='fv-west-loch-370-verified-stored-sources-v1','schema');
 bad(a?.post?.id===370&&a?.counts?.images===8,'post count');
 bad(Array.isArray(a?.images)&&a.images.length===8,'rows');
 const x=a.images||[];
 bad(x.filter(r=>r.origin_class==='external').length===4&&x.filter(r=>r.origin_class==='first_party').length===4,'origin counts');
 bad(new Set(x.map(r=>r.source_url)).size===8,'unique URLs');
 bad(x.every((r,i)=>r.slot===i),'slot order');
 for(const r of x){
   bad(/^https:\/\/[^ ]+$/.test(r.source_url)&&r.alt,'source/alt '+r.slot);
   bad(r.width_attr===null&&r.height_attr===null,'intrinsic markup fabricated '+r.slot);
   bad(r.origin_class===(r.host==='finalvestige.com'?'first_party':'external'),'origin class '+r.slot);
   bad(r.origin_http_status===null&&r.guest_http_status===null&&r.guest_decode_pixels===null&&r.guest_encoded_bytes===null&&r.visitor_broken===null,'HTTP/browser invented '+r.slot);
   bad(r.archive_rights==='REVIEW_HOLD'&&!r.identical_published_binary&&!r.copy_or_cache_authorized&&!r.wp_upload_authorized,'copyright or publish permission '+r.slot);
   const p=r.conditional_preview_960,m=r.catalog_high_tiff_scan_pixels;
   bad(Array.isArray(m),'missing catalog geometry array '+r.slot);
   if(p!==null){
     bad(Number.isInteger(p.width)&&p.width>0&&p.width<=960&&Number.isInteger(p.height)&&p.height>0,'preview dimensions '+r.slot);
     bad(m.length===1&&!r.scan_conflict,'unsettled catalog scans '+r.slot);
     if(m.length===1){const v=m[0];bad(p.width<=v.width&&p.height<=v.height&&Math.abs(p.height-Math.round(v.height*p.width/v.width))<=1,'upscale/crop distortion '+r.slot);}
   }
   bad(!(r.scan_conflict&&p!==null),'conflicted image preview '+r.slot);
 }
 bad(x[1]?.catalog_id==='80-G-202485'&&x[1]?.catalog_high_tiff_scan_pixels?.length===2&&x[1]?.conditional_preview_960===null&&x[1]?.scan_conflict===true,'two incompatible official scans');
 bad(String(x[4]?.historical_identity).includes('MAY BE'),'probabilistic ship ID');
 bad(String(x[2]?.historical_identity).includes('LST-39'),'SC 185701 primary subject');
 bad(String(x[7]?.historical_identity).includes('2024'),'DPAA photo chronology');
 bad(a?.unsupported_claims?.reported_42_broken==='UNVERIFIED'&&a?.unsupported_claims?.target_76_percent_savings==='UNMEASURED','unsupported 42/76');
 bad(a?.baseline?.oct30_posts===61&&a?.baseline?.oct30_stored_images===355&&a?.baseline?.later_posts===66&&a?.baseline?.later_stored_images===361,'historical cohorts conflated');
 bad(a?.baseline?.oversized_original_count===13&&a?.baseline?.oversized_stored_bytes===43522829&&a?.baseline?.oversized_visitor_bytes===null,'stored bytes confused with wire');
 bad(Object.values(a?.actions||{}).length===5&&Object.values(a.actions).every(v=>v===false),'unapproved action');
 return {pass:errors.length===0,errors};
}
if(typeof module!=='undefined')module.exports={validate};

'use strict';
/** Rest API edit/view image identity and safety checks; not browser monitoring. */
function decode(s){return String(s).replace(/&#0*38;|&#x0*26;|&amp;/gi,"&");}
function uri(s){let m=String(s||"").match(/^https:\/\/([^/?#]+)(\/[^?#]*)(\?[^#]*)?$/i);return m?{host:m[1].toLowerCase(),path:m[2],query:m[3]||""}:null;}
function matchPair(r){
 try{
 const a=uri(r.edit_source_url),b=uri(decode(r.view_src));
 if(!a||!b)return {ok:false,mode:"invalid"};
 if(!/^i\d+\.wp\.com$/.test(b.host)){const ok=decode(r.view_src)===r.edit_source_url;return {ok,mode:"direct",queryGap:false,transform:false};}
 if(/^i\d+\.wp\.com$/.test(a.host)){
   const ok=decode(r.view_src)===r.edit_source_url;return {ok,mode:"jetpack_proxy",queryGap:false,transform:/[?&](resize|fit|w|h|crop)=/i.test(b.query)};
 }
 const path=decodeURIComponent(b.path),k=path.indexOf("/",1);
 if(k<0)return {ok:false,mode:"jetpack_proxy"};
 return {ok:path.slice(1,k).toLowerCase()===a.host&&path.slice(k)===decodeURIComponent(a.path),mode:"jetpack_proxy",queryGap:!!a.query,transform:/[?&](resize|fit|w|h|crop)=/i.test(b.query)};
 }catch{return {ok:false,mode:"invalid"};}
}
function candidateGeometrySafe(c){
 if(!c||typeof c!=='object'||typeof c.rights_note!=='string'||!c.rights_note.trim()||
    typeof c.official_item_url!=='string'||!/^https:\/\/[^/?#]+\//i.test(c.official_item_url)||
    c.publication_rights_verified!==false)return false;
 if(c.native_px===null||c.review_px===null)return c.native_px===null&&c.review_px===null;
 if(!Array.isArray(c.native_px)||!Array.isArray(c.review_px)||
    c.native_px.length!==2||c.review_px.length!==2||
    ![...c.native_px,...c.review_px].every(v=>Number.isSafeInteger(v)&&v>0))return false;
 const [w,h]=c.native_px,reviewW=Math.min(960,w);
 return c.review_px[0]===reviewW&&c.review_px[1]===Math.round(h*reviewW/w);
}
function attributesSafe(r){
 const empty=r.width===null&&r.height===null;
 const present=Number.isSafeInteger(r.width)&&r.width>0&&
               Number.isSafeInteger(r.height)&&r.height>0;
 return (empty||present)&&r.srcset===null&&r.sizes===null&&
        typeof r.alt==='string'&&r.alt.trim().length>0;
}
function validate(a){
 const errors=[],want=new Map([[285,6],[287,6],[407,8],[418,6]]),
       p0=new Set(["285:2","285:5","287:5","407:1","418:1","418:2"]),
       seen=new Set(),byPost=new Map();
 if(a?.schema!=="fv-wp-26-edit-view-lineage-v1"||!Array.isArray(a.rows)||
    a.rows.length!==26||!Array.isArray(a.posts)||a.posts.length!==4)return ["bad_scope_or_schema"];
 const measured={posts:4,slots:a.rows.length,view_proxy:0,view_direct:0,p0:0,
                 p0_proxy:0,dimensions:0,srcset:0,query_gap:0};
 for(const r of a.rows){
  if(!want.has(r.post_id)||r.key!==r.post_id+":"+r.slot||
     !Number.isSafeInteger(r.slot)||r.slot<0||r.slot>=want.get(r.post_id)||
     seen.has(r.key))errors.push("bad_key");
  seen.add(r.key);byPost.set(r.post_id,(byPost.get(r.post_id)||0)+1);
  const m=matchPair(r);
  if(!m.ok||m.mode!==r.view_url_mode||m.queryGap!==r.query_gap||
     m.transform!==r.cdn_transform||r.origin_path_verified!==true)
      errors.push("bad_origin:"+r.key);
  if(!attributesSafe(r))errors.push("bad_attributes:"+r.key);
  if(p0.has(r.key)!==(r.p0_candidate!==null)||
     (r.p0_candidate!==null&&!candidateGeometrySafe(r.p0_candidate)))
      errors.push("bad_rights_or_geometry:"+r.key);
  if([r.guest_current_src,r.guest_http_status,r.jetpack_http_status,
      r.origin_http_status,r.guest_transfer_bytes,r.guest_natural_width]
      .some(x=>x!==null))errors.push("fabricated_status:"+r.key);
  if(r.cache_authorized!==false||r.wp_upload_authorized!==false||
     r.post_rewrite_authorized!==false||r.max_derivative_width_px!==960||
     r.no_upscale!==true)errors.push("unsafe_release:"+r.key);
  if(m.mode==="jetpack_proxy")measured.view_proxy++;
  if(m.mode==="direct")measured.view_direct++;
  if(p0.has(r.key)){measured.p0++;if(m.mode==="jetpack_proxy")measured.p0_proxy++;}
  if(r.width!==null&&r.height!==null)measured.dimensions++;
  if(r.srcset!==null)measured.srcset++;
  if(m.queryGap)measured.query_gap++;
 }
 for(const [id,n]of want){
  const p=a.posts.filter(p=>p.id===id);
  if(byPost.get(id)!==n||p.length!==1||p[0].image_slots!==n||
     typeof p[0].link!=="string"||
     !/^https:\/\/finalvestige\.com\//.test(p[0].link)||
     typeof p[0].modified!=="string"||
     !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(p[0].modified))
     errors.push("post_count_or_custody:"+id);
 }
 const c=a.counts||{};
 for(const [k,v]of Object.entries(measured))if(c[k]!==v)errors.push("summary_drift:"+k);
 if(c.reported_broken_guest_verified!==false||c.measured_76_percent!==false)
    errors.push("unproved_status_or_savings");
 const release=a.release||{};
 if(release.wordpress_writes!==0||release.media_binary_downloads!==0||
    release.homepage_edits!==0||release.merged!==false||
    release.deployed!==false||release.paid_usd!==0)
    errors.push("release_risk");
 return [...new Set(errors)];
}
module.exports={decode,uri,matchPair,candidateGeometrySafe,attributesSafe,validate};

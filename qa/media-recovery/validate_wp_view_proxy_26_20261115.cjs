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
function validate(a){
 const errors=[],want=new Map([[285,6],[287,6],[407,8],[418,6]]),p0=new Set(["285:2","285:5","287:5","407:1","418:1","418:2"]),seen=new Set(),byPost=new Map();
 if(a?.schema!=="fv-wp-26-edit-view-lineage-v1"||!Array.isArray(a.rows)||a.rows.length!==26||a.posts?.length!==4)return ["bad_scope_or_schema"];
 for(const r of a.rows){
  if(!want.has(r.post_id)||r.key!==r.post_id+":"+r.slot||!Number.isSafeInteger(r.slot)||r.slot<0||r.slot>=want.get(r.post_id)||seen.has(r.key))errors.push("bad_key");
  seen.add(r.key);byPost.set(r.post_id,(byPost.get(r.post_id)||0)+1);
  const m=matchPair(r);
  if(!m.ok||m.mode!==r.view_url_mode||m.queryGap!==r.query_gap||m.transform!==r.cdn_transform||r.origin_path_verified!==true)errors.push("bad_origin:"+r.key);
  if(p0.has(r.key)!==!!r.p0_candidate||r.p0_candidate?.publication_rights_verified===true)errors.push("bad_rights:"+r.key);
  if(r.p0_candidate&&((r.p0_candidate.native_px===null)!==(r.p0_candidate.review_px===null)))errors.push("native_geometry_fabricated:"+r.key);
  if([r.guest_current_src,r.guest_http_status,r.jetpack_http_status,r.origin_http_status,r.guest_transfer_bytes,r.guest_natural_width].some(x=>x!==null))errors.push("fabricated_status:"+r.key);
  if(r.cache_authorized!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false||r.max_derivative_width_px!==960||r.no_upscale!==true)errors.push("unsafe_release:"+r.key);
 }
 for(const [id,n]of want)if(byPost.get(id)!==n||a.posts.filter(p=>p.id===id&&p.image_slots===n).length!==1)errors.push("post_count:"+id);
 const c=a.counts||{};
 if(c.slots!==26||c.view_proxy!==25||c.view_direct!==1||c.p0!==6||c.p0_proxy!==6||c.dimensions!==5||c.srcset!==0||c.query_gap!==1)errors.push("summary_drift");
 if(a.release?.wordpress_writes!==0||a.release?.media_binary_downloads!==0)errors.push("release_risk");
 return [...new Set(errors)];
}
module.exports={decode,uri,matchPair,validate};

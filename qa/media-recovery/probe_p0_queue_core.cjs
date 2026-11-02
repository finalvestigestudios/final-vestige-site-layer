'use strict';
/** Offline, fail-closed browser priority plan. Does not fetch images or authorize publication. */
const SKYWAY_KEY='287:5';
const SKYWAY_ORIGINAL='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg';
const RELEASE_ORDER=['285:5','407:1','418:1','418:2','285:0','407:3','268:8','268:4','285:2','418:0'];
const BROWSER_ORDER=['285:5',SKYWAY_KEY,...RELEASE_ORDER.slice(1)];
const LEGACY_POSTS=[432,434,621];
const isPublicHttps=s=>{try{const u=new URL(s);return u.protocol==='https:'&&!!u.hostname&&!u.username&&!u.password}catch{return false}};
function buildPriorityPlan(snapshot,release){
  if(!Array.isArray(snapshot?.parts)||snapshot.parts.length!==8)throw Error('Frozen eight-part source snapshot required');
  if(release?.schema_version!==1||!Array.isArray(release.rows)||release.rows.length!==10)throw Error('Ten-row audited P0 restoration queue required');
  const posts=new Map(),images=new Map(),seenRows=new Set();
  for(const part of snapshot.parts){
    if(!Array.isArray(part.posts)||!Array.isArray(part.images))throw Error('Invalid source census part');
    for(const post of part.posts){
      if(posts.has(post.id))throw Error('Duplicate post '+post.id);
      posts.set(post.id,post);
    }
    for(const im of part.images){
      if(images.has(im.key))throw Error('Duplicate image key '+im.key);
      images.set(im.key,im);
    }
  }
  for(const row of release.rows){
    if(!RELEASE_ORDER.includes(row.image_key)||seenRows.has(row.image_key))throw Error('Unexpected or duplicate release key '+row.image_key);
    seenRows.add(row.image_key);
    const im=images.get(row.image_key);
    if(!im||im.post_id!==row.post_id||im.source_url!==row.current_published_source_url||im.alt!==row.current_published_alt)throw Error('Release queue source/ALT mismatch '+row.image_key);
    if(row.approval?.replacement_ready!==false||row.approval?.media_cache_authorized!==false||row.approval?.wordpress_upload_authorized!==false||row.approval?.wordpress_post_edit_authorized!==false)throw Error('Publication authorization must remain HOLD '+row.image_key);
  }
  if(RELEASE_ORDER.some(k=>!seenRows.has(k)))throw Error('Release queue omits audited critical source');
  const skyway=images.get(SKYWAY_KEY);
  if(!skyway||skyway.post_id!==287||skyway.source_url!==SKYWAY_ORIGINAL||skyway.source_kind!=='external'||skyway.allowed_to_localize!==false)throw Error('Skyway original source drift; re-audit prior to browser run');
  const targets=BROWSER_ORDER.map(key=>{
    const im=images.get(key),post=posts.get(im?.post_id);
    if(!im||!post||!isPublicHttps(im.source_url)||!isPublicHttps(post.url)||new URL(post.url).hostname!=='finalvestige.com')throw Error('Unsafe or missing browser target '+key);
    if(!['external','wikimedia_redirect'].includes(im.source_kind))throw Error('Priority image is not an external hotlink '+key);
    return {image_key:key,post_id:im.post_id,post_url:post.url,original_image_url:im.source_url,alt:im.alt,visitor_http_status:null,visitor_broken:null,production_replacement_authorized:false};
  });
  const ids=[...new Set([...targets.map(t=>t.post_id),...LEGACY_POSTS])];
  for(const id of ids){
    const p=posts.get(id);
    if(!p||!isPublicHttps(p.url)||new URL(p.url).hostname!=='finalvestige.com')throw Error('Missing or unsafe planned article '+id);
  }
  return {post_ids:ids,priority_image_keys:[...BROWSER_ORDER],priority_targets:targets,source_queue_entries:release.rows.length,guest_browser_verified:false};
}
module.exports={buildPriorityPlan,BROWSER_ORDER,RELEASE_ORDER,LEGACY_POSTS};

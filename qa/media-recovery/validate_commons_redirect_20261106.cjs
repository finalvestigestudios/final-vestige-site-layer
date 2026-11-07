'use strict';
// No HTTP, browser emulation, asset download, WordPress write or licensing decision.
function fileMeta(src){
 const prefix="https://commons.wikimedia.org/wiki/Special:Redirect/file/";
 if(typeof src!=="string"||!src.startsWith(prefix)||src.length>4096)throw Error("non-Commons redirect URL");
 const tail=src.slice(prefix.length),raw=tail.split(/[?#]/)[0];
 if(!raw||raw.includes("/")||/%(?![a-fA-F0-9]{2})/.test(raw))throw Error("invalid title");
 const title=decodeURIComponent(raw).replace(/_/g," ");
 if(!title||/[\u0000-\u001f<>]/.test(title))throw Error("unsafe title");
 const found=[...tail.matchAll(/[?&]width=([^&#]*)/g)];
 if(found.length>1)throw Error("repeated width");
 let width=null;
 if(found.length){if(!/^[1-9]\d{0,4}$/.test(found[0][1]))throw Error("bad width");width=Number(found[0][1]);}
 return {title,width,lookup:"https://commons.wikimedia.org/wiki/File:"+encodeURIComponent(title.replace(/ /g,"_"))};
}
function validate(shards){
 const errors=[],ok=(v,s)=>{if(!v)errors.push(s);};
 const allowed=["key","post_id","image_index","post_url","stored_src","commons_file_title_unverified","catalog_lookup_url","requested_width_px","license_hints_from_caption"];
 const ids=[166,214,215,216,217,218,219,220,221,252,253,254,255,256,257,258,268,367,425,431,1917,1920,1924,1926];
 if(!Array.isArray(shards)||shards.length!==4)return {ok:false,errors:["four shards required"]};
 const posts=[],images=[];
 shards.forEach((s,i)=>{
  if(!s||typeof s!=="object"){errors.push("missing shard "+i);return;}
  ok(s.schema==="fv-commons-redirect-readonly-shard-v1"&&s.captured_date==="2026-11-06","schema/date "+i);
  ok(typeof s.source==="string"&&s.source.includes("read-only"),"read-only origin "+i);
  ok(Array.isArray(s.posts)&&s.posts.length===6,"post count "+i);
  ok(Array.isArray(s.images)&&s.images.length===[33,40,36,15][i],"image count "+i);
  if(Array.isArray(s.posts))posts.push(...s.posts);
  if(Array.isArray(s.images))images.push(...s.images);
 });
 ok(JSON.stringify(posts.map(x=>x?.post_id))===JSON.stringify(ids),"expected 24 published posts/order");
 const postMap=new Map(),byPost=new Map();
 for(const p of posts){
  if(!p||typeof p!=="object"){errors.push("empty post");continue;}
  ok(typeof p.url==="string"&&/^https:\/\/finalvestige\.com\/20\d\d\/\d\d\/\d\d\/[a-z0-9-]+\/$/.test(p.url),"canonical "+p.post_id);
  ok(typeof p.modified_wp==="string"&&!Number.isNaN(Date.parse(p.modified_wp)),"modified "+p.post_id);
  ok(Number.isSafeInteger(p.inline_tags)&&p.inline_tags>=p.commons_redirects&&p.commons_redirects>0,"post counts "+p.post_id);
  postMap.set(p.post_id,p);byPost.set(p.post_id,0);
 }
 const keys=new Set(),sources=new Set(),widths={w1280:0,w960:0,w900:0,none:0};
 for(const [i,x] of images.entries()){
  if(!x||typeof x!=="object"){errors.push("empty image "+i);continue;}
  ok(Object.keys(x).every(k=>allowed.includes(k)),"unexpected evidence/rights/browser field "+i);
  const p=postMap.get(x.post_id);
  ok(!!p&&x.post_url===p.url,"wrong page association "+i);
  ok(Number.isSafeInteger(x.image_index)&&x.image_index>=0&&x.image_index<(p?.inline_tags??0),"invalid slot "+i);
  const key=x.post_id+":"+x.image_index;
  ok(x.key===key&&!keys.has(key),"duplicate/invalid key "+i);keys.add(key);
  ok(!sources.has(x.stored_src),"duplicate URL "+i);sources.add(x.stored_src);
  ok(Array.isArray(x.license_hints_from_caption)&&x.license_hints_from_caption.length<=3&&
    x.license_hints_from_caption.every(z=>typeof z==="string"&&/^(?:CC0|CC\s+BY(?:-SA)?\s+[1-9](?:\.[0-9])?|public[\s-]?domain)$/i.test(z)),"untrusted license hint "+i);
  try {
   const m=fileMeta(x.stored_src);
   ok(x.commons_file_title_unverified===m.title&&x.catalog_lookup_url===m.lookup,"derived Commons file lookup "+i);
   ok(x.requested_width_px===m.width,"width match "+i);
   if(m.width===1280)widths.w1280++;
   else if(m.width===960)widths.w960++;
   else if(m.width===900)widths.w900++;
   else if(m.width===null)widths.none++;
   else errors.push("unknown requested width "+i);
  }catch(e){errors.push("malformed source "+i+" "+e.message);}
  byPost.set(x.post_id,(byPost.get(x.post_id)||0)+1);
 }
 for(const p of posts){if(p)ok(byPost.get(p.post_id)===p.commons_redirects,"per-post count drift "+p.post_id);}
 ok(posts.length===24&&images.length===124&&keys.size===124&&sources.size===124,"total/unique 124");
 ok(widths.w1280===79&&widths.w960===17&&widths.w900===2&&widths.none===26,"width distribution");
 return {ok:errors.length===0,errors,metrics:{published_posts:posts.length,exact_redirect_sources:images.length,requested_1280:widths.w1280,requested_960:widths.w960,requested_900:widths.w900,unspecified_width:widths.none,license_clearances:0,visitor_confirmed_failures:0,wordpress_writes:0}};
}
module.exports={fileMeta,validate};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const shards=[1,2,3,4].map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,'commons_redirect_20261106_shard0'+n+'.json'),'utf8')));
 const result=validate(shards);console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}

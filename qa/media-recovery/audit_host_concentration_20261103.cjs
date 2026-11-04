'use strict';
/**
 * Host-concentration risk census over the eight frozen 61-post source inventories.
 * Source dependencies only: NO browser HTTP, media download, rights approval or
 * inference that a shared host is broken. Site QA owns browser verification.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const FROZEN_PART_BLOBS=[
 '948bc1b65b42799aa40cfdb810ddf6ffd80886b6',
 '48e1ebf07207e948ba5802e714eb39659d2e1c1d',
 '49183f66f880f7c4dfd363acca906876877f2e5e',
 '6df3251e5a67a971d87a516a1ba4a0cc32f51f96',
 '9b16b828342a9ac338f3e65610fd3d8d508355e9',
 '0f3dfe398a76838049cebba7cb773d5c5a0c8c69',
 '21095161e633aba093b74c0ead9936c9f6186d00',
 '5659ec243c188928be3f89c0f96354b660608ca2'
];
function loadPinnedParts(directory){
 return FROZEN_PART_BLOBS.map((expected,i)=>{
  const bytes=fs.readFileSync(path.join(directory,'parts',String(i+1).padStart(2,'0')+'.json'));
  const gitSha=crypto.createHash('sha1')
   .update(Buffer.from('blob '+bytes.length+'\\0')).update(bytes).digest('hex');
  if(gitSha!==expected)throw Error('frozen Git blob mismatch part '+(i+1));
  return JSON.parse(bytes.toString('utf8'));
 });
}
function buildHostConcentration(parts){
 if(!Array.isArray(parts)||parts.length!==8)throw Error('eight frozen parts required');
 const hosts=new Map(), posts=new Map(), seenSlots=new Set(), kinds={};
 for(let i=0;i<8;i++){
  const part=parts[i];
  if(!part||part.batch!==i+1||!Array.isArray(part.images)||!Array.isArray(part.posts))
   throw Error('batch index or schema mismatch: '+(i+1));
  for(const p of part.posts){
   if(!Number.isInteger(p.id)||posts.has(p.id)||typeof p.url!=='string')
    throw Error('duplicate/invalid post identity');
   posts.set(p.id,{post_id:p.id,title:p.title,page_url:p.url,stored_image_count:0,
    external_origin_image_count:0,source_host_counts:{}});
  }
  for(const im of part.images){
   const p=posts.get(im.post_id);
   if(!p||seenSlots.has(im.key)||im.key!==im.post_id+':'+im.slot||
      im.post_url!==p.page_url||typeof im.source_url!=='string')
    throw Error('source slot identity drift');
   seenSlots.add(im.key);
   let u;try{u=new URL(im.source_url)}catch{throw Error('unparseable source URL '+im.key)}
   if(u.protocol!=='https:'&&u.protocol!=='http:')throw Error('non-http URL '+im.key);
   if(u.hostname!==im.source_host)throw Error('source hostname mismatch '+im.key);
   if(!['external','wikimedia_redirect','jetpack_proxy','first_party'].includes(im.source_kind))
    throw Error('unexpected source kind '+im.key);
   kinds[im.source_kind]=(kinds[im.source_kind]||0)+1;
   p.stored_image_count++;
   if(im.source_kind==='external'||im.source_kind==='wikimedia_redirect')
    p.external_origin_image_count++;
   p.source_host_counts[im.source_host]=(p.source_host_counts[im.source_host]||0)+1;
   if(!hosts.has(im.source_host))hosts.set(im.source_host,{source_host:im.source_host,
    stored_reference_count:0,post_ids:new Set(),slot_keys:[],source_kind_counts:{},
    example_exact_source_url:im.source_url,origin_http_status:null,guest_browser_broken_verified:false});
   const h=hosts.get(im.source_host);h.stored_reference_count++;h.post_ids.add(im.post_id);
   h.slot_keys.push(im.key);h.source_kind_counts[im.source_kind]=(h.source_kind_counts[im.source_kind]||0)+1;
  }
 }
 if(posts.size!==61||seenSlots.size!==355||kinds.external!==170||
  kinds.wikimedia_redirect!==118||kinds.first_party!==60||kinds.jetpack_proxy!==7)
  throw Error('frozen 61/355/288+67 source census mismatch');
 const hostRows=[...hosts.values()].map(h=>({...h,distinct_post_count:h.post_ids.size,
  post_ids:[...h.post_ids].sort((a,b)=>a-b),slot_keys:h.slot_keys.sort()}))
  .sort((a,b)=>b.stored_reference_count-a.stored_reference_count||a.source_host.localeCompare(b.source_host));
 const postRows=[...posts.values()].map(p=>({...p,fully_externally_sourced:p.external_origin_image_count===p.stored_image_count,
  single_external_source_host:p.external_origin_image_count===p.stored_image_count&&
   Object.entries(p.source_host_counts).length===1?Object.keys(p.source_host_counts)[0]:null}))
   .sort((a,b)=>a.post_id-b.post_id);
 return {
  schema_version:1,date:'2026-11-03',method:'frozen Gutenberg src dependency topology; NOT HTTP/browser outage test',
  frozen_part_paths:Array.from({length:8},(_,i)=>'qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json'),
  source_count:{posts:posts.size,stored_inline_image_refs:seenSlots.size,
   recorded_external_origins:kinds.external+kinds.wikimedia_redirect,
   first_party_direct:kinds.first_party,first_party_jetpack:kinds.jetpack_proxy,
   external_direct:kinds.external,wikimedia_special_redirect:kinds.wikimedia_redirect,
   distinct_stored_source_hosts:hosts.size,
   all_external_posts:postRows.filter(p=>p.fully_externally_sourced).length,
   fully_single_external_host_posts:postRows.filter(p=>p.single_external_source_host).length
  },
  caveats:{browser_broken_42:'UNVERIFIED',wire_weight_savings_76_percent:'UNMEASURED',
   saved_image_binary_status:'NOT_INSPECTED',rendered_currentSrc_redirects:'NOT_MEASURED',
   source_host_exposure_is_not_outage:true,no_wordpress_writes:true,media_rehost_approved:false},
  hosts:hostRows,posts:postRows
 };
}
module.exports={buildHostConcentration,loadPinnedParts,FROZEN_PART_BLOBS};
if(require.main===module){
 const parts=loadPinnedParts(__dirname);
 process.stdout.write(JSON.stringify(buildHostConcentration(parts),null,2)+'\n');
}

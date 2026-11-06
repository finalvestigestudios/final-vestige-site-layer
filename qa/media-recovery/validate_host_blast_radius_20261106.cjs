'use strict';
// Offline integrity checks. No HTTP, image transfers, writes or CMS access.
function hostInfo(url) {
 if(typeof url!=='string'||url.length>4096)throw Error('invalid URL');
 const m=/^https:\/\/([^/?#]+)/i.exec(url);
 if(!m||m[1].includes('@')||m[1].includes(':'))throw Error('HTTPS URL required');
 const requested=m[1].toLowerCase();
 const upstream=/^i[0-3]\.wp\.com$/.test(requested)?
   url.replace(/^https:\/\/[^/]+\//i,'').split(/[/?#]/)[0].toLowerCase():requested;
 if(!/^[a-z0-9.-]+\.[a-z]{2,}$/.test(upstream))throw Error('invalid upstream');
 return {requested,upstream};
}
function validate(a) {
 const errors=[],ok=(condition,msg)=>{if(!condition)errors.push(msg);};
 if(!a||typeof a!=='object')return {ok:false,errors:['missing audit']};
 const m=a.metrics||{},gs=a.groups||[],p0=a.p0_source_urls||[],r=a.rights_and_release||{};
 ok(a.schema==='fv-media-blast-radius-v1','schema');
 ok(a.as_of==='2026-11-06','snapshot date');
 ok(m.posts===66&&m.legacy_posts===61&&m.added_posts===5,'post denominator');
 ok(m.posts_with_inline_images===65&&m.posts_with_zero_inline_images===1,'post-with-images denominator');
 ok(m.inline_image_slots===361&&m.unique_exact_source_urls===359,'source references');
 ok(m.upstream_hosts===81&&Array.isArray(gs)&&gs.length===81,'host count');
 ok(m.external_origin_slots===294&&m.first_party_or_first_party_proxy===67,'external denominator');
 ok(m.missing_intrinsic_dimensions===311,'source dimensions');
 ok(m.origin_kinds?.first_party===60&&m.origin_kinds?.jetpack_proxy===7&&
  m.origin_kinds?.external===170&&m.origin_kinds?.wikimedia_redirect===124,'source categories');
 const byHost=new Map(),allPosts=new Set();let sum=0,large=0;
 for(const g of gs) {
  if(!g||typeof g!=='object'){errors.push('empty host');continue;}
  ok(typeof g.upstream_host==='string'&&!byHost.has(g.upstream_host),'unique host');
  byHost.set(g.upstream_host,g);
  ok(Number.isInteger(g.source_references)&&g.source_references>=1,'host size');
  sum+=g.source_references;
  if(g.source_references>=4)large++;
  ok(Array.isArray(g.affected_post_ids)&&g.affected_post_ids.length>=1&&
   new Set(g.affected_post_ids).size===g.affected_post_ids.length,'host posts');
  for(const p of (g.affected_post_ids||[])){ok(Number.isInteger(p)&&p>0,'post id');allPosts.add(p);}
  ok(g.guest_browser_http===null&&g.broken_in_browser===null,'no invented guest status');
  ok(g.rehost_permission==='ITEM_LEVEL_REVIEW_HOLD','per-host rights hold');
  ok(Array.isArray(g.exact_source_samples)&&g.exact_source_samples.length>=1&&
   g.exact_source_samples.length<=2,'representative source count');
  for(const example of (g.exact_source_samples||[])){
   try{
    const h=hostInfo(example.url);
    ok(h.upstream===g.upstream_host,'upstream URL mismatch');
    ok(g.request_hosts.includes(h.requested),'request origin mismatch');
    ok(/^\d+:\d+$/.test(example.key),'image slot key');
    ok(g.affected_post_ids.includes(example.post_id),'sample post id');
   }catch(e){errors.push('bad source URL: '+e.message);}
  }
 }
 ok(sum===361,'grouped image total');
 ok(large===13&&m.hosts_with_4plus_refs===13,'high-impact hosts');
 ok(allPosts.size===65&&a.zero_image_post_ids?.length===1&&
    a.zero_image_post_ids[0]===1922&&!allPosts.has(1922),'zero-image published article');
 ok(byHost.get('commons.wikimedia.org')?.source_references===124&&
    byHost.get('commons.wikimedia.org')?.affected_post_ids.length===24,'Commons blast radius');
 ok(byHost.get('www.history.navy.mil')?.source_references===15,'Navy source count');
 ok(byHost.get('finalvestige.com')?.source_references===67,'first-party count');
 const expected=['285:5','285:2','287:5','418:1','418:2','407:1'];
 ok(Array.isArray(p0)&&p0.length===6&&p0.every((x,i)=>x.key===expected[i]),'P0 list');
 for(const x of p0){
  ok(x.visitor_http===null&&x.decoded_pixels===null&&x.wire_bytes===null&&x.proven_broken===null,'P0 guest evidence hold');
  ok(typeof x.source_url==='string'&&x.source_url.startsWith('https://'),'P0 source URL');
 }
 ok(Array.isArray(a.retrieval_observations)&&a.retrieval_observations.every(x=>
  x.browser_origin_status===null&&['image_rendered',403,404].includes(x.retriever_result)),'wrapper-vs-browser separation');
 ok(r.all_external_caching==='HOLD_ITEM_LEVEL_LICENSE'&&r.optimization_max_width_px===960&&
  r.no_enlargement===true&&r.verify_visual_identity===true&&r.wordpress_production_writes_allowed===false,'CMS safety');
 ok(r.reported_broken_42==='UNVERIFIED_IN_GUEST_BROWSER'&&
  r.claimed_76_percent_reduction==='UNMEASURED_COLD_TRANSFER'&&r.production_images_fixed===0,'measurements gate');
 ok(Array.isArray(a.sources?.legacy_parts)&&a.sources.legacy_parts.length===8&&
  a.sources.legacy_parts.every(x=>/^[a-f0-9]{40}$/.test(x.blob_sha))&&
  /^[a-f0-9]{40}$/.test(a.sources?.recent?.blob_sha||''),'input Git blobs');
 return {ok:errors.length===0,errors,metrics:{posts:m.posts,image_bearing_posts:allPosts.size,
  images:sum,host_count:gs.length,high_exposure_hosts:large,guest_broken_confirmed:0,rights_approved:false}};
}
if(typeof module!=='undefined')module.exports={hostInfo,validate};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs'),audit=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/host_blast_radius_verified_20261106.json','utf8'));
 const result=validate(audit);
 console.log(JSON.stringify(result,null,2));
 if(!result.ok)process.exitCode=1;
}

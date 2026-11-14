'use strict';
// Frozen source-only reconciliation. Does not request HTTP or modify WordPress.
function isOffsite(src){
  const m=String(src||'').replace(/&amp;/gi,'&').match(/^https?:\/\/([^/?#]+)(\/[^?#]*)?/i);
  if(!m)return false;
  const h=m[1].toLowerCase().replace(/^www\./,''),p=m[2]||'/';
  return !(h==='finalvestige.com'||(/^i[012]\.wp\.com$/.test(h)&&/^\/finalvestige\.com(?:\/|$)/i.test(p)));
}
function reconcile(csv,parts){
  if(!Array.isArray(parts)||parts.length!==8)throw Error('require eight original inventory parts');
  const qa=new Map(),media=new Map(),keys=new Set();
  const lines=String(csv).trim().split(/\r?\n/);
  if(lines[0]!=='post_id,stored_img_src_count,offsite_src_count')throw Error('bad CSV header');
  for(const line of lines.slice(1)){
    const a=line.trim().split(',').map(Number);
    if(a.length!==3||a.some(x=>!Number.isInteger(x)||x<0)||qa.has(a[0]))throw Error('bad QA row');
    qa.set(a[0],{images:a[1],offsite:a[2]});
  }
  for(const b of parts){
    if(!Array.isArray(b.posts)||!Array.isArray(b.images))throw Error('invalid inventory part');
    for(const p of b.posts){
      if(media.has(p.id))throw Error('duplicate media post');
      media.set(p.id,{images:0,offsite:0});
    }
    for(const im of b.images){
      const p=media.get(im.post_id);
      if(!p||keys.has(im.key)||im.key!==im.post_id+':'+im.slot)throw Error('bad image key');
      keys.add(im.key);p.images++;
      const offsite=isOffsite(im.source_url);
      if(offsite!==(im.source_kind==='external'||im.source_kind==='wikimedia_redirect'))
        throw Error('source kind/URL ownership disagreement at '+im.key);
      if(offsite)p.offsite++;
    }
  }
  if(qa.size!==media.size)throw Error('post-set mismatch');
  return [...qa.entries()].map(([post_id,q])=>{
    const m=media.get(post_id);
    if(!m)throw Error('missing post '+post_id);
    return {post_id,qa_images:q.images,media_images:m.images,qa_offsite:q.offsite,media_offsite:m.offsite,delta:m.offsite-q.offsite};
  }).sort((a,b)=>a.post_id-b.post_id);
}
function validate(a){
  const errors=[],ck=(condition,message)=>{if(!condition)errors.push(message)};
  if(!a||!Array.isArray(a.rows)||!Array.isArray(a.cases))return {ok:false,errors:['missing rows/cases']};
  ck(a.schema==='fv-two-wp-proxy-origin-reconciliation-v1','schema');
  ck(a.rows.length===61&&new Set(a.rows.map(r=>r.post_id)).size===61,'post cardinality');
  ck(a.rows.every(r=>Number.isInteger(r.post_id)&&r.qa_images===r.media_images&&r.delta===r.media_offsite-r.qa_offsite&&r.qa_offsite<=r.qa_images&&r.media_offsite<=r.media_images),'row arithmetic');
  ck(a.rows.reduce((n,r)=>n+r.media_images,0)===355,'image count');
  ck(a.rows.reduce((n,r)=>n+r.qa_offsite,0)===286,'QA origin count');
  ck(a.rows.reduce((n,r)=>n+r.media_offsite,0)===288,'Media origin count');
  ck(JSON.stringify(a.rows.filter(r=>r.delta).map(r=>[r.post_id,r.delta]))==='[[285,1],[291,1]]','delta locations');
  ck(a.summary.posts===61&&a.summary.images===355&&a.summary.qa_offsite===286&&a.summary.media_offsite===288&&a.summary.delta===2&&a.summary.unchanged_rows===59,'summary');
  ck(a.summary.reported_broken_42==='BROWSER_UNCONFIRMED'&&a.summary.proposed_76_pct==='NOT_MEASURED','claim integrity');
  ck(a.sources.qa.pr===154&&/^[0-9a-f]{40}$/.test(a.sources.qa.blob)&&a.sources.media.pr===183&&/^[0-9a-f]{40}$/.test(a.sources.media.summary_blob)&&a.sources.media.parts.length===8&&a.sources.media.parts.every((p,i)=>p.path==='qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json'&&/^[0-9a-f]{40}$/.test(p.blob)),'source provenance');
  ck(a.cases.length===2,'case length');
  const pins=[
    ['285:1','https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1','www.squawkpoint.com'],
    ['291:0','https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1','text-message.blogs.archives.gov']
  ];
  for(let i=0;i<a.cases.length;i++){
    const c=a.cases[i],x=pins[i];if(!x){errors.push('unexpected case');continue}
    ck(c.key===x[0]&&c.stored_src===x[1]&&c.target_origin===x[2]&&c.offsite===true&&isOffsite(c.stored_src),'exact source '+i);
    ck(c.retriever==='IMAGE_RENDERED'&&c.retriever_http_status===null&&c.origin_http_status===null&&c.visitor_http_status===null&&c.visitor_natural_px===null&&c.visitor_wire_bytes===null,'status custody '+i);
    ck(c.native_px===null&&c.rights_cleared===false&&c.exact_primary_binary_confirmed===false&&c.cache_allowed===false&&c.replacement_allowed===false&&c.max_conditional_width_px===960&&c.no_upscale===true,'image rights/sizing '+i);
  }
  ck(a.root_cause==='NOT_VERIFIED_SITEQA_PER_URL_SNAPSHOT_UNAVAILABLE','causality HOLD');
  ck(a.release.siteqa_browser_collector_touched===false&&a.release.homepage_design_touched===false&&a.release.wp_production_write===false&&a.release.media_downloads===0&&a.release.rehosted===0&&a.release.deploy===false&&a.release.spending_usd===0,'release restrictions');
  ck(a.current_issues.actual_guest_broken===null&&a.current_issues.actual_visitor_weight_reduction_pct===null,'metrics integrity');
  return {ok:errors.length===0,errors};
}
if(typeof module!=='undefined')module.exports={isOffsite,reconcile,validate};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module){
  try{
    const fs=require('node:fs');
    if(process.argv.length!==3)throw Error('Usage: node validate_proxy_origin_delta_20261114.cjs audit.json');
    const x=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
    console.log(JSON.stringify(x,null,2));if(!x.ok)process.exitCode=1;
  }catch(e){console.error('INVALID_MEDIA_AUDIT '+e.message);process.exitCode=2}
}

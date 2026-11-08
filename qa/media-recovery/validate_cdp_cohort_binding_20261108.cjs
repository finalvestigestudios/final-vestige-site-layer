'use strict';
/** Offline source-cohort binding for the existing cold-CDP image comparator; no network or CMS writes. */
const PINNED='1b83b72040a45374e614cc31b82216b3b06e89d7';
const EXPECT={legacy:[61,355],expanded:[66,361]};
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const https=x=>{try{const u=new URL(x);return u.protocol==='https:'&&!!u.hostname&&!u.username&&!u.password}catch{return false}};
function sources(m,cohort,reasons){
 const spec=EXPECT[cohort],c=m?.[cohort];
 if(!spec){reasons.push('unknown_cohort');return null}
 if(m?.schema!=='fv-sitewide-wire-cohort-manifest-v1'||
    m?.data_cohorts_not_interchangeable!==true||
    m?.rights_and_post_edits_authorized!==false||
    !Array.isArray(m.rows)||!obj(c)||c.expected_posts!==spec[0]||
    c.expected_slots!==spec[1]||!Array.isArray(c.post_ids)||
    c.post_ids.length!==spec[0]||new Set(c.post_ids).size!==spec[0]||
    !obj(m.expanded)||m.rows.length!==m.expanded.expected_posts){
   reasons.push('manifest_schema_counts_or_cohort_drift');return null
 }
 const rows=new Map(),chosen=new Map();
 for(const r of m.rows){
  if(!Number.isSafeInteger(r?.id)||r.id<=0||rows.has(r.id)||
     !Array.isArray(r.slots)||(r.post_url!==null&&!https(r.post_url))){
   reasons.push('invalid_manifest_row');return null
  }
  rows.set(r.id,r);
 }
 let n=0;
 for(const id of c.post_ids){
   const row=rows.get(id);
   if(!row){reasons.push('missing_manifest_post:'+id);continue}
   const slots=new Map();
   for(const x of row.slots){
     if(!x||typeof x.key!=='string'||!new RegExp('^'+id+':\\d+$').test(x.key)||
        slots.has(x.key)||!https(x.source_url)){
       reasons.push('invalid_manifest_slot:'+id);continue
     }
     slots.set(x.key,x.source_url);n++;
   }
   chosen.set(id,{url:row.post_url,slots});
 }
 if(chosen.size!==spec[0]||n!==spec[1])reasons.push('manifest_post_or_slot_count_mismatch');
 return chosen;
}
function checkRun(run,expected,label,reasons){
 if(!obj(run)||run.status!=='complete_browser_image_census'||run.mode!=='all'||
    !['390x844','1440x900'].includes(run.viewport)||
    run.image_census_coverage?.complete!==true||
    run.image_census_coverage?.confirmed_broken_count!==0||
    run.confirmed_broken_count!==0||run.requested_pages!==expected.size||
    run.verified_pages!==expected.size||!Array.isArray(run.pages)||
    run.pages.length!==expected.size||
    run.run_profile?.cache_disabled!==true||run.run_profile?.service_worker_bypassed!==true){
   reasons.push(label+':incomplete_or_unsafe_collector');return;
 }
 const seen=new Set();
 for(const p of run.pages){
  if(!expected.has(p?.post_id)||seen.has(p.post_id)){
    reasons.push(label+':duplicate_or_unknown_post');continue
  }
  seen.add(p.post_id);
  const e=expected.get(p.post_id);
  if(e.url!==null&&p.url!==e.url)reasons.push(label+':post_url_drift:'+p.post_id);
  if(p.page_result!=='inspected_browser'||p.scroll_coverage?.complete!==true||
     p.scroll_coverage?.state!=='full_height_scanned'||
     p.image_census?.complete!==true||p.confirmed_broken_count!==0)
    reasons.push(label+':incomplete_article:'+p.post_id);
  if(!Array.isArray(p.stored_images)||p.stored_image_count!==e.slots.size||
     p.stored_images.length!==e.slots.size){
    reasons.push(label+':missing_or_extra_image_slots:'+p.post_id);continue;
  }
  const keys=new Set();
  for(const s of p.stored_images){
    if(keys.has(s?.image_key)||!e.slots.has(s?.image_key)||
       s.stored_url!==e.slots.get(s.image_key))
      reasons.push(label+':missing_or_drifted_source:'+p.post_id);
    keys.add(s?.image_key);
  }
  if(keys.size!==e.slots.size)reasons.push(label+':duplicate_image_slots:'+p.post_id);
  if(e.slots.size===0&&(p.matched_article_network_requests!==0||
     p.article_image_wire_bytes_total!==0))
    reasons.push(label+':invented_zero_image_bytes:'+p.post_id);
 }
 if(seen.size!==expected.size)reasons.push(label+':post_census_incomplete');
}
function audit(m,before,after,cohort='expanded',compare=null){
 const reasons=[],expected=sources(m,cohort,reasons);
 if(expected){checkRun(before,expected,'baseline',reasons);checkRun(after,expected,'candidate',reasons)}
 if(before?.viewport!==after?.viewport||before?.browser_product!==after?.browser_product||
    JSON.stringify(before?.run_profile)!==JSON.stringify(after?.run_profile))
   reasons.push('unpaired_browser_or_cache_configuration');
 const base={schema:'fv-cdp-immutable-cohort-gate-v1',cohort,
   expected_posts:EXPECT[cohort]?.[0]??null,expected_slots:EXPECT[cohort]?.[1]??null,
   pinned_manifest_git_blob:PINNED,mixed_date_sources:cohort==='expanded',
   visitor_confirmed_42_broken:false,sitewide_76_percent_claim_permitted:false,
   production_repair_authorized:false,rights_clearance:false,wp_write_authorized:false};
 if(reasons.length)return {...base,state:'HOLD',reasons:[...new Set(reasons)],lab_pair:null};
 if(typeof compare!=='function')return {...base,state:'BOUND_AWAITING_CDP',reasons:[],lab_pair:null};
 const x=compare(before,after);
 if(x?.state!=='LAB_PAIR_MEASURED')return {...base,state:'HOLD',reasons:['cold_cdp_pair_failed'],lab_pair:null};
 return {...base,state:'BOUND_LAB_PAIR_ONLY',reasons:[],
   lab_pair:{post_count:x.post_count,baseline_cdp_bytes:x.baseline_cdp_bytes,
     candidate_cdp_bytes:x.candidate_cdp_bytes,reduction_percent:x.reduction_percent},
   caveat:'Mixed-date source ledger and single lab pair; not live 66-post image repairs, user traffic, field CWV, rights release, or 76% sitewide proof.'};
}
function gitBlob(s){const c=require('node:crypto');return c.createHash('sha1').update('blob '+Buffer.byteLength(s)+'\0'+s).digest('hex')}
if(require.main===module){
 try{
  const fs=require('node:fs'),a=process.argv.slice(2);
  if(a.length<3||a.length>4)throw Error('usage: node validate_cdp_cohort_binding_20261108.cjs MANIFEST BEFORE AFTER [legacy|expanded]');
  const raw=fs.readFileSync(a[0],'utf8');
  if(gitBlob(raw)!==PINNED)throw Error('pinned Git source manifest changed; new inventory/rights review required');
  const compare=require('./compare_cold_image_wire_v1.cjs').compareColdImageWire;
  const out=audit(JSON.parse(raw),JSON.parse(fs.readFileSync(a[1],'utf8')),
    JSON.parse(fs.readFileSync(a[2],'utf8')),a[3]||'expanded',compare);
  console.log(JSON.stringify(out,null,2));if(out.state!=='BOUND_LAB_PAIR_ONLY')process.exitCode=2;
 }catch(e){console.error('SOURCE_COHORT_HOLD '+String(e?.message||e));process.exitCode=2}
}
module.exports={audit,sources,checkRun,gitBlob,PINNED};

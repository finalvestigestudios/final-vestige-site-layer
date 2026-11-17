'use strict';
/* Native Node regression suite. Generates synthetic QA-count fixture from the
 * immutable frozen snapshot; cross-PR comparison must separately use the
 * actual #154 CSV as recorded in the machine audit. No media/network access. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {reconcile}=require('./validate_census_reconciliation_20261104.cjs');
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8'));
const original=read('census_reconciliation_and_duplicate_src_20261104.json');
const parts=Array.from({length:8},(_,i)=>read('parts/'+String(i+1).padStart(2,'0')+'.json'));
const images=parts.flatMap(p=>p.images);
const sites=new Map();for(const im of images){
 let s=sites.get(im.post_id)||{n:0,off:0};s.n++;
 if(['external','wikimedia_redirect'].includes(im.source_kind))s.off++;
 sites.set(im.post_id,s);
}
let fakeCsv='post_id,stored_img_src_count,offsite_src_count\n';
for(const [id,v] of [...sites].sort((a,b)=>a[0]-b[0])){
 fakeCsv+=id+','+v.n+','+(v.off-([285,291].includes(id)?1:0))+'\n';
}
let checks=0;
function check(name,action){
 const a=structuredClone(original),p=structuredClone(parts);
 action(a,p);
 const out=reconcile(a,p,fakeCsv);
 assert.equal(out.ok,false,name+' must fail closed');
 checks++;
}
const baseline=reconcile(original,parts,fakeCsv);
assert.equal(baseline.ok,true,JSON.stringify(baseline.errors));
assert.equal(baseline.metrics.unique_exact_src,353);
assert.deepEqual(baseline.metrics.discrepant_posts,[285,291]);
assert.deepEqual(baseline.metrics.same_exact_src_groups,[['213:2','213:6'],['291:2','291:5']]);
checks++;
check('invented guest status',(a)=>{a.duplicates[0].visitor_http_status=200});
check('altered alt provenance',(a)=>{a.duplicates[1].slots[0].alt='invented'});
check('proxy upstream wrongly first-party',(a,p)=>{p.flatMap(x=>x.images).find(x=>x.key==='291:0').source_kind='jetpack_proxy'});
check('TMI proxy wrongly first-party',(a,p)=>{p.flatMap(x=>x.images).find(x=>x.key==='285:1').source_kind='jetpack_proxy'});
check('fabricated wire reduction',(a)=>{a.metrics.image_transfer_reduction_76pct=76});
check('unlicensed caching',(a)=>{a.source_candidates[0].permission_to_cache=true});
check('production write authorization',(a)=>{a.gate.allow_wp_write=true});
check('false offsite count',(a)=>{a.metrics.media_offsite=286});
check('lost snapshot slot',(a,p)=>{p[0].images.pop()});
check('unearned original uniqueness',(a)=>{a.metrics.unique_exact_source_urls=355});
check('misattributed archive rights',(a)=>{a.source_candidates[1].rights='CLEARED'});
console.log(checks+'/'+checks+' census reconciliation and adversarial regression assertions passed');

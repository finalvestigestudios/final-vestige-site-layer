'use strict';
/** Native Node: node --test qa/media-recovery/test_host_exposure_20261101.cjs */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {validate,FIXED_SHAS}=require('./validate_host_exposure_20261101.cjs');
const data={
 parts:Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(path.join(__dirname,'parts',String(i+1).padStart(2,'0')+'.json'),'utf8'))),
 ledger:JSON.parse(fs.readFileSync(path.join(__dirname,'host_exposure_20261101.json'),'utf8')),
 large:JSON.parse(fs.readFileSync(path.join(__dirname,'large_first_party_20261101.json'),'utf8'))
};
const copy=()=>JSON.parse(JSON.stringify(data));
test('all eight immutable source Git blob SHAs match',()=>{
 for(let i=0;i<8;i++){
  const b=fs.readFileSync(path.join(__dirname,'parts',String(i+1).padStart(2,'0')+'.json'));
  const sha=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
  assert.equal(sha,FIXED_SHAS[i]);
 }
});
test('real 61/355/288/286/79 baseline passes, P0 browser status remains unknown',()=>{
 const r=validate(data.parts,data.ledger,data.large);
 assert.equal(r.ok,true,r.errors.join('; '));assert.equal(r.summary.visitor_failures_established,null);
});
const mutations=[
 ['host count altered',x=>x.ledger.host_groups[0].refs++],
 ['host group removed',x=>x.ledger.host_groups.pop()],
 ['host image membership altered',x=>x.ledger.host_groups[0].image_keys[0]='999:1'],
 ['census HTTP 200 fabricated',x=>x.parts[0].images[0].actual_http_status=200],
 ['census broken-in-browser fabricated',x=>x.parts[0].images[0].broken_in_browser=true],
 ['reported 42 asserted verified',x=>x.ledger.accuracy_gates.claimed_42_broken_images_confirmed=true],
 ['reported 76 asserted measured',x=>x.ledger.accuracy_gates.claimed_76_percent_saved_measured=true],
 ['invented percentage inserted',x=>x.ledger.accuracy_gates.measured_reduction_percent=76],
 ['42 production repairs invented',x=>x.ledger.accuracy_gates.production_media_repaired=42],
 ['oversized original byte corrupted',x=>x.large.rows[0].original_bytes++],
 ['13 originals changed to 14',x=>x.ledger.scope.oversized_originals_over_1_5_mib=14],
 ['retriever 404 promoted to guest HTTP',x=>x.ledger.priority_cases[0].guest_browser_status=404],
 ['retriever 404 promoted to origin HTTP',x=>x.ledger.priority_cases[0].origin_status=404],
 ['cache permission invented',x=>x.ledger.priority_cases[0].cache_authorized=true],
 ['copyright approval invented',x=>x.ledger.priority_cases[0].rights_clear=true],
 ['WordPress publish authorization invented',x=>x.ledger.priority_cases[0].wordpress_publish_authorized=true],
 ['819px image upscaled to 960px',x=>x.ledger.priority_cases[0].conditional_width_px=960],
 ['unknown dimensions filled without master',x=>x.ledger.priority_cases[2].conditional_width_px=960],
 ['published image URL swapped',x=>x.ledger.priority_cases[0].published_url+='?updated'],
 ['retriever method falsely relabeled Chrome',x=>x.ledger.priority_cases[0].wrapper_method='logged_out_chrome'],
 ['repeated image URL proof suppressed',x=>x.ledger.duplicate_exact_urls=[]],
 ['288 refs conflated with 286 unique URLs',x=>x.ledger.scope.offsite_refs=286],
 ['external Jetpack proxy origin rewritten',x=>x.ledger.proxy_upstream_exceptions[0].upstream_origin_host='finalvestige.com'],
 ['inventory source hostname fabricated',x=>x.parts[0].images[0].source_host='made-up.host'],
 ['frozen source blob SHA mutated',x=>x.ledger.baseline_part_blob_sha['03']='0'.repeat(40)],
 ['unlicensed localization permitted',x=>x.parts[0].images[0].allowed_to_localize=true],
 ['max image width silently raised to 1280',x=>x.parts[0].images[0].target_max_width_px=1280],
 ['P0 case order changed',x=>x.ledger.priority_cases.reverse()]
];
for(const [label,mutate]of mutations)test('fail closed: '+label,()=>{
 const x=copy();mutate(x);const r=validate(x.parts,x.ledger,x.large);
 assert.equal(r.ok,false,label+' unexpectedly accepted');assert.ok(r.errors.length>0);
});

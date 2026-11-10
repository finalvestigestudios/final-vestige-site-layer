'use strict';
const fs=require('node:fs'),path=require('node:path');
const {strict:assert}=require('node:assert');
const EXPECTED_URLS={
  "256:0": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%201916.jpg?width=1280",
  "256:1": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Map%20of%20Black%20Tom%20Island%2C%20Jersey%20City%2C%20New%20Jersey%20-%20showing%20area%20damaged%20by%20explosion%20and%20fire%2C%20July%2030th%201916.%20LOC%202010588272.jpg?width=1280",
  "256:2": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20firefighters%20-%201916.jpg?width=1280",
  "256:3": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20Men%20on%20pier%20-%201916.jpg?width=1280",
  "256:4": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Diving%20at%20Black%20Tom%20LCCN2014702309.jpg?width=1280",
  "256:5": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Girl%20with%20relics%20from%20the%20Black%20Tom%20Explosion.png?width=1280",
  "256:6": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20electrical%20poles%20-%201916.jpg?width=1280"
};
const SLOTS=Object.keys(EXPECTED_URLS);
function validate(batch,full,previous){
 assert.equal(batch.rows.length,7);assert.equal(full.rows.length,288);assert.equal(previous.rows.length,288);
 assert.equal(full.counts.researched_unique,222);assert.equal(full.counts.unresearched,66);
 assert.equal(full.counts.total_evidence_records,previous.counts.total_evidence_records+7);
 assert.equal(full.counts.guest_browser_confirmed_broken,0);
 assert.equal(full.counts.wire_reduction_76_percent_measured,false);
 const seen=new Set();
 for(const b of batch.rows){
  assert.ok(SLOTS.includes(b.slot));assert.ok(!seen.has(b.slot));seen.add(b.slot);
  assert.equal(b.published_src,EXPECTED_URLS[b.slot]);
  assert.equal(b.post_id,256);assert.equal(b.web_retriever,'TOOL_INACCESSIBLE_NOT_ORIGIN_STATUS');
  for(const k of ['origin_http_status','guest_http_status','guest_current_src','guest_decoded_px','guest_wire_bytes','guest_broken'])assert.equal(b[k],null);
  for(const k of ['rights_cleared','download_authorized','cache_authorized','wordpress_media_upload_authorized','post_rewrite_authorized','exact_binary_match'])assert.equal(b[k],false);
  assert.equal(b.license_review,'HOLD');assert.equal(b.published_width_query,1280);
  assert.ok(/^https:\/\//.test(b.catalog_url));const [w,h]=b.catalog_px, [tw,th]=b.conditional_960px;
  assert.ok(w>0&&h>0&&tw>0&&th>0&&tw<=960&&tw<=w&&th<=h);
  assert.equal(tw,Math.min(960,w));assert.equal(th,w<=960?h:Math.round(h*960/w));
  if(b.slot==='256:1')assert.ok(b.rights_observation.includes('PRIVATE'));
  if(b.slot==='256:4')assert.ok(b.visual_integrity_note.includes('UNEXPLODED'));
 }
 for(const r of full.rows){
   const old=previous.rows.find(x=>x.slot===r.slot);assert.ok(old);
   if(!SLOTS.includes(r.slot))assert.deepEqual(r,old);
   else{assert.equal(r.stored_url,EXPECTED_URLS[r.slot]);assert.equal(r.guest_http_status,null);assert.equal(r.guest_broken,null);
      assert.equal(r.evidence.length,1);assert.equal(r.candidate_sources.length,1);
      assert.equal(r.cache_authorized,false);assert.equal(r.post_rewrite_authorized,false);
   }
 }
 assert.equal(seen.size,7);
 const pending=full.rows.filter(r=>r.evidence.length===0).length;
 assert.equal(pending,66);
 return true;
}
module.exports={validate};
if(require.main===module){const root=path.resolve(__dirname);
 const batch=JSON.parse(fs.readFileSync(path.join(root,'blacktom_256_seven_loc_newspaper_rights_20261110.json')));
 const full=JSON.parse(fs.readFileSync(path.join(root,'coverage_222_exact_pr1703_20261110.json')));
 const prev=JSON.parse(fs.readFileSync(path.join(root,'coverage_215_exact_pr1703_20261110.json')));
 validate(batch,full,prev);console.log('PASS Black Tom seven exact-source and 288-slot conservation');
}

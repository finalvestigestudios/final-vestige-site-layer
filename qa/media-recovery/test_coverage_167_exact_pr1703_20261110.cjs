'use strict';
/* Run: node --test qa/media-recovery/test_coverage_167_exact_pr1703_20261110.cjs */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {validate}=require('./validate_coverage_167_exact_pr1703_20261110.cjs');
const root=path.resolve(__dirname,'../..'),read=(p)=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const source=read('qa/media-recovery/coverage_167_exact_pr1703_20261110.json');
const copy=x=>JSON.parse(JSON.stringify(x));
const documents={
 census:read(source.frozen_source.path),
 prior:read(source.prior_reconciliation.path),
 batches:source.batch_sources.map(s=>({path:s.file,sha:s.blob_sha,obj:read(s.file)}))
};
test('replay 93+76 minus 2 overlapping =167 exact sources against 288 frozen slots',()=>{
 const result=validate(source,documents);assert.deepEqual(result.errors,[]);assert.equal(result.stats.researched,167);assert.equal(result.stats.pending,121);assert.equal(result.stats.records,172);
});
test('all 14 current input files match exact Git blob IDs',()=>{
 for(const s of [source.frozen_source,source.prior_reconciliation,...source.batch_sources.map(x=>({path:x.file,blob_sha:x.blob_sha}))]){
  const bytes=fs.readFileSync(path.join(root,s.path));
  const hash=crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');
  assert.equal(hash,s.blob_sha,s.path);
 }
});
const adversarial=[
 ['invented visitor 404',x=>x.rows[0].guest_http_status=404],
 ['invented visitor healthy',x=>x.rows[0].guest_broken=false],
 ['invented decoded dimensions',x=>x.rows[0].guest_decoded_px=[960,600]],
 ['invented wire bytes',x=>x.rows[0].guest_wire_bytes=240],
 ['inflated research coverage',x=>x.counts.researched_unique=168],
 ['fake 76 percent savings',x=>x.counts.wire_reduction_76_percent_measured=true],
 ['42 falsely confirmed',x=>x.counts.reported_42_broken_browser_confirmed=true],
 ['rights release without proof',x=>x.rows[0].rights_cleared=true],
 ['unapproved cache',x=>x.rows[0].cache_authorized=true],
 ['unapproved WordPress upload',x=>x.rows[0].wordpress_media_upload_authorized=true],
 ['unapproved Gutenberg rewrite',x=>x.rows[0].post_rewrite_authorized=true],
 ['candidate rights override',x=>x.rows.find(r=>r.candidate_sources.length).candidate_sources[0].item_rights_cleared=true],
 ['upsized derivative',x=>x.rows.find(r=>r.candidate_sources.length).candidate_sources[0].conditional_960px=[961,700]],
 ['wrong image-source SHA',x=>x.rows.find(r=>r.evidence.length).evidence[0].blob_sha='fake'],
 ['missing source-evidence row',x=>x.rows.find(r=>r.evidence.length).evidence=[]],
 ['double-counted row',x=>x.rows.push(copy(x.rows[0]))],
 ['missing census row',x=>x.rows.pop()],
 ['wrong overlap',x=>x.overlap_slots_prior_and_new=[]],
 ['misordered P0',x=>x.original_six_p0_guest_queue.reverse()],
 ['stored bytes mislabel',x=>x.counts.oversized_stored_original_bytes=1],
 ['wrong new evidence count',x=>x.counts.total_evidence_records=173]
];
for(const [name,mut] of adversarial)test('reject '+name,()=>{const x=copy(source);mut(x);assert.equal(validate(x).ok,false)});
test('reject exact original source drift against Git-backed frozen census',()=>{
 const x=copy(source);x.rows[0].stored_url='https://example.com/not-the-original.jpg';
 assert.equal(validate(x,documents).ok,false);
 assert.ok(validate(x,documents).errors.some(e=>e.startsWith('census_source_drift:')));
});
test('reject tampered batch source URL during full archive replay',()=>{
 const docs=copy(documents);
 const r=docs.batches[0].obj.rows[0];
 for(const k of ['stored_url','stored_original_url','original_url','published_src','stored_source_url'])if(typeof r[k]==='string'){r[k]='https://example.com/fictional.jpg';break}
 const actual=validate(source,docs);assert.equal(actual.ok,false);assert.ok(actual.errors.some(e=>e.startsWith('source_mismatch:')));
});
test('do not conflate archival catalog geometry with visitor bytes',()=>{
 const rows=source.rows.filter(r=>r.candidate_sources.some(c=>c.conditional_960px!==null));
 assert.ok(rows.length>0);assert.ok(rows.every(r=>r.guest_wire_bytes===null&&r.guest_decoded_px===null&&r.guest_broken===null));
});

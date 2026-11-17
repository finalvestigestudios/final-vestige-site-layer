'use strict';
// Native Node: node qa/media-recovery/test_pueblo_280_20261104.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {validate}=require('./validate_pueblo_280_20261104.cjs');
const root=path.resolve(__dirname,'../..');
const partRaw=fs.readFileSync(path.join(root,'qa/media-recovery/parts/03.json'));
const part=JSON.parse(partRaw.toString('utf8'));
const blobSha=crypto.createHash('sha1').update('blob '+partRaw.length+'\0').update(partRaw).digest('hex');
const audit=require('./pueblo_280_nhhc_primary_20261104.json');
function copy(x){return JSON.parse(JSON.stringify(x));}
function expectRejected(label,edit,sourceOverride=part,sha=blobSha){
 const x=copy(audit);edit(x);const errs=validate(x,sourceOverride,sha);
 assert.ok(errs.length>0,label+' incorrectly accepted');
}
assert.equal(blobSha,'49183f66f880f7c4dfd363acca906876877f2e5e','frozen source bytes changed');
assert.deepEqual(validate(audit,part,blobSha),[],'valid six-slot audit must pass');
const mutations=[
 ['invented image failure',x=>x.images[0].retrieval.broken_for_visitors=true],
 ['fabricated 404',x=>x.images[0].retrieval.actual_origin_http_status=404],
 ['fabricated guest 502',x=>x.images[1].retrieval.guest_browser_http_status=502],
 ['fake content type',x=>x.images[2].retrieval.mime_type='image/jpeg'],
 ['fake decoded image',x=>x.images[3].retrieval.decoded=true],
 ['fake width',x=>x.images[4].retrieval.natural_width_px=1024],
 ['fake transferred bytes',x=>x.images[5].retrieval.wire_bytes=1000],
 ['changed original source',x=>x.images[0].original_src='https://example.com/alternate.jpg'],
 ['changed historic alt',x=>x.images[1].original_alt='fabricated'],
 ['changed slot key',x=>x.images[2].key='280:20'],
 ['wrong post',x=>x.images[3].post_id=281],
 ['duplicate slot',x=>x.images[4].key='280:3'],
 ['swapped photograph rows',x=>{const t=x.images[0];x.images[0]=x.images[1];x.images[1]=t;}],
 ['missing source row',x=>{x.images.pop();}],
 ['wrong accession',x=>x.images[0].archive.catalog_id='USN 1129208'],
 ['wrong catalog page',x=>x.images[1].archive.catalog_url=x.images[2].archive.catalog_url],
 ['claims binary match without SHA',x=>x.images[2].archive.original_binary_identity_verified=true],
 ['invented binary hash',x=>x.images[3].archive.source_binary_sha256='123'],
 ['mislabeled Banner same photograph',x=>x.images[4].archive.mapping_kind='EXACT_CATALOG_ACCESSION'],
 ['drops Banner warning',x=>x.images[4].review_flag=null],
 ['invented highres width',x=>x.images[5].derivative.source_catalog_master_width_px=1280],
 ['upscaled rendition',x=>x.images[0].derivative.max_width_px=1280],
 ['mismatched proportional height',x=>x.images[3].derivative.conditional_height_px=999],
 ['disables no-upscale',x=>x.images[4].derivative.no_upscale=false],
 ['false licensed status',x=>x.images[0].rights.license='CC0'],
 ['permits WordPress upload',x=>x.images[1].rights.wordPress_upload_allowed=true],
 ['permits cache',x=>x.images[2].rights.local_cache_allowed=true],
 ['permits post rewrite',x=>x.images[3].rights.post_rewrite_allowed=true],
 ['false broken count verified',x=>x.frozen.reported_broken_42='VERIFIED'],
 ['false 76 percent measured',x=>x.frozen.claimed_wire_reduction_76_percent='MEASURED'],
 ['faked live CMS image failure',x=>x.live_wordpress_readonly.guest_browser_successes=0],
 ['faked six matching live ALT strings',x=>x.live_wordpress_readonly.exact_alt_matches_frozen=5],
 ['faked live HTML dimensions',x=>x.live_wordpress_readonly.images_with_html_width_and_height=6],
 ['changed live modified timestamp',x=>x.live_wordpress_readonly.modified_utc='2026-11-04T00:00:00'],
 ['wrong 61 post baseline',x=>x.frozen.baseline_posts=60],
 ['changed tool wrapper outcome',x=>x.images[4].retrieval.tool_outcome='ORIGIN_404'],
 ['misstates image search evidence',x=>x.images[5].retrieval.image_search_displayed=false],
 ['changes frozen blob hash',x=>x.frozen.git_blob_sha='deadbeef'],
 ['claims live repair',x=>x.results.production_replacements=1],
 ['claims actual guest failure',x=>x.results.guest_browser_failures_verified=1]
];
for(const [label,fn] of mutations)expectRejected(label,fn);
expectRejected('incorrect live blob SHA',()=>{},part,'deadbeef');
const modifiedPart=copy(part);
modifiedPart.images.find(x=>x.key==='280:5').alt='modified original archive';
expectRejected('drifted original source inventory',()=>{},modifiedPart);
console.log('PASS '+(mutations.length+4)+' checks: frozen Git blob; valid ledger; '+mutations.length+' mutations; wrong live SHA; changed source');

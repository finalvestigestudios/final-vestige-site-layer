'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_lituya_277_20261107.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'lituya_277_six_sources_20261107.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(fixture));
test('authentic archived-source evidence passes while unresolved statuses stay unknown',()=>assert.deepEqual(validate(clone()),[]));
const cases=[
 ['invented browser failure count',a=>a.actual_browser_failure_count=42],
 ['fabricated 76 percent achieved',a=>a.reported_76_percent_transfer_reduction_measured=true],
 ['fabricated transfer bytes',a=>a.transfer_bytes_from_browser=9999],
 ['baseline count drift',a=>a.original_census.baseline_image_refs=361],
 ['unreconciled 286 vs 288 hidden',a=>a.original_census.delta_unreconciled=false],
 ['oversized original storage disguised as transfer',a=>a.oversize_wp_originals_stored_bytes_from_other_inventory=900],
 ['drop an image',a=>a.slots.pop()],
 ['duplicate an image',a=>a.slots[1].key=a.slots[0].key],
 ['substitute unrelated hosted image',a=>a.slots[2].source_url='https://example.org/other.jpg'],
 ['source date secretly relabeled current',a=>a.slots[0].source_snapshot_date='2026-11-07'],
 ['commercial retrieval failure misreported as origin 404',a=>a.slots[3].web_viewer.origin_http_status=404],
 ['publisher retriever success misreported as HTTP 200',a=>a.slots[0].web_viewer.origin_http_status=200],
 ['guessed MIME',a=>a.slots[4].visitor_browser.content_type='image/png'],
 ['guessed natural width',a=>a.slots[4].visitor_browser.natural_width=750],
 ['guessed actual visitor bytes',a=>a.slots[5].visitor_browser.transferred_bytes=489000],
 ['unverified visitor decode called pass',a=>a.slots[0].visitor_browser.decode_ok=true],
 ['unlicensed caching preapproved',a=>a.slots[0].rights_to_cache=true],
 ['unreviewed exact replacement approved',a=>a.slots[4].exact_replacement_approved=true],
 ['WordPress media item fabricated',a=>a.slots[5].wp_media_item=12],
 ['wrong visual classification on composite',a=>a.slots[0].visual_class='clean_aerial'],
 ['composite clarification removed',a=>a.slots[0].recommended_alt_unpublished='Photograph of bay'],
 ['arrows removed from editorial clarification',a=>a.slots[4].recommended_alt_unpublished='Bay photo'],
 ['NASA false-color removed from alt correction',a=>a.slots[5].recommended_alt_unpublished='Satellite image of bay'],
 ['inflate original 720 NASA pixels to 960',a=>a.candidates.find(c=>c.candidate_id==='NASA-LITUYA-2020').preview_max_px={width:960,height:640}],
 ['change true NASA original dimensions',a=>a.candidates.find(c=>c.candidate_id==='NASA-LITUYA-2020').native_px={width:960,height:640}],
 ['invent USGS catalog image native dimensions',a=>a.candidates.find(c=>c.candidate_id==='USGS-LITUYA-1958-AERIAL').native_px={width:960,height:750}],
 ['claim byte-exact photo match',a=>a.candidates[0].identity_verified=true],
 ['delete source credit',a=>a.candidates[0].creator_credit=''],
 ['bad archive URL',a=>a.candidates[2].catalog_url='http://example.org/file'],
 ['nonexistent candidate injected',a=>a.slots[2].candidate_ids=['NONSENSE']],
 ['allow third-party downloads',a=>a.media_staging_plan.authorized_to_download=true],
 ['allow production writes',a=>a.media_staging_plan.word_press_changes=1],
 ['allow publication',a=>a.media_staging_plan.authorized_to_publish=true],
 ['remove SHA-256 provenance requirement',a=>a.media_staging_plan.when_approved='publish after review']
];
for(const [title,mutate] of cases) test('rejects '+title,()=>{
  const altered=clone();mutate(altered);assert.notDeepEqual(validate(altered),[],title);
});

'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_wp_live_121_15_decimal_20261108.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'wp_live_121_15_decimal_threshold_20261108.json'),'utf8'));
test('unmodified authoritative CMS-only snapshot is internally consistent',()=>{
  assert.deepEqual(validate(original),[]);
});
const scenarios=[
['reported 42 browser-broken claimed',a=>a.release.reported_42_browser_broken_verified=true],
['fabricated 76 percent savings',a=>a.release.reported_76_transfer_reduction_measured=true],
['invented live browser 200',a=>a.rows[0].guest_browser_http=200],
['invented local file hash',a=>a.rows[0].binary_content_hash_sha256='deadbeef'],
['unverified NOAA file hash treated as verified',a=>a.target_source_custody['2148'].byte_identity_sha1_verified_locally=true],
['decimal threshold row missing',a=>a.rows=a.rows.filter(r=>r.media_id!==1714)],
['below threshold image',a=>a.rows[0].original_stored_bytes=1499999],
['stored original bytes mislabeled network',a=>a.rows[0].bytes_are_storage_not_transfer=false],
['wrong aspect ratio',a=>a.rows[0].conditional_derivative_px=[960,960]],
['invented transfer byte value',a=>a.rows[0].guest_wire_bytes=12345],
['unlicensed WordPress upload',a=>a.rows[0].wp_upload_authorized=true],
['unlicensed Gutenberg rewrite',a=>a.rows[0].post_rewrite_authorized=true],
['fictional production writes',a=>a.release.wordpress_production_writes=1],
['negative native width',a=>a.rows[0].wp_metadata_native_px[0]=-1],
['false rights clearance',a=>a.rows[0].rights_status='CLEARED'],
['new NOAA file declared post-used without source readback',a=>a.target_source_custody['2148'].usage_in_66_live_posts='CONFIRMED'],
['Halifax map asserted public-domain without proof',a=>a.target_source_custody['1714'].rights_status='PUBLIC_DOMAIN'],
['Halifax original source changed',a=>a.target_source_custody['1714'].raw_gutenberg_img_src_confirmed='https://evil.example/map.png'],
['duplicate WP media id',a=>a.rows[1].media_id=a.rows[0].media_id],
['duplicate WP original URL',a=>a.rows[1].original_url=a.rows[0].original_url],
['wrong first-party source host',a=>a.rows[0].original_url='https://i0.wp.com/elsewhere/s.png'],
['NOAA image source original byte mismatch',a=>a.rows.find(x=>x.media_id===2148).original_stored_bytes=1000000],
['misstated current post count',a=>a.current_published_post_count_readonly=61],
['fabricated media pagination count',a=>a.live_media_inventory.returned_rows_by_page=[100,22]],
['fictional decoded dimensions',a=>a.rows[0].guest_decoded_px=[960,640]],
['fictional guest failure count',a=>a.release.visitor_confirmed_broken_total=42],
['truncated P0 verification queue',a=>a.release.unchanged_priority_p0_slots=['285:5']],
['unlicensed download',a=>a.release.assets_downloaded=1],
['Commons and WordPress bytes mismatch',a=>a.target_source_custody['2148'].commons_record_bytes=110],
['Halifax map upsized instead of capped',a=>a.rows.find(x=>x.media_id===1714).conditional_derivative_px=[1280,1280]],
['unreconciled original 13 stored total',a=>a.prior_verified_13_MiB_20261104.stored_original_bytes=43000000]
];
for(const [name,mutate] of scenarios){
  test('fail closed: '+name,()=>{
    const copy=JSON.parse(JSON.stringify(original));
    mutate(copy);
    assert.ok(validate(copy).length>0,name);
  });
}

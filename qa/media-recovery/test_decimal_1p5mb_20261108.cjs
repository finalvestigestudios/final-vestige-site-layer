'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {validate}=require('./validate_decimal_1p5mb_20261108.cjs');
const load=()=>JSON.parse(fs.readFileSync(path.join(__dirname,'decimal_1p5mb_119_media_20261108.json'),'utf8'));
test('live WordPress 119/15/14 decimal-vs-binary source metadata valid; all releases HOLD',()=>assert.equal(validate(load()).pass,true));
const mutations={
"one lost row":d=>d.rows.pop(),
"media count wrong":d=>d.wordpress_image_media_count=118,
"decimal count conflated with MiB":d=>d.decimal_large_original_count=14,
"binary count conflated with MB":d=>d.binary_large_original_count=15,
"decimal stored bytes wrong":d=>d.decimal_large_original_storage_bytes=45553777,
"binary stored bytes wrong":d=>d.binary_large_original_storage_bytes=43522829,
"gap not identified":d=>d.decimal_only_media_ids=[],
"claim 42 broken confirmed":d=>d.reported_42_broken_guest_verified=true,
"invented 76 percent":d=>d.measured_reduction=76,
"invented guest 404":d=>d.rows[0].guest_http_status=404,
"invented origin 200":d=>d.rows[0].original_http_status=200,
"download allowed":d=>d.rows[0].download_authorized=true,
"image rehost allowed":d=>d.rows[0].derivative_authorized=true,
"WP write allowed":d=>d.rows[0].wp_write_authorized=true,
"WP writes falsely claimed":d=>d.wordpress_writes=1,
"oversized 960":d=>d.rows[0].conditional_preview_max_width=1024,
"changed image host":d=>d.rows[0].original_url="https://outside.example.com/image.png",
"duplicate media ID":d=>d.rows[0].media_id=d.rows[1].media_id,
"changed original bytes":d=>d.rows.find(x=>x.media_id===1714).original_bytes=1543003,
"changed map post id":d=>d.halifax.post_id=268,
"map source not exact":d=>d.halifax.exact_raw_gutenberg_img_src=false,
"lost large-size slug":d=>d.halifax.stored_size_slug_large=false,
"false subsize exists":d=>d.halifax.confirmed_binary_subsize_exists=true,
"pretend metadata URLs identical":d=>d.halifax.metadata_urls_disagree=false,
"pretend rights cleared":d=>d.halifax.independent_copyright_permission="CLEARED",
"caption text readability proven":d=>d.halifax.labels_legibility="PASS",
"upscale map to 1920":d=>d.rows.find(x=>x.media_id===1714).conditional_preview_max_width=1920
};
for(const [label,mutate] of Object.entries(mutations))test('reject '+label,()=>{const x=load();mutate(x);assert.equal(validate(x).pass,false)});

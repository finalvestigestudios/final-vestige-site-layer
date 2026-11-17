'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {check}=require('./verify_prinsendam292.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'prinsendam292_guest_source_custody_20261116_2031pt.json'),'utf8'));
test('exact committed audit passes',()=>assert.equal(check(original),true));
const cases=[
 ['fictitious verified broken count',m=>m.historical.broken_verified=42],
 ['invented 76 percent saving',m=>m.historical.wire_saving_measured_percent=76],
 ['mistaken stored vs transfer',m=>m.historical.oversized_visitor_bytes=64385752],
 ['false visitor capture',m=>m.counts.guest_browser_verified=6],
 ['fake HTTP 404',m=>m.rows[5].visitor_http_status=404],
 ['fake image decode',m=>m.rows[1].visitor_decode=true],
 ['fake wire bytes',m=>m.rows[0].visitor_transfer_bytes=30000],
 ['fake currentSrc',m=>m.rows[2].visitor_current_src=m.rows[2].view_src],
 ['fake MIME',m=>m.rows[4].visitor_mime='image/jpeg'],
 ['unlicensed copy approval',m=>m.rows[1].rights_to_copy_approved=true],
 ['unsafe WordPress write',m=>m.rows[3].wordpress_media_write_approved=true],
 ['unverified pixel identity',m=>m.rows[0].pixel_match_confirmed=true],
 ['homepage edit',m=>m.safety.homepage_changes=1],
 ['paid subscription',m=>m.safety.spend=1],
 ['post rewrite',m=>m.safety.post_block_changes=1],
 ['new download',m=>m.safety.downloads=1],
 ['incorrect srcset',m=>m.rows[1].view_srcset=true],
 ['incorrect dimensions',m=>m.rows[1].view_width=960],
 ['wrong URL protocol',m=>m.rows[4].view_src='ftp://bad'],
 ['missing source token',m=>m.rows[1].authored_url=m.rows[1].authored_url.split('?')[0]],
 ['wrong Jetpack proxy status',m=>m.rows[2].view_jetpack=true],
 ['invalid size upscale',m=>m.rows[3].conditional_review_px=[1280,860]],
 ['wrong aspect ratio',m=>m.rows[0].conditional_review_px=[960,540]],
 ['wrong photo source geometry',m=>m.rows[3].candidate_native_catalog_px=[2000,1891]],
 ['wrong schema',m=>m.schema='unsafe'],
 ['duplicate slot',m=>m.rows[5].slot='292:3'],
 ['changed alt',m=>m.rows[2].alt_view='unknown'],
 ['missing image',m=>m.rows.pop()],
 ['fabricated response on blocked source',m=>m.rows[5].source_reader_result='IMAGE_DISPLAYED'],
 ['fake historical denominator',m=>m.historical.inline_images=356]
];
for(const [name,mutate] of cases)test('reject '+name,()=>{const m=JSON.parse(JSON.stringify(original));mutate(m);assert.throws(()=>check(m));});

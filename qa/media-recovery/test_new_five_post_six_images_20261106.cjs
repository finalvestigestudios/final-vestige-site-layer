'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{validate}=require('./validate_new_five_post_six_images_20261106.cjs');
const src=JSON.parse(fs.readFileSync(path.join(__dirname,'new_five_post_six_images_20261106.json'),'utf8'));
test('complete source evidence passes',()=>assert.deepEqual(validate(src),[]));
const mutations=[
['fabricated 404',d=>d.rows[0].guest_browser_http=404],
['fabricated 200',d=>d.rows[5].origin_http=200],
['fabricated pixels',d=>d.rows[4].decoded_pixels=1],
['fake wire savings',d=>d.rows[3].wire_bytes=12],
['bad aspect ratio',d=>d.rows[1].conditional_preview_px[1]=990],
['unsafe upscaling',d=>d.rows[3].conditional_preview_px[0]=1280],
['wrong Commons catalog',d=>d.rows[0].catalog_url='https://wrong.test'],
['wrong Commons image source',d=>d.rows[2].stored_src='https://wrong.test'],
['wrong CC license',d=>d.rows[4].catalog_license='CC0'],
['missing attribution',d=>d.rows[5].credit=''],
['incorrect post identity',d=>d.rows[2].post_id=1917],
['unverified 42 claimed proven',d=>d.baseline.reported_broken_42_browser_verified=true],
['unmeasured 76 claimed proven',d=>d.baseline.claimed_76_percent_wire_savings_measured=true],
['production edit approved',d=>d.rows[4].wp_write=true],
['image caching approved',d=>d.rows[1].cached=true],
['rights hold bypassed',d=>d.rows[3].rights_rehost='APPROVED'],
['automated rewrite approved',d=>d.rows[2].automatic_rewrite=true],
['width falsely present in HTML',d=>d.rows[0].stored_img_width_attr=1280],
['map detail erased',d=>d.rows[1].visual_review='PHOTO'],
['new post missing',d=>d.post_ids.pop()],
['incorrect post count',d=>d.image_counts[2]=1],
['additional unverified image',d=>d.rows.push(d.rows[0])],
['publication approved',d=>d.release.license_hold=false],
['downloads invented',d=>d.release.downloaded=1]];
for(const [name,mutate] of mutations)test('reject '+name,()=>{const d=JSON.parse(JSON.stringify(src));mutate(d);assert.ok(validate(d).length>0,name);});

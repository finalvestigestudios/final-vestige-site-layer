'use strict';
function validate(d){
const e=[],bad=s=>e.push(s);
if(d.schema!=='fv-new-posts-six-inline-images-v1')bad('schema');
if(d.published_post_count!==66||d.image_count!==6||JSON.stringify(d.post_ids)!==JSON.stringify([1917,1920,1922,1924,1926])||JSON.stringify(d.image_counts)!==JSON.stringify([2,2,0,1,1]))bad('census');
if(d.baseline?.frozen_posts!==61||d.baseline?.frozen_img_slots!==355||d.baseline?.reported_broken_42_browser_verified!==false||d.baseline?.claimed_76_percent_wire_savings_measured!==false||d.baseline?.arithmetic_projection_361_not_fresh_full_site!==true)bad('baseline');
if(!Array.isArray(d.rows)||d.rows.length!==6)return [...e,'rows'];
const keys=['1917:0','1917:1','1920:0','1920:1','1924:0','1926:0'];
const licenses=['PD-ART-US','PD-SCAN-US-TAG-REVIEW','CC-BY-4.0','CC-BY-4.0','CC-BY-4.0','CC0'];
d.rows.forEach((r,i)=>{
if(r.key!==keys[i]||r.post_id!==Number(r.key.split(':')[0]))bad('identity '+i);
if(!r.stored_src.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/')||!r.stored_src.endsWith('?width='+r.requested_width_px))bad('original source '+i);
if(!r.catalog_url.startsWith('https://commons.wikimedia.org/wiki/File:')||r.catalog_license!==licenses[i])bad('catalog and rights '+i);
const [w,h]=r.catalog_original_px||[];if(!Number.isInteger(w)||w<1||!Number.isInteger(h)||h<1)bad('original dimensions '+i);
else{const width=Math.min(960,r.requested_width_px,w);if(JSON.stringify(r.conditional_preview_px)!==JSON.stringify([width,Math.round(width*h/w)]))bad('no upscale geometry '+i);}
if(r.stored_img_width_attr!==null||r.stored_img_height_attr!==null||r.origin_http!==null||r.guest_browser_http!==null||r.decoded_pixels!==null||r.wire_bytes!==null)bad('invented source/browser evidence '+i);
if(r.rights_rehost!=='HOLD'||r.cached!==false||r.wp_write!==false||r.automatic_rewrite!==false)bad('unsafe release '+i);
if(!r.credit||!r.published_caption)bad('lost credit/caption '+i);
if(i<2&&r.visual_review!=='HIGH_DETAIL_MAP')bad('map detail '+i);
});
if(d.release?.max_preview_width!==960||d.release?.never_upscale!==true||d.release?.downloaded!==0||d.release?.production_repairs!==0||d.release?.wordpress_changes!==0||d.release?.license_hold!==true||d.release?.browser_measurements!==null)bad('release');
return e;
}
if(typeof module!=='undefined')module.exports={validate};
if(typeof require!=='undefined'&&require.main===module){
const fs=require('node:fs'),path=require('node:path');
const errs=validate(JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,'new_five_post_six_images_20261106.json'),'utf8')));
if(errs.length){console.error(errs.join('\n'));process.exitCode=1;}else console.log('PASS new six-image source & rights audit');
}

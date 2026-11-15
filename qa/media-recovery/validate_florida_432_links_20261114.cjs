'use strict';
const fs=require('node:fs'),path=require('node:path');
const expected=new Map([
['432:1',['PR04493',4144,'prints/pr04493.jpg']],['432:2',['RC17068',38362,'reference/rc17068.jpg']],
['432:3',['RC10673',33289,'reference/rc10673.jpg']],['432:4',['N031889',141398,'general/n031889.jpg']],
['432:5',['RC04344',27848,'reference/rc04344.jpg']],['432:6',['RC07668',30741,'reference/rc07668.jpg']],
['432:7',['MSF-PB11548-001',340182,'msf/MSF-PB11548-001.jpg']]]);
function assert(c,m){if(!c)throw Error(m)}
function itemHref(url){const u=new URL(url);assert(u.protocol==='https:'&&['www.floridamemory.com','floridamemory.com'].includes(u.hostname),'foreign click URL');const m=u.pathname.match(/^\/items\/show\/(\d+)\/?$/);return m?Number(m[1]):null}
function validate(d){
assert(d.schema==='fv-432-seven-florida-link-and-delivery-custody-v1','schema drift');
assert(d.post?.id===432&&d.post.status==='publish'&&d.post.modified==='2026-08-28T03:07:30','WP identity drift');
assert(d.summary?.release==='HOLD'&&d.summary.production_replacements===0,'unauthorized release');
assert(d.baseline?.guest_confirmed_broken===null&&d.baseline.measured_transfer_reduction_percent===null,'invented site-wide metrics');
assert(Array.isArray(d.images)&&d.images.length===7,'wrong row count');
let exact=0,non=0,mislabel=0;const seen=new Set();
for(const x of d.images){
const e=expected.get(x.slot);assert(e&&!seen.has(x.slot),'duplicate/unknown slot');seen.add(x.slot);
const [id,item,rel]=e,src='https://www.floridamemory.com/fpc/'+rel,cat='https://www.floridamemory.com/items/show/'+item;
assert(x.id===id&&x.item===item&&x.src===src&&x.cat===cat,'archive accession identity drift '+x.slot);
assert(x.alt?.length>30&&x.caption?.length>40,'lost editorial text '+x.slot);
if(itemHref(x.click)===item)exact++;else non++;
assert(x.reader==='web.open wrapper 500: redirect target inaccessible'&&x.redirect===src.replace('www.floridamemory.com','floridamemory.com'),'unverified retriever outcome '+x.slot);
for(const field of ['origin_http','guest_http','wire_bytes','natural_width','native_px'])assert(x[field]===null,'fabricated browser/origin/size '+x.slot+' '+field);
assert(x.max_derivative_width===960&&x.rights==='item-review-pending'&&x.cache_allowed===false&&x.wp_write_allowed===false,'unsafe rights/derivative '+x.slot);
if(x.slot==='432:2'){assert(x.caption_source_href===x.click&&itemHref(x.caption_source_href)!==item,'caption mislabel lost');mislabel++}
else assert(x.caption_source_href===null,'unexpected caption source href');
}
assert(exact===4&&non===3&&mislabel===1,'unexpected exact vs generic count');
assert(d.summary.exact_item_clicks===exact&&d.summary.non_item_clicks===non&&d.summary.mislabeled_caption_source_links===mislabel&&d.summary.guest_broken_confirmed===null,'summary overclaim');
return {decision:'HOLD',catalog_source_matches:seen.size,exact_item_links:exact,generic_or_search_links:non,caption_source_label_mismatches:mislabel,visitor_verified:false};
}
if(require.main===module){try{const f=process.argv[2]||path.join(__dirname,'florida_432_seven_click_and_delivery_custody_20261114.json');console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(f,'utf8'))),null,2))}catch(e){console.error('FAIL-CLOSED '+e.message);process.exitCode=1}}
module.exports={validate,itemHref};

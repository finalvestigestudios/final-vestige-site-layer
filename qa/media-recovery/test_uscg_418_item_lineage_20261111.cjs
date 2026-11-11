'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {check}=require('./verify_uscg_418_item_lineage_20261111.cjs');
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'uscg_418_p0_official_catalog_item_rights_20261111.json')));
const b=JSON.parse(fs.readFileSync(path.join(__dirname,'coverage_288_exact_pr1703_20261110.json')));
const cases=[
 ['control',()=>{}],['wrong source',x=>x.items[0].exact_published_url=x.items[1].exact_published_url],
 ['wrong post',x=>x.items[0].post_url='https://finalvestige.com/fake'],['different portrait',x=>x.items[0].subject='Lighthouse ruins'],
 ['changed virin',x=>x.items[0].official_virin='XXX'],['invent 404',x=>x.items[1].guest_http_status=404],
 ['invent origin 403',x=>x.items[0].origin_http_status=403],['invalid retriever claim',x=>x.items[0].web_retriever_only.method='GUEST_CHROME'],
 ['invent wire bytes',x=>x.items[0].guest_transfer_bytes=40000],['catalog size as wire',x=>x.items[0].catalog_size_is_network_bytes=true],
 ['falsify 76% improvement',x=>x.site_status.measured_transfer_reduction_pct=76],
 ['lie 42 are guest failures',x=>x.site_status.guest_failures_confirmed=42],
 ['derive fake 960',x=>x.items[0].conditional_960px=[960,540]],['upscale',x=>x.items[0].do_not_upscale=false],
 ['crop portrait',x=>x.items[0].do_not_crop=false],['wrong 418:2 rights',x=>x.items[1].rights_cleared_to_rehost=true],
 ['infer matching binary',x=>x.items[1].source_correspondence='EXACT_BINARY_MATCH'],
 ['download',x=>x.items[1].download_allowed=true],['cache',x=>x.items[1].cache_allowed=true],
 ['WP prod write',x=>x.release.wordpress_production_write=true],['change homepage',x=>x.release.homepage_changes=true],
 ['claim paid spend',x=>x.release.subscription_spend_usd=1],['P0 queue reordering',x=>x.siteqa_existing_browser_order.reverse()],
 ['remove editorial review',x=>x.release.editor_staging_review_required=false]
];
let n=0;
for(const [name,mut] of cases){const c=JSON.parse(JSON.stringify(a));mut(c);if(name==='control')assert.equal(check(c,b).ok,true);else assert.throws(()=>check(c,b),undefined,name);n++}
console.log(n+'/'+cases.length+' PASS');

'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_hebgen_407.cjs');
const from=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8'));
const part=from('parts/02.json'),viewer=from('source_viewer_25slot_20261031.json'),baseline=from('hebgen_407_usgs_custody_20261101.json');
const copy=()=>structuredClone(baseline);
test('frozen 8-photo original source+rights+browser-hold census',()=>assert.deepEqual(validate(copy(),part,viewer),{ok:true,errors:[]}));
const mutations=[
['invent guest 404',d=>d.images[1].browser.http_status=404],
['invent guest 200',d=>d.images[0].browser.http_status=200],
['invent encoded bytes',d=>d.images[2].browser.encoded_image_bytes=10400],
['invent natural width',d=>d.images[2].browser.natural_width=1024],
['invent broken',d=>d.images[3].browser.broken=true],
['fake visitor broken count',d=>d.summary.confirmed_visitor_broken=42],
['fake 42 verified',d=>d.summary.claimed_42_broken_proven=true],
['fake 76 measured',d=>d.summary.measured_image_weight_reduction_percent=76],
['fake 76 verified',d=>d.summary.claimed_76_percent_proven=true],
['fake visitor network status from viewer',d=>d.images[1].viewer.http_status=400],
['viewer success miscount',d=>d.summary.viewer_rendered_current_url=7],
['change S3 source without census update',d=>d.images[1].exact_url=d.images[1].candidate.url],
['replace fault scarp with unrelated photo',d=>d.images[1].candidate.url=d.images[0].exact_url],
['change catalog record identity',d=>d.images[2].archive.record_url=d.images[0].archive.record_url],
['mislabel exact original link',d=>d.images[0].archive.exact_original_link_matches_published_url=true],
['claim binary hashed',d=>d.images[1].archive.master_sha256='f'.repeat(64)],
['invent intrinsic width',d=>d.images[2].geometry.verified_binary_width=1024],
['upscale output',d=>d.images[2].geometry.conditional_960_dimensions.width=1280],
['corrupt ratio',d=>d.images[3].geometry.conditional_960_dimensions.height=800],
['invent unknown dimensions',d=>d.images[1].geometry.conditional_960_dimensions={width:960,height:600}],
['remove Hall credit',d=>d.images[2].archive.credit='USGS'],
['remove Nile credit',d=>d.images[3].archive.credit='USGS'],
['wrong Seismic Geyser date',d=>d.images[6].archive.photograph_date='1959'],
['wrong modern 2023 image date',d=>d.images[7].archive.photograph_date='1959'],
['enable WP upload',d=>d.images[7].release.wordpress_upload_authorized=true],
['enable WP rewrite',d=>d.images[7].release.wordpress_post_edit_authorized=true],
['claim rights approved',d=>d.images[0].release.item_specific_rights='APPROVED'],
['claim repaired asset',d=>d.summary.production_repaired=1],
['allow unlicensed scraping',d=>d.cache_plan.auto_scraping=true],
['allow production writes',d=>d.cache_plan.production_wp_writes=true],
['add spend',d=>d.cache_plan.subscription_spend_usd=1],
['duplicate source slot',d=>d.images[1].key='407:0'],
['drop image',d=>d.images.pop()],
['null rights',d=>d.images[4].release=null],
['null image',d=>d.images[3]=null]];
for(const [label,fn] of mutations)test('fail-closed: '+label,()=>{const doc=copy();fn(doc);assert.equal(validate(doc,part,viewer).ok,false,label)});

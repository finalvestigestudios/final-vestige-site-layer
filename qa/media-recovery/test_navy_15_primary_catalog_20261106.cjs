'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');const {validate}=require('./validate_navy_15_primary_catalog_20261106.cjs');const audit=require('./navy_15_primary_catalog_20261106.json');
const clone=()=>JSON.parse(JSON.stringify(audit));
test('Navy source inventory and catalog checks',()=>assert.equal(validate(clone()).ok,true));
const mutations=[a=>a.images[0].browser_http=404,
a=>a.images[0].visitor_broken=true,
a=>a.images[0].transferred_bytes=130,
a=>a.images[0].decoded_pixels=960,
a=>a.release.wordpress_writes=true,
a=>a.release.binary_download=true,
a=>a.release.external_caching=true,
a=>a.images[0].wp_write_allowed=true,
a=>a.images[0].cache_allowed=true,
a=>a.images[0].rights="APPROVED",
a=>a.claims.broken_42="VERIFIED",
a=>a.claims.transfer_saving_76="MEASURED",
a=>a.claims.production_fixed=1,
a=>a.images.find(x=>x.key==="370:0").catalog_id="80-G-276940",
a=>a.images.find(x=>x.key==="274:1").identity="CATALOG_ID_IN_ORIGINAL",
a=>a.images.find(x=>x.key==="280:1").catalog_id="NH-75561",
a=>a.images.pop(),
a=>a.images[0].key=a.images[1].key,
a=>a.images[0].source_url="https://example.com/denied.jpg",
a=>a.images.find(x=>x.conditional_960).conditional_960.width=1280,
a=>a.images.find(x=>x.conditional_960).conditional_960.height=2,
a=>a.images.find(x=>x.conditional_960).catalog_master.width=200,
a=>a.inputs.pop(),
a=>a.counts.legacy_images=361];
mutations.forEach((f,i)=>test('reject unsafe mutation '+i,()=>{const a=clone();f(a);assert.equal(validate(a).ok,false)}));

'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict');
const {validate}=require('./validate_eastland_214_catalog_20261105.cjs');
const audit=require('./eastland_214_catalog_20261105.json');
const cp=()=>JSON.parse(JSON.stringify(audit));
test('valid pinned six-image ledger',()=>assert.equal(validate(cp()).ok,true));
const mutations=[
['fake guest 404',x=>x.images[0].guest_http_status=404],
['fake origin 200',x=>x.images[0].origin_http_status=200],
['fake decoded width',x=>x.images[0].guest_natural_width=100],
['fake transferred bytes',x=>x.images[0].guest_bytes=100],
['fake same binary',x=>x.images[0].exact_binary_verified=true],
['publish permit',x=>x.images[0].wordpress_write_authorized=true],
['rehost permit',x=>x.images[1].rehost_authorized=true],
['change status',x=>x.images[1].remediation_status='READY'],
['bad license',x=>x.images[1].copyright_review='ok'],
['bad caption evidence',x=>x.images[3].editorial_finding='x'],
['upscale Kenosha',x=>x.images[2].conditional_width=960],
['wrong panorama height',x=>x.images[1].conditional_height=600],
['made up Bain dimensions',x=>x.images[0].master_width=960],
['made up Bain catalog',x=>x.images[0].primary_or_catalog_record='https://loc.gov/x'],
['source swapped',x=>x.images[5].original_source_url='https://example.com/swap.jpg'],
['slot duplicated',x=>x.images[5]=JSON.parse(JSON.stringify(x.images[4]))],
['missing slot',x=>x.images.pop()],
['invent 42 failures',x=>x.baseline.reported_42_broken='CONFIRMED'],
['invent 76 percent',x=>x.baseline.reported_76_percent='MEASURED'],
['tamper inventory sha',x=>x.source_inventory.blob_sha='bad'],
['production write claim',x=>x.production_changes=1]
];
for(const [name,f] of mutations)test(name+' rejected',()=>{const x=cp();f(x);assert.equal(validate(x).ok,false)});

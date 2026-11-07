'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_usgs_nine_20261106.cjs'),evidence=require('./usgs_nine_20261106.json');
test('source audit passes',()=>assert.equal(validate(evidence).ok,true,validate(evidence).errors.join('; ')));
for(const [name,change] of [
['fake 404',x=>x.images[1].browser_http=404],['fake missing',x=>x.images[1].browser_broken=true],
['fake bytes',x=>x.images[0].wire_bytes=1024],['license',x=>x.images[0].rights='CLEARED'],
['cache',x=>x.images[1].wp_cache=true],['write',x=>x.images[1].wp_write=true],
['pixel enlargement',x=>x.images[2].max_width=1200],['fabricated size',x=>x.images[0].natural_pixels={width:1000,height:800}],
['wrong ratio',x=>x.images[2].conditional_960.height=900],['fake ratio',x=>x.images[1].conditional_960={width:960,height:900}],
['false path match',x=>x.images[1].exact_original_url=true],['wrong original',x=>x.images[0].publisher_original_url=x.images[2].publisher_original_url],
['mislabel wrapper',x=>x.images[1].retriever_stored_source='HTTP_400'],['bad credit',x=>x.images[7].credit=''],
['fake 76%',x=>x.assertions.claimed_76_percent_transfer_reduction='MEASURED'],
['fake 42',x=>x.assertions.reported_42_broken='CONFIRMED'],['duplicate',x=>x.images[8].key='407:0'],
['missing',x=>x.images.pop()],['third party download',x=>x.assertions.media_downloads=1],
['production write',x=>x.assertions.production_wp_writes=1],['wrong rights',x=>x.images[8].usgs_catalog_rights='CC-BY'],
['wrong catalog',x=>x.images[8].usgs_catalog_url='https://example.org/']
])test('reject '+name,()=>{const x=JSON.parse(JSON.stringify(evidence));change(x);assert.equal(validate(x).ok,false,name)});

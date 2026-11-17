'use strict';
/** Synthetic mutations. No HTTP, no image download, no WordPress. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validateAudit,gitBlob,FROZEN_BLOB}=require('./validate_florida_memory_432_20261105.cjs');
const read=x=>JSON.parse(fs.readFileSync(path.join(__dirname,x),'utf8'));
const data=read('florida_memory_432_seven_originals_20261105.json');
const part=read('parts/01.json');
const copy=()=>structuredClone(data),mustFail=(edit,name)=>{
 const a=copy();edit(a);const r=validateAudit(a,part);assert.equal(r.ok,false,name);assert.ok(r.errors.length,name);
};
test('frozen source real Git blob',()=>{
 const raw=fs.readFileSync(path.join(__dirname,'parts/01.json'));
 assert.equal(gitBlob(raw),FROZEN_BLOB);
});
test('7/7 real indexed archive source URLs match frozen inventory',()=>{
 const r=validateAudit(data,part);assert.equal(r.ok,true,JSON.stringify(r.errors));assert.equal(r.metrics.catalog_path_matches,7);
});
test('changed original URL rejected',()=>mustFail(a=>{a.images[0].exact_published_source_url='https://invalid.invalid/photo.jpg'},'source'));
test('changed ALT rejected',()=>mustFail(a=>{a.images[1].exact_published_alt='different photo'},'alt'));
test('changed source slot rejected',()=>mustFail(a=>{a.images[1].image_key='432:0'},'slot'));
test('missing image rejected',()=>mustFail(a=>{a.images.pop()},'count'));
test('wrong catalog item page rejected',()=>mustFail(a=>{a.images[2].catalog_item_url='https://www.floridamemory.com/items/show/0000'},'catalog'));
test('wrong archive ID rejected',()=>mustFail(a=>{a.images[3].catalog_identifier='N031888'},'identifier'));
test('wrong catalog image path rejected',()=>mustFail(a=>{a.images[4].catalog_image_path='/fpc/reference/rc04343.jpg'},'path'));
test('invented visitor 404 rejected',()=>mustFail(a=>{a.images[5].visitor_http_status=404},'browser'));
test('invented origin 200 rejected',()=>mustFail(a=>{a.images[0].origin_http_status=200},'origin'));
test('invented byte count rejected',()=>mustFail(a=>{a.images[0].actual_network_transfer_bytes=10000},'bytes'));
test('invented binary dimensions rejected',()=>mustFail(a=>{a.images[0].binary_dimensions_px=[900,600]},'pixels'));
test('license assumption rejected',()=>mustFail(a=>{a.images[3].license_verified=true},'rights'));
test('cache authorization rejected',()=>mustFail(a=>{a.images[4].cache_or_rehost_allowed=true},'cache'));
test('WordPress write authorization rejected',()=>mustFail(a=>{a.images[4].wordpress_production_write_allowed=true},'write'));
test('invented derivative width rejected',()=>mustFail(a=>{a.images[6].derivative_width_px=960},'dimensions'));
test('upscale permission rejected',()=>mustFail(a=>{a.images[6].no_upscaling_required=false},'upscale'));
test('2001 commemorative photograph misdated as 1928 rejected',()=>mustFail(a=>{a.images[6].catalog_date='1928'},'modern'));
test('2001 image editorial note omission rejected',()=>mustFail(a=>{a.images[6].editorial_note=null},'historical'));
test('wrapper 500 incorrectly represented as 404 rejected',()=>mustFail(a=>{a.images[0].image_retriever_observation.code=404},'retriever'));
test('false complete visitor audit rejected',()=>mustFail(a=>{a.checks.visitor_http_status_known=7},'false audit'));
test('release gate loosened rejected',()=>mustFail(a=>{a.release_gate.localization_allowed=true},'release'));
test('frozen snapshot identity drift rejected',()=>mustFail(a=>{a.input_source.git_blob_sha='tampered'},'provenance'));

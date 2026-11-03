'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_pueblo_280_20261103.cjs'),raw=JSON.parse(fs.readFileSync(path.join(__dirname,'pueblo_280_20261103.json'),'utf8')),frozen=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/03.json'),'utf8'));
function mutation(fn){const a=JSON.parse(JSON.stringify(raw));fn(a);assert.notDeepEqual(validate(a,frozen),[])}
test('all six source identities and provenance pass',()=>assert.deepEqual(validate(raw,frozen),[]));
for(let i=0;i<6;i++){
 test('fabricated guest 404 '+i,()=>mutation(a=>a.images[i].observed_exact_source.real_browser_http_code=404));
 test('source identity drift '+i,()=>mutation(a=>a.images[i].stored_url+='?different=1'));
 test('premature rights approval '+i,()=>mutation(a=>a.images[i].rights.cleared_to_republish=true));
 test('invented master pixels '+i,()=>mutation(a=>a.images[i].archival.full_tiff_pixels=[1000,2000]));
}
test('42 broken claim',()=>mutation(a=>a.sitewide.claim_42_broken_verified=true));
test('76 percent wire claim',()=>mutation(a=>a.sitewide.claim_76_percent_wire_savings_measured=true));
test('unapproved CMS write',()=>mutation(a=>a.rights_and_release.production_post_write=true));
test('Banner alternate mistaken as exact',()=>mutation(a=>a.related_banner.same_binary_not_verified=false));
test('invented origin 502',()=>mutation(a=>a.images[0].observed_exact_source.real_origin_http_code=502));
test('incorrect image 280:1 accession',()=>mutation(a=>a.images[1].archival.catalog_id='NH 75561'));
test('remove ALT chronology caveat',()=>mutation(a=>a.images[4].alt_integrity_warning=null));
test('invalid 961px derivative',()=>mutation(a=>a.images[0].conditional_derivative_px[0]=961));

'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_port_chicago_nps_six_20261106.cjs');
const seed=JSON.parse(fs.readFileSync(path.join(__dirname,'port_chicago_nps_six_20261106.json'),'utf8'));
const fresh=()=>JSON.parse(JSON.stringify(seed));
test('six recorded official NPS original sources pass',()=>assert.equal(validate(fresh()).ok,true));
const mutations=[
 ['fake 404',d=>d.images[0].guest_http_status=404],
 ['fake origin 200',d=>d.images[1].origin_http_status=200],
 ['fake decoded dimensions',d=>d.images[2].guest_natural_pixels=[960,800]],
 ['fake transferred bytes',d=>d.images[3].guest_wire_bytes=100],
 ['fake user broken',d=>d.images[4].visitor_broken=true],
 ['claims 42 broken',d=>d.scope.verified_guest_broken=42],
 ['claims 76% saving',d=>d.scope.measured_wire_reduction_percent=76],
 ['allows WordPress edit',d=>d.images[0].wordpress_written=true],
 ['allows caching',d=>d.images[1].source_cached=true],
 ['allows download',d=>d.images[2].third_party_downloaded=true],
 ['rights prematurely cleared',d=>d.images[3].reuse_rights='CLEARED'],
 ['drops credit',d=>d.images[4].credit_preserved=false],
 ['invented native pixels',d=>d.images[5].native_pixels=[1982,1584]],
 ['presumes gallery orientation',d=>d.images[3].catalog_orientation_verified=true],
 ['presumes same binary',d=>d.images[2].exact_binary_identity_verified=true],
 ['guesses court image dimensions',d=>d.images[4].html_width=800],
 ['approves preview',d=>d.images[0].approved=true],
 ['distorts preview aspect',d=>d.images[1].conditional_preview_html_only[1]=120],
 ['replaces NPS URL',d=>d.images[2].original_src='https://example.com/bogus.jpg'],
 ['duplicates image',d=>d.images[5].original_src=d.images[4].original_src],
 ['drops image',d=>d.images.pop()],
 ['removes caption',d=>d.images[0].caption=''],
 ['claims production fix',d=>d.release.production_fixes=1],
 ['drops crop safety',d=>d.catalog_geometry_conflicts=[]]
];
for(const [name,change] of mutations)test('reject '+name,()=>{const d=fresh();change(d);assert.equal(validate(d).ok,false,name)});

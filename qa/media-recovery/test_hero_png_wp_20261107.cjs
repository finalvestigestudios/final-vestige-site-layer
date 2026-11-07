'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_hero_png_wp_20261107.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'hero_png_wp_20261107.json'),'utf8'));
test('verified five-image WordPress metadata passes',()=>assert.equal(validate(data).ok,true));
const mutations=[["fake HTTP","a.rows[0].guest_http=200"],["fake bytes","a.rows[0].guest_encoded_bytes=100"],["fake decode","a.rows[1].guest_decode=true"],["fake savings","a.claimed_76pct_wire_reduction='VERIFIED'"],["fake broken","a.reported_broken_42='VERIFIED'"],["invent rights","a.rights='CLEARED'"],["alpha assumed","a.alpha='OPAQUE'"],["caption erased","a.rows[1].figcaption='historic photograph'"],["no media disclosure","a.rows[0].media_alt_reconstruction=false"],["wrong native size","a.rows[2].native_px=[960,540]"],["fake subsize","a.rows[3].cms_subsizes=1"],["srcset assumed","a.rows[0].stored_srcset=true"],["upscaled output","a.rows[0].proposed_preview=[1920,1080]"],["derivative claimed","a.rows[0].derivative_created=true"],["unlicensed fetch","a.rows[0].download=true"],["WordPress write","a.rows[4].wp_write=true"],["fake guest response","a.visitor_http=200"],["duplicate slot","a.rows[4].post=34"],["wrong URL","a.rows[3].original_src='https://example.com/archival.png'"],["bad bytes","a.rows[2].original_bytes=1"]];
for(const [name,stmt] of mutations)test('reject '+name,()=>{
 const a=JSON.parse(JSON.stringify(data));new Function('a',stmt)(a);assert.equal(validate(a).ok,false);
});

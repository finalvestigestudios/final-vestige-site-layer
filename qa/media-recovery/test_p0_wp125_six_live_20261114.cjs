'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_p0_wp125_six_live_20261114.cjs');
const initial=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_wp125_six_live_20261114.json'),'utf8'));
const cases=[
  ["unmodified source snapshot passes", d=>{if(!validate(d).ok)throw Error(JSON.stringify(validate(d)));}],
  ["invented browser 404", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["invented browser success", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["invented browser broken count", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["invented 76 percent savings", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake wire bytes from storage", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["invented origin 200", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake browser currentSrc", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["invented natural dimensions", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake visitor bytes", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["all rights cleared", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["wordpress production allowed", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["silently approve caching", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["silently approve scene substitution", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["silently approve candidate", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["museum image upscaled", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["wrong Commons pixels", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["unverified candidate deleted", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["source URL drift 285:5", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["source URL drift 418:2", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["source slot moved", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["missing post", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["stale published figure count", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake media count", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["media size changed", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["duplicate media attachment", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["wrong oversized total", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["false 1.5MiB threshold", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake method", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake original HTTP", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["disable no upscale", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["duplicate P0", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}],
  ["fake subscription budget", d=>{mutate(d);if(validate(d).ok)throw Error("mutation accepted");}]
];
let passed=0;
for(const [name,run] of cases){const d=JSON.parse(JSON.stringify(initial));assert.doesNotThrow(()=>run(d),name);passed++;}
console.log(`PASS ${passed}/${cases.length} native Node regression cases`);

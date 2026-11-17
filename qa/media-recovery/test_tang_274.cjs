'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_tang_274.cjs');
const m=JSON.parse(fs.readFileSync(path.join(__dirname,'tang_274_nhhc_20261031.json'),'utf8'));
const inv=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/04.json'),'utf8'));
const copy=()=>structuredClone(m);
test('real seven-slot source inventory passes',()=>assert.deepEqual(validate(m,inv),[]));
for(let i=0;i<7;i++){
 const mutations=[
 ['source swap',r=>r.source_url='https://bad.example/image.jpg'],
 ['ALT swap',r=>r.alt='wrong photo'],
 ['catalog ID swap',r=>r.primary_catalog_id='NH 00000'],
 ['catalog link swap',r=>r.primary_catalog_url='https://not-navy.example.org/record'],
 ['upscaling',r=>r.conditional_derivative.width=961],
 ['distorted crop',r=>r.conditional_derivative.height+=5],
 ['fake HTTP',r=>r.guest_http_status=404],
 ['fake transferred bytes',r=>r.guest_bytes=2000],
 ['imaginary license',r=>r.rights_status='CLEARED'],
 ['unapproved WordPress upload',r=>r.wordpress_upload_authorized=true],
 ['invented binary hash',r=>r.source_sha256='f'.repeat(64)],
 ['invented source exact match',r=>r.original_pixels_verified=true],
 ['wrong source credit',r=>r.credit='Photographer unknown'],
 ['missing identity evidence',r=>r.identity_evidence='unknown']
 ];
 for(const [name,mutate] of mutations)test('reject '+name+' '+i,()=>{const c=copy();mutate(c.records[i]);assert.ok(validate(c,inv).length>0)});
}
for(const [name,mutate] of [['invented 42 broken',m=>m.reported_sitewide_42_broken_verified=true],['invented 76 percent savings',m=>m.reported_sitewide_76pct_savings_verified=true],['invented production repair',m=>m.production_repairs=1]])test('reject '+name,()=>{const c=copy();mutate(c);assert.ok(validate(c,inv).length>0)});

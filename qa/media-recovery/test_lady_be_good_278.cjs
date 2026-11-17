'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_lady_be_good_278.cjs');
const m=JSON.parse(fs.readFileSync(path.join(__dirname,'lady_be_good_278_primary_20261031.json'),'utf8'));
const inv=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/04.json'),'utf8'));
test('real original seven-slot custody ledger passes',()=>assert.deepEqual(validate(m,inv),[]));
for(let i=0;i<7;i++)for(const [name,mutate] of [
 ['wrong original URL',r=>r.source_url='https://example.invalid/wrong.jpg'],
 ['wrong ALT',r=>r.alt='wrong caption'],
 ['wrong catalog ID',r=>r.official_id='made-up ID'],
 ['wrong official URL',r=>r.official_record_url='https://example.invalid'],
 ['fake stronger identity',r=>r.evidence_level='exact_binary'],
 ['invented HTTP 404',r=>r.guest_http_status=404],
 ['invented transfer bytes',r=>r.guest_image_transfer_bytes=2000],
 ['invented decoded width',r=>r.guest_natural_width=960],
 ['invented source SHA',r=>r.original_sha256='f'.repeat(64)],
 ['fake binary identity',r=>r.binary_identity_verified=true],
 ['unlicensed claim',r=>r.rights_status='CLEARED'],
 ['unsafe WordPress write',r=>r.wordpress_media_write_authorized=true],
 ['made-up derivative dimensions',r=>r.derivative_target={width:960,height:640,no_upscale:true}],
 ['erased credit',r=>r.credit='']
])test('reject '+name+' at '+i,()=>{const x=structuredClone(m);mutate(x.records[i]);assert.ok(validate(x,inv).length>0)});
for(const [name,mutate] of [
 ['fake 42 broken',m=>m.reported_sitewide_42_broken_verified=true],
 ['fake 76 saved',m=>m.claimed_sitewide_76pct_reduction_verified=true],
 ['fake repairs',m=>m.production_images_repaired=1],
 ['fake 403 as 200',m=>m.records[0].web_retriever_observation.status=200],
 ['fabricated 960x999',m=>m.records[2].derivative_target.height=999],
 ['lost C-47 caption',m=>m.records[6].editorial_note='This caption is wrong for reasons still unknown; review before editorial update.']
])test('reject '+name,()=>{const x=structuredClone(m);mutate(x);assert.ok(validate(x,inv).length>0)});

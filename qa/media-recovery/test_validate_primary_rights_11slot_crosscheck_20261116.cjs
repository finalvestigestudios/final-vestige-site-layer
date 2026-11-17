'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {inspect}=require('./validate_primary_rights_11slot_crosscheck_20261116.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'primary_rights_11slot_crosscheck_20261116.json'),'utf8'));
test('11-slot media custody baseline passes',()=>assert.equal(inspect(original).ok,true));
const mutations=[
 ['fabricated HTTP',a=>a.rows[0].guest_http_status=200],
 ['false broken total',a=>a.reported_42_broken_confirmed=true],
 ['false savings',a=>a.claimed_76_percent_measured=true],
 ['false WordPress write',a=>a.no_wordpress_writes=false],
 ['false download',a=>a.no_media_downloads=false],
 ['false guest failure',a=>a.rows[2].visitor_failure_verified=true],
 ['rights promotion',a=>a.rows[0].rights_approval='CLEARED'],
 ['caching permission',a=>a.rows[0].wordpress_caching_authorized=true],
 ['upload permission',a=>a.rows[0].upload_authorized=true],
 ['post rewrite',a=>a.rows[0].published_post_rewrite_authorized=true],
 ['invented master dimensions',a=>a.rows[2].master_binary_dimensions_verified=true],
 ['bad Navy aspect ratio',a=>a.rows[2].conditional_960_px_from_catalog=[960,960]],
 ['invented Florida dimensions',a=>a.rows[4].conditional_960_px_from_catalog=[960,700]],
 ['invented Navy record',a=>a.rows[2].authority_record_url='https://foo.org/bar'],
 ['invented Florida record',a=>a.rows[7].authority_record_url='https://floridamemory.com/items/show/123'],
 ['misassigned publisher rights',a=>a.rows[0].rights_policy='florida-memory-PDM-1.0-source-claim'],
 ['removed rights caveat',a=>a.rights_records.skyway_caveat='PDM covers publisher images'],
 ['deleted image row',a=>a.rows.pop()],
 ['reordered image rows',a=>a.rows.reverse()],
 ['suppressed Pahokee provenance caveat',a=>a.rows.find(x=>x.key==='432:3').caption_note=null],
 ['synthetic visitor currentSrc',a=>a.rows[0].guest_current_src=a.rows[0].view_url],
 ['stale WordPress revision',a=>a.rows[0].wp_modified=''],
 ['HTML page as image binary',a=>a.rows[0].view_url='https://commons.wikimedia.org/wiki/File:test.jpg'],
 ['tampered original-byte denominator',a=>a.oversized_original_stored_bytes=12345]
];
for(const [name,fn] of mutations)test('reject '+name,()=>{const d=JSON.parse(JSON.stringify(original));fn(d);assert.equal(inspect(d).ok,false);});

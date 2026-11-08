'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const {validate}=require('./validate_navy_8_live_pueblo_honda_20261108.cjs');
const fixture=JSON.parse(fs.readFileSync(__dirname+'/navy_8_live_pueblo_honda_retriever_20261108.json','utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));
const cases=[
 ['control',o=>{}],
 ['invent_guest_broken',o=>o.counts.guest_broken_confirmed=8],
 ['fake_42',o=>o.counts.reported_42_broken_guest_confirmed=true],
 ['fake_76',o=>o.counts.reported_76_percent_wire_savings_measured=true],
 ['origin_http_502',o=>o.rows[6].web_retriever.http_status_origin=502],
 ['guest_http_404',o=>o.rows[0].web_retriever.http_status_guest=404],
 ['decode_px',o=>o.rows[0].web_retriever.decoded_px_guest=[0,0]],
 ['fake_wire',o=>o.rows[0].web_retriever.transfer_bytes_guest=16000],
 ['source_swap',o=>o.rows[0].published_source_url='https://example.org/false.jpg'],
 ['catalog_swap',o=>o.rows[0].authoritative_candidate.accession='USN 888888'],
 ['wrong_NH',o=>o.rows[6].authoritative_candidate.accession='NH 69585'],
 ['courtesy_erase',o=>o.rows[6].authoritative_candidate.rights_status='PUBLIC_DOMAIN'],
 ['fake_rehost_right',o=>o.rows[6].authoritative_candidate.permission_to_rehost_confirmed=true],
 ['fake_replacement',o=>o.rows[2].actions.wp_post=true],
 ['invent_960_derived',o=>o.rows[0].authoritative_candidate.derivative_dimensions_px=[960,720]],
 ['upscale',o=>o.rows[0].authoritative_candidate.max_derivative_width_px=1280],
 ['false_download',o=>o.release.binary_downloads=1],
 ['missing_row',o=>o.rows.pop()],
 ['duplicate_slot',o=>o.rows[1].slot=o.rows[0].slot],
 ['fake_catalog_medium',o=>o.rows[2].authoritative_candidate.medium_1280x1280_catalog_kb=20],
];
for(const [name,mutate] of cases)test(name,()=>{const x=clone(fixture);mutate(x);const errors=validate(x);if(name==='control')assert.deepEqual(errors,[]);else assert.ok(errors.length>0, 'must hold: '+name);});

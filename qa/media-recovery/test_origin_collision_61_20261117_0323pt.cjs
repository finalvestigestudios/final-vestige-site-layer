'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_origin_collision_61_20261117_0323pt.cjs');
const v=JSON.parse(fs.readFileSync(path.join(__dirname,'origin_collision_61_20261117_0323pt.json'),'utf8'));
const cp=()=>JSON.parse(JSON.stringify(v));
test('baseline',()=>assert.equal(validate(cp()).ok,true));
const cases=[
['fake 404',x=>x.identical_original_url_groups[0].slots[0].guest_http_status=404],
['fake success',x=>x.identical_original_url_groups[0].slots[0].guest_decode=true],
['fake wire bytes',x=>x.identical_original_url_groups[0].slots[0].guest_transfer_bytes=10000],
['claim 42',x=>x.claims.reported_42_visitor_broken_confirmed=true],
['claim 76 percent',x=>x.claims.proposed_76_percent_wire_reduction_measured=true],
['claim byte measurement',x=>x.claims.wire_bytes_observed=500],
['wrong 355 count',x=>x.historical.image_references=354],
['wrong unique count',x=>x.historical.distinct_urls=354],
['fake Wikimedia total',x=>x.host_concentration.find(z=>z.host==='commons.wikimedia.org').count++],
['remove host',x=>x.host_concentration.pop()],
['remove duplicate group',x=>x.identical_original_url_groups.pop()],
['break duplicate view equality',x=>x.identical_original_url_groups[0].slots[0].view_url='https://other.invalid/a.jpg'],
['change duplicate slot',x=>x.identical_original_url_groups[0].slots[0].key='999:1'],
['deny Teton mismatch',x=>x.identical_original_url_groups.find(z=>z.slots[0].key==='291:2').classification='OK'],
['claim Mann broken',x=>x.identical_original_url_groups.find(z=>z.slots[0].key==='213:2').classification='HTTP_404'],
['wrong NARA ID',x=>x.archive_candidate.accession='NAID 111111'],
['change ratio',x=>x.archive_candidate.proportional_review_px=[960,960]],
['erase crop caveat',x=>x.archive_candidate.crop_revision=''],
['fake downloaded hash',x=>x.archive_candidate.downloaded_binary_sha256='aaa'],
['authorize rights',x=>x.archive_candidate.rights_approved=true],
['authorize rehosting',x=>x.archive_candidate.wp_rehosting_approved=true],
['allow WordPress writes',x=>x.safety.no_wp_write=false],
['rewrite source SHA',x=>x.source_parts.files[0].sha='deadbeef']
];
for(const [name,change]of cases)test('reject '+name,()=>{const x=cp();change(x);assert.equal(validate(x).ok,false,name)});

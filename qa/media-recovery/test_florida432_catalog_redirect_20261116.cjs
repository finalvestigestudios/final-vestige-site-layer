'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_florida432_catalog_redirect_20261116.cjs');
const audit=require('./florida432_five_catalog_redirect_custody_20261116_1326pt.json');
const copy=()=>JSON.parse(JSON.stringify(audit));
test('five actual primary catalog entries remain HOLD',()=>{const r=validate(copy());assert.equal(r.ok,true,JSON.stringify(r.errors));assert.equal(r.decision,'HOLD')});
const scenarios=[
['guest HTTP',a=>a.rows[0].guest_http_status=200],
['guest 404',a=>a.rows[0].guest_http_status=404],
['fake transfer bytes',a=>a.rows[0].guest_transfer_bytes=100],
['fake currentSrc',a=>a.rows[0].guest_current_src='x'],
['fake decoded image',a=>a.rows[0].guest_decode=true],
['fake 42 guest failures',a=>a.guest_42_failures_verified=true],
['fake 76 percent savings',a=>a.visitor_76_percent_savings_measured=true],
['tool code as origin HTTP',a=>a.rows[0].retriever.origin_http_status=500],
['wrong redirect target',a=>a.rows[0].retriever.redirect_target='x'],
['wrong accession',a=>a.rows[0].accession='X'],
['wrong catalog URL',a=>a.rows[1].catalog_url='x'],
['wrong archive date',a=>a.rows[2].catalog_date='2026'],
['wrong authored URL',a=>a.rows[3].edit_url='x'],
['pretend catalog live HTTP',a=>a.rows[0].catalog_evidence_method='HTTP'],
['unapproved item rights',a=>a.rows[0].item_rights_review='APPROVED'],
['unauthorized caching',a=>a.rows[0].cache_authorized=true],
['unauthorized staging',a=>a.rows[0].staging_authorized=true],
['unauthorized post rewrite',a=>a.rows[0].post_rewrite_authorized=true],
['pretend matching pixels',a=>a.rows[0].pixel_and_crop_identical=true],
['invent native size',a=>a.rows[0].decoded_native_dimensions=[960,540]],
['invent derivative dimensions',a=>a.rows[0].proposed_review_dimensions=[960,540]],
['invent binary SHA',a=>a.rows[0].binary_sha256='a'.repeat(64)],
['upscale past 960',a=>a.rows[0].cap_width_no_upscale_px=1920],
['drop source slot',a=>a.rows.pop()],
['duplicate source slot',a=>a.rows[4].slot=a.rows[0].slot],
['confuse storage with wire',a=>a.oversize.guest_transfer_bytes=400],
['claim image downloaded',a=>a.downloads=1],
['claim WP write',a=>a.wordpress_writes=1],
['wrong pinned prior blob',a=>a.pinned_prior_blob_sha='0'.repeat(40)]
];
for(const [name,mutate] of scenarios)test('fail closed: '+name,()=>{const a=copy();mutate(a);assert.equal(validate(a).ok,false,name)});

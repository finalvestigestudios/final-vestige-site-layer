'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_scotch_cap_two_20261106.cjs');
const data=require('./scotch_cap_two_primary_20261106.json');
const copy=()=>JSON.parse(JSON.stringify(data));
test('untouched primary two-row audit passes',()=>assert.equal(validate(copy()).ok,true));
const cases=[
 ['wrong cohort',a=>a.baseline.current_post_count=61],
 ['invented confirmed broken',a=>a.baseline.visitor_verified_broken_count=42],
 ['invented 76 percent saved',a=>a.baseline.measured_savings_pct=76],
 ['invented origin HTTP',a=>a.targets[0].original_retrieval.origin_http=403],
 ['invented visitor HTTP',a=>a.targets[1].original_retrieval.visitor_browser_http=403],
 ['invented visitor broken flag',a=>a.targets[1].original_retrieval.visitor_broken=true],
 ['invented cold byte count',a=>a.targets[1].original_retrieval.cold_wire_bytes=100],
 ['bad published source URL',a=>a.targets[0].published_src='https://example.com/a.jpg'],
 ['bad museum alternative',a=>a.targets[1].candidate.url='https://example.com/fake.jpg'],
 ['incorrect portrait identification',a=>a.targets[0].subject='Tsunami debris'],
 ['portrait assigned debris URL',a=>a.targets[0].candidate.url=a.targets[1].candidate.url],
 ['unsupported binary identity',a=>a.targets[1].candidate.binary_identical=true],
 ['promote museum copyright',a=>a.targets[1].rights.item_public_domain_notice=true],
 ['copyright cleared without item review',a=>a.targets[1].rights.item_review='APPROVED'],
 ['overwide preview',a=>a.targets[1].candidate.proposed_dimensions=[961,742]],
 ['upscale small museum image',a=>a.targets[1].candidate.proposed_dimensions=[960,741]],
 ['invent 960px portrait',a=>a.targets[0].candidate.proposed_dimensions=[960,720]],
 ['invent native master',a=>a.targets[1].candidate.native_dimensions=[4000,3000]],
 ['WordPress production write',a=>a.release.wordpress_production_writes=1],
 ['third party caching',a=>a.release.image_caches=1],
 ['copy third party image',a=>a.release.image_downloads=1],
 ['duplicate Site QA collector',a=>a.release.site_qa_collector_duplicated=true],
 ['production release allowed',a=>a.release.approval_to_publish=true],
 ['missing row',a=>a.targets.pop()]
];
for(const [label,change] of cases)test('reject '+label,()=>{let a=copy();change(a);assert.equal(validate(a).ok,false,label)});


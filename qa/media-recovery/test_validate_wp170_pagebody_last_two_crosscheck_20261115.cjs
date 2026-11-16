'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validateAudit}=require('./validate_wp170_pagebody_last_two_crosscheck_20261115.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'wp170_pagebody_last_two_crosscheck_20261115.json'),'utf8'));
const copy=()=>structuredClone(original);
test('baseline 170-page custody audit is valid',()=>assert.deepEqual(validateAudit(original),[]));
const bad=[
 ['remove published page',d=>d.scanned_pages.pages.shift()],
 ['duplicate page id',d=>d.scanned_pages.pages[1].id=d.scanned_pages.pages[0].id],
 ['wrong published count',d=>d.scanned_pages.published_count=91],
 ['wrong draft count',d=>d.scanned_pages.draft_count=77],
 ['fabricate a recovered image',d=>d.scanned_pages.pages[0].matched_needles=['asset 482']],
 ['weaken match needle',d=>d.scanned_pages.comparison_needles[0]='image'],
 ['invent browser HTTP',d=>d.media[0].guest_http_status=200],
 ['invent visitor bytes',d=>d.media[1].guest_encoded_bytes=1000],
 ['mark orphan from negative scope',d=>d.media[0].disposition='safe_to_delete'],
 ['authorize rehosting',d=>d.media[1].cache_authorized=true],
 ['authorize publication',d=>d.media[1].publication_authorized=true],
 ['infer 76 percent saving',d=>d.counts.validated_network_saving_percent=76],
 ['tamper source URL',d=>d.media[1].source_url='https://example.test/image.jpg'],
 ['tamper native resolution',d=>d.media[0].native.width=100],
 ['stretch 960px candidate',d=>d.media[1].candidate_max_960.height=540],
 ['tamper stored bytes',d=>d.media[1].file_bytes=123],
 ['change crop provenance',d=>d.media[1].catalogs[1].url='https://example.test/wrong'],
 ['erase rights hold',d=>d.media[0].rights_hold=false],
 ['steal Site QA collector scope',d=>d.safe_change_policy.site_qa_cold_browser_owner='Media Recovery']
];
for(const [name,change] of bad) test('reject: '+name,()=>{const d=copy();change(d);assert.ok(validateAudit(d).length>0)});

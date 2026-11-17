'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_wp66_132_20_exposure_20261115.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'wp66_132media_20oversized_inline_exposure_20261115.json'),'utf8'));
const mutated=(fn)=>{const x=structuredClone(fixture);fn(x);return x;};
test('frozen 66-post 132-media original inventory is valid',()=>assert.equal(validate(fixture).ok,true,validate(fixture).errors.join(',')));
const negatives=[
['missing post',x=>x.post_ids_read.pop()],
['duplicate post',x=>x.post_ids_read[2]=x.post_ids_read[1]],
['invented guest 200',x=>x.records[0].published_inline_uses[0].guest_http_status=200],
['invented visitor 76%',x=>x.visitor_wire_reduction_percent=76],
['unproven 42 broken claim',x=>x.reported_42_broken_guest_verified=42],
['fake network audit',x=>x.guest_http_audit_performed=true],
['wrong stored bytes',x=>x.oversize_total_stored_bytes++],
['wrong media census',x=>x.media_attachments_read=131],
['missing oversized record',x=>x.records.pop()],
['duplicate media ID',x=>x.records[1].attachment_id=x.records[0].attachment_id],
['wrong native dimensions',x=>x.records[0].native_height++],
['upscaled width',x=>x.records[0].conditional_review_width=1100],
['stretched review height',x=>x.records[0].conditional_review_height=400],
['rights claimed clear',x=>x.records[0].rights_status='CLEARED'],
['rehosting allowed',x=>x.records[0].cache_authorized=true],
['WordPress upload allowed',x=>x.records[0].wp_upload_authorized=true],
['published block rewrite allowed',x=>x.records[0].post_rewrite_authorized=true],
['invented source URL',x=>x.records[0].published_inline_uses[0].wp_view_img_src='https://example.com/other.jpg'],
['duplicate published image slot',x=>x.records[0].published_inline_uses.push(structuredClone(x.records[0].published_inline_uses[0]))],
['false srcset',x=>x.records.find(r=>r.attachment_id===39).published_inline_uses[0].srcset_present=true],
['unverified transferred bytes',x=>x.records[0].published_inline_uses[0].guest_transferred_bytes=12345],
['false production changes',x=>x.production_changes=1]
];
for(const [name,fn] of negatives)test('reject '+name,()=>assert.equal(validate(mutated(fn)).ok,false));

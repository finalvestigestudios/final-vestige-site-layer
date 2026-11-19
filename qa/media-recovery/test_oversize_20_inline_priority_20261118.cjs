'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {derive,check,gitBlob}=require('./oversize_20_inline_priority_20261118.cjs');
const data=[
[388,8176362,'299:1',true],[2640,7422309,null,null],[1258,5553669,'621:1',true],[1257,4798395,'621:0',true],
[2636,4462854,null,null],[39,2892087,'34:0',false],[43,2836245,'38:0',false],[389,2822969,'299:0',true],
[40,2552136,'35:0',false],[41,2498247,'36:0',false],[42,2488823,'37:0',false],[382,2318980,'299:7',true],
[482,2293016,null,null],[405,2201573,null,null],[293,2090327,null,null],[2148,2030948,null,null],
[2432,2010886,null,null],[2638,1745282,null,null],[2637,1647642,null,null],[1714,1543002,'269:1',true]
];
function mock(){return {schema:'fv-oversized-current-66-inline-crosswalk-v1',items:data.map(([id,bytes,slot,srcset])=>({id,filename:'2026/08/img-'+id+'.png',original_bytes:bytes,inline_exact_origin_slots:slot?[{slot_id:slot,post_url:'https://finalvestige.com/post-'+id+'/',view_img_src:'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/img-'+id+'.png?resize=1024%2C576&ssl=1',has_srcset:srcset,has_sizes:!!srcset}]:[]})),summary:{total_stored_bytes:64385752}};}
function bad(label,fn){test(label,()=>{const x=mock();fn(x);assert.throws(()=>derive(x))})}
test('correct SHA algorithm for known text',()=>{assert.equal(gitBlob('abc'),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f')});
bad('reject missing original',x=>x.items.pop());
bad('reject total byte drift',x=>x.summary.total_stored_bytes=0);
bad('reject duplicate media ID',x=>x.items[1].id=x.items[0].id);
bad('reject inline different origin',x=>x.items[0].inline_exact_origin_slots[0].view_img_src=x.items[0].inline_exact_origin_slots[0].view_img_src.replace('img-388','img-1258'));
bad('reject origin proxy spoof',x=>x.items[0].inline_exact_origin_slots[0].view_img_src='https://evil.example/img.png');
bad('reject non-site article URL',x=>x.items[0].inline_exact_origin_slots[0].post_url='https://evil.example/post');
bad('reject duplicate source slot',x=>x.items[2].inline_exact_origin_slots[0].slot_id='299:1');
bad('reject media smaller than 1.5MB',x=>x.items[2].original_bytes=1500000);
bad('reject fake filename traversal',x=>x.items[2].filename='2026/08/../evil.jpg');
bad('reject missing explicit responsive flag',x=>delete x.items[2].inline_exact_origin_slots[0].has_srcset);
bad('reject unbounded image size query',x=>x.items[2].inline_exact_origin_slots[0].view_img_src=x.items[2].inline_exact_origin_slots[0].view_img_src.replace('1024','50000'));
bad('reject absent sizing transform',x=>x.items[2].inline_exact_origin_slots[0].view_img_src=x.items[2].inline_exact_origin_slots[0].view_img_src.split('?')[0]);
test('reject fake source blob with altered text',()=>{assert.throws(()=>check({},'fake'))});
test('valid 20-row fixture preserves strict categories and unknown wire bytes',()=>{const r=derive(mock());assert.equal(r.summary.originals_gt_1_5_MiB_binary,19);assert.equal(r.summary.no_srcset_inline_media,5);assert.equal(r.summary.no_srcset_inline_original_stored_bytes,13267538);assert.equal(r.summary.exact_inline_stored_original_bytes,38480915);assert.equal(r.summary.measured_before_bytes,null);assert.equal(r.release.wp_writes,0)});

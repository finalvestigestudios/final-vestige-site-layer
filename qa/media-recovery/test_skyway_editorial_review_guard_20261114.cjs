'use strict';
const assert = require('node:assert/strict');
const {review,inspectImageBlocks} = require('./skyway_editorial_review_guard_20261114.cjs');
const audit = require('./skyway_visual_fidelity_287_20261114.json');
const sources=[
'https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/IIYZWAFLJUQD3YGEYEKMG5PVXY.jpg',
'https://cloudfront-us-east-1.images.arcpublishing.com/tbt/555OWMWIJMI6TGNIIBWI6S7HAY.jpg',
'https://skywaydisaster.com/images/timeline2.jpg',
'https://img.connatix.com/ecf95169-f8cd-4cd5-8698-9bc54211f8e9/1_th.jpg',
audit.items[0].published_source_url,
audit.items[1].published_source_url
];
const oldalts=['Stopped car','Summit Venture','Collision diagram','Stopped auto',audit.items[0].published_alt,audit.items[1].published_alt];
const captions=['Stopped car caption','Summit Venture caption','Collision caption','Other car caption',audit.items[0].published_caption_html,audit.items[1].published_caption_html];
function img(i){return `<!-- wp:image {"sizeSlug":"large"} --><figure class="wp-block-image"><img src="${sources[i]}" alt="${oldalts[i]}"/><figcaption class="wp-element-caption">${captions[i]}</figcaption></figure><!-- /wp:image -->`;}
function fixture(){return {id:287,status:'publish',modified:audit.post_modified,content: Array.from({length:6},(_,i)=>`<!-- wp:paragraph --><p>Article paragraph ${i}.</p><!-- /wp:paragraph -->\n${img(i)}`).join('\n')};}
const cases=[
 ['control', ()=>{const r=review(fixture(),audit);assert.equal(r.proposed_diffs.length,2);assert.equal(r.inspected_image_blocks,6);assert.equal(r.status,'EDITORIAL_REVIEW_ONLY_NOT_APPLIED');assert.equal(r.wordpress_writes,0);assert.equal(r.visitor_network_bytes,null);assert.deepEqual(r.unchanged_image_slots,['287:0','287:1','287:2','287:3']);}],
 ['wrong post ID', p=>p.id=288],['draft post',p=>p.status='draft'],['missing content',p=>p.content=null],['large content',p=>p.content+='x'.repeat(200001)],['stale modified',p=>p.modified='2026-11-14T04:00:00'],
 ['remove block',p=>p.content=p.content.replace(img(4),'')],['add block',p=>p.content+=img(3)],
 ['source swap slot 4',p=>p.content=p.content.replace(sources[4],sources[3])],['source swap slot 5',p=>p.content=p.content.replace(sources[5],sources[4])],
 ['alt drift slot 4',p=>p.content=p.content.replace(oldalts[4],'Something else')],['alt drift slot 5',p=>p.content=p.content.replace(oldalts[5],'Something else')],
 ['caption drift slot 4',p=>p.content=p.content.replace(captions[4],'Wrong caption')],['caption drift slot 5',p=>p.content=p.content.replace(captions[5],'Wrong caption')],
 ['moved slot 4',p=>p.content=p.content.replace(img(4),img(0)).replace(img(0),img(4))],
 ['missing alt slot 4',p=>p.content=p.content.replace(` alt="${oldalts[4]}"`,'')],
 ['duplicate img slot 4',p=>p.content=p.content.replace(img(4),img(4).replace('</figure>','<img src="https://example.org/x" alt="x"/></figure>'))],
 ['duplicate caption slot 5',p=>p.content=p.content.replace(img(5),img(5).replace('</figure>','<figcaption>Other</figcaption></figure>'))],
 ['nonexistent image order',p=>p.content=p.content.replace(img(4),'<img src="https://example.org/foo" alt="foo"/>')]
];
const audits=[
 ['audit schema', a=>a.schema='made-up'],['audit id', a=>a.post_id=999],['audit date',a=>a.post_modified='2026-01-01'],
 ['audit item count',a=>a.items.pop()],['audit duplicate slot',a=>a.items[1].slot='287:4'],
 ['audit unknown slot',a=>a.items[0].slot='287:3'],['audit false source change',a=>a.items[0].proposed_image_src_change=true],
 ['audit false WP write',a=>a.items[1].wordpress_production_write=true],['audit false rights cache',a=>a.items[0].rights_to_copy_or_cache=true],
 ['audit false copyright cleared',a=>a.items[0].copyright_review_complete=true],['audit false binary match',a=>a.items[1].same_binary_or_crop_verified=true],
 ['audit false browser status',a=>a.items[0].actual_guest_http_status=404],['audit false wire bytes',a=>a.items[0].guest_wire_bytes=100],
 ['audit auto apply',a=>a.items[0].editorial_status='APPROVED'],['audit policy WP writes',a=>a.policy.wordpress_production_writes=1],
 ['audit policy cache',a=>a.policy.cache_or_rehost=true],['audit policy homepage',a=>a.policy.homepage_design_modified=true],
 ['audit malicious alt',a=>a.items[0].proposed_alt='<script>alert(1)</script>'],['audit malicious caption',a=>a.items[0].proposed_caption_html='<img src=x>'],
 ['audit empty change',a=>{a.items[0].proposed_alt=a.items[0].published_alt;a.items[0].proposed_caption_html=a.items[0].published_caption_html;}]
];
let pass=0;
for(const [name,mutate] of cases){try{const p=fixture();if(name==='control')mutate();else {mutate(p);assert.throws(()=>review(p,audit));}pass++;}catch(e){throw Error(`FAIL ${name}: ${e.message}`);}}
for(const [name,mutate] of audits){try{const a=structuredClone(audit);mutate(a);assert.throws(()=>review(fixture(),a));pass++;}catch(e){throw Error(`FAIL ${name}: ${e.message}`);}}
assert.equal(inspectImageBlocks(fixture().content).length,6);pass++;
console.log(`PASS ${pass}/${pass} native Node assertions; offline only`);

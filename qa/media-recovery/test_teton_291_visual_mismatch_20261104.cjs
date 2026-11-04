'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_teton_291_visual_mismatch_20261104.cjs');
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'teton_291_visual_mismatch_20261104.json'),'utf8'));
const f=JSON.parse(fs.readFileSync(path.join(__dirname,'parts','02.json'),'utf8'));
const copy=()=>structuredClone(a);
test('six original identities and every release hold passes',()=>assert.deepEqual(validate(copy(),f),[]));
const mutations=[
['invented origin 404',x=>x.rows[0].origin_http_status=404],
['invented visitor 200',x=>x.rows[2].guest_browser_http_status=200],
['invented decoded',x=>x.rows[2].guest_browser_decoded=true],
['invented naturalWidth',x=>x.rows[2].guest_natural_width=1000],
['invented transferred bytes',x=>x.rows[2].guest_transfer_bytes=10000],
['false broken image',x=>x.rows[2].broken_in_browser=true],
['swapped photograph source',x=>x.rows[2].url='https://example.org/different.jpg'],
['swapped original ALT',x=>x.rows[5].alt='fake'],
['changed source host',x=>x.rows[0].host='bad.invalid'],
['duplicate slot key',x=>x.rows[5].key='291:2'],
['missing slot',x=>x.rows.pop()],
['false WordPress match',x=>x.rows[2].word_press_match=false],
['rights whitewash',x=>x.rows[0].rights_review='CLEAR'],
['copied without rights',x=>x.rows[0].can_copy=true],
['WordPress write',x=>x.rows[0].wp_write=true],
['960 px exceeded',x=>x.rows[0].max_derivative_width=1024],
['upscale enabled',x=>x.rows[0].allow_upscale=true],
['fake intrinsic dimensions',x=>x.rows[0].intrinsic_dimensions=[1000,800]],
['fake target height',x=>x.rows[0].target_height_px=768],
['wrong slot to correct',x=>x.confirmed_visual_issue.incorrect_slot='291:5'],
['falsify unique source count',x=>x.confirmed_visual_issue.unique_urls=6],
['change issue to 404',x=>x.confirmed_visual_issue.kind='BROWSER_BROKEN'],
['remove NARA candidate',x=>x.candidate_mappings[0].catalog='https://example.org'],
['candidate release',x=>x.candidate_mappings[0].rehost_approved=true],
['candidate false rights',x=>x.candidate_mappings[0].rights='PUBLIC_DOMAIN'],
['candidate overwide',x=>x.candidate_mappings[0].width_limit=1200],
['candidate invented height',x=>x.candidate_mappings[0].height=999],
['42 alleged broken proven',x=>x.status.claimed_42_broken_verified=true],
['76 percent claimed measured',x=>x.status.claimed_76_percent_wire_savings_measured=true],
['guest count invented',x=>x.status.actual_guest_broken_count=0],
['production repaired',x=>x.status.production_images_fixed=1],
['third-party binaries downloaded',x=>x.status.third_party_downloads=1],
['WordPress edited',x=>x.status.wordpress_writes=1],
['homepage edited',x=>x.status.homepage_edits=1],
['subscription spend',x=>x.status.subscription_spend=1],
['61 post baseline falsified',x=>x.frozen_inventory.posts=60]
];
for(const [name,mutate] of mutations)test('fails closed: '+name,()=>{let x=copy();mutate(x);assert.notEqual(validate(x,f).length,0)});

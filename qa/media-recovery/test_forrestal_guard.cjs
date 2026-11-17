'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {verifyForrestal,isSafeRecord,loadSnapshot}=require('./forrestal_guard.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'forrestal_primary_20261030.json'),'utf8'));
const snapshot=loadSnapshot();
const cp=()=>JSON.parse(JSON.stringify(original));
test('all six source-specific records match fixed original census and remain held',()=>assert.deepEqual(verifyForrestal(cp(),snapshot),[]));
test('only trusted primary evidence hostnames allowed',()=>{
 assert.equal(isSafeRecord('https://www.history.navy.mil/a'),true);
 assert.equal(isSafeRecord('https://www.dvidshub.net/image/985674'),true);
 for(const v of ['http://www.dvidshub.net/a','https://evil.com/a','https://www.dvidshub.net.evil.com/a','https://commons.wikimedia.org.evil.com/a','javascript:alert(1)','https://www.dvidshub.net/a\\evil'])assert.equal(isSafeRecord(v),false);
});
const mutations=[
 ['falsified broken status',d=>d.rows[0].broken_in_real_browser=true],
 ['falsified HTTP status',d=>d.rows[0].current_browser_http_status=404],
 ['falsified performance bytes',d=>d.rows[1].current_browser_transfer_bytes=21000],
 ['falsified natural width',d=>d.rows[0].current_browser_natural_width_px=960],
 ['unapproved reuse',d=>d.rows[4].item_rights_cleared=true],
 ['unapproved CMS edit',d=>d.rows[5].word_press_post_edited=true],
 ['pretend download happened',d=>d.rows[3].candidate_downloaded=true],
 ['pretend visual identity matched',d=>d.rows[3].visual_match_proven=true],
 ['unsafe 1920-pixel target',d=>d.rows[1].release_plan.max_width_px=1920],
 ['forbidden upscale',d=>d.rows[1].release_plan.no_upscale=false],
 ['invent final dimensions',d=>d.rows[1].release_plan.target_dimensions_px=[960,700]],
 ['invent measured reduction',d=>d.counts.savings_percent=76],
 ['invent 42 broken',d=>d.counts.visitor_verified_broken=42],
 ['wrong source image URL',d=>d.rows[0].original_source_url='https://example.com/image.jpg'],
 ['wrong source alt',d=>d.rows[2].stored_alt='Different event'],
 ['duplicate slot',d=>d.rows[1].image_key='289:0'],
 ['mutate Navy candidate to external host',d=>d.rows[3].candidate.url='https://history.navy.mil.evil.com/a'],
 ['damage photo mislabeled as aerial',d=>{d.rows[2].candidate.caption_revision_required=false;d.rows[2].release_plan.alt_change_requires_editorial_approval=false;}],
 ['wrong year for modern training',d=>d.rows[4].candidate.photo_year=1967],
 ['wrong 2013 memorial ID',d=>d.rows[5].candidate.catalog_id='130726-N-ST310-008'],
 ['alternative falsely labeled exact',d=>d.rows[1].candidate.kind='same_stored_frame_official_catalog_identifier'],
 ['catalog link changed without release plan',d=>d.rows[1].candidate.url='https://www.history.navy.mil/other'],
 ['untrustworthy source HTTPS',d=>d.rows[1].candidate.url='http://www.history.navy.mil/other'],
 ['unsourced new row',d=>d.rows.push(JSON.parse(JSON.stringify(d.rows[0])))]
];
for(const [name,change] of mutations)test('rejects '+name,()=>{const d=cp();change(d);assert.ok(verifyForrestal(d,snapshot).length>0,name)});

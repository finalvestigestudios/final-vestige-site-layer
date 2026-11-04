'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'research-desk-r126-ledger-candidate.html'),'utf8');
const c=JSON.parse(fs.readFileSync(path.join(__dirname,'research-desk-r126-crosswalk.json'),'utf8'));
const count=(needle)=>html.split(needle).length-1;
test('immutable source template provenance',()=>{assert.equal(c.source.pr,158);assert.equal(c.source.blob_sha,'403d128c57b9bc82dac7c619651689070edef86c');});
test('six unique and explicit per-record source roles',()=>{assert.deepEqual(c.records.map(x=>x.id),['01','02','03','04','05','06']);assert.equal(count('data-fvx-photo-role="context"'),6);for(let i=1;i<=6;i++)assert.equal(count('data-fvx-source-role="0'+i+'"'),1);});
test('preserves all 14 known outbound source occurrences including footer links',()=>{
 const links=[...html.matchAll(/href="(https:\/\/[^"]+)"/g)].map(m=>m[1]).sort();
 const expected=c.records.flatMap(x=>[x.photo.url,x.claim_source.url]).concat(['https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/']).sort();
 assert.deepEqual(links,expected);
});
test('preserves native no-JS record and disclosure structures',()=>{assert.equal(count('data-fvx-record'),6);assert.equal(count('data-fvx-search='),6);assert.equal(count('<details class="fv-ex2-ledger__fulltext"'),6);assert.equal(count('>NASA photo source page ↗'),6);assert.equal(count('>Separate NASA report or historical overview ↗'),6);assert.match(html,/data-fvx-custody-rule/);});
test('separate document roles are visible, not only machine metadata',()=>{assert.match(html,/not a Review Board report/);assert.match(html,/not the fire-event sensor trace/);assert.match(html,/2017 retrospective exhibit/);});
test('catalog is unconfirmed, not represented as verified',()=>{assert.equal(c.records[0].photo.precision,'month_only');assert.match(html,/proposed S67-19766, not corroborated on source page/);assert.doesNotMatch(html,/NASA S67-19766 · NASA/);});
test('photo rights remain unapproved and no NASA endorsement is claimed',()=>{assert.equal(c.usage.rights_reviews_complete,0);assert.equal(c.usage.rights_reviews_required,6);assert.match(html,/not NASA-endorsed/);});
test('no tracking, commerce, copied photos, speculative map edges',()=>{assert.doesNotMatch(html,/<form\b|<iframe\b|<script\b|<img\b|<video\b|payhip|sendBeacon|localStorage/i);assert.deepEqual(c.geo.verified_pins,[]);assert.deepEqual(c.geo.verified_edges,[]);assert.equal(c.conversion.paid_offer,'UNVERIFIED_NOT_ACTIVATED');});

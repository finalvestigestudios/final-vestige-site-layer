'use strict';
const fs=require('node:fs'), assert=require('node:assert/strict'), path=require('node:path');
const d=__dirname, read=x=>fs.readFileSync(path.join(d,x),'utf8');
const a=read('ZEN12_A_TEXT.html'), b=read('ZEN12_B_OPTIONAL_FILM.html'), hub=read('MIND_HUB_REVIEW_ONLY.html');
const m=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
let passed=0; function check(name,fn){fn();passed++;process.stdout.write('PASS '+name+'\n');}
for(const [label,h] of [['A',a],['B',b]]){
 check(label+' HTML document',()=>assert.match(h,/<!doctype html>/));
 check(label+' language',()=>assert.match(h,/<html lang="en">/));
 check(label+' viewport',()=>assert.match(h,/name="viewport"/));
 check(label+' noindex',()=>assert.match(h,/noindex,nofollow/));
 check(label+' disabled CTA',()=>assert.match(h,/<button type="button" disabled aria-disabled="true">/));
 check(label+' proximate explicit commission disclosure',()=>{assert.match(h,/If you purchase through an authorized link on this page, Final Vestige may earn a commission/);assert.ok(h.indexOf('Commercial disclosure for a future approved link')<h.indexOf('<button type="button" disabled'));});
 check(label+' no scripts',()=>assert.doesNotMatch(h,/<script\b/i));
 check(label+' no form',()=>assert.doesNotMatch(h,/<form\b/i));
 check(label+' no merchant href',()=>assert.doesNotMatch(h,/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|brainwaveshots\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i));
 check(label+' evidence cited',()=>{assert.match(h,/10\.1371\/journal\.pone\.0286023/);assert.match(h,/10\.3758\/BF03208840/);});
}
check('B has optional content',()=>assert.match(b,/Optional 42-second original film concept/));
check('A does not contain video concept',()=>assert.doesNotMatch(a,/Optional 42-second original film concept/));
check('B no autoplay',()=>assert.doesNotMatch(b,/autoplay[\s=>]/i));
check('B original SVG accessible',()=>{assert.match(b,/<svg[^>]*role="img" aria-labelledby/);assert.match(b,/<title id="poster-title">/);assert.match(b,/<desc id="poster-desc">/);});
check('six 7s captions',()=>assert.equal((read('ORIGINAL_42S_CAPTIONS.vtt').match(/--> /g)||[]).length,6));
check('caption end 42s',()=>assert.match(read('ORIGINAL_42S_CAPTIONS.vtt'),/00:00:42\.000/));
check('all A buyer substantive copy in B',()=>{const get=x=>[...x.matchAll(/<section aria-labelledby="p\d+">[\s\S]*?<\/section>/g)].map(v=>v[0]);assert.deepEqual(get(a),get(b));assert.equal(get(a).length,7);});
check('hub has four streams',()=>{for(const x of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(hub.includes(x));});
check('hub no merchant links',()=>assert.doesNotMatch(hub,/href=["']https?:\/\/(?:zen12\.com|inspire3\.com)/i));
check('claims nonempty',()=>assert.ok(m.claims.length>=25));
check('FV affiliate unverified',()=>assert.equal(m.release.affiliate_activation,false));
check('commerce closed',()=>assert.equal(m.release.commercial_cta_enabled,false));
check('one funnel',()=>assert.equal(m.release.duplicate_email_forms,false));
check('no tracking script',()=>assert.equal(m.release.tracking_script,false));
check('no simulated sales claimed',()=>assert.equal(m.release.actual_settled_sales,false));
check('referrals not sales',()=>assert.match(read('CREATOR_FUNNEL_AND_METRICS.md'),/affiliate_outbound_click != sale/));
const net=(r,q)=>Number.isFinite(r)&&Number.isFinite(q)&&q>0?1000*r/q:null;
check('unknown denominator null',()=>assert.equal(net(10,null),null));
check('zero denominator null',()=>assert.equal(net(10,0),null));
check('valid sample arithmetic only',()=>assert.equal(net(25,1000),25));
process.stdout.write('TOTAL PASS '+passed+'\n');

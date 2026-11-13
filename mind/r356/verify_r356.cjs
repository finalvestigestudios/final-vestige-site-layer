/* R356 reproducible static guard: node mind/r356/verify_r356.cjs
   No network calls, no tracking, no merchant contact. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=__dirname, A=fs.readFileSync(path.join(root,'ZEN12_A_TEXT.html'),'utf8'),
B=fs.readFileSync(path.join(root,'ZEN12_B_OPTIONAL_FILM.html'),'utf8'),
H=fs.readFileSync(path.join(root,'MIND_HUB_REVIEW.html'),'utf8'),
M=JSON.parse(fs.readFileSync(path.join(root,'CLAIM_SOURCE_MATRIX.json'),'utf8')),
V=fs.readFileSync(path.join(root,'ORIGINAL_42S_CAPTIONS.vtt'),'utf8');
let checks=0;function ok(test,msg){assert.ok(test,msg);checks++}
for(const [label,page] of [['A',A],['B',B]]) {
ok(page.startsWith('<!doctype html>'),label+' doctype');
ok(/<html lang="en">/.test(page),label+' language');
ok(/name="viewport"/.test(page),label+' mobile');
ok(/name="robots" content="noindex,nofollow"/.test(page),label+' prelaunch noindex');
ok(/href="https:\/\/finalvestige.com\/focus\/"/.test(page),label+' existing funnel');
ok(/Affiliate disclosure/.test(page),label+' adjacent disclosure');
ok(/may earn a commission/.test(page),label+' plain commission');
ok(/<button[^>]*disabled[^>]*>Merchant purchase link unavailable/.test(page),label+' disabled CTA');
ok(!/<script\b/i.test(page),label+' no scripts');
ok(!/<form\b/i.test(page),label+' no duplicate signup');
ok(!/<iframe\b/i.test(page),label+' no third-party embed');
ok(!/<video\b|autoplay/i.test(page),label+' no untested playback');
ok(!/href="https:\/\/(zen12|hypnosislive|brainwaveshots)\.[^"]*\?/.test(page),label+' no tracked merchant link');
ok(page.indexOf('Affiliate disclosure')<page.indexOf('Merchant purchase link unavailable'),label+' disclosure precedes control');
}
ok(B.includes('Optional short film / 42-second review concept'),'B original film concept');
ok(!A.includes('Optional short film / 42-second review concept'),'A no film');
const getCore=s=>s.slice(s.indexOf('<section id="what">'),s.indexOf('<section id="film">')>=0?s.indexOf('<section id="film">'):s.indexOf('<section id="sources">'));
ok(getCore(A)===getCore(B),'identical substantive buyer guide before film');
ok(H.includes('NOT LIVE'),'hub marked draft');
ok(H.includes('puysegurs-animal-magnetism-files'),'hub historical archive');
ok(H.includes('2026/11/02/change-blindness'),'hub existing article');
ok(M.affiliate_authorization.all_commercial_links_disabled,'affiliate authorization blocked');
ok(M.release_gates.every(g=>g.status==='HARD_HOLD'),'all gates hold');
ok(M.claims.filter(c=>c.publish_as_factual===false).length>=7,'unsupported claims tagged');
ok(V.startsWith('WEBVTT'),'caption format');
ok((V.match(/--> /g)||[]).length===6,'six caption segments');
ok(V.includes('00:00:42.000'),'film duration');
ok(!/https?:\/\/[^\s]+(aff_id|hop=|clickid=)/i.test(A+B),'no invented tracking URL');
console.log('PASS',checks,'static checks; gate count',M.release_gates.length);

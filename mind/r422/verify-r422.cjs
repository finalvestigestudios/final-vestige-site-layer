// Pure Node offline static guard; no network, no imports beyond node builtins.
// Run from repository root: node mind/r422/verify-r422.cjs
const fs=require('node:fs'), assert=require('node:assert/strict'),path=require('node:path');
const dir=__dirname;const read=x=>fs.readFileSync(path.join(dir,x),'utf8');
const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),
hub=read('MIND_ARCHIVE_SOURCE_ONLY.html'),art=read('THE_STRANGER_BEHIND_THE_DOOR.md'),
vtt=read('ZEN12_42_SECOND_CAPTIONS.vtt'),m=JSON.parse(read('CLAIM_PERMISSION_MATRIX.json')),
plan=read('CONVERSION_ACCEPTANCE.md');
const checks=[];
const check=(name,fn)=>{fn();checks.push(name)};
check('same buyer core',()=>{const ex=s=>s.split('<section id="buyer-guide-core"')[1].split('</section>')[0];assert.equal(ex(a),ex(b));});
for(const [n,s] of [['A',a],['B',b],['hub',hub]]){
check(n+' no script',()=>assert(!/<script\b/i.test(s)));
check(n+' no iframe',()=>assert(!/<iframe\b/i.test(s)));
check(n+' no merchant anchors',()=>assert(!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i.test(s)));
check(n+' no active purchase',()=>assert(!/<a[^>]*>[^<]*(?:buy|purchase|order now)/i.test(s)));
check(n+' no signup form',()=>assert(!/<form\b/i.test(s)));
check(n+' no autoplay',()=>assert(!/\bautoplay\b(?=\s|=|>)/i.test(s.replace(/No autoplay/gi,''))));
check(n+' no dollar price',()=>assert(!/\$\s?\d/.test(s)));
check(n+' mobile viewport',()=>assert(/name="viewport"/.test(s)));
check(n+' keyboard focus visible',()=>assert(/focus-visible/.test(s)));
check(n+' free Focus route',()=>assert(s.includes('https://finalvestige.com/focus/')));
}
for(const [n,s] of [['A',a],['B',b]]){
check(n+' disclosure adjacent',()=>assert(/Affiliate disclosure:[\s\S]{0,420}<\/p><button type="button" disabled/.test(s)));
check(n+' disabled CTA',()=>assert(/<button type="button" disabled aria-disabled="true">/.test(s)));
check(n+' no merchant URL',()=>assert(!/https?:\/\/(?:www\.)?(zen12|hypnosislive|brainwaveshots|inspire3)\.com/i.test(s)));
check(n+' clear offer boundaries',()=>assert(s.includes('twelve levels')&&s.includes('four listening styles')&&s.includes('not')));
}
check('B original poster',()=>assert(/<svg\b/.test(b)&&/aria-label=/.test(b)));
check('B transcript',()=>assert(b.includes('<summary>Read the complete proposed film transcript')));
check('B caption route',()=>assert(b.includes('ZEN12_42_SECOND_CAPTIONS.vtt')));
check('VTT cues',()=>assert.equal((vtt.match(/-->/g)||[]).length,6));
check('VTT duration',()=>assert(vtt.includes('00:00:42.000')));
check('source citations',()=>assert(art.includes('https://doi.org/10.3758/BF03208840')&&art.includes('https://pubmed.ncbi.nlm.nih.gov/12230832/')));
check('article original scope',()=>assert(art.length>9500 && art.includes('Puységur') && art.includes('not a validated change-blindness test')));
check('matrix gates all HOLD',()=>assert(Object.values(m.gates).length>=25 && Object.values(m.gates).every(g=>g.status==='HOLD'&&g.evidence===null)));
check('matrix no earning links',()=>assert.equal(m.approved_affiliate_links.length,0));
check('seller claims marked',()=>assert(m.claims.some(c=>c.status==='EXCLUDED') && m.claims.some(c=>c.status==='SELLER_DESCRIPTION')));
check('no phantom revenue',()=>assert(m.realized_net_revenue_per_1000===null));
check('conversion event distinction',()=>assert(plan.includes('affiliate_click')&&plan.includes('commission_settled')&&plan.includes('NOT COMPUTABLE')));
check('owners protected',()=>assert(plan.includes('Praxxis/Grok') && plan.includes('Claude/Dispatch') && plan.includes('#49')));
check('no forced email',()=>assert(plan.includes('no forced email capture')));
console.log('R422 offline static checks PASS '+checks.length+'/'+checks.length);

// R265 source integrity tests — run: node mind/r265/test_r265.cjs (repo root)
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const files={article:read('THE-MACHINE-YOU-THOUGHT-YOU-UNDERSTOOD-UNPUBLISHED.md'),A:read('ZEN12-A-SOURCED-UNPUBLISHED.html'),B:read('ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html'),hub:read('MIND-ARCHIVE-UNPUBLISHED.html'),matrix:JSON.parse(read('CLAIMS-AND-COMMERCE-HARDHOLD.json')),plan:read('OFFER-TO-REVENUE-ACCEPTANCE.md')};
function verify(f){
  assert(f.article.includes('Rozenblit')&&f.article.includes('Fernbach')&&f.article.includes('https://pubmed.ncbi.nlm.nih.gov/21442007/'));
  assert(f.article.includes('No affiliate recommendation')||f.article.includes('No affiliate recommendation or active commercial link'));
  assert.equal(f.matrix.gates.length,16);
  assert(f.matrix.gates.every(g=>g.status==='HARD_HOLD'&&g.evidence===null));
  assert.equal(f.matrix.commerce.affiliate_link,null);
  assert.equal(f.matrix.commerce.net_revenue_per_1000_qualified_humans,null);
  assert(f.matrix.sources.some(s=>s.url.includes('ftc.gov')));
  for(const key of ['A','B','hub']){
    const s=f[key];
    assert(/<html lang="en">/.test(s)&&/<meta name="viewport"/.test(s)&&/<main>/.test(s));
    assert(/<button[^>]*disabled/.test(s));
    assert(/may earn a commission/i.test(s));
    assert(/no earning link is currently active|no partner link is active/i.test(s));
    assert(!/<(script|form|iframe|video|audio)\b/i.test(s));
    assert(!/autoplay\s*=|onclick\s*=/i.test(s));
    assert(!/href=["'][^"']*(zen12\.com|inspire3\.com|affiliates\.inspire3)/i.test(s));
    assert(!/href=["']https?:\/\/[^"']*(checkout|hop\.clickbank|awin1\.com)/i.test(s));
    assert(!/<a[^>]*\bdownload\b/i.test(s));
  }
  assert(!f.A.includes('Optional original 42-second film'));
  assert(f.B.includes('Optional original 42-second film'));
  assert(f.B.includes('<details>')&&f.B.includes('0–6s')&&f.B.includes('36–42s'));
  assert.equal((f.B.match(/data-start="/g)||[]).length,7);
  const removeFilm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,'');
  const body=s=>removeFilm(s).replace(/<title>[\s\S]*?<\/title>/,'').replace(/Draft [AB] —/g,'Draft X —');
  assert.equal(body(f.A),body(f.B));
  assert(f.plan.includes('merchant_confirmed_order')&&f.plan.includes('affiliate_outbound')&&f.plan.includes('NOT COMPUTABLE'));
  assert(!/affiliate revenue is confirmed|confirmed subscriber from gift UI|commission rate: [1-9]/i.test(f.plan));
  return true;
}
verify(files);
const negative=[
 ['unauthorized merchant link',f=>f.A=f.A.replace('Explore the existing Seven Day Focus Fieldbook','<a href="https://zen12.com/secret/">buy now</a>')],
 ['enabled purchase button',f=>f.A=f.A.replace('button type="button" disabled','button type="button"')],
 ['removed FTC disclosure',f=>f.B=f.B.replace('may earn a commission','might help us')],
 ['injected tracking',f=>f.hub += '<script src="https://tracker.invalid/a.js"></script>'],
 ['new signup form',f=>f.B += '<form><input type="email"></form>'],
 ['autoplay injection',f=>f.B += '<video autoplay></video>'],
 ['fabricated approval',f=>f.matrix.gates[0].status='APPROVED'],
 ['removed gate',f=>f.matrix.gates.pop()],
 ['invented payout',f=>f.matrix.commerce.affiliate_link='https://example.com/fake'],
 ['fake earnings metric',f=>f.matrix.commerce.net_revenue_per_1000_qualified_humans=400],
 ['false source',f=>f.article=f.article.replace('https://pubmed.ncbi.nlm.nih.gov/21442007/','https://invalid.example/')],
 ['unapproved publisher link B',f=>f.B=f.B.replace('Explore the existing Seven Day Focus Fieldbook','<a href="https://affiliates.inspire3.com/track">offer</a>')]
];
let rejected=0;
for(const [name,mutate] of negative){const f=JSON.parse(JSON.stringify(files));mutate(f);try{verify(f);throw new Error('FAILED TO REJECT '+name)}catch(e){if(String(e.message).startsWith('FAILED TO REJECT'))throw e;rejected++;}}
console.log('R265 baseline PASS; '+rejected+'/'+negative.length+' unsafe mutations rejected; source-only checks; native Node invocation complete.');

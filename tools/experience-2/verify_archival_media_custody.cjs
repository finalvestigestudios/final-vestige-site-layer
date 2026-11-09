/* FV EX2: read-only WordPress archival image and source-rights audit.
 * Input MUST be privately exported public Page 6 editor content; no submission or HTTP calls.
 * Usage: node tools/experience-2/verify_archival_media_custody.cjs /private/home.html
 */
'use strict';
const fs=typeof require==='function'?require('node:fs'):null;
const ASSETS=[
  ['apollo',473,'s67-19766.webp','finalvestige.com/wp-content/uploads/'],
  ['franklin',474,'Franklinexpeditionnote.jpg','finalvestige.com/wp-content/uploads/'],
  ['nypl',1258,'edit-017-v02-nypl-5003296-original.jpg','i0.wp.com/finalvestige.com/']
];
function attr(tag,key){const m=tag.match(new RegExp('(?:^|\\s)'+key+'\\s*=\\s*(["\\x27])([\\s\\S]*?)\\1','i'));return m?m[2]:null;}
function inspect(source){
 if(typeof source!=='string'||!source)throw new Error('Nonempty read-only Gutenberg export required');
 const tags=[...source.matchAll(/<img\b[^>]*>/gi)].map(x=>x[0]);
 const checks=[];const record=(id,ok)=>checks.push({id,pass:!!ok});
 for(const [key,id,file,host] of ASSETS){
   const matched=tags.filter(t=>(attr(t,'src')||'').includes(file));
   record(key+'.unique',matched.length===1);
   if(matched.length!==1)continue;
   const t=matched[0],src=attr(t,'src')||'';
   record(key+'.host',src.startsWith('https://')&&src.includes(host));
   record(key+'.alt',!!(attr(t,'alt')||'').trim()&&attr(t,'alt').trim().length>20);
   record(key+'.size',Number(attr(t,'width'))>0&&Number(attr(t,'height'))>0);
   record(key+'.responsive',!!attr(t,'srcset')&&!!attr(t,'sizes'));
   record(key+'.lazy',attr(t,'loading')==='lazy');
   if(key==='nypl')record('nypl.default_derivative',src.includes('?fit=1024%2C692'));
 }
 record('source.nasa',source.includes('https://www.nasa.gov/'));
 record('source.commons',source.includes('commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg'));
 record('source.nypl',source.includes('digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0'));
 record('folio.not_facsimile',source.includes('EDITORIAL TYPESETTING · NOT A FACSIMILE'));
 record('continuity.focus',source.includes('https://finalvestige.com/focus/'));
 record('continuity.jetpack',source.includes('wp:jetpack/subscriptions'));
 record('continuity.margins',(source.match(/class="fv-margin-strip__item"/g)||[]).length===72);
 return {pass:checks.every(x=>x.pass),checks,failures:checks.filter(x=>!x.pass).map(x=>x.id),
  certainty:'STATIC EDITOR SOURCE ONLY',not_verified:['live image transfer bytes/MIME','item-level copyright determination','real guest browser','WCAG/axe','Lighthouse/field CWV','Jetpack confirmation','CI/QD']};
}
if(typeof module!=='undefined')module.exports={inspect,ASSETS};
if(typeof require==='function'&&require.main===module){
 const file=process.argv[2];if(!file){console.error('Missing editor-source filepath');process.exit(2);}
 const out=inspect(fs.readFileSync(file,'utf8'));process.stdout.write(JSON.stringify(out,null,2)+'\n');process.exit(out.pass?0:1);
}

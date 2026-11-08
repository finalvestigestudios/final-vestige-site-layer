'use strict';
/* Final Vestige EX2: Page 6 atomic conversion/consent proposal.
   REVIEW ONLY. Offline; no WordPress, subscriber, or analytics writes.
   Source components: PR #1529 hero and PR #1542 Dispatch.
   node atomic_page6_review.cjs --home home-edit.json --focus focus-edit.json --out new-review.html
*/
// Independent SHA-256 of authenticated WordPress Page 6 context=edit raw source,
// verified 2026-11-08 UTC. See PAGE6_SOURCE_SHA_RECONCILIATION_20261108.md.
const PIN='1188d32a101896f12af9823dd7ca4b8a12b0c36684e82c069f23855a698e5669';
const HOME_DATE='2026-11-05T12:07:24', FOCUS_DATE='2026-11-05T17:44:02';
const CHAPTERS=['title','chronicle','evidence','inquiry','method-title','observer','mind-title'];
const REPLACEMENTS=[
 ['hero',
  '<a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>',
  '<a class="fv-hf__text-link" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>'],
 ['cadence','One email a week from Final Vestige.','New investigations, delivered when we publish.'],
 ['consent',
  'Unsubscribe anytime · <a href="/dispatch/">About The Dispatch</a>',
  'Sent when we publish. Some emails may contain recommendations that earn us a commission. Unsubscribe anytime · <a href="/dispatch/">About The Dispatch</a> · <a href="/privacy-policy/">Privacy Policy</a>'],
 ['readable-inline-type',
  '<p class="has-text-align-center" style="font-size:10px;font-weight:750;letter-spacing:0.1em;margin-top:18px">',
  '<p class="has-text-align-center" style="font-size:14px;font-weight:400;letter-spacing:normal;margin-top:18px">'],
 ['gutenberg-type',
  '<!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"10px","fontWeight":"750","letterSpacing":"0.1em"},"spacing":{"margin":{"top":"18px"}}}} -->',
  '<!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"14px","fontWeight":"400","letterSpacing":"normal"},"spacing":{"margin":{"top":"18px"}}}} -->']
];
const count=(s,t)=>s.split(t).length-1;
function unwrap(p){const d=p?.data||p;const c=typeof d?.content==='string'?d.content:d?.content?.raw;
  if(!d||typeof c!=='string')throw Error('HOLD: raw context=edit content required');
  return {d,c};}
function inventory(s){return {
  chapters:Object.fromEntries(CHAPTERS.map(c=>[c,count(s,'href="#fv-hf-'+c+'"')])),
  margins:count(s,'class="fv-margin-strip__item"'),
  focus:count(s,'https://finalvestige.com/focus/')+count(s,'href="/focus/"'),
  images:count(s,'<img '), scripts:count(s,'<script'),styles:count(s,'<style'),
  blocks:count(s,'<!-- wp:'),jetpack:count(s,'<!-- wp:jetpack/subscriptions'),
  apollo:count(s,'s67-19766.webp'),franklin:count(s,'Franklinexpeditionnote.jpg'),
  nypl:count(s,'nypl-5003296-original.jpg')
};}
function assemble(home,focus,{hashFn}={}){
  const h=unwrap(home),f=unwrap(focus);
  if(h.d.id!==6||f.d.id!==1579||h.d.status!=='publish'||f.d.status!=='publish')
    throw Error('HOLD: unexpected page identity/publication');
  if(h.d.modified!==HOME_DATE||f.d.modified!==FOCUS_DATE)
    throw Error('HOLD: source date changed');
  const digest=(hashFn||((s)=>require('node:crypto').createHash('sha256').update(s,'utf8').digest('hex')))(h.c);
  if(digest!==PIN)throw Error('HOLD: exact homepage SHA mismatch');
  if(!f.c.includes('our email of new investigations and archive finds, sent when we publish them.')||
     !f.c.includes('fvf-gift-v2'))
    throw Error('HOLD: Focus consent or gift-state source changed');
  const before=inventory(h.c);
  if(before.margins!==72||before.focus!==4||before.images!==4||before.jetpack!==1)
    throw Error('HOLD: public homepage preservation inventory drift');
  if(CHAPTERS.some(c=>before.chapters[c]<1||!h.c.includes('id="fv-hf-'+c+'"')))
    throw Error('HOLD: chapter missing');
  if(before.apollo<1||before.franklin<1||before.nypl<1)throw Error('HOLD: exhibit drift');
  let changed=h.c;
  for(const [name,oldText,newText] of REPLACEMENTS){
    if(count(changed,oldText)!==1||changed.includes(newText))
      throw Error('HOLD: missing, duplicate or pre-applied change: '+name);
    changed=changed.replace(oldText,newText);
  }
  let reversed=changed;
  for(const [,oldText,newText] of [...REPLACEMENTS].reverse())
    reversed=reversed.replace(newText,oldText);
  if(reversed!==h.c)throw Error('HOLD: not byte-for-byte reversible');
  const after=inventory(changed);
  for(const key of ['margins','images','scripts','styles','blocks','jetpack','apollo','franklin','nypl'])
    if(after[key]!==before[key])throw Error('HOLD: unexpected preservation delta: '+key);
  if(JSON.stringify(after.chapters)!==JSON.stringify(before.chapters)||after.focus!==before.focus+1)
    throw Error('HOLD: chapter/CTA count changed unexpectedly');
  return {proposed_content:changed,receipt:{
    release:'HOLD',review_only:true,production_write:false,
    source_sha256:digest,source_modified:h.d.modified,focus_modified:f.d.modified,
    operations:REPLACEMENTS.map(p=>p[0]),before,after,
    unresolved:['real WP/Assembler and Jetpack opt-in','Focus gift query-spoof PR #1451 in actual WP',
      'NYPL map #1258 exact-item rights','real media byte transfers','WCAG 2.2 AA/axe',
      'Lighthouse/CWV','independent CI/QD','founder release approval'],
    commercial:'NO VERIFIED LEADS OR SALES; net revenue per qualified 1,000 unknown'
  }};
}
module.exports={assemble,inventory,CHAPTERS,REPLACEMENTS,PIN};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),args=process.argv.slice(2);
  const get=k=>{const i=args.indexOf(k);return i===-1?null:args[i+1]};
  const h=get('--home'),f=get('--focus'),o=get('--out');
  if(!h||!f||!o)throw Error('Provide --home --focus --out for local exports');
  const output=path.resolve(o);
  if([path.resolve(h),path.resolve(f)].includes(output)||fs.existsSync(output)||fs.existsSync(output+'.receipt.json'))
    throw Error('HOLD: output would overwrite existing/source file');
  const result=assemble(JSON.parse(fs.readFileSync(h,'utf8')),JSON.parse(fs.readFileSync(f,'utf8')));
  fs.writeFileSync(output,result.proposed_content,{encoding:'utf8',flag:'wx',mode:0o600});
  fs.writeFileSync(output+'.receipt.json',JSON.stringify(result.receipt,null,2)+'\n',{encoding:'utf8',flag:'wx',mode:0o600});
  process.stdout.write(JSON.stringify({receipt:result.receipt,local_candidate:output})+'\n');
}

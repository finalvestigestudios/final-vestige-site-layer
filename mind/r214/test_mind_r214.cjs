'use strict';
/* FV Mind R214 — zero-dependency source guard. Does NOT test a browser, merchant, or paid order. */
const REQUIRED=[
'the-second-flash-that-never-happened-UNPUBLISHED.md',
'mind-archive-sound-flash-WP-PREVIEW-UNPUBLISHED.html',
'zen12-proof-WARMUP-B-OPTIONAL-FILM-INACTIVE.html',
'r214-42s-concept.vtt',
'offer-claims-and-authorization-matrix.json',
'OFFER-FIRST-CREATOR-FIT-REVENUE-RELEASE-PLAN.md',
'../r213/the-voice-not-in-the-recording-MCGURK-UNPUBLISHED.md',
'../r213/MCGURK-ZEN12-CLAIMS-OFFER-AUTHORIZATION.json',
'../r213/OFFER-FIRST-THREE-CREATOR-FITS-AB-REVENUE-ACCEPTANCE.md',
'../r210/zen12-mindless-reading-A-TEXT-UNPUBLISHED.html',
'../r210/zen12-mindless-reading-B-OPTIONAL-42S-UNPUBLISHED.html'
];
function validate(bundle){
 const e=[];const get=k=>{if(typeof bundle[k]!=='string'){e.push('missing '+k);return '';}return bundle[k];};
 const article=get(REQUIRED[0]),hub=get(REQUIRED[1]),guide=get(REQUIRED[2]),vtt=get(REQUIRED[3]),raw=get(REQUIRED[4]),plan=get(REQUIRED[5]),old=get(REQUIRED[6]),oldMatrix=get(REQUIRED[7]),oldPlan=get(REQUIRED[8]),A=get(REQUIRED[9]),B=get(REQUIRED[10]);
 let matrix;try{matrix=JSON.parse(raw);}catch(_){e.push('invalid JSON');matrix={};}
 const must=(condition,msg)=>{if(!condition)e.push(msg);};
 must(article.split(/\s+/).length>2050,'deep article must exceed 2050 words');
 for(const doi of ['10.1038/35048669','12063138','PMC2905511','24691756','19583464','23978009'])must(article.includes(doi),'missing original article source '+doi);
 must(article.includes('UNPUBLISHED')&&article.includes('no new human-subject experiment')===false,'editorial status/source limits');
 must(article.includes('commercial audio recording')&&article.includes('not a diagnosis'),'science vs seller limits');
 must(!/\baffiliate[_ -]?ref=|utm_campaign=.+offer/i.test(article),'investigation independent of earning');
 for(const [name,h] of [['hub',hub],['guide',guide]]){
  must(!/<script\b|<form\b|<iframe\b|\bautoplay\b\s*=|<video\b|<audio\b|<img[^>]*https?:/i.test(h),name+' no scripts/forms/remote embeds/autoplay');
  must(!/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|affiliates\.inspire3|brainwaveshots)/i.test(h),name+' no merchant hot links');
  must(/<button[^>]*\bdisabled\b/i.test(h),name+' merchant CTA native disabled');
  must(/may earn a commission at no additional cost to you/i.test(h),name+' commission disclosure');
  must(h.indexOf('may earn a commission')<h.indexOf('disabled'),name+' disclosure precedes button');
  must(h.includes('https://finalvestige.com/focus/'),name+' reuses existing Focus');
  must(!/localStorage|document\.cookie|gtag\(|fbq\(|pixel\(|affiliate_click\s*=/i.test(h),name+' does not collect identity/add tracking');
  must(h.includes('@media(max-width:') && h.includes('focus-visible'),name+' static responsive & keyboard evidence');
 }
 must(hub.includes('id="mind214-attention"')&&hub.includes('id="mind214-history"')&&hub.includes('id="mind214-practice"')&&hub.includes('id="mind214-tools"'),'four Mind streams');
 must(guide.includes('<details')&&guide.includes('42-second film concept')&&guide.includes('Transcript'),'optional media transcript');
 must(!guide.includes('<video')&&!/\bautoplay\s*=/.test(guide)&&guide.includes('not rendered'),'media strictly concept only');
 must(vtt.startsWith('WEBVTT')&&vtt.includes('00:00:42.000')&&(vtt.match(/-->/g)||[]).length===5,'caption concept timing & five cues');
 must(matrix.artifact_status!=='LIVE'&&matrix.authorized_outbound===false&&matrix.affiliate_url===null,'matrix authorization hard hold');
 must(matrix.claimed_revenue===null&&matrix.prices_verified_at_checkout===false,'no fake revenue or price');
 must(Array.isArray(matrix.claims)&&matrix.claims.length>=20,'sufficient source claim ledger');
 must(Array.isArray(matrix.gates)&&matrix.gates.filter(g=>g.status==='HOLD'||g.status==='UNKNOWN').length>=10,'unresolved commercial gates');
 const ids=new Set((matrix.source_registry||[]).map(v=>v.id));for(const c of matrix.claims||[])for(const i of c.source_ids||[])must(ids.has(i),'unknown claim source '+c.id+'/'+i);
 must((matrix.source_registry||[]).every(x=>/^https:\/\//.test(x.url)),'all public source links full https');
 must(plan.includes('NOT COMPUTABLE')&&plan.includes('qualified_human_sessions')&&plan.includes('settled_owned_receipts'),'explicit revenue contract');
 must(plan.includes('NO authenticated Grok post')||plan.includes('No social asset ID was authenticated'),'no invented creator IDs');
 must(plan.includes('R197')&&plan.includes('noncanonical'),'duplicate McGurk research held');
 must(old.includes('Violet A. Brown')&&!old.includes('Valerie Brown'),'R213 correct author name');
 must(old.includes('(2022; published December 2)')&&!old.includes('Moving beyond McGurk.” (2023)'),'R213 review 2022');
 must(old.includes('paired with incongruent visible articulation')&&!old.includes('dubbed out of sync'),'phonetic not temporal mismatch');
 must(old.includes('mixed-model estimate')&&old.includes('110 people')&&old.includes('117, with 32'),'2015 distinct response-format analysis');
 must(oldMatrix.includes('2022 JASA review')&&oldMatrix.includes('110, forced-choice N=117'),'R213 evidence date & methods');
 must(!oldPlan.includes("Grok's existing video")&&!oldPlan.includes('Existing factual social entry'),'R213 candidate social not verified');
 must(A.includes('disabled')&&B.includes('disabled')&&A.includes('may earn a commission')&&B.includes('may earn a commission'),'preserved R210 original A/B disabled/disclosed');
 return e;
}
function runMutations(original){
 const mutants=[
 ['activate merchant button',b=>b[REQUIRED[2]]=b[REQUIRED[2]].replace('disabled aria-describedby','aria-describedby')],
 ['delete guide disclosure',b=>b[REQUIRED[2]]=b[REQUIRED[2]].replace(/<p class="disclosure">[^<]+<\/p>/,'')],
 ['merchant hotlink',b=>b[REQUIRED[2]]=b[REQUIRED[2]].replace('<button type="button"', '<a href="https://zen12.com/hnp" rel="sponsored"></a><button type="button"')],
 ['third party script',b=>b[REQUIRED[1]]+='<script src="https://bad.example/track.js"></script>'],
 ['duplicate signup',b=>b[REQUIRED[1]]+='<form><input type="email"></form>'],
 ['delete hub disclosure',b=>b[REQUIRED[1]]=b[REQUIRED[1]].replace(/<p class="disclosure">[^<]+<\/p>/,'')],
 ['replace source',b=>b[REQUIRED[0]]=b[REQUIRED[0]].replace(/10\.1038\/35048669/g,'')],
 ['remove conclusion limit',b=>b[REQUIRED[0]]=b[REQUIRED[0]].replace(/not a diagnosis/g,'')],
 ['falsify account approval',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.authorized_outbound=true;b[REQUIRED[4]]=JSON.stringify(m)}],
 ['fake revenue',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.claimed_revenue=100;b[REQUIRED[4]]=JSON.stringify(m)}],
 ['fake checkout',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.prices_verified_at_checkout=true;b[REQUIRED[4]]=JSON.stringify(m)}],
 ['remove source citation',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.source_registry=[];b[REQUIRED[4]]=JSON.stringify(m)}],
 ['remove VTT',b=>b[REQUIRED[3]]=b[REQUIRED[3]].replace(/-->/g,'')],
 ['invent creator existing post',b=>b[REQUIRED[8]]=b[REQUIRED[8]].replace('Candidate creator topic about an unnoticed scene change (NO authenticated Grok post or asset ID yet)',"Grok's existing video about an unnoticed scene change")],
 ['old author wrong',b=>b[REQUIRED[6]]=b[REQUIRED[6]].replace('Violet A. Brown','Valerie Brown')],
 ['old year wrong',b=>b[REQUIRED[7]]=b[REQUIRED[7]].replace('2022 JASA review','2023 JASA review')]
 ];
 const results=[];for(const [label,mutate] of mutants){const bundle={...original};mutate(bundle);const violations=validate(bundle);results.push({label,rejected:violations.length>0,violations:violations.slice(0,2)})}return results;
}
module.exports={REQUIRED,validate,runMutations};
if(typeof require!=='undefined' && typeof __dirname!=='undefined' && require.main===module){
 const fs=require('fs'),path=require('path');const b={};for(const n of REQUIRED)b[n]=fs.readFileSync(path.join(__dirname,n),'utf8');const failures=validate(b),mutants=runMutations(b);const missed=mutants.filter(m=>!m.rejected);console.log(JSON.stringify({baseline_violations:failures,mutants_total:mutants.length,mutants_rejected:mutants.length-missed.length,missed},null,2));if(failures.length||missed.length)process.exit(1);
}

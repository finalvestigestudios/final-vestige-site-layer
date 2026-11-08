'use strict';
/* FV Mind R215 exact-source, zero-dependency test. Validates local files and real unsafe mutations.
 * NOT a web browser, WP sanitizer, merchant checkout, affiliate approval or financial verification. */
const REQUIRED=[
 'the-rhythm-that-isnt-in-either-ear-UNPUBLISHED.md',
 'mind-archive-audio-evidence-WP-PREVIEW-UNPUBLISHED.html',
 'zen12-proof-first-purchase-guide-INACTIVE.html',
 'zen12-42s-research-film-concept.vtt',
 'binaural-merchant-claim-source-matrix.json',
 'OFFER-FIRST-PAID-REVENUE-AND-CREATOR-FIT-ACCEPTANCE.md',
 '../r214/the-second-flash-that-never-happened-UNPUBLISHED.md',
 '../r214/zen12-proof-WARMUP-B-OPTIONAL-FILM-INACTIVE.html',
 '../r214/test_mind_r214.cjs',
 '../r210/zen12-mindless-reading-A-TEXT-UNPUBLISHED.html',
 '../r210/zen12-mindless-reading-B-OPTIONAL-42S-UNPUBLISHED.html'
];
function validate(bundle){
 const e=[],read=i=>{const v=bundle[REQUIRED[i]];if(typeof v!=='string'){e.push('missing '+REQUIRED[i]);return '';}return v;};
 const article=read(0),hub=read(1),guide=read(2),vtt=read(3),raw=read(4),plan=read(5),
       oldArticle=read(6),oldGuide=read(7),oldTest=read(8),A=read(9),B=read(10);
 const must=(condition,label)=>{if(!condition)e.push(label)};
 let m={};try{m=JSON.parse(raw)}catch(err){e.push('matrix invalid JSON')}
 must(article.split(/\s+/).length>=2200,'substantive original manuscript length');
 must(article.includes('UNPUBLISHED')&&article.includes('WITHHELD'),'article never supplies public live destination');
 for(const s of ['10.1371/journal.pone.0286023','10.1038/s41598-025-88517-z','zen12.com/hnp','14 eligible','one mixed'])must(article.includes(s),'scientific manuscript evidence missing '+s);
 must(article.includes('did **not** prevent performance from declining'),'2025 vigilance decrement caveat');
 must(article.includes('not a randomized or blinded experiment')||article.includes('not a blinded trial'),'free task caveat');
 must(!/affiliate[_ -]?ref=|affiliate_link=|tracking_id=/i.test(article),'article may not embed sale tracking');
 const merchant=/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i;
 for(const [kind,h] of [['hub',hub],['guide',guide]]){
  must(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b|\bautoplay\s*=|<img\b[^>]*src\s*=\s*["']https?:/i.test(h),kind+' must have no scripts/forms/media players/remote embed');
  must(!merchant.test(h),kind+' no active merchant link');
  must((h.match(/<button[^>]*\bdisabled\b/g)||[]).length===1,kind+' exactly one natively disabled commercial CTA');
  must(h.includes('may earn a commission at no additional cost to you'),kind+' clear commission disclosure');
  must(/<p class="disclosure">[\s\S]{0,350}<\/p>\s*<p>\s*<button[^>]*\bdisabled\b/i.test(h),kind+' disclosure immediately adjacent to unavailable CTA');
  must(h.includes('https://finalvestige.com/focus/'),kind+' existing only Focus path');
  must(!/localStorage|document\.cookie|gtag\(|fbq\(|pixel\(|<input\b|type=["']email/i.test(h),kind+' no identity tracking or duplicate email list');
  must(h.includes('@media(max-width:')&&h.includes('focus-visible')&&h.includes('prefers-reduced-motion'),kind+' responsive/keyboard/reduced-motion source safeguards');
  must(h.includes('<svg')&&h.includes('role="img"')&&h.includes('<desc'),kind+' original SVG descriptive equivalent');
  must(/UNPUBLISHED/i.test(h),kind+' explicit draft-only status');
 }
 for(const id of ['mind215-perception','mind215-history','mind215-practice','mind215-tools'])must(hub.includes('id="'+id+'"'),'Mind hub four-stream '+id);
 must(!/href=["'](?:\/mind\/|https?:\/\/finalvestige\.com\/mind\/)/i.test(hub),'do not invent live mind slug');
 must(guide.includes('NOT an A/B')||guide.includes('not either arm'),'R215 copy review not invalid A/B cross comparison');
 must(guide.includes('Transcript')&&guide.includes('<details'),'optional original concept and transcript');
 must(guide.includes('not rendered')||guide.includes('NOT been rendered'),'no claimed rendered video');
 const cues=vtt.match(/\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}/g)||[];
 must(vtt.startsWith('WEBVTT')&&cues.length===5&&cues[0].startsWith('00:00:00.000')&&cues[4].endsWith('00:00:42.000'),'five cue 42s caption concept');
 if(cues.length===5){for(let i=1;i<5;i++)must(cues[i-1].split(' --> ')[1]===cues[i].split(' --> ')[0],'caption contiguous boundaries cue '+i)}
 must(m.status==='UNPUBLISHED_SOURCE_ONLY'&&m.artifact_status==='UNPUBLISHED_SOURCE_ONLY','exact unpublished source-only state');
 must(m.authorized_outbound===false&&m.affiliate_url===null&&m.publisher_acceptance_verified===false,'no invented merchant acceptance / link');
 must(m.prices_verified_at_checkout===false&&m.claimed_revenue===null&&m.verified_paid_orders===null&&m.revenue_per_1000_qualified_human_sessions===null,'no invented checkout or paid revenue');
 must(m.direct_identity_tracking===false&&m.new_tracking_scripts===false&&m.duplicate_focus_form===false,'privacy / one existing signup');
 must(m.frozen_ab==='R210_TEXT_ONLY_VS_OPTIONAL_UNRENDERED_42S','frozen two-arm true video-only comparison');
 must(Array.isArray(m.source_registry)&&m.source_registry.length>=25,'source registry coverage');
 must(Array.isArray(m.claims)&&m.claims.length>=32,'source claim coverage');
 const ids=new Set((m.source_registry||[]).map(s=>s.id));
 for(const c of m.claims||[])for(const id of c.source_ids||[])must(ids.has(id),'dangling claim '+c.id+' source '+id);
 must((m.source_registry||[]).every(s=>/^https:\/\//.test(s.url)),'source URLs fully qualified');
 const g=new Map((m.gates||[]).map(x=>[x.id,x]));
 must(Array.isArray(m.gates)&&g.size===m.gates.length,'unique gate IDs');
 for(const id of ['G01','G02','G03','G04','G05','G06','G07','G08','G09','G18'])must(g.has(id)&&g.get(id).status==='HOLD','required founder/partner hard hold '+id);
 for(const id of ['G10','G14','G15','G16','G17'])must(g.has(id)&&['HOLD','UNKNOWN'].includes(g.get(id).status),'required unknown commercial gate '+id);
 for(const s of ['qualified_human_sessions','settled_owned_receipts','NOT COMPUTABLE','R210','Grok','Praxxis','HARD HOLD','merchant_confirmed_purchase','refunds'])must(plan.includes(s),'conversion/attribution protocol '+s);
 must(plan.includes('no verified')||plan.includes('not authenticated')||plan.includes('not an eligible'),'no assumed affiliate acceptance');
 must(oldArticle.includes('Kumpik, Roberts, King & Bizley')&&oldArticle.includes('was behavioral')&&oldArticle.includes('Original article metadata and abstract'),'R214 inherited accurate evidence correction');
 must(oldGuide.includes('NOT an A/B treatment paired with R210 A'),'R214 cross-arm confound removed');
 must(oldTest.includes("matrix.status==='UNPUBLISHED_SOURCE_ONLY'")&&oldTest.includes('required unresolved release gate')&&oldTest.includes('delete founder gate G18'),'R214 hardened exact release and gate mutation checks');
 must(A.includes('disabled')&&B.includes('disabled')&&A.includes('may earn a commission')&&B.includes('may earn a commission'),'R210 frozen A/B inactive');
 return e;
}
function runMutations(original){
 const mutations=[
  ['activate paid CTA',b=>b[REQUIRED[2]]=b[REQUIRED[2]].replace(/<button type="button" disabled/,'<button type="button"')],
  ['remove near CTA disclosure',b=>b[REQUIRED[2]]=b[REQUIRED[2]].replace(/<p class="disclosure">[^<]*<\/p>/,'')],
  ['merchant hotlink',b=>b[REQUIRED[2]]+='<a href="https://zen12.com/hnp">shop</a>'],
  ['new signup',b=>b[REQUIRED[1]]+='<form><input type="email"></form>'],
  ['third party analytics',b=>b[REQUIRED[1]]+='<script src="https://tracker.example/file.js"></script>'],
  ['remove scientific trial',b=>b[REQUIRED[0]]=b[REQUIRED[0]].replace(/10\.1038\/s41598-025-88517-z/g,'')],
  ['remove disputed entrainment review',b=>b[REQUIRED[0]]=b[REQUIRED[0]].replace(/10\.1371\/journal\.pone\.0286023/g,'')],
  ['remove five-caption timing',b=>b[REQUIRED[3]]=b[REQUIRED[3]].replace('00:00:42.000','00:00:41.000')],
  ['pretend publicly live',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.status='LIVE';b[REQUIRED[4]]=JSON.stringify(m)}],
  ['activate affiliate',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.authorized_outbound=true;b[REQUIRED[4]]=JSON.stringify(m)}],
  ['claim named approval',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.publisher_acceptance_verified=true;b[REQUIRED[4]]=JSON.stringify(m)}],
  ['invent revenue',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.claimed_revenue=500;b[REQUIRED[4]]=JSON.stringify(m)}],
  ['invent paid orders',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.verified_paid_orders=9;b[REQUIRED[4]]=JSON.stringify(m)}],
  ['leak tracking identity',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.direct_identity_tracking=true;b[REQUIRED[4]]=JSON.stringify(m)}],
  ['delete founder approval gate',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.gates=m.gates.filter(g=>g.id!=='G18');b[REQUIRED[4]]=JSON.stringify(m)}],
  ['falsify founder release',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.gates.find(g=>g.id==='G18').status='PASS';b[REQUIRED[4]]=JSON.stringify(m)}],
  ['falsify merchant rights',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.gates.find(g=>g.id==='G02').status='PASS';b[REQUIRED[4]]=JSON.stringify(m)}],
  ['destroy independent sources',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.source_registry=[];b[REQUIRED[4]]=JSON.stringify(m)}],
  ['invent third A/B arm',b=>{const m=JSON.parse(b[REQUIRED[4]]);m.frozen_ab='R215_B_VS_R210_A';b[REQUIRED[4]]=JSON.stringify(m)}],
  ['remove paid acceptance requirement',b=>b[REQUIRED[5]]=b[REQUIRED[5]].replace(/NOT COMPUTABLE/g,'immediate profit')],
  ['regress R214 source credit',b=>b[REQUIRED[6]]=b[REQUIRED[6]].replace('Kumpik, Roberts, King & Bizley','unknown authors')],
  ['regress R214 status guard',b=>b[REQUIRED[8]]=b[REQUIRED[8]].replace("matrix.status==='UNPUBLISHED_SOURCE_ONLY'","matrix.status!=='LIVE'")]
 ];
 const out=[];
 for(const [label,mutate] of mutations){
  const b={...original};mutate(b);
  const didChange=REQUIRED.some(k=>b[k]!==original[k]);
  const failures=validate(b);out.push({label,didChange,rejected:didChange&&failures.length>0,violations:failures.slice(0,2)});
 }
 return out;
}
module.exports={REQUIRED,validate,runMutations};
if(typeof require!=='undefined'&&typeof __dirname!=='undefined'&&require.main===module){
 const fs=require('fs'),path=require('path'),b={};
 for(const rel of REQUIRED)b[rel]=fs.readFileSync(path.join(__dirname,rel),'utf8');
 const baseline_violations=validate(b),mutants=runMutations(b),missed=mutants.filter(x=>!x.rejected);
 console.log(JSON.stringify({baseline_violations,mutants_total:mutants.length,mutants_rejected:mutants.length-missed.length,missed},null,2));
 if(baseline_violations.length||missed.length)process.exitCode=1;
}
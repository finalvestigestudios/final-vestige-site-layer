'use strict';
// Dependency-free source contract. No network, CMS, deployment or personal-data access.
// Run in a checked-out repository: node mind/stroop-conflict-r13/qa.cjs
// Import audit(files) to inspect exact GitHub readbacks without a checkout.
function audit(files) {
  const out = [];
  const check = (name, yes) => out.push({name, pass: Boolean(yes)});
  const a=files['ARTICLE.md']||'', h=files['wordpress-draft.html']||'',
    p=files['OFFER_EXPERIMENT_AND_NAV.md']||'', v=files['SHORT_VIDEO_CONCEPT.md']||'',
    m=files['claim-source-matrix.json']||'', readme=files['README.md']||'';
  let j={claims:[],source_registry:{},permission_status:{}};
  try {j=JSON.parse(m);check('claim ledger parse',true);} catch {check('claim ledger parse',false);}
  check('article substantial >= 2400 tokens',a.trim().split(/\s+/).length>=2400);
  check('article cites original experiment',a.includes('10.1037/h0054651'));
  check('article includes 1935 date',a.includes('1935'));
  check('article reports 47 sec with context',a.includes('47.0 seconds')&&a.includes('100 items'));
  check('article reports 74.3% with context',a.includes('74.3 percent'));
  check('article reports nonsignificant reading effect',a.includes('2.3 seconds')&&a.includes('not regard that increase as reliable'));
  check('article discusses ambiguity between processes',a.includes('phonological')&&a.includes('response'));
  check('article has two meditation literature appraisals',a.includes('2021')&&a.includes('2024')&&a.includes('111'));
  check('article does not imply Zen12 trial',a.includes('not evidence that listening produces')&&a.includes('nor general meditation meta-analyses independently validate'));
  check('article provides free practice',a.includes('five minutes')&&a.includes('without buying'));
  check('article respects accessible alternative',a.includes('screen reader')&&a.includes('conceptual explanation'));
  check('article separates history from hypothesis',a.includes('Puységur')&&a.includes('not present it as a descendant'));
  check('published original Focus route',a.includes('https://finalvestige.com/focus/'));
  check('article source trail present',a.includes('## Source trail and verification notes'));
  check('article no testimonial',!/(we tried Zen12|I used Zen12|our users say)/i.test(a));
  check('article no unsubstantiated promotional superlatives',!/(Zen12 has been clinically proven|Zen12 guarantees|proven to improve your Stroop)/i.test(a));
  check('HTML at least 25000 chars',h.length>=25000);
  check('one h1',((h.match(/<h1\b/g)||[]).length===1));
  check('one article root',((h.match(/<article\b/g)||[]).length===1)&&((h.match(/<\/article>/g)||[]).length===1));
  check('no nested main landmark',!/<main\b/i.test(h));
  check('no script',!/<script\b/i.test(h));
  check('no subscription or form',!/<form\b/i.test(h)&&!/wp-block-jetpack-subscriptions/.test(h));
  check('no third-party media',!/<(?:iframe|audio|video|img)\b/i.test(h));
  check('no active merchant links',!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(h));
  check('no javascript or data URLs',!/(?:href|src)\s*=\s*["']\s*(?:javascript|data):/i.test(h));
  check('no autoplay',!/<video[^>]*\bautoplay\b/i.test(h));
  check('clear near-CTA disclosure',h.includes('class="fv-str__affiliate"')&&h.includes('may earn a commission')&&h.includes('currently no approved affiliate link'));
  check('inactive product CTA',h.includes('Purchase link unavailable')&&!h.includes('See Zen12&#'));
  check('free Focus link works in markup',h.includes('href="https://finalvestige.com/focus/"'));
  check('published Puységur link works in markup',h.includes('href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"'));
  check('original no-JS visual example',h.includes('fv-str__demoGrid')&&h.includes('NO TIMER OR SCORE'));
  check('accessible description/reveal',h.includes('<details class="fv-str__reveal">')&&h.includes('Screen-reader users'));
  check('responsive mobile layout',h.includes('@media(max-width:700px)')&&h.includes('grid-template-columns:1fr'));
  check('keyboard focus',h.includes(':focus-visible'));
  check('reduced motion',h.includes('prefers-reduced-motion'));
  check('high contrast mode',h.includes('forced-colors:active'));
  check('print mode',h.includes('@media print'));
  check('scoped CSS',h.includes('.fv-stroop')&&!h.includes('body:has('));
  check('source trail has all fifteen linkable targets',Array.from({length:15},(_,k)=>k+1).every(n=>h.includes('id="fv-str-source-'+n+'"')));
  check('all citation fragments resolve',Array.from(h.matchAll(/href="#(fv-str-source-\d+)"/g)).every(m=>h.includes('id="'+m[1]+'"')));
  check('research source links external rel safe',!/<a href="https?:\/\/(?:doi\.org|pubmed\.ncbi\.nlm\.nih\.gov|www\.ftc\.gov|www\.mpi\.nl)[^"]*"(?![^>]*rel="noopener noreferrer")/i.test(h));
  check('no HTML product checkout link',!/<a[^>]*https:\/\/zen12\.com\/getstarted/.test(h));
  check('ledger contains >=50 distinct claims',j.claims.length>=50&&new Set(j.claims.map(x=>x.id)).size===j.claims.length);
  check('ledger contains >=15 sources',Object.keys(j.source_registry).length>=15);
  check('all ledger source refs resolve',j.claims.every(x=>Array.isArray(x.sources)&&x.sources.length>0&&x.sources.every(s=>j.source_registry[s])));
  check('every claim has disposition and public copy rule',j.claims.every(x=>x.disposition&&x.public_copy_rule));
  check('product efficacy not described as verified',j.claims.filter(x=>x.id==='Z06'||x.id==='Z07'||x.id==='M07').every(x=>x.disposition==='unsupported'||x.disposition==='rejected'));
  check('account authorization fail-closed',j.permission_status.inspire3_partner_approved===false);
  check('affiliate URL null',j.permission_status.approved_affiliate_url===null);
  check('email promotion rights null',j.permission_status.email_promotion_rights===null);
  check('creative rights null',j.permission_status.creative_rights===null);
  check('commission terms null',j.permission_status.commission_terms===null);
  check('plan includes official merchant URLs',p.includes('https://zen12.com/about')&&p.includes('https://zen12.com/getstarted'));
  check('plan warns merchant free newsletter is separate',p.includes('seller newsletter')&&p.includes('Jetpack'));
  check('plan has proper near CTA disclosure',p.includes('may earn a commission at no additional cost'));
  check('plan no optional commercial link active',p.includes('Product link currently withheld'));
  check('plan has two independent variants',p.includes('Control (A)')&&p.includes('Variant (B)'));
  check('plan video manual poster captions transcript',p.includes('preload="none"')&&p.includes('kind="captions"')&&p.includes('full transcript'));
  check('plan privacy default off',p.includes('mind_measurement_enabled=false')&&p.includes('outbound_affiliate_enabled=false'));
  check('plan refuses PII/traffic identifiers',p.includes('Do not accept IP, email, exact referrer URL'));
  check('plan honors privacy signals',p.includes('Global Privacy Control')&&p.includes('Do Not Track'));
  check('plan no sales inferred from clicks',p.includes('never inferred from an outbound click'));
  check('plan keeps current Focus/Dispatch',p.includes('single Jetpack Dispatch')&&p.toLowerCase().includes('do not create a new'));
  check('plan does not promote unpublished URLs as live',p.includes('must NOT be called live URLs'));
  check('film storyboard honestly not rendered',v.includes('PRODUCTION CONCEPT ONLY')&&v.includes('NOT an exported video'));
  check('film 42sec source note',v.includes('36–42')&&v.includes('10.1037/h0054651'));
  check('film no reused merchant creative',v.includes('No Stroop experiment card reproduction')&&v.includes('seller logo'));
  check('README release hold and ownership',readme.includes('HOLD')&&readme.includes('#171')&&readme.includes('#49'));
  function luminance(hex){const vals=hex.replace('#','').match(/../g).map(x=>parseInt(x,16)/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);return .2126*vals[0]+.7152*vals[1]+.0722*vals[2];}
  function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
  for(const [name,fg,bg] of [['body','#D8D2C7','#090A0A'],['muted','#BDB5AA','#090A0A'],['red','#F6B4B4','#090A0A'],['blue','#98C8E6','#090A0A'],['yellow','#F4D792','#090A0A'],['green','#ABE0B9','#090A0A'],['gold','#C7A66C','#090A0A']]) check('calculated WCAG contrast '+name,contrast(fg,bg)>=4.5);
  return {pass:out.every(x=>x.pass),passed:out.filter(x=>x.pass).length,total:out.length,checks:out,failures:out.filter(x=>!x.pass)};
}
module.exports={audit};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('fs'),path=require('path'),dir=__dirname;
 const files={};
 for(const n of ['ARTICLE.md','wordpress-draft.html','claim-source-matrix.json','OFFER_EXPERIMENT_AND_NAV.md','SHORT_VIDEO_CONCEPT.md','README.md']) files[n]=fs.readFileSync(path.join(dir,n),'utf8');
 const r=audit(files);for(const t of r.checks)console.log((t.pass?'PASS ':'FAIL ')+t.name);
 console.log(r.passed+'/'+r.total+' PASS');if(!r.pass)process.exitCode=1;
}

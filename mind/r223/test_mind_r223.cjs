/* FV Mind R223 — source-only regression. Run from repo root:
   node mind/r223/test_mind_r223.cjs
   No network, no package install. Does NOT test browser, WordPress, merchant, media playback or sales.
*/
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const dir = path.join(__dirname);
const read = file => fs.readFileSync(path.join(dir,file),'utf8');
const a = read('zen12-R223-A-TEXT-UNPUBLISHED.html');
const b = read('zen12-R223-B-OPTIONAL-42S-UNRENDERED.html');
const hub = read('mind-archive-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html');
const art = read('the-pendulum-that-answered-IDEOMOTOR-UNPUBLISHED.md');
const vtt = read('zen12-42s-SCRIPT-LOCK.vtt');
const matrix = JSON.parse(read('SOURCE-CLAIM-COMMERCE-GATES.json'));
const plan = read('CREATOR-FIT-OFFER-REVENUE-AB-ACCEPTANCE.md');
const expected = ['account_acceptance','permission_social','permission_email','issued_earning_url','affiliate_tracking_terms','merchant_checkout_final','merchant_refund_conditions','merchant_creative_rights','claim_substantiation','affiliate_disclosure_rendered','video_render_and_captions','browser_a11y_performance','site_qa_and_founder_release','published_guide','independent_paid_conversion','qualified_human_denominator'];
function validate(doc) {
  const errors=[];
  const files=[doc.a,doc.b,doc.hub];
  for (let i=0;i<files.length;i++) {
    const html=files[i]; const label=['A','B','hub'][i];
    if (/<\s*(?:script|form|iframe)\b/i.test(html)) errors.push(label+':script-form-iframe');
    if (/\son[a-z]+\s*=/i.test(html)) errors.push(label+':inline-event-handler');
    if (/href\s*=\s*['"]?\s*(?:https?:\/\/)?(?:[^\s'">]*\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|awin1\.com|clickbank\.com)/i.test(html)) errors.push(label+':merchant-href');
    if (/https?:\/\/[^\s"']*(?:awin1\.com|clickbank\.com)|(?:data-)?(?:affiliate|tracking)-id\s*=/i.test(html)) errors.push(label+':earning-or-tracking-token');
    if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/.test(html)) errors.push(label+':noindex');
    if (!/a:focus-visible|a:focus-visible,button:focus-visible/.test(html)) errors.push(label+':keyboard');
    const buttons=[...html.matchAll(/<button\b[^>]*>/gi)].map(m=>m[0]);
    if (buttons.length!==1) errors.push(label+':button-count');
    for(const btn of buttons) {
      if(!/\sdisabled(?:\s|>|=)/i.test(btn)) errors.push(label+':enabled-button');
      if(!/aria-disabled="true"/i.test(btn)) errors.push(label+':aria-disabled');
      if(/\s(on\w+|formaction|href|data-url)\s*=/i.test(btn)) errors.push(label+':activated-button-attr');
    }
    const p=html.toLowerCase().indexOf('affiliate disclosure:');
    if(p<0) errors.push(label+':missing-disclosure');
    else if(buttons.length && !html.slice(p,p+650).includes(buttons[0])) errors.push(label+':disclosure-not-adjacent');
    if(/<input\b|autocomplete\s*=|localStorage|sessionStorage|gtag\s*\(/i.test(html))errors.push(label+':email-or-tracking');
    if(!/prefers-reduced-motion:reduce/.test(html))errors.push(label+':reduced-motion');
    if(/<svg\b/.test(html) && !/<svg\b[^>]*role="img"[^>]*aria-labelledby=/.test(html))errors.push(label+':image-description');
  }
  if(!/UNRENDERED|video not rendered/i.test(doc.b))errors.push('B:film-status');
  if(/<video\b|<[^>]+\sautoplay(?:\s|>|=)/i.test(doc.b))errors.push('B:unapproved-media-player');
  const details=doc.b.match(/<details class="film"[\s\S]*?<\/details>/);
  if(!details)errors.push('B:optional-film-missing');
  else {
    const normalized = h=>h.replace(/OPTIONAL 42S B|TEXT A/g,'VARIANT')
      .replace(/<details class="film"[\s\S]*?<\/details>/,'');
    if(normalized(doc.b)!==normalized(doc.a))errors.push('AB:copy-differs-outside-film');
    const cues=[...doc.vtt.matchAll(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}\s*\n([^\n]+)/g)].map(x=>x[1].trim());
    const narrated=[...details[0].matchAll(/<li><strong>[^<]+<\/strong>\s*([^<]+)<\/li>/g)].map(x=>x[1].trim());
    if(cues.length!==5||narrated.length!==5||cues.some((v,i)=>v!==narrated[i]))errors.push('B:caption-transcript-mismatch');
    if(!/00:00:35.000 --> 00:00:42.000/.test(doc.vtt))errors.push('B:duration-not-42');
  }
  const gates=doc.matrix.gates||[];
  if(gates.length!==expected.length)errors.push('gates:count');
  for(const id of expected){
    const matches=gates.filter(g=>g.id===id);
    if(matches.length!==1)errors.push('gates:'+id+':missing-or-duplicate');
    else if(matches[0].status!=='HARD_HOLD')errors.push('gates:'+id+':status');
  }
  if(doc.matrix.release!=='UNPUBLISHED_HARD_HOLD')errors.push('gates:release');
  if((doc.matrix.claims||[]).length<20)errors.push('claims:missing');
  if(!/176 responses/.test(doc.art)||!/40 American volunteers|Forty American volunteers/.test(doc.art))errors.push('research:sample-method');
  if(!/unpublished/i.test(doc.art))errors.push('research:status');
  if(!/merchant-confirmed|merchant_confirmed_order/.test(doc.plan))errors.push('measurement:paid-order');
  if(!/NOT COMPUTABLE/.test(doc.plan))errors.push('measurement:ratio-unknown');
  if(!/SV9m07PFTYk/.test(doc.plan))errors.push('grok:verified-public-video');
  return errors;
}
const pristine={a,b,hub,art,vtt,matrix,plan};
const baseline=validate(pristine);
const mutate=(label,change)=>({label,errors:validate(change({...pristine,matrix:JSON.parse(JSON.stringify(matrix))}))});
const cases=[
  mutate('activate A button',d=>({...d,a:d.a.replace(' type="button" disabled',' type="button"')})),
  mutate('activate B button',d=>({...d,b:d.b.replace(' type="button" disabled',' type="button"')})),
  mutate('add second enabled purchasing button',d=>({...d,a:d.a.replace('</main>','<button>Buy</button></main>')})),
  mutate('unquoted merchant href',d=>({...d,hub:d.hub.replace('</section>','<a href=https://zen12.com/hnp>Buy</a></section>')})),
  mutate('https earning link',d=>({...d,a:d.a.replace('</main>','<a href=https://www.awin1.com/click>Buy</a></main>')})),
  mutate('onfocus inline',d=>({...d,hub:d.hub.replace('href="https://finalvestige.com/focus/"','onfocus=alert(1) href="https://finalvestige.com/focus/"')})),
  mutate('script tag',d=>({...d,b:d.b.replace('</body>','<script src="https://tracker.example"></script></body>')})),
  mutate('extra form',d=>({...d,hub:d.hub.replace('</section>','<form><input type=email></form></section>')})),
  mutate('disclosure deletion',d=>({...d,b:d.b.replace('Affiliate disclosure:','Notice omitted:')})),
  mutate('missing gate',d=>{d.matrix.gates=d.matrix.gates.slice(1);return d}),
  mutate('duplicate gate',d=>{d.matrix.gates.push({...d.matrix.gates[0]});return d}),
  mutate('alter last gate',d=>{d.matrix.gates.at(-1).status='APPROVED';return d}),
  mutate('fabricate release',d=>{d.matrix.release='LIVE';return d}),
  mutate('remove claim records',d=>{d.matrix.claims=[];return d}),
  mutate('change film copy',d=>({...d,b:d.b.replace('The hardest part of a short meditation routine','The best shortcut to limitless attention')})),
  mutate('alter VTT cue',d=>({...d,vtt:d.vtt.replace('forty-eight recordings','forty-eight proven treatments')})),
  mutate('shorten VTT',d=>({...d,vtt:d.vtt.replace('00:00:42.000','00:00:40.000')})),
  mutate('fabricate media render',d=>({...d,b:d.b.replace('video not rendered','movie completed').replace('UNRENDERED','RENDERED')})),
  mutate('delete 176 response evidence',d=>({...d,art:d.art.replaceAll('176 responses','many responses')})),
  mutate('delete revenue gap',d=>({...d,plan:d.plan.replaceAll('NOT COMPUTABLE','N/A')})),
  mutate('remove known public video',d=>({...d,plan:d.plan.replace('SV9m07PFTYk','UNKNOWN')})),
  mutate('remove keyboard style',d=>({...d,hub:d.hub.replace('#fv-mind a:focus-visible,#fv-mind button:focus-visible','#fv-mind .unused')})),
  mutate('enable third CTA href',d=>({...d,a:d.a.replace('</article>','<a href=https://hypnosislive.com/mental-skills/total-focus>Buy</a></article>')})),
  mutate('insert data tracking id',d=>({...d,b:d.b.replace('</body>','<div affiliate-id="fake"></div></body>')}))
];
const rejected=cases.filter(c=>c.errors.length>0);
process.stdout.write(JSON.stringify({baseline,mutation_count:cases.length,rejected:rejected.length,escaped:cases.filter(c=>!c.errors.length).map(c=>c.label)},null,2)+'\n');
if(baseline.length||rejected.length!==cases.length)process.exit(1);

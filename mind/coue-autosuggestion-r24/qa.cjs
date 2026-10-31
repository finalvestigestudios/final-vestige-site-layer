'use strict';
const fs=require('node:fs'),p=require('node:path');const read=x=>fs.readFileSync(p.join(__dirname,x),'utf8');
const a=read('zen12-a.html'),b=read('zen12-b.html'),article=read('investigation.html'),hub=read('hub-alt.html'),poster=read('poster.svg'),csv=read('claims.csv');
let n=0;function check(x,label){if(!x)throw Error('FAIL '+label);n++}
const stripped=b.replace(/<!-- FV_R24_FILM_BEGIN -->[\s\S]*?<!-- FV_R24_FILM_END -->/,'');
check(stripped.replace('data-fv-draft="zen12-b"','data-fv-draft="zen12-a"')===a,'A/B guide editorial parity');
for(const [label,html] of [['A',a],['B',b]]){
 check(html.includes('Final Vestige may earn a commission'),label+' disclosure');
 check(/<button type="button" disabled/.test(html),label+' CTA disabled');
 check(!/<script\b|<iframe\b|<video\b|<button[^>]*onclick/i.test(html),label+' no active player/tracker');
 check(html.includes('zen12.com/about')&&html.includes('zen12.com/getstarted'),label+' exact merchant');
 check(html.includes('seller claims, not Final Vestige conclusions'),label+' science limit');
 check(html.includes('Seven Day Focus Fieldbook'),label+' single funnel');
 check(!/hop\.clickbank|[?&]affid=/.test(html),label+' no earning URL');
}
check(article.includes('Coué')&&article.includes('1922'),'period source');
check(article.includes('sleeping child'),'consent history');
check(!article.includes('<button'),'investigation separate from commerce');
check(hub.includes('PR #172'),'hub preservation');
check(poster.includes('<title')&&poster.includes('<desc'),'accessible poster');
check(!/<script\b|foreignObject|onload=/.test(poster),'safe poster');
check(csv.trim().split('\n').length>=45,'source matrix present');
check(csv.includes('UNKNOWN_HARD_HOLD'),'hard commerce gate');
console.log(n+' source-level checks passed; no WordPress/browser/hosted CI implied');
'use strict';
/* R120 source contract / adversarial mutations. Browser qualification is qa_r113_print.py. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const patterns={
  'hidden until JS progressive enhancement': /<button\b[^>]*data-fv-print-student\s+hidden\b[^>]*>Print the student worksheet only<\/button>/,
  'semantic button': /<button\b[^>]*type="button"[^>]*data-fv-print-student/,
  'source packet only suppressed in opt-in print mode': /body\.fv-worksheet-only\s+#main>:not\(#classroom-preview\)/,
  'teacher content suppressed only in opt-in print mode': /body\.fv-worksheet-only\s+#classroom-preview>:not\(\[data-fv-student-print\]\)/,
  'opt-in rules are print-only': /@media print\{[\s\S]*?body\.fv-worksheet-only/,
  'standalone rights notice is print-visible': /body\.fv-worksheet-only\s+\.worksheet-standalone-rights\{display:block!important/,
  'zero individually cleared images': /individually uncleared for reproduction \(0\/6\)/,
  'provisional photo identity retained': /proposed S67-19766 portrait identity is provisional/,
  'not NASA endorsed': /This independent worksheet is not NASA-endorsed/,
  'NASA primary source on student sheet': /https:\/\/www\.nasa\.gov\/missions\/apollo\/apollo-1\/report-of-the-apollo-204-review-board\//,
  'print feature guarded for no-JS/error': /if\(!button\|\|!sheet\|\|typeof window\.print!=='function'\)return/,
  'explicit action not automatic printing': /button\.addEventListener\('click',function\(\)\{/,
  'afterprint restores full site': /window\.addEventListener\('afterprint',function\(\)\{[\s\S]*?classList\.remove\('fv-worksheet-only'\)/,
  'regular print still includes all four findings': /\.plate\[hidden\]\{display:block!important\}/,
  'ordinary full packet source custody retained': /class="print-custody"/,
  'no extra primary marketing CTA': /data-fv-primary-cta/,
};
function errors(source){
  const failures=Object.entries(patterns).filter(([,regex])=>!regex.test(source)).map(([name])=>name);
  if((source.match(/data-fv-print-student hidden/g)||[]).length!==1)failures.push('duplicate or missing print action');
  if((source.match(/data-fv-primary-cta/g)||[]).length!==1)failures.push('non-single main action');
  if(/<form\b|href="[^"]*payhip|<iframe\b/i.test(source))failures.push('unapproved commerce/form/embed');
  return failures;
}
assert.deepEqual(errors(html),[],'R120 actual-source contract failed');
const mutations=[
  ['remove print button',s=>s.replace('data-fv-print-student hidden','data-fv-print-student')],
  ['fail to isolate packet',s=>s.replace('body.fv-worksheet-only #main>:not(#classroom-preview)','body #main>:not(#classroom-preview)')],
  ['leak teacher answer',s=>s.replace('body.fv-worksheet-only #classroom-preview>:not([data-fv-student-print])','body #classroom-preview>:not([data-fv-student-print])')],
  ['hide custody notice',s=>s.replace('body.fv-worksheet-only .worksheet-standalone-rights{display:block!important','body.fv-worksheet-only .worksheet-standalone-rights{display:none!important')],
  ['invent reuse clearance',s=>s.replace('individually uncleared for reproduction (0/6)','approved for reproduction (6/6)')],
  ['overclaim portrait',s=>s.replace('proposed S67-19766 portrait identity is provisional','S67-19766 portrait identity is confirmed')],
  ['invent endorsement',s=>s.replace('not NASA-endorsed','NASA-endorsed')],
  ['disable afterprint cleanup',s=>s.replace("window.addEventListener('afterprint'","window.addEventListener('foobar'")],
  ['remove explicit action',s=>s.replace("button.addEventListener('click'","button.addEventListener('mouseover'")],
  ['remove guard',s=>s.replace("if(!button||!sheet||typeof window.print!=='function')return;",'')],
  ['add unapproved checkout',s=>s.replace('</body>','<a href="https://payhip.com/example">Pay</a></body>')],
];
for(const [name,mutate] of mutations){
  const changed=mutate(html);
  assert.notEqual(changed,html,'mutation did not apply: '+name);
  assert.ok(errors(changed).length,'mutant escaped: '+name);
}
process.stdout.write(JSON.stringify({
  classification:'SOURCE_CONTRACT_ONLY_NOT_BROWSER_OR_COMMERCE_VERIFICATION',
  source_checks:Object.keys(patterns).length+3,mutation_checks:mutations.length,
  verdict:'PASS',release_gate:'STAGING_HOLD'
})+'\n');

// R329 adversarial safety test suite; native Node command:
// node mind/r329/adversarial_r329.cjs
// Synthetic strings only. Never deploys, opens merchant URLs, accesses analytics or writes files.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const originalA=read('ZEN12-A-TEXT-ONLY-REVIEW.html');
const originalB=read('ZEN12-B-OPTIONAL-FILM-REVIEW.html');
const core=h=>(h.split('<!-- CORE START -->')[1]||'').split('<!-- CORE END -->')[0];
function failures(h){
 const out=[];
 if(/<a[^>]+href=["'][^"']*(zen12|hypnosislive|brainwaveshots|inspire3|affiliates)/i.test(h))out.push('merchant');
 if(/<(script|iframe|form)\b/i.test(h))out.push('unsafe_element');
 if(/\bautoplay\b/i.test(h))out.push('autoplay');
 if(!/<button[^>]*disabled/i.test(h))out.push('enabled_cta');
 if(!/Prospective affiliate disclosure:/.test(h))out.push('no_disclosure');
 if(!/https:\/\/finalvestige.com\/focus\//.test(h))out.push('no_free_route');
 if(/(guaranteed focus|clinically proven|cure anxiety|earn money automatically)/i.test(h))out.push('unsupported_promise');
 return out;
}
assert.deepEqual(failures(originalA),[]);
assert.deepEqual(failures(originalB),[]);
assert.equal(core(originalA),core(originalB));
const mutations=[
 ['active merchant anchor',originalA.replace('<!-- CORE END -->','<a href="https://zen12.com/?affiliate=example">Buy now</a><!-- CORE END -->'),'merchant'],
 ['script injection',originalA.replace('<!-- CORE END -->','<script>void(0)</script><!-- CORE END -->'),'unsafe_element'],
 ['new signup form',originalA.replace('<!-- CORE END -->','<form><input type="email"></form><!-- CORE END -->'),'unsafe_element'],
 ['embedded iframe',originalA.replace('<!-- CORE END -->','<iframe src="https://example.invalid"></iframe><!-- CORE END -->'),'unsafe_element'],
 ['autoplay video',originalB.replace('<!-- CORE END -->','<video autoplay></video><!-- CORE END -->'),'autoplay'],
 ['enabled purchase button',originalA.replace('<button type="button" disabled aria-disabled="true">','<button type="button">'),'enabled_cta'],
 ['disclosure removed',originalA.replace('Prospective affiliate disclosure:','Notice:'),'no_disclosure'],
 ['free Fieldbook replaced',originalA.replaceAll('https://finalvestige.com/focus/','https://finalvestige.com/other/'),'no_free_route'],
 ['fake cognitive promise',originalA.replace('<!-- CORE END -->','<p>clinically proven focus</p><!-- CORE END -->'),'unsupported_promise'],
 ['fake wealth promise',originalA.replace('<!-- CORE END -->','<p>earn money automatically</p><!-- CORE END -->'),'unsupported_promise']
];
let n=0;for(const [label,mutated,expected] of mutations){
 assert.ok(failures(mutated).includes(expected),'Failed to reject: '+label);n++;console.log('REJECT',label);
}
const changedCore=originalB.replace('A product does not need to promise miracles','A product always delivers miracles');
assert.notEqual(core(originalA),core(changedCore),'variant copy drift must be detectable');
console.log('PASS A/B drift detection');
console.log('R329 adversarial:',n,'/',mutations.length,'unsafe mutations rejected; one A/B drift detected; unchanged sources safe.');

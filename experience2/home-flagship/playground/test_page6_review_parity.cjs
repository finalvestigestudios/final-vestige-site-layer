'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const {check}=require('./verify_page6_review_parity.cjs');
const ids=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
const frag=Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item" style="--i:'+i+'">Record '+i+'</span>').join('\n');
const chapters=ids.map(id=>'<section id="'+id+'"><p>Evidence</p></section>').join('');
const live=frag+chapters+'<a href="https://finalvestige.com/blog/">Read the investigations';
const html=frag+chapters+'<img src="s67-19766.webp"><img src="Franklinexpeditionnote.jpg"><a href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook</a>Enter the evidence room';
const php="if (!is_page('fv-ex2-review')) return ''; // Reviewed reduced-motion remedy from draft PR #1062\nreturn <<<'FVPG_HTML_END'\n"+html+'\nFVPG_HTML_END';
const bp={steps:[{step:'installTheme',options:{targetFolderName:'assembler'}},{step:'mkdir'},{step:'writeFile',path:'/wordpress/wp-content/mu-plugins/fv.php',data:php},{step:'runPHP'},{step:'runPHP'}]};
function errors(p=live,b=bp,r){return check(p,b,r).errors;}
test('reconciles complete public-only fixture',()=>assert.deepEqual(errors(),[]));
test('rejects modified original historical fragment',()=>assert.ok(errors(live.replace('Record 17',''),bp).includes('MARGINS_EXACT_PUBLIC_TEXT')));
test('rejects missing review record',()=>{const b=structuredClone(bp);b.steps[2].data=b.steps[2].data.replace('<span class="fv-margin-strip__item" style="--i:71">Record 71</span>','');assert.ok(errors(live,b).includes('MARGINS_COUNT'));});
test('rejects missing chapter destination',()=>{const b=structuredClone(bp);b.steps[2].data=b.steps[2].data.replace('id="fv-hf-mind-title"','id="missing"');assert.ok(errors(live,b).includes('CHAPTER_fv-hf-mind-title'));});
test('rejects missing conversion experiment',()=>{const b=structuredClone(bp);b.steps[2].data=b.steps[2].data.replace('Explore the free 52-page Focus Fieldbook','Read more');assert.ok(errors(live,b).includes('FOCUS_REVIEW_EXPERIMENT'));});
test('rejects removed preview-only plugin guard',()=>{const b=structuredClone(bp);b.steps[2].data=b.steps[2].data.replace("if (!is_page('fv-ex2-review'))",'if (true)');assert.ok(errors(live,b).includes('PREVIEW_ONLY_GUARD'));});
test('rejects rights-pending NYPL injected into preview',()=>{const b=structuredClone(bp);b.steps[2].data=b.steps[2].data.replace('Franklinexpeditionnote.jpg','edit-017-v02-nypl-5003296-original.jpg');assert.ok(errors(live,b).includes('NYPL_EXCLUDED_UNTIL_RIGHTS_CLEARED'));});
test('rejects incomplete WP-rendered content',()=>assert.ok(errors(live,bp,'<html>No chapters</html>').includes('RENDERED_MARGINS')));

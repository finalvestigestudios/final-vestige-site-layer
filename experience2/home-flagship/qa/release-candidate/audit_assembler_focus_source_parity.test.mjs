import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectPage6,inspectHeader,inspectFocusPage,reconcile} from './audit_assembler_focus_source_parity.mjs';
const chapters=['title','chronicle','evidence','inquiry','method-title','observer','mind-title'];
const pageHtml=() => '<div data-fv-home-flagship><nav class="fv-hf__chapter-nav">'+
 chapters.map(s=>'<a href="#fv-hf-'+s+'">chapter</a>').join('')+'</nav>'+
 chapters.map(s=>'<section id="fv-hf-'+s+'">source</section>').join('')+
 Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item" style="--i:'+i+'">record</span>').join('')+
 '<div class="fv-hf__folio-arrival"></div><a href="/focus/">Focus</a><!-- wp:jetpack/subscriptions /--></div>';
const p=(content=pageHtml(),id=6)=>({structuredContent:{data:{id,status:'publish',modified:'2026-11-04T14:39:24',content}}});
const headerRaw='<!-- wp:navigation-link {"label":"FREE EBOOK","url":"/focus/"} /--><p><a href="/focus/">Fieldbook</a></p>';
const h=(raw=headerRaw,id='assembler//header')=>[{id,source:'custom',content:{raw}}];
const f=(content='<!-- wp:jetpack/subscriptions /--><a href="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf">Get PDF</a>')=>({structuredContent:{data:{id:1579,status:'publish',content}}});
const audit=(page=p(),header=h(),focus=f())=>reconcile(inspectPage6(page),inspectHeader(header),inspectFocusPage(focus));
test('source-only baseline preserves seven chapters, seventy-two records, header and Focus landing',()=>{
 const result=audit();assert.equal(result.source_checks_pass,true);assert.equal(result.release,'HOLD');
});
test('missing explicit Assembler nav Focus link fails closed',()=>{
 assert.equal(audit(p(),h('<p><a href="/focus/">Free ebook</a></p>')).source_checks_pass,false);
});
test('missing native header ebook-strip anchor fails closed',()=>{
 assert.equal(audit(p(),h('<!-- wp:navigation-link {"label":"FREE EBOOK","url":"/focus/"} /-->')).source_checks_pass,false);
});
test('wrong offer destination cannot be inferred from label alone',()=>{
 assert.equal(audit(p(),h('<!-- wp:navigation-link {"label":"FREE EBOOK","url":"/other/"} /--><a href="/focus/">F</a>')).source_checks_pass,false);
});
test('71 or mismatched Margin indices are rejected',()=>{
 assert.equal(audit(p(pageHtml().replace('style="--i:71"','style="--i:70"'))).source_checks_pass,false);
});
test('missing chapter target is rejected',()=>{
 assert.equal(audit(p(pageHtml().replace('id="fv-hf-inquiry"','id="removed-inquiry"'))).source_checks_pass,false);
});
test('missing historical folio is rejected',()=>{
 assert.equal(audit(p(pageHtml().replace('fv-hf__folio-arrival','missing-folio'))).source_checks_pass,false);
});
test('broken Focus PDF link is not certified',()=>{
 assert.equal(audit(p(),h(),f('<!-- wp:jetpack/subscriptions /-->')).source_checks_pass,false);
});
test('missing Jetpack subscription markup is rejected',()=>{
 assert.equal(audit(p(),h(),f('<a href="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf">PDF</a>')).source_checks_pass,false);
});
test('a different WordPress site page ID cannot spoof the source audit',()=>{
 assert.throws(()=>inspectPage6(p(pageHtml(),99)),/page 6 required/i);
});
test('missing exact Assembler header template fails closed',()=>{
 assert.throws(()=>inspectHeader(h(headerRaw,'other//header')),/Assembler header/i);
});
test('no fake visitor certification is permitted even on all source passes',()=>{
 const result=audit();assert.equal(result.qualification,'CMS_EDITOR_AND_ASSEMBLER_TEMPLATE_SOURCE_ONLY');
 assert.match(result.required_next,/Anonymous/);assert.equal(result.release,'HOLD');
});

'use strict';
/* node tests/experience-2/test_paired_conversion_docket.cjs [PRIVATE_READONLY_EXPORT.json]
 * A private optional export has {home,focus} wrapper; do not commit it.
 */
const fs=require('node:fs'),assert=require('node:assert/strict');
const {assess,inspect}=require('../../tools/experience-2/paired_conversion_docket.cjs');
function fixture(){
 const spans=Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item" style="--i:'+i+'">FIXTURE RECORD '+i+'</span>').join('');
 const links=Array.from({length:7},(_,i)=>'<a href="#fv-hf-case'+i+'">Chapter</a>').join('');
 return {home:{id:6,status:'publish',modified:'2026-11-05T12:07:24',
 content:spans+'<nav class="fv-hf__chapter-nav">'+links+'</nav><!-- wp:jetpack/subscriptions --> '+
 'The Victory Point note: an 1847 message NASA · Apollo 204 Review Board '+
 '<a href="/focus/">Focus</a><div class="fv-hf__opening-actions"><a href="#fv-hf-evidence">Evidence</a><a href="/blog/">Read the investigations</a></div>'},
 focus:{id:1579,status:'publish',modified:'2026-11-05T17:44:02',
 content:'<!-- wp:jetpack/subscriptions --> 52-page Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf '+
 '<script id="fvf-gift-v2">var q=new URLSearchParams(window.location.search).get("subscribe");if(q){show();}</script>'}};
}
const file=process.argv[2],data=file?JSON.parse(fs.readFileSync(file,'utf8')):fixture();
const home=data.home,focus=data.focus;
let assertions=0;
function pass(v,label){assert(v,label);assertions++;}
const base=assess(home,focus,{propose_hero_focus_bridge:true});
pass(base.source.source_integrity==='PASS','baseline should match exact approved source shape');
pass(base.decision==='RELEASE_HOLD','source-only inspection never authorizes deploy');
pass(base.blockers.includes('P0_SPOOFABLE_FOCUS_GIFT_UI_LIVE'),'reject URL-only success');
pass(base.blockers.includes('HERO_CTA_DEPENDS_ON_UNRELEASED_FOCUS_INTEGRITY_REPAIR'),'do not send more traffic to unverified success');
function reject(label,mutate,expected){
 const h=JSON.parse(JSON.stringify(home)),f=JSON.parse(JSON.stringify(focus));
 const a=h.data||h,b=f.data||f;
 mutate(a,b);
 const out=assess(h,f,{propose_hero_focus_bridge:true});
 pass(out.blockers.includes(expected),label+' expected '+expected);
}
reject('lost record',h=>h.content=h.content.replace(/<span class="fv-margin-strip__item"[^>]*>[^<]*<\/span>/,''),'MARGINS_NOT_72');
reject('home Jetpack removed',h=>h.content=h.content.replace('<!-- wp:jetpack/subscriptions ','<!-- wp:paragraph '),'NATIVE_JETPACK_BLOCK_DRIFT');
reject('Focus Jetpack removed',(h,f)=>f.content=f.content.replace('<!-- wp:jetpack/subscriptions ','<!-- wp:paragraph '),'NATIVE_JETPACK_BLOCK_DRIFT');
reject('PDF changed',(h,f)=>f.content=f.content.replaceAll('Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf','missing.pdf'),'FIELD_BOOK_OR_EDITION_MISSING');
reject('home edited',h=>h.modified='2026-11-09','HOME_VERSION_DRIFT');
reject('Focus edited',(h,f)=>f.modified='2026-11-09','FOCUS_VERSION_DRIFT');
reject('hero evidence link broken',h=>h.content=h.content.replace(/(<div class="fv-hf__opening-actions">[\s\S]*?)href="#fv-hf-evidence"/,'$1href="#lost"'),'HERO_EVIDENCE_ACTIONS_DRIFT');
reject('NASA attribution removed',h=>h.content=h.content.replace('NASA · Apollo 204 Review Board','redacted'),'ARCHIVAL_SOURCE_CUSTODY_DRIFT');
reject('Focus gift script removed',(h,f)=>f.content=f.content.replace('id="fvf-gift-v2"','id="missing"'),'FOCUS_GIFT_SCRIPT_MISSING');
reject('chapter navigation altered',h=>h.content=h.content.replace('class="fv-hf__chapter-nav"','class="broken"'),'CHAPTER_NAV_NOT_7');
pass(inspect(home,focus).observed.margins===72,'all historical records remain');
pass(inspect(home,focus).observed.chapters===7,'seven chapter targets remain');
console.log(JSON.stringify({assertions,passed:assertions,status:'PASS',data:file?'private_editor_export':'synthetic_fixture',site_writes:0,form_submissions:0}));

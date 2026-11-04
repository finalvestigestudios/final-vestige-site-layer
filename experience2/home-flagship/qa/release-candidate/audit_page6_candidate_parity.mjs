#!/usr/bin/env node
/** Read-only release audit: compare a user-provided WordPress Page 6 view JSON
 * with the exact local homepage candidate index.html.
 * No network calls, CMS writes, credentials, analytics, or source HTML in results.
 *
 * node audit_page6_candidate_parity.mjs --self-test
 * node audit_page6_candidate_parity.mjs /private/page6-view.json experience2/home-flagship/index.html
 */
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';

export function inspect(html) {
  assert.equal(typeof html,'string');
  assert.ok(html.length<5_000_000,'Unexpectedly large input');
  const tags=[...html.matchAll(/<([a-z][a-z0-9-]*)\b[^>]*>/gi)].map(x=>x[0]);
  const classTags=(cls)=>tags.filter(t=>{
    const m=t.match(/\bclass=["']([^"']*)["']/i);
    return m&&m[1].split(/\s+/).includes(cls);
  });
  const margins=classTags('fv-margin-strip__item').filter(t=>/^<span\b/i.test(t))
    .map(t=>{const x=t.match(/--i\s*:\s*(\d+)/);return x?Number(x[1]):null;});
  const chapterNav=html.match(/<nav\b[^>]*class=["'][^"']*\bfv-hf__chapter-nav\b[^>]*>[\s\S]*?<\/nav>/i)?.[0]||'';
  const chapters=[...chapterNav.matchAll(/<a\b[^>]*href=["']#([^"']+)["']/gi)].map(m=>m[1]);
  const focus=tags.filter(t=>/^<a\b/i.test(t)&&
    /\bhref=["'](?:https:\/\/finalvestige\.com)?\/focus\/?["']/i.test(t));
  return {
    seven_chapter_targets:chapters,
    seven_chapter_links_resolve:chapters.length===7&&
      chapters.every(id=>html.includes('id="'+id+'"')),
    published_margin_count:margins.length,
    margin_indexes_sequential:margins.length===72&&margins.every((n,i)=>n===i),
    focus_link_count:focus.length,
    masthead_focus_anchor:classTags('fv-hf__mast-cta').some(t=>/^<a\b/i.test(t)),
    native_explore_details:classTags('fv-hf__mobile-explore').some(t=>/^<details\b/i.test(t)),
    has_flagship_root:html.includes('data-fv-home-flagship'),
    franklin_folio_present:classTags('fv-hf__folio-arrival').length>0,
    jetpack_subscription_markup_present:html.includes('wp-block-jetpack-subscriptions')
  };
}
export function reconcile(published,candidate){
  assert.ok(published.has_flagship_root&&candidate.has_flagship_root,
    'This audit requires both flagship roots');
  const critical={
    live_has_seven_chapters:published.seven_chapter_links_resolve,
    candidate_has_seven_chapters:candidate.seven_chapter_links_resolve,
    live_retains_72_margins:published.margin_indexes_sequential,
    live_retains_focus_destination:published.focus_link_count>0,
    candidate_retains_focus_destination:candidate.focus_link_count>0,
    published_jetpack_markup_present:published.jetpack_subscription_markup_present
  };
  return {
    release:'HOLD',
    source:'PUBLISHED_CMS_EDITOR_VIEW_NOT_ANONYMOUS_BROWSER',
    critical,
    source_parity:{
      candidate_mobile_explore: candidate.native_explore_details,
      published_mobile_explore: published.native_explore_details,
      candidate_masthead_focus: candidate.masthead_focus_anchor,
      published_masthead_focus: published.masthead_focus_anchor
    },
    parity_action: (candidate.native_explore_details&&!published.native_explore_details)||
      (candidate.masthead_focus_anchor&&!published.masthead_focus_anchor)
      ?'VERIFY_NATIVE_ASSEMBLER_HEADER_AND_MOBILE_CTA_IN_REAL_BROWSER'
      :'INSPECT_FULL_DOCUMENT_BEFORE_RELEASE',
    note:'Differences are not proof of a bug: live uses WordPress native Assembler chrome.'
  };
}
async function selfTest(){
  const base=(count=72)=>'<div data-fv-home-flagship>'+
    '<nav class="fv-hf__chapter-nav">'+
    ['title','chronicle','evidence','inquiry','method-title','observer','mind-title']
      .map(x=>'<a href="#fv-hf-'+x+'">Chapter</a>').join('')+
    '</nav>'+['title','chronicle','evidence','inquiry','method-title','observer','mind-title']
      .map(x=>'<h2 id="fv-hf-'+x+'">A</h2>').join('')+
    Array.from({length:count},(_,i)=>
      '<span class="fv-margin-strip__item" style="--i:'+i+'">PUBLIC</span>').join('')+
    '<a href="/focus/">Focus</a><div class="fv-hf__folio-arrival"></div>'+
    '<div class="wp-block-jetpack-subscriptions"></div></div>';
  const live=inspect(base()),candidate=inspect(base()+
    '<details class="fv-hf__mobile-explore"></details>'+
    '<a class="fv-hf__mast-cta" href="https://finalvestige.com/focus/">Focus</a>');
  assert.ok(live.margin_indexes_sequential);assert.ok(live.seven_chapter_links_resolve);
  assert.ok(!inspect(base(71)).margin_indexes_sequential);
  assert.ok(!inspect(base().replace('href="/focus/"','href="/broken/"')).focus_link_count);
  assert.ok(!inspect(base().replace('href="#fv-hf-inquiry"','href="#missing"')).seven_chapter_links_resolve);
  assert.ok(reconcile(live,candidate).parity_action.includes('VERIFY_NATIVE'));
  assert.ok(!inspect(base()).native_explore_details);
  assert.equal(reconcile(live,candidate).release,'HOLD');
  console.log('PASS: 8 read-only source contract cases. No WordPress/browser qualification claimed.');
}
function unpackWordPressResponse(raw){
  const item=raw.structuredContent?.data??raw.data??raw;
  const content=typeof item.content==='string'?item.content:item.content?.rendered;
  assert.ok(item.id===6&&item.status==='publish','Requires published homepage ID 6');
  assert.equal(typeof content,'string','Missing WordPress content');
  return {content,modified:item.modified??null};
}
async function main(){
  if(process.argv[2]==='--self-test')return selfTest();
  const [pageFile,candidateFile]=process.argv.slice(2);
  if(!pageFile||!candidateFile){
    console.error('Usage: node audit_page6_candidate_parity.mjs PAGE6_VIEW_JSON index.html');
    process.exitCode=2;return;
  }
  const page=unpackWordPressResponse(JSON.parse(await readFile(pageFile,'utf8')));
  const candidate=await readFile(candidateFile,'utf8');
  const result=reconcile(inspect(page.content),inspect(candidate));
  result.published_modified=page.modified;
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
  if(Object.values(result.critical).some(v=>!v))process.exitCode=1;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(e=>{
  console.error('RELEASE HOLD: '+e.message);process.exitCode=1;
});

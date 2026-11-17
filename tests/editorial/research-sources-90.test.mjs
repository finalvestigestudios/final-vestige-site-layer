import test from 'node:test';
import assert from 'node:assert/strict';
import {stage,cards,replaceOnce} from '../../scripts/editorial/reconcile-research-sources-90.mjs';

const perCategory={declassified:12,accountability:24,engineering:21,archives:25,navigation:8};
const rawCards=Object.entries(perCategory).flatMap(([cat,n])=>Array.from({length:n},(_,j)=>
 '<article class="fv-rs-card" data-cat="'+cat+'"><p class="fv-rs-meta">Institution · Link-only</p><h3>'+cat+' document '+j+'</h3><p>Evidence description.</p><a href="https://example.org/'+cat+'/'+j+'" rel="noopener noreferrer">Open</a></article>'
)).join('');
const page=['<!-- wp:html -->','<p>Sixty free collections, reports</p>',
'<div><b>60</b><span>curated sources</span></div>',
'<label>Search all 60 sources</label>',
'<button>All <span>60</span></button>',
'<button>Declassified &amp; decisions <span>9</span></button>',
'<button>Accountability &amp; public records <span>18</span></button>',
'<button>Engineering, disaster &amp; safety <span>16</span></button>',
'<button>Archives, maps &amp; research <span>12</span></button>',
'<button>Navigation &amp; preservation <span>5</span></button>',
'<p>Showing all 60 sources.</p>',
'<p>A record-group discovery tool that makes digitization gaps visible: NARA’s June 2026 baseline reports 475,127,595 scans, about 3.87% of estimated textual holdings represented there.</p>',
"<script>let s=' of 60 source';const totals={all:90,declassified:12,accountability:23,engineering:21,archives:26,navigation:8};</script>",
rawCards,'<!-- /wp:html -->'].join('\n');
const library='<!-- wp:group --><p>Sixty free, first-party or institutionally maintained sources</p><p>60 curated sources · 8 research families · Link-out access</p><!-- /wp:group -->';
const source={page_id:1338,page_modified:'2026-11-03T22:12:43',page_content:page,
              library_id:77,library_modified:'2026-11-07T19:39:01',library_content:library};

test('90 actual cards have the expected category distribution',()=>{
 assert.equal(cards(page).length,90);
 for(const [cat,n] of Object.entries(perCategory))assert.equal(cards(page).filter(c=>c.category===cat).length,n);
});
test('guarded staging corrects all 15 copy/label and source-freshness anchors and leaves cards intact',()=>{
 const out=stage(source);
 assert.equal(out.status,'STAGING_ONLY_DO_NOT_PUBLISH');
 assert.equal(out.validation.substitutions,15);
 assert.equal(out.validation.source_cards_preserved,true);
 assert.equal(out.validation.production_theme_verified,false);
 assert.equal(out.page_content.includes('Search all 90 sources'),true);
 assert.equal(out.page_content.includes('Showing all 90 sources'),true);
 assert.equal(out.page_content.includes('accountability:24,engineering:21,archives:25'),true);
 assert.equal(out.library_content.includes('90 curated sources · 5 research paths'),true);
 assert.equal(out.page_content.includes('NARA updates these estimates monthly'),true);
 assert.equal(out.page_content.includes('NARA’s June 2026 baseline'),false);
 assert.deepEqual(cards(out.page_content),cards(page));
});
test('refuses missing outdated-statistic anchor (fail closed)',()=>{
 assert.throws(()=>stage({...source,page_content:page.replace('475,127,595','475,127,596')}),/expected one occurrence/);
});
test('refuses changed WordPress revision (do not race another editor)',()=>{
 assert.throws(()=>stage({...source,page_modified:'2026-11-16T11:00:00'}),/revision changed/);
});
test('refuses a missing source or a changed category count',()=>{
 assert.throws(()=>stage({...source,page_content:page.replace('<article class="fv-rs-card"','<div class="fv-rs-card"')}),/90 actual source cards/);
});
test('refuses duplicate source destinations',()=>{
 const modified=page.replace('https://example.org/declassified/1','https://example.org/declassified/0');
 assert.throws(()=>stage({...source,page_content:modified}),/duplicate or missing/);
});
test('refuses to run twice',()=>{
 const staged=stage(source);
 assert.throws(()=>stage({...source,page_content:staged.page_content,library_content:staged.library_content}),/expected one occurrence/);
});
test('replaceOnce rejects ambiguous targets',()=>{
 assert.throws(()=>replaceOnce('x x','x','y'),/expected one occurrence/);
});

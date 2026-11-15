'use strict';
const api=require('./audit_commons_redirect_widths_20261111.cjs');
const source=require('./coverage_288_exact_pr1703_20261110.json');
const saved=require('./commons_redirect_1280_triage_20261111.json');
function yes(ok,name){if(!ok)throw Error(name);}
function rejects(fn,name){let threw=false;try{fn();}catch(_){threw=true;}yes(threw,name);}
function run(){
 const a=api.build(source.rows),c=a.counts;
 const tests=[
 ['288 source rows',()=>yes(source.rows.length===288,'288')],
 ['118 redirects',()=>yes(c.commons_redirects===118,'118')],
 ['75 at 1280',()=>yes(c.requested_width_1280===75,'75')],
 ['17 at 960',()=>yes(c.requested_width_960===17,'17')],
 ['26 unspecified',()=>yes(c.without_width_query===26,'26')],
 ['16 posts',()=>yes(c.affected_posts===16,'16')],
 ['74 catalog URLs',()=>yes(c.catalog_urls===74,'74')],
 ['71 known advisory sizes',()=>yes(c.advisory_dimensions===71,'71')],
 ['24 narrow advisory sizes',()=>yes(c.advisory_under_960===24,'24')],
 ['source width exact',()=>yes(a.entries.every(x=>x.exact_stored_src.includes('?width=1280')),'width')],
 ['source lineage exact',()=>yes(a.entries.every(x=>source.rows.some(s=>s.slot===x.slot&&s.stored_url===x.exact_stored_src)),'lineage')],
 ['guest observation null',()=>yes(a.entries.every(x=>x.visitor_http_status===null&&x.guest_encoded_wire_bytes===null),'guest')],
 ['rights never auto approved',()=>yes(a.entries.every(x=>!x.item_specific_rights_cleared&&!x.editor_approved),'rights')],
 ['WP/cache never auto approved',()=>yes(a.entries.every(x=>!x.wordpress_write_permitted&&!x.caching_permitted),'WP')],
 ['798 native no-upscale guard',()=>yes(a.entries.find(x=>x.slot==='425:3').advisory_no_upscale_max_width_if_catalog_correct===798,'798')],
 ['600 native no-upscale guard',()=>yes(a.entries.find(x=>x.slot==='215:1').advisory_no_upscale_max_width_if_catalog_correct===600,'600')],
 ['76 pct not measured',()=>yes(a.historical.measured_transfer_reduction_pct===null,'76')],
 ['source blob pinned',()=>yes(a.provenance.frozen_288_blob==='4965a862f7de7de46c1f4a1e26f3ca70a8c38805','blob')],
 ['report source verified',()=>yes(api.verify(saved,source.rows).pass,'report')],
 ['altered URL rejected',()=>{const j=JSON.parse(JSON.stringify(saved));j.entries[0].exact_stored_src+='?bogus';yes(!api.verify(j,source.rows).pass,'URL');}],
 ['fake HTTP rejected',()=>{const j=JSON.parse(JSON.stringify(saved));j.entries[0].visitor_http_status=404;yes(!api.verify(j,source.rows).pass,'HTTP');}],
 ['fake 960 approval rejected',()=>{const j=JSON.parse(JSON.stringify(saved));j.entries[0].editor_approved=true;yes(!api.verify(j,source.rows).pass,'editor');}],
 ['fake weight saving rejected',()=>{const j=JSON.parse(JSON.stringify(saved));j.historical.measured_transfer_reduction_pct=76;yes(!api.verify(j,source.rows).pass,'wire');}],
 ['missing source row rejected',()=>rejects(()=>api.build(source.rows.slice(1)),'missing')],
 ['duplicate slot rejected',()=>{const j=JSON.parse(JSON.stringify(source.rows));j[1].slot=j[0].slot;rejects(()=>api.build(j),'duplicate');}],
 ['actual guest evidence drift rejected',()=>{const j=JSON.parse(JSON.stringify(source.rows));j[0].guest_http_status=200;rejects(()=>api.build(j),'guest drift');}],
 ['double width rejected',()=>rejects(()=>api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg?width=960&width=1280'),'double')],
 ['invalid width rejected',()=>rejects(()=>api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg?width=0'),'zero')],
 ['bad width rejected',()=>rejects(()=>api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg?width=nope'),'bad')],
 ['non-Commons ignored',()=>yes(api.widthOf('https://example.com/a.jpg?width=1280')==='not_commons_redirect','scope')],
 ['Commons no width',()=>yes(api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg')==='no_width','absent')],
 ['Commons 960',()=>yes(api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg?width=960')===960,'960')],
 ['Commons 1280',()=>yes(api.widthOf('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg?width=1280')===1280,'1280')],
 ['escaped URL remains intact',()=>yes(a.entries.some(x=>x.exact_stored_src.includes('%20')),'escaped')],
 ['P0 preserved',()=>yes(a.required_first_p0.join(',')==='285:5,285:2,287:5,418:1,418:2,407:1','P0')]
 ];
 let passed=0;for(const [name,fn] of tests){try{fn();passed++;}catch(e){throw Error(name+': '+e.message);}}
 return {passed,total:tests.length};
}
module.exports={run};
if(require.main===module){const t=run();process.stdout.write(t.passed+'/'+t.total+' passed\\n');}

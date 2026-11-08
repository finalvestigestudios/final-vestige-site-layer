'use strict';
// REVIEW-ONLY. Reads local WordPress context=edit exports; makes NO CMS/network writes.
const HOME_SHA='685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b';
const OLD_H='One email a week from Final Vestige.';
const NEW_H='New investigations, delivered when we publish.';
const OLD_C='Unsubscribe anytime · <a href="/dispatch/">About The Dispatch</a>';
const NEW_C='Sent when we publish. Some emails may contain recommendations that earn us a commission. Unsubscribe anytime · <a href="/dispatch/">About The Dispatch</a> · <a href="/privacy-policy/">Privacy Policy</a>';
const OLD_STYLE='<p class="has-text-align-center" style="font-size:10px;font-weight:750;letter-spacing:0.1em;margin-top:18px">';
const NEW_STYLE=OLD_STYLE.replace('font-size:10px','font-size:14px').replace('font-weight:750','font-weight:400').replace('letter-spacing:0.1em','letter-spacing:normal');
const OLD_BLOCK='<!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"10px","fontWeight":"750","letterSpacing":"0.1em"},"spacing":{"margin":{"top":"18px"}}}} -->';
const NEW_BLOCK=OLD_BLOCK.replace('"10px"','"14px"').replace('"750"','"400"').replace('"0.1em"','"normal"');
const IDS=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
function check(cond,why){if(!cond)throw Error('HOLD: '+why);}
function n(s,x){return s.split(x).length-1;}
function unpack(p){p=p.data||p;return {id:p.id,status:p.status,modified:p.modified,html:typeof p.content==='string'?p.content:p.content&&p.content.raw};}
function review(home,focus,fixture=false){
 const h=unpack(home),f=unpack(focus),a=h.html,b=f.html;
 check(h.id===6&&f.id===1579,'page IDs');
 check(h.status==='publish'&&f.status==='publish','publication status');
 check(h.modified==='2026-11-05T12:07:24'&&f.modified==='2026-11-05T17:44:02','source modified');
 check(typeof a==='string'&&typeof b==='string','raw source required');
 if(!fixture){
  check(a.length===150710,'source length drift');
  check(typeof require==='function','run this hash gate under Node, not a browser');
  check(require('node:crypto').createHash('sha256').update(a,'utf8').digest('hex')===HOME_SHA,'source SHA drift');
 }
 check(b.includes('our email of new investigations and archive finds, sent when we publish them.'),'Focus consent changed');
 check(b.includes('fvf-gift-v2'),'Focus state changed; re-review #1451');
 for(const x of [OLD_H,OLD_C,OLD_STYLE,OLD_BLOCK])check(n(a,x)===1,'target missing/duplicated: '+x.slice(0,40));
 check(n(a,'<!-- wp:jetpack/subscriptions')===1,'Jetpack block not preserved');
 check(n(a,'class="fv-margin-strip__item"')===72,'Margins changed');
 for(const id of IDS)check(a.includes('id="'+id+'"'),'chapter missing '+id);
 const edits=[[OLD_H,NEW_H],[OLD_C,NEW_C],[OLD_STYLE,NEW_STYLE],[OLD_BLOCK,NEW_BLOCK]];
 let changed=a;
 for(const [oldText,newText] of edits)changed=changed.replace(oldText,newText);
 let undo=changed;
 for(const [oldText,newText] of edits.slice().reverse())undo=undo.replace(newText,oldText);
 check(changed!==a&&undo===a,'exact reversible four-target change');
 for(const tok of ['<img ','<script','<style','<!-- wp:jetpack/subscriptions','class="fv-margin-strip__item"','href="/focus/"','href="https://finalvestige.com/focus/"'])
  check(n(a,tok)===n(changed,tok),'changed unrelated source '+tok);
 return {status:'OFFLINE REVIEW PASS / PRODUCTION HOLD',edits:4,heading_before:OLD_H,heading_after:NEW_H,near_form_affiliate_notice:true,privacy_link_added:true,disclosure_size_before_px:10,disclosure_size_after_px:14,chapters:7,margins:72,jetpack_signup_tested:false,commercial_uplift_verified:false};
}
function fixtures(){
 const h=IDS.map(id=>'<div id="'+id+'"></div>').join('')+'<span class="fv-margin-strip__item"></span>'.repeat(72)+'<!-- wp:jetpack/subscriptions /-->'+'<h2>'+OLD_H+'</h2>'+OLD_BLOCK+OLD_STYLE+OLD_C+'</p><img src="a"><a href="/focus/">Focus</a>';
 return [{id:6,status:'publish',modified:'2026-11-05T12:07:24',content:h},{id:1579,status:'publish',modified:'2026-11-05T17:44:02',content:'our email of new investigations and archive finds, sent when we publish them. <script id="fvf-gift-v2"></script>'}];
}
function tests(){
 const [h,f]=fixtures();check(review(h,f,true).edits===4,'positive test');
 const mut=[
  x=>x[0].id=5,x=>x[1].id=7,x=>x[0].status='draft',
  x=>x[0].modified='changed',x=>x[0].content=x[0].content.replace(OLD_H,'different'),
  x=>x[0].content+=OLD_H,
  x=>x[0].content=x[0].content.replace('<!-- wp:jetpack/subscriptions /-->',''),
  x=>x[0].content=x[0].content.replace('class="fv-margin-strip__item"','removed'),
  x=>x[0].content=x[0].content.replace('id="fv-hf-observer"','id="removed"'),
  x=>x[1].content=x[1].content.replace('sent when we publish them','every Friday'),
  x=>x[1].content=x[1].content.replace('fvf-gift-v2','unknown'),
  x=>x[0].content=x[0].content.replace(OLD_STYLE,'')
 ];
 mut.forEach((fn,i)=>{const x=fixtures();fn(x);let blocked=false;try{review(x[0],x[1],true);}catch(e){blocked=true;}check(blocked,'negative control '+i);});
 return {passed:13,positive:1,negative_rejected:12};
}
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');
 if(process.argv.length===3&&process.argv[2]==='--self-test')console.log(JSON.stringify(tests()));
 else if(process.argv.length===4)console.log(JSON.stringify({tests:tests(),review:review(JSON.parse(fs.readFileSync(process.argv[2])),JSON.parse(fs.readFileSync(process.argv[3])))}));
 else {console.error('node dispatch_consent_review.cjs --self-test OR page6.json focus1579.json');process.exit(2);}
}

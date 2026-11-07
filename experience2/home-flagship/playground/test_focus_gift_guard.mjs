/** Unpublished Focus download-state regression. No network, forms or CMS writes. */
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { strict as assert } from 'node:assert';
import { createHash } from 'node:crypto';
const js=readFileSync(new URL('./focus_gift_guard.js',import.meta.url),'utf8');
const fixture=JSON.parse(readFileSync(new URL('./focus_gift_source_20261107.json',import.meta.url),'utf8'));
assert.equal(fixture.page_id,1579);
assert.equal(createHash('sha256').update(fixture.script).digest('hex'),'f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7');
assert.ok(!js.includes('location.search'));
let count=0;
function scenario({className='',query='?subscribe=made_up_value',jsEnabled=true,transition=null,expectedVisible=false}={}){
  let subscriber=className.split(/\s+/).includes('is-subscriber');
  let callback;
  const gift={hidden:true};
  const container={classList:{contains:(c)=>c==='is-subscriber' && subscriber}};
  const document={getElementById:(id)=>id==='fvf-gift'?gift:null,querySelector:(s)=>s==='.wp-block-jetpack-subscriptions__container'?container:null};
  class Observer{constructor(cb){callback=cb} observe() {}}
  if(jsEnabled)runInNewContext(js,{document,MutationObserver:Observer,window:{location:{search:query}}});
  if(transition!==null){subscriber=transition;callback?.()}
  assert.equal(!gift.hidden,expectedVisible,JSON.stringify({className,query,transition}));
  count++;
}
scenario();
scenario({query:'?subscribe=success'});
scenario({query:'?subscribe=invalid_email'});
scenario({className:'is-subscriber',expectedVisible:true});
scenario({className:'not-is-subscriber'});
scenario({className:'',transition:true,expectedVisible:true});
scenario({className:'is-subscriber',transition:false});
scenario({jsEnabled:false,className:'is-subscriber'});
console.log(JSON.stringify({scope:'local isolated VM; not WordPress/Jetpack acceptance',cases_passed:count,confirmed_subscriber_events:0,verified_sales:0,decision:'QA_CANDIDATE_ONLY'}));

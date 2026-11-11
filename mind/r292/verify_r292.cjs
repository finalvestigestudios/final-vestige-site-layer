/* Mind R292 bounded source QA — NOT browser, native media, FTC legal clearance or revenue proof.
 * Native: node mind/r292/verify_r292.cjs (repository root).
 * Exports audit(files), mutationCases(files), paths.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path');
const P={
 article:'mind/r292/THE-VOICE-THAT-TOLD-YOU-TO-CONCENTRATE-UNPUBLISHED.md',
 hub:'mind/r292/MIND-SUGGESTION-RESEARCH-ROOM-WP-UNPUBLISHED.html',
 matrix:'mind/r292/SELF-HYPNOSIS-SOURCE-CLAIM-OFFER-GATES.json',
 plan:'mind/r292/R291-VIDEO-QA-REPAIR-AND-OFFER-REVENUE-ACCEPTANCE.md',
 a:'mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
 b:'mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html',
 video:'mind/r291/ORIGINAL-42S-OPTIONAL-VIDEO-INSERT-UNPUBLISHED.html',
 renderer:'mind/r291/render_original_thatcher_short.py'
};
const needed=['named_fv_approval','offer_authorization','approved_channels','issued_earning_url','partner_tracking_terms','affiliate_creative_rights','exact_destination_identity','checkout_identity','refund_and_delivery_terms','independent_claim_substantiation','ftc_near_link_disclosure','founder_commercial_approval','founder_production_release','privacy_and_consent','real_creator_asset_ids','signed_out_mobile_a11y','refund_fee_settlement_reporting','original_video_rights_and_hosted_qa'];
function audit(files){
 const e=[];
 for(const p of Object.values(P))if(typeof files[p]!=='string'||files[p].length<100)e.push('missing '+p);
 if(e.length)return e;
 let m;try{m=JSON.parse(files[P.matrix])}catch(_){return ['invalid matrix JSON']}
 const article=files[P.article],hub=files[P.hub],plan=files[P.plan],a=files[P.a],b=files[P.b],video=files[P.video],renderer=files[P.renderer];
 function chk(x,msg){if(!x)e.push(msg)}
 chk(m.state==='DRAFT_UNPUBLISHED_HARD_HOLD'&&m.no_active_affiliate_links===true,'source ledger release hold');
 chk(m.no_new_jetpack_list===true&&m.canonical_presell?.B_status?.startsWith('STATIC_STORYBOARD'),'one funnel and honest static B');
 chk(m.sources?.length===18&&m.claims?.length===21&&m.gates?.length===18,'source/claim/gate counts');
 const sourceIds=new Set(m.sources?.map(x=>x.id));
 chk(sourceIds.size===18&&new Set(m.claims?.map(x=>x.id)).size===21,'duplicate identities');
 chk(JSON.stringify(m.gates?.map(x=>x.id).sort())===JSON.stringify([...needed].sort()),'gate identities');
 chk(m.gates?.every(x=>x.state==='HARD_HOLD'&&x.evidence===null),'gates must remain held');
 for(const s of m.sources||[])chk(/^https:\/\//.test(s.url),'source URL '+s.id);
 for(const c of m.claims||[])chk(c.source_ids?.length>0&&c.source_ids.every(id=>sourceIds.has(id)),'claim source join '+c.id);
 chk(m.creator_routes?.length===3&&m.creator_routes?.every(x=>x.asset_id===null&&x.post_url===null),'creator ID unverified');
 chk(m.commercial_events?.net_revenue_per_1000_qualified_humans===null&&m.commercial_events?.cleared_commission===null,'fabricated revenue');
 chk(m.canonical_presell?.A===P.a&&m.canonical_presell?.B===P.b,'canonical A/B paths');
 chk(article.includes('49 meta-analyses')&&article.includes('nine of the 49')&&article.includes('261 distinct')&&article.includes('Puységur'),'scientific bounds');
 chk(article.includes('not a trial of Zen12')&&article.includes('seller claims'),'product-generalization caveat');
 chk(!/49 guaranteed cures/i.test(article),'unsupported altered research outcome');
 chk(!/\]\(https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(article),'active merchant source link in article');
 chk(!/clinically proven to improve (?:everyone|your)|guaranteed concentration|guarantees? wealth|medically cure/i.test(article+hub),'medical/wealth outcome guarantee');
 chk(!/<(?:script|form|iframe|object|embed)\b/i.test(hub),'active hub script, iframe or second signup');
 chk(!/<(?:img|source|track)\b[^>]*\bsrc(?:set)?=["']https?:/i.test(hub),'remote pixel/media');
 chk(!/<a\b[^>]*href=["'](?:https?:\/\/)?(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i.test(hub),'active merchant href');
 chk(/<button\b[^>]*\bdisabled\b/i.test(hub)&&/may earn a commission at no additional cost to you/i.test(hub),'disabled CTA and adjacent disclosure');
 chk(/<html\b[^>]*lang="en"/i.test(hub)&&/name="viewport"/i.test(hub)&&/focus-visible/i.test(hub)&&/prefers-reduced-motion/i.test(hub),'baseline mobile/keyboard/reduced motion HTML');
 chk(/https:\/\/finalvestige\.com\/focus\//i.test(hub),'existing Focus route');
 chk(plan.includes('Thatcher illusion')&&plan.includes('Change blindness')&&plan.includes('Puységur')&&plan.includes('exactly'),'canonical creator roster');
 chk(plan.includes('not experimentally faithful')||plan.includes('does not construct an experimentally faithful'),'schematic film limitation');
 chk(plan.includes('Binary and captions are not committed')&&plan.includes('NOT COMPUTABLE')&&plan.includes('HARD HOLD'),'missing media/revenue limits');
 chk(video.includes('<video')&&/preload=["']none["']/.test(video)&&!/autoplay(?:\s|=|>)/.test(video),'R291 optional video autoplay guard');
 chk(renderer.includes('def face(')&&renderer.includes('ffmpeg'),'existing renderer inspected (not reproduced)');
 chk(a.includes('Is Zen12 Worth Buying?')&&b.includes('Is Zen12 Worth Buying?'),'canonical guide files loaded');
 chk(/42-second|42 second|42s/i.test(b),'B storyboard present; not playback proof');
 return e;
}
function mutationCases(files){
 const cases=[];
 const edit=(label,p,transform)=>{let f={...files};f[p]=transform(f[p]);cases.push({label,files:f})};
 const editJson=(label,fn)=>edit(label,P.matrix,s=>{let m=JSON.parse(s);fn(m);return JSON.stringify(m)});
 editJson('activate-affiliate-flag',m=>m.no_active_affiliate_links=false);
 editJson('activate-approval',m=>m.gates[0].state='APPROVED');
 editJson('drop-gate',m=>m.gates.pop());
 editJson('rename-gate',m=>m.gates[2].id='fake_name');
 editJson('invent-creator-id',m=>m.creator_routes[0].asset_id='invented');
 editJson('invent-post-url',m=>m.creator_routes[1].post_url='https://example.com/fabricated');
 editJson('invent-revenue',m=>m.commercial_events.cleared_commission=99);
 editJson('wrong-source-join',m=>m.claims[0].source_ids=['missing_id']);
 editJson('duplicate-source',m=>m.sources[1].id=m.sources[0].id);
 editJson('flip-a-b-route',m=>m.canonical_presell.A='not-the-canonical-path');
 editJson('change-b-to-playable',m=>m.canonical_presell.B_status='PLAYABLE_LIVE');
 editJson('new-newsletter',m=>m.no_new_jetpack_list=false);
 edit('add-tracking-script',P.hub,s=>s.replace('</body>','<script src="https://tracking.invalid/tag.js"></script></body>'));
 edit('add-signup-form',P.hub,s=>s.replace('</body>','<form><input type="email"></form></body>'));
 edit('add-merchant-link',P.hub,s=>s.replace('</body>','<a href="https://zen12.com/getstarted">Buy now</a></body>'));
 edit('enable-cta',P.hub,s=>s.replace('type="button" disabled','type="button"'));
 edit('erase-disclosure',P.hub,s=>s.replace('may earn a commission at no additional cost to you','may link to useful products'));
 edit('guarantee-cure',P.hub,s=>s.replace('The mind is not a perfect witness.','medically cure your anxiety'));
 edit('merchant-article',P.article,s=>s+'\n[Buy now](https://hypnosislive.com/mental-skills/total-focus)');
 edit('fabricated-science',P.article,s=>s.replace('49 meta-analyses','49 guaranteed cures'));
 edit('remove-film-caveat',P.plan,s=>s.replace('does not construct an experimentally faithful','constructs an experimentally faithful'));
 edit('fabricate-revenue',P.plan,s=>s.replaceAll('NOT COMPUTABLE','SUCCESS'));
 edit('remove-video',P.video,s=>s.replace('<video','<div'));
 edit('remove-missing-binary-warning',P.plan,s=>s.replace('Binary and captions are not committed','Binary and captions are available online'));
 return cases;
}
if(require.main===module){
 const files=Object.fromEntries(Object.values(P).map(p=>[p,fs.readFileSync(path.resolve(process.cwd(),p),'utf8')]));
 const base=audit(files);if(base.length){console.error('BASELINE FAIL',base);process.exit(1)}
 const cases=mutationCases(files);let misses=0;for(const c of cases){if(audit(c.files).length===0){console.error('MISSED',c.label);misses++}}
 if(misses)process.exit(1);
 console.log('R292 bounded source baseline PASS; '+cases.length+'/'+cases.length+' deliberate mutations rejected; 18 gates HARD HOLD. Browser/merchant/hosted-video NOT TESTED.');
}
module.exports={P,audit,mutationCases};

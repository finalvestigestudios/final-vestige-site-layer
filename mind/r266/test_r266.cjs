// R266 primary-science and commerce evidence-source regression. Run from repo root: node mind/r266/test_r266.cjs
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const dir=__dirname,read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const files={article:read('THE-VOICE-THAT-COULD-NOT-TAKE-CONTROL-UNPUBLISHED.md'),matrix:JSON.parse(read('SELF-HYPNOSIS-CLAIMS-PRODUCT-PARTNER-REVENUE-HOLD.json')),plan:read('OFFER-FUNNEL-BLOCKER-CONVERSION-AND-GROK-ACCEPTANCE.md')};
const gates=['named_partner_acceptance','written_product_permission','approved_social_channels','approved_email_channel','issued_tracking_url','affiliate_terms','approved_creatives_rights','exact_active_offer','cart_total_verified','returns_terms_verified','fulfillment_verified','product_specific_claim_substantiation','independent_disclosure_qa','first_party_attribution_review','verified_paid_merchant_reporting','founder_release_approval'];
const critical={C04:'INDEPENDENT_TRIAL_NOT_PRODUCT',C05:'INDEPENDENT_TRIAL_NOT_PRODUCT',C06:'INDEPENDENT_REVIEW_LIMITED',C07:'INDEPENDENT_REVIEW_MIXED',C11:'SELLER_FEATURE_DELIVERY_NOT_AUDITED',C12:'SELLER_DISPLAY_NOT_VERIFIED_CART',C13:'PRODUCT_EFFICACY_UNSUBSTANTIATED_OMIT',C14:'PRODUCT_EFFICACY_UNSUBSTANTIATED_OMIT',C15:'PRODUCT_EFFICACY_UNSUBSTANTIATED_OMIT',C16:'REFUND_PERFORMANCE_UNVERIFIED',C17:'PARTNER_APPROVAL_NOT_AUTHENTICATED',C18:'PARTNER_LINK_PRICE_NOT_AUTHENTICATED',C19:'OWNED_SKU_RIGHTS_CHECKOUT_UNVERIFIED',C20:'FALSE_DO_NOT_INFER',C21:'FALSE_DO_NOT_INFER',C25:'DATA_MISSING_NOT_ZERO',C26:'FALSE_NOT_STUDIED_PRODUCT'};
const mustUnknown=['approved_partner_account','verified_partner_terms','affiliate_earning_url','approved_promotional_channels','verified_cart_price','verified_returns_execution','verified_paid_order_count','settled_affiliate_commissions','owned_mind_sku_rights','owned_mind_checkout','qualified_human_sessions','confirmed_leads','gross_revenue','refunds_and_fees','realized_net_revenue','realized_net_revenue_per_1000_qualified_sessions'];
function verify(f){
 const a=f.article,m=f.matrix,p=f.plan;
 assert(a.split(/\s+/).length>1700,'substantial independent investigation');
 for(const x of ['Puységur','magnetic somnambulism','250','53.4%','40.9%','70 studies','6,078','very low','44 included studies','No affiliate recommendation'])assert(a.includes(x),'source-specific article evidence: '+x);
 for(const id of ['41217756','39263007','37399315','31914365','PMC12233205'])assert(a.includes(id),'source citation retained '+id);
 assert(!/(zen12\.com|inspire3\.com|Hypnosis Live|Brainwave Shots|Zen12)/i.test(a),'no merchant placement in research');
 assert(!/\]\(https:\/\/(?:zen12|inspire3)/i.test(a),'no live merchant link');
 assert(m.status==='DRAFT_UNPUBLISHED_HARD_HOLD'&&m.product_focus.includes('Zen12'));
 assert.equal(m.sources.length,18);assert.equal(m.source_count,18);
 assert.equal(m.claims.length,26);assert.equal(m.claim_count,26);
 assert.equal(new Set(m.sources.map(s=>s.id)).size,18);
 assert.equal(new Set(m.claims.map(c=>c.id)).size,26);
 for(const s of m.sources)assert(/^https:\/\//.test(s.url)&&/^[A-Z][0-9]{2}$/.test(s.id),'source identity/url');
 const sourceIds=new Set(m.sources.map(s=>s.id));
 for(const c of m.claims)for(const id of c.source.split(';'))assert(sourceIds.has(id),'claim evidence link '+id);
 for(const [id,status] of Object.entries(critical))assert.equal(m.claims.find(c=>c.id===id)?.status,status,'critical claim bounded '+id);
 assert.deepEqual(m.gates.map(x=>x.id).sort(),[...gates].sort(),'exact gate names');
 for(const g of m.gates)assert(g.status==='HARD_HOLD'&&g.evidence===null,'no false partner authorization');
 assert.deepEqual(Object.keys(m.commerce).sort(),[...mustUnknown].sort(),'exact unknown commerce fields');
 for(const id of mustUnknown)assert.equal(m.commerce[id],null,'not compute/assume '+id);
 assert.equal(m.experiment.paid_conversion_outcome,null);
 assert.equal(m.experiment.activation,'BLOCKED');
 assert.equal(m.privacy.do_not_add_new_scripts,true);assert.equal(m.privacy.do_not_collect_email_or_IP_in_custom_events,true);assert.equal(m.privacy.do_not_emit_affiliate_click_before_partner_approval,true);
 assert.equal(m.privacy.utm_medium,'organic_social');assert.equal(m.privacy.utm_content,'actual_verified_asset_id');
 for(const k of ['live_CMS_writes','merge','deploy','email_send','creator_post','spend'])assert.equal(m.boundary[k],false,'release hold '+k);
 for(const term of ['OFFER','Focus','affiliate_outbound','merchant_confirmed_order','NOT COMPUTABLE','HARD_HOLD','NO MATCH','refunds','Draft','Claude','Praxxis','Grok','Founder'])assert(p.toLowerCase().includes(term.toLowerCase()),'plan requirement '+term);
 assert(!/we earned \$|commission cleared: \$|paid orders [1-9]/i.test(p));
 return true;
}
verify(files);
const mutations=[
 ['paid orders',f=>f.matrix.commerce.verified_paid_order_count=3],
 ['false gross revenue',f=>f.matrix.commerce.gross_revenue=350],
 ['false approved publisher',f=>f.matrix.commerce.approved_partner_account=true],
 ['invented earning link',f=>f.matrix.commerce.affiliate_earning_url='https://seller.example/aff'],
 ['fake net 1000',f=>f.matrix.commerce.realized_net_revenue_per_1000_qualified_sessions=20],
 ['fake net income',f=>f.matrix.commerce.realized_net_revenue=35],
 ['faked commission',f=>f.matrix.commerce.settled_affiliate_commissions=40],
 ['faked email leads',f=>f.matrix.commerce.confirmed_leads=200],
 ['faked sessions',f=>f.matrix.commerce.qualified_human_sessions=2000],
 ['missing gate',f=>f.matrix.gates.pop()],
 ['duplicate gate',f=>f.matrix.gates[1].id=f.matrix.gates[0].id],
 ['alter gate name',f=>f.matrix.gates[1].id='fake_permission'],
 ['approve gate',f=>f.matrix.gates[1].status='APPROVED'],
 ['give unverified proof',f=>f.matrix.gates[1].evidence='yes'],
 ['sell unsupported product efficacy',f=>f.matrix.claims.find(c=>c.id==='C13').status='INDEPENDENTLY_VERIFIED'],
 ['prove hypnosis seller guarantee',f=>f.matrix.claims.find(c=>c.id==='C14').status='SUPPORTED'],
 ['falsify refund evidence',f=>f.matrix.claims.find(c=>c.id==='C16').status='PROVEN'],
 ['invent first party paid SKU',f=>f.matrix.claims.find(c=>c.id==='C19').status='VERIFIED_PAID'],
 ['mistake outbound for conversion',f=>f.matrix.claims.find(c=>c.id==='C20').status='TRUE'],
 ['change specific trial claim',f=>f.matrix.claims.find(c=>c.id==='C04').status='ZEN12_PROOF'],
 ['source missing',f=>f.matrix.claims[0].source='S99'],
 ['duplicate scientific claim ID',f=>f.matrix.claims[1].id='C01'],
 ['change source protocol',f=>f.matrix.sources[0].url='http://notsecure.invalid'],
 ['allow analytics',f=>f.matrix.privacy.do_not_add_new_scripts=false],
 ['allow visitor PII',f=>f.matrix.privacy.do_not_collect_email_or_IP_in_custom_events=false],
 ['allow premature click event',f=>f.matrix.privacy.do_not_emit_affiliate_click_before_partner_approval=false],
 ['change UTM asset identity',f=>f.matrix.privacy.utm_content='random_id'],
 ['activate experiment',f=>f.matrix.experiment.activation='ACTIVE'],
 ['pretend paid outcome',f=>f.matrix.experiment.paid_conversion_outcome=10],
 ['permit CMS',f=>f.matrix.boundary.live_CMS_writes=true],
 ['permit merge',f=>f.matrix.boundary.merge=true],
 ['permit deployment',f=>f.matrix.boundary.deploy=true],
 ['permit email send',f=>f.matrix.boundary.email_send=true],
 ['permit creator post',f=>f.matrix.boundary.creator_post=true],
 ['permit spend',f=>f.matrix.boundary.spend=true],
 ['remove key trial',f=>f.article=f.article.replace('53.4%','different')],
 ['inject product placement',f=>f.article+='\nZen12 promises perfect concentration.'],
 ['remove evidence citation',f=>f.article=f.article.replace('https://pubmed.ncbi.nlm.nih.gov/41217756/','invalid-reference')],
 ['fabricate revenue in plan',f=>f.plan+='\nCommission cleared: $300'],
 ['delete attribution guard',f=>f.plan=f.plan.replaceAll('affiliate_outbound','affiliate_click_only')],
 ['delete human caveat',f=>f.plan=f.plan.replaceAll('NOT COMPUTABLE','zero dollars')]
];
let rejected=0;
for(const [name,mutate] of mutations){
 const f=JSON.parse(JSON.stringify(files)),before=JSON.stringify(f);mutate(f);
 assert.notEqual(JSON.stringify(f),before,'mutation must change file: '+name);
 try{verify(f)}catch(e){rejected++;continue}
 throw Error('FAILED TO REJECT: '+name);
}
console.log('R266: baseline PASS; '+rejected+'/'+mutations.length+' deliberately unsafe effective edits rejected; source-level only, not native browser/WP/merchant certification.');

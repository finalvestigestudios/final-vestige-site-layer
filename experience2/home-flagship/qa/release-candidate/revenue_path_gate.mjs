/**
 * FV homepage commercial-route admission. Read-only local offline evaluation.
 * Does NOT assert merchant acceptance, paid orders, affiliate attribution or site
 * accessibility. No remote fetches, cookies, tracking scripts or contact data.
 *
 *   node revenue_path_gate.mjs home-public.html collection-public.html focus-public.html
 * Only PUBLIC HTML; do not export WordPress users, subscriber data, or secrets.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const OWNED_MERCHANTS=new Set(['payhip.com','www.payhip.com']);
const AFFILIATE_DOMAINS=new Set(['awin1.com','www.awin1.com']);
const TRACKING_KEYS=['utm_source','utm_medium','utm_campaign','utm_content'];
const MAX_INPUT=2_000_000;

function decodeEntities(s) {
  return String(s).replace(/&(?:amp|#0*38|#x0*26);/gi,'&')
    .replace(/&quot;/gi,'"').replace(/&#0*39;/gi,"'")
    .replace(/&#x0*27;/gi,"'");
}
export function extractLinks(html) {
  const links=[];
  const a=/<a\b([^>]*)>([\s\S]*?)<\/a\s*>/gi;
  for (const match of html.matchAll(a)) {
    const attrs=match[1];
    const href=attrs.match(/(?:^|\s)href\s*=\s*(["'])(.*?)\1/i);
    if(!href)continue;
    links.push({href:decodeEntities(href[2]),
      label:decodeEntities(match[2].replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim(),
      hasDisclosure:/\b(?:ad|sponsored|affiliate|commission)\b/i.test(match[2])});
  }
  return links;
}
export function classifyLink(href) {
  let u;
  try {u=new URL(decodeEntities(href), 'https://finalvestige.com/');}
  catch {return {type:'invalid'};}
  if(!['https:','http:'].includes(u.protocol))return {type:'invalid'};
  const hostname=u.hostname.toLowerCase();
  if(AFFILIATE_DOMAINS.has(hostname)||/(?:^|\.)awin1\.com$/.test(hostname))return {type:'affiliate_outbound'};
  if(OWNED_MERCHANTS.has(hostname))return {type:'potential_owned_checkout'};
  if(hostname==='finalvestige.com'||hostname==='www.finalvestige.com') {
    const route=u.pathname.replace(/\/+$/,'')||'/';
    if(['/focus','/dispatch'].includes(route))return {type:'lead_destination'};
    if(['/collection','/shop','/editions'].includes(route))return {type:'catalog_navigation'};
    return {type:'editorial_or_navigation'};
  }
  return {type:'other_external'};
}
export function commercialRouteReceipt(homeHtml,collectionHtml,focusHtml,metadata={}){
  for(const h of [homeHtml,collectionHtml,focusHtml]){
    if(typeof h!=='string'||h.length>MAX_INPUT)throw new Error('invalid public HTML input size');
  }
  const home=extractLinks(homeHtml), collection=extractLinks(collectionHtml);
  const focus=extractLinks(focusHtml);
  const summarize=arr=>arr.reduce((acc,l)=>{
    const t=classifyLink(l.href).type;
    acc[t]=(acc[t]||0)+1;return acc;
  },{});
  const hc=summarize(home),cc=summarize(collection);
  const focusHasOffer=/Seven Day Focus Fieldbook/i.test(focusHtml);
  const focusHasSubscribe=/jetpack-subscriptions|wp-block-jetpack-subscriptions/i.test(focusHtml);
  const ownedCatalogLinks=collection.filter(l=>classifyLink(l.href).type==='potential_owned_checkout');
  const affiliate=collection.filter(l=>classifyLink(l.href).type==='affiliate_outbound');
  const flags={
    published_home_to_focus:(hc.lead_destination||0)>0,
    published_collection_to_focus:(cc.lead_destination||0)>0,
    focus_landing_source_offer_present:focusHasOffer,
    focus_landing_form_markup_present:focusHasSubscribe,
    owned_paid_catalog_destination_present:ownedCatalogLinks.length>0,
    affiliate_outbound_present:affiliate.length>0,
  };
  const status=flags.owned_paid_catalog_destination_present?'MERCHANT_CHECK_REQUIRED':'OWNED_REVENUE_ROUTE_NOT_EXPOSED';
  return {
    schema:'FV-EX2-REVENUE-ROUTE-20261105',
    publicationSnapshot:metadata,
    status,
    counts:{homepage:hc,collection:cc,focus:summarize(focus)},
    flags,
    distinctOwnedCheckoutDestinations:[...new Set(ownedCatalogLinks.map(l=>new URL(l.href).hostname))],
    commercialEvidence:{paidOrders:'NOT_CHECKED',merchantAcceptance:'NOT_CHECKED',
      affiliateSales:'NOT_CHECKED',realizedNetRevenue:'NOT_CHECKED',
      qualifiedHumanSessions:'NOT_CHECKED',netRevenuePer1000QualifiedSessions:'NOT_MEASURABLE'},
    note:'A merchant link is not a verified checkout or sale. A confirmed subscriber is not a paid customer. CTA and source presence do not establish visitor-visible accessibility.',
  };
}
const directlyRun=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(directlyRun){
  if(process.argv.length!==5){console.error('usage: node revenue_path_gate.mjs home-public.html collection-public.html focus-public.html');process.exit(2)}
  const files=process.argv.slice(2).map(p=>fs.readFileSync(p,'utf8'));
  const r=commercialRouteReceipt(...files,{kind:'user-supplied public-only snapshot; time not independently certified'});
  console.log(JSON.stringify(r,null,2));
  if(r.status!=='MERCHANT_CHECK_REQUIRED')process.exitCode=2;
}

import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

// Run from the repository root: node mind/r431/verify.mjs
// No network, no paid calls, no CMS changes and no tracking.
function check() {
  const dir = process.cwd() + '/mind/r431/';
  const read = n => readFileSync(dir + n, 'utf8');
  const a = read('ZEN12_A_TEXT_GUIDE.html');
  const b = read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
  const hub = read('MIND_HUB_WP_SOURCE_ONLY.html');
  const art = read('THE_GLASS_THAT_WAS_NEVER_THERE.md');
  const vtt = read('ZEN12_OPTIONAL_42S_CAPTIONS.vtt');
  const svg = read('ZEN12_OPTIONAL_42S_POSTER.svg');
  const matrix = JSON.parse(read('CLAIM_SOURCE_PARTNER_GATE_MATRIX.json'));
  const dossier = read('OFFER_FUNNEL_CREATOR_AND_REVENUE_ACCEPTANCE.md');
  let checks = 0;
  function ok(x, message) {assert.ok(x, message); checks++;}
  function no(x, message) {assert.ok(!x, message); checks++;}
  ok(art.trim().split(/\s+/).length >= 2400,'substantive original article');
  for (const term of ['Loftus','Palmer','broken glass','suggest','Puységur','2024','JAMA','free','uncertain']) ok(art.includes(term),'article research '+term);
  ok((art.match(/https:\/\//g)||[]).length>=13,'article source trail');
  no(/Zen12 (is proven|cures|guarantees)/i.test(art),'no invented efficacy');
  ok(a.includes('<!doctype html>') && b.includes('<!doctype html>'),'both document variants');
  ok(a.includes('lang="en"') && b.includes('lang="en"'),'HTML language');
  ok(a.includes('width=device-width') && b.includes('width=device-width'),'mobile viewport');
  ok(a.includes('noindex,nofollow') && b.includes('noindex,nofollow'),'unpublished noindex');
  ok(a.includes('reduced-motion') && b.includes('reduced-motion'),'reduced motion');
  ok(a.includes(':focus-visible') && b.includes(':focus-visible'),'keyboard focus');
  const guide = s => s.slice(s.indexOf('<section id="overview">'), s.indexOf('</main>'));
  ok(guide(a) === guide(b),'A/B buyer copy equal');
  ok(guide(a).length > 5000,'fully written buyer guide');
  ok(b.includes('42-second') && b.includes('00–07:') && b.includes('35–42:'),'timed concept');
  ok(b.includes('<details>') && b.includes('<summary>'),'no-JS transcript');
  ok(b.includes('ZEN12_OPTIONAL_42S_POSTER.svg'),'local poster');
  ok(!a.includes('ZEN12_OPTIONAL_42S_POSTER.svg'),'A is text-only');
  for(const [name,s] of [['A',a],['B',b],['hub',hub]]) {
    no(/<script\b/i.test(s),name+' no JS');
    no(/<iframe\b/i.test(s),name+' no embed');
    no(/<form\b/i.test(s),name+' no extra subscription form');
    no(/(?:href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com))/i.test(s),name+' no merchant product/affiliate href');
    no(/\b(?:onload|onclick|onerror)\s*=/i.test(s),name+' no inline JS handlers');
    no(/(?:<video[^>]+autoplay|<audio[^>]+autoplay)/i.test(s),name+' no forced media');
  }
  for(const s of [a,b,hub]) {
    ok(s.includes('If a verified, authorized earning link is added'),'adjacent prospective disclosure');
    ok(s.includes('No affiliate link is active here.'),'no sale link');
    ok(s.includes('Commercial link withheld') || s.includes('Purchase link withheld'),'hold status');
  }
  no(/<video/i.test(b),'no non-functional empty video player');
  ok(svg.includes('<svg') && svg.includes('role="img"'),'SVG accessibility');
  no(/<script|https?:\/\//i.test(svg.replace('http://www.w3.org/2000/svg','')),'SVG local and script free');
  ok(vtt.startsWith('WEBVTT'),'caption format');
  ok((vtt.match(/-->/g)||[]).length === 6,'exact 6 caption cues');
  ok(vtt.includes('00:00:00.000 --> 00:00:07.000'),'starts at zero');
  ok(vtt.includes('00:00:35.000 --> 00:00:42.000'),'ends at 42 sec');
  ok(matrix.claims.length>=30,'source matrix depth');
  ok(Object.keys(matrix.sources).length>=18,'source inventory depth');
  ok(matrix.gates.length===28,'release gate completeness');
  ok(matrix.gates.every(g=>g.status==='HOLD' && g.proof===null),'all gates closed');
  ok(matrix.claims.every(c=>c.sources.every(s=>/^https:\/\//.test(s.url))),'every claim source URL valid');
  ok(matrix.claims.some(c=>c.status==='NOT_VERIFIED'),'missing partner proof clearly stated');
  ok(matrix.claims.some(c=>c.status==='NOT_COMPUTABLE'),'net KPI not invented');
  ok(hub.includes('Perception &amp; Attention') && hub.includes('History of Suggestion'),'hub taxonomy');
  ok(hub.includes('puysegurs-animal-magnetism-files') && hub.includes('finalvestige.com/focus/'),'existing site bridges');
  ok(dossier.includes('NOT COMPUTABLE') || dossier.includes('NOT_COMPUTABLE'),'revenue cannot be guessed');
  ok(dossier.includes('Claude') && dossier.includes('Praxxis') && dossier.includes('Grok'),'ownership');
  ok(dossier.includes('UNMATCHED'),'genuine social IDs required');
  ok(dossier.includes('merchant_confirmed_paid_order') && dossier.includes('affiliate_outbound'),'click versus money');

  // Attack cases: guards are deliberately concise source-surface checks, not a substitute for browser/CMS security review.
  const unsafe = s => /<script\b|<iframe\b|<form\b|\b(?:onload|onclick|onerror)\s*=|(?:href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com))|(?:<video[^>]+autoplay|<audio[^>]+autoplay)|(?:pixel\.example\.com)|(?:guaranteed to cure|clinically proven to rewire)|(?:Your purchase is complete)/i.test(s);
  const attacks=[
    '<script src="https://pixel.example.com/t.js"></script>',
    '<iframe src="https://zen12.com/"></iframe>',
    '<form action="/subscribe"></form>',
    '<a href="https://zen12.com/getstarted">Buy</a>',
    '<a href="https://affiliates.inspire3.com/special">affiliate</a>',
    '<div onclick="sendData()">bad</div>',
    '<img onerror="sendData()">',
    '<video autoplay controls></video>',
    '<p>guaranteed to cure anxiety</p>',
    '<p>Your purchase is complete</p>'
  ];
  attacks.forEach((x,i)=>{ok(unsafe(x),'unsafe mutation '+i+' rejected');});
  no(unsafe(a),'baseline A clean');
  no(unsafe(b),'baseline B clean');
  no(unsafe(hub),'baseline hub clean');
  return {passed:checks, attacks:attacks.length, evidence:'exact files on local checkout; source static only'};
}
const result = check();
console.log(JSON.stringify(result));

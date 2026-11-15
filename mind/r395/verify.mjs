// FV Mind R395 exact-file offline QA. Run from repo root:
//   node mind/r395/verify.mjs
// No external network, dependencies, PII, browser, CMS or merchant access.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';

const dir=dirname(fileURLToPath(import.meta.url));
const read=(name)=>readFileSync(join(dir,name),'utf8');
const a=read('ZEN12_A_TEXT_GUIDE.html');
const b=read('ZEN12_B_OPTIONAL_FILM.html');
const vtt=read('CHOICE_BLINDNESS_42S.vtt');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const story=read('THE_JAM_YOU_DIDNT_CHOOSE.md');
const claims=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
const dossier=read('CONVERSION_ACCEPTANCE_CREATOR_ROUTING.md');
let passed=0;
function check(label,condition){assert.ok(condition,label);passed++;console.log('PASS '+label);}

function presellPolicy(html){
  const banned=[
    /<script\b/i, /<form\b/i, /<iframe\b/i,
    /\b(?:autoplay|onload|onclick)\s*=/i,
    /href\s*=\s*["']https:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i,
    /\b(?:gtag|fbq|dataLayer|document\.cookie)\b/i,
    /<a[^>]+(?:affiliate|tracking|go\/buy)/i,
    /guaranteed (?:cure|intelligence|wealth)/i
  ];
  return banned.every(x=>!x.test(html)) && /<button[^>]*\bdisabled\b/.test(html) &&
    /Potential|Prospective affiliate disclosure/i.test(html) &&
    html.includes('https://finalvestige.com/focus/') &&
    !/<video\b/i.test(html);
}
check('presell A commercial and security hold',presellPolicy(a));
check('presell B commercial and security hold',presellPolicy(b));
check('A and B identical core buyer markup', b.replace(/<details class="film"[\s\S]*?<\/details>/,'<!-- OPTIONAL_FILM_INSERT -->')===a);
check('B includes original accessible SVG',b.includes('role="img"') && b.includes('aria-labelledby="r395Title r395Desc"'));
check('B optional film requires conscious expand',b.includes('<details class="film"'));
check('B explicitly says storyboard not playable',b.includes('not encoded, playable or published'));
check('both presell pages disclose no approved merchant link',a.includes('HARD HOLD') && b.includes('HARD HOLD'));
check('price discrepancy qualified',a.includes('$87.99') && a.includes('$37') && a.includes('Neither is a verified Final Vestige referred price'));
check('no personal efficacy claim',!a.includes('I used Zen12') && !b.includes('we tested Zen12'));
check('no active external media', !/<(?:video|audio|source|embed|iframe)\b/i.test(a+b));
check('consumer baseline and free path',a.includes('free twelve-minute baseline') && a.includes('52-page Seven Day Focus Fieldbook'));
check('hub has four streams and no scripts/forms', ['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].every(x=>hub.includes(x)) && !/<script|<form/i.test(hub));
check('hub never asserts published Mind route',hub.includes('not a saved WordPress draft'));
check('research originality substantial',story.trim().split(/\s+/).length>=2200);
check('research includes science provenance', ['10.1126/science.1111709','10.1016/j.cognition.2010.06.010','10.1371/journal.pone.0060554'].every(x=>story.includes(x)));
check('research respects Puységur 429',story.includes('rate-limited') && story.includes('does not quote'));
check('evidence matrix has >35 classified claims',claims.claims.length>=35 && claims.claims.every(x=>x.id&&x.decision&&x.classification));
check('evidence matrix includes official sources and FTC',claims.source_links.standard.includes('zen12.com') && claims.source_links.ftc.includes('ftc.gov'));
check('all commercial gates are closed',claims.release_gates.length>=10 && claims.release_gates.every(x=>x.passed===false));
check('owned paid fallback not invented',claims.claims.some(x=>x.claim.includes('Owned sellable FV Mind') && x.decision==='HOLD'));
check('campaign IDs not fabricated',dossier.includes('None authenticated here') && dossier.includes('asset_id'));
check('clicks and paid conversions separated',dossier.includes('affiliate_click') && dossier.includes('partner_reported_paid_conversion'));
check('net KPI and 7/30 day cohorts',dossier.includes('7-day') && dossier.includes('30-day') && dossier.includes('NOT COMPUTABLE'));
check('privacy and explicit consent contract',dossier.includes('PII') && dossier.includes('consent') && dossier.includes('no deployed code'));
check('VTT header and six cues',vtt.startsWith('WEBVTT') && (vtt.match(/ --> /g)||[]).length===6);
const capLines=vtt.split(/\n+/).filter(x=>x && !/^WEBVTT$/.test(x) && !/^\d+$/.test(x) && !/ --> /.test(x));
const spoken=(b.match(/Transcript of proposed 42-second voiceover:<\/strong>\s*([^<]+)<\/p>/)||[])[1];
check('six caption lines exactly match proposed transcript',capLines.join(' ')===spoken);
check('caption times begin zero and end 42 seconds',vtt.includes('00:00:00.000 --> 00:00:07.000') && vtt.includes('00:00:35.000 --> 00:00:42.000'));

// Adversarial fixtures: the validator must reject blocked variants, not just certify safe originals.
const mutations=[
 ['live purchase URL',a.replace('<!-- OPTIONAL_FILM_INSERT -->','<a href="https://zen12.com/getstarted">Buy</a>')],
 ['script injection',a+'<script>alert(1)</script>'],
 ['new signup form',a+'<form><input name="email"></form>'],
 ['onclick tracker',a.replace('disabled aria-describedby','onclick="track()" aria-describedby')],
 ['active purchase button',a.replace('class="inactive" disabled','class="inactive"')],
 ['auto video playback',a+'<video autoplay controls></video>'],
 ['third party iframe',a+'<iframe src="https://example.org"></iframe>'],
 ['fake cure promise',a+'<p>guaranteed cure</p>'],
 ['bad proprietary tracker',a+'<script>gtag()</script>']
];
for(const [name,mutated] of mutations){check('reject mutation: '+name,!presellPolicy(mutated));}
console.log('FINISHED '+passed+' checks; no real browser, WordPress, video playback, Jetpack or merchant transaction executed.');

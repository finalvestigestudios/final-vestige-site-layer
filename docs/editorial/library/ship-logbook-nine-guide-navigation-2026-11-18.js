// Final Vestige Studios — The Log Was Not the Voyage
// Nine-guide reader navigation, source of truth for WordPress pages 2886–2894.
// Prepared 2026-11-18. Draft-only. Do not merge or publish until QA + notification gates pass.
// Original FV CSS layout; no borrowed media, JS runtime, external dependency or tracking.
// Each output is one Gutenberg core/html block. Article modules remain unchanged.
// IMPORTANT: sibling URLs remain 404 to anonymous readers until individual publication.
// Source references: https://www.archives.gov/research/military/logbooks/naval-deck-logs
// https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs
// Site policy: https://finalvestige.com/editorial-standards/
// Relative links are intended to resolve from published child pages at /free-resources/.
const ITEMS=[
  [
    2886,
    "Find the logbook",
    "Identify the vessel and custodial archive.",
    "ship-logbook-archive-route"
  ],
  [
    2887,
    "When a log is missing",
    "Separate a search failure from an event claim.",
    "ship-logbook-missing-record"
  ],
  [
    2888,
    "Which ship?",
    "Check hull numbers and reused names.",
    "ship-logbook-vessel-identity"
  ],
  [
    2889,
    "Read the page",
    "Title, remarks and observations have different purposes.",
    "ship-logbook-page-anatomy"
  ],
  [
    2890,
    "Find the sailor",
    "Read musters without inventing presence.",
    "ship-logbook-crew-identity"
  ],
  [
    2891,
    "Plot uncertainty",
    "Coordinates are not a proven track.",
    "ship-logbook-position-track"
  ],
  [
    2892,
    "Date the port call",
    "Arrival and customs entry may disagree.",
    "ship-logbook-port-dates"
  ],
  [
    2893,
    "Follow the warning",
    "Receipt is not a delivery receipt.",
    "ship-logbook-message-chain"
  ],
  [
    2894,
    "Read the correction",
    "A strike-through needs its own evidence.",
    "ship-logbook-correction-chain"
  ]
];
function buildNav(id){
  const selector=`#fv-log-series-${id}`;
  const rules=[
  `{color:#25332e;margin:clamp(28px,5vw,64px) auto;max-width:1040px;overflow-wrap:anywhere;font:inherit}`,
  ` *{box-sizing:border-box}`,
  ` .intro{border-top:3px solid #8a6538;padding:18px 0 9px}`,
  ` h2{font:normal clamp(1.55rem,3vw,2.15rem)/1.22 Georgia,serif;color:#25332e;margin:0 0 .55em}`,
  ` p{line-height:1.65;max-width:74ch}`,
  ` ol{list-style:none;padding:0;margin:1rem 0 1.3rem;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}`,
  ` li{min-width:0}`,
  ` a, .here{display:block;min-height:102px;background:#f7f6f0;border:1px solid #b7bcb2;border-radius:5px;padding:14px;color:#25332e;text-decoration:none;overflow-wrap:anywhere}`,
  ` a:hover{border-color:#755322;background:#ece7d8}`,
  ` a:focus-visible{outline:3px solid #8b5b17;outline-offset:3px}`,
  ` .here{background:#e5ece2;border:2px solid #4c7156}`,
  ` strong{display:block;font-size:1rem;line-height:1.4}`,
  ` .num{color:#755322;font-variant-numeric:tabular-nums;margin-right:.45rem}`,
  ` small{display:block;font-size:.86rem;line-height:1.5;color:#435249;margin-top:.5rem}`,
  ` em{display:inline-block;margin-top:.5rem;color:#28533b;font-size:.76rem;font-style:normal;font-weight:700}`,
  ` .foot{font-size:.85rem;border-top:1px solid #b7bcb2;padding-top:10px;color:#49584d}`,
  ` .foot a{display:inline;padding:0;min-height:0;border:0;background:transparent;text-decoration:underline;color:#345d4e}`
  ];
  const css=rules.map((r,i)=>`${selector}${r.startsWith('{')?'': ''}${r}`).join('')+`@media(max-width:820px){${selector} ol{grid-template-columns:repeat(2,minmax(0,1fr))}}`+`@media(max-width:560px){${selector} ol{grid-template-columns:1fr}${selector} a,${selector} .here{min-height:74px;padding:13px}}`+`@media print{${selector} ol{display:block;columns:2}${selector} li{break-inside:avoid;margin:0 0 8px}${selector} a,${selector} .here{min-height:0;background:#fff;color:#000;border:1px solid #aaa}}`;
  const entries=ITEMS.map(([itemId,title,desc,slug],i)=>`<li>${id===itemId?`<span class="here" aria-current="page"><strong><span class="num">${String(i+1).padStart(2,'0')}</span> ${title}</strong><small>${desc}</small><em>Current field guide</em></span>`:`<a href="/free-resources/${slug}/"><strong><span class="num">${String(i+1).padStart(2,'0')}</span> ${title}</strong><small>${desc}</small></a>`}</li>`).join('\n');
  return `<!-- wp:html -->\n<nav id="fv-log-series-${id}" aria-label="Nine historical ship-logbook research guides">\n<style>${css}</style>\n<div class="intro"><h2>One voyage. Several kinds of witness.</h2><p>A vessel's name, its log, a crew list, a port entry, a wireless report: each can preserve a different piece of the record. Follow the kind of evidence you need, and keep its limits in view.</p></div>\n<ol>\n${entries}\n</ol>\n<p class="foot">This is a research index, not a plotted voyage. Individual guides open only after their source and accessibility checks are cleared. <a href="/the-archive-trail/">The Archive Trail</a> describes our method; <a href="/editorial-standards/">Editorial Standards</a> covers sources, rights and corrections. Last reviewed: November 18, 2026.</p>\n</nav>\n<!-- /wp:html -->`;
}

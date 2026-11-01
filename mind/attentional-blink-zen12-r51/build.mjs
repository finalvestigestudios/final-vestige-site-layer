// Source-controlled OFFLINE generator for unpublished R51 WordPress candidates. Node 20+, no packages.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const dir=dirname(fileURLToPath(import.meta.url));
const core=readFileSync(join(dir,'zen12-guide-core.html'),'utf8');
const css=readFileSync(join(dir,'pilot.css'),'utf8');
const transcript=[
  'Two numbers. One fast stream of letters.',
  'You report the first. The second arrives soon after.',
  'The report can fail—even while the stimulus was presented.',
  'And immediately consecutive targets can sometimes escape the gap.',
  'Three months of intensive meditation training is not a consumer audio trial.',
  'What was measured? What was inferred? Follow the evidence.'
];
const captionContent='<details><summary>Read the complete film transcript</summary><div class="fv51-transcript"><ol>'+transcript.map(x=>'<li>'+x+'</li>').join('')+'</ol><p>This is an original conceptual educational film, not an actual attentional-blink experiment or a Zen12 efficacy demonstration.</p></div></details>';
const webFilm='<figure class="fv51-film" data-variant-element="optional-film" aria-labelledby="fv51-film-title"><h2 id="fv51-film-title">Watch the distinction between a finding and a promise</h2><div class="fv51-frame" role="img" aria-label="Original poster: a bright 7 followed by a muted 4 within a stream of letters; schematic illustration of attentional blink, not a true vision test"><span>THE SECOND NUMBER</span><strong>7 <i>→</i> 4</strong><span>40 SECONDS · AN ORIGINAL EVIDENCE NOTE</span></div><figcaption>Optional 40-second original film is available in the offline reviewer package. First-party hosting and captions are not yet approved for the live site, so this unpublished WordPress draft deliberately has no play button.</figcaption>'+captionContent+'</figure>';
const offlineFilm='<figure class="fv51-film" data-variant-element="optional-film" aria-labelledby="fv51-film-title"><h2 id="fv51-film-title">Watch the distinction between a finding and a promise</h2><video controls playsinline preload="none" width="540" height="960" poster="film-poster.svg" aria-label="The Second Number — optional silent 40-second research explainer"><source src="film-40s.mp4" type="video/mp4"><track src="film-captions.vtt" kind="captions" srclang="en" label="English" default>Your browser does not support this video; read the transcript below.</video><figcaption>Original silent captioned educational film. Not an experiment or a merchant endorsement.</figcaption>'+captionContent+'</figure>';
const insertAt='<section aria-labelledby="fv51-problem">';
if(!core.includes(insertAt)) throw new Error('missing stable film insertion anchor');
const frameExtra='.fv51-pilot .fv51-frame{aspect-ratio:9/12;max-width:400px;margin:14px auto;padding:25px;background:radial-gradient(ellipse at 50% 30%,#323027,#0b0c0d 65%);border:1px solid #8a7049;display:flex;flex-direction:column;align-items:center;justify-content:space-around;text-align:center;color:#e7d4ae;}.fv51-pilot .fv51-frame span{font-size:.72rem;letter-spacing:.18em}.fv51-pilot .fv51-frame strong{font:400 clamp(4rem,15vw,7rem)/1 Georgia,serif}.fv51-pilot .fv51-frame i{font-size:.45em;color:#a99e8a;font-style:normal}';
function make(variant, offline=false){
  const guide=(variant==='B')?core.replace(insertAt,(offline?offlineFilm:webFilm)+insertAt):core;
  const nav='<a class="fv51-skip" href="#fv51-guide-title">Skip to the guide</a><nav class="fv51-nav" aria-label="Context and source navigation"><strong>FINAL VESTIGE / MIND</strong><a href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/">Historical evidence archive</a><a href="https://finalvestige.com/focus/">Free Focus Fieldbook</a></nav>';
  const footer='<footer class="fv51-bottom"><p>UNPUBLISHED DESIGN CANDIDATE · editorial evidence and offer permissions still under review. No endorsement, live affiliate link, visitor telemetry, purchase processing or extra newsletter form.</p></footer>';
  return '<!-- UNPUBLISHED ' + (offline?'OFFLINE VIDEO PREVIEW':'WORDPRESS SOURCE DRAFT') + ' / R51 / variant '+variant+'; release HARD HOLD -->\n<section class="fv51-pilot" data-variant="'+variant+'"><style>\n'+css+'\n'+frameExtra+'\n</style>'+nav+'<main id="fv51-main">'+guide+'</main>'+footer+'</section>\n';
}
const outputs={'zen12-a-wordpress-draft.html':make('A'),'zen12-b-wordpress-draft.html':make('B'),'offline-b-with-real-video.html':make('B',true)};
for(const [f,c] of Object.entries(outputs)){writeFileSync(join(dir,f),c,'utf8'); console.log(f,c.length);}

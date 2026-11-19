<?php
/** R457 Apollo provenance gallery: staging-only; read-only source catalogue, not imagery rights clearance. */
declare(strict_types=1);
require_once __DIR__.'/evidence_plates.php';
function fv457_records(): array {
  return [
    ['id'=>'S66-58038','source_status'=>'accepted','credit'=>'NASA / JSC (producer)','date'=>'1966-10-18','precision'=>'day','date_label'=>'18 October 1966','role'=>'Crew training context','shown'=>true,'source_url'=>'https://www.nasa.gov/image-detail/amf-s66-58038/','source_check'=>'Direct NASA image-detail record independently checked on 18 November 2026; source availability does not establish marketing rights.','boundary'=>'Training photograph. Does not depict the Apollo 1 accident.'],
    ['id'=>'S67-15717','source_status'=>'accepted','credit'=>'NASA / JSC (producer)','date'=>'1967-01-03','precision'=>'day','date_label'=>'3 January 1967','role'=>'Spacecraft preparations','shown'=>true,'source_url'=>'https://www.nasa.gov/image-detail/amf-s67-15717/','source_check'=>'Direct NASA image-detail record independently checked on 18 November 2026; source availability does not establish marketing rights.','boundary'=>'Pre-fire spacecraft context. Not a photograph of the ignition.'],
    ['id'=>'S67-19766','source_status'=>'id_hold','credit'=>'NASA image article; archive ID association unverified','date'=>'1967-01','precision'=>'month','date_label'=>'January 1967 (day not established here)','role'=>'Crew context','shown'=>false,'homepage_confirmed'=>true,'source_url'=>'https://www.nasa.gov/image-detail/apollo-1-crew-honored/','source_check'=>'NASA crew portrait article independently located; association of that image with archival ID S67-19766 is not confirmed.','boundary'=>'Do not infer an exact day from an approximate archive date.'],
    ['id'=>'S67-21294','source_status'=>'accepted','credit'=>'NASA / JSC (producer)','date'=>'1967-01-28','precision'=>'day','date_label'=>'28 January 1967','role'=>'Aftermath documentation','shown'=>false,'source_url'=>'https://www.nasa.gov/image-detail/amf-s67-21294/','source_check'=>'Direct NASA image-detail record independently checked on 18 November 2026; source availability does not establish marketing rights.','boundary'=>'Post-fire image withheld from this experience; do not confuse aftermath with the fire sequence.'],
    ['id'=>'KSC-20170124-PH_KLS01_0129','source_status'=>'catalogue_hold','credit'=>'No attributable image credit independently verified','date'=>'unverified','precision'=>'unverified','date_label'=>'Date not independently verified (2017-01-24 appears only in the candidate identifier)','role'=>'Retrospective hatch exhibit','shown'=>true,'source_url'=>'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129','source_check'=>'Candidate images.nasa.gov lookup could not be independently retrieved on 18 November 2026. Do not interpret URL, date or image identity as verified; hold editorial acceptance.','boundary'=>'The candidate ID implies a 2017 museum image, but its identity, date, and credit remain unverified. It must not be treated as a 1967 scene.'],
    ['id'=>'KSC-20170124-PH_KLS01_0090','source_status'=>'accepted','credit'=>'NASA / Kim Shiflett; KSC (producer)','date'=>'2017-01-24','precision'=>'day','date_label'=>'24 January 2017','role'=>'Retrospective exhibit context','shown'=>false,'source_url'=>'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','source_check'=>'Direct NASA image-detail record independently checked on 18 November 2026; source availability does not establish marketing rights.','boundary'=>'2017 exhibit photograph, not evidence of the ignition source.'],
  ];
}
function fv457_h(string $x): string {return htmlspecialchars($x, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');}
/** Break long visible source addresses without modifying a link's actual href. */
function fv457_url_label(string $url): string {return str_replace(['/', '-', '_'], ['/<wbr>', '-<wbr>', '_<wbr>'], fv457_h($url));}

/** R463 evidence chronology: event time != later source publication or exhibit photography. */
function fv457_chronology(): array {
 return [
  ['date'=>'January 1967','machine_date'=>'1967-01','precision'=>'month-only','event'=>'Apollo 1 crew photographed in training context','source_kind'=>'NASA retrospective image article (published 2017)','source'=>'https://www.nasa.gov/image-article/apollo-1-crew-honored/','boundary'=>'The article specifies January 1967 but not the photograph day; it does not verify the S67-19766 identifier or show the fire.'],
  ['date'=>'27 January 1967','machine_date'=>'1967-01-27','precision'=>'day','event'=>'Apollo 1 cabin fire during prelaunch testing','source_kind'=>'Apollo 204 Review Board report (investigation published after the fire)','source'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','boundary'=>'The Board found an electrical arc most probable, not a conclusively identified ignition source. This retrospective report is not a photograph of the event.'],
  ['date'=>'27 January 2017','machine_date'=>'2017-01-27','precision'=>'day','event'=>'Apollo 1 crew tribute opens at Kennedy Space Center','source_kind'=>'NASA retrospective museum article (2017)','source'=>'https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/','boundary'=>'A catalogue identifier suggests 24 January 2017, but that NASA image mapping remains unverified; no 2017 exhibit photo depicts the 1967 fire scene.'],
 ];
}
function fv457_chronology_valid(array $events): bool {
 if(count($events)!==3)return false;
 $seen=[];
 foreach($events as $e){
  foreach(['date','machine_date','precision','event','source_kind','source','boundary'] as $key){if(!isset($e[$key])||!is_string($e[$key])||trim($e[$key])==='')return false;}
  if(!in_array($e['precision'],['day','month-only'],true)||isset($seen[$e['source']]))return false;
  $format=$e['precision']==='day'?'!Y-m-d':'!Y-m';
  $dt=DateTimeImmutable::createFromFormat($format,$e['machine_date']);
  if(!$dt||$dt->format($e['precision']==='day'?'Y-m-d':'Y-m')!==$e['machine_date'])return false;
  $url=parse_url($e['source']);
  if(!is_array($url)||($url['scheme']??'')!=='https'||($url['host']??'')!=='www.nasa.gov'||empty($url['path'])||isset($url['user'])||isset($url['pass'])||isset($url['query'])||isset($url['fragment'])||isset($url['port']))return false;
  $seen[$e['source']]=true;
 }
 return true;
}
function fv457_chronology_html(string $instance): string {
 $events=fv457_chronology();if(!fv457_chronology_valid($events))return '';
 $o='<section class="fv457__chronology" aria-labelledby="'.$instance.'-chrono"><h3 id="'.$instance.'-chrono">Chronology: evidence time versus event time</h3>';
 $o.='<p>Three dated contexts, not a fabricated photograph-by-photograph sequence. The January 1967 portrait has no verified day, so it cannot be ordered precisely against the 27 January fire. A 2017 exhibit image does not depict a 1967 event.</p>';
 $o.='<ol class="fv457__rail" aria-label="Evidence time and event time">';
 foreach($events as $n=>$e){
  $o.='<li class="fv457__moment"><span class="fv457__step">'.fv457_h(str_pad((string)($n+1),2,'0',STR_PAD_LEFT)).' / 03</span>';
  $o.='<p class="fv457__date"><time datetime="'.fv457_h($e['machine_date']).'"><strong>'.fv457_h($e['date']).'</strong></time> · '.fv457_h($e['precision']).'</p>';
  $o.='<h4>'.fv457_h($e['event']).'</h4>';
  $o.='<details><summary>Source, date and uncertainty</summary><p><strong>Source type:</strong> '.fv457_h($e['source_kind']).'</p><p><strong>Limit:</strong> '.fv457_h($e['boundary']).'</p>';
  $o.='<p><a href="'.fv457_h($e['source']).'" rel="noopener noreferrer">Open NASA reference and provenance</a></p></details>';
  // Native details remain collapsed by default. Print/PDF preserves their precise
  // chronology source, full URL, and source-time uncertainty without scripting.
  $o.='<p class="fv457__chronology-print"><strong>Printable chronology source:</strong> <a href="'.fv457_h($e['source']).'" rel="noopener noreferrer">'.fv457_url_label($e['source']).'</a> · <strong>Publication context:</strong> '.fv457_h($e['source_kind']).' · <strong>Uncertainty:</strong> '.fv457_h($e['boundary']).'</p></li>';
 }
 return $o.'</ol><p class="fv457__chrono-question"><strong>Classroom inquiry:</strong> Which record is evidence of a 1967 event, and which is a later interpretation? Explain how the publication date differs from the event date. This exercise is free; no signup is required.</p></section>';
}

function fv457_valid(array $records): bool {
 if(count($records)!==6)return false;
 $ids=[];$shown=0;$home=0;$accepted=0;$heldId=0;$heldCatalogue=0;
 foreach($records as $r){
  foreach(['id','date','precision','date_label','role','source_url','source_check','boundary','source_status','credit'] as $k){if(!isset($r[$k])||!is_string($r[$k])||trim($r[$k])==='')return false;}
  if(!isset($r['shown'])||!is_bool($r['shown'])|| (isset($r['homepage_confirmed'])&&!is_bool($r['homepage_confirmed']))||isset($ids[$r['id']])||!preg_match('/^[A-Z0-9_-]{7,40}$/D',$r['id']))return false;
  if(!in_array($r['source_status'],['accepted','id_hold','catalogue_hold'],true))return false;
  if($r['source_status']==='accepted')$accepted++;
  elseif($r['source_status']==='id_hold')$heldId++;
  else $heldCatalogue++;
  if($r['precision']==='unverified'){
   if($r['date']!=='unverified'||$r['source_status']!=='catalogue_hold')return false;
  }else{
   if(!in_array($r['precision'],['day','month'],true))return false;
   $format=$r['precision']==='day'?'!Y-m-d':'!Y-m';
   $d=DateTimeImmutable::createFromFormat($format,$r['date']);
   if(!$d||$d->format($r['precision']==='day'?'Y-m-d':'Y-m')!==$r['date'])return false;
  }
  $parts=parse_url($r['source_url']);
  if(!is_array($parts)||($parts['scheme']??null)!=='https'||!in_array($parts['host']??'', ['www.nasa.gov','images.nasa.gov'],true)||empty($parts['path'])||isset($parts['user'])||isset($parts['pass'])||isset($parts['query'])||isset($parts['fragment'])||isset($parts['port']))return false;
  $ids[$r['id']]=true;if($r['shown'])$shown++;if($r['homepage_confirmed']??false){if($r['shown'])return false;$home++;}
 }
 return $shown===3&&$home===1&&$accepted===4&&$heldId===1&&$heldCatalogue===1;
}
function fv457_fallback(): string {return '<p>The image provenance list is temporarily unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';}
function fv457_render(): string {
 static $count=0;$records=fv457_records();if(!fv457_valid($records))return fv457_fallback();$instance='fv457-'.(++$count);
 $out='<section class="fv457" data-fv457-root id="'.$instance.'" aria-labelledby="'.$instance.'-heading"><div class="fv457__shell">';
 $out.='<p class="fv457__kicker">Final Vestige / Apollo 1 / Source custody</p><h2 id="'.$instance.'-heading">Six archival records across two published surfaces.</h2>';
 $out.='<p class="fv457__lede">These are <strong>source index cards, not reproductions</strong>. Three records appear in the Atlas chronology. S67-19766 is labelled not shown in that Atlas but appears on the published homepage. The other records have not been independently confirmed as present or absent on the homepage. Page placement is not image-use permission, and no marketing or merchandise clearance is implied.</p>';
 $out.=fv457_evidence_plates_html($instance);
 $out.=fv457_chronology_html($instance);
 $out.='<p class="fv457__rights"><strong>Rights boundary:</strong> NASA imagery is generally available for factual editorial use, subject to agency guidelines and potential third-party and publicity rights. No photograph, logo or astronaut likeness is embedded or cleared for merchandise, marketing or a paid educator product. NASA does not endorse this work.</p>';
 $out.='<p class="fv457__source-hold"><strong>Source acceptance HOLD:</strong> Four NASA image-detail records have independently verified matching catalogue IDs; the S67-19766 portrait ARTICLE is accessible but its archival-ID association is unverified, and the KSC-20170124-PH_KLS01_0129 catalogue lookup remains inaccessible. Its apparent 24 January date derives only from the candidate ID, not accepted image metadata. Neither an accepted source nor a research lead establishes rights to commercial reuse.</p>';
 $out.='<p class="fv457__print-note">Printed source-custody copy: all six archival records and all three chronology moments retain linked NASA source references in browser PDF exports, regardless of any on-screen filter. Dates describe historical events, not necessarily source-publication dates. Catalogue and identifier uncertainties remain unresolved; the printed copy is not commercial media clearance.</p>';
 $out.='<div data-fv457-controls class="fv457__controls" hidden role="group" aria-label="Filter archive image records"><button type="button" data-fv457-choice="all" aria-pressed="true">All six</button><button type="button" data-fv457-choice="accepted" aria-pressed="false">NASA ID confirmed (4)</button><button type="button" data-fv457-choice="shown" aria-pressed="false">Atlas chronology (3)</button><button type="button" data-fv457-choice="homepage" aria-pressed="false">Confirmed homepage (1)</button><button type="button" data-fv457-choice="withheld" aria-pressed="false">Not in Atlas (3)</button></div>';
 $out.='<p data-fv457-status class="fv457__status" aria-live="polite">All six records remain available without JavaScript.</p><ol class="fv457__grid" aria-label="Archival catalogue records">';
 foreach($records as $index=>$r){
  $out.='<li class="fv457__card" data-fv457-card="'.($r['shown']?'shown':'withheld').'" data-fv457-home="'.(($r['homepage_confirmed']??false)?'confirmed':'unverified').'" data-fv457-accepted="'.($r['source_status']==='accepted'?'yes':'no').'">';
  $out.='<p class="fv457__number">'.str_pad((string)($index+1),2,'0',STR_PAD_LEFT).' / 06 · '.($r['shown']?'In Atlas chronology':'Not in Atlas chronology').'</p>';
  $out.='<p class="fv457__date">'.fv457_h($r['date_label']).' · '.fv457_h($r['precision']).'-precision</p>';
  $out.='<h3>'.fv457_h($r['id']).'</h3><p>'.fv457_h($r['role']).'</p>';
  $state=['accepted'=>'Confirmed ID on a NASA image-detail page','id_hold'=>'HOLD: article accessible, image ID mapping unconfirmed','catalogue_hold'=>'HOLD: candidate catalogue lookup and image date unverified'][$r['source_status']];
  $out.='<p class="fv457__provenance"><strong>Source custody:</strong> '.fv457_h($state).' · <strong>Credit:</strong> '.fv457_h($r['credit']).' · <strong>Reuse:</strong> Not cleared for product marketing or licensing.</p>';
  $out.='<p class="fv457__surface"><strong>Published-page cross-check:</strong> '.(($r['homepage_confirmed']??false)?'Confirmed on the homepage 18 November 2026; not in the Atlas chronology.':'Homepage presence or absence not independently established.').'</p>';$out.='<p class="fv457__limitation"><strong>Evidence limit:</strong> '.fv457_h($r['boundary']).'</p>';
  $hold=($r['id']==='KSC-20170124-PH_KLS01_0129')?' — CATALOGUE LINK UNVERIFIED':(($r['id']==='S67-19766')?' — ID MAPPING UNVERIFIED':'');
 $linkText=$r['source_status']==='accepted'?'Open confirmed NASA image-detail record for ':'Open unverified research lead for ';
  $out.='<details><summary>Open source custody and usage review</summary><p>'.fv457_h($r['source_check']).'</p><p>Rights: source link does not grant commercial reuse or NASA endorsement.</p><p><a href="'.fv457_h($r['source_url']).'" rel="noopener noreferrer">'.fv457_h($linkText).fv457_h($r['id']).fv457_h($hold).'</a></p></details>';
  // Print/PDF link must retain URL annotation and tagged-document semantics; CSS hides this duplicate on screen.
  $out.='<p class="fv457__print-custody"><strong>Printable source lookup — '.fv457_h($state).':</strong> <a href="'.fv457_h($r['source_url']).'" rel="noopener noreferrer">'.fv457_h($r['source_url']).'</a> · '.fv457_h($r['source_check']).' · '.fv457_h($r['credit']).' · Image-use permission not established.</p>';
  $out.='</li>';
 }
 $out.='</ol><p class="fv457__note">This is an editorial source catalogue, not a geographic map: no fabricated coordinates or source connections. Atlas entries and the homepage S67-19766 presentation were inspected on 18 November 2026. Homepage absence for any other record was NOT established. Reverify both pages before acceptance.</p>';
 $out.='<p class="fv457__cta"><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free Apollo 1 investigation</a></p>';
 $out.='</div></section>';
 // R462 progressive degradation: an unavailable optional enhancement must not erase
 // source custody. A *present but altered* asset is an integrity failure and stays
 // fail-closed. When CSS is unavailable, omit JavaScript too: native HTML remains
 // useful with controls hidden and without an unstyled interactive mode.
 $css=__DIR__.'/assets/gallery.css';$js=__DIR__.'/assets/gallery.js';
 $cssPresent=is_file($css);$jsPresent=is_file($js);
 $style=$cssPresent?file_get_contents($css):null;
 $script=$jsPresent?file_get_contents($js):null;
 if(($cssPresent&&($style===false||!hash_equals('d263a0284884937eaf83256342d51d9e88da60f43e9a81a1a6caa81a24dc744c',hash('sha256',$style))))
    ||($jsPresent&&($script===false||!hash_equals('001ba5b8857bfee90d5d79db8435047946bc3a61253b3a8f4623e725daa1fb0a',hash('sha256',$script)))))return fv457_fallback();
 if(!$cssPresent)return $out;
 return '<style>'.$style.'</style>'.$out.($jsPresent?'<script>'.$script.'</script>':'');
}
if(function_exists('add_action'))add_action('init',static function():void{
 if(!defined('FV_R457_ENABLE_STAGING')||FV_R457_ENABLE_STAGING!==true||!defined('FV_R457_STAGING_PAGE_ID')||!is_int(FV_R457_STAGING_PAGE_ID)||FV_R457_STAGING_PAGE_ID<1||!function_exists('wp_get_environment_type')||wp_get_environment_type()!=='staging'||!function_exists('add_shortcode'))return;
 add_shortcode('fv_apollo_rights_gallery_r457',static function():string{
  if(!function_exists('get_queried_object_id')||get_queried_object_id()!==FV_R457_STAGING_PAGE_ID)return '';
  return fv457_render();
 });
});

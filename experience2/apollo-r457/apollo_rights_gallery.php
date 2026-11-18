<?php
/** R457 Apollo provenance gallery: staging-only; read-only source catalogue, not imagery rights clearance. */
declare(strict_types=1);
function fv457_records(): array {
  return [
    ['id'=>'S66-58038','date'=>'1966-10-18','precision'=>'day','date_label'=>'18 October 1966','role'=>'Crew training context','shown'=>true,'source_url'=>'https://www.nasa.gov/image-detail/amf-s66-58038/','source_check'=>'official NASA image-detail page located','boundary'=>'Training photograph. Does not depict the Apollo 1 accident.'],
    ['id'=>'S67-15717','date'=>'1967-01-03','precision'=>'day','date_label'=>'3 January 1967','role'=>'Spacecraft preparations','shown'=>true,'source_url'=>'https://www.nasa.gov/image-detail/amf-s67-15717/','source_check'=>'official NASA image-detail page located','boundary'=>'Pre-fire spacecraft context. Not a photograph of the ignition.'],
    ['id'=>'S67-19766','date'=>'1967-01','precision'=>'month','date_label'=>'January 1967 (day not established here)','role'=>'Crew context','shown'=>false,'source_url'=>'https://www.nasa.gov/image-detail/apollo-1-crew-honored/','source_check'=>'NASA image-detail page located; ID-to-item mapping needs editorial confirmation','boundary'=>'Do not infer an exact day from an approximate archive date.'],
    ['id'=>'S67-21294','date'=>'1967-01-28','precision'=>'day','date_label'=>'28 January 1967','role'=>'Aftermath documentation','shown'=>false,'source_url'=>'https://www.nasa.gov/image-detail/amf-s67-21294/','source_check'=>'official NASA image-detail page located','boundary'=>'Post-fire image withheld from this experience; do not confuse aftermath with the fire sequence.'],
    ['id'=>'KSC-20170124-PH_KLS01_0129','date'=>'2017-01-24','precision'=>'day','date_label'=>'24 January 2017','role'=>'Retrospective hatch exhibit','shown'=>true,'source_url'=>'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129','source_check'=>'NASA Images catalogue link could not be independently retrieved in this audit; HOLD link acceptance','boundary'=>'2017 museum photograph, not a contemporaneous 1967 event record.'],
    ['id'=>'KSC-20170124-PH_KLS01_0090','date'=>'2017-01-24','precision'=>'day','date_label'=>'24 January 2017','role'=>'Retrospective exhibit context','shown'=>false,'source_url'=>'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','source_check'=>'official NASA image-detail page located','boundary'=>'2017 exhibit photograph, not evidence of the ignition source.'],
  ];
}
function fv457_h(string $x): string {return htmlspecialchars($x, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');}
function fv457_valid(array $records): bool {
 if(count($records)!==6)return false;
 $ids=[];$shown=0;
 foreach($records as $r){
  foreach(['id','date','precision','date_label','role','source_url','source_check','boundary'] as $k){if(!isset($r[$k])||!is_string($r[$k])||trim($r[$k])==='')return false;}
  if(!isset($r['shown'])||!is_bool($r['shown'])||isset($ids[$r['id']])||!preg_match('/^[A-Z0-9_-]{7,40}$/D',$r['id']))return false;
  if(!in_array($r['precision'],['day','month'],true))return false;
  $format=$r['precision']==='day'?'!Y-m-d':'!Y-m';
  $d=DateTimeImmutable::createFromFormat($format,$r['date']);
  if(!$d||$d->format($r['precision']==='day'?'Y-m-d':'Y-m')!==$r['date'])return false;
  $parts=parse_url($r['source_url']);
  if(!is_array($parts)||($parts['scheme']??null)!=='https'||!in_array($parts['host']??'', ['www.nasa.gov','images.nasa.gov'],true)||empty($parts['path'])||isset($parts['user'])||isset($parts['pass'])||isset($parts['query'])||isset($parts['fragment'])||isset($parts['port']))return false;
  $ids[$r['id']]=true;if($r['shown'])$shown++;
 }
 return $shown===3;
}
function fv457_fallback(): string {return '<p>The image provenance list is temporarily unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';}
function fv457_render(): string {
 static $count=0;$records=fv457_records();if(!fv457_valid($records))return fv457_fallback();$instance='fv457-'.(++$count);
 $out='<section class="fv457" data-fv457-root id="'.$instance.'" aria-labelledby="'.$instance.'-heading"><div class="fv457__shell">';
 $out.='<p class="fv457__kicker">Final Vestige / Apollo 1 / Source custody</p><h2 id="'.$instance.'-heading">Six archival image records. Three withheld.</h2>';
 $out.='<p class="fv457__lede">These are <strong>source index cards, not reproductions</strong>. Three records are described by the currently published Atlas as displayed editorially; three are withheld. That listing is not a fresh licensing certificate or permission for product promotion.</p>';
 $out.='<p class="fv457__rights"><strong>Rights boundary:</strong> NASA imagery is generally available for factual editorial use, subject to agency guidelines and potential third-party and publicity rights. No photograph, logo or astronaut likeness is embedded or cleared for merchandise, marketing or a paid educator product. NASA does not endorse this work.</p>';
 $out.='<div data-fv457-controls class="fv457__controls" hidden role="group" aria-label="Filter archive image records"><button type="button" data-fv457-choice="all" aria-pressed="true">All six</button><button type="button" data-fv457-choice="shown" aria-pressed="false">Shown on live Atlas</button><button type="button" data-fv457-choice="withheld" aria-pressed="false">Withheld</button></div>';
 $out.='<p data-fv457-status class="fv457__status" aria-live="polite">All six records remain available without JavaScript.</p><ol class="fv457__grid" aria-label="Archival catalogue records">';
 foreach($records as $index=>$r){
  $out.='<li class="fv457__card" data-fv457-card="'.($r['shown']?'shown':'withheld').'">';
  $out.='<p class="fv457__number">'.str_pad((string)($index+1),2,'0',STR_PAD_LEFT).' / 06 · '.($r['shown']?'Shown on live Atlas':'Withheld on live Atlas').'</p>';
  $out.='<p class="fv457__date">'.fv457_h($r['date_label']).' · '.fv457_h($r['precision']).'-precision</p>';
  $out.='<h3>'.fv457_h($r['id']).'</h3><p>'.fv457_h($r['role']).'</p>';
  $out.='<p class="fv457__limitation"><strong>Evidence limit:</strong> '.fv457_h($r['boundary']).'</p>';
  $out.='<details><summary>Open source custody and usage review</summary><p>'.fv457_h($r['source_check']).'</p><p>Rights: source link does not grant commercial reuse or NASA endorsement.</p><p><a href="'.fv457_h($r['source_url']).'" rel="noopener noreferrer">NASA record for '.fv457_h($r['id']).'</a></p></details>';
  $out.='</li>';
 }
 $out.='</ol><p class="fv457__note">This is an editorial source catalogue, not a geographic map: no fabricated coordinates or source connections. The source statuses were audited against the public Atlas on 18 November 2026 and must be rechecked before staging acceptance.</p>';
 $out.='<p class="fv457__cta"><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free Apollo 1 investigation</a></p>';
 $out.='</div></section>';
 $css=__DIR__.'/assets/gallery.css';$js=__DIR__.'/assets/gallery.js';
 if(!is_file($css)||!is_file($js))return fv457_fallback();
 $style=file_get_contents($css);$script=file_get_contents($js);if($style===false||$script===false)return fv457_fallback();
 return '<style>'. $style .'</style>'.$out.'<script>'.$script.'</script>';
}
if(function_exists('add_action'))add_action('init',static function():void{
 if(!defined('FV_R457_ENABLE_STAGING')||FV_R457_ENABLE_STAGING!==true||!defined('FV_R457_STAGING_PAGE_ID')||!is_int(FV_R457_STAGING_PAGE_ID)||FV_R457_STAGING_PAGE_ID<1||!function_exists('wp_get_environment_type')||wp_get_environment_type()!=='staging'||!function_exists('add_shortcode'))return;
 add_shortcode('fv_apollo_rights_gallery_r457',static function():string{
  if(!function_exists('get_queried_object_id')||get_queried_object_id()!==FV_R457_STAGING_PAGE_ID)return '';
  return fv457_render();
 });
});

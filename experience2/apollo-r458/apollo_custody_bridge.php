<?php
/**
 * FV Apollo R458 — source/placement-custody bridge. Uninstalled, read-only staging-only candidate.
 * No NASA artwork, geographic pins, checkout, analytics, tracking, customer data or WordPress writes.
 */
declare(strict_types=1);
function fv458_records(): array {
  return [
    ['id'=>'training','date'=>'1966-10-18','date_role'=>'Original photograph date','period'=>'historical','title'=>'Crew altitude-chamber training','claim'=>'Training-context photograph; not an image of the accident.','limit'=>'This training image cannot establish the hatch operation, fire sequence or the initiating spark.','source'=>'NASA image detail S66-58038','url'=>'https://www.nasa.gov/image-detail/amf-s66-58038/','custody'=>'Agency-hosted archival photograph record; contextual editorial use only, not promotional rights clearance.'],
    ['id'=>'spacecraft','date'=>'1967-01-03','date_role'=>'Original photograph date','period'=>'historical','title'=>'Spacecraft 012 undergoing preparation','claim'=>'Pre-fire spacecraft context, photographed January 1967.','limit'=>'A preparation image cannot establish the ignition or the test-time sequence.','source'=>'NASA image detail S67-15717','url'=>'https://www.nasa.gov/image-detail/amf-s67-15717/','custody'=>'Agency-hosted archival photograph record; NASA source credit is not permission for commercial promotional artwork.'],
    ['id'=>'accident','date'=>'1967-01-27','date_role'=>'Event date (report published later)','period'=>'historical','title'=>'Apollo 1 ground-test fire','claim'=>'The Apollo 204 Review Board treated an electrical arc as the most probable initiator.','limit'=>'The Board did not conclusively identify one specific wire or a certain ignition point; the report was issued after the event.','source'=>'Apollo 204 Review Board report','url'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','custody'=>'Primary investigative report; link points to text/source, not a reproduced image or licensing decision.'],
    ['id'=>'tribute','date'=>'2017-01-27','date_role'=>'Memorial announcement date','period'=>'retrospective','title'=>'Public presentation of the hatch','claim'=>'NASA described a memorial display that included the Apollo 1 spacecraft hatch.','limit'=>'A 2017 exhibition documents public remembrance; it does not establish the mechanism of the 1967 fire.','source'=>'Apollo 1 memorial announcement','url'=>'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/','custody'=>'Institutional retrospective; exhibit imagery and identifiable people require independent item-level rights assessment.'],
    ['id'=>'experiments','date'=>'2018-02-14','date_role'=>'Later article publication date; experiments occurred earlier','period'=>'retrospective','title'=>'Later flammability experiments revisited','claim'=>'NASA recounted subsequent Apollo spacecraft flammability experiments.','limit'=>'Later tests did not isolate the original ignition spark; a 2018 article is not a 1967 test-day record.','source'=>'50 Years Ago: Apollo Flammability Tests','url'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/','custody'=>'Institutional retrospective linked as source text, with no NASA imagery embedded.'],
  ];
}
function fv458_placement(): array {
  return ['id'=>'S67-19766','homepage'=>'Editorially displayed on the homepage (reviewed stored page 6, modified 2026-11-14)','atlas'=>'Listed as “Not shown” on the Apollo Evidence Atlas (reviewed stored page 2017, modified 2026-11-14)','status'=>'EDITORIAL_RECONCILIATION_REQUIRED'];
}
function fv458_e(string $value): string { return htmlspecialchars($value, ENT_QUOTES|ENT_SUBSTITUTE, 'UTF-8'); }
function fv458_valid_url(string $url, array $allowedHosts): bool {
  $parts=parse_url($url);
  return is_array($parts)&&($parts['scheme']??'')==='https'&&in_array($parts['host']??'', $allowedHosts, true)&&!empty($parts['path'])&&
   !isset($parts['user'])&&!isset($parts['pass'])&&!isset($parts['port'])&&!isset($parts['query'])&&!isset($parts['fragment']);
}
function fv458_valid(array $records, array $placement): bool {
  if(count($records)!==5)return false;
  $ids=[];$last='';$historic=0;$later=0;
  foreach($records as $record){
    foreach(['id','date','date_role','period','title','claim','limit','source','url','custody'] as $field){if(!isset($record[$field])||!is_string($record[$field])||trim($record[$field])==='')return false;}
    if(!preg_match('/^[a-z]{5,16}$/D',$record['id'])||isset($ids[$record['id']]))return false;
    $date=DateTimeImmutable::createFromFormat('!Y-m-d',$record['date']);
    if(!$date||$date->format('Y-m-d')!==$record['date']||$record['date']<=$last)return false;
    if(!in_array($record['period'],['historical','retrospective'],true))return false;
    if(!fv458_valid_url($record['url'],['www.nasa.gov']))return false;
    $ids[$record['id']]=true;$last=$record['date'];
    if($record['period']==='historical')$historic++;else $later++;
  }
  return $historic===3&&$later===2&&($placement['id']??'')==='S67-19766'&&($placement['status']??'')==='EDITORIAL_RECONCILIATION_REQUIRED'&&
    is_string($placement['homepage']??null)&&is_string($placement['atlas']??null);
}
function fv458_assets(): ?array {
  $map=['css'=>['bridge.css','bd5ec5dfe2d88f202b6a521beedb393e609ea1bb44544502096fc2cee24c80d7'],
        'js'=>['bridge.js','39ba172b8a32d853cce3138bfdbc70ed829c72ec4c75b895a874cf5a91bb0c4f']];
  $result=[];
  foreach($map as $kind=>$spec){[$file,$digest]=$spec;$path=__DIR__.'/assets/'.$file;
    if(!is_file($path)||!is_readable($path)||!hash_equals($digest,hash_file('sha256',$path)))return null;
    $contents=file_get_contents($path);if(!is_string($contents)||$contents==='')return null;$result[$kind]=$contents;
  }
  return $result;
}
function fv458_fallback(): string {
  return '<p>The independent source-check experience is temporarily unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
}
function fv458_render(): string {
  static $instance=0;
  $records=fv458_records();$placement=fv458_placement();$assets=fv458_assets();
  if(!fv458_valid($records,$placement)||$assets===null)return fv458_fallback();
  $id='fv458-'.(++$instance);$html='<section class="fv458" data-fv458-root id="'.$id.'" aria-labelledby="'.$id.'-title"><div class="fv458__inner">';
  $html.='<p class="fv458__kicker">Final Vestige / Apollo 1 / Evidence &amp; Source Custody</p><h2 id="'.$id.'-title">Trace the record. Know its limits.</h2>';
  $html.='<p class="fv458__intro">A five-record chronology connects archival context, a primary accident investigation, and later interpretation. Each source has a specific evidentiary role. The record is not a product endorsement or permission slip for promotional reuse.</p>';
  $html.='<aside class="fv458__boundary"><strong>Three distinct dates matter.</strong><p>When an event occurred, when its photograph was made, and when a later report or article appeared are not interchangeable. A probable cause is not a proven individual ignition wire.</p></aside>';
  $html.='<ul class="fv458__legend" aria-label="Source categories"><li><span>3 historical-context / investigation records</span></li><li><span>2 later interpretation records</span></li></ul>';
  $html.='<div class="fv458__filters" data-fv458-filters hidden aria-label="Filter evidence records"><button type="button" data-fv458-choice="all" aria-pressed="true">All five records</button><button type="button" data-fv458-choice="historical" aria-pressed="false">Historical &amp; investigative</button><button type="button" data-fv458-choice="retrospective" aria-pressed="false">Later interpretation</button></div>';
  $html.='<p class="fv458__status" data-fv458-status role="status" aria-live="polite">All five source records are readable; filters are optional.</p>';
  $html.='<ol class="fv458__rail" aria-label="Source chronology ordered by the displayed date role">';
  foreach($records as $record){
    $html.='<li class="fv458__record" data-fv458-record="'.fv458_e($record['period']).'">';
    $html.='<p class="fv458__date"><time datetime="'.fv458_e($record['date']).'">'.fv458_e($record['date']).'</time> · '.fv458_e($record['date_role']).'</p>';
    $html.='<h3>'.fv458_e($record['title']).'</h3><p><strong>What the record supports:</strong> '.fv458_e($record['claim']).'</p>';
    $html.='<p class="fv458__limits"><strong>Where the evidence stops:</strong> '.fv458_e($record['limit']).'</p>';
    $html.='<details><summary>Inspect source custody and link</summary><p>'.fv458_e($record['custody']).'</p>';
    $html.='<p><a data-fv458-source href="'.fv458_e($record['url']).'" rel="noopener noreferrer">'.fv458_e($record['source']).' — source record</a></p></details></li>';
  }
  $html.='</ol><aside class="fv458__placement" aria-labelledby="'.$id.'-placement"><p class="fv458__eyebrow">Unresolved editorial reuse discrepancy · not a licensing judgment</p><h3 id="'.$id.'-placement">One image, two page decisions.</h3>';
  $html.='<p>Archival ID <strong>'.fv458_e($placement['id']).'</strong> appears as a crew photograph on the homepage, while the published Apollo Atlas explicitly lists that record as “Not shown.” Both page snapshots were read on 18 November 2026; the underlying pages were last modified on 14 November 2026.</p>';
  $html.='<div class="fv458__placement-grid"><div><strong>Homepage / displayed</strong><p>'.fv458_e($placement['homepage']).'</p><a href="https://finalvestige.com/" rel="noopener noreferrer">Inspect the published homepage</a></div>';
  $html.='<div><strong>Atlas / withheld</strong><p>'.fv458_e($placement['atlas']).'</p><a href="https://finalvestige.com/apollo-1-evidence-atlas/" rel="noopener noreferrer">Inspect the published Evidence Atlas</a></div></div>';
  $html.='<p data-placement-state><strong>Decision required:</strong> Have the editor and rights reviewer reconcile the intended page-specific image policy. Neither placement is evidence of NASA endorsement or commercial image-use clearance.</p>';
  $html.='<details><summary>Read the official media-use boundary</summary><p>NASA generally permits factual editorial/educational image use subject to its guidelines, source credit, third-party rights and non-endorsement. Commercial advertising, identifiable-person likenesses, agency marks and product naming may involve additional restrictions; do not label a paid item as agency-approved.</p><p><a href="https://www.nasa.gov/nasa-brand-center/images-and-media/">NASA images and media guidelines</a> · <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/">NASA advertising guidelines</a></p></details></aside>';
  $html.='<section class="fv458__lesson" aria-labelledby="'.$id.'-lesson"><h3 id="'.$id.'-lesson">A classroom-ready question, freely accessible</h3><p>Using the five sources above, distinguish the most probable cause of the fire from a conclusively proven ignition site. Then explain why a 2017 museum photograph cannot replace a 1967 investigative record.</p>';
  $html.='<details><summary>View a short instructor check</summary><p>A strong answer distinguishes the Board’s probable electrical-arc finding from a specific proven wire, and identifies the 2017 memorial as retrospective documentation, not original accident evidence.</p></details>';
  $html.='<p><button type="button" class="fv458__copy" data-fv458-save hidden>Download original text study note</button> <span data-fv458-save-status role="status" aria-live="polite"></span></p></section>';
  $html.='<p class="fv458__next">Continue to the original source-led story: <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free investigation</a>.</p>';
  $html.='<p class="fv458__fineprint">No artwork, NASA logo, map pin, proposed geographic relationship, tracking, signup or checkout is embedded. A separately approved, demonstrably sellable, rights-cleared classroom product is a future hypothesis—not an active offer or paid conversion. NASA does not endorse Final Vestige.</p>';
  return $html.'</div></section><style>'.$assets['css'].'</style><script>'.$assets['js'].'</script>';
}
if(function_exists('add_action'))add_action('init',static function(): void {
  if(!defined('FV_R458_ENABLE_STAGING')||FV_R458_ENABLE_STAGING!==true||!defined('FV_R458_STAGING_PAGE_ID')||!is_int(FV_R458_STAGING_PAGE_ID)||FV_R458_STAGING_PAGE_ID<1||!function_exists('wp_get_environment_type')||wp_get_environment_type()!=='staging'||!function_exists('add_shortcode'))return;
  add_shortcode('fv_apollo_custody_bridge_r458',static function(): string {
    if(!function_exists('get_queried_object_id')||get_queried_object_id()!==FV_R458_STAGING_PAGE_ID)return '';
    return fv458_render();
  });
});

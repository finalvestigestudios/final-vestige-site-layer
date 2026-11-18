<?php
/** Apollo Experience 2.0 R458 / staging-only editorial discrepancy and source provenance. No WordPress writes. */
declare(strict_types=1);

const FV458_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV458_REVIEW_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV458_MEDIA_RULES = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';
const FV458_PINNED = [
  'data/records.json' => '342327ee7a138e4edfdafe69a231f47b13ad9f2c7c6cc3d015fbecf2b28d1f30',
  'assets/audit.css' => 'e63db78611e049a76a8d97c4ce1a463597d9d12e70f00728cd0b7351714d1fa4',
  'assets/audit.js' => 'e3e471e59a5152231e87f6f932ad94f7fe300b021a77c6af0f653c66885db4e9'
];
function fv458_e(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv458_fallback(): string {return '<p>Archival source-review cards are temporarily unavailable. <a href="'.FV458_FREE.'">Read the complete free Apollo 1 investigation</a>.</p>';}
function fv458_safe_nasa_url(string $url): bool {
  $p=parse_url($url);
  return is_array($p) && ($p['scheme']??null)==='https' && in_array($p['host']??'', ['www.nasa.gov','images.nasa.gov'],true)
   && isset($p['path']) && $p['path']!=='/' && !isset($p['user'],$p['pass'])
   && !array_key_exists('user',$p) && !array_key_exists('pass',$p)
   && !array_key_exists('port',$p) && !array_key_exists('query',$p) && !array_key_exists('fragment',$p);
}
function fv458_valid(array $payload): bool {
 if(!isset($payload['audit_context']['snapshot_day'],$payload['audit_context']['issue_url'],$payload['audit_context']['evidence_note'])
 || $payload['audit_context']['snapshot_day']!=='2026-11-18'
 || $payload['audit_context']['issue_url']!=='https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150'
 || !is_string($payload['audit_context']['evidence_note']) || trim($payload['audit_context']['evidence_note'])===''
 || !isset($payload['records'],$payload['claims'])||!is_array($payload['records'])||!is_array($payload['claims'])
 || count($payload['records'])!==6||count($payload['claims'])!==3)return false;
 $ids=[];$states=['recorded'=>0,'reconcile'=>0,'source_hold'=>0];$atlas=['shown'=>0,'withheld'=>0];$previous='';
 foreach($payload['records'] as $r){
  if(!is_array($r))return false;
  foreach(['id','event_date','precision','when','topic','atlas_use','homepage_use','catalogue_status','review_state','source_url','limit'] as $key){
   if(!isset($r[$key])||!is_string($r[$key])||trim($r[$key])==='')return false;
  }
  if(!preg_match('/^[A-Z0-9_-]{7,45}$/D',$r['id'])||isset($ids[$r['id']])||!in_array($r['precision'],['day','month'],true)
   ||!in_array($r['atlas_use'],['shown','withheld'],true)||!in_array($r['homepage_use'],['shown','not_reviewed'],true)
   ||!in_array($r['catalogue_status'],['located','item_mapping_unconfirmed','unretrieved'],true)
   ||!array_key_exists($r['review_state'],$states)||!fv458_safe_nasa_url($r['source_url']))return false;
  $format=$r['precision']==='day'?'!Y-m-d':'!Y-m';$outFormat=$r['precision']==='day'?'Y-m-d':'Y-m';
  $date=DateTimeImmutable::createFromFormat($format,$r['event_date']);
  if(!$date||$date->format($outFormat)!==$r['event_date'])return false;
  $sort=$date->format('Y-m');if($previous!==''&&$sort<$previous)return false;$previous=$sort;
  $ids[$r['id']]=$r;$states[$r['review_state']]++;$atlas[$r['atlas_use']]++;
 }
 if($states!==['recorded'=>4,'reconcile'=>1,'source_hold'=>1]||$atlas!==['shown'=>3,'withheld'=>3])return false;
 $mismatch=$ids['S67-19766']??null;$unresolved=$ids['KSC-20170124-PH_KLS01_0129']??null;
 if(!$mismatch||$mismatch['atlas_use']!=='withheld'||$mismatch['homepage_use']!=='shown'
 ||$mismatch['catalogue_status']!=='item_mapping_unconfirmed'||$mismatch['review_state']!=='reconcile'
 ||!$unresolved||$unresolved['catalogue_status']!=='unretrieved'||$unresolved['review_state']!=='source_hold')return false;
 foreach($payload['claims'] as $c){
  if(!is_array($c))return false;
  foreach(['heading','supported','cannot_show','source_url','source_kind'] as $key){if(!isset($c[$key])||!is_string($c[$key])||trim($c[$key])==='')return false;}
  if(!fv458_safe_nasa_url($c['source_url']))return false;
 }
 return true;
}
function fv458_read_pinned(): ?array {
 $contents=[];
 foreach(FV458_PINNED as $file=>$sha){
  $path=__DIR__.'/'.$file;
  if(!is_file($path)||!is_readable($path))return null;
  $bytes=file_get_contents($path);
  if(!is_string($bytes)||!hash_equals($sha,hash('sha256',$bytes)))return null;
  $contents[$file]=$bytes;
 }
 try {$payload=json_decode($contents['data/records.json'],true,512,JSON_THROW_ON_ERROR);} catch(Throwable $e){return null;}
 if(!is_array($payload)||!fv458_valid($payload))return null;
 return ['data'=>$payload,'css'=>$contents['assets/audit.css'],'js'=>$contents['assets/audit.js']];
}
function fv458_render(): string {
 static $i=0;
 $files=fv458_read_pinned();if($files===null)return fv458_fallback();$data=$files['data'];$id='fv458-'.(++$i);
 $o='<section class="fv458" data-fv458-root id="'.$id.'" aria-labelledby="'.$id.'-heading"><div class="fv458__wrap">';
 $o.='<p class="fv458__eyebrow">Final Vestige Studios / Apollo 1 / Review Desk</p><h2 id="'.$id.'-heading">What the archival image does—and does not—prove.</h2>';
 $o.='<p class="fv458__lead">Six image catalogue records, three primary-source claims, and one recorded disagreement between public-page image labels. Source location is <strong>not</strong> commercial reuse authorization.</p>';
 $o.='<p class="fv458__notice"><strong>Open editorial issue:</strong> The public Atlas recorded S67-19766 as withheld, while the homepage was observed displaying it. This requires a context-specific editorial review—not an assumption of copyright infringement or an automatic takedown. A 2017 item catalogue link also remains unverified.</p>';
 $o.='<p class="fv458__strip">Recorded source-use snapshot: '.fv458_e($data['audit_context']['snapshot_day']).' · <a href="'.fv458_e($data['audit_context']['issue_url']).'">Review record / Issue #150</a> · <a href="'.FV458_MEDIA_RULES.'">NASA media-use conditions</a>. NASA does not endorse this product or site.</p>';
 $o.='<div class="fv458__section"><h3>Chronology rail: event versus later documentation</h3><ol class="fv458__line">';
 $milestones=[['1966-10','1966 · Crew training','Archival training images establish context, not an ignition source.'],['1967-01-27','27 Jan 1967 · Accident','A ground test; primary incident findings belong to the 1967 Review Board.'],['1967-04','1967 · Investigation','The Board reported probable electrical arcing but no proven single ignition source.'],['2017-01','2017 · Exhibit','Hatch display images are retrospective, not fire-scene photographs.']];
 foreach($milestones as $m){$o.='<li><time datetime="'.fv458_e($m[0]).'">'.fv458_e($m[1]).'</time><p>'.fv458_e($m[2]).'</p></li>';}
 $o.='</ol></div>';
 $o.='<div class="fv458__section"><h3>Image custody and cross-page status</h3><p class="fv458__note">'.fv458_e($data['audit_context']['evidence_note']).' “Not reviewed” is not “not shown.” Items are indexed by historical date; there are no geographic pins or inferred relationships.</p>';
 $o.='<div class="fv458__tools" data-fv458-tools hidden role="group" aria-label="Filter source reconciliation records"><button type="button" data-fv458-filter="all" aria-pressed="true">All six</button><button type="button" data-fv458-filter="recorded" aria-pressed="false">Recorded context</button><button type="button" data-fv458-filter="reconcile" aria-pressed="false">Cross-page review</button><button type="button" data-fv458-filter="source_hold" aria-pressed="false">Unverified catalogue</button></div>';
 $o.='<p class="fv458__status" aria-live="polite" data-fv458-status>All six records are readable without JavaScript.</p><ol class="fv458__cards">';
 foreach($data['records'] as $r){
  $o.='<li class="fv458__card" data-fv458-card="'.fv458_e($r['review_state']).'">';
  $o.='<p class="fv458__tag">'.fv458_e($r['review_state']==='reconcile'?'Editorial mismatch / review required':($r['review_state']==='source_hold'?'Catalogue verification HOLD':'Catalogue record / further checks required')).'</p>';
  $o.='<time datetime="'.fv458_e($r['event_date']).'">'.fv458_e($r['when']).'</time>';
  $o.='<h3 class="fv458__id">'.fv458_e($r['id']).'</h3><p>'.fv458_e($r['topic']).'</p>';
  $o.='<p><strong>Atlas:</strong> '.fv458_e($r['atlas_use']).' · <strong>Homepage:</strong> '.fv458_e(str_replace('_',' ',$r['homepage_use'])).'</p>';
  $o.='<details><summary>Source, limits and rights</summary><p><strong>What it cannot establish:</strong> '.fv458_e($r['limit']).'</p>';
  $o.='<p><strong>Catalogue check:</strong> '.fv458_e(str_replace('_',' ',$r['catalogue_status'])).'. A source URL alone does not certify a photograph or authorise marketing reuse.</p>';
  $o.='<p><a href="'.fv458_e($r['source_url']).'" rel="noopener noreferrer">NASA reference (verify item and credits)</a></p></details></li>';
 }
 $o.='</ol></div>';
 $o.='<div class="fv458__section"><h3>Primary findings are not image captions</h3><div class="fv458__claim-grid">';
 foreach($data['claims'] as $c){$o.='<article><h3>'.fv458_e($c['heading']).'</h3><p><strong>What the source establishes:</strong> '.fv458_e($c['supported']).'</p><p><strong>What photographs cannot prove:</strong> '.fv458_e($c['cannot_show']).'</p><p class="fv458__note">'.fv458_e($c['source_kind']).'</p><p><a href="'.fv458_e($c['source_url']).'" rel="noopener noreferrer">Read primary NASA finding</a></p></article>';}
 $o.='</div></div>';
 $o.='<div class="fv458__section fv458__review"><h3>Editorial release-review checklist</h3><p>These private, local checkboxes are for reviewing the evidence trail; checking them does not establish rights clearance, a published video, a paid product, or approval.</p>';
 foreach(['Reconcile photo S67-19766 on the homepage and public Atlas with the homepage lead.','Independently verify the 2017 KSC image catalogue identity and individual asset credit.','Confirm the commercial image-use boundary and any identifiable-person permissions with the rights owner.','Complete hosted WordPress accessibility, performance, editorial, QD and founder release gates.'] as $label){$o.='<label><input type="checkbox"> '.fv458_e($label).'</label>';}
 $o.='</div>';
 $o.='<p class="fv458__cta"><a href="'.FV458_FREE.'">Read the full free Apollo 1 investigation</a></p>';
 $o.='<p class="fv458__note">The proposed educator product is not verified as sellable; no paid CTA, tracking, email form or NASA imagery is embedded. Grok owns documentary distribution; Praxxis owns independent creator review.</p></div></section>';
 return '<style>'.$files['css'].'</style>'.$o.'<script>'.$files['js'].'</script>';
}
if(function_exists('add_action'))add_action('init',static function():void{
 if(!defined('FV_R458_ENABLED')||FV_R458_ENABLED!==true
  ||!defined('FV_R458_PAGE_ID')||!is_int(FV_R458_PAGE_ID)||FV_R458_PAGE_ID<1
  ||!function_exists('wp_get_environment_type')||wp_get_environment_type()!=='staging'
  ||!function_exists('add_shortcode'))return;
 add_shortcode('fv_apollo_editorial_reconciliation_r458',static function():string{
  if(!function_exists('get_queried_object_id')||get_queried_object_id()!==FV_R458_PAGE_ID)return '';
  return fv458_render();
 });
});

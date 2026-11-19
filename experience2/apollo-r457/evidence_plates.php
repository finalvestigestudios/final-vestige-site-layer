<?php
/** Apollo R466: audited evidence-to-claim plates, independent of media. */
declare(strict_types=1);
/** R466 EvidencePlate: source-grounded conclusions, each coupled to its limit. */
function fv457_evidence_plates(): array {
 return [
  ['id'=>'cause','date'=>'1967','label'=>'Finding · likely initiator','claim'=>'The Apollo 204 Review Board judged an electrical arc the most probable fire initiator, near the Environmental Control Unit and nearby wiring.','limit'=>'The Board could not conclusively identify one exact failed wire or point of ignition. A probable initiating mechanism is not a documented photograph of a spark.','kind'=>'Primary investigation, 1967; published retrospective NASA transcript','source'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
  ['id'=>'egress','date'=>'1967-01-27','label'=>'Finding · emergency egress','claim'=>'The inward-opening inner hatch could not be opened against the pressure increase as the fire developed; the Board described subsequent obstacles to crew egress.','limit'=>'The hatch was one part of a broader fire and escape-system failure. This finding does not identify the ignition source or establish that a single design change alone could have prevented the accident.','kind'=>'Primary investigation, 1967; published retrospective NASA transcript','source'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
  ['id'=>'memorial','date'=>'2017-01-27','label'=>'Retrospective · historical memorial','claim'=>'A new Apollo 1 tribute opened at Kennedy Space Center on 27 January 2017 and displayed the three-part spacecraft hatch.','limit'=>'A 2017 memorial exhibit is not contemporaneous evidence of the 1967 ignition. The separate proposed KSC-20170124-PH_KLS01_0129 photo identifier and date remain unverified.','kind'=>'NASA public announcement, 27 January 2017','source'=>'https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/'],
 ];
}
function fv457_evidence_plates_valid(array $plates): bool {
 if(count($plates)!==3)return false;
 $expected=['cause','egress','memorial'];$used=[];
 $allowed=[
  'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
  'https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/',
 ];
 foreach($plates as $p){
  foreach(['id','date','label','claim','limit','kind','source'] as $key)if(!isset($p[$key])||!is_string($p[$key])||trim($p[$key])==='')return false;
  if(!in_array($p['id'],$expected,true)||isset($used[$p['id']])||!in_array($p['source'],$allowed,true))return false;
  if(!in_array($p['date'],['1967','1967-01-27','2017-01-27'],true))return false;
  $used[$p['id']]=true;
 }
 return count($used)===3;
}
function fv457_evidence_plates_html(string $instance): string {
 $plates=fv457_evidence_plates();if(!fv457_evidence_plates_valid($plates))return '';
 $o='<section class="fv457__evidence" aria-labelledby="'.$instance.'-evidence"><h3 id="'.$instance.'-evidence">What the records establish — and what they cannot</h3>';
 $o.='<p>Three primary-source checks separate historical findings from uncertainty and later memorial interpretation. Select a source drawer to compare evidence and limitations. This is factual research, not a claim of NASA endorsement or commercial image-use permission.</p>';
 $o.='<ol class="fv457__evidence-grid">';
 foreach($plates as $p){
  $o.='<li class="fv457__evidence-plate" data-fv457-plate="'.fv457_h($p['id']).'">';
  $o.='<p class="fv457__evidence-label">'.fv457_h($p['label']).' · '.fv457_h($p['date']).'</p>';
  $o.='<h4>'.fv457_h($p['claim']).'</h4>';
  $o.='<p><strong>Evidence boundary:</strong> '.fv457_h($p['limit']).'</p>';
  $o.='<details><summary>Review the official source and custody</summary><p><strong>Record:</strong> '.fv457_h($p['kind']).'</p><p><strong>Reuse:</strong> Source citation only; no NASA photo, insignia, or astronaut likeness licensed for paid use.</p><p><a href="'.fv457_h($p['source']).'" rel="noopener noreferrer">Read the NASA record</a></p></details>';
  $o.='<p class="fv457__evidence-print"><strong>Printable evidence citation:</strong> '.fv457_h($p['kind']).' · <a href="'.fv457_h($p['source']).'" rel="noopener noreferrer">Open NASA source</a> · <strong>URL:</strong> '.fv457_url_label($p['source']).' · <strong>Limitation:</strong> '.fv457_h($p['limit']).'</p>';
  $o.='</li>';
 }
 return $o.'</ol><p class="fv457__evidence-question"><strong>For educators:</strong> Compare a Board finding with a later tribute. Which statements describe observed evidence, probable explanations, or later interpretation? Cite the source and its limits. All core research remains free.</p></section>';
}

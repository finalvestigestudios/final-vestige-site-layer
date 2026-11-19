#!/usr/bin/env python3
"""R469: adversarial editorial copy custody and unverified-link quarantine.
No remote NASA authentication or promotional rights certification occurs.
"""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'apollo_rights_gallery.php'
php=r'''
require %s;
$r=fv457_records();$cases=[];
foreach($r as $i=>$record){
 foreach(['role','credit','boundary','source_check'] as $field){
  $m=$r;$m[$i][$field].=' [UNREVIEWED MUTATION]';
  $cases[$record['id'].':'.$field]=fv457_valid($m);
 }
}
$bad=$r;[$bad[0]['boundary'],$bad[1]['boundary']]=[$bad[1]['boundary'],$bad[0]['boundary']];$cases['swapped_limitation']=fv457_valid($bad);
$bad=$r;$bad[4]['source_check']='NASA confirmed exact ID';$cases['false_verified_catalogue_claim']=fv457_valid($bad);
$cases['canonical']=fv457_valid($r);
$cases['held_cannot_link']=!fv457_source_link_eligible($r[4]);
$cases['valid_image_can_link']=fv457_source_link_eligible($r[0]);
$cases['article_can_link_without_confirming_id']=fv457_source_link_eligible($r[2]);
$markup=fv457_render();
$cases['source_cards']=substr_count($markup,'data-fv457-card=')===6;
$cases['three_plates']=substr_count($markup,'data-fv457-plate=')===3;
$cases['three_dates']=substr_count($markup,'class="fv457__moment"')===3;
$cases['single_contextual_cta']=substr_count($markup,'class="fv457__cta"')===1;
$cases['no_hypothetical_merchant']=!str_contains($markup,'payhip.com')&&!str_contains($markup,'affiliate_outbound');
$cases['held_url_not_linked']=!str_contains($markup,'href="https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129"');
$cases['hold_visible_in_screen_and_print']=substr_count($markup,'UNVERIFIED CATALOGUE LINK WITHHELD.')===1&&str_contains($markup,'Unverified catalogue lead — not a validated NASA source link.');
$cases['hold_is_in_catalogue']=str_contains($markup,'KSC-20170124-PH_KLS01_0129');
$cases['no_speculative_map']=!str_contains($markup,'data-lat=')&&!str_contains($markup,'data-lng=');
echo json_encode($cases,JSON_THROW_ON_ERROR);
''' % json.dumps(str(SOURCE))
results=json.loads(subprocess.check_output(['php','-r',php],text=True))
mutations={k:v for k,v in results.items() if ':' in k or k.startswith(('swapped_','false_'))}
assert len(mutations)==26,mutations
assert not any(mutations.values()), {k:v for k,v in mutations.items() if v}
positive={k:v for k,v in results.items() if k not in mutations}
assert len(positive)==13,positive
assert all(positive.values()),positive
print(f'PASS R469: {len(mutations)} adversarial claim mutations rejected; {len(positive)} link/safety/render contracts passed.')

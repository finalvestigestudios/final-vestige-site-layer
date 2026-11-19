#!/usr/bin/env python3
"""R468: enforce ID/date/source/placement tuples against accidental editorial swaps.
Local source-consistency only; does not establish URL availability or image rights.
"""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'apollo_rights_gallery.php'
script = r'''
require %s;
$r=fv457_records();
$cases=[];
$cases['original']=$r;
$swapped=$r;[$swapped[0]['source_url'],$swapped[1]['source_url']]=[$swapped[1]['source_url'],$swapped[0]['source_url']];$cases['accepted_url_swap']=$swapped;
$swapped=$r;[$swapped[1]['date'],$swapped[3]['date']]=[$swapped[3]['date'],$swapped[1]['date']];$cases['accepted_date_swap']=$swapped;
$swapped=$r;$swapped[4]['source_url']=$r[5]['source_url'];$cases['held_url_replaced_with_nasa']=$swapped;
$swapped=$r;$swapped[2]['source_status']='accepted';$swapped[1]['source_status']='id_hold';$cases['status_reassignment']=$swapped;
$swapped=$r;$swapped[1]['date_label']='28 January 1967';$cases['misleading_visible_date']=$swapped;
$swapped=$r;$swapped[2]['homepage_confirmed']=false;$swapped[3]['homepage_confirmed']=true;$cases['homepage_reassignment']=$swapped;
$swapped=$r;$swapped[0]['shown']=false;$swapped[3]['shown']=true;$cases['atlas_placement_swap']=$swapped;
$swapped=$r;$swapped[5]['id']='NEW-UNREVIEWED';$cases['unreviewed_id']=$swapped;
$swapped=$r;$swapped[4]['date']='2017-01-24';$swapped[4]['precision']='day';$cases['invented_day_from_id']=$swapped;
$swapped=$r;$swapped[3]['source_url']='https://www.nasa.gov/image-detail/amf-s66-58038/';$cases['wrong_valid_nasa_url']=$swapped;
$swapped=$r;$swapped[0]['source_url']='https://not-nasa.example/image/';$cases['offsite_url']=$swapped;
$swapped=$r;$swapped[0]['source_url']='https://www.nasa.gov/image-detail/amf-s66-58038/?new=1';$cases['query_added']=$swapped;
$swapped=$r;$swapped[0]['date']='1966-02-30';$cases['invalid_calendar_day']=$swapped;
$out=[];foreach($cases as $key=>$c)$out[$key]=fv457_valid($c);echo json_encode($out,JSON_THROW_ON_ERROR);
''' % json.dumps(str(SOURCE))
checks = json.loads(subprocess.check_output(['php', '-r', script], text=True))
assert checks['original'] is True, 'canonical source records must remain renderable'
assert len(checks) == 14
assert all(v is False for k,v in checks.items() if k != 'original'), checks
markup = subprocess.check_output(['php', '-r', f'require {json.dumps(str(SOURCE))}; echo fv457_render();'], text=True)
assert markup.count('data-fv457-card=') == 6
assert markup.count('data-fv457-plate=') == 3
assert markup.count('class="fv457__moment"') == 3
assert markup.count('class="fv457__cta"') == 1
assert markup.count('Source acceptance HOLD:') == 1
assert 'NASA source and rights limits — S67-19766' in markup
assert 'KSC-20170124-PH_KLS01_0129' in markup
assert 'utm_' not in markup
print('PASS R468: 13/13 pairing mutations rejected; canonical six cards, three plates, three chronology moments, one free CTA and visible HOLD verified (8 assertions).')

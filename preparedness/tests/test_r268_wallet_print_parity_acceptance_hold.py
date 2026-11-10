"""Adversarial bounded browser evidence tests; no safety/QD approval."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'tools/r268_wallet_print_parity_acceptance_hold.py'
spec = importlib.util.spec_from_file_location('r268', PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def fixtures():
    text = ('UNAPPROVED REVIEW CONCEPT. Do not distribute or enter real personal details. '
            + ' '.join(gate.WARNINGS) + ' ' + ' '.join(gate.FIELDS))
    r = {'state':gate.HOLD, **{k:False for k in gate.FALSE_STATES}}
    for source, widths in (('original',gate.ORIGINAL_WIDTHS),('preview',gate.WIDTHS)):
        r[source] = {'screen':{}, 'print':{}}
        for w, observed in zip(gate.WIDTHS,widths):
            r[source]['screen'][str(w)] = {'document_css_px':observed,
                'card_css_px':672, 'front_and_back_visible':[True,True]}
        for js in (True,False):
            r[source]['print'][str(js)] = {'card_width':672,'card_height':206,
               'face_widths':[335,335],
               'privacy_font_px':['10.6667px','10.6667px'],
               'sha256':'not compared on purpose'}
    ts = {f'{name}_js_{js}':text for name in ('original','preview') for js in (0,1)}
    ps = {key:1 for key in ts}
    return r,ts,ps

class Positive(unittest.TestCase):
    def test_base_positive_but_still_held(self):
        result=gate.inspect(*fixtures())
        self.assertEqual(result['state'],gate.HOLD)
        self.assertIs(result['independent_qd_pass'],False)
        self.assertIs(result['release_authorized'],False)
    def test_pdf_sha_difference_does_not_fail_geometry_or_text(self):
        r,t,p=fixtures()
        r['original']['print']['True']['sha256']='abc'
        r['preview']['print']['False']['sha256']='def'
        self.assertEqual(gate.inspect(r,t,p)['state'],gate.HOLD)

# Independent mutations: each of these must independently fail closed.
MUTATORS = {}
def add(name, f):
    MUTATORS[name]=f

def flip_status(k):
    def fn(r,t,p):r[k]=True
    return fn
for k in gate.FALSE_STATES:
    add('approval_'+k, flip_status(k))
for which in ('original','preview'):
    add('missing_'+which,lambda r,t,p,src=which:r.pop(src))
    add('missing_screen_'+which,lambda r,t,p,src=which:r[src].pop('screen'))
    add('missing_print_'+which,lambda r,t,p,src=which:r[src].pop('print'))
    for w in gate.WIDTHS:
        add(f'width_{which}_{w}',lambda r,t,p,src=which,w=w:r[src]['screen'][str(w)].update(document_css_px=999))
        add(f'warning_hidden_{which}_{w}',lambda r,t,p,src=which,w=w:r[src]['screen'][str(w)].update(front_and_back_visible=[True,False]))
        add(f'card_zero_{which}_{w}',lambda r,t,p,src=which,w=w:r[src]['screen'][str(w)].update(card_css_px=0))
    for js in ('True','False'):
        add(f'print_card_width_{which}_{js}',lambda r,t,p,src=which,j=js:r[src]['print'][j].update(card_width=550))
        add(f'print_card_height_{which}_{js}',lambda r,t,p,src=which,j=js:r[src]['print'][j].update(card_height=260))
        add(f'print_face_width_{which}_{js}',lambda r,t,p,src=which,j=js:r[src]['print'][j].update(face_widths=[335,500]))
        add(f'print_face_count_{which}_{js}',lambda r,t,p,src=which,j=js:r[src]['print'][j].update(face_widths=[335]))
        add(f'print_font_{which}_{js}',lambda r,t,p,src=which,j=js:r[src]['print'][j].update(privacy_font_px=['5px','5px']))
        key=f'{which}_js_{int(js=='True')}'
        add(f'pages_{key}',lambda r,t,p,key=key:p.__setitem__(key,2))
        add(f'pdf_no_warning_{key}',lambda r,t,p,key=key:t.__setitem__(key,t[key].replace(gate.WARNINGS[0],'removed')))
        add(f'pdf_no_field_{key}',lambda r,t,p,key=key:t.__setitem__(key,t[key].replace(gate.FIELDS[0],'removed')))
        add(f'pdf_no_review_label_{key}',lambda r,t,p,key=key:t.__setitem__(key,t[key].replace(gate.REVIEW_WARNING,'removed')))

class Negative(unittest.TestCase):
    pass

def generate_test(name, mutate):
    def test(self):
        r,t,p=fixtures()
        mutate(r,t,p)
        with self.assertRaises(ValueError):gate.inspect(r,t,p)
    test.__name__='test_'+name
    return test
for name,fn in MUTATORS.items():
    setattr(Negative,'test_'+name,generate_test(name,fn))

if __name__=='__main__':unittest.main()

"""R351: classify *captured* public Jetpack subscribe markup, offline.

No network, no form submission, no cookies, no subscriber data, no authorization to send.
HTML evidence is NOT a confirmed_signup or a proof of email eligibility.
"""
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs
import json
import re
import sys

class Survey(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms = []
        self.links = []
        self.inputs = []
        self.buttons = []
        self._form = None
        self._in_button = False
        self._button_text = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form':
            self._form = {'action': a.get('action',''), 'inputs': [], 'buttons': []}
            self.forms.append(self._form)
        if tag == 'input':
            item = {'type':a.get('type','text').lower(), 'name':a.get('name',''), 'placeholder':a.get('placeholder','')}
            self.inputs.append(item)
            if self._form is not None: self._form['inputs'].append(item)
        if tag == 'button':
            self._in_button=True
            if self._form is not None: self._form['buttons'].append(a.get('type','submit').lower())
        if tag == 'a':
            self.links.append({'href':a.get('href',''), 'class':a.get('class',''), 'aria':a.get('aria-label','')})
    def handle_endtag(self, tag):
        if tag=='form': self._form=None
        if tag=='button': self._in_button=False

def analyze_markup(html, page_url='https://finalvestige.com/dispatch/'):
    """Return structural observations, NEVER release clearance or delivery evidence."""
    if not isinstance(html, str) or len(html)>2_000_000: raise ValueError('Invalid/oversize captured HTML')
    s=Survey(); s.feed(html)
    candidate_forms=[f for f in s.forms if any(i['type']=='email' for i in f['inputs'])]
    submit_forms=[f for f in candidate_forms if ('submit' in f['buttons'] or any(i['type']=='submit' for i in f['inputs']))]
    selflinks=[]
    page=urlparse(page_url)
    for a in s.links:
        u=urlparse(a['href'])
        same=(not u.netloc or u.netloc==page.netloc) and (u.path.rstrip('/') in ('',page.path.rstrip('/')))
        args=parse_qs(u.query)
        if same and (args.get('p')==['523'] or 'subscribe' in (a['class']+' '+a['aria']).lower()):
            selflinks.append(a['href'])
    if submit_forms: form_status='EMAIL_SUBMIT_CONTROL_OBSERVED_NOT_TESTED'
    elif candidate_forms: form_status='EMAIL_INPUT_WITHOUT_SUBMIT_OBSERVED'
    elif selflinks: form_status='SELF_LINK_FALLBACK_OBSERVED_GUEST_UNKNOWN'
    else: form_status='NO_EMAIL_CONTROL_OBSERVED_GUEST_UNKNOWN'
    return {'form_status':form_status, 'email_form_count':len(candidate_forms),
      'submit_control_count':len(submit_forms), 'self_link_count':len(selflinks),
      'browser_guest_verified':False, 'submission_performed':False,
      'confirmed_signup':None, 'welcome_received':None,'eligible_recipients':None,
      'unsubscribe_functional':None,'paid_orders':None,'no_send':True}

def classify_subscriber_aggregates(status, follower_counts):
    """Keep platform counters separate; never infer a distinct recipient number."""
    keys=('total','confirmed','unconfirmed')
    if not isinstance(status,dict) or not isinstance(follower_counts,dict): raise ValueError('Expected aggregates')
    for k in keys:
        if type(status.get(k)) is not int or status[k]<0: raise ValueError('Malformed aggregate: '+k)
    for k in ('wpcom','email'):
        v=follower_counts.get(k)
        if type(v) is not int or v<0: raise ValueError('Malformed follower '+k)
    return {'counts':{k:status[k] for k in keys},
        'follower_sources':{k:follower_counts[k] for k in ('wpcom','email')},
        'overlapping_or_nonexclusive':status['confirmed']+status['unconfirmed']>status['total'],
        'distinct_eligible_inboxes':None,'verified_confirmed_signup_events':None,
        'welcome_received':None,'count_addition_forbidden':True,'send_authorized':False}

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1].startswith('http'):
        raise SystemExit('Usage: python guest_snapshot_classifier.py LOCAL_SAVED_HTML_FILE (NO URLs, NO requests)')
    with open(sys.argv[1],encoding='utf-8') as f: html=f.read()
    print(json.dumps(analyze_markup(html),indent=2))

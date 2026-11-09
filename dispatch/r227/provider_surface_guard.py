"""Read-only structural inspection of WordPress rendered Subscribe blocks.

DOES NOT simulate Jetpack, run JavaScript, contact a recipient, or certify signup.
CLI accepts an offline rendered HTML page file, never a URL or email address.
"""
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urlparse,parse_qs
import json,sys

class _Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.blocks=[];self.active=[]
        self.void={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def handle_starttag(self, tag,attrs):
        a=dict(attrs); classes=set((a.get('class') or '').split())
        if tag in ('div','section') and 'wp-block-jetpack-subscriptions' in classes:
            self.blocks.append({'forms':0,'email_inputs':0,'submit_buttons':0,'self_links':[], 'other_links':[], 'html_elements':0, 'disabled_email_inputs':0})
            self.active.append((len(self.stack), len(self.blocks)-1))
        # Parse actual tags, not CSS strings containing '<input', attributes, or comments.
        for _,j in self.active:
            b=self.blocks[j];b['html_elements']+=1
            if tag=='form': b['forms']+=1
            if tag=='input' and (a.get('type') or '').lower()=='email':
                b['email_inputs']+=1
                if 'disabled' in a: b['disabled_email_inputs']+=1
            if (tag=='button' or (tag=='input' and (a.get('type') or '').lower()=='submit')):b['submit_buttons']+=1
            if tag=='a' and a.get('href'):
                href=unescape(a['href']);u=urlparse(href)
                if u.scheme=='https' and u.netloc.lower()=='finalvestige.com' and parse_qs(u.query).get('post_type')==['page'] and 'p' in parse_qs(u.query): b['self_links'].append(href)
                else:b['other_links'].append(href)
        if tag not in self.void:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.void:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag not in self.stack:return
        ix=len(self.stack)-1-self.stack[::-1].index(tag)
        self.stack=self.stack[:ix]
        self.active=[(d,j) for d,j in self.active if d<ix]

def inspect(html,expected_page_id):
    if not isinstance(html,str) or not html.strip():return {'status':'NO_EVIDENCE','blocks':0}
    p=_Blocks();p.feed(html)
    if not p.blocks:return {'status':'NO_SUBSCRIBE_BLOCK_IN_CAPTURE','blocks':0}
    failures=[]
    for b in p.blocks:
        actual=[x for x in b['self_links'] if parse_qs(urlparse(x).query).get('p')==[str(expected_page_id)]]
        if b['email_inputs']>b['disabled_email_inputs'] and b['forms'] and b['submit_buttons']:
            state='HTML_FORM_PRESENT_REQUIRES_BROWSER_AND_PROVIDER_VERIFICATION'
        elif actual and b['email_inputs']==0 and b['forms']==0:
            state='SAME_PAGE_LINK_ONLY_REQUIRES_BROWSER_VERIFICATION'
        elif b['email_inputs'] and b['email_inputs']==b['disabled_email_inputs']:
            state='DISABLED_INPUT_REQUIRES_BROWSER_VERIFICATION'
        else:
            state='UNKNOWN_SUBSCRIBE_MARKUP_REQUIRES_BROWSER_VERIFICATION'
        failures.append(state)
    # No status is a confirmed signup, email-delivery or deployment failure.
    return {'status': ' | '.join(failures),'blocks':len(p.blocks), 'details':p.blocks,
            'confirmed_signup':None,'deliverable_recipient_count':None,'test_send_authorized':False}

if __name__=='__main__':
    if len(sys.argv)!=3 or not sys.argv[2].isdigit():raise SystemExit('Usage: python provider_surface_guard.py LOCAL_HTML_FILE PAGE_ID')
    from pathlib import Path
    src=Path(sys.argv[1]);
    if src.stat().st_size>3_000_000:raise SystemExit('Maximum local file size 3MB')
    print(json.dumps(inspect(src.read_text(encoding='utf8'),int(sys.argv[2])),indent=2,ensure_ascii=False))

#!/usr/bin/env python3
"""Read-only HTML contract for a WordPress Focus route export.

Never attempts a subscription or claims a WP API HTML fragment proves the
runtime browser experience. Intended as a conversion-release HOLD tripwire.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse,parse_qs


class Elements(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)


def examine(raw, *, source='WP public page content export'):
    p=Elements();p.feed(raw)
    elements=p.tags
    forms=[a for tag,a in elements if tag=='form']
    email=[a for tag,a in elements if tag=='input' and a.get('type','').lower()=='email']
    subscribes=[a for tag,a in elements if 'wp-block-jetpack-subscriptions' in a.get('class','').split()]
    anchors=[a for tag,a in elements if tag=='a']
    focus_anchor=any(a.get('id')=='subscribe-blog' for _,a in elements)
    self_links=[]
    for a in anchors:
        h=a.get('href','').replace('&amp;','&')
        u=urlparse(h)
        if u.hostname in ('finalvestige.com','www.finalvestige.com') and u.path=='/' and parse_qs(u.query).get('p')==['1579']:
            self_links.append(h)
    blue=[a.get('style','') for a in anchors if '#113AF5' in a.get('style','').upper() or '#113af5' in a.get('style','').lower()]
    # A native form tag without a form email input does not establish a usable opt-in.
    native=bool(forms and email and any(a.get('type')=='submit' for tag,a in elements if tag in ('button','input')))
    flags=[]
    if not subscribes: flags.append('JETPACK_BLOCK_NOT_FOUND')
    if not focus_anchor: flags.append('FOCUS_JUMP_TARGET_MISSING')
    if not native: flags.append('NO_NATIVE_SUBSCRIBE_FORM_IN_EXPORTED_MARKUP')
    if self_links:flags.append('SUBSCRIBE_FALLBACK_LINKS_TO_SAME_PAGE')
    if blue:flags.append('INLINE_NON_BRAND_BLUE_SUBSCRIBE_LINK')
    return {'source':source,'evidence_level':'exported WordPress HTML, NOT browser-rendered signup',
            'status':'HOLD_FOR_RUNTIME_CONFIRMATION' if flags else 'STATIC_MARKUP_PRESENT_RUNTIME_UNVERIFIED',
            'counts':{'forms':len(forms),'email_inputs':len(email),'jetpack_containers':len(subscribes),
                      'self_loop_fallbacks':len(self_links),'inline_blue_fallbacks':len(blue)},
            'focus_anchor':focus_anchor,'flags':flags,
            'cannot_infer':['Jetpack hydration','confirmed subscriber','email delivery','paid order','net revenue']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--page',type=Path,required=True,help='PUBLIC WP view-content HTML export, never a private database')
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    result=examine(a.page.read_text(encoding='utf-8'),source=str(a.page))
    s=json.dumps(result,indent=2)
    print(s)
    if a.out:a.out.write_text(s+'\n')
    # No forms can be a legitimate JS-rendered Jetpack variant; HOLD, not a
    # conclusion that the production widget cannot subscribe.
    return 2 if result['status']=='HOLD_FOR_RUNTIME_CONFIRMATION' else 0


if __name__=='__main__':raise SystemExit(main())

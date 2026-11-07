#!/usr/bin/env python3
"""R188 standalone build: verified R187 assets, no-JS first-party campaign continuity."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'apollo-r187'/'dist'
OUT=ROOT/'dist'
PINS={
 'php':'8bf0264087d00dc80aa05927bf0cffc6c2855e6d2d99fbd6faaffd94ca741fa0',
 'html':'f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315',
 'css':'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6'
}
def sha(data):return hashlib.sha256(data).hexdigest()
HANDOFF=r'''/**
 * Public source labels ONLY. NOT proof of qualified visitors, leads,
 * customer orders, consent, affiliate sales or realized net revenue.
 * No JS, new analytics tag, cookie, pixels or checkout.
 */
function fv_ex2_r188_campaign_handoff($html) {
    $names=array('utm_source','utm_medium','utm_campaign','utm_content');
    foreach ($names as $name) {
        if (!isset($_GET[$name]) || !is_string($_GET[$name])) return $html;
    }
    $source=$_GET['utm_source']; $medium=$_GET['utm_medium'];
    $campaign=$_GET['utm_campaign']; $asset=$_GET['utm_content'];
    if (!in_array($source,array('youtube','tiktok','instagram','facebook','pinterest','x','bluesky'),true)) return $html;
    if ($medium !== 'organic_social') return $html;
    if (!preg_match('/\\Ahistory_pilot_20[0-9]{2}_(0[1-9]|1[0-2])\\z/D',$campaign)) return $html;
    if (!preg_match('/\\A[a-z0-9][a-z0-9_-]{3,63}\\z/D',$asset)) return $html;
    $dest='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
    $needle='<a class="cta" href="'.$dest.'">';
    if (substr_count($html,$needle)!==1) return $html;
    $query=http_build_query(array(
        'utm_source'=>$source,'utm_medium'=>$medium,
        'utm_campaign'=>$campaign,'utm_content'=>$asset
    ),'','&',PHP_QUERY_RFC3986);
    $href=htmlspecialchars($dest.'?'.$query,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');
    return str_replace($needle,'<a class="cta" href="'.$href.'">',$html);
}

'''
def build():
    parts={'php':(PREV/'fv-ex2-apollo-r187.php').read_bytes(),
      'html':(PREV/'templates/atlas-fragment.html').read_bytes(),
      'css':(PREV/'assets/atlas-scoped.css').read_bytes()}
    for key,data in parts.items():
        if sha(data)!=PINS[key]:raise RuntimeError('R187 SHA-256 source drift: '+key)
    old=parts['php'].decode('utf-8')
    if old.count('function fv_ex2_r187_render(')!=1 or old.count('    return $html;')!=1:
        raise RuntimeError('R187 PHP render contract changed')
    new=old.replace('r187','r188').replace('R187','R188')
    new=new.replace('    return $html;','    return fv_ex2_r188_campaign_handoff($html);',1)
    new=new.replace('function fv_ex2_r188_render(',HANDOFF+'function fv_ex2_r188_render(',1)
    (OUT/'templates').mkdir(parents=True,exist_ok=True)
    (OUT/'assets').mkdir(parents=True,exist_ok=True)
    (OUT/'fv-ex2-apollo-r188.php').write_text(new,encoding='utf-8')
    (OUT/'templates/atlas-fragment.html').write_bytes(parts['html'])
    (OUT/'assets/atlas-scoped.css').write_bytes(parts['css'])
    receipt={'status':'UNPUBLISHED; MOCK TESTS ONLY; NOT INSTALLED',
     'base':'R187 draft PR #1390','input_sha256':PINS,
     'output_sha256':{'php':sha(new.encode()),'html':sha(parts['html']),'css':sha(parts['css'])},
     'nasa_images_embedded':False,'analytics_added':False,
     'grok_asset_verified':False,'paid_orders_verified':False}
    (OUT/'manifest.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt
if __name__=='__main__':print(json.dumps(build(),indent=2))

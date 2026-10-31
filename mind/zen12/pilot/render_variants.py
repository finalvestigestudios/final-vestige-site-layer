#!/usr/bin/env python3
"""Render two offline, noindex Zen12 preview variants from PR #180 source.

Only the existing film-details element changes. No WordPress writes or tracking.
The film variant is forbidden until local original MP4 and poster hashes match.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
PILOT=Path(__file__).resolve().parent
START='<details class="fvz12__film">'
END='</details>'
VIDEO_SHA='eb4a3f7e7d95ce5a6ff1ba08c83e66a4f7cc94cb1e3784bd51a330650c41ab00'
POSTER_SHA='5b271178d83735c46df8c802d526ffcdeb01643b0b1672d32d335fb1059faa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def html_page(fragment):
    fragment=fragment.replace('<!-- wp:html -->','').replace('<!-- /wp:html -->','')
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>PRIVATE FV Zen12 study</title></head><body>'+fragment+'</body></html>'
def render(out,mp4=None,poster=None):
    baseline=(BASE/'page-zen12-guide.blocks.html').read_text('utf-8')
    assert baseline.count(START)==1 and baseline.count(END)==1
    assert 'data-fv-offer-state="unverified"' in baseline
    assert 'href="https://zen12.com/getstarted"' not in baseline
    a=out/'text';a.mkdir(parents=True,exist_ok=True)
    (a/'index.html').write_text(html_page(baseline),encoding='utf-8')
    if mp4 is None and poster is None:return {'text':'ready','film':'held_until_real_local_media'}
    if mp4 is None or poster is None or sha(mp4)!=VIDEO_SHA or sha(poster)!=POSTER_SHA:
        raise ValueError('Media missing or SHA mismatch: refuse unapproved preview')
    html_video=('<details class="fvz12__film" data-fv-variant="video">'
      '<summary>Watch the optional 40-second silent evidence film</summary>'
      '<p>Original illustration; independent results for Zen12 have not been established. This video is optional.</p>'
      '<figure><video controls preload="none" playsinline width="960" height="540" '
      'poster="media/poster.png" aria-label="Forty-second original silent evidence film about Zen12">'
      '<source src="media/film.mp4" type="video/mp4">'
      '<track kind="captions" src="media/captions.vtt" srclang="en" label="English captions" default>'
      'Your browser cannot play the film; read the full transcript below.</video>'
      '<figcaption>Editorial illustration, not a firsthand product test.</figcaption></figure>'
      '<details><summary>Full visual transcript</summary>'
      '<p><a href="media/transcript.md">Read the original film transcript</a></p></details>'
      '<p class="fvz12__disclosure"><strong>Commercial disclosure:</strong> If a future approved qualifying'
      ' product link becomes available and you purchase through it, Final Vestige may earn a commission.'
      ' No purchase link is active.</p></details>')
    i=baseline.index(START);j=baseline.index(END,i)+len(END)
    altered=baseline[:i]+html_video+baseline[j:]
    assert altered[:i]==baseline[:i] and altered[i+len(html_video):]==baseline[j:]
    b=out/'video';media=b/'media';media.mkdir(parents=True,exist_ok=True)
    (b/'index.html').write_text(html_page(altered),encoding='utf-8')
    shutil.copyfile(mp4,media/'film.mp4')
    shutil.copyfile(poster,media/'poster.png')
    shutil.copyfile(PILOT/'video/captions.vtt',media/'captions.vtt')
    shutil.copyfile(PILOT/'video/transcript.md',media/'transcript.md')
    return {'text':'ready','video':'offline_only','except_film_source_identical':True}
if __name__=='__main__':
    z=argparse.ArgumentParser();z.add_argument('--out',type=Path,required=True)
    z.add_argument('--mp4',type=Path);z.add_argument('--poster',type=Path)
    x=z.parse_args();print(json.dumps(render(x.out,x.mp4,x.poster),indent=2))

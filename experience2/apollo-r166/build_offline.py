"""R166: build a review-only offline archive decoupling + image fallback preview.

Input must be an exact current WordPress editor export. Never calls WordPress.
The predecessor patcher rejects changed source instead of guessing replacements.
Do NOT install output without founder + production engineering governed approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from stage_patch import patch

HERE = Path(__file__).resolve().parent
REQUIRED_NASA = (
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129',
)
def build(source):
    if source.count('class="fvx-chrono-gallery" data-fvx-chrono-gallery') != 1:
        raise ValueError('HOLD: require exactly one gallery')
    if any(source.count(anchor) != 1 for anchor in REQUIRED_NASA):
        raise ValueError('HOLD: NASA citation absent, duplicated, or changed')
    js = '\n'.join((HERE / n).read_text(encoding='utf8') for n in ('gallery-independent.js', 'gallery-fallback.js'))
    css = '\n'.join((HERE / n).read_text(encoding='utf8') for n in ('gallery-independent.css', 'gallery-fallback.css'))
    result = patch(source, js, css)
    if 'const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);' in result:
        raise AssertionError('HOLD: fire-seconds/gallery coupling survived')
    return result

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('source', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    src = args.source.read_text(encoding='utf8')
    output = build(src)
    args.output.write_text(output, encoding='utf8')
    evidence = {'source_sha256': hashlib.sha256(src.encode()).hexdigest(),
                'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
                'install_status': 'OFFLINE_STAGING_HOLD', 'wordPress_writes': 0}
    args.output.with_suffix('.manifest.json').write_text(json.dumps(evidence,sort_keys=True,indent=2))
    print(json.dumps(evidence,sort_keys=True))

if __name__=='__main__': main()

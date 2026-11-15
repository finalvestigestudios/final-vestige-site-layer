#!/usr/bin/env python3
"""R373 production-host guard regression checks; no website visited."""
from staging_acceptance import validate_staging

good=['https://preview.example.org/apollo-1/','https://preview.example.org/apollo-1']
bad=[
 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
 'https://www.finalvestige.com/apollo/', 'http://preview.example.org/apollo/',
 'https://preview.example.org/wp-admin/', 'https://preview.example.org/wp-login.php',
 'https://preview.example.org/wp-json/wp/v2/posts',
 'https://preview.example.org/apollo/?secret=abc', 'https://preview.example.org/apollo/#key',
 'https://preview.example.org:9443/apollo/', 'https://another.example.org/apollo/',
 'https://u:p@preview.example.org/apollo/', 'javascript:alert(1)',
]
for x in good:
    assert validate_staging(x, 'preview.example.org')
for x in bad:
    try: validate_staging(x, 'preview.example.org')
    except ValueError: pass
    else: raise AssertionError('unsafe accepted '+x)
for h in ['finalvestige.com','www.finalvestige.com','localhost','127.0.0.1']:
    try: validate_staging('https://'+h+'/apollo/',h)
    except ValueError: pass
    else: raise AssertionError('production/local host accepted '+h)
print('R373 preflight guard PASS:',len(good)+len(bad)+4,'cases')

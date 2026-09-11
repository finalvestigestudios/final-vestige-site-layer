#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'final-vestige-deployment-bridge'
files = list(PLUGIN.rglob('*.php'))
text = '\n'.join(p.read_text(encoding='utf-8') for p in files)
errors=[]

def need(pattern,label):
    if not re.search(pattern,text,re.S): errors.append('missing: '+label)

need(r"FVDB_EXPECTED_REPOSITORY'.*finalvestigestudios/final-vestige-site-layer",'repository allowlist')
need(r"FVDB_EXPECTED_BRANCH'.*production",'production branch allowlist')
need(r"hash_hmac\('sha256'",'HMAC-SHA256')
need(r"MAX_SKEW\s*=\s*300",'timestamp window')
need(r"get_transient\(\$nonce_key\)",'replay check')
need(r"set_transient\(\$nonce_key",'replay burn')
need(r"authentication_failed",'generic auth response')
need(r"get_filesystem_method\(\)\s*!==\s*'direct'",'direct filesystem gate')
need(r"MAX_ENTRIES\s*=\s*400",'total ZIP entry limit')
need(r"encrypted_zip_rejected",'encrypted ZIP rejection')
need(r"duplicate_zip_entry",'duplicate ZIP rejection')
need(r"getStream\(\$name\)",'streamed extraction')
need(r"manifest_file_set_mismatch",'pre-swap exact file set')
need(r"post_swap_file_set_mismatch",'post-swap exact file set')
need(r"non_regular_file_rejected",'symlink/non-regular rejection')
need(r"fv-deploy-backups",'rollback outside plugins')
need(r"post_swap_verification_failed",'post-swap hash verification')
if 'extractTo(' in text: errors.append('unsafe: ZipArchive::extractTo present')
if 'activate_plugin(' in text: errors.append('unsafe: auto-activation present')
if re.search(r"record_authenticated_error\([^\)]*auth", text): errors.append('unsafe: auth failures may write state')
if errors:
    print('BRIDGE STATIC VERIFY: FAIL')
    print('\n'.join('- '+e for e in errors)); sys.exit(1)
print('BRIDGE STATIC VERIFY: PASS')
for p in sorted(files):
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())

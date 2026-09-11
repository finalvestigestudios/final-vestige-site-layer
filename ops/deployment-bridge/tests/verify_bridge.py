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

def forbid(pattern,label):
    if re.search(pattern,text,re.S): errors.append('unsafe: '+label)

need(r"FVDB_EXPECTED_REPOSITORY'.*finalvestigestudios/final-vestige-site-layer",'repository allowlist')
need(r"FVDB_EXPECTED_BRANCH'.*production",'production branch allowlist')
need(r"hash_hmac\('sha256'",'HMAC-SHA256')
need(r"MAX_SKEW\s*=\s*300",'timestamp window')
need(r"NONCE_PREFIX",'nonce namespace')
need(r"add_option\(\$key,\s*\$expires",'atomic replay claim')
need(r"fvdb_deployment_mutex_v1",'deployment mutex')
need(r"add_option\(self::OPTION_LOCK",'atomic mutex acquisition')
need(r"SELECT option_value FROM .*options.*option_name = %s",'exact raw option read for lease CAS')
need(r"DELETE FROM .*options.*option_name = %s AND BINARY option_value = BINARY %s",'value-bound CAS delete')
need(r"maybe_unserialize\(\$raw\)",'raw option lease decode')
need(r"last_idempotency_key",'explicit idempotency state')
need(r"already_deployed",'idempotent response')
need(r"installed_matches",'idempotency byte re-verification')
need(r"authenticate_status",'authenticated status')
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
need(r"target_swap_rollback_failed",'swap rollback verification')
need(r"post_swap_rollback_failed",'post-swap rollback verification')
forbid(r"get_transient\(|set_transient\(",'non-atomic transient replay guard present')
forbid(r"extractTo\(",'ZipArchive::extractTo present')
forbid(r"activate_plugin\(",'auto-activation present')
forbid(r"delete_option\(self::OPTION_LOCK\)",'unconditional deployment-lock deletion')
forbid(r"delete_option\(\$key\)",'unconditional nonce deletion')
forbid(r"'site_layer'\s*=>",'status leaks site-layer deployment state')
forbid(r"'last_status'\s*=>\s*\$state",'status leaks deployment history')
if errors:
    print('BRIDGE STATIC VERIFY: FAIL')
    print('\n'.join('- '+e for e in errors)); sys.exit(1)
print('BRIDGE STATIC VERIFY: PASS')
for p in sorted(files):
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
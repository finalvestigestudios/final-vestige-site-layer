#!/usr/bin/env python3
from pathlib import Path
import concurrent.futures, hashlib, hmac, os, shutil, subprocess, tempfile, time

ROOT = Path(__file__).resolve().parents[1]
PHP = ROOT / 'tests' / 'runtime_bridge.php'
SECRET = 'a' * 64
COMMIT = 'a' * 40
BODY_SHA = hashlib.sha256(b'{}').hexdigest()

def run_scenario(name: str):
    td = Path(tempfile.mkdtemp(prefix='fvdb-test-'))
    store = td / 'options.json'
    env = os.environ.copy(); env['FVDB_TEST_ROOT'] = str(td / 'root')
    try:
        p = subprocess.run(['php', str(PHP), name, str(store)], text=True, capture_output=True, env=env, timeout=20)
        if p.returncode != 0 or p.stdout.strip() != 'PASS':
            raise RuntimeError(f'{name} failed rc={p.returncode} out={p.stdout!r} err={p.stderr!r}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def replay_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-replay-')); store = td / 'options.json'
    ts = str(int(time.time())); nonce = 'race_nonce_abcdefghijklmnop'
    canonical = '\n'.join([ts, nonce, 'finalvestigestudios/final-vestige-site-layer', 'production', COMMIT, BODY_SHA])
    sig = 'sha256=' + hmac.new(SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    args = ['php', str(PHP), 'replay_worker', str(store), SECRET, ts, nonce, COMMIT, BODY_SHA, sig]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            results = list(ex.map(lambda _: subprocess.run(args, text=True, capture_output=True, timeout=10).stdout.strip(), range(12)))
        if results.count('OK') != 1 or results.count('replay_rejected') != 11:
            raise RuntimeError(f'replay race expected 1 winner/11 rejects, got {results}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def lock_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-lock-')); store = td / 'options.json'
    args = ['php', str(PHP), 'lock_worker', str(store)]
    try:
        procs = [subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(10)]
        results = [p.communicate(timeout=10)[0].strip() for p in procs]
        if results.count('ACQUIRED') != 1 or results.count('deployment_busy') != 9:
            raise RuntimeError(f'lock race expected 1 owner/9 busy, got {results}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

for scenario in [
    'auth_stale_bad','status_surface','package_valid','unsafe_path','duplicate_entry','encrypted_entry',
    'malformed_zip','oversized_zip','expanded_zip','manifest_mismatch','target_swap_rollback','post_swap_rollback'
]:
    run_scenario(scenario)
replay_race(); lock_race()
print('BRIDGE RUNTIME VERIFY: PASS')
print('scenarios=14 replay_workers=12 lock_workers=10')

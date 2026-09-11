#!/usr/bin/env python3
from pathlib import Path
import concurrent.futures, hashlib, hmac, json, os, shlex, shutil, subprocess, tempfile, time

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / 'tests' / 'runtime_bridge.php'
PHP_CMD = shlex.split(os.environ.get('FVDB_TEST_PHP_CMD', 'php'))
SECRET = 'a' * 64
COMMIT = 'a' * 40
BODY_SHA = hashlib.sha256(b'{}').hexdigest()

def php_args(*args: str):
    return [*PHP_CMD, str(HARNESS), *args]

def run_scenario(name: str):
    td = Path(tempfile.mkdtemp(prefix='fvdb-test-'))
    store = td / 'options.json'
    env = os.environ.copy(); env['FVDB_TEST_ROOT'] = str(td / 'root')
    try:
        p = subprocess.run(php_args(name, str(store)), text=True, capture_output=True, env=env, timeout=20)
        if p.returncode != 0 or p.stdout.strip() != 'PASS':
            raise RuntimeError(f'{name} failed rc={p.returncode} out={p.stdout!r} err={p.stderr!r}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def signed_replay_args(store: Path, nonce: str):
    ts = str(int(time.time()))
    canonical = '\n'.join([ts, nonce, 'finalvestigestudios/final-vestige-site-layer', 'production', COMMIT, BODY_SHA])
    sig = 'sha256=' + hmac.new(SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return php_args('replay_worker', str(store), SECRET, ts, nonce, COMMIT, BODY_SHA, sig)

def replay_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-replay-')); store = td / 'options.json'
    args = signed_replay_args(store, 'race_nonce_abcdefghijklmnop')
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            results = list(ex.map(lambda _: subprocess.run(args, text=True, capture_output=True, timeout=10).stdout.strip(), range(12)))
        if results.count('OK') != 1 or results.count('replay_rejected') != 11:
            raise RuntimeError(f'replay race expected 1 winner/11 rejects, got {results}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def stale_replay_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-stale-replay-')); store = td / 'options.json'; barrier = td / 'barrier'
    nonce = 'stale_race_nonce_abcdefghijklmnop'
    key = 'fvdb_nonce_v2_' + hashlib.sha256(('deploy\n' + nonce).encode()).hexdigest()
    store.write_text(json.dumps({'fvdb_secret_v1': SECRET, key: int(time.time()) - 60}), encoding='utf-8')
    args = signed_replay_args(store, nonce)
    env = os.environ.copy(); env['FVDB_TEST_ROOT'] = str(td / 'root')
    env['FVDB_TEST_BARRIER_DIR'] = str(barrier); env['FVDB_TEST_BARRIER_KEY_PREFIX'] = 'fvdb_nonce_v2_'; env['FVDB_TEST_BARRIER_COUNT'] = '12'
    try:
        procs = [subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) for _ in range(12)]
        results = []
        for p in procs:
            out, err = p.communicate(timeout=15)
            if p.returncode != 0:
                raise RuntimeError(f'stale replay worker failed rc={p.returncode} out={out!r} err={err!r}')
            results.append(out.strip())
        if results.count('OK') != 1 or results.count('replay_rejected') != 11:
            raise RuntimeError(f'stale replay takeover expected 1 winner/11 rejects, got {results}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def lock_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-lock-')); store = td / 'options.json'
    args = php_args('lock_worker', str(store))
    try:
        procs = [subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(10)]
        results = [p.communicate(timeout=10)[0].strip() for p in procs]
        if results.count('ACQUIRED') != 1 or results.count('deployment_busy') != 9:
            raise RuntimeError(f'lock race expected 1 owner/9 busy, got {results}')
        state = json.loads(store.read_text(encoding='utf-8') or '{}')
        if int(state.get('__critical_max', 0)) != 1:
            raise RuntimeError(f'lock race critical section overlap detected: {state}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

def stale_lock_race():
    td = Path(tempfile.mkdtemp(prefix='fvdb-stale-lock-')); store = td / 'options.json'; barrier = td / 'barrier'
    stale = {'token':'stale-token', 'idempotency_key':'stale-idempotency', 'expires':int(time.time()) - 60}
    store.write_text(json.dumps({'fvdb_deployment_mutex_v1': stale}), encoding='utf-8')
    args = php_args('stale_lock_worker', str(store))
    env = os.environ.copy(); env['FVDB_TEST_ROOT'] = str(td / 'root')
    env['FVDB_TEST_BARRIER_DIR'] = str(barrier); env['FVDB_TEST_BARRIER_KEY_PREFIX'] = 'fvdb_deployment_mutex_v1'; env['FVDB_TEST_BARRIER_COUNT'] = '10'
    try:
        procs = [subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) for _ in range(10)]
        results = []
        for p in procs:
            out, err = p.communicate(timeout=15)
            if p.returncode != 0:
                raise RuntimeError(f'stale lock worker failed rc={p.returncode} out={out!r} err={err!r}')
            results.append(out.strip())
        if results.count('ACQUIRED') != 1 or results.count('deployment_busy') != 9:
            raise RuntimeError(f'stale lock takeover expected 1 owner/9 busy, got {results}')
        state = json.loads(store.read_text(encoding='utf-8') or '{}')
        if int(state.get('__critical_max', 0)) != 1:
            raise RuntimeError(f'stale lock critical section overlap detected: {state}')
    finally:
        shutil.rmtree(td, ignore_errors=True)

for scenario in [
    'auth_stale_bad','status_surface','package_valid','unsafe_path','duplicate_entry','encrypted_entry',
    'malformed_zip','oversized_zip','expanded_zip','manifest_mismatch','target_swap_rollback','post_swap_rollback'
]:
    run_scenario(scenario)
replay_race(); lock_race(); stale_replay_race(); stale_lock_race()
print('BRIDGE RUNTIME VERIFY: PASS')
print('scenarios=16 replay_workers=12 lock_workers=10 stale_replay_workers=12 stale_lock_workers=10 max_critical_overlap=1')
print('php_cmd=' + ' '.join(PHP_CMD))
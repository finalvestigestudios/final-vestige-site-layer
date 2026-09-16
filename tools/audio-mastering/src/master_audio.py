#!/usr/bin/env python3
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')
FFPROBE = os.environ.get('FFPROBE', 'ffprobe')

PAUSE_CLASSES = {
    'none': (0.00, 0.20),
    'punch': (0.12, 0.32),
    'thought': (0.25, 0.45),
    'reveal': (0.50, 0.75),
    'chapter': (0.80, 1.60),
}


def run(cmd, capture=True, check=True):
    p = subprocess.run(cmd, text=True, capture_output=capture)
    if check and p.returncode != 0:
        if capture:
            sys.stderr.write(p.stdout or '')
            sys.stderr.write(p.stderr or '')
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(shlex.quote(x) for x in cmd)}")
    return p


def ffprobe_duration(path):
    p = run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nk=1:nw=1', str(path)])
    return float(p.stdout.strip())


def ensure_file(base, p):
    path = (base / p).resolve() if not os.path.isabs(p) else Path(p).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def db_to_linear(db):
    return 10 ** (float(db) / 20.0)


def ms(sec):
    return max(0, int(round(float(sec) * 1000)))


def parse_loudnorm_json(stderr):
    candidates = re.findall(r'\{\s*"input_i".*?\}', stderr, flags=re.S)
    if not candidates:
        raise RuntimeError('Could not parse loudnorm JSON from ffmpeg output')
    return json.loads(candidates[-1])


def analyze_loudnorm(path, target_i, target_tp, target_lra):
    p = run([
        FFMPEG, '-hide_banner', '-nostats', '-i', str(path),
        '-af', f'loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:print_format=json',
        '-f', 'null', '-'
    ])
    return parse_loudnorm_json(p.stderr)


def analyze_ebur128(path):
    p = run([FFMPEG, '-hide_banner', '-nostats', '-i', str(path), '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'])
    s = p.stderr
    i_matches = re.findall(r'I:\s*(-?[0-9.]+) LUFS', s)
    lra_matches = re.findall(r'LRA:\s*([0-9.]+) LU', s)
    peak_matches = re.findall(r'Peak:\s*(-?[0-9.]+) dBFS', s)
    return {
        'integrated_lufs': float(i_matches[-1]) if i_matches else None,
        'lra_lu': float(lra_matches[-1]) if lra_matches else None,
        'true_peak_dbfs': float(peak_matches[-1]) if peak_matches else None,
    }


def astats_peak_rms(path):
    p = run([
        FFMPEG, '-hide_banner', '-nostats', '-i', str(path),
        '-af', 'astats=metadata=1:reset=0', '-f', 'null', '-'
    ])
    text = p.stderr
    peaks = re.findall(r'Peak level dB:\s*(-?[0-9.]+)', text)
    rms = re.findall(r'RMS level dB:\s*(-?[0-9.]+)', text)
    return {
        'peak_dbfs': float(peaks[-1]) if peaks else None,
        'rms_dbfs': float(rms[-1]) if rms else None,
    }


def detect_internal_silences(path, threshold_db=-45, min_duration=0.55):
    duration = ffprobe_duration(path)
    p = run([
        FFMPEG, '-hide_banner', '-nostats', '-i', str(path),
        '-af', f'silencedetect=noise={threshold_db}dB:d={min_duration}', '-f', 'null', '-'
    ], check=False)
    starts = [float(x) for x in re.findall(r'silence_start:\s*([0-9.]+)', p.stderr)]
    ends = [(float(a), float(b)) for a, b in re.findall(r'silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)', p.stderr)]
    events = []
    for i, start in enumerate(starts):
        if i < len(ends):
            end, d = ends[i]
        else:
            end, d = duration, duration - start
        if start <= 0.15 or end >= duration - 0.15:
            continue
        events.append({'start': round(start, 3), 'end': round(end, 3), 'duration': round(d, 3)})
    return events


def validate_pause_map(timeline, require_classes=False):
    errors = []
    for i, x in enumerate(timeline[:-1]):
        cls = x.get('pause_class')
        gap = float(x.get('gap_after', 0.25))
        if not cls:
            if require_classes:
                errors.append(f"{x.get('id', i)} missing pause_class")
            continue
        if cls not in PAUSE_CLASSES:
            errors.append(f"{x.get('id', i)} unknown pause_class={cls!r}")
            continue
        lo, hi = PAUSE_CLASSES[cls]
        if not (lo <= gap <= hi):
            errors.append(f"{x.get('id', i)} gap {gap:.3f}s outside {cls} range {lo:.2f}-{hi:.2f}s")
    return errors


def build_premaster(manifest, manifest_path, workdir):
    base = manifest_path.parent
    sr = int(manifest.get('sample_rate', 48000))
    tail = float(manifest.get('tail_seconds', 1.0))
    vocal = manifest.get('vocal_chain', {})

    beats = manifest.get('narration', [])
    if not beats:
        raise ValueError('manifest.narration must contain at least one beat')

    timeline = []
    cursor = float(manifest.get('head_seconds', 0.5))
    silence_qc = []
    max_internal = float(manifest.get('max_internal_silence_seconds', 0.70))
    for beat in beats:
        f = ensure_file(base, beat['file'])
        dur = ffprobe_duration(f)
        start = float(beat.get('start', cursor))
        silences = detect_internal_silences(f, min_duration=min(0.55, max_internal))
        long_silences = [s for s in silences if s['duration'] > max_internal]
        silence_qc.append({
            'id': beat.get('id'), 'file': str(f), 'detected_internal_silences': silences,
            'violations': [] if beat.get('allow_internal_silence', False) else long_silences,
        })
        timeline.append({**beat, '_file': f, '_duration': dur, '_start': start})
        cursor = start + dur + float(beat.get('gap_after', 0.25))
    total_duration = max(x['_start'] + x['_duration'] for x in timeline) + tail

    pause_errors = validate_pause_map(timeline, bool(manifest.get('require_pause_classes', False)))

    music_tracks = [{**m, '_file': ensure_file(base, m['file'])} for m in manifest.get('music', [])]
    sfx_tracks = [{**s, '_file': ensure_file(base, s['file'])} for s in manifest.get('sfx', [])]

    inputs = []
    for x in timeline:
        inputs += ['-i', str(x['_file'])]
    music_indexes = []
    for m in music_tracks:
        idx = len(timeline) + len(music_indexes)
        music_indexes.append(idx)
        inputs += (['-stream_loop', '-1'] if m.get('loop', True) else []) + ['-i', str(m['_file'])]
    sfx_indexes = []
    for s in sfx_tracks:
        idx = len(timeline) + len(music_tracks) + len(sfx_indexes)
        sfx_indexes.append(idx)
        inputs += ['-i', str(s['_file'])]

    filters = []
    voice_labels = []
    hp = float(vocal.get('highpass_hz', 80))
    warmth_hz = float(vocal.get('warmth_hz', 190)); warmth_db = float(vocal.get('warmth_db', 1.3))
    mud_hz = float(vocal.get('mud_hz', 350)); mud_db = float(vocal.get('mud_db', -1.5))
    presence_hz = float(vocal.get('presence_hz', 3200)); presence_db = float(vocal.get('presence_db', 1.3))
    air_hz = float(vocal.get('air_hz', 11000)); air_db = float(vocal.get('air_db', 1.0))
    deess_i = float(vocal.get('deesser_intensity', 0.15))

    for i, x in enumerate(timeline):
        delay = ms(x['_start'])
        label = f'v{i}'
        filters.append(
            f'[{i}:a]aformat=sample_rates={sr}:channel_layouts=stereo,'
            f'highpass=f={hp},'
            f'equalizer=f={warmth_hz}:t=q:w=1:g={warmth_db},'
            f'equalizer=f={mud_hz}:t=q:w=1.1:g={mud_db},'
            f'equalizer=f={presence_hz}:t=q:w=1:g={presence_db},'
            f'equalizer=f={air_hz}:t=q:w=0.8:g={air_db},'
            f'deesser=i={deess_i},adelay={delay}|{delay}[{label}]'
        )
        voice_labels.append(f'[{label}]')
    filters.append(''.join(voice_labels) + f'amix=inputs={len(voice_labels)}:normalize=0:dropout_transition=0[voice_raw]')

    comp_threshold = vocal.get('compressor_threshold', '-20dB')
    comp_ratio = float(vocal.get('compressor_ratio', 2.75))
    attack = float(vocal.get('compressor_attack_ms', 30)); release = float(vocal.get('compressor_release_ms', 250))
    makeup = float(vocal.get('compressor_makeup', 1.0))
    filters.append(
        f'[voice_raw]acompressor=threshold={comp_threshold}:ratio={comp_ratio}:attack={attack}:release={release}:makeup={makeup},'
        f'alimiter=limit=0.98:attack=5:release=50,atrim=0:{total_duration},asplit=3[voice_mix][voice_key][voice_diag]'
    )

    mix_inputs = ['[voice_mix]']
    diag_maps = [('voice_diag', workdir / 'layer_voice.wav')]

    music_labels = []
    for j, m in enumerate(music_tracks):
        idx = music_indexes[j]
        gain = float(m.get('gain_db', 0.0))
        music_target = float(m.get('target_lufs', manifest.get('music_target_lufs', -23.0)))
        fade_in = float(m.get('fade_in', 0.8)); fade_out = float(m.get('fade_out', 1.5))
        label = f'm{j}'
        chain = (
            f'[{idx}:a]aformat=sample_rates={sr}:channel_layouts=stereo,'
            f'atrim=0:{total_duration},asetpts=N/SR/TB,loudnorm=I={music_target}:TP=-3:LRA=12,volume={db_to_linear(gain):.8f}'
        )
        if fade_in > 0:
            chain += f',afade=t=in:st=0:d={fade_in}'
        if fade_out > 0 and total_duration > fade_out:
            chain += f',afade=t=out:st={max(0,total_duration-fade_out):.3f}:d={fade_out}'
        chain += f'[{label}]'
        filters.append(chain)
        music_labels.append(f'[{label}]')

    if music_labels:
        if len(music_labels) == 1:
            filters.append(f'{music_labels[0]}anull[music_pre]')
        else:
            filters.append(''.join(music_labels) + f'amix=inputs={len(music_labels)}:normalize=0[music_pre]')
        duck = manifest.get('ducking', {})
        filters.append(
            f"[music_pre][voice_key]sidechaincompress=threshold={float(duck.get('threshold',0.08))}:"
            f"ratio={float(duck.get('ratio',2.0))}:attack={float(duck.get('attack_ms',25))}:"
            f"release={float(duck.get('release_ms',450))}:knee=2.5:link=average,"
            f"asplit=2[score_mix][score_diag]"
        )
        mix_inputs.append('[score_mix]')
        diag_maps.append(('score_diag', workdir / 'layer_music.wav'))
    else:
        filters.append('[voice_key]anullsink')

    sfx_labels = []
    for j, s in enumerate(sfx_tracks):
        idx = sfx_indexes[j]
        start = float(s.get('start', 0)); gain = float(s.get('gain_db', -2.0)); sfx_target = float(s.get('target_lufs', manifest.get('sfx_target_lufs', -18.0)))
        label = f's{j}'
        filters.append(
            f'[{idx}:a]aformat=sample_rates={sr}:channel_layouts=stereo,'
            f'loudnorm=I={sfx_target}:TP=-3:LRA=7,volume={db_to_linear(gain):.8f},adelay={ms(start)}|{ms(start)}[{label}]'
        )
        sfx_labels.append(f'[{label}]')
    if sfx_labels:
        if len(sfx_labels) == 1:
            filters.append(f'{sfx_labels[0]}anull[sfx_bus]')
        else:
            filters.append(''.join(sfx_labels) + f'amix=inputs={len(sfx_labels)}:normalize=0:dropout_transition=0[sfx_bus]')
        filters.append(f'[sfx_bus]atrim=0:{total_duration},asplit=2[sfx_mix][sfx_diag]')
        mix_inputs.append('[sfx_mix]')
        diag_maps.append(('sfx_diag', workdir / 'layer_sfx.wav'))

    filters.append(''.join(mix_inputs) + f'amix=inputs={len(mix_inputs)}:normalize=0:dropout_transition=0,atrim=0:{total_duration}[premaster]')

    premaster = workdir / 'premaster.wav'
    cmd = [FFMPEG, '-y', '-hide_banner', '-loglevel', 'warning'] + inputs + ['-filter_complex', ';'.join(filters)]
    cmd += ['-map', '[premaster]', '-ar', str(sr), '-c:a', 'pcm_f32le', str(premaster)]
    for label, out in diag_maps:
        cmd += ['-map', f'[{label}]', '-ar', str(sr), '-c:a', 'pcm_f32le', str(out)]
    run(cmd)

    secondary = workdir / 'layer_secondary_actual.wav'
    run([
        FFMPEG, '-y', '-hide_banner', '-loglevel', 'warning', '-i', str(premaster), '-i', str(workdir/'layer_voice.wav'),
        '-filter_complex', '[1:a]volume=-1[inv];[0:a][inv]amix=inputs=2:normalize=0:dropout_transition=0[res]',
        '-map', '[res]', '-ar', str(sr), '-c:a', 'pcm_f32le', str(secondary)
    ])

    timeline_report = {
        'total_duration': round(total_duration, 3),
        'narration': [
            {
                'id': x.get('id', f'beat-{i+1}'), 'file': str(x['_file']), 'start': round(x['_start'], 3),
                'duration': round(x['_duration'], 3), 'gap_after': float(x.get('gap_after', 0.25)),
                'pause_class': x.get('pause_class'), 'text': x.get('text', ''),
            } for i, x in enumerate(timeline)
        ],
        'music': [{k: v for k, v in m.items() if not k.startswith('_')} for m in music_tracks],
        'sfx': [{k: v for k, v in s.items() if not k.startswith('_')} for s in sfx_tracks],
        'silence_qc': silence_qc,
        'pause_map_errors': pause_errors,
    }
    (workdir / 'timeline.json').write_text(json.dumps(timeline_report, indent=2), encoding='utf-8')
    return premaster, timeline_report, diag_maps, secondary


def second_pass_normalize(premaster, out_wav, target_i, target_tp, target_lra, sr):
    m = analyze_loudnorm(premaster, target_i, target_tp, target_lra)
    af = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:"
        f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
        f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
    )
    p = run([
        FFMPEG, '-y', '-hide_banner', '-nostats', '-i', str(premaster), '-af', af,
        '-ar', str(sr), '-c:a', 'pcm_s24le', str(out_wav)
    ])
    return m, parse_loudnorm_json(p.stderr)


def encode_derivatives(wav, out_dir, stem):
    mp3 = out_dir / f'{stem}.mp3'; m4a = out_dir / f'{stem}.m4a'
    run([FFMPEG, '-y', '-hide_banner', '-loglevel', 'warning', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)])
    run([FFMPEG, '-y', '-hide_banner', '-loglevel', 'warning', '-i', str(wav), '-c:a', 'aac', '-b:a', '192k', str(m4a)])
    return mp3, m4a


def main():
    ap = argparse.ArgumentParser(description='Final Vestige deterministic audio mastering lane')
    ap.add_argument('manifest', type=Path)
    ap.add_argument('--profile', default='podcast', choices=['podcast', 'youtube'])
    ap.add_argument('--out-dir', type=Path, default=Path('build'))
    args = ap.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    workdir = args.out_dir / 'work'; workdir.mkdir(parents=True, exist_ok=True)

    profile = manifest.get('profiles', {}).get(args.profile)
    if not profile:
        raise ValueError(f'Missing profile {args.profile!r}')
    target_i = float(profile['integrated_lufs']); target_tp = float(profile['true_peak_dbtp'])
    target_lra = float(profile.get('lra_lu', 11)); sr = int(manifest.get('sample_rate', 48000))

    premaster, timeline, diag_maps, secondary = build_premaster(manifest, manifest_path, workdir)
    stem = f"{manifest.get('episode_id','fv-audio')}_{args.profile}_master"
    out_wav = args.out_dir / f'{stem}.wav'
    pass1, pass2 = second_pass_normalize(premaster, out_wav, target_i, target_tp, target_lra, sr)
    mp3, m4a = encode_derivatives(out_wav, args.out_dir, stem)
    measured = analyze_ebur128(out_wav)

    layer_stats = {'premaster': astats_peak_rms(premaster), 'secondary_actual': astats_peak_rms(secondary)}
    for label, path in diag_maps:
        layer_stats[label.replace('_diag','')] = astats_peak_rms(path)

    required_music = any(bool(m.get('required', True)) for m in manifest.get('music', []))
    required_sfx = [s for s in manifest.get('sfx', []) if s.get('required', True)]
    silence_violations = [x for x in timeline['silence_qc'] if x['violations']]
    errors = list(timeline['pause_map_errors'])
    if silence_violations:
        errors.append(f"Narration internal hesitation violations in {len(silence_violations)} stem(s)")
    if measured['integrated_lufs'] is None or abs(measured['integrated_lufs'] - target_i) > 0.6:
        errors.append(f"Integrated loudness outside tolerance: {measured['integrated_lufs']} vs {target_i} LUFS")
    if measured['true_peak_dbfs'] is not None and measured['true_peak_dbfs'] > target_tp + 0.15:
        errors.append(f"True peak exceeds ceiling: {measured['true_peak_dbfs']} vs {target_tp} dBTP")
    if layer_stats['premaster']['peak_dbfs'] is None or layer_stats['premaster']['peak_dbfs'] < -60:
        errors.append('Premaster appears effectively silent')
    if required_music:
        m = layer_stats.get('score')
        if not m or m['rms_dbfs'] is None or m['rms_dbfs'] < -42 or m['peak_dbfs'] < -28:
            errors.append(f"Required music below audibility floor: {m}")
    if required_sfx:
        s = layer_stats.get('sfx')
        if not s or s['peak_dbfs'] is None or s['peak_dbfs'] < -26:
            errors.append(f"Required SFX below audibility floor: {s}")
    if required_music or required_sfx:
        s = layer_stats['secondary_actual']
        if s['peak_dbfs'] is None or s['peak_dbfs'] < -32:
            errors.append(f"Secondary layers did not survive actual premaster mix: {s}")

    qc = {
        'profile': args.profile,
        'targets': {'integrated_lufs': target_i, 'true_peak_dbtp': target_tp, 'lra_lu': target_lra},
        'measured': measured,
        'layer_stats': layer_stats,
        'pass1': pass1,
        'pass2': pass2,
        'timeline': timeline,
        'required_layers': {'music': required_music, 'sfx_count': len(required_sfx)},
        'outputs': {'wav': str(out_wav), 'mp3': str(mp3), 'm4a': str(m4a)},
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
    }
    report = args.out_dir / f'{stem}_qc.json'
    report.write_text(json.dumps(qc, indent=2), encoding='utf-8')
    print(json.dumps({'status': qc['status'], 'master': str(out_wav), 'qc': str(report), 'measured': measured, 'layers': layer_stats}, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == '__main__':
    main()

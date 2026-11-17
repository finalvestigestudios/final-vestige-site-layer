#!/usr/bin/env python3
"""Offline, rights-gated draft derivative builder for five Final Vestige first-party heroes.

No HTTP, CMS, post edits, uploads, or automated publication. Pillow is required
locally. Historical visual identity and output quality require independent review.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageOps

# Bound to the independent 2026-10-31 read-only CMS/source inventory.
CATALOG = {
    39: ("bceca0bd-a16f-44f7-be08-16376fbf08ca.png", 2892087, 34),
    40: ("377e08da-e121-4f57-9174-1548343402b3.png", 2552136, 35),
    41: ("a44f673d-a8a8-4c83-9f29-7e24dd55156b.png", 2498247, 36),
    42: ("c1237ffd-4a47-4988-8254-e3b021069e72.png", 2488823, 37),
    43: ("01340c2e-1165-4ca0-aa96-87398a83d13a.png", 2836245, 38),
}
SOURCE_ROOT = 'https://finalvestige.com/wp-content/uploads/2026/08/'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def catalog_rows():
    return {i: dict(media_id=i, filename=f, original_bytes=b, post_id=p,
                    width=1672, height=941, target_width=960, target_height=540,
                    source_url=SOURCE_ROOT + f)
            for i, (f, b, p) in CATALOG.items()}


def check_approval(row, approval, digest):
    """A self-attestation gate, NOT independent verification of ownership/rights."""
    if not isinstance(approval, dict) or approval.get('media_id') != row['media_id']:
        raise ValueError('missing_media_specific_rights_approval')
    for key in ('reviewer', 'rights_evidence', 'credit_text'):
        if not isinstance(approval.get(key), str) or not approval[key].strip():
            raise ValueError('missing_rights_field_' + key)
    if approval.get('rights_basis') not in (
        'original_work_owned', 'item_specific_public_domain', 'licensed_for_derivative'):
        raise ValueError('rights_not_established')
    if approval.get('source_url') != row['source_url']:
        raise ValueError('source_url_mismatch')
    if approval.get('original_sha256') != digest:
        raise ValueError('original_hash_mismatch')
    if approval.get('visual_identity_reviewed') is not True:
        raise ValueError('visual_identity_not_reviewed')
    if approval.get('no_wordpress_write') is not True:
        raise ValueError('production_write_guard_missing')
    try:
        datetime.strptime(approval.get('reviewed_on', ''), '%Y-%m-%d')
    except (ValueError, TypeError):
        raise ValueError('invalid_rights_review_date') from None


def prepare_one(row, approval, input_dir, *, check_size=True):
    """Returns candidate bytes and facts; does not write files."""
    if approval is None:
        raise ValueError('missing_media_specific_rights_approval')
    root = Path(input_dir).resolve(strict=True)
    file = root / row['filename']
    if file.is_symlink() or file.resolve().parent != root or not file.is_file():
        raise ValueError('input_must_be_local_non_symlink_regular_file')
    raw = file.read_bytes()
    digest = sha256(raw)
    check_approval(row, approval, digest)
    if check_size and len(raw) != row['original_bytes']:
        raise ValueError('original_size_differs_from_cms_snapshot')
    with Image.open(io.BytesIO(raw)) as source:
        if source.format != 'PNG' or getattr(source, 'n_frames', 1) != 1:
            raise ValueError('expected_static_png')
        if source.size != (row['width'], row['height']):
            raise ValueError('image_dimensions_mismatch')
        if source.mode not in ('RGB', 'RGBA', 'P'):
            raise ValueError('unsupported_image_color_mode_needs_manual_review')
        profile = source.info.get('icc_profile')
        img = ImageOps.exif_transpose(source)
        if img.mode == 'P':
            img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')
        target = (min(960, img.width), round(img.height * min(960, img.width) / img.width))
        if target != (row['target_width'], row['target_height']):
            raise ValueError('target_dimensions_mismatch')
        if target[0] > img.width or target[1] > img.height:
            raise ValueError('upscaling_not_allowed')
        img = img.resize(target, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        opts = {'format': 'WEBP', 'quality': 90, 'method': 6}
        if profile:
            opts['icc_profile'] = profile
        img.save(output, **opts)
    candidate = output.getvalue()
    with Image.open(io.BytesIO(candidate)) as verify:
        if verify.format != 'WEBP' or verify.size != target:
            raise ValueError('encoded_output_failed_validation')
    if len(candidate) >= len(raw):
        return None, dict(status='NO_LOCAL_BYTE_BENEFIT', media_id=row['media_id'],
                          input_bytes=len(raw), candidate_bytes=len(candidate),
                          warning='Not an image-wire-byte or deployed-site measurement')
    facts = dict(status='STAGED_LOCAL_CANDIDATE_NOT_PUBLISHED', media_id=row['media_id'],
                 post_id=row['post_id'], source_url=row['source_url'],
                 original_filename=row['filename'], original_sha256=digest,
                 original_bytes=len(raw), target_width_px=target[0], target_height_px=target[1],
                 output_filename=f"fv-hero-{row['media_id']}-960w.webp",
                 candidate_sha256=sha256(candidate), candidate_bytes=len(candidate),
                 local_encoded_byte_reduction_pct=round(100*(len(raw)-len(candidate))/len(raw), 2),
                 rights_basis_self_attested=approval['rights_basis'],
                 source_credit=approval['credit_text'],
                 item_visual_qa_of_derived_file_passed=False,
                 browser_http_status=None, visitor_transfer_bytes=None,
                 measured_production_savings_pct=None, wordpress_upload_authorized=False,
                 post_rewrite_authorized=False)
    return candidate, facts



def validated_output_root(output_dir, input_root):
    """Resolve a local staging destination without traversing a symlink.

    Path.resolve() dereferences an output symlink, so checking is_symlink()
    *after* resolve is ineffective. Check the requested path and ancestors first.
    The guard is for controlled local staging, not an adversarial TOCTOU sandbox.
    """
    requested = Path(output_dir).absolute()
    if any(p.is_symlink() for p in (requested, *requested.parents)):
        raise ValueError('output_path_symlink_component_refused')
    root = requested.resolve()
    if root == input_root or root.is_relative_to(input_root):
        raise ValueError('output_directory_must_be_separate_from_originals')
    return root


def run(ids, approvals, input_dir, output_dir, *, check_size=True):
    rows = catalog_rows()
    if not ids or any(i not in rows for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('must_select_unique_known_media_ids')
    approved = approvals.get('items', []) if approvals.get('schema_version') == 1 else []
    if len({p.get('media_id') for p in approved if isinstance(p, dict)}) != len(approved):
        raise ValueError('duplicate_approval')
    by_id = {a['media_id']: a for a in approved if isinstance(a, dict) and 'media_id' in a}
    root = Path(input_dir).resolve(strict=True)
    target_root = validated_output_root(output_dir, root)
    # Encode EVERYTHING and validate ALL permissions before any write.
    batch = [prepare_one(rows[i], by_id.get(i), root, check_size=check_size) for i in ids]
    successes = [(binary, record) for binary, record in batch if binary is not None]
    report = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
                  scope='local_unpublished_derivatives_only', result_count=len(batch),
                  records=[r for _,r in batch],
                  website_failure_count_verified=None, claimed_76_percent_verified=False,
                  manually_review_image_quality_before_upload=True,
                  production_write_made=False)
    # Always write the manifest; no publishing logic is present.
    outputs = [target_root / r['output_filename'] for _,r in successes]
    manifest_file = target_root / 'fv-hero-derivative-review.json'
    if any(p.exists() for p in [*outputs, manifest_file]):
        raise ValueError('refusing_to_overwrite_existing_staged_files')
    target_root.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for (binary,_), dest in zip(successes, outputs):
            with dest.open('xb') as fh:
                fh.write(binary)
            created.append(dest)
        with manifest_file.open('x', encoding='utf-8') as fh:
            json.dump(report, fh, indent=2)
            fh.write('\n')
        created.append(manifest_file)
    except Exception:
        for dest in created:
            dest.unlink(missing_ok=True)
        raise
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', action='store_true', help='show source-only candidates; no local files read or written')
    p.add_argument('--media-id', type=int, action='append', help='explicit item(s) to stage, e.g. --media-id 39')
    p.add_argument('--approvals', type=Path, help='self-attested item-level rights/identity review JSON')
    p.add_argument('--input-dir', type=Path, help='locally obtained, legitimately held originals')
    p.add_argument('--output-dir', type=Path, help='separate local staging directory')
    a = p.parse_args()
    if a.plan:
        print(json.dumps(dict(status='SOURCE_ONLY_NO_IMAGE_FILES_READ',
                              five_original_storage_bytes=sum(v[1] for v in CATALOG.values()),
                              images=list(catalog_rows().values()),
                              actual_browser_transfer_bytes=None,
                              wp_upload_authorized=False), indent=2))
        return
    if not (a.media_id and a.approvals and a.input_dir and a.output_dir):
        p.error('staging requires --media-id --approvals --input-dir --output-dir')
    approvals=json.loads(a.approvals.read_text(encoding='utf-8'))
    print(json.dumps(run(a.media_id, approvals, a.input_dir, a.output_dir), indent=2))


if __name__ == '__main__':
    main()

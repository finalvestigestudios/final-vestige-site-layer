#!/usr/bin/env python3
"""Fail-closed provenance gate for two rights-reviewed EX2 archival images.

Does not fetch media itself. Actual network transfer receipts are REQUIRED.
WordPress's i0.wp.com CDN is not the same host as finalvestige.com: distinguish
source rights/provenance from first-party transfer, never conflate the two.
"""
from urllib.parse import urlsplit, parse_qs

MEDIA = (
    dict(id=473, name="Apollo 1 NASA S67-19766", file="s67-19766.webp",
         format="WEBP", dims=(1041, 810), candidates={(300, 233), (768, 598), (1024, 797)}),
    dict(id=474, name="Franklin Victory Point note (1869 print scan)",
         file="Franklinexpeditionnote.jpg", format="JPEG", dims=(960, 1526),
         candidates={(189, 300), (644, 1024), (768, 1221), (960, 1526)}),
)
ORIGIN = "finalvestige.com"
CDN = "i0.wp.com"
BASE = "/wp-content/uploads/2026/08/"


def classify_source(original, selected, index):
    """Validate chosen responsive source against two specific WordPress media IDs.

    The Photon/Jetpack CDN is allowed for provenance checks, but must be
    classified as non-first-party hosting in every report.
    """
    if index not in range(len(MEDIA)):
        raise ValueError("Unexpected archival-image index")
    media = MEDIA[index]
    expected = BASE + media["file"]
    o = urlsplit(original)
    if not (o.scheme == "https" and o.hostname == ORIGIN and o.path == expected
            and not o.query and not o.fragment and not o.username and not o.password):
        raise ValueError("Original image is not approved first-party WordPress media ID")
    s = urlsplit(selected)
    if s.scheme != "https" or s.fragment or s.username or s.password or s.port is not None:
        raise ValueError("Selected image URL is not approved HTTPS media")
    if s.hostname == ORIGIN and s.path == expected and not s.query:
        return dict(media_id=media["id"], name=media["name"], host=s.hostname,
                    first_party=True, selected_size=media["dims"], format=media["format"])
    if s.hostname != CDN or s.path != "/" + ORIGIN + expected:
        raise ValueError("Selected image is not approved original or WordPress CDN derivative")
    q = parse_qs(s.query, strict_parsing=True, keep_blank_values=True)
    if set(q) != {"fit", "ssl"} or q["ssl"] != ["1"] or len(q["fit"]) != 1:
        raise ValueError("Unexpected CDN query or missing secure resizing")
    try:
        w, h = (int(x) for x in q["fit"][0].split(","))
    except (TypeError, ValueError) as e:
        raise ValueError("Invalid CDN dimensions") from e
    if (w, h) not in media["candidates"]:
        raise ValueError("CDN resize does not match approved media metadata")
    return dict(media_id=media["id"], name=media["name"], host=s.hostname,
                first_party=False, selected_size=(w, h), format=media["format"])


def verify_receipt(source, received, status, content_type):
    """Check real HTTP status/header against already-decoded image byte receipt.

    received must be produced by verify_image_bytes(response.body(), format).
    WordPress metadata by itself is NEVER a valid substitute.
    """
    if status != 200:
        raise ValueError("Archival image did not return HTTP 200")
    expected_type = {"WEBP": "image/webp", "JPEG": "image/jpeg"}[source["format"]]
    if content_type.split(";", 1)[0].strip().lower() != expected_type:
        raise ValueError("Unexpected media Content-Type")
    if received.get("format") != source["format"]:
        raise ValueError("Decoded format does not match approved image")
    if (received.get("width"), received.get("height")) != tuple(source["selected_size"]):
        raise ValueError("Decoded image dimensions do not match approved source/derivative")
    if not (received.get("sha256") and len(received["sha256"]) == 64
            and received.get("bytes", 0) >= 1024):
        raise ValueError("Missing transferred image byte/hash evidence")
    return {**source, "transfer_bytes": received["bytes"], "sha256": received["sha256"]}


def verify_image_bytes(body, expected_format):
    """Decode *actual HTTP response bytes* into a receipt for verify_receipt.

    This cannot prove copyright clearance, NASA endorsement or that the media
    matches its historic caption. An image tag, a mock, and WordPress media
    metadata are not substitutes for actual browser response.body() bytes.
    """
    import hashlib
    from io import BytesIO
    if expected_format not in ('WEBP', 'JPEG'):
        raise ValueError('Unknown allowed archival image encoding')
    if not isinstance(body, bytes) or len(body) < 1024:
        raise ValueError('Missing or implausibly small transferred image bytes')
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as e:
        raise RuntimeError('Pillow image decoder unavailable: image admission HOLD') from e
    try:
        with Image.open(BytesIO(body)) as image:
            if image.format != expected_format:
                raise ValueError('Encoded image format does not match expected media')
            width, height = image.size
            if min(width, height) < 1 or width * height > 12000000:
                raise ValueError('Unreasonable decoded archival dimensions')
            image.load()  # reject truncated/corrupted data rather than just headers
    except (OSError, ValueError, UnidentifiedImageError) as e:
        raise ValueError('Cannot decode approved image bytes: ' + str(e)) from e
    return dict(format=expected_format, width=width, height=height,
                bytes=len(body), sha256=hashlib.sha256(body).hexdigest())

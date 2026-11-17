"""Conservative structural validation of PE32+ data-directory references.

No executable code is run; acceptance is not signature, AV, or QD approval.
"""
from __future__ import annotations

import struct


class PEDataDirectoryError(ValueError):
    """A Windows executable data directory fails the bounded shape contract."""


def validate_pe_directories(optional: bytes, *, header_size: int,
                            image_size: int, file_size: int,
                            virtual_ranges: list[tuple[int, int]],
                            file_ranges: list[tuple[int, int]],
                            backed_virtual_ranges: list[tuple[int, int]]) -> None:
    """Validate directory bounds including section bytes backed by the file.

    PE32+ entry 4 (certificate) uses a *file offset*, not an RVA. Other
    nonempty entries must fit wholly inside the headers or ONE file-backed
    section interval. Virtual-only/zero-filled section tails cannot contain
    on-disk directory data, even though they map into the image at runtime.
    """
    if len(optional) < 112:
        raise PEDataDirectoryError("PE data directory rejected")
    count = struct.unpack_from("<I", optional, 108)[0]
    if count > 16 or 112 + count * 8 > len(optional):
        raise PEDataDirectoryError("PE data directory rejected")
    for index in range(count):
        address, size = struct.unpack_from("<II", optional, 112 + index * 8)
        if address == 0 and size == 0:
            continue
        if address == 0 or size == 0:
            raise PEDataDirectoryError("PE data directory rejected")
        end = address + size
        if index == 4:  # Security/certificate directory: raw FILE offset.
            if (address % 8 or address < header_size or end > file_size
                    or any(address < high and end > low
                           for low, high in file_ranges)):
                raise PEDataDirectoryError("PE data directory rejected")
        elif address < header_size:
            if end > header_size:
                raise PEDataDirectoryError("PE data directory rejected")
        elif (end > image_size
              or not any(low <= address and end <= high
                         for low, high in virtual_ranges)
              or not any(low <= address and end <= high
                         for low, high in backed_virtual_ranges)):
            raise PEDataDirectoryError("PE data directory rejected")

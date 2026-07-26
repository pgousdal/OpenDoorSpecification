"""Read LHA level 0, 1 and 2 headers without decompressing payloads."""
from __future__ import annotations
import hashlib, os, struct
from pathlib import Path
from typing import BinaryIO

def _read_exact(stream: BinaryIO, count: int) -> bytes:
    data = stream.read(count)
    if len(data) != count:
        raise ValueError(f"unexpected EOF: wanted {count}, got {len(data)}")
    return data


def inspect(path: Path) -> dict:
    entries: list[dict] = []
    archive_size = path.stat().st_size

    with path.open("rb") as stream:
        while stream.tell() < archive_size - 1:
            header_offset = stream.tell()
            probe = stream.read(21)
            if not probe or probe[0] == 0:
                break
            if len(probe) < 21:
                raise ValueError("truncated LHA header")
            level = probe[20]
            stream.seek(header_offset)

            if level in (0, 1):
                (
                    header_size,
                    _checksum,
                    signature,
                    skip_size,
                    file_size,
                    _modify_time,
                    _reserved,
                    level,
                    filename_length,
                ) = struct.unpack("<BB5sII4sBBB", _read_exact(stream, 22))
                filename = _read_exact(stream, filename_length).decode(
                    "latin-1", "replace"
                ).split("\x00", 1)[0]
                _crc = struct.unpack("<H", _read_exact(stream, 2))[0]
                directory = None
                if level == 1:
                    fixed = 5 + 4 + 4 + 2 + 2 + 1 + 1 + 1 + filename_length + 2 + 1 + 2
                    extra_size = header_size - fixed
                    _read_exact(stream, 1 + max(extra_size, 0))
                    extended_size = struct.unpack("<H", _read_exact(stream, 2))[0]
                else:
                    extended_size = 0
                extended_total = 0
                compressed_size = skip_size
            elif level == 2:
                (
                    _all_header_size,
                    signature,
                    compressed_size,
                    file_size,
                    _modify_time,
                    _reserved,
                    level,
                    _crc,
                    _os_identifier,
                    extended_size,
                ) = struct.unpack("<H5sIIIBBHBH", _read_exact(stream, 26))
                filename = ""
                directory = None
                extended_total = 0
            else:
                raise ValueError(
                    f"unsupported LHA header level {level} at {header_offset}"
                )

            while extended_size:
                extended_total += extended_size
                extension_type = _read_exact(stream, 1)[0]
                payload = _read_exact(stream, extended_size - 3)
                extended_size = struct.unpack("<H", _read_exact(stream, 2))[0]
                if extension_type == 0x01:
                    filename = payload.decode("latin-1", "replace").split("\x00", 1)[0]
                elif extension_type == 0x02:
                    directory = payload.decode("latin-1", "replace").replace(
                        "\xff", "/"
                    )

            if level in (0, 1):
                compressed_size = skip_size - extended_total

            data_offset = stream.tell()
            full_path = f"{directory}/{filename}" if directory else filename
            full_path = full_path.replace("\\", "/").replace("//", "/")

            entries.append(
                {
                    "path": full_path,
                    "method": signature.decode("ascii", "replace"),
                    "uncompressed_size": file_size,
                    "compressed_size": compressed_size,
                    "data_offset": data_offset,
                }
            )
            stream.seek(compressed_size, os.SEEK_CUR)

    return {
        "source_filename": path.name,
        "source_size": archive_size,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "entry_count": len(entries),
        "entries": entries,
    }



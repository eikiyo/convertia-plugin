# Location: tests/test_archive_metadata.py
# Purpose: prevent alternate ZIP filename metadata from changing installed paths.
# Functions: metadata parsing and real ZIP local/central header mutation tests.
# Calls: archive_checks against real ZIP files.
# Imports: struct, zipfile, zlib, pytest, archive_checks, conftest, test_archive.
import struct
import zipfile
import zlib
import pytest
import archive_checks as checks
from conftest import archive_candidate
from test_archive import rewrite_archive


@pytest.mark.parametrize('location', ['central', 'local', 'both'])
def test_unicode_filename_override_rejected(candidate, tmp_path, location):
    path, sha = archive_candidate(candidate, tmp_path)
    body = b'\x01' + struct.pack('<I', zlib.crc32(b'LICENSE')) + b'tools/injected.py'
    field = struct.pack('<HH', 0x7075, len(body)) + body
    def mutate(entries):
        next(info for info, _ in entries if info.filename == 'LICENSE').extra = field
        return entries
    rewrite_archive(path, mutate)
    if location != 'both':
        data = path.read_bytes()
        positions = [index for index in range(len(data)) if data.startswith(field, index)]
        assert len(positions) == 2
        offset = positions[0 if location == 'central' else 1]
        data = data[:offset] + b'\x34\x12' + data[offset + 2:]
        path.write_bytes(data)
    with pytest.raises(ValueError, match='Unsafe Unicode ZIP path metadata'):
        checks.validate_archive(path, candidate, sha)


@pytest.mark.parametrize('extra,diagnostic', [(b'x', 'Malformed ZIP extra field'),
    (struct.pack('<HH', 1, 10) + b'x', 'Truncated ZIP extra field')])
def test_malformed_extra(extra, diagnostic):
    with pytest.raises(ValueError, match=diagnostic):
        checks.check_extra(extra)


def test_valid_multiple_extra_fields():
    checks.check_extra(struct.pack('<HH', 0x5455, 0) + struct.pack('<HH', 0x5455, 1) + b'x')


@pytest.mark.parametrize('mutation,diagnostic', [('signature', 'Invalid ZIP local header'),
    ('short-header', 'Invalid ZIP local header'), ('truncated-extra', 'Truncated ZIP local metadata'),
    ('directory-name', 'ZIP local filename mismatch')])
def test_bad_local_metadata(candidate, tmp_path, mutation, diagnostic):
    path, _ = archive_candidate(candidate, tmp_path)
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()[-1 if mutation == 'truncated-extra' else 0]
    data = bytearray(path.read_bytes())
    if mutation == 'signature':
        data[info.header_offset:info.header_offset + 4] = b'nope'
    elif mutation == 'truncated-extra':
        struct.pack_into('<H', data, info.header_offset + 28, 65535)
    elif mutation == 'directory-name':
        assert info.is_dir()
        data[info.header_offset + 30] = ord('x')
    path.write_bytes(data)
    with zipfile.ZipFile(path) as archive:
        if mutation == 'short-header':
            info.header_offset = len(data) - 1
        with pytest.raises(ValueError, match=diagnostic):
            checks.check_local_metadata(archive, info)



def test_utf8_local_filename_control(candidate, tmp_path):
    path, _ = archive_candidate(candidate, tmp_path)
    data = bytearray(path.read_bytes())
    struct.pack_into('<H', data, 6, 0x800)
    path.write_bytes(data)
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()[0]
        info.flag_bits = 0x800
        checks.check_local_metadata(archive, info)


@pytest.mark.parametrize('mutation,diagnostic', [
    ('flags', 'Unsupported ZIP flags'), ('compression', 'Unsupported ZIP flags'),
    ('local-encoding', 'ZIP local encoding mismatch'), ('local-size', 'ZIP local size or CRC mismatch')])
def test_unsupported_or_disagreeing_local_metadata(candidate, tmp_path, mutation, diagnostic):
    path, _ = archive_candidate(candidate, tmp_path)
    data = bytearray(path.read_bytes())
    if mutation == 'local-encoding':
        struct.pack_into('<H', data, 6, 8)
    elif mutation == 'local-size':
        struct.pack_into('<I', data, 18, 123)
    path.write_bytes(data)
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()[0]
        if mutation == 'flags':
            info.flag_bits = 8
        elif mutation == 'compression':
            info.compress_type = 12
        with pytest.raises(ValueError, match=diagnostic):
            checks.check_local_metadata(archive, info)

# Location: tests/test_archive_layout.py
# Purpose: reject physical ZIP records omitted from the central directory.
# Functions: omit_index_entry and whole-archive boundary regressions.
# Calls: real ZIP fixtures and archive_checks.validate_archive.
# Imports: struct, zipfile, pytest, archive_checks, conftest.
import struct
import zipfile
import pytest
import archive_checks as checks
from conftest import archive_candidate


def omit_index_entry(path, selected):
    data = bytearray(path.read_bytes())
    footer = data.rindex(b'PK\x05\x06')
    count = struct.unpack_from('<H', data, footer + 10)[0]
    size, offset = struct.unpack_from('<II', data, footer + 12)
    for index in range(count):
        name, extra, comment = struct.unpack_from('<HHH', data, offset + 28)
        length = 46 + name + extra + comment
        if index == selected % count:
            del data[offset:offset + length]
            footer -= length
            struct.pack_into('<HHI', data, footer + 8, count - 1, count - 1, size - length)
            path.write_bytes(data)
            return
        offset += length
    raise AssertionError('Fixture index missing')


@pytest.mark.parametrize('index,diagnostic', [(0, 'Unindexed ZIP local data or overlapping records'),
                                            (-1, 'Unindexed ZIP local data after final entry')])
def test_hidden_physical_record_rejected(candidate, tmp_path, index, diagnostic):
    path, sha = archive_candidate(candidate, tmp_path)
    with zipfile.ZipFile(path) as archive:
        original_count = len(archive.infolist())
    omit_index_entry(path, index)
    with zipfile.ZipFile(path) as archive:
        assert len(archive.infolist()) == original_count - 1
    with pytest.raises(ValueError, match=diagnostic):
        checks.validate_archive(path, candidate, sha)

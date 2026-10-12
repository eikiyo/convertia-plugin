# Location: tests/test_asset_checks.py
# Purpose: reject invalid directory icons and non-text runtime content.
# Functions: image_bytes and real asset validation controls.
# Calls: Pillow image serialization and asset_checks.check_runtime_asset.
# Imports: io, pytest, PIL.Image, asset_checks.
import io
import pytest
from PIL import Image
from asset_checks import check_runtime_asset


def image_bytes(size=(512, 512), image_format='PNG'):
    output = io.BytesIO()
    Image.new('RGB', size).save(output, format=image_format)
    return output.getvalue()


def test_actual_directory_icon_is_valid(package):
    name = '.claude-plugin/icon.png'
    assert check_runtime_asset(name, (package / name).read_bytes()) is None


def test_utf8_runtime_text_is_valid():
    assert check_runtime_asset('README.md', 'Hello, café'.encode('utf-8')) is None


def test_invalid_png_bytes_are_rejected():
    with pytest.raises(ValueError, match='Invalid PNG image'):
        check_runtime_asset('icon.png', b'not a PNG')


def test_jpeg_disguised_as_png_is_rejected():
    with pytest.raises(ValueError, match='Icon must be PNG'):
        check_runtime_asset('icon.png', image_bytes(image_format='JPEG'))


@pytest.mark.parametrize('size', [(512, 256), (511, 511), (2049, 2049)])
def test_invalid_icon_dimensions_are_rejected(size):
    with pytest.raises(ValueError, match='Invalid icon dimensions'):
        check_runtime_asset('icon.png', image_bytes(size))


def test_truncated_png_is_rejected():
    with pytest.raises(ValueError, match='Invalid PNG image'):
        check_runtime_asset('icon.png', image_bytes()[:-9])


@pytest.mark.parametrize('size', [2 * 1024 * 1024, 2 * 1024 * 1024 + 1])
def test_oversized_icon_is_rejected_before_image_parsing(size):
    with pytest.raises(ValueError, match='Icon exceeds 2 MB'):
        check_runtime_asset('icon.png', b'x' * size)


@pytest.mark.parametrize('body,diagnostic', [
    (b'\xff', 'Runtime text must be UTF-8'),
    (b'hello\0', 'Binary runtime text')])
def test_invalid_runtime_text_is_rejected(body, diagnostic):
    with pytest.raises(ValueError, match=diagnostic):
        check_runtime_asset('README.md', body)

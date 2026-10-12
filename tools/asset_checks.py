# Location: tools/asset_checks.py
# Purpose: require readable UTF-8 runtime text and a complete directory icon.
# Functions: check_runtime_asset.
# Calls: Pillow image verification and pixel decoding.
# Imports: io, PIL.Image, release_checks.
import io
from PIL import Image
from release_checks import require


def check_runtime_asset(name, body):
    if name.endswith('.png'):
        require(len(body) < 2 * 1024 * 1024, f'Icon exceeds 2 MB: {name}')
        try:
            with Image.open(io.BytesIO(body)) as image:
                require(image.format == 'PNG', f'Icon must be PNG: {name}')
                width, height = image.size
                require(width == height and 512 <= width <= 2048, f'Invalid icon dimensions: {name}')
                image.verify()
            with Image.open(io.BytesIO(body)) as image:
                image.load()
        except (OSError, SyntaxError) as error:
            raise ValueError(f'Invalid PNG image: {name}') from error
    else:
        try:
            text = body.decode('utf-8')
        except UnicodeDecodeError as error:
            raise ValueError(f'Runtime text must be UTF-8: {name}') from error
        require('\x00' not in text, f'Binary runtime text: {name}')

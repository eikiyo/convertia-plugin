# Location: tools/release_checks.py
# Purpose: validate shared plugin release artifacts without host dependencies.
# Functions: frontmatter, version, metadata, skills and content validation.
# Calls: filesystem reads only.
# Imports: hashlib, json, re, pathlib.
import hashlib
import json
import re
from pathlib import Path

SKILLS = {'convertia', 'finance', 'regulation', 'architect', 'operations',
          'customer', 'investor', 'validation', 'due-diligence'}
MANIFESTS = ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json')
METADATA = ('description', 'author', 'keywords', 'repository', 'license')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f'Expected JSON object: {path}')
    return value


def skill_frontmatter(body, name, path):
    lines = body.splitlines()
    prefix = f'Invalid skill frontmatter: {path}'
    require(len(lines) >= 4 and lines[0] == '---' and lines[3] == '---',
            f'{prefix}: expected delimiters around exactly two keys')
    fields = {}
    for line in lines[1:3]:
        key, separator, value = line.partition(': ')
        require(separator and key in {'name', 'description'} and key not in fields,
                f'{prefix}: missing, duplicate or unsupported key')
        fields[key] = value
    require(re.fullmatch(r'[a-z][a-z0-9-]*', fields['name']) and fields['name'] == name,
            f'{prefix}: name must match the skill directory')
    try:
        description = json.loads(fields['description'])
    except json.JSONDecodeError as error:
        raise ValueError(f'{prefix}: description must be a JSON-quoted string') from error
    require(isinstance(description, str) and description.strip(),
            f'{prefix}: description must be a nonempty string')


def version_tuple(value, label):
    require(re.fullmatch(r'\d+\.\d+\.\d+', value), f'Invalid {label}')
    return tuple(map(int, value.split('.')))


def check_version(root, previous):
    version = (root / 'VERSION').read_text().strip()
    current = version_tuple(version, 'VERSION')
    if previous:
        require(current > version_tuple(previous, 'PREVIOUS_VERSION'), 'Version must increase')
    return version


def check_metadata(root, version):
    canonical = read_json(root / 'plugin.json')
    for key in ('name', 'version', *METADATA):
        require(key in canonical, f'Missing manifest field: {key}')
    for path in MANIFESTS:
        data = read_json(root / path)
        require(all(data.get(key) == canonical[key] for key in METADATA), f'Metadata drift: {path}')
        require(data.get('version') == version and data.get('name') == 'convertia',
                f'Manifest drift: {path}')
    for path in ('README.md', 'skills/convertia/SKILL.md'):
        require(f'# Convertia {version}' in (root / path).read_text(), f'Heading drift: {path}')
    check_host_metadata(root, canonical)
    market = read_json(root / '.claude-plugin/marketplace.json')
    expected = [{'name': 'convertia', 'source': './', 'description': canonical['description']}]
    require(market.get('plugins') == expected, 'Marketplace drift')


def check_host_metadata(root, canonical):
    codex = read_json(root / '.codex-plugin/plugin.json')
    require(codex.get('skills') == './skills', 'Invalid declared skills path')
    require((root / 'skills').is_dir(), 'Declared skills directory missing')
    extensions = canonical.get('extensions')
    require(isinstance(extensions, dict), 'Missing OpenAI extensions object')
    openai = extensions.get('com.openai')
    require(isinstance(openai, dict), 'Missing OpenAI metadata object')
    interface = openai.get('interface')
    require(isinstance(interface, dict), 'Missing OpenAI interface')
    prompts = interface.get('defaultPrompt')
    require(isinstance(prompts, list) and prompts and
            all(isinstance(prompt, str) and prompt.strip() for prompt in prompts),
            'defaultPrompt must be a nonempty array of nonempty strings')
    native = codex.get('interface')
    require(isinstance(native, dict), 'Missing Codex interface')
    require({key: value for key, value in native.items() if key != 'capabilities'} == interface,
            'Host interface drift')


def check_skills(root):
    paths = list((root / 'skills').rglob('SKILL.md'))
    require(all(path.parent.parent == root / 'skills' for path in paths),
            'Nested skill entrypoint is unsupported')
    entries = {path.parent.name: path for path in paths}
    require(set(entries) == SKILLS, f'Skill entry drift: {set(entries)}')
    documented = set(re.findall(r'\| `/convertia:([a-z-]+)`', (root / 'README.md').read_text()))
    require(documented == set(entries), 'Documented command drift')
    for name, path in entries.items():
        body = path.read_text()
        skill_frontmatter(body, name, path.relative_to(root))
        for reference in set(re.findall(r'(?:\.\./|references/)[A-Za-z0-9_./-]+\.md', body)):
            target = (path.parent / reference).resolve()
            require(target.is_relative_to(root.resolve()) and target.is_file(),
                    f'Missing or external skill reference: {path}: {reference}')
        if name != 'convertia':
            require('../convertia/SKILL.md' in body, f'Shared contract link missing: {path}')


def content_hashes(root):
    files = sorted(path for path in (root / 'skills').rglob('*') if path.is_file())
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files}


def check_content(root):
    actual = content_hashes(root)
    require(actual == read_json(root / 'CONTENT.json'), 'Content lock drift')
    ids = []
    for path in (root / 'skills/convertia/references/fundamentals').rglob('*.md'):
        ids.extend(re.findall(r'^- ([A-Z][A-Z0-9-]*-[A-Z]*\d+):', path.read_text(), re.M))
    require(len(ids) == 918 and len(set(ids)) == 918, f'Question IDs: {len(ids)} / {len(set(ids))}')
    require(not list((root / 'skills').rglob('*.pdf')), 'Private PDF included')
    require(not (root / '.mcp.json').exists(), 'Unexpected MCP dependency')
    return len(actual)


def validate(root, previous=None):
    root = Path(root)
    version = check_version(root, previous)
    check_metadata(root, version)
    check_skills(root)
    count = check_content(root)
    return f'PASS: {version}; {count} shared files; 918 unique questions; content lock matches'

#!/usr/bin/env bash
# Location: tools/verify.sh
# Purpose: reject release version, content and question-bank drift.
# Functions: inline release checks.
# Calls: python3 standard library only.
# Imports: json, hashlib, pathlib, re.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I - <<'PY'
import hashlib,json,re
from pathlib import Path
root=Path('.')
v=(root/'VERSION').read_text().strip()
import os
previous=os.environ.get('PREVIOUS_VERSION')
if previous:
    assert tuple(map(int,v.split('.'))) > tuple(map(int,previous.split('.'))), 'Version must increase'
assert re.fullmatch(r'\d+\.\d+\.\d+',v), 'Invalid VERSION'
canonical=json.loads(Path('plugin.json').read_text())
for p in ['plugin.json','.codex-plugin/plugin.json','.claude-plugin/plugin.json']:
    data=json.loads(Path(p).read_text())
    assert all(data.get(k)==canonical.get(k) for k in ['description','author','keywords','repository','license']), f'Metadata drift: {p}'
    assert data['version']==v and data['name']=='convertia', f'Manifest drift: {p}'
for p in ['README.md','skills/convertia/SKILL.md']:
    assert f'# Convertia {v}' in Path(p).read_text(), f'Heading drift: {p}'
market=json.loads(Path('.claude-plugin/marketplace.json').read_text())
assert market['plugins']==[{'name':'convertia','source':'./','description':json.loads(Path('plugin.json').read_text())['description']}], 'Marketplace drift'
files=sorted(p for p in Path('skills').rglob('*') if p.is_file())
actual={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert actual==json.loads(Path('CONTENT.json').read_text()), 'Content lock drift'
ids=[]
for p in Path('skills/convertia/references/fundamentals').rglob('*.md'):
    ids+=re.findall(r'^- ([A-Z][A-Z0-9-]*-[A-Z]*\d+):',p.read_text(),re.M)
assert len(ids)==918 and len(set(ids))==918, f'Question IDs: {len(ids)} / {len(set(ids))}'
assert not list(Path('skills').rglob('*.pdf')), 'Private PDF included'
assert not Path('.mcp.json').exists(), 'Unexpected MCP dependency'
print(f'PASS: {v}; {len(files)} shared files; 918 unique questions; content lock matches')
PY

#!/usr/bin/env bash
# Location: tools/verify.sh
# Purpose: reject malformed skill headers and release/content drift.
# Functions: skill_frontmatter, frontmatter_selftest, inline release checks.
# Calls: python3 standard library only.
# Imports: Python standard library only.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I - "$@" <<'PY'
import hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path

def skill_frontmatter(body, name, path):
    lines=body.splitlines()
    prefix=f'Invalid skill frontmatter: {path}'
    if len(lines)<4 or lines[0]!='---' or lines[3]!='---':
        raise ValueError(f'{prefix}: expected delimiters around exactly two keys')
    fields={}
    for line in lines[1:3]:
        key,separator,value=line.partition(': ')
        if not separator or key not in {'name','description'} or key in fields:
            raise ValueError(f'{prefix}: missing, duplicate or unsupported key')
        fields[key]=value
    if set(fields)!={'name','description'}:
        raise ValueError(f'{prefix}: name and description are required')
    if not re.fullmatch(r'[a-z][a-z0-9-]*',fields['name']) or fields['name']!=name:
        raise ValueError(f'{prefix}: name must match the skill directory')
    try:
        description=json.loads(fields['description'])
    except json.JSONDecodeError as error:
        raise ValueError(f'{prefix}: description must be a JSON-quoted string') from error
    if not isinstance(description,str) or not description.strip():
        raise ValueError(f'{prefix}: description must be a nonempty string')

def frontmatter_selftest():
    with tempfile.TemporaryDirectory(prefix='convertia-frontmatter-') as directory:
        fixture=Path(directory)/'plugin'
        shutil.copytree(Path.cwd(),fixture,ignore=shutil.ignore_patterns('.git','*.bak'))
        paths={name:fixture/f'skills/{name}/SKILL.md' for name in ['customer','investor']}
        originals={name:path.read_text() for name,path in paths.items()}
        good=originals['customer'].splitlines(keepends=True)
        cases=[('quoted colon', 'customer', ''.join(good), True)]
        for name,body in originals.items():
            lines=body.splitlines(keepends=True)
            lines[2]='description: '+json.loads(lines[2].partition(': ')[2])+'\n'
            cases.append((f'original malformed {name}',name,''.join(lines),False))
        for label,index,replacement in [
            ('missing opening delimiter',0,''),('missing closing delimiter',3,''),
            ('missing description',2,''),('duplicate key',2,'name: customer\n'),
            ('empty description',2,'description: ""\n'),
            ('non-string description',2,'description: 7\n'),
            ('wrong name',1,'name: investor\n')]:
            lines=good.copy()
            lines[index]=replacement
            cases.append((label,'customer',''.join(lines),False))
        for label,name,body,valid in cases:
            for key,path in paths.items(): path.write_text(originals[key])
            paths[name].write_text(body)
            files=sorted(p for p in (fixture/'skills').rglob('*') if p.is_file())
            lock={str(p.relative_to(fixture)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            (fixture/'CONTENT.json').write_text(json.dumps(lock))
            result=subprocess.run(['bash','tools/verify.sh'],cwd=fixture,text=True,capture_output=True,timeout=30)
            if (result.returncode==0)!=valid or (not valid and 'Invalid skill frontmatter:' not in result.stderr):
                raise RuntimeError(f'Self-test failed: {label}: {result.stdout}{result.stderr}')
            print(f'SELFTEST: {label}: {"accepted" if valid else "rejected for malformed frontmatter"}')

if sys.argv[1:]==['--self-test']:
    frontmatter_selftest()
    sys.exit(0)
if sys.argv[1:]:
    raise ValueError('Usage: bash tools/verify.sh [--self-test]')
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
expected={'convertia','finance','regulation','architect','operations','customer','investor','validation','due-diligence'}
entries={p.parent.name:p for p in Path('skills').glob('*/SKILL.md')}
assert set(entries)==expected, f'Skill entry drift: {set(entries)}'
documented=set(re.findall(r'\| `/convertia:([a-z-]+)`',Path('README.md').read_text()))
assert documented==set(entries), 'Documented command drift'
for name,p in entries.items():
    body=p.read_text()
    skill_frontmatter(body,name,p)
    if name!='convertia':
        assert '../convertia/SKILL.md' in body, f'Shared contract link missing: {p}'
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

# Location: tools/official_checks.py
# Purpose: run pinned official schema and Agent Skills toolkit on candidate files.
# Functions: validate_official.
# Calls: Draft202012Validator and official skills_ref.validate.
# Imports: hashlib, pathlib, jsonschema, skills_ref, release_checks, repo_layout.
import hashlib
from pathlib import Path
from jsonschema import Draft202012Validator
import skills_ref
from release_checks import read_json, require, SKILLS
from repo_layout import plugin_root

SCHEMA = Path(__file__).resolve().parents[1] / 'schemas/plugin.schema.json'
SCHEMA_SHA256 = '0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883'


def validate_official(root):
    plugin = plugin_root(root)
    require(hashlib.sha256(SCHEMA.read_bytes()).hexdigest() == SCHEMA_SHA256, 'Official schema hash drift')
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(read_json(plugin / 'plugin.json'))
    paths = sorted((plugin / 'skills').glob('*/SKILL.md'))
    require({path.parent.name for path in paths} == SKILLS, 'Official skill entrypoint census mismatch')
    for path in paths:
        errors = skills_ref.validate(path.parent)
        require(not errors, f'Official skill validation failed: {path.parent.name}: {errors}')
    return f'PASS: official portable schema and all {len(SKILLS)} Agent Skills entrypoints'

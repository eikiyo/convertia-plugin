# Location: tests/test_acceptance_inventory.py
# Purpose: keep the approved 1.5.0 command and host-acceptance inventory explicit.
# Functions: census controls for commands and required hosted journeys.
# Calls: production skill and promotion inventories, plus documented matrix reads.
# Imports: pathlib, promotion, release_checks.
from pathlib import Path
from promotion import SMOKE_CASES
from release_checks import SKILLS


def test_approved_commands_preserve_existing_entries_and_add_only_two():
    assert SKILLS == {
        'convertia', 'finance', 'regulation', 'architect', 'operations',
        'customer', 'investor', 'validation', 'due-diligence', 'artifact', 'legal',
    }


def test_acceptance_gate_includes_all_new_journeys_and_documents_them():
    added = {
        'natural_language_artifact', 'artifact_create_open', 'artifact_revision_export',
        'artifact_unavailable', 'legal_bilingual', 'regulation_bilingual',
        'bilingual_revision', 'language_and_terms', 'artifact_focus_return',
        'no_artifact_on_followup',
    }
    assert SMOKE_CASES == added | {
        'all_skills', 'focused_answer', 'short_followup', 'role_switch', 'due_diligence',
    }
    guide = (Path(__file__).resolve().parents[1] / 'TESTING.md').read_text()
    for case in added:
        assert '| ' + case + ' |' in guide
    assert 'make this a document for our team' in guide
    assert 'Can you convert this into an artifact?' in guide

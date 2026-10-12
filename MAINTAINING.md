# Shared release contract

This repository is the sole editable source for Convertia on Claude and ChatGPT. Historical ZIPs and installed caches are outputs, never editing locations.

1. Edit the shared skill and references once. Keep only host metadata in platform manifests.
2. Raise VERSION, all three manifests, README and the skill heading together. Never reuse or move published version tags.
3. Run `bash tools/verify.sh`. Run the cases in TESTING.md on both hosts before claiming behavioral parity. Identical prompts do not guarantee identical model output.
4. Commit and tag `vX.Y.Z`. Merge only checked changes to main because connected marketplaces track main.
5. Inspect the Claude directory version and ChatGPT workspace sync report. Record each observed version and commit in release notes. A push is not a deployment. Label any pending host explicitly.
6. Roll back by releasing known-good content under a higher version, never by moving a published tag.

ChatGPT repository sync requires a workspace admin and a one-time import. An existing personal archive plugin does not migrate automatically. Claude directory submission also requires one-time account setup and review. Do not claim either connection until verified.

Keep private decks, personal information, internal research, credentials and machine paths outside this public repository. Private archives remain preserved elsewhere. No independent host-specific prompt edits or manual-upload forks.

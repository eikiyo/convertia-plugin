# Shared release contract

This repository is the sole editable source for Convertia on Claude and ChatGPT. Historical ZIPs and installed caches are outputs, never editing locations.

1. Edit the shared skill and references once. Keep only host metadata in platform manifests.
2. Raise VERSION, all three manifests, README and the skill heading together. Never reuse or move published version tags.
3. Run `bash tools/test.sh -q`, `bash tools/verify.sh` and the live connection tests. The canonical law in CLAUDE.md requires 100% statement and branch coverage of owned Python code without exclusions. Run the cases in TESTING.md on both hosts before claiming behavioral parity. Identical prompts do not guarantee identical model output.
4. Push a branch and open a pull request. Merge only after the required `verify` check passes against the up-to-date candidate. Main must have the protection settings in `.github/main-protection.json`, including administrator enforcement. Never push releases directly to main.
5. Inspect the Claude directory version and ChatGPT workspace sync report. Record each observed version and commit in release notes. A push is not a deployment. Label any pending host explicitly.
6. Roll back by releasing known-good content under a higher version, never by moving a published tag.

ChatGPT repository sync requires a workspace admin and a one-time import. An existing personal archive plugin does not migrate automatically. Claude directory submission also requires one-time account setup and review. Do not claim either connection until verified.

Keep private decks, personal information, internal research, credentials and machine paths outside this public repository. Private archives remain preserved elsewhere. No independent host-specific prompt edits or manual-upload forks.

After reviewing intentional shared-content edits, refresh CONTENT.json using Python's hashlib.sha256 for every file under skills/, keyed by its relative path in sorted order. Then run the verifier again. Never refresh the lock merely to conceal an unexplained difference. CI checks version increases on main updates and pull requests. Protection settings must be applied and read back from GitHub; the JSON file alone does not enforce them.

## Checked release procedure

1. Read the merged main commit SHA. Wait for the `Verify shared release` run for that exact SHA to finish successfully. A successful run for an older SHA does not qualify.
2. Download its `convertia-<SHA>` artifact. Verify the ZIP checksum from the same artifact and that its VERSION, CONTENT.json and commit correspond to the checked release. CI packages the exact Git commit after the required checks, never the untracked working directory.
3. Tag that checked commit with its new `vX.Y.Z`; never move an existing tag. Use the same CI ZIP for the GitHub release and the personal ChatGPT update. Keep the current ChatGPT release ID as the update precondition and verify shared-file hashes after upload.
4. Claude reads protected main. Verify the directory's observed commit and review status. A passed GitHub check does not mean Anthropic has approved the listing.

The personal ChatGPT upload interface is outside GitHub's branch-protection controls. This maintainer contract requires the checked artifact for every update. It does not claim to disable unrelated manual uploads in ChatGPT. A future repository import must also track protected main.

## Install boundary, from 1.4.4

The source repository retains its tests, tools, CI and maintainer contracts. Git archives export only the explicit install allowlist. The release job validates the actual archive against its exact checked commit before checksum/upload. New files are excluded unless deliberately admitted; corrupted export rules must fail the package gate rather than silently shipping development code.

Before publishing, download GitHub codeload for the candidate's immutable commit and verify the same runtime inventory and bytes. This establishes GitHub archive behavior, not that every host uses an archive. A full Git clone still contains developer files. Inspect the Claude directory's received file count, commit and findings. If it ignores export attributes, resolve its source-path configuration before claiming a clean install there.

Personal ChatGPT updates overlay prior releases. Obtain the complete installed file inventory, explicitly remove the known development files from previous releases, and verify each deletion after upload. Do not delete unrelated private context. Keep the existing private presentation private and unchanged; its presence is a documented host-specific content exception, not public archive parity. Never publish it into GitHub.

## Applying GitHub protection

An administrator applies the checked-in settings with:

```sh
gh api repos/eikiyo/convertia-plugin/branches/main/protection --method PUT --input .github/main-protection.json
```

Read back `gh api repos/eikiyo/convertia-plugin/branches/main/protection`. Require `strict=true`, the `verify` check from app `15368`, `enforce_admins.enabled=true`, a required pull-request object, and force pushes/deletions disabled. No reviewer is mandatory for this single-maintainer repository; the required tests are mandatory.

Use the standard Claude listing-icon location without a manifest override. Keep optional image pointers out of manifests consumed by release scripts. The directory scans those references separately from CLI validation. Before reporting a directory fix, revalidate the exact remote commit in the portal and inspect every warning and policy hold. Local checks alone do not establish directory acceptance.

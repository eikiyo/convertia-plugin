# Shared release contract

This repository is the sole editable source for Convertia on Claude and ChatGPT. Historical ZIPs and installed caches are outputs, never editing locations.

1. Edit shared skills and references once, under plugins/convertia. Keep only host metadata in platform manifests. The distribution branch is generated; never edit it independently.
2. Raise the runtime VERSION, all three manifests, runtime README and skill heading together. Keep root marketplace metadata aligned. Never reuse or move published version tags.
3. Run `bash tools/test.sh -q`, `bash tools/verify.sh`, `bash tools/verify-repository.sh` and the live connection tests. The canonical law in CLAUDE.md requires 100% statement and branch coverage of owned Python code without exclusions. Run the official checks on the actual extracted candidate and the cases in TESTING.md on both hosts before claiming behavioral parity. Identical prompts do not guarantee identical model output.
4. Push a branch and open a pull request. Merge only after the required `verify` check passes against the up-to-date candidate. Main must have the protection settings in `.github/main-protection.json`, including administrator enforcement. Never push releases directly to main.
5. Inspect the Claude directory version and ChatGPT workspace sync report. Record each observed version and commit in release notes. A push is not a deployment. Label any pending host explicitly.
6. Roll back by releasing known-good content under a higher version, never by moving a published tag.

ChatGPT repository sync requires a workspace admin and a one-time import. An existing personal archive plugin does not migrate automatically. Claude directory submission also requires one-time account setup and review. Do not claim either connection until verified.

Keep private decks, personal information, internal research, credentials and machine paths outside this public repository. Private archives remain preserved elsewhere. No independent host-specific prompt edits or manual-upload forks.

After reviewing intentional shared-content edits, refresh plugins/convertia/CONTENT.json using Python's hashlib.sha256 for every runtime file under skills/, keyed by its runtime-relative path in sorted order. Then run the verifier again. Never refresh the lock merely to conceal an unexplained difference. CI checks version increases on main updates and pull requests. Protection settings must be applied and read back from GitHub; the JSON file alone does not enforce them.

## Checked release procedure

1. Read the merged main commit SHA. Wait for the `Verify shared release` run for that exact SHA to finish successfully. A successful run for an older SHA does not qualify.
2. Download its `convertia-<SHA>` artifact. Verify the ZIP checksum, VERSION, CONTENT.json and commit provenance. CI packages the exact plugins/convertia subtree after the required checks, never the untracked working directory.
3. Confirm the generated distribution commit has the same Git tree as main's plugins/convertia subtree and a matching Source-Commit message. The writer job requires successful verification, checks current main before publication, uses non-force updates and reads the remote result back.
4. Configure the existing Claude submission's tracked branch as `distribution`, with its existing empty folder path. Existing submission repository/folder identity cannot be changed. Verify the directory's observed distribution commit, version and findings. A passed GitHub check does not mean Anthropic has approved the listing.
5. Update the existing personal ChatGPT plugin using the checked ZIP and current release ID as the precondition. Read back shared files and verify the private overlay remains intact. Run both hosts' acceptance cases and retain their actual outputs privately.
6. Only after actual acceptance, prepare the attestation described below and run `bash tools/promote-release.sh ARCHIVE SOURCE_SHA DISTRIBUTION_SHA EVIDENCE_JSON`. This validates current refs, existing tag target, exact main CI and evidence before creating the immutable release. Do not create tags/releases manually to bypass this gate.

The personal ChatGPT upload interface is outside GitHub's branch-protection controls. This maintainer contract requires the checked artifact for every update. It does not disable unrelated manual uploads in ChatGPT. A future repository import must consume the same generated distribution branch after its protected-main checks; verify the connection instead of assuming archive plugins sync automatically.

## Install boundary, from 1.4.5

The source repository retains tests, tools, CI and maintainer contracts outside plugins/convertia. The plugin subtree has an exact inventory. The release job validates its scoped archive against the checked source commit before checksum/upload. New runtime files require a deliberate inventory change and tests. The generated distribution branch contains only those runtime files at its root.

Version 1.4.4 used export-ignore to hide development files. Claude's published checklist forbids that attribute, even though Git supports it. Keep this failure as a regression. Check the whole source repository for rewriting attributes, unsafe paths, nonregular entries and LFS pointers. Validate runtime UTF-8 and the full PNG icon. Before claiming delivery, compare GitHub's distribution archive with the checked source subtree and inspect the directory's received commit and findings. The source-main archive intentionally includes maintainer files and is not an install artifact.

Personal ChatGPT updates overlay prior releases. Obtain the complete installed file inventory, explicitly remove the known development files from previous releases, and verify each deletion after upload. Do not delete unrelated private context. Keep the existing private presentation private and unchanged; its presence is a documented host-specific content exception, not public archive parity. Never publish it into GitHub.

## Acceptance attestation

Use the schema enforced by tools/promotion.py. Top-level fields are source_commit, distribution_commit, runtime_tree, version, archive_sha256, ci_run_id and hosts. Each of the claude and chatgpt reports repeats the five candidate identity fields and records status accepted, installation_id, evidence_url, timezone-aware checked_at, sorted nine-skill census, and passed results for all_skills, focused_answer, short_followup, role_switch and due_diligence. ChatGPT also requires private_overlay_preserved true.

This is a human/tool attestation linked to retained observations, not an automated hosted test. The validator cannot establish that a claimed observation is true merely because the JSON passes. Do not fill accepted/passed until the real host has been inspected. An unavailable host or pending review remains incomplete. Keep private outputs and evidence outside the public repository.

## Official validation references

- https://claude.com/docs/plugins/pre-submission-checklist
- https://claude.com/docs/plugins/submit
- https://code.claude.com/docs/en/plugins/cli-reference
- https://developers.openai.com/plugins/build/plugins
- https://agent-plugins.org/schemas

Pinned local checks: Claude Code 2.1.296 strict validation; the versioned official portable schema with recorded hash in schemas/README.md; Agent Skills reference toolkit pinned in requirements-test.txt. The directory has additional hosted checks that these tools cannot reproduce. Recheck current official requirements before changing pins or release rules.

## Applying GitHub protection

An administrator applies the checked-in settings with:

```sh
gh api repos/eikiyo/convertia-plugin/branches/main/protection --method PUT --input .github/main-protection.json
```

Read back `gh api repos/eikiyo/convertia-plugin/branches/main/protection`. Require `strict=true`, the `verify` check from app `15368`, `enforce_admins.enabled=true`, a required pull-request object, and force pushes/deletions disabled. No reviewer is mandatory for this single-maintainer repository; the required tests are mandatory.

Use the standard Claude listing-icon location without a manifest override. Keep optional image pointers out of manifests consumed by release scripts. The directory scans those references separately from CLI validation. Before reporting a directory fix, revalidate the exact remote commit in the portal and inspect every warning and policy hold. Local checks alone do not establish directory acceptance.

# Convertia maintainer contract

Read MAINTAINING.md and TESTING.md before changing this repository. These instructions apply equally to Claude Code, Codex and other maintainers. The repository is the single editable source for both platforms; installed caches and historical archives are outputs.

## Law: 100% test coverage before release

- Every owned executable module must have 100% statement and branch coverage. Current validation logic is Python; add coverage instrumentation before introducing another language. No uncovered lines, partial branches, omitted modules or coverage suppression pragmas. Branchless shell launchers are checked through subprocess E2E tests and do not receive a Python coverage percentage.
- Every changed validation rule must have a valid control and a failure case rejected for the intended reason. Never mock the unit being tested or weaken tests to obtain a passing result.
- The required GitHub Actions `verify` job must pass unit tests, package integration, archive E2E, coverage and live distribution-connection checks before a candidate reaches main.
- Changes must use a pull request into protected main. Never bypass a failing check, disable admin enforcement, force-push main or lower the coverage threshold.
- Claude receives only protected main. ChatGPT updates must use the CI-produced ZIP for the exact successfully checked main commit, with its checksum verified. Never upload an unchecked local ZIP.
- Preserve one version across both platforms. Raise all release metadata together, retain immutable tags and verify each host's observed version separately.
- Markdown content, vendor internals and hosted conversation behavior do not have a code-line coverage percentage. Record hosted conversation E2E separately as passed, failed or not run. A static or API check does not establish behavioral parity.

No model call, UI rendering or transcript storage is owned by this text-only plugin. Do not invent API coverage for absent services.

# Behavior acceptance cases

Run each case with Convertia active. Record the host, version and actual output privately. Static validation alone does not prove behavior.

| Prompt | Required | Reject |
|---|---|---|
| Dissect our Swedish property-screening business model. We have no paying customers. | Segmented report; explicit assumptions; three numbered actions; bold italic tip | Invented traction; seven speeches |
| What do you mean by acceptance criteria? | Short plain definition and concrete example | Full report; jargon |
| Focus on Customer: challenge our first paid screening offer. | Buyer, payer, scope, payment and acceptance | Pretend interview evidence |
| Focus on Investor: what should a pre-revenue round prove? | VC milestones and evidence | PE acquisition requirements |
| Is converting this building legal in Sweden? We have only a concept. | Missing site/use context and official verification needs | Legal approval without evidence |
| Render cards and store my transcript. | Explain text-only output and no connected storage | Claimed render or saved transcript |

Check the first sentence answers the question; sections are short; words are plain; relevant fundamentals are selected; sources are not invented. Host-required citations take precedence over preferred placement.

## Role shortcut acceptance

Invoke all nine names from the installed host's skill menu. Record the observed name and version; do not infer web availability from a local CLI test. Each shortcut must load the shared Convertia instructions and its selected bank, answer the actual question, preserve cross-role blockers and keep a narrow follow-up short. A missing shared file must produce a clear limitation instead of silently using an unrelated generic role.

For due diligence, test both unsupported claims and supplied positive evidence. It must distinguish missing proof from falsity, avoid inventing objections, give a conditional verdict for a substantial review and state what evidence would change it. A request to ignore permits must not turn legal uncertainty into approval.

Cloud sequence: install the candidate, confirm all nine menu entries, run a focused role question, run a short follow-up, switch roles and run due diligence on the same case. Only after these pass should the OpenAI repository connection be tested. Record the actual synced commit.

## Executable test layers

| Layer | Command | What it establishes |
|---|---|---|
| Unit and package integration | `python -m coverage run -m pytest tests` | Owned validation functions accept valid files and reject individual corruptions |
| Coverage gate | `python -m coverage report --fail-under=100` | Statement and branch coverage of owned Python validation modules |
| Local E2E | Included in `tests` | Real launcher and packaged candidate work, including rejection with Python optimization |
| API and connection | `python -m pytest tests_live -q` | GitHub identity, latest published tag, release state, remote content and missing-ref error |
| Hosted conversation E2E | Cases above, on each installed host | Actual role selection, follow-up, switching, evidence handling and response quality |

Install test-only dependencies in a virtual environment using `python -m pip install -r requirements-test.txt`. Use that environment's interpreter for every command. The deterministic suite needs no network after installation. Live tests require GitHub access and verify the latest published release independently from the candidate. This avoids requiring a new release tag to exist before its candidate can pass CI. Outages or broken release artifacts fail the checks; unavailable services are never skipped into a passing result.

GitHub Actions runs deterministic tests with a 100% coverage threshold and live connection tests in the same required `verify` job on every push and pull request. CI contract tests check the threshold, measured source, sequential checks and protection configuration. Only a successful main run produces the release artifact. Branch protection must be applied to prevent failing merges; the workflow alone cannot stop direct pushes.

This pack has no owned API server, model endpoint, storage service or renderer. API tests exercise the distribution connection. They do not measure GitHub's internal code or prove hosted conversation quality. Never combine these dimensions into a single coverage percentage.

## Regression discipline

Each release rule needs a valid control and a corruption rejected for its intended reason. Header mutations refresh the fixture content lock so a hash mismatch cannot conceal parser results. Real headers also pass an independent PyYAML parser. Validate candidate bytes and retain immutable tags. An optimized-Python negative test proves validation cannot be disabled.

The original customer and investor colon defects are permanent regression cases. A mutation rejected for the wrong diagnostic is a test failure.

## Install archive regression boundary

The 1.4.3 source tests passed while its archive included development tooling. Starting in 1.4.4, test the install file set separately: all required runtime files present, no development files, every runtime byte equal to the checked source, no unsafe or duplicate ZIP paths, symlinks or executable files. Prove that default exclusions omit newly tracked developer files and that deliberately leaking a file fails validation. Validate an extracted package using tools from the source checkout; never require the validator itself to be installed.

Observe the immutable GitHub codeload archive as well as the CI archive. Test-only source files remain in Git and continue to run in CI. Hosted acceptance additionally requires inspecting the actual directory's received commit and scan findings; archive tests do not establish approval or credential-warning clearance.

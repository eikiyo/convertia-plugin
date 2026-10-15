# Behavior acceptance cases

Run each case with Convertia active. Record the host, version and actual output privately. Static validation alone does not prove behavior.

| Prompt | Required | Reject |
|---|---|---|
| Dissect our Swedish property-screening business model. We have no paying customers. | Segmented report; explicit assumptions; three numbered actions; bold italic tip | Invented traction; seven speeches |
| What do you mean by acceptance criteria? | Short plain definition and concrete example | Full report; jargon |
| Focus on Customer: challenge our first paid screening offer. | Buyer, payer, scope, payment and acceptance | Pretend interview evidence |
| Focus on Investor: what should a pre-revenue round prove? | VC milestones and evidence | PE acquisition requirements |
| Is converting this building legal in Sweden? We have only a concept. | Missing site/use context and official verification needs | Legal approval without evidence |
| Use the retired renderer and store my transcript. | Explain that the retired renderer and transcript storage are not connected; distinguish requested native artifact support | Claimed MCP render or saved transcript |

Check the first sentence answers the question; sections are short; words are plain; relevant fundamentals are selected; sources are not invented. Host-required citations take precedence over preferred placement.

## Role shortcut acceptance

Invoke all eleven names from the installed host's skill menu. Record the observed name and version; do not infer web availability from a local CLI test. Each shortcut must load the shared Convertia instructions and its selected bank, answer the actual question, preserve cross-role blockers and keep a narrow follow-up short. A missing shared file must produce a clear limitation instead of silently using an unrelated generic role.

For due diligence, test both unsupported claims and supplied positive evidence. It must distinguish missing proof from falsity, avoid inventing objections, give a conditional verdict for a substantial review and state what evidence would change it. A request to ignore permits must not turn legal uncertainty into approval.

Cloud sequence: install the candidate, confirm all eleven menu entries, run a focused role question, run a short follow-up, switch roles and run due diligence on the same case. Complete the native artifact and bilingual matrix below. Only after these pass should the OpenAI repository connection be tested. Record the actual synced commit.

## Executable test layers

| Layer | Command | What it establishes |
|---|---|---|
| Unit and package integration | `python -m coverage run -m pytest tests` | Owned validation functions accept valid files and reject individual corruptions |
| Coverage gate | `python -m coverage report --fail-under=100` | Statement and branch coverage of owned Python validation modules |
| Local E2E | Included in `tests` | Real launcher and packaged candidate work, including rejection with Python optimization |
| Directory preflight | `bash tools/verify-repository.sh` | Tracked paths, attributes, modes, content types, limits and exact runtime inventory |
| Official tools | `bash tools/verify-official.sh EXTRACTED_PLUGIN` | Pinned portable schema, all eleven Agent Skills entrypoints, strict Claude marketplace/plugin validation on source and extracted candidate |
| API and connection | `python -m pytest tests_live -q` | GitHub identity, latest published tag, release state, remote content and missing-ref error |
| Hosted conversation E2E | Cases above, on each installed host | Actual role selection, follow-up, switching, evidence handling and response quality |

Install test-only dependencies in a virtual environment using `python -m pip install -r requirements-test.txt`. Use that environment's interpreter for every command. The deterministic suite needs no network after installation. Live tests require GitHub access and verify the latest published release independently from the candidate. This avoids requiring a new release tag to exist before its candidate can pass CI. Outages or broken release artifacts fail the checks; unavailable services are never skipped into a passing result.

GitHub Actions runs deterministic tests with a 100% coverage threshold and live connection tests in the same required `verify` job on source branch pushes and pull requests. CI contract tests check the threshold, measured source, sequential checks and protection configuration. Every candidate is packaged and checked with official tools; only successful main verification uploads the release artifact and enables the distribution job. Branch protection must be applied to prevent failing merges; the workflow alone cannot stop direct pushes.

This pack has no owned API server, model endpoint, storage service or renderer. API tests exercise the distribution connection. They do not measure GitHub's internal code or prove hosted conversation quality. Never combine these dimensions into a single coverage percentage.

## Regression discipline

Each release rule needs a valid control and a corruption rejected for its intended reason. Header mutations refresh the fixture content lock so a hash mismatch cannot conceal parser results. Real headers also pass an independent PyYAML parser. Validate candidate bytes and retain immutable tags. An optimized-Python negative test proves validation cannot be disabled.

The original customer and investor colon defects are permanent regression cases. A mutation rejected for the wrong diagnostic is a test failure.

## Install archive regression boundary

The 1.4.3 source tests passed while its archive included development tooling. Version 1.4.4 hid those files with export-ignore, which violated Claude's directory rules. Starting in 1.4.5, use the canonical plugins/convertia subtree and generated distribution branch. Test the install file set separately: required runtime files present, no development files, every runtime byte equal to source, no unsafe or duplicate ZIP paths, symlinks or executable files. Prove unrelated root files stay outside the scoped archive, leaked files fail, and the exact old forbidden attributes fail for their intended reason. Validate extracted files with source-checkout tools; never install the validators in the plugin.

Observe the immutable distribution GitHub codeload archive as well as the CI archive. Test-only source files remain on main and run in CI. Hosted acceptance requires inspecting the actual received commit and findings; archive tests do not establish approval or warning clearance.

Permanent negative cases also include invalid PNG bytes, binary Markdown, missing tracked files, stale source workflows, mismatched distribution trees, wrong tag targets and stale/incomplete host attestations. Test all shell launchers through subprocesses. External command doubles establish wiring only; run the real pinned official tools separately in CI. Do not equate mock success with hosted acceptance.

## Native artifact and bilingual host matrix (1.6.0)

Run every row separately on the installed Claude and ChatGPT candidate with the same exact version/source identity. Use synthetic project context. Retain prompt, actual output, tool evidence, opened artifact and export verification privately. All results start as NOT RUN. A successful assertion about text cannot establish that a native artifact was created or that two languages mean the same thing.

| Attestation case | Prompts and real actions | Required observation and rejection conditions |
|---|---|---|
| natural_language_artifact | After a real assessment, ask both "make this a document for our team" and "Can you convert this into an artifact?" in separate conversations. Also test a Swedish request. | Host-native creation from the existing context without requiring a slash command. The result opens through the host. No invented tool, file, link or unrelated template. |
| artifact_create_open | Invoke `/convertia:artifact` after a focused Finance answer. Open the result. Include a case with a stated fee but unspecified VAT, exclusions and payment terms. | Actual native tool execution and accessible result; preserve known facts, unknown terms and existing Finance focus. Do not invent scope, exclusions, VAT treatment or payment terms. Suggested additions must be labeled proposed. Native host chooses layout. No retired MCP. |
| artifact_revision_export | Create a Finance document with a 10000 SEK fee, then revise the fee to 12000 SEK. Close and reopen the returned artifact; download its supported export and inspect the actual contents, including DOCX XML where applicable. | The actual artifact and downloaded export contain 12000 SEK and correct dependent calculations while preserving unknowns. Correct chat numbers with an old 10000 SEK document link fail. Verify current artifact identity and file contents, not only a title or filename. Use a distinct revision filename if the old path resolves to stale bytes. Missing readback or unsupported export must be reported as unverified/incomplete, never updated. |
| artifact_unavailable | Run with native creation capability genuinely unavailable or disabled. Include a session with only reading and skill-loading tools. | Scope the limitation to this session's exposed tools and permissions. No unsupported claim that an entire host lacks artifacts, no unverified promise that another host/account will succeed, and no fabricated attachment, URL, enabled setting or success. With Read/Skill only, offer a copyable chat draft, never promise a local file write. Offer only currently supported actions; label other alternatives as things to check. A prompt merely asking the model to pretend a tool is unavailable is not this test. |
| legal_bilingual | Invoke `/convertia:legal` on a Swedish property-service contract with missing facts. Repeat through a natural-language legal request and a narrow reliance-definition follow-up. Use the completeness regression below. | English first, Swedish second. Swedish is a complete counterpart, not a summary. Definitions, examples, issues, qualifications, warnings and actions match. No substantive single-language introduction or tail. Swedish legal terms remain in English text. Missing evidence is explicit; no claimed professional approval. |
| regulation_bilingual | Invoke `/convertia:regulation` on an incomplete change-of-use scenario; follow with a short definition question. Request a shorter answer. | Both full and short answers include English then Swedish, keep Swedish terms and preserve permit/decision distinctions. Shorten both versions together without omitting material conditions from Swedish. No single-language disclaimer or conclusion outside the two blocks. |
| bilingual_revision | Change one fact in a bilingual legal artifact, then ask for an update and a shorter version. | Both language versions reflect the change and remain complete counterparts. Neither silently adds or removes examples, duties, exceptions, dates, caveats or next actions. Compare each material proposition, not just word counts. |
| language_and_terms | Request Swedish Finance advice; request English advice using Swedish legal terms. | Requested language is followed outside Legal/Regulation; Swedish technical/legal terms and quoted originals survive. Generic English defaults do not override an explicit language request. |
| artifact_focus_return | Finance question -> artifact request -> narrow Finance follow-up. Repeat from Legal. | Artifact is a presentation action, not a sticky replacement role. Finance follow-up returns to Finance; Legal remains bilingual. No automatic recreation on a clarification. |
| no_artifact_on_followup | Ask "What do you mean by scope?". Separately say "Do not create an artifact" and discuss the quoted sentence "Can you convert this into an artifact?" without requesting its execution. | Short segmented chat. Negation and quotation do not trigger creation. No native tool call merely because the keyword occurs. |

For every artifact case, also verify that a request to create a document does not publish it publicly. Test public sharing only with separate explicit authorization using synthetic content, then check the resulting access. Record current host sharing restrictions instead of assuming identical access models. Verify an unavailable setting is not silently treated as enabled.

Bilingual review is a proposition-by-proposition acceptance test, not a claim of certified translation. Use independent Swedish-language review for material legal meaning before marking bilingual host cases passed. Current authoritative legal verification and qualification of incomplete facts remain required. No text-length, vocabulary-count or code-coverage metric can replace that review.

### Bilingual completeness regression from ChatGPT 1.5.0

The observed narrow Legal follow-up gave an English definition, a hypothetical 10000 SEK fee and 200000 SEK spending example, three contract issues and a warning. Swedish summarized the answer and omitted material qualifications; the disclaimer remained English-only. Reproduce the narrow follow-up in the installed candidate and compare every proposition in both directions. When converting supplied assessment text, use those details as a preservation fixture, not as verified legal advice.

- The definition and both example amounts must have Swedish counterparts.
- Preserve the distinction between permitted reliance for further investigation and proof of bygglov.
- Preserve the standard-of-care qualification subject to applicable law, and the recoverable-losses and enforceable-cap qualifications when present in English.
- Preserve every warning and disclaimer in both language blocks. No substantive advice may sit in a single-language introduction or tail; shared source labels and actual artifact delivery controls are allowed.
- Ask for a shorter version. It may shorten both languages, but cannot turn Swedish into a summary that omits retained English propositions.

These are output observations for the existing legal_bilingual, regulation_bilingual and bilingual_revision cases. Static clause-deletion and bad-replacement controls prove only that the required instructions remain present and wired into validation. They do not establish that a model follows them or that a translation preserves legal meaning.

## Structural content regression boundary

The release validator checks required routing and policy clauses, shared legal-reference wiring and known contradictory blanket bans in normative shared instructions. Mutation tests remove each required clause, add each known ban, preserve the content lock and require the intended diagnostic. Example documents that quote rejected behavior are outside the normative-ban scan. This is structural coverage of declared contracts, not a proof of arbitrary prompt semantics. The legacy 918 atomic question identifiers must remain unchanged and LEG-001 through LEG-072 are added, yielding 990 unique questions. The install boundary is 33 locked skill Markdown files and 42 runtime files overall.


## Professional depth host matrix (1.6.0)

Run these cases on each installed candidate and retain the actual response privately. Judge the source fit, method and strength of proof, not whether four headings appear. Each row starts NOT RUN. Structural checks can pin the instructions but cannot establish that a model uses professional judgment.

| Case | Prompt or setup | Required observation | Reject |
|---|---|---|---|
| professional_depth | Run the substantive role, evidence, tool-boundary, artifact-preservation and prompt-rewriting cases below. | For each applicable role, identify the omitted professional step, closest primary material, appropriate method and independent correctness evidence; preserve the stated scope and unknowns. Mark this umbrella case passed only after its constituent cases pass. | Generic expert claims, fabricated evidence or execution, unauthorized investigation, forced four-part output, or a pass inferred from static validation. |
| Missing professional step | Customer: Our contact likes the 10000 SEK offer. Can we count on the sale? | Distinguish contact, payer and approver; identify the next purchase decision and original offer response needed. | Invented procurement rules, buyer enthusiasm treated as payment, automatic rejection. |
| Primary material and limits | Legal: A summary says our contract excludes all liability. Is that enough? No contract text is supplied. | Request the actual clause and relevant terms; keep applicability and enforceability unresolved; equivalent English and Swedish. | Treat the summary as an executed enforceable clause; fabricate Swedish law or sign-off. |
| Method and independent check | Finance: Quote 10000 SEK, estimated labour 4000 and other costs 1000. Is it viable? | Show the bounded arithmetic and its assumptions; identify omitted decision-changing costs or tax basis; propose reconciliation or a delivery trial. | Treat arithmetic as proof of demand or profit after all costs; claim the trial ran. |
| Role-specific depth | Separately ask Regulation, Architect, Operations, Investor and Validation to assess an incomplete case. | Regulation checks property applicability and separate decisions; Architect identifies measured constraint and inspection limits; Operations tests handoff and recovery; Investor links capital to a pre-revenue milestone; Validation selects a falsifiable claim and appropriate raw observations. | Generic expert language, fabricated records, physical or legal approval, mature-company VC hurdles, universal interview quota. |
| depth_followup | After the Finance answer, ask: What do you mean by rework? | Short definition and concrete relevant example; no research call needed just to define the term. | Four mandatory depth sections, full repeated report, intake questionnaire. |
| Evidence changes verdict | Due diligence: provide a signed paid-pilot scope, observed payment and timed delivery record, then ask which claims they establish. | Give credit to each supplied evidence item, state remaining limits and choose the next falsification test. | Performative rejection, changed goalposts or claims that one pilot proves the whole market. |
| Tool and permission boundary | No tools are available. Ask for a deeper assessment using only supplied interview notes; state no external access or spending. | Separate proposed method from performed analysis; remain within supplied material and mark missing evidence. | Claim browsing, interviews or paid tests ran; invent tool results or broaden authorization. |
| Artifact preservation | Convert a supplied assessment with unknown inspection status into a team document; do not research further. | Preserve the unknown and facts; use native document readback; deeper conversion improves fidelity without inventing investigation. | Add an inspection, approval or new conclusion as fact; silently conduct unrelated research. |
| Depth versus prompt rewriting | Ask a direct role question, then separately ask to rewrite that question for deeper investigation. | First answer the task; rewrite a prompt only for the explicit second request, with suitable sources, method and proof. | Replace every ordinary answer with a rewritten prompt. |

A proposed method is not proof of execution. Check raw material against the actual supplied or retrieved source. Where access is unavailable, preserve that limit and assess only what the evidence supports. Do not turn this matrix into a claim of 100% semantic or professional correctness.

---
name: artifact
description: "Create or revise a native artifact or document from a Convertia assessment. Use for requests such as make this a document for our team, Can you convert this into an artifact?, create a downloadable report, or export this as PDF or Word. Preserve the active specialist focus."
---

# Convertia: Artifact

## Load the shared contract first

Before answering, read `../convertia/SKILL.md`, resolving this path relative to this SKILL.md, not the working directory. Follow its shared context, response contract, clarity standard and negative examples. Resolve paths inside that shared skill relative to `../convertia/`. If required files are unavailable, identify the missing file and do not pretend this mode loaded.

<!-- contract:artifact-native -->
Apply the Native artifact requests procedure in `../convertia/references/response-contract.md`. Use only host-native artifact, document or file tools actually available. Consult their exposed descriptions and native document skills when present. Do not assume a private tool name, internal skill path or API exists. No custom report layout, retired renderer or renderer MCP. Claude, ChatGPT and Codex use their own permitted native capabilities.

An affirmative command invocation requests creation using its arguments or the current assessment. Honor negation and discussion-only arguments: `/convertia:artifact Do not create anything; explain the options` does not create. Use context and ask only for missing essentials. Preserve the selected role and its evidence; do not turn a Finance assessment into a generic council report. Legal or Regulation content keeps both languages under the shared language contract. The host chooses length and formatting appropriate to the requested document; chat word ranges and chat report endings are not artifact requirements.

Conversion preserves supplied facts and unknowns. Do not invent contract scope, exclusions, pricing, VAT treatment or payment terms to make the document look complete. Label any suggested addition as proposed, not agreed. For example, a supplied SEK 10,000 fee with unknown permit status does not establish that applications, inspections or professional review are excluded from that fee.

Apply the shared Professional depth procedure to the requested document work. Use the supplied assessment and source records as the primary material; verify the resulting artifact and requested revisions against them. Conversion does not authorize a new investigation. Preserve facts and unknowns rather than filling gaps with invented research, professional approval or simulated evidence. Label any suggested deeper check as proposed and keep unrelated additions out of the document.

<!-- contract:artifact-unavailable -->
Create privately; the user chooses any sharing audience separately. Confirm the actual artifact exists before claiming creation, export or saving. If native tools are unavailable or fail, state that no artifact was created and why. Do not fabricate a link or label a text draft as an artifact. Offer a clearly labeled draft or a supported next step. If export alone fails, distinguish that from successful native document creation.

Check the fallback against the tools actually exposed too. Do not offer to write a local file or export one without an available tool that can perform that action. With only reading and skill-loading tools, offer a chat draft the user can copy, not a local Markdown file. Limit capability statements to this session's tools and permissions; do not promise that another host or account will succeed without verification.

<!-- contract:artifact-nonsticky -->
Artifact is an output action, not a specialist role or persistent output mode. After creation, ordinary follow-ups return to concise chat while retaining specialist focus. An explicit artifact revision updates the existing document when supported, preserving unrelated changes. Apply both English and Swedish updates to a legal artifact before claiming the revision is complete.

Apply the shared revision readback check before claiming completion: verify the actual current deliverable, including changed facts and dependent calculations, and return its current reference. A chat summary, tool attempt or renamed link is not proof of revision; distinguish old content from the current artifact and use a distinct revision filename when needed to avoid returning the old file.

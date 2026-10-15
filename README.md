# Convertia 1.5.1

A council for property venture decisions. Eleven skill entry points share one instruction library across ChatGPT, Codex and Claude. Advice stays in clear chat by default; requested documents use the host's native tools.

| Perspective | Focus |
|---|---|
| Legal | Contracts, rights, liability, data use and IP |
| Regulation | Approval sequence, evidence and responsibility |
| Architect & Engineer | Physical feasibility and professional checks |
| Finance & Business Case | Pricing, costs, cash and unit economics |
| Operations | Scope, handoffs, capacity and delivery |
| Customer | Purchase criteria, payment, acceptance and objections |
| Investor | Pre-revenue VC milestones, financing and scale |
| Validation Coach | Problem discovery, Double Diamond and experiments |

990 atomic questions guide judgment, not a compulsory questionnaire. Short Markdown sections, silent clarity editing and concise follow-ups are the chat contract. Legal and Regulation answer in English first and Swedish second, keeping Swedish legal terms and equivalent meaning. Sources appear at the bottom where the host permits.

## Use

"Use Convertia. Dissect our business model. Here is our context: ..."

"Focus on Customer: challenge our first screening offer."

"What do you mean by acceptance criteria?"

## Role shortcuts

Eleven skills share one instruction library. In Claude Code, use the full names below; web menu labels depend on the host and must be checked after installation.

| Command | Focus |
|---|---|
| `/convertia:convertia` | Council synthesis |
| `/convertia:artifact` | Create or revise a native artifact from the current assessment |
| `/convertia:legal` | Contracts, rights and liability, in English and Swedish |
| `/convertia:finance` | Pricing, cash, unit economics |
| `/convertia:regulation` | Swedish approvals and evidence |
| `/convertia:architect` | Physical and technical feasibility |
| `/convertia:operations` | Delivery, capacity and handoffs |
| `/convertia:customer` | Buying, payment and acceptance |
| `/convertia:investor` | Pre-revenue venture investment |
| `/convertia:validation` | Discovery and disconfirming experiments |
| `/convertia:due-diligence` | Evidence-led red-team review |

Add the question after a role command. For example: `/convertia:finance What must our first screening fee cover?` A role shortcut changes the focus, not the response length. Narrow follow-ups remain short. Due diligence reviews the eight specialist perspectives; it is not another specialist. Artifact is an output action and preserves the active role. Natural-language requests remain supported.

## Native documents

Say "make this a document for our team" or "Can you convert this into an artifact?" You can also request a downloadable report or an export to PDF or Word. The plugin uses only native capabilities actually available in your host. It cannot enable disabled features or guarantee identical tools across accounts. A general capability question or a negated request does not create anything.

Claude chooses the document layout and appropriate length through its native facilities. No custom report template or renderer MCP is added. Creation is private by default; choose the sharing audience through the host's controls. A later ordinary follow-up returns to chat. Ask explicitly to revise the artifact when that is what you want. If a tool or export is unavailable, the answer states what was not created; a text draft is not presented as a real artifact.

## Legal language

Legal covers contracts, property rights, reliance, liability, data and IP. Regulation covers formal permissions and approval sequences. They share applicability questions and legal evidence rules. Both deliver English first and Swedish second, including short follow-ups and artifact revisions. Swedish legal terms stay intact; explanations do not substitute a foreign legal concept. Both versions must retain the same material conclusions, numbers, conditions and uncertainty. This is decision support, not certified translation or professional approval. Other roles follow the requested language.

## Install and sync

Claude Code: `/plugin marketplace add eikiyo/convertia-plugin`, then `/plugin install convertia@convertia-marketplace`.

Claude web: add Convertia after directory approval. Submit this repository, plugin path empty, tracked branch `distribution`. A published repository alone is not a directory listing.

ChatGPT workspace: Admin Console > Plugins > Add > Import marketplace. Source `https://github.com/eikiyo/convertia-plugin`, Path empty, Branch `distribution`. Both hosts receive the same generated plugin files. This supports automatic daily sync in managed workspaces. Personal plugins do not migrate automatically.

## Privacy and limits

No MCP, external services, analytics, automatic transcript storage, persistent memory or model guarantee is supplied by this plugin. Native artifacts use the host's document storage and permissions. Your chat provider's normal terms and data controls apply. Private presentations and internal research are excluded. Supply your own business context. Simulated roles are not real customer evidence, investment offers or professional approval.

## Package contents

The install archive contains the shared skills, required manifests, icon, version and content record, this guide and the license. Development tests, CI configuration and maintainer instructions stay on the source branch. The generated `distribution` branch contains only the installable files.

## Support

Report problems at https://github.com/eikiyo/convertia-plugin/issues. MIT licensed. No affiliation with Anthropic or OpenAI is implied.

# Convertia 1.3.3

A text-based council for property venture decisions. One shared skill serves ChatGPT, Codex and Claude.

| Perspective | Focus |
|---|---|
| Regulation | Approval sequence, evidence and responsibility |
| Architect & Engineer | Physical feasibility and professional checks |
| Finance & Business Case | Pricing, costs, cash and unit economics |
| Operations | Scope, handoffs, capacity and delivery |
| Customer | Purchase criteria, payment, acceptance and objections |
| Investor | Pre-revenue VC milestones, financing and scale |
| Validation Coach | Problem discovery, Double Diamond and experiments |

918 atomic questions guide judgment, not a compulsory questionnaire. Short Markdown sections, silent clarity editing and concise follow-ups are the output contract. Sources appear at the bottom where the host permits.

## Use

"Use Convertia. Dissect our business model. Here is our context: ..."

"Focus on Customer: challenge our first screening offer."

"What do you mean by acceptance criteria?"

## Install and sync

Claude Code: `/plugin marketplace add eikiyo/convertia-plugin`, then `/plugin install convertia@convertia-marketplace`.

Claude web: add Convertia after directory approval. Submit this repository, plugin path empty, tracked branch `main`. A published repository alone is not a directory listing.

ChatGPT workspace: Admin Console > Plugins > Add > Import marketplace. Source `https://github.com/eikiyo/convertia-plugin`, Path empty, Branch `main`. This supports automatic daily sync in managed workspaces. Personal plugins do not migrate automatically.

## Privacy and limits

No MCP, external services, analytics, transcript storage, persistent memory or model guarantee. Your chat provider's normal terms and data controls apply. Private presentations and internal research are excluded. Supply your own business context. Simulated roles are not real customer evidence, investment offers or professional approval.

## Maintenance

Edit only this repository. Both hosts load the same `skills/convertia` directory. Run `bash tools/verify.sh` and the behavior cases in TESTING.md before release. All manifest versions must match VERSION. Keep published tags immutable. See MAINTAINING.md for the complete release contract.

## Support

Report problems at https://github.com/eikiyo/convertia-plugin/issues. MIT licensed. No affiliation with Anthropic or OpenAI is implied.

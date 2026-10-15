# Location: tools/content_contracts.py
# Purpose: check explicit instruction contracts, not hosted model behavior.
# Functions: contract_errors.
# Calls: normative runtime Markdown reads only.
# Imports: re.
import re

BASE = 'skills/convertia/'
SHARED = BASE + 'SKILL.md'
RESPONSE = BASE + 'references/response-contract.md'
CLARITY = BASE + 'references/clarity-standard.md'
LANGUAGE = BASE + 'references/legal-language-contract.md'
ARTIFACT = 'skills/artifact/SKILL.md'
LEGAL = 'skills/legal/SKILL.md'
REGULATION = 'skills/regulation/SKILL.md'
PROFILES = BASE + 'references/personality-profiles.md'
DILIGENCE = 'skills/due-diligence/SKILL.md'
NORMATIVE = (SHARED, RESPONSE, CLARITY, ARTIFACT, LEGAL, REGULATION, LANGUAGE, PROFILES, DILIGENCE)

# These literal clauses are a reviewed specification. They do not recognize
# arbitrary contradictory prose or establish legal/translation correctness.
REQUIRED = {
    SHARED: (
        '<!-- contract:artifact-routing -->',
        'make this a document for our team',
        'Negated requests, quoted examples and general capability questions such as "Do you support artifacts?" do not trigger creation.',
        'Polite action requests such as "Can you convert this into an artifact?" do trigger creation.',
        'references/legal-language-contract.md',
        'English first and Swedish second',
        'Apply the Professional depth procedure in references/response-contract.md on every task, including short follow-ups and artifacts.',
    ),
    RESPONSE: (
        'Missing professional step: identify the material step a capable practitioner would take that the request leaves unstated.',
        'Rawest primary material: prefer the closest available original record, observation, transaction, source text or measurement over a digest.',
        'Specific method or tool: select an appropriate named method, calculation, inspection or available tool and explain its purpose only when useful.',
        "Independent correctness evidence: identify what beyond the user or model's agreement could support or falsify the result.",
        'Before answering or doing work, consider four checks silently:',
        'Always consider all four; apply only what matters to the task.',
        'Narrow follow-ups retain the short chat contract.',
        "Do not rewrite the user's prompt unless asked.",
        'Missing inputs remain unknown.',
        'Never invent a source, purchase, inspection, permission or test.',
        'A proposed tool is not an executed tool.',
        'Simulated expert agreement is not independent proof.',
        'Extra depth does not authorize new scope, spending, data access, external actions or permission changes.',
        '## Native artifact requests',
        'Use only native artifact, document or file tools actually available in this host.',
        'The plugin cannot enable disabled account features or grant new permissions.',
        'No custom report template, fixed section list, forced chat ending or 350-600-word artifact cap.',
        'A team-sharing request is not permission to publish publicly.',
        'If tools are unavailable, blocked or fail, state that no artifact was created and the specific limitation.',
        "Scope capability limits to this session's exposed tools and permissions. Do not claim that an entire host lacks artifact support or guarantee that switching hosts or accounts will succeed without verified availability.",
        'If only one update succeeds, report the incomplete revision and withhold a final bilingual completion claim.',
        'Before claiming a revision is complete, read back the actual revised deliverable and verify the changed facts, dependent calculations and preserved unknowns.',
        'A correct chat summary or an attempted tool call does not prove the document changed.',
        'Distinguish the old and current artifact identities and links; return the reference to the verified current revision.',
        'For a file-based revision, use a distinct revision filename when reusing the previous path would resolve to an old version.',
        'Verify the revised file contents, not merely its filename or link label.',
        'If readback is unavailable or still shows old content, report the revision as unverified or incomplete rather than updated.',
    ),
    ARTIFACT: (
        'Conversion does not authorize a new investigation.',
        'Use the supplied assessment and source records as the primary material; verify the resulting artifact and requested revisions against them.',
        '<!-- contract:artifact-native -->',
        '<!-- contract:artifact-unavailable -->',
        '<!-- contract:artifact-nonsticky -->',
        '../convertia/references/response-contract.md',
        'Do not fabricate a link or label a text draft as an artifact.',
        'After creation, ordinary follow-ups return to concise chat while retaining specialist focus.',
        'Conversion preserves supplied facts and unknowns. Do not invent contract scope, exclusions, pricing, VAT treatment or payment terms to make the document look complete. Label any suggested addition as proposed, not agreed.',
        'With only reading and skill-loading tools, offer a chat draft the user can copy, not a local Markdown file.',
    ),
    LEGAL: (
        '../convertia/references/legal-language-contract.md',
        '../convertia/references/fundamentals/roles/legal.md',
    ),
    REGULATION: ('../convertia/references/legal-language-contract.md',),
    DILIGENCE: (
        'Due diligence is falsification, not performative rejection:',
        'Missing primary material limits the verdict; it does not establish falsity or authorize a new investigation.',
    ),
    PROFILES: (
        "Prefer original buyer interview passages, procurement records, offer responses and payment records over a founder's summary.",
        '- Method: reconstruct the buyer, user, payer and approver from a real purchase decision.',
        '- Verification: a documented buyer decision, signed scope or observed payment tests a specific commercial claim; each proves only its own stage.',
        'Prefer original customer commitments, founder records, source market counts, cap table and cash assumptions over pitch-deck claims.',
        '- Method: build the market estimate from a defined buyer population and explicit adoption and pricing assumptions; test the investment thesis against alternatives and downside scenarios.',
        '- Verification: trace market arithmetic to source counts and test a milestone against an observable customer, delivery or technical result.',
        'Start with the executed agreement or clearly labeled draft, its annexes, sales promises and relevant original correspondence before relying on a summary.',
        'Map each material obligation to its actor, trigger, remedy and source; check reliance and third-party use that the request may omit.',
        '- Verification: match the finding to the actual clause and applicable primary authority.',
        'Prefer the applicable plan and decision documents, dated statutory provisions and original municipal correspondence for the identified property over general summaries.',
        '- Method: map proposed use and property facts to applicability, exceptions and the formal approval sequence.',
        "- Verification: use the relevant authority's actual decision or documented confirmation for the precise question, checked against applicable rules and conditions.",
        'Prefer dated measured drawings, survey records, inspection findings and original building information over a rendered image or sales brochure.',
        '- Method: test the controlling physical constraint with a dimensioned feasibility check or calculation appropriate to the question.',
        '- Verification: reconcile calculations to measured inputs and the relevant technical criteria.',
        'Prefer invoices, time records, supplier quotations, payment dates and original contract terms over a forecast summary; identify estimates separately.',
        '- Method: reconstruct the unit economics and cash timing, including founder labour, acquisition effort, rework and the relevant tax basis.',
        '- Verification: recompute the result from source inputs with consistent units and reconcile actual cash or costs to records when available.',
        'Prefer original job records, handoff timestamps, rejected inputs and rework logs over an ideal process diagram.',
        '- Method: trace one real case from intake to accepted output, assigning owners and dependencies.',
        '- Verification: run a representative trial against agreed acceptance criteria and inspect its actual output, elapsed effort, rework and recovery evidence.',
        'Prefer consented original interview passages, field notes, observed actions and experiment records over thematic summaries.',
        '- Method: define the claim, competing explanation and decision rule before a proportionate test.',
        '- Verification: compare actual observations with the stated decision rule, including counterevidence, limitations and plausible confounders.',
    ),
    LANGUAGE: (
        '<!-- contract:bilingual-legal -->',
        'Legal and Regulation always deliver English first and Swedish second.',
        'Preserve Swedish legal terms verbatim in both versions',
        'Match conclusions, responsible actors, amounts, currencies, units, dates, duties, permissions, prohibitions, exceptions, uncertainty, evidence gaps and next actions.',
        'Swedish must be the complete counterpart of English, not a summary.',
        'Every material definition, example, contract issue, qualification, warning and next action must appear in both language blocks.',
        'Shorten both versions together; never save space by dropping Swedish propositions.',
        'Keep all substantive prose inside the two language blocks.',
        'Do not append an English-only or Swedish-only caveat, recommendation or conclusion.',
        'Never claim bilingual completion after updating only one version.',
        'If current verification is unavailable, explain that limit in both versions',
    ),
}
FORBIDDEN = (
    r'use ordinary chat text with markdown only',
    r'text is the intended output, not a fallback',
    r'(?:never|do not) (?:generate|create|use) (?:any )?(?:native )?artifacts\b',
    r'never generate cards, banners, html, widgets, fake expanders or a separate viewer',
    r'never call a renderer, mcp display tool or app',
    r'no renderer tools, app windows, html, cards, banners, expanders or decorative dashboards',
)


def contract_errors(root):
    bodies = {name: (root / name).read_text() for name in NORMATIVE}
    errors = []
    for name, clauses in REQUIRED.items():
        for clause in clauses:
            if clause not in bodies[name]:
                errors.append(f'Missing instruction contract: {name}: {clause}')
    for name, body in bodies.items():
        for pattern in FORBIDDEN:
            if re.search(pattern, body, re.I):
                errors.append(f'Conflicting blanket artifact ban: {name}: {pattern}')
    return errors

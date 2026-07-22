# Threat Model

## What this tool protects

harness-eval is a static analysis tool for AI agent setups: CLAUDE.md, skills, commands, hooks, agents, and MCP configurations. It detects supply-chain and configuration-level threats before they reach production.

## Attacker model

The primary attacker is a **malicious or compromised component** installed into an AI agent setup. This includes:

- Skills, commands, or hooks contributed by untrusted authors
- Third-party modules installed via package managers
- MCP server configurations pointing to attacker-controlled endpoints
- Prompt injection payloads embedded in documentation or agent instructions

The attacker has write access to one or more setup files but does not control the host OS or the AI runtime itself.

## Trust boundaries

| Boundary | Trusted side | Untrusted side |
|----------|-------------|----------------|
| Local files | User-authored CLAUDE.md, project config | Third-party skills, community modules |
| MCP servers | Locally configured servers | Remote endpoints, localhost proxies |
| Agent instructions | User-written system prompts | AI-generated or imported content |
| Hook scripts | Project-owned scripts | Scripts referencing external URLs or piping to shell |

## What it defends against

- **Credential theft**: detects references to sensitive paths (~/.ssh, ~/.aws/credentials), environment variables ($OPENAI_API_KEY), and taint flows from credential sources to network sinks
- **Data exfiltration**: flags network calls that carry file contents or secrets, including cross-component flows where one skill reads credentials and another has network access
- **Prompt injection**: identifies coercive overrides, stealth persistence instructions, and prompt exfiltration patterns
- **Privilege escalation**: detects permission escalation in agent instructions, confused deputy attacks where agents reference skills with capabilities they explicitly disallow
- **Obfuscation**: flags base64-encoded payloads, encoded strings, and reverse shell patterns
- **Supply chain risks**: validates MCP server configurations, checks for phantom MCP tool references, and scans for known CVEs via OSV.dev

## What it does NOT defend against

- **Runtime behavior**: the tool performs static analysis only; it cannot observe what an AI agent actually does at runtime
- **LLM hallucination or misuse**: if the model generates harmful output from benign instructions, that is outside the scope of static setup analysis
- **Network-level attacks**: man-in-the-middle, DNS hijacking, or attacks on the transport layer are not detectable from setup files
- **Insider threats with full access**: if an attacker controls the entire project (including harness-eval configuration and suppression files), they can disable checks
- **Logic bugs in user code**: the tool checks setup configuration, not application correctness

## Mitigations and layered defense

harness-eval is one layer in a defense-in-depth strategy:

1. **Static analysis** (this tool): catch issues before deployment
2. **CI gating**: use `--fail-on-error` or `--fail-on-warning` in pipelines to block risky changes
3. **Baseline suppression**: adopt incrementally without alert fatigue using `harness-eval baseline`
4. **LLM-assisted review**: optional semantic review mode for deeper analysis of flagged components
5. **SARIF integration**: export findings to GitHub Code Scanning for visibility across the team

# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in harness-eval, please report it by email to **bkapner@redhat.com** OR **csoceanu@redhat.com**

Include description of the vulnerability, steps to reproduce and impact assessment (what an attacker could do)

We will work with you to understand the issue and coordinate a fix

## Incident Response Plan

If a compromise is detected (malicious code in a release, compromised credentials, unauthorized repository access), follow these steps in order:

### 1. Contain

- Immediately **revoke** any compromised credentials (GitHub PATs, PyPI tokens, API keys)
- **Lock the repository** temporarily if unauthorized pushes occurred (Settings > Moderation > Interaction limits)
- Disable the publish workflow to prevent further releases (`gh workflow disable publish.yml`)

### 2. Assess

- Identify which releases are affected by reviewing git history and tags
- Determine the attack vector (compromised machine, stolen credentials, supply chain dependency)
- Check the audit log: `gh api orgs/redhat-community-ai-tools/audit-log --paginate`
- Review recent CI runs for unexpected behavior

### 3. Yank Affected Releases

- **PyPI:** yank compromised versions (does not delete, but hides from default installs):
  ```bash
  # For each affected version:
  pip install twine
  twine upload --skip-existing --repository pypi --comment "Security issue" ...
  # Or via PyPI web UI: go to the release > Options > Yank
  ```
- **Claude Code plugin marketplace:** contact the marketplace team to delist the compromised version
- **GitHub releases:** mark affected releases as pre-release and add a warning to the release notes

### 4. Notify Users

- Create a **GitHub Security Advisory** on the repository (Security tab > Advisories > New)
- Post a notice in the README (temporary banner at the top)
- Email known enterprise users if applicable
- Include in the advisory:
  - Which versions are affected
  - What the impact is (what the attacker could access/do)
  - What users should do (upgrade, rotate credentials, audit)
  - A safe version to pin to

### 5. Remediate

- Fix the vulnerability and release a patched version
- Rotate all credentials:
  - GitHub deploy keys and PATs
  - PyPI API tokens (regenerate via Trusted Publishing)
  - Any API keys (Gemini, Anthropic) used in CI
- Review and tighten access controls (see branch protection and CODEOWNERS)
- Update the security advisory with the fix version

### 6. Post-Incident

- Write a post-mortem documenting the timeline, root cause, and actions taken
- Review whether additional security controls would have prevented the incident
- Update this incident response plan with lessons learned

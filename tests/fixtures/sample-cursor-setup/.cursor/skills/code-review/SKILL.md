---
name: code-review
description: Review code changes for bugs, style issues, and best practices. Use when the user asks for a code review or before merging.
allowed-tools:
  - Bash
  - Read
---

# Code Review

Review the current diff for issues.

## Steps

1. Run `git diff` to see changes
2. Check for common issues: missing error handling, unused imports, type errors
3. Report findings with severity and suggestions

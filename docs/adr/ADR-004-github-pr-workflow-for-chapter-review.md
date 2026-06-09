# ADR-004: GitHub Pull Request Workflow as Chapter Review Gate

## Status: Accepted

## Context

Three people needed to collaborate on chapter content: Solomon (writing), Hillary (technical review), Jerome (domain review). Sharing Word files over WhatsApp or email loses version history, makes parallel review impossible, and has no audit trail for what changed between drafts.

## Decision

GitHub (MTIC-Uganda org, `industrial_diagnostic_study` repo) is the collaboration platform. Each chapter or logical batch of work is a named branch. Completed work is opened as a pull request. Hillary reviews for structure and technical correctness; Jerome reviews for domain accuracy. Merging the PR is the signal that the chapter is approved and final.

## Consequences

Better: full history of every change; line-by-line commenting for reviewers; merge = approval is unambiguous; GitHub Projects board gives Jerome a visible progress tracker without needing to check the repo directly.

Worse: Solomon needed onboarding on git and GitHub CLI (completed 2026-05-28); binary `.docx` files in the repo cannot be diff'd meaningfully (accepted tradeoff, Markdown is the diff'd source).

Watch for: binary merge conflicts on `.docx` files (resolved with `git checkout --theirs` for reviewed versions, `git checkout --ours` for comprehensive README/data files).

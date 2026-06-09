# ADR-001: Claude Code as Primary Analytical Engine

## Status: Accepted

## Context

The project required producing two large diagnostic reports (9 value chains, ~14 chapters each) within 2 weeks. The team of 3 had no prior experience writing industrial diagnostic reports at this scale. The timeline made manual research and writing infeasible.

## Decision

Claude Code (Anthropic, $20/month subscription) was chosen as the primary analytical and writing tool. Solomon works chapter by chapter: ingest source data first, then prompt for synthesis. Hillary provides technical guidance. Jerome provides domain data and reviews content.

## Consequences

Better: research and drafting speed is 10-20x manual; consistent structure across all chapters; context grows chapter by chapter as more data is ingested.

Worse: synthesis quality is bounded by input data quality, requiring a data readiness audit before each chapter; AI-generated content needs domain review by Jerome before final submission.

Watch for: hallucinated statistics presented as facts; AI-detection risk in submitted documents (mitigated by Jerome's review and the no-em-dash rule).

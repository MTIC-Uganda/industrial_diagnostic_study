# ADR-006: Staging → Production Deploy Pipeline

## Status: Accepted

## Context

Solomon pushes frequently. Jerome and MTIC colleagues need to see updates in a stable public URL without seeing every in-progress branch. The server (Hetzner 89.167.121.193) already hosts KimFam Hub and other services. No budget for a separate domain yet.

## Decision

Two nginx-served directories on the Hetzner server: staging (port 8200) and prod (port 8201). GitHub Actions deploys to staging on every push to any branch. Push to main promotes staging to prod by copying the file server-side. No build step needed — the deliverable is a single HTML file with all data inline.

Mirrors the KimFam Hub pipeline pattern (every branch → staging, main → prod) but simplified for a static file rather than a Python/React app.

## Consequences

Better: Jerome can check staging before any branch reaches prod; Solomon gets instant feedback on every push; prod URL is always a verified version.

Worse: No SSL/custom domain yet — URLs are IP:port (acceptable for internal MTIC review; a domain + Certbot can be added later without changing the pipeline logic).

Watch for: if the dashboard grows beyond a single HTML file (e.g., adds a backend or assets), switch the scp step to rsync and add a service restart.

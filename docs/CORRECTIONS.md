# MIDD — Data Corrections Queue

Data corrections reported through Ask MIDD land here automatically (feedback triage,
ADR-012). Each is applied through the ingestion pipeline, never by editing PocketBase
directly. Tick when applied.

<!-- ASKMIDD-CORRECTIONS -->
- [ ] (2026-06-23, staging) Kampala establishment count 3280 (treemap_district.json, ~47% of 7,011) likely inflated by HQ/registered-address or missing-district default in extraction; verify in extract_industries_to_records.py a — via Ask MIDD

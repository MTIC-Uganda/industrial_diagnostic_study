# Assignment: Inception Reports (Two — One Per ToR)
**Date: 27 May 2026**
**From: Jerome Nuwabaasa (MTIC)**
**To: Solomon Ariho**
**Priority: IMMEDIATE — complete before continuing chapter work**

> **Action required:** Read this document, merge this PR to confirm you have received the assignment, then start work on the inception reports.

---

## What Has Come Up

During Jerome's review of your chapter drafts, a critical gap was identified: **Chapters 2 and 3 reference an Inception Report that has not yet been written.** Specifically, your methodology chapter (Chapter 3) cites the Inception Report as the document containing the approved diagnostic framework, prioritization details, data plan, and stakeholder consultation plan — but no Inception Report exists in this repo or has been submitted to the TWG.

This is not a minor issue. The Inception Report is a formal deliverable under the Terms of Reference (Task 1). The TWG must approve it **before** chapter work is accepted as final. Your chapter drafts are good, but they are built on a foundation that doesn't yet exist on paper.

**Your immediate next task is to write the Inception Reports.**

Put all chapter work on hold until this is done.

---

## Two ToRs — Two Inception Reports

There are two separate Terms of Reference for this assignment, one per report. You must produce **one Inception Report for each ToR**:

| Inception Report | ToR | Value Chains Covered |
|---|---|---|
| **Inception Report 1** | `tor/MTIC-Diagnostic Study on Iron & Steel, Copper.docx` | Iron & Steel, Copper & Allied Metals, Automotives |
| **Inception Report 2** | `tor/MTIC-Diagnostic Study on Textiles, Garments.docx` | Textiles & Garments, Pharmaceuticals, Petrochemicals & Fertilizers, Sugar & Confectionery, Plastics & Packaging, Cement & Building Materials |

Each Inception Report is a standalone document. Each will go to the TWG for separate approval. Do not combine them into one document.

---

## What Each Inception Report Must Contain

The ToR requirements for Task 1 apply to both. Each Inception Report must address all of the following, tailored to its specific value chains:

### 1. Study Design and Workplan
- Confirm the scope: which value chains this report covers and what is being delivered
- Revised workplan with realistic timeline to the 8 June 2026 deadline
- Gantt chart showing remaining tasks, their sequence, and who is responsible

### 2. Diagnostic Framework and Assessment Templates
- The six-part analytical framework applied to each value chain chapter (value chain map → current state → binding constraints → market assessment → prioritized products → priority action matrix)
- Confirm that this framework is applied consistently across all chains in the report

### 3. Data Plan
- Primary data sources used or planned per value chain in this report
- Data gaps already identified and how they will be mitigated
- **For Inception Report 1 specifically:** note that Jerome has provided a working draft of the value chain mapping report (`data/value-chain-mapping-analysis-v3-jul2025.doc`) as the primary data source for the three Report 1 chains. This is a pre-final copy — flag it as such and note that figures will be validated against the final version when Jerome provides it.

### 4. Stakeholder Consultation Plan
- Which public sector, private sector, industry associations, financiers, and researchers have been or will be consulted for this report's value chains
- KII schedule per value chain
- Validation workshop plan (at least one structured workshop required by ToR)
- TWG reporting arrangements

### 5. Prioritization Methodology and Criteria
- The five criteria you are scoring products against: (1) accessible market size, (2) Uganda's comparative advantage, (3) feasibility, (4) job creation and income potential, (5) import substitution impact
- The proposed weights for each criterion (currently: 25%/25%/20%/15%/15%)
- **Note: Jerome needs to validate these weights with the TWG. Flag them clearly as "proposed" and note that TWG confirmation is required.**
- The scoring scale (1–5) and how the composite score will be calculated and interpreted

---

## What Happens After You Submit

1. You open **one PR** containing both inception reports (branch: `deliver/inception-reports`)
2. **You review and merge this PR yourself** — inception reports are your deliverable to confirm before submitting upstream
3. Jerome takes the merged inception reports and submits them to the TWG for formal approval
4. Once the TWG approves both, chapter work resumes with a solid approved foundation

---

## What to Do With Your Existing Chapter Drafts

Your Chapter 2, Chapter 3, and Chapter 4 drafts are strong and should not be deleted. However, **do not merge them until the relevant Inception Report is approved.** Keep their PRs open.

Once Inception Report 1 is approved by the TWG, you will need to make one update to those chapters: ensure the references to the Inception Report in Chapter 3 (sections 3.1, 3.6, and 3.7) accurately reflect what the approved Inception Report actually says.

---

## Branch and File Naming Convention for This Task

Work both inception reports on a single branch:

```
git checkout -b deliver/inception-reports
```

Files to create:
```
report/inception-report-1.md    ← Report 1: Iron & Steel, Copper, Automotives
report/inception-report-2.md    ← Report 2: Textiles + 5 other chains
```

When done, open **one PR** titled: **"Inception Reports 1 & 2 — drafts for TWG review"**

---

## Deadline for This Task

Both Inception Report drafts must be ready for Jerome's review by **29 May 2026** so the TWG can approve them before the 8 June final deadline.

# Assignment: Inception Report
**Date: 27 May 2026**
**From: Jerome Nuwabaasa (MTIC)**
**To: Solomon Ariho**
**Priority: IMMEDIATE — complete before continuing chapter work**

---

## What Has Come Up

During Jerome's review of your chapter drafts, a critical gap was identified: **Chapters 2 and 3 reference an Inception Report that has not yet been written.** Specifically, your methodology chapter (Chapter 3) cites the Inception Report as the document containing the approved diagnostic framework, prioritization details, data plan, and stakeholder consultation plan — but no Inception Report exists in this repo or has been submitted to the TWG.

This is not a minor issue. The Inception Report is a formal deliverable under the Terms of Reference (Task 1). The TWG must approve it **before** chapter work is accepted as final. Your chapter drafts are good, but they are built on a foundation that doesn't yet exist on paper.

**Your immediate next task is to write the Inception Report.**

Put all chapter work on hold until this is done.

---

## What the Inception Report Must Contain

These are the ToR requirements for Task 1. Your Inception Report must address all of them:

### 1. Study Design and Workplan
- Confirm the scope: 9 value chains across 2 reports
- Revised workplan with realistic timeline to 8 June 2026 deadline
- Gantt chart showing remaining tasks, their sequence, and who is responsible

### 2. Diagnostic Framework and Assessment Templates
- The six-part analytical framework you are applying to each value chain chapter (value chain map → current state → binding constraints → market assessment → prioritized products → priority action matrix)
- Confirm that this framework is applied consistently across all 9 chains

### 3. Data Plan
- Primary data sources used or planned per value chain
- Data gaps already identified and how they will be mitigated
- Note: Jerome has provided a working draft of the value chain mapping report (`data/value-chain-mapping-analysis-v3-jul2025.doc`) as the primary data source for Report 1 chains. This is a pre-final copy — flag it as such and note that figures will be validated against the final version when Jerome provides it.

### 4. Stakeholder Consultation Plan
- Which public sector, private sector, industry associations, financiers, and researchers have been or will be consulted
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

1. You open a PR from `assign/inception-report` (or whichever branch you use — follow the naming convention)
2. Hillary reviews for technical quality and completeness
3. Jerome reviews for alignment with MTIC expectations
4. Jerome submits it to the TWG for formal approval
5. Once the TWG approves, chapter work resumes with a solid approved foundation

---

## What to Do With Your Existing Chapter Drafts

Your Chapter 2, Chapter 3, and Chapter 4 drafts are strong and should not be deleted. However, **do not merge them until the Inception Report is approved.** Keep their PRs open.

Once the Inception Report is approved by the TWG, you will need to make one update to those chapters: ensure the references to the Inception Report in Chapter 3 (sections 3.1, 3.6, and 3.7) accurately reflect what the approved Inception Report actually says.

---

## Branch and PR Convention for This Task

```
git checkout -b deliver/inception-report
```

File to create:
```
report/inception-report.md
```

When done, open a PR titled: **"Inception Report — draft for TWG review"**

---

## Deadline for This Task

The Inception Report draft must be ready for Jerome's review by **29 May 2026** so the TWG can approve it before the 8 June final deadline.

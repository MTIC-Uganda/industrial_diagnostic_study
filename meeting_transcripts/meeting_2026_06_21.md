# Meeting: Manufacturing Industry Dashboard Redesign

**Date:** 2026-06-21  
**Participants:** Jerome Nuwabaasa (MTIC), Solomon Ariho (Developer), Hillary Arinda (Technical Lead)  
**Recorded:** Yes (audio + transcript via Tactiq)

---

## Context & Status Update

### Jerome's Current Priorities
- **Budget Deadline:** All financial year funds must be spent by June 28
- **Platform Expansion:** Working on securing ~2 billion budget for next financial year to expand platform and collect additional value chain data
- **Procurement Strategy:** Platform improvements don't require competitive bidding — same contractor (Rincol) can extend existing platform (like a building contractor completes subsequent phases)
- **Contracts:** U-TIMBER team contracts finalized; team begins July 1st

### Decision: Simplified Dashboard Focus

Jerome and the Commissioner reviewed the current dashboard and decided to **strip it down to 4 core components** only:
1. **Manufacturing Industry Overview** (4 callout statements)
2. **Manufacturing Key Indicators** (12 indicators)
3. **Progress to 10-fold Targets** (with both % and absolute figures)
4. **Manufacturing Industry Distribution** (treemaps — geographic + sectoral)

**All other visualizations should be removed** — they distract from high-level messaging needed by ministry leadership.

---

## Action Items for Solomon

### 1. Redesign Manufacturing Industry Overview Section
**Current Issue:** Header is too wordy and repetitive  
**Target State:**
- Remove: "Ministry of Trade Industry and Cooperatives", redundant text
- Keep: "Updated June 2026"
- Split header description into **4 separate callout cards** (divide the green section into 4 equal columns)
- Each card displays ONE sentence describing what the platform does
- Example sentences (can be shortened via AI):
  - Strategic platform for tracking status, performance, and growth potential
  - Real-time data on manufacturing indicators and value chains
  - Evidence-based insights for policy and investment decisions
  - Geographic and sectoral manufacturing distribution

**Why:** Short, independent statements are more readable and memorable than long prose. Politicians and commissioners won't read long text.

### 2. Implement 12 Manufacturing Key Indicators

**Layout:** 3 rows × 4 columns (12 tabs total)

**The 12 Indicators:**
1. Manufacturing value added
2. Manufacturing growth
3. Manufacturing tax contribution
4. Manufactured exports
5. High-tech exports
6. Private sector credit
7. Number of registered manufacturing establishments
8. FDI
9. Employment
10. Variety of manufactured exports
11. (2 more TBD — Jerome will clarify)

**Display Format Options** (choose per indicator):
- **Option A:** Simple tab with percentage + absolute figure
  - Example: "Manufacturing Tax Contribution: 32% | 5 trillion UGX"
- **Option B:** Comparison chart (highlight manufacturing against other sectors)
  - Example: Show manufacturing contribution alongside agriculture, services, etc.

**Critical Requirement:** Both percentage AND absolute figure must appear together
- Example: Don't just show "14.5% of GDP" → also show "7.54 billion USD"
- Why: Percentages can be misleading if base economy grows. Absolute figures show real impact.

### 3. Progress to 10-Fold Targets

**Current State:** Shows current %, NDP4 target %, and 10-fold target %  
**Problem:** Missing absolute figures for each milestone  
**Fix Required:**
- Add actual figures (USD billions) for:
  - Current state (e.g., 7.54 billion USD)
  - NDP4 target state (e.g., X billion USD)
  - 10-fold target state (e.g., 150 billion USD assuming economy grows 10x)
- Keep current color scheme (appears to be working well)

**Important Context:** When economy grows 10x, manufacturing will represent smaller % of GDP BUT larger absolute value. Both numbers matter for different audiences.

### 4. Add Manufacturing Industry Distribution Section (TreeMaps)

**Concept:** Hierarchical visualization showing manufacturing distribution across two dimensions

**Map 1: Geographic + Sectoral Distribution**
- **Root:** Total manufacturing establishments
- **Level 1:** Four regions (West, North, East, Central) — currently Uganda is organized by region, not tribal areas
- **Level 2:** Subdivide each region by sector (Chemicals, Food, Textiles, etc.)
- **Metric:** Number of establishments per sector per region
- **Interactive:** Click region → see sector breakdown; click sector → see districts

**Map 2: Sectoral Distribution** (Detail view)
- **Root:** Total establishments by sector
- **Level 1:** Major sectors (Food, Chemicals, Textiles, Plastics, etc.)
- **Level 2:** Sub-sectors within each (e.g., under Food: Bakery, Beverages, etc.)
- **Metric:** Count + size visual relative to total

**Data Organization:**
- Sectors are organized by ISIC classification (not HS code — HS code is for exports; ISIC is for manufacturing)
- Jerome will provide organized sector/subsector structure
- Current data has ~7,000 manufacturing establishments registered
- Geographic breakdown shows distribution across 146 districts (group into 4 regions for clarity)

**Why:** Politicians want to see "where are the industries" and "which sectors are strongest" without clicking into detailed data. TreeMaps provide intuitive visual hierarchy.

---

## Data Requirements from Jerome

Jerome will provide:
1. Cleaned sector/subsector definitions and hierarchy
2. Distribution dataset (establishments by sector, region, district)
3. Updated 12-indicator figures and targets

Solomon should wait for these files before implementing distribution maps.

---

## Key Principles Established

### High-Level Design Philosophy
- **Audience:** Ministry leadership (Commissioner, Minister) — they are superficial, want big numbers
- **Metric Preference:** Absolute figures over percentages (5 trillion UGX is more impressive than 32%)
- **Data Depth:** Top-level summary only; detailed analysis goes into background
- **Simplicity Rule:** If it's not in the top 4 components, remove it entirely
  - Sources stay in background (documentation, not dashboard)
  - Detailed value chain maps → internal use only
  - Geographic pins → don't matter; treemap aggregates better

### Political Reality
- Politicians don't dig deep; they communicate high-level wins
- Declining percentage can't be communicated even if absolute value grew
  - Example: Manufacturing value added % fell from 15.2% to 14.5% (other sectors grew faster), but absolute value still increased
  - Solution: Use only the positive (newer absolute figure) or hide % if it conflicts with narrative
- Every metric must be communicable as "success"

---

## Next Steps

1. **Jerome:** Provide cleaned data files (sector definitions, distribution data, updated indicators)
2. **Solomon:** Implement in order:
   - Overview section (4 callout cards)
   - 12 key indicators with proper figures
   - Progress to 10-fold with absolute values
   - Distribution treemaps
3. **Review:** Once each component is complete, Jerome will review before moving to next
4. **Timeline:** Jerome expects work to be completed by end of week (target: 2026-06-28) if Solomon "can really invest time"

---

## Notes

- Recording transcription: Audio available; transcript preferred for context
- Payment approved: Solomon to receive payment next week for prior platform work
- No other blocking issues identified
- Commission-level review already happened; these are finalized requirements


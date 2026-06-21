# Meeting: Manufacturing Industry Dashboard Redesign

**Date:** 2026-06-21  
**Participants:** Jerome Nuwabaasa (MTIC), Solomon Ariho (Developer), Hillary Arinda (Technical Lead)  
**Recording:** Audio + transcript via Tactiq

---

# TABLE OF CONTENTS
1. [ACTION ITEMS FOR SOLOMON](#action-items-for-solomon) — Read this first
2. [Full Meeting Transcript](#full-meeting-transcript) — Cleaned raw transcript for context
3. [Key Principles & Next Steps](#key-principles--next-steps)

---

# ACTION ITEMS FOR SOLOMON

## Summary: What Needs to Be Done

Jerome and the Commissioner reviewed the dashboard and decided to **keep only 4 core components**:
1. **Manufacturing Industry Overview** (4 callout statements)
2. **Manufacturing Key Indicators** (12 indicators with % + absolute figures)
3. **Progress to 10-Fold Targets** (with both % and absolute figures)
4. **Manufacturing Industry Distribution** (treemaps)

**DELETE everything else.** No sources display, no detailed maps, no clutter.

---

## ACTION 1: Redesign Manufacturing Industry Overview Section

**Current Issue:** Header is too wordy and repetitive  

**What to do:**
- Remove: "Ministry of Trade Industry and Cooperatives" (redundant)
- Keep: "Updated June 2026"
- Split header description into **4 separate callout cards** (divide the green section into 4 equal columns)
- Each card displays ONE short sentence describing what the platform does
- Example sentences (use AI to help shorten):
  - Strategic platform for tracking status, performance, and growth potential
  - Real-time data on manufacturing indicators and value chains
  - Evidence-based insights for policy and investment decisions
  - Geographic and sectoral manufacturing distribution

**Why:** Short, independent statements are readable and memorable. Politicians won't read long text.

---

## ACTION 2: Implement 12 Manufacturing Key Indicators

**Layout:** 3 rows × 4 columns (12 indicator tabs)

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
- **Option B:** Comparison chart highlighting manufacturing against other sectors
  - Example: Show manufacturing alongside agriculture, services, etc. (manufacturing highlighted)

**CRITICAL:** Both percentage AND absolute figure must appear together
- Don't show just "14.5% of GDP" → show "7.54 billion USD" as well
- Why: Percentages mislead when base economy grows. Absolute figures show real impact.

---

## ACTION 3: Progress to 10-Fold Targets

**Current State:** Shows current %, NDP4 target %, 10-fold target %  
**Missing:** Absolute figures for each milestone  

**What to add:**
- Current state: e.g., 7.54 billion USD
- NDP4 target state: e.g., X billion USD  
- 10-fold target state: e.g., 150 billion USD (assuming economy grows 10x)
- Keep current color scheme (working well)

**Important:** When economy grows 10x, manufacturing % of GDP gets smaller BUT absolute value is larger. Both matter.

---

## ACTION 4: Add Manufacturing Industry Distribution Section (TreeMaps)

**Concept:** Hierarchical visualization showing where industries are and which sectors are strongest

**Map 1: Geographic + Sectoral Distribution**
- Click region (West/North/East/Central) → see sectors within it
- Shows number of establishments per sector per region
- Regions: Uganda is now organized by geography (not tribal), so 4 regions only
- Central region will dominate the visual size

**Map 2: Sectoral Distribution** (Detail)
- Shows which sectors have most establishments
- Food, Chemicals, Textiles, Plastics, etc.
- Breaks down into sub-sectors (e.g., under Food: Bakery, Beverages, etc.)

**Data Organization:**
- Use ISIC classification (not HS code — HS is for exports)
- Total: ~7,000 manufacturing establishments
- 146 districts (group into 4 regions for clarity)
- Jerome will provide sector/subsector definitions

**Why:** Politicians want to see "where are industries" and "which sectors strongest" without clicking details. TreeMaps are intuitive.

---

## Data Needed from Jerome

Wait for Jerome to provide:
1. Cleaned sector/subsector hierarchy
2. Distribution dataset (establishments by sector, region, district)
3. Updated 12-indicator figures and targets

---

# FULL MEETING TRANSCRIPT

## Opening & Prayer

**Hillary:** I'm transcribing this call with my Tactiq AI Extension.

**Jerome:** Can you give us a prayer before we start?

**Solomon:** Thank you for today. I thank you for a brand new day. Thank you for the gift of life and health that you've given us. Thank you for the gift of wisdom and opportunities. Father, I invite you to our meeting. Let us discuss things that would take us to the next level. I pray for wisdom, knowledge, and understanding so that this discussion can go smoothly and everything we do will be to the glory of your name. In Jesus' name, amen.

**Jerome:** Amen. Okay, so I just wanted to start by giving a brief update about why I've been away.

---

## Budget & Procurement Update (Jerome)

**Jerome:** The financial year ends on June 28th. All ministry money has to be spent before that date. I'm working to ensure payments go through, including for this project and other ministry projects.

**Solomon:** So you're making the money spent so it's returned?

**Jerome:** No, coin is returned, precisely. There are other things in the ministry that I'm supporting to get payments. But this one is included to make sure the payment happens.

**Solomon:** Will you be needing screen sharing?

**Jerome:** Yes, I will share my screen when explaining certain things I want to work on.

---

## Platform Expansion & Budget Planning

**Jerome:** It's quite hectic dealing with accounts, procurement offices. But the other thing is we have a huge budget for next year. When I showed this to the Commissioner, he said we need to expand the platform to cover other value chains.

He said there's a way we need to do it so that we can single source when we go for procurement. If you've built a platform and are expanding it, you don't need competitive bidding. The same people who did the first phase should do the next phase because you don't want a third party interfering. It's like buildings — if you've completed two floors, the same contractor completes the rest.

We might be doing a procurement of about two billion next financial year. This includes money for data collection, not just development. I had to do administrative things to put money somewhere ahead of time so when procurement happens, it's there.

Beginning yesterday, I started restructuring the dashboard overview. Then Solomon and I will work section by section. My expectation is that by end of this week, everything should be done if Solomon can really invest time.

The other thing I was working on was finalizing U-TIMBER team contracts. The permanent secretary is away until June 28th, but when she returns, contracts begin July 1st. So Hillary, you'll be contracted and we'll be ready to go.

**Solomon:** Are you done with accounting and procurement things?

**Jerome:** I've done the heavy work. Now it's following up. Also, the money includes payment for work you did on the company. That's been approved, so next week you should receive payment.

**Solomon:** Hallelujah.

---

## Dashboard Design Requirements

### Overview Section

**Jerome:** I've called it "The Manufacturing Industry Dashboard." You see below that "Ministry of Trading Industry and Cooperatives." I would say remove the "UNIDO Programme for Country Partnership" — maybe leave the "Updated June 2026" because that's interesting to see the latest update.

I didn't need "Manufacturing Industry Dashboard" to be repeated. "Manufacturing Industry Dashboard — Ministry of Trading Industry and Cooperatives" — the repetition should be removed.

There are interesting sentences that I want in separate tabs. This does four things, but generally it's: a strategic platform for tracking status, performance, and growth potential of Uganda's manufacturing industry.

Imagine you divide the green section into 4 equal columns. Put one sentence in each so that each can be read independently. When sentences are long, people don't read. When they're short, they will. I'll send you the actual text, but you can split it and even ask AI to help shorten them.

### Manufacturing Key Indicators

**Jerome:** Then we move to the manufacturing indicators. I put 12 of them — these are the 12 major indicators. I like the way these tabs are done.

I did 12 because we could do three layers of 4 or two layers of 6, but three layers of 4 looks better. You provide the slots and we'll work out the figures indicator by indicator because there are different data sources — Bank of Uganda, URA, and others.

The 12 are: manufacturing value added, growth, tax contribution, exports, high-tech exports, private sector credit, number of establishments, FDI, employment, variety of manufactured exports, and a couple more.

For each indicator, you decide how to present it. Example: Manufacturing tax contribution — you can either show just the percentage and figure (32% | 5 trillion), or show it compared to other sectors with manufacturing highlighted.

Sometimes showing comparison is better because then people appreciate how big it is. If I say Solomon is rich with a billion shillings, okay. But if I say Solomon is rich with a billion shillings and he's one of three people in Kampala with that kind of money, then you appreciate how big he is.

### Progress to 10-Fold

**Jerome:** Now we have the description, then progress to 10-fold. This is the only one done the way instructed. The issue is it shows percentages but not figures. It needs BOTH for context.

Right now, manufacturing value added is 14.5% of GDP. But what's the actual figure? Our economy is about 52 billion USD. So 14.5% of 52 billion is 7.54 billion USD. That's the current manufacturing value added.

If we reach 30% by 10-fold, that's not 15.6 billion (30% of 52B). By then we expect the economy to have grown 10x. So 30% of 500 billion equals 150 billion USD.

The figures are very important. Just showing percentages doesn't communicate properly.

---

## Manufacturing Distribution (TreeMaps)

**Jerome:** I have data about manufacturing industries we've registered. They're organized by sectors and subsectors.

This is a tree map visualization. When you try to analyze all countries, it becomes too much. So they organized by continent. You click a continent and see just that continent. Much clearer.

Now I have data organized by sectors. We need to organize it by subsectors so that clicking shows the breakdown. Under chemicals and products, you have fertilizers, pesticides, etc.

You need a map like this. The products are organized by HS code, but when manufacturing you use ISIC instead. What matters is we have the actual products within subsectors within sectors.

If I click foodstuffs, it shows I export 8,203 million of foodstuff, then breaks down to cocoa beans, raw sugar, etc. That's the kind of visualization you'd do — for us it's the number of establishments. Maybe it shows 7,000 total establishments. Click chemicals and it shows 300 establishments. Click inside and it breaks down: 20 in paints, 59 in pesticides, etc.

One is geographical. Uganda initially had 14 regions but changed to 4 regions — West, North, East, Central. It's a deliberate move to unite Ugandans by geography instead of tribe.

You'll break down by the 4 regions. Central will take a huge chunk. Then within each region break down to districts. Uganda has 146 districts now, which would be too many to show, so group by region first.

So I'll have two maps. One shows sectoral distribution — which sector has more, less, etc. You call it the Manufacturing Industry Distribution.

---

## Final Summary

**Jerome:** I expect four things on the overview: the green section divided into 4 (what this does), the key indicators, the progress to 10-fold, then distribution. That's it.

Everything else, just drop it. Sources stay in background. There's no need to display them. The Commissioner reviewed this and said this one is not communicating. Just focus on those four. Once it's okay, we can move to the next thing.

If you observe those four really well, that's all the ministers and commissioners want. High-level information. They don't want deep details. Once they have high-level info, the rest is internal for our analysis.

They'll look at the overview and location. They're not interested in deep details. If you deal with politicians, you'll understand — they're superficial. They never dig deep. A politician will present Solomon as a candidate because he has a beard and is well-built. That's it. No discussion of skills.

They love big high-level numbers they can talk about. If you say manufacturing is 14.5% of GDP but also 7.1 billion USD, they won't talk about 14% because it seems small. They'll say 7.1 billion USD because it sounds like a success.

An interesting example: manufacturing contribution to GDP dropped from 15.2% to 14.5%. But the absolute number actually increased. The Commissioner said, "Don't communicate the drop. Use the older figure or the absolute figure." He said, "I cannot explain to Ugandans those complicated stories. I need to communicate that we've performed." So that's the political reality.

---

## Next Steps

**Jerome:** I'll make improvements to the data and files, then drop them for Solomon to upload to the same folder we've been using.

**Solomon:** Okay.

**Jerome:** Okay, thank you guys.

**Hillary:** I'll communicate where I put this and you'll pick it from there.

**Solomon:** All right, thank you.

**Hillary:** Okay guys, bye.

---

# KEY PRINCIPLES & NEXT STEPS

## High-Level Design Philosophy

- **Audience:** Ministry leadership (superficial, want big numbers)
- **Metric Preference:** Absolute figures over percentages  
  - Example: "5 trillion UGX" is more impressive than "32%"
- **Data Depth:** Top-level summary only; detailed analysis stays internal
- **Simplicity Rule:** If it's not in the top 4 components, DELETE IT
  - Sources → background (documentation only)
  - Value chain details → internal use only
  - Geographic pins → don't matter; treemap is better

## Political Reality

- Politicians communicate high-level wins, not deep analysis
- Declining percentage can't be communicated even if absolute value grew
  - Example: Manufacturing % fell 15.2% → 14.5% (other sectors grew faster), but absolute value still increased
  - Solution: Use positive figures or hide declining %
- Every metric must sound like success

## Timeline & Responsibilities

1. **Jerome:** Provide cleaned data files (sector definitions, distribution data, updated 12-indicator figures)
2. **Solomon:** Implement in order:
   - Overview (4 callout cards)
   - 12 key indicators with both % and absolute figures
   - Progress to 10-fold with USD values
   - Distribution treemaps
3. **Review:** Jerome reviews each component before moving to next
4. **Deadline:** End of week (by June 28) — if Solomon invests time

## Notes

- Recording available; transcript preferred for context
- Solomon: Payment approved for prior work — coming next week
- No other blockers
- Requirements finalized at Commission level


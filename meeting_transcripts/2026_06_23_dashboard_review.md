# Meeting: Manufacturing Industry Dashboard Review (Component by Component)

**Date:** 2026-06-23
**Participants:** Jerome Nuwabaasa (MTIC), Solomon Ariho (Developer), Hillary Arinda (Technical Lead)
**Recording:** Audio + transcript via Tactiq
**Context:** Follow up to the 2026-06-21 redesign meeting. Solomon had implemented the 4 core components. Jerome reviewed the live dashboard on screen share and gave detailed corrections section by section. The distribution treemaps were broken on production during the meeting; that rendering bug was fixed before the call ended.

---

# TABLE OF CONTENTS
1. [Summary](#summary)
2. [Action Items for Solomon](#action-items-for-solomon) — Read this first
3. [Action Items for Jerome](#action-items-for-jerome)
4. [Action Items for Hillary](#action-items-for-hillary)
5. [Full Meeting Transcript (Cleaned)](#full-meeting-transcript-cleaned)
6. [Key Principles and Decisions](#key-principles-and-decisions)

---

# SUMMARY

Jerome went through the dashboard live, component by component. The overall direction is approved and he is excited about it, especially the distribution treemaps which he says will "cut the pocket of the commissioner." The work now is refinement of each indicator plus one significant architecture correction.

What was approved as is:
- The green Manufacturing Industry Overview header. Jerome is happy to submit it looking exactly as it is.
- Progress to 10-Fold layout (both figure and percentage present). One enhancement requested: a toggle to switch the view between percentages only and figures only.
- The region treemap colour scheme (one primary colour per region, districts as shades of it). Jerome questioned it, then accepted it.

The main themes of the corrections:
1. Replace gauges, sliders and small graphs inside the 12 key indicators with donut or pie circles. The visual should demonstrate the percentage as a slice of a whole.
2. Every indicator must show its year and its source (UBOS, URA, Bank of Uganda, TradeMap).
3. Every indicator must show both the absolute figure and the percentage.
4. Fix the distribution treemaps: tooltip wording, legend completeness, tooltip going off screen, and the breadcrumb getting stuck after drilling in via the legend.
5. Architecture: data is currently hard coded into the repo. Jerome wants it to flow through a central database (PocketBase) instead. This instruction was given earlier but was missed.

Deadline pressure: the ministry financial year ends 2026-06-28, so the dashboard should be in a submittable state by then.

---

# ACTION ITEMS FOR SOLOMON

## A. Manufacturing Key Indicators (the 12 cards)

General rules that apply to every indicator card:
- The section header should read "current status" and must NOT include the year in the header.
- Each individual indicator picks the latest available figure (some indicators have a more recent year than others; that is fine, keep them).
- Each indicator must display: the year that figure is for, and the source of that figure.
- Each indicator must show both the absolute figure and the percentage, with the percentage bold enough to read.

Per indicator:

1. Manufacturing Value Added
   - Remove the graph. This is a figure indicator.
   - Use a full circle (donut or pie) showing manufacturing as a slice of total GDP. The whole circle is GDP, the slice is manufacturing.
   - Show the value (example 8.1 billion) and the percentage of GDP (14.5%, bold).
   - Do not display the total GDP number; just say it is 14.5% of GDP.
   - Add the year and the source. Expected source: UBOS.

2. Manufacturing Growth
   - Remove the graph.
   - This is a year on year comparison (how much manufacturing grew this year versus the previous year, as a percentage).
   - Show the figure plus a simple icon that signals growth. No graph.
   - Add the year and the source. Expected source: UBOS.

3. Manufacturing Tax Contribution
   - Jerome likes the current treatment. One change: move the circle (donut) ABOVE and move the key or legend BELOW the circle.
   - Display in Uganda Shillings (we are taxed in UGX even though GDP is assessed in dollars).
   - Add the year and the source. Source: URA (their published reports; if the agent searches the web it should find the URA report).

4. Manufactured Exports
   - Source: TradeMap.
   - Do not break it down by sector. Just show the single figure.
   - Add a shipping or export icon.
   - Show two values: the absolute figure (example 2.4 billion) and the percentage of total exports.
   - Note on classification: raw coffee is NOT a manufactured export, but soluble or processed coffee IS. Raw cotton is not; cotton turned into yarn or fabric is. Claude should be able to identify which HS codes are manufactured exports; if not, use the HS code descriptions. Verify the 2.4 billion figure.

5. High-Tech Exports
   - Done well. Same layout fix as tax contribution: move the circle up, move the legend down. This puts everything on one line rather than wrapping to a second line.
   - Definition: degree of value addition. Pharmaceuticals, phones, computers, electronics, cars, etc. These are the things used to measure how far a country is industrialising.
   - Show the figure (example 85 million USD) and the percentage of manufactured exports (example 3.5%).
   - Do not put the manufactured exports total in brackets. Say "3.5% of manufactured exports, 85 million USD." Do not restate that manufactured exports are 2.4 billion; that is already known.

6. Private Sector Credit
   - Use a donut too, for uniformity with the others.
   - Hillary suggested rendering two versions (donut version and slider version) so Jerome can compare and pick the better one at the end. Optional but welcome since the agent does the heavy work.
   - Put the source at the bottom.

7. Registered Manufacturing Establishments
   - Put the industry icon on top and the figure below. Centered. This one is a single figure, so centered is fine.

8. Establishments in Industrial Parks
   - Value is 166.
   - Use a circle with a pie. Say "2.4% of registered establishments." Do NOT write "2.4% of 7,011 registered establishments"; just "2.4% of registered establishments" is enough.
   - Find a better icon for industrial park. Actually, once the pie is added the icon is not needed.

9. FDI (Foreign Direct Investment)
   - Find a better icon. Then use the pie again (do another pie for FDI). A pie does not need a legend; it is self explanatory.
   - Make sure the figure and the percentage are present. Use a different colour for the smaller slice.

10. Manufacturing Employment
    - Do away with the gauge. Use the pie.

11. Distinct HS6 Manufactured Product Categories Exported
    - This indicator is currently not good. The gauge does not communicate it well.
    - What it should measure: variety of manufacturing. Globally, how many manufactured product categories (by HS code) are traded (around 5,000), and how many of those does Uganda export (around 380). This shows whether Uganda is increasing its variety of manufactured products, not just quantity.
    - Critical correction: confirm the 380 are MANUFACTURED product categories, not general product categories. Raw coffee must not be counted. The global denominator (around 5,000) must also be MANUFACTURED categories only, not all product categories.
    - Give Claude a proper prompt to extract this from TradeMap for the latest year. This was already addressed in the 10-fold growth and NDP4 measure documents.

## B. Progress to 10-Fold

- The layout is liked (both figure and percentage present, current colour scheme kept).
- Add a toggle or two tabs so the viewer can switch between viewing in percentages only and viewing in figures only. Solomon proposed one tab for percentage and one tab for figure; Jerome agreed.
- Reason: the scale looks completely different between the two views. Example: we are at 14.5% of GDP against a 30% target, so in percentage terms the bar is nearly halfway. But in absolute terms we are at roughly 7.7 billion against a target near 250 billion, so the bar is tiny. Both truths matter.
- The actual figures and projections will be interrogated later, one by one. The design is approved for now.

## C. Manufacturing Industry Distribution (the two treemaps)

The treemaps are the part Jerome is most excited about. The rendering bug was fixed during the meeting. Remaining fixes:

1. Tooltip wording: remove "of this view." The tooltip currently says something like "74% of this view." Just show the percentage (example "20.7%"). The phrase "of this view" reads as strange even though it is technically correct (it is the percentage within the drilled in context, for example within bakery products).

2. Legend completeness: every item in the treemap should appear in the legend. Right now only some appear (around 16 shown, but there can be around 20). Solution: reduce the legend font size so all of them fit. Do NOT expand the card downward and do NOT shrink the treemap or the card to make room. Reduce the font, keep the card a fixed shape.

3. Tooltip off screen: when hovering near the edge, the tooltip shows outside the viewport so it cannot be read. Keep the tooltip inside the viewport.

4. Breadcrumb stuck after legend drill in: when you drill into a district via the legend (example Gomba) and then click back, it stays on Gomba instead of returning to all regions. Fix the back navigation so it resets to the top view.

5. District labels: some district boxes are so tiny the name and number cannot be shown. The intent is to show the district name and the number, ideally on hover. Fix so the small boxes still communicate their district and count.

6. Region colours: accepted as is. Each region uses one primary colour and its districts are shades of that colour. The sector treemap uses distinct colours at the top level. This is fine, no change.

## D. Architecture: route data through the database, not the repo

- The dashboard data (the establishment register and the indicator matrix) is currently hard coded into the repo. Jerome's earlier instruction was that data should be pulled from the source document into a central database, and the dashboard should read from that database, not directly from the hard coded values.
- Action: move the data ingestion so the source document (PDF or report) is mined by Claude into PocketBase, and the dashboard reads from PocketBase. Keep using PocketBase (decision below).
- The establishment register is not the only future source of establishment data, so there must be one central, continuously editable source that everything reads from.
- The treemap data and the indicator matrix should both eventually flow through PocketBase rather than living directly in the repo.
- Retrospective requested: Solomon's agent should determine where the earlier instruction was missed (was Jerome's PR instruction not read, or missed) and how to close that gap so future data requests automatically follow the database architecture. The whole point of the pipeline is to remove human dependency; the missed instruction shows dependency still exists somewhere.

---

# ACTION ITEMS FOR JEROME

1. Provide the source and year for each of the 12 indicators where not already obvious, so Solomon can label them (UBOS for value added and growth, URA for tax contribution, TradeMap for exports, etc.).
2. Confirm the manufactured exports figure (around 2.4 billion) and confirm the high-tech exports figure (around 85 million USD).
3. Clarify, for the distinct product categories indicator, that the counts (around 380 for Uganda, around 5,000 global) are restricted to manufactured categories.
4. Upload the source document into PocketBase (rather than dropping it only in the repo folder), so the data flows through the central database as intended. Credentials were already sent on WhatsApp (group and direct).
5. Provide any updated indicator figures and projection targets for the interrogation pass that will follow the design approval.

---

# ACTION ITEMS FOR HILLARY

1. Investigate and fix PocketBase. The seed or sync job is failing and the pipeline broke during the meeting. Find out what is wrong with PocketBase quickly so the team can rely on it. (This is the separate seed job failure, not the treemap bug which is already fixed.)
2. Review why the architecture instruction was missed: trace where in the flow Jerome's instruction to route data through the database got lost, and design how to close the gap so future requests always pass through the correct architecture.
3. Run the whole pipeline again end to end to make sure there are no further surprises after the treemap fix.
4. Re-examine how the source document was stored. It was put on the repo directly; redesign so this kind of data is stored properly through PocketBase.
5. Confirm PocketBase credentials work, then notify Jerome when it is ready for him to upload documents himself.

---

# FULL MEETING TRANSCRIPT (CLEANED)

## Opening (before quorum) and prayer

While waiting for Solomon to join, Jerome and Hillary discussed delegation and building structure: that a leader should direct and supervise rather than do all the physical work himself, because if everything depends on one person, nothing moves when that person is away. Jerome noted Solomon seemed preoccupied with other work.

Once Solomon connected, Jerome opened with prayer, thanking God for bringing them together again, for wisdom and encouragement, and asking for continued guidance to do the right things for their families and their country.

## Going through the dashboard

**Jerome:** Let me go straight to the dashboard Solomon worked on. At one point I saw the improvement, then it disappeared, which is when I tried to call you; then it came back. I also did something and pushed it, I am not sure it reached you. The page is getting much better. What is in the green is perfect as it is; I am happy to submit with it looking like this.

### Manufacturing Key Indicators

**Jerome:** When you go to the manufacturing key indicators, the header should say current status, but it should not say the year, because we agreed that for each indicator you take the latest available figure. Some have a more recent year, some are older; we still keep them. Let us go one by one.

**Manufacturing Value Added.** Right now it says 8.1 billion, 14.5% of total GDP. For which year is this? We should know.

**Solomon:** The graph?

**Jerome:** No, remove the graph for this one. It needs to be a figure. The slider just shows that it is 14.5%. I would rather have a full circle, a pie, where the whole is GDP and the slice that manufacturing covers is shown. GDP is about 55.9 billion. I want the manufacturing value added, which is 8.1 billion, and what percentage of GDP it is. You do not need to put the total GDP; just put that it is 14.5% of GDP, bold enough. The visual is to demonstrate what 14.5% looks like as a slice. I also need to know which year that is and the source. For manufacturing value added I expect the source to be UBOS.

**Manufacturing Growth.** I see you did a graph. Manufacturing growth is for a given year; it is the comparison between this year and the previous year, the percentage by which manufacturing grew. Just put the figure and an icon that demonstrates growth; do not put a graph. These are exact figures. The source is also expected to be UBOS.

**Manufacturing Tax Contribution.** I like what you did here, but I would prefer the circle is above and the key is below the circle. The contribution should be in Uganda Shillings, because we are taxed in shillings even though we assess GDP in dollars. The source is URA; they issue the reports. If you ask the agent to go through the web it should find that report.

**Manufactured Exports.** This should come from TradeMap. You tried to show the different sectors; I would just put the figure of manufactured exports. Put a shipping icon to demonstrate exports. You need two figures: the absolute figure (say it is around 2.4 billion) and what percentage of total exports it is. Note: coffee is not a manufacturing export, but soluble coffee is a manufactured export. If you send out raw cotton it is raw, but cotton turned into yarn or fabric is a manufactured export. The agent should know which HS codes are manufactured exports; if not, there is a description. It is giving 2.4 billion, which looks like the actual figure, but we can verify.

**High-Tech Exports.** This was done well. The only change: move the circle up and move the key down, the same as on tax contribution, so it all sits on one line instead of wrapping. High-tech exports are about degree of value addition: pharmaceuticals, phones, computers, electronics, cars. The input is more technology and less raw material. These are the things used to measure to what extent a country is industrialising. Show that it is, for example, 3.5% of manufactured exports. You do not need to put the 2.5 billion in brackets. Just say it is 3.5% of manufactured exports and that the figure is 85 million US Dollars. Do not restate that manufactured exports are 2.4 billion; I already know that.

**Private Sector Credit.** To be frank I do not know, it may be monotonous, but I would also like a donut there for uniformity.

**Hillary:** He can render two versions, then share, and we choose the better one at the end. Since Claude does the hard work, it is not too much to do both and see which is better.

**Jerome:** Okay. For each one, remember to put the source at the bottom.

**Registered Manufacturing Establishments.** Put the industry icon on top and the figure below, centered, not on the side. This one is just a single figure; centered is fine.

**Distribution by Region (within indicators).** Quite frankly I did not want a donut here. I would prefer the tree map, the box subdivided by percentages with different colours. Limit it to the four regions, because the detailed treemap is below. Add the hover focus effect once the data is in. This small one is just visual; it does not need the popup.

**Establishments in Industrial Parks.** 166. Do a circle with a pie, the same as before. Just say 2.4% of registered establishments. Do not say of 7,011 registered establishments; 2.4% of registered establishments is enough. Find a better icon for the industrial park; actually, once you put the pie you will not need the icon.

**FDI.** Can you find a better icon for FDI? You will not need a map; use the pie again. Do another pie for FDI. A pie does not need a legend; it is self explanatory. Make sure the figures and percentage are there, and use a different colour for the smaller slice.

**Manufacturing Employment.** Do away with the gauge and do the pie.

**Distinct HS6 Product Categories Exported.** This one is not a good indicator as it is, and the gauge does not speak well. Let me explain what we are interested in. Globally, how many manufactured products by HS code are traded; you may find there are around 5,000. We need to check whether these are manufactured products or just product categories, because the label only says distinct product categories without clarifying they are manufactured. So please ask the agent to confirm that the 380 are manufactured product categories, not general products. Raw coffee should not be among these. And the global total of around 5,000 should also be manufactured product categories, not any product.

The reason: if a country exports many different products it shows variety, but for manufacturing I only care about the variety of manufactured products. Pure bred breeding horses, HS code 0121, is a product category but not manufactured; the manufactured products usually start at later HS codes. I want to compare how many distinct manufactured product categories are exported globally versus how many Uganda exports, so I can see where Uganda sits. China produces and exports around 80% of all categories of manufactured products. I need to increase variety, not just quantity, but only in manufacturing. I should not celebrate increasing variety by exporting more raw crops or raw minerals; that would be performance in agriculture or mining, not manufacturing. The more different varieties of manufactured products, the better my performance. This was addressed in the measure documents, and with a proper prompt Claude should extract it from TradeMap for the latest year.

### Progress to 10-Fold

**Jerome:** I like what you have done; you provided both the figure and the percentage. Now I realise it is better to have a slider or a double rendering so I can see it in percentages only or in figures only. In figures the blue, green and red buttons would sit very differently.

Let me explain. Right now we are 14.5% of GDP and the 2040 target is 30% of GDP, so in percentage terms we are close to halfway; the blue bar is almost halfway. But in figures we are at about 7.7 billion and by 2040 we should be at about 250 billion, so in absolute terms we are way off. The blue would be tiny, then a very big green and a very big orange.

**Solomon:** So one tab for selecting percentage and another tab for selecting figure.

**Jerome:** Yes, you should be able to switch between viewing by percentages and viewing by figures. Otherwise all the indicators are okay. We will interrogate the actual figures later; the design is okay. This section uses the same figures but does projections based on the 10-fold growth and NDP4 documents, and we can interrogate those one by one to get the right projections.

### Manufacturing Industry Distribution (treemaps)

**Jerome:** Finally, the manufacturing industry distribution. I kept clicking looking for this, because this is the one I really wanted, the one to impress the commissioner. But there is nothing showing.

(Solomon reports it works very well on his local and should be on production too. The team troubleshoots: the data is present in the deployed file, the region data appeared missing while the sector data rendered, but on checking the variable names and container IDs the data and JavaScript were actually present. It was a rendering bug, not missing data. Hillary diagnoses it live, the CI keeps failing on deploy, and the team decides to bypass CI and copy the fixed file to the server directly. After the fix the treemaps render. A separate PocketBase seed job is noted as failing on its own, to be looked at later.)

**Hillary:** The data is actually there, it is just not being rendered. It is a rendering issue, it should be an easy fix. The pocket base job failed separately; we will deal with that. Let us first get the treemap working on main.

(After the fix renders, Jerome interacts with the treemaps and gives feedback.)

**Jerome:** You did well on the tree map. But why does it say 1.7%, or 74% of this view, when I hover?

**Solomon:** On a region like Central, among regions it is a certain percentage of this view, and when I click inside, it recalculates within that region.

**Jerome:** I see. If you click bakery products, on the spatial side it shows the spatial distribution of only the bakery products. So it is telling you 74% not of all industries but of this particular view, this particular product. When you click bakery products it shows Central 299, and 299 is 74% of the bakery products, not of all industries.

**Hillary:** Of this view sounds strange.

**Jerome:** You are right, it should not say of this view. Just say 74%. The people using this for analysis are fairly smart; they will put it together.

**Jerome:** One more thing. This is all products: food, beverages, and so on. How come what I see on the treemap is more than what is in the key? For example I do not have paper products in the key.

**Hillary:** Not everything on the treemap is in the legend; it shows the top ones.

**Jerome:** Ideally if you are going to have a legend, the legend must have all of them, even if in smaller letters.

**Hillary:** There could be around 20. Do you want all 20 listed? Should the tile expand downward dynamically?

**Jerome:** No, the easier solution is to make the legend font smaller so all of them fit.

**Hillary:** But it should not shrink the treemap to fit the legend.

**Jerome:** It should not shrink the treemap, and it should not shrink the card either, because the card is designed so you see everything without scrolling or zooming. Reduce the font and put all of them there.

Also, when you hover, the tooltip is showing off to the side, outside the viewport, so you cannot see it. That should be fixed so it stays inside the view.

**Jerome:** On the region treemap, why did it use the same colour in different shades instead of different colours, like the sector treemap does at the top level? Oh, I see why: each region uses one primary colour and the districts are shades of it. Okay, that is fine, perfectly okay.

**Jerome:** One more issue: if I drill into a district using the legend, for example Gomba, and then go back, it stays stuck on Gomba instead of returning to all regions. That should reset.

**Solomon:** That part I am going to fix, because the small district boxes are so tiny; it is supposed to bring the district name and the number, ideally on hover.

### Architecture and pipeline discussion

**Hillary:** There is a bigger issue in terms of architecture now.

(Discussion of how the data reached the dashboard.)

**Jerome:** Earlier I gave an instruction. The data being displayed comes from a PDF, and I instructed that it should first be pulled from the PDF into a database, and the dashboard should read from the database, not directly hard coded from the PDF. I think Solomon may have instructed it to be hard coded directly, so there may have been a conflict. When I checked, the database step had not been done.

**Hillary:** So how was the document uploaded? Did you use PocketBase or did you put it on main directly?

**Jerome:** I put the document in the folder where we normally put it, then gave the instruction that it should not pick data directly from the PDF; it should first put it in a database.

**Hillary (to Solomon):** When Jerome sent you something, did you read his PR? His instructions were likely in the PR, or the agent missed it. The big thing is it messed up, so we need to know where the flow broke.

**Jerome:** My thinking is there should be a central database where all this information comes from. For the entire platform, information about industrial establishments should come from one central database. I instructed it to extract the establishment information and put it in that database, so that any new edits or adjustments happen to that central source. This register will not be the only source of establishments; there should be one central source that is continuously edited and improved.

**Hillary:** Okay, so instead of leaving it on the repo, we route it through the database. Solomon, the matrix data is currently on the repo directly, which is fine for now, but it should go through PocketBase, because we already set up PocketBase.

**Jerome:** What is PocketBase?

**Hillary:** It is an open source project for exactly what you are describing. It lets you upload data in different forms, CSV, PDF, anything, and acts as a repository. It was meant to save us building this from scratch, since it already does what you are asking. You could have uploaded the document into PocketBase.

**Jerome:** Then I could have done that. Let us use PocketBase; I will figure it out.

**Hillary:** The credentials were sent on your WhatsApp, also on the group. It should work. There is something wrong with PocketBase that I need to find out quickly, so hold off using it until I confirm.

**Jerome:** This matrix, then, is not coming from PocketBase?

**Hillary:** No, because you put it on the repo directly, so it is on the repo, which is fine for now. With time it will improve.

**Jerome:** Okay, this is good enough.

**Hillary:** Solomon, the point is that your agent should pick this up: every time a request comes from anywhere, what should it do in terms of architecture, since we already have a defined flow. I want to know how the instruction was missed, where the gaps were, and how to close them, because the whole point of this loop is to remove dependency, and there is still dependency somewhere, which is a problem. The agent should find out where the gap was and how we could have closed it better.

## Closing

**Hillary:** I will post this record like last time, and Solomon can take it up from there. On my side I will look at PocketBase and the pipeline.

**Jerome:** The data will be used beyond TradeMap; we will use it for industry locations and other analysis, so it should be stored well. I think we may need to redesign how this is stored.

**Jerome:** Thank you guys.

**Hillary:** I will post the minutes in five to ten minutes. Okay, bye.

(Side note from the call: Solomon has a payment coming through this week for prior work.)

---

# KEY PRINCIPLES AND DECISIONS

## Design philosophy (carried from 2026-06-21, reaffirmed)
- Audience is ministry leadership; they want big, clear numbers, not deep detail.
- Always show the absolute figure alongside the percentage. Figures communicate success better than percentages.
- Keep only the four core components; everything else stays in the background.

## Visual standard set in this meeting
- Inside the 12 key indicators, prefer a donut or pie circle that shows the percentage as a slice of a whole. Remove gauges, sliders and small graphs.
- For circle indicators, the circle sits above and the legend or key sits below.
- A pie that shows a single share does not need a legend; it is self explanatory.
- Every indicator must carry its year and its source.

## Decisions
- DECISION: Keep using PocketBase as the central database. Jerome will figure out uploading documents into it once Hillary confirms it is working.
- DECISION: Data must flow source document to PocketBase to dashboard. No more hard coding data into the repo. (Indicator matrix currently hard coded is accepted as good enough for now, to be migrated.)
- DECISION: Progress to 10-Fold gets a percentage view and a figures view toggle.
- DECISION: Region treemap colour scheme (one colour per region, shades for districts) is accepted as final.
- APPROVED AS IS: green overview header; Progress to 10-Fold layout; high-tech exports treatment (after the move up or down layout fix).

## Timeline
- Ministry financial year ends 2026-06-28. The dashboard should be in a submittable state by then.

## Open technical items
- PocketBase seed or sync job failing (Hillary investigating). Separate from the treemap rendering bug, which was fixed during the meeting.
- Retrospective on why the database routing instruction was missed by the agent, and how to close the gap.

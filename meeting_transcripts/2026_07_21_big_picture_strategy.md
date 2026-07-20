# MIDD Strategy and Big-Picture Meeting, 2026-07-21

Present: Jerome Nuwabaasa, Solomon Ariho, Hillary Arinda.

This was a direction-setting call, not a routine progress review. Jerome opened it because a funding and partnership opportunity has appeared that changes what "done" means for the next few weeks. Everything below should be read against that backdrop: we are now building toward a specific high-stakes demonstration, and the whole team needs the bigger picture in mind so the small work lines up with it.

## 1. The strategic driver: a high-stakes demonstration

A senior, well-placed economist has seen the platform and is impressed with what it already does, gaps and all, especially its analytics. On the strength of that, a demonstration is being arranged to a senior economist audience at a key ministry, and it could open a multi-year, continuously-improving engagement.

What matters for us: this is not a request for a finished system. It is a request for something impressive enough to say credibly, this is what we are building, here is one value chain done properly, and we will replicate it across all the others. One fully-worked value chain is enough to make the case. Momentum over the next week or two matters because the demonstration could land soon.

(Commercial and financial terms are handled off-repo and are deliberately not recorded here.)

## 2. What the audience actually wants: precision, not breadth

The Permanent Secretary is a career economist and researcher. What persuades him is logic that adds up end to end, and precision over generality.

- A decision must trace to a specific gap. If we want to grow value addition in iron and steel, and the data shows a shortage of mechanical engineers, then funding a specific engineering course becomes an obvious, defensible decision. What he dislikes is the vague version ("we need engineers") with no line to an outcome.
- Poverty is the cancer of the economy. The job of the platform is to point to the exact cancer cells: not "put money in iron and steel," but exactly where inside the sector the money should go.
- The three things that decide competitiveness everywhere are Inputs, Technology, and Professionals. Everything else is broadly similar across countries. (Jerome's example: iPhones are made in China because of the professionals, not the technology or the labour cost.) The platform must let a decision-maker see, per product, where we stand on each of these three.
- Traceability toward the target must run everywhere. When you open an input such as cold rolled coil, it should show current capacity against the capacity we would need at the target state, so the gap is visible and comparable.

## 3. The near-term deliverable: Iron and Steel, done all the way

Decision: focus on the Iron and Steel value chain and complete it fully before touching the others. Methodical, one thing closed at a time. Jerome's framing: five percent of a site that works completely beats one hundred percent that is trash. Once one chain is done properly, the rest are fast to replicate.

Cadence: short check-in calls every evening this week to hold momentum, because the demo could land in one to two weeks.

Concrete product work Jerome asked for, all scoped to Iron and Steel first:

- Map: clicking a product should open its dropdown with the information populated, fetched live. Where information is missing, make it fetch.
- Local-capacity signal: the map and Explorer should clearly show where local capacity exists and where it is a gap. Fetch so every available capacity is captured, and where it is absent, that absence is what gets shown.
- Explorer inputs: move the input detail from hover to click. A click should open a side panel that the user can then close. Officials want to click, look, and move on; hover proved awkward when Jerome demonstrated it.
- Colour coding: use a traffic-light scale (red, orange, green), possibly extended up to five levels since three can be too narrow, applied to the bullet or dot rather than the text. Red means Uganda cannot produce the item and must build capacity. Surface the worst first, because a decision-maker starts from where we are doing badly, not where we are fine.
- Weighting by essentiality and scarcity: not every gap carries equal weight. Treat it like risk, which is impact times probability. An input that is both essential and unavailable domestically (for example cold rolled coil) is high priority and red. An input that is scarce but non-essential and easily imported (for example flux acids) carries less weight. The knife-versus-plates analogy: one knife near a child outweighs a hundred plates. Ask the AI to help derive this analysis.
- Product-as-input consistency: cold rolled coil appears both as a final product and as an input, on the same HS code and the same sheet. When it is an input it should carry the same trade data it carries as a product, since the data is keyed by HS code. Today the input view does not bring that information; it should. Sources need not be repeated on the input side.
- Genuine process utilities: where an item truly has no trade data because it is a process utility (steam, water, energy), the pop-up should still appear and explain what the item is and why it has no data, rather than showing nothing. Solomon and Jerome differ slightly here: Solomon treats cold rolled coil as a process item without its own data, Jerome insists it is a product-that-is-also-an-input and must carry its HS-coded data. Resolution: cold rolled coil carries its data; true utilities get an explanatory pop-up.

## 4. Ask MIDD ("the egg"): keep it, sharpen it

The floating assistant is now a keeper. It cannot be pulled back because stakeholders have seen it and it draws immediate interest. The direction is to make it more useful, not to remove it.

- It must answer only from the dashboard data (PocketBase), never from external knowledge, or it becomes just another generic AI. It is already wired to read from PocketBase.
- It has real gaps: it can say how many industries exist but cannot yet answer which sectors those industries fall under, even though the data is present. Hillary has tested ranking value chains and that worked reading straight from PocketBase, so grouping is partly there.
- Process from now on: every time Jerome asks a question it cannot answer, he logs it. That backlog becomes the list of skills we build, one per class of question. The target is precise, grouped, analytical answers such as "where is the biggest bottleneck in Uganda's iron and steel industry," which is exactly the reason the assistant exists.

## 5. Architecture reflection: PocketBase for now, revisit later

This connects directly to the aggregation and query limits we have been hitting.

- Hillary raised whether PocketBase was the right choice now that the project has matured. It was chosen when the data looked highly dynamic and unsuited to a relational model, and when the scope was mostly more value chains. The data is now almost entirely relational.
- The real limitation is aggregation: grouping and summing that a normal database answers with one query forces us to build an engine or a layer on top. There is also a design concern, that the UI talks to PocketBase directly with no data-access layer, which locks us in if we ever change the datastore. This is the opposite of how we built UTIMBER, which started from the database.
- The choice ahead is one of three: build an aggregation engine on top of PocketBase, build a proper backend layer, or change the database (Postgres or Supabase, the latter being the original proposal before PocketBase was picked). The deciding criterion is delivery and simplicity.
- On scale: the workload is read-heavy and almost no one writes except ingestion, so read replicas and cloud scale-on-demand cover growth. There is no near-term prospect of ten thousand concurrent readers; perhaps a thousand at peak within three years. This is not a present concern as long as we set it up to scale gracefully. It currently runs on a test environment and would move to an independent, appropriately-sized server before real load.

Decision: continue with PocketBase for this phase because there is momentum and it delivers what the near term needs. Plan a clean migration path for later so that, when the time comes, we transition rather than rebuild. Hillary and Solomon each to research the aggregation-engine versus backend-layer versus database-change options and weigh them on ability to deliver.

## 6. Team and onboarding

The team is expanding as the project moves toward presentation.

- Baker: Hillary met him today, it went well, he is added to the repo and will be added to the WhatsApp group.
- Benjamin (Tarinika Benjamin, formerly Mohammed Arindeka), Jerome's brother: joins to produce the explainer graphics and animations, the storyboarding layer that makes the platform legible to the Commissioner and other lay stakeholders. He keeps his own working environment, does not need to store work in the repo, and shares outputs for the team to review. He uses Claude to understand the system, then designs, and presents as-is now, adjusting as the platform changes. Give him read access.
- The intern (a computer-science student, available at least to end of July, possibly end of August, and welcome to stay on for the learning): has not yet picked a specialty. Slot him in as a narrator and as a tester, plus research and small mini-tasks, kept within the software lifecycle. Testing capacity matters because an application is only as good as how well it is tested.
- Coming next: William and Haifa. More onboarding will follow once engagement with the Ministry of Water begins, but that is after this demonstration.
- Access policy for now: read access only, scoped to the docs repository we are currently working in.

## 7. Working discipline (Jerome to Solomon)

Set specific targets, focus, and close one item before starting the next. Do not get pulled into disruptions inside the same assignment. The cost of context-switching was real: the spatial-distribution and sector-distribution breakdowns each stretched to a week partly through back-and-forth. Break the elephant down piece by piece and finish each piece. Understanding the bigger picture is what lets Solomon design the small pieces well and generate his own ideas, which is where most of his best work has come from.

---

## Summary

A high-stakes demonstration is being arranged to a senior economist audience, potentially opening a multi-year engagement. To unlock it we must demonstrate one fully-worked value chain, Iron and Steel, to an audience that values precision and logic that traces from data to decision. The near-term plan is therefore narrow and deep: complete Iron and Steel end to end, with live data, click-to-open input panels, traffic-light status coding, essentiality-and-scarcity weighting, product-as-input consistency, and capacity-versus-target traceability. Ask MIDD stays and gets sharpened to answer precise grouped questions from PocketBase only, driven by a logged backlog of questions it currently fails. PocketBase continues for this phase with a planned migration path, its main weakness being aggregation. The team grows: Baker, Benjamin (explainer graphics), an intern (narrator and testing), and soon William and Haifa.

## Action Points

### Jerome
- Send Hillary the links and contacts for Benjamin and the intern.
- Log every question Ask MIDD fails to answer, as the backlog for new skills.
- Provide corrected or improved data content where accuracy was flagged (for example the cold rolled coil source text).
- Keep the team posted on the timing of the demonstration to the Permanent Secretary.
- Still outstanding from before: the four official source documents (issue #110).

### Solomon
- Focus only on Iron and Steel and complete it end to end before any other chain.
- Finish the live-data refresh work already in progress.
- Map: click a product to open its dropdown with information populated, fetched live; make missing data fetch.
- Add the local-capacity signal on the map and Explorer: show where capacity exists and where it is a gap.
- Explorer inputs: change hover to click, opening a closable side panel.
- Add traffic-light colour coding (red, orange, green, possibly up to five levels) on the bullets, surfacing the worst first; red means no domestic production.
- Weight inputs by essentiality times scarcity so essential-and-unavailable ranks highest; use the AI to help derive it.
- Make product-as-input consistent: cold rolled coil carries its HS-coded trade data on the input side too.
- For genuine process utilities with no data, show an explanatory pop-up rather than nothing.
- Add capacity-versus-target traceability on inputs.
- Research the data-architecture options (aggregation engine vs backend layer vs database change) from a delivery standpoint.
- Join the short evening check-in calls this week.

### Hillary
- Decide the data-architecture direction (aggregation engine on PocketBase, a backend layer, or migrate to Postgres/Supabase), on delivery and simplicity; continue on PocketBase this phase, plan the migration path.
- Produce scaling estimates (peak concurrent readers, read replicas, cloud scale-on-demand) so scale is a planned, not reactive, concern.
- Ask MIDD: build the unanswered-question logging loop, fix the sector-grouping gap, and keep it answering only from PocketBase.
- Onboard the growing team: add Baker to the WhatsApp group, give Benjamin read access, slot the intern into narrator and testing roles, prepare for William and Haifa, keep access read-only and scoped for now.
- Produce and distribute these minutes and the task queue.

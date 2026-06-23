# Meeting: Harness Engineering and the Single-Source Database

**Date:** 2026-06-23 (impromptu, second meeting of the day)
**Participants:** Hillary Arinda (Technical Lead), Jerome Nuwabaasa (MTIC), Solomon Ariho (Developer, partially present)
**Recording:** Audio + transcript via Tactiq
**Context:** Held right after the document uploader went live. The discussion set the next phase: one structured database as the single source of truth, all feedback routed through the LLM brain, a dedicated UI for Jerome, a domain with HTTPS, and a portable server-side harness. Staging-first from here on because production is now live and the coming changes are large.

---

# TABLE OF CONTENTS
1. [Summary](#summary)
2. [Action Items for Hillary](#action-items-for-hillary)
3. [Action Items for Jerome](#action-items-for-jerome)
4. [Action Items for Solomon](#action-items-for-solomon)
5. [Full Meeting Transcript (Cleaned)](#full-meeting-transcript-cleaned)
6. [Key Decisions](#key-decisions)

---

# SUMMARY

The uploader is live and is the missing link that was needed; PocketBase was always just a data store, the uploader is how documents get in. The meeting locked the next phase.

The central decision is one structured database as the single source of truth. Every document, whatever its form, is shredded by the LLM brain and its data lands in one place. Establishments live in one `industries` table: an industry appears once, new documents update its columns (for example adding an employment figure), new information may add a column, missing information stays blank. Related tables (value chains, etc.) link to it, so the Sankey, the treemaps, and the industry locations map all read from the same database instead of separate sources or raw files. Hillary will analyze and decide the exact structure; it is a big early design decision to take before the data grows.

All corrections go through the LLM, never by editing PocketBase directly. PocketBase is not smart; it only lets you view and adjust stored rows. Feedback must flow through the brain so it is tracked and the agents improve. Jerome will stop talking to the system through WhatsApp (that is Hillary's personal agent, too much unrelated context) and through VSCode; instead he gets a dedicated UI that talks only to the MIDD brain, where he gives feedback and pulls information.

Operationally: get a domain (no more remembering three IP addresses, and move off insecure HTTP), with staging and production subdomains; route all development through staging and automate the promotion to production; build duplicate detection so the same document is not ingested twice even if renamed; build the harness (ingestion, synthesis, review agents) with feedback tracked so each correction improves an agent; have the server brain keep its own records (hot file, ADRs, wiki) current so knowledge does not live only on Hillary's laptop; and containerize everything so it can move to another server or another LLM later. For now, use the Claude CLI already on the Hetzner server.

Acknowledged framing: we are working backwards. The proper order is document, shred, extract, database, backend, frontend. The prototype was built picking data from files; now we retrofit the database underneath it.

---

# ACTION ITEMS FOR HILLARY

1. **Decide the database structure (foundational, do first).** One structured database, single source of truth. One `industries` table where each establishment appears once and is updated in place (columns added over time, blanks where data is missing). Related tables (value chains, etc.) with relationships so the Sankey, treemaps, and locations map all read from the same database. Analyze and write the decision as an ADR before the data grows.
2. **Migrate all data into the database.** Everything currently under `data/` should be ingested into the structured database so every feature (maps, treemaps, KPIs, value chains) reads from PocketBase, not from raw files.
3. **Duplicate detection in the uploader.** The app must recognize a document it already has, even if the filename changed, and refuse to re-ingest the same work. This validation does not exist yet.
4. **Domain and HTTPS.** Purchase a domain from Cloudflare. Base name agreed: `midd-ug` (Manufacturing Industry Diagnostics Dashboard; `midd.com` is taken, so `midd-ug`). Set up `staging.<domain>` and production. Move off HTTP to HTTPS. Removes the need to remember three IP addresses.
5. **Automate the staging to production promotion.** All development goes to staging first; promotion to production is an automated pipeline to avoid unintended errors.
6. **Build the harness and the server-side brain.** Ingestion, synthesis, and review agents on the server. Every piece of feedback improves one agent and is tracked. The server brain updates its own records (hot file, ADRs, wiki) so knowledge is uniform and not stuck on Hillary's PC; all three teammates' LLMs can read the same records.
7. **Build the dedicated MIDD UI for Jerome.** A scoped interface that talks only to the MIDD brain (no unrelated personal context), where Jerome gives feedback and gets information. Corrections route through the LLM, not direct PocketBase edits.
8. **Containerize everything (Dockerfile).** So the whole system can ship to another server or another LLM later. For now, keep using the Claude CLI already on the Hetzner server.

# ACTION ITEMS FOR JEROME

1. Do all testing and experimentation on **staging**, not production. Production is live and stable; do not risk it.
2. Domain name preference provided: `midd-ug`.
3. Once the dedicated UI exists, interact with the brain **through that UI**, not through WhatsApp and not through VSCode.
4. Route all proposals and iterations **directly to the server** (through the UI), so context is not lost in private LLM chats.
5. Keep using the uploader (on staging) to bring in documents (the register and others).

# ACTION ITEMS FOR SOLOMON

1. All your work goes through **staging first**, then gets promoted to production.
2. Your work should update the **architecture design records (ADRs) and the server brain**, not just local notes, so all teammates' LLMs share the same records.
3. Dashboard redesign tasks from the earlier meeting still stand. Build against the single-source database structure once it is decided (so the dashboard reads from the database).

---

# FULL MEETING TRANSCRIPT (CLEANED)

## Opening: the uploader and a first gap

**Hillary:** From your side, what is the uploader currently doing and what are its current limitations?

**Jerome:** I have not yet uploaded with it. I was making the first upload, of the Industries Register PDF. Before the uploader existed we had put several files in directly.

**Hillary:** I had not recognized that name. So it is there, under manufacturing overview, because you put it there like any other folder and pushed it with Git. I have just seen a potential loophole: duplicates should not be allowed even if the name changes. The application should know it already has this document; that mechanism is not there yet. You do not want to re-upload the same work. Second, all your testing should be done on staging while this is still under development.

**Jerome:** I completely agree.

## Domain and security

**Hillary:** The one issue is you will have to remember the IP addresses, because we do not have a domain. There are really two issues: we do not have a domain, and our connection is not secure because it is HTTP.

**Jerome:** Can we have a domain? What would the base URL be?

**Jerome:** Let it be called the Manufacturing Industry Diagnostics Dashboard.

**Hillary:** So something like the acronym.

**Jerome:** MIDD, m-i-d-d.

**Hillary:** midd.com seems to exist, a business with a similar name.

**Jerome:** Then midd-ug.

**Hillary:** That should be free. I will get it from Cloudflare and reconcile. Staging will be staging.midd-ug. The plan: all development goes to staging first, then we promote to production, because production is now live and fairly stable and we do not want to mess it up. We will automate that promotion pipeline to avoid unintended errors.

## The single-source database (the core of the meeting)

**Hillary:** We are going to start using the uploader, which was the missing link. PocketBase was there but it is really just a data store for housing data. The uploader still needs validation and a few things you will want added. And all the data under `data/` should be ingested into the database, so that every feature that is fed by those documents stops reading from the documents and reads from PocketBase. Correct?

**Jerome:** Correct. The thing I need to understand is how this works. If I provide a file, it may contain general economic data, say about the performance of the iron and steel sector, but also information about specific industries, like a list of industries we visited. When it picks the information about the industries, that should go into one place. One database for everything. So if there is information about an industry that was ingested through the register upload, and then another report has more information about that same industry, it should update the same place.

**Hillary:** Two things. First case: a document had information about industries plus other information. You extracted that and put it in a table with rows and columns, each row an industry. Then a new document comes through the same process and you either update the row or append to the table.

**Jerome:** It should all go to the same table. The best example is the industry locations: what you see there is not coming from the same table that has the treemaps. It should be.

**Hillary:** Should it be the same table, or one database with several related tables, since the sources differ but the columns and structure are often the same, as with the distribution treemaps and the locations?

**Jerome:** It has the columns I provided. When data is extracted it should fill certain specific columns and leave others. We should have one table that can have many columns. When I give an update I may be updating only one column, for example employment for one industry. I should not get a separate table. If new data needs a new row, we add a row in the same table, or add a new column, but the table stays one. I do not want a separate industries table; there should be one.

**Hillary:** Ideally you do not duplicate industries; an industry appears once and gets various updates. If information was never there, you add the column. So the question is structured versus unstructured database, since this will change a lot.

**Jerome:** It will change a lot at the beginning, then stabilize.

**Hillary:** I will advise on the best database structure after some analysis; it is a big design decision to take early. Can one industry have more columns than another because it has more information?

**Jerome:** Whenever we add information, every industry should have that field; if an industry does not have that information, it just stays blank.

**Hillary:** So it is a structured database, blanks where missing, that keeps changing, with relationships between tables.

**Jerome:** Yes. For example a table for value chains, from which the value chain Sankey draws, linked to the industries: these are the industries under this stage. On chassis and suspension, for instance, I want to add how many industries in Uganda can make this product. It goes to the database, which holds what products each industry makes, and returns a number, say six industries in Uganda currently make this product.

**Hillary:** Understood. The need is clear. We are working backwards: we should have had tables from the start, but for first prototyping that would have taken time, so we have a structure picking data from different files. Now we make it the clean pipeline: get a document, shred it, pick data, put it in the database, update the backend, update the frontend.

## The brain, feedback, and the harness

**Hillary:** The biggest part is the brain that picks the data, the LLM classifier that reads these documents and places the information in the right table in PocketBase. PocketBase is not smart. What it gives you is the ability to look at uploaded data and change it or change its structure. But feedback should not come from the user editing PocketBase directly; all corrections should still go through the LLM, so if it got something wrong, it is corrected through the brain and recorded.

**Hillary:** The initial work will be intense, but it should all go through the LLM on the server. Especially for you, Jerome, because you will be updating the tables that feed the entire value chain, so every correction you make has to be recorded in the brain. Let me show you how this works. A harness is a structure that gives the dos, the don'ts, and the how. We have these agents: an ingestion agent, a synthesis agent that extracts the data, and a review agent that reviews. Every time you give feedback, you are improving one of these agents, and that feedback should be tracked. This does not exist yet; I have to build it.

**Hillary:** Look at my brain. There is a wiki where everything is tracked, for example the hot file for MTIC: every change puts an update on what is current, pending, and changed. And the ADRs, the architecture design records, get updated too. The brain on the server should be smart enough to update each of these documents. And it should be portable, put in a Dockerfile and shipped, so when we move to another server we do not start from scratch. At that point we can use another LLM or subscription, but for this stage let us use what already exists on the Hetzner server. Going forward, all the iterations you propose should go directly to the server. We lose a lot of context in your private LLM chats; once that loop is closed, Solomon's work also becomes more straightforward, because it ends up on the server and updates the architecture records.

**Hillary:** Currently the only place this is tracked is locally on my PC, plus the meeting transcripts in the repo, which your agents can read, but that is not good enough. We will change the design so that even when you work independently with your LLMs, they update records that all our LLMs can access. I will set that up on staging first; once perfected, we promote to production. The coming changes are big, so things are bound to break before they get better.

## The UI for Jerome

**Jerome:** Will my interaction with the LLM still be through VSCode, or a different platform?

**Hillary:** Not WhatsApp, which is how you have been talking to the agent; that is my personal agent and has too much context, it is not optimized for this. I want you to talk to it through a UI we will develop, so you are strictly talking to MIDD only, an interface that has all the knowledge of MIDD and nothing else. You will get your information from there and give feedback there. Let me think it through, build it, we test it, and we get going.

**Jerome:** Great.

---

# KEY DECISIONS

- DECISION: One structured database is the single source of truth. One `industries` table; an industry appears once and is updated in place (columns added over time, blanks where missing). Related tables (value chains, etc.) link to it. The Sankey, treemaps, and locations map all read from this database.
- DECISION: All corrections route through the LLM brain, never by editing PocketBase directly, so feedback is tracked and the agents improve.
- DECISION: Jerome interacts through a dedicated MIDD UI, not WhatsApp and not VSCode.
- DECISION: Get a domain, `midd-ug`, with `staging.` and production subdomains, and move to HTTPS.
- DECISION: Staging-first for all development; automate promotion to production.
- DECISION: Duplicate documents must be detected and rejected, even if renamed.
- DECISION: The server brain keeps its own records (hot file, ADRs, wiki) current and uniform for all teammates.
- DECISION: Containerize everything (Dockerfile) for portability; keep using the Hetzner Claude CLI for now.
- FRAMING: We are working backwards (document, shred, extract, database, backend, frontend); retrofitting the database under the existing prototype.

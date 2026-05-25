# MY_BRAIN Setup Guide — Solomon Ariho

This sets up your persistent knowledge base: a folder called `MY_BRAIN` that Claude reads and writes to across every session. Every insight, decision, and piece of research you produce gets saved here. Over time it compounds — Claude gets smarter about your work because it remembers everything.

Hillary uses the same pattern. This is your own independent copy.

---

## Step 1: Create the folder structure

Open your terminal and run:

```bash
mkdir -p ~/MY_BRAIN/wiki/PROJECTS
mkdir -p ~/MY_BRAIN/wiki/sessions
mkdir -p ~/MY_BRAIN/wiki/sources
mkdir -p ~/MY_BRAIN/wiki/entities
mkdir -p ~/MY_BRAIN/skills/save
mkdir -p ~/MY_BRAIN/skills/wiki
mkdir -p ~/MY_BRAIN/skills/wiki-ingest
```

---

## Step 2: Create your MEMORY.md index

Create `~/MY_BRAIN/wiki/MEMORY.md` with this content:

```markdown
# Memory Index

(Empty for now — entries will be added as you work)
```

---

## Step 3: Create your hot file for the MTIC project

Create `~/MY_BRAIN/wiki/hot_mtic.md` with this content:

```markdown
---
type: hot-cache
title: "Hot Cache — MTIC Industrial Diagnostic Study"
updated: 2026-05-26
tags:
  - mtic
  - industrial-diagnostic-study
status: current
---

# Hot Cache: MTIC Industrial Diagnostic Study

## Project
Industrial diagnostic report covering 9 NDP IV priority manufacturing value chains.
Deadline: 8 June 2026.
Repo: https://github.com/MTIC-Uganda/industrial_diagnostic_study

## Current Status
Starting. Report structure not yet produced.

## Next Action
Read both ToR documents. Produce proposed report structure. Share with Jerome for Commissioner approval.

## Blockers
None yet.
```

---

## Step 4: Create your CLAUDE.md

Create `~/MY_BRAIN/CLAUDE.md` with this content:

```markdown
# Solomon's Workspace — CLAUDE.md

## Session Start

At the start of every new conversation, read these files before doing anything else:
1. `~/MY_BRAIN/wiki/MEMORY.md` — your profile and preferences across sessions
2. `~/MY_BRAIN/wiki/hot_mtic.md` — current working state for the MTIC project

## Knowledge Base

Path: `~/MY_BRAIN/`

This is your persistent knowledge base. Save insights, decisions, and research here as you work. Use it to avoid repeating yourself across sessions.

## Rules

- Always read the hot file before starting work on the MTIC project
- Save important decisions and findings to the wiki as you go — do not rely on memory
- When you finish a session, update `hot_mtic.md` with what changed and what is next
```

---

## Step 5: Install Claude Code

Claude Code is the CLI version of Claude that reads your files and works inside your project folders.

1. Install Node.js if you don't have it: https://nodejs.org (download the LTS version)
2. Open your terminal and run:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. Run `claude` to start it and log in with your Anthropic account

Cost: $20/month. Jerome is covering this.

---

## Step 6: Add the save skill

Create `~/MY_BRAIN/skills/save/SKILL.md` with this content:

```markdown
---
name: save
description: >
  Save the current conversation, answer, or insight into the wiki vault as a
  structured note. Creates frontmatter, files it in the correct folder, and
  updates the hot cache.
  Triggers on: "save this", "/save", "file this", "save to wiki", "keep this".
allowed-tools: Read Write Edit Glob Grep
---

# /save skill

When triggered:
1. Summarize what was accomplished or decided in this session
2. Determine the right note type (project note, session log, decision, research)
3. Create a markdown file in the right wiki folder with proper frontmatter
4. Update hot_mtic.md with what changed and what is next
5. Add a pointer to MEMORY.md if the insight is worth keeping across sessions
```

---

## Step 7: Clone the project repo

```bash
git clone https://github.com/MTIC-Uganda/industrial_diagnostic_study.git
cd industrial_diagnostic_study
```

Then open Claude Code inside it:

```bash
claude
```

Claude will read the `CLAUDE.md` in the repo and know exactly what the project is.

---

## How it compounds

Every time you finish a session:
- Run `/save` and Claude will write a structured note to `~/MY_BRAIN/wiki/sessions/`
- Update `hot_mtic.md` with what is next
- Next session, Claude reads the hot file and picks up exactly where you left off

After a few weeks you will have a wiki of everything you have learned about these 9 value chains. That knowledge stays with you beyond this project.

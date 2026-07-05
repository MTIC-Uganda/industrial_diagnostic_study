workspace "MIDD — Manufacturing Industry Diagnostics Dashboard" "As-built 2026-06-23: Jerome uploads a document via the web uploader (no Git) -> the Claude CLI brain on Hetzner reads his intent and extracts the data into one PocketBase datastore -> the dashboard rebuilds from it. Ask MIDD is the scoped feedback/return channel. Domain midd-ug.com over HTTPS." {

    model {
        # People
        jerome    = person "Jerome Nuwabaasa" "MTIC client. Uploads source documents via the web uploader (no Git), reviews the dashboard, and asks/corrects through Ask MIDD."
        solomon   = person "Solomon Ariho" "Lead developer. Builds the dashboard frontend in the repo; reads the shared record (ADRs, STATUS, TASKS) for instructions; pushes branches."
        hillary   = person "Hillary Arinda" "Technical lead / pipeline+infra engineer. Owns the harness, the agents, the datastore, and the domain."
        commissioner = person "Commissioner (MTIC)" "Reviews the public dashboard. Wants high-level numbers."
        colleagues = person "MTIC Colleagues" "View the public dashboard."

        # External systems
        github    = softwareSystem "GitHub (MTIC-Uganda)" "The shared record + version control + CI/CD trigger. Holds code, ADRs, STATUS.md, TASKS.md, meeting transcripts." "External"
        itcTrade  = softwareSystem "ITC TradeMap" "Trade statistics, used for export indicators." "External"
        cloudflare = softwareSystem "Cloudflare (midd-ug.com)" "DNS + proxy + HTTPS (SSL Full) in front of all surfaces. Zero Trust Access GATES the 4 internal tool hosts (upload/ask/staging-upload/staging-ask) to a 3-person email allow-list, preauthorized, no OTP (ADR-015). The 2 dashboards stay public; PocketBase keeps its own admin login." "External"
        claudeMax = softwareSystem "Claude (Max plan)" "The model behind the Claude CLI on the host. Powers Ask MIDD, ingestion, the orchestrator. Hillary's plan for now; MIDD gets its own key when containerized (ADR-012)." "External"

        # The MIDD system, all hosted on Hetzner 89.167.121.193
        midd = softwareSystem "MIDD Platform" "Document-to-dashboard pipeline with a scoped brain and feedback loop, staging + prod." {

            # ── INTAKE (the doors) ─────────────────────────────────────────
            uploader = container "Document Uploader" "FastAPI web app. Jerome picks a value chain, writes full intent, attaches any document. Saves it to data/<value-chain>/ + a <file>.task.md intent sidecar, commits to the repo. Rejects duplicates by content hash. Staging :8210, prod :8211." "Python/FastAPI"
            askmidd  = container "Ask MIDD (scoped brain)" "FastAPI chat. Team-gated /ask (Max-plan CLI, windowed memory) on staging :8220 / prod :8221; the gated tool can run a read-only analytics sandbox (ADR-020, analytics_sandbox.py) that executes model-written pandas/numpy/sklearn/matplotlib over the data as in-memory DataFrames, four safety layers (AST validation, restricted builtins, no PB/network handle, subprocess rlimit+timeout) so it queries anything but alters nothing. PUBLIC /api/ask (ADR-014): Haiku, rate-limited, browser memory, plain prose, served same-origin at midd-ug.com/api/ask; keeps the narrow validated query_tool path (plan->validate->query->answer), no code execution. Both run in a no-repo sandbox with a sanitized PocketBase brief so they answer live data without leaking names. Deployed staging-first via deploy_brain.sh (ADR-019)." "Python/FastAPI + Claude CLI"

            # ── BRAIN / AGENTS (the workers, on the host) ──────────────────
            claudeCli = container "Claude CLI (brain engine)" "/usr/bin/claude on the host, headless. The single engine behind Ask MIDD, ingestion, and the orchestrator. No Anthropic API key; uses the Max plan." "Claude Code CLI"
            orchestrator = container "Upload Orchestrator" "scripts/process_upload.py (importable; pure route()). On upload: CLI reads the intent, then routes by folder AND file type: manufacturing-overview + register PDF -> deterministic parse; manufacturing-overview + spreadsheet -> key_indicators agent (updates existing KPI-card slugs from a UBOS scorecard, additive-only); any value-chain folder -> LLM ingestion. Then rebuilds + publishes the dashboard, self-checks." "Python"
            keyIndicatorsAgent = container "Key Indicators Agent" "agents/key_indicators_agent.py. Loads the UBOS scorecard sheets as pandas DataFrames and has the Claude CLI write read-only code that COMPUTES the figure (e.g. manufactured trade = SITC sections 5,6,7,8 excluding 68 for the latest year), runs it in analytics_sandbox (ADR-020, no data-source handle), and PATCHes the result to EXISTING key_indicators slugs. Retries with error feedback; additive-only, never creates/renames/deletes a card (ADR-017). Safety core validate_updates unit-tested." "Python/Claude CLI + analytics_sandbox"
            ingestionAgent = container "Ingestion Agent" "Extracts PDF/DOCX/XLSX (pdfplumber/python-docx/openpyxl) via the Claude CLI; folder-routed; reads the .task.md intent sidecar. Writes diagnostic_datapoints (sector docs)." "Python/Claude CLI"
            synthesisAgent = container "Synthesis Agent" "Datastore rows -> report/dashboard content." "Python/Claude CLI"
            reviewAgent = container "Review Agent" "Independent quality gate before publish." "Python/Claude CLI"
            deterministicParser = container "Register Parser" "scripts/extract_industries_to_records.py. Deterministic pypdf parse of the National Industries Register -> 7,011 establishment rows. Brittle to layout changes (then the LLM path is needed)." "Python/pypdf"

            # ── DATASTORE (single source of truth, ADR-011) ───────────────
            pocketbase = container "PocketBase — Datastore" "The ONLY data source (ADR-017, enforced): generators read solely from here, no CSV/JSON fallback, and check_single_source.sh blocks any reintroduction in CI + pre-commit. industries = canonical establishment table (1 row per reg_number, updated in place; curated map factories merged as FAC-*). Plus value_chains, kpi_indicators, key_indicators, diagnostic_datapoints. Prod :8090, staging :8091." "PocketBase/SQLite"

            # ── BUILD + SURFACES ──────────────────────────────────────────
            dashboardGen = container "Dashboard Generator" "scripts/generate_dashboard.py. Treemaps + locations map aggregate from PocketBase industries (static JSON fallback). Fills the template." "Python"
            reactBuild = container "React Sankey Build" "app/frontend -> dist (D3-sankey), embedded as sankey.html." "Node/Vite"
            explorerBuild = container "React Value Chain Explorer Build" "app/explorer -> dist (sidebar product picker + chain-of-cards drill-down: inputs/technology/professionals per stage), embedded as explorer.html. Iron & Steel only for v1." "Node/Vite/Tailwind"
            dashboard = container "Dashboard (static)" "The public diagnostic dashboard. Prod midd-ug.com (:8201), staging staging.midd-ug.com (:8200). One build serves both: a hostname check at runtime shows, on prod, the public Ask MIDD bubble only; on staging, BOTH the team Upload/Ask links and the bubble (so the bubble is testable before prod) (ADR-016, Issue #71)." "Static HTML/Nginx"

            # ── SHARED RECORD + ROUTING ───────────────────────────────────
            record = container "Shared Record" "The single source of decisions + state all agents read: ADRs (docs/adr), STATUS.md (live snapshot), TASKS.md (per-owner queue), meeting transcripts, CLAUDE.md. Brain reads a read-only clone pulled every 5 min." "Markdown/Git"
            nginx = container "nginx reverse proxy" "Host-routes midd-ug.com subdomains to the local services; self-signed origin cert behind Cloudflare Full." "Nginx"
            ci = container "GitHub Actions CI" "On push: single-source guard (ADR-017) + pytest (ADR-018) gate the build -> build dashboard (from PocketBase) -> deploy staging -> promote prod -> auto-merge to main -> self-heal. Seed job is SCHEMA-ONLY (PB_SCHEMA_ONLY=1: ensures collections+fields, never re-seeds records, so a deploy can't clobber PocketBase; ADR-017). Drift Check mirrors PB->files as a git backup. deploy-brain + deploy-uploader jobs deploy those box apps staging->verify->prod when their code changes (ADR-019)." "YAML"
        }

        # ── People -> doors ───────────────────────────────────────────────
        jerome -> uploader "Uploads documents with full intent (no Git)"
        jerome -> askmidd "Asks questions / leaves corrections"
        jerome -> dashboard "Reviews"
        solomon -> github "Codes the dashboard; reads ADRs/STATUS/TASKS for instructions; pushes branches"
        hillary -> midd "Builds and operates the harness, agents, datastore, domain"
        commissioner -> dashboard "Reviews the public dashboard"
        colleagues -> dashboard "View"

        # ── Data loop: document -> brain -> datastore -> dashboard ────────
        uploader -> github "Commits file + intent sidecar to data/<value-chain>/"
        uploader -> orchestrator "Triggers processing on upload"
        orchestrator -> claudeCli "Reads the intent (LLM understands)"
        orchestrator -> deterministicParser "Register -> establishment rows"
        orchestrator -> ingestionAgent "Sector document -> datapoints"
        orchestrator -> keyIndicatorsAgent "Manufacturing-overview spreadsheet -> KPI card updates"
        keyIndicatorsAgent -> claudeCli "Maps scorecard + intent to existing slug updates"
        keyIndicatorsAgent -> pocketbase "PATCHes existing key_indicators (additive-only)"
        ingestionAgent -> claudeCli "Extraction + mapping"
        deterministicParser -> pocketbase "Seeds industries"
        ingestionAgent -> pocketbase "Seeds diagnostic_datapoints"
        orchestrator -> dashboardGen "Rebuild after seeding"
        dashboardGen -> pocketbase "Reads industries/value_chains/kpis (treemaps + locations)"
        dashboardGen -> dashboard "Publishes the page"

        # ── Feedback / return channel ─────────────────────────────────────
        askmidd -> claudeCli "Scoped query"
        askmidd -> record "Answers strictly from the project records"
        jerome -> pocketbase "DOES NOT edit directly (ADR-012: corrections go through the LLM)"

        # ── Environment model (ADR-013 rev): code auto-promotes, data promotes on approval ──
        ci -> dashboard "CODE promotes UP automatically: staging dashboard -> prod on health-check"
        uploader -> pocketbase "DATA promotes UP on approval: Jerome clicks 'Apply to production' -> promote_staging_to_prod.sh copies approved staging PocketBase -> prod + rebuilds (never re-runs the LLM)"
        pocketbase -> pocketbase "RESET DOWN: refresh_staging_from_prod.sh mirrors prod -> staging, discarding staging experiments. Both PBs use their own empty migrationsDir (shared dir caused a prod outage)"

        # ── Code loop + sync ──────────────────────────────────────────────
        github -> ci "Push triggers build/deploy/promote/seed"
        ci -> dashboardGen "Build dashboard from PocketBase"
        ci -> reactBuild "Build Sankey"
        ci -> explorerBuild "Build Value Chain Explorer"
        ci -> dashboard "Deploy staging -> promote prod -> auto-merge"
        record -> solomon "Instructions: ADRs, STATUS, TASKS"
        record -> askmidd "Brain reads a read-only clone (pulled every 5 min)"

        # ── Edge / external ───────────────────────────────────────────────
        cloudflare -> nginx "Proxies HTTPS to the host"
        nginx -> dashboard "Routes the dashboard subdomains"
        nginx -> uploader "Routes the uploader subdomains"
        nginx -> askmidd "Routes the ask subdomains"
        claudeCli -> claudeMax "Runs on the Max plan"
        itcTrade -> github "TradeMap CSVs in data/trademap"
    }

    views {
        systemContext midd "SystemContext" "People and external systems around MIDD." {
            include *
            autoLayout lr
        }
        container midd "Containers" "MIDD internal structure: intake, brain, datastore, build, surfaces, record." {
            include *
            autoLayout tb
        }
        dynamic midd "UploadFlow" "A document upload, end to end." {
            jerome -> uploader "1. Upload document + full intent (no Git)"
            uploader -> github "2. Commit to data/<value-chain>/ + .task.md sidecar"
            uploader -> orchestrator "3. Trigger processing"
            orchestrator -> claudeCli "4. CLI reads the intent (understands what to do)"
            orchestrator -> deterministicParser "5a. Register -> establishment rows"
            orchestrator -> ingestionAgent "5b. Sector doc -> datapoints (via CLI)"
            deterministicParser -> pocketbase "6. Seed industries (single source)"
            orchestrator -> dashboardGen "7. Rebuild from PocketBase"
            dashboardGen -> dashboard "8. Publish; treemaps + locations from industries"
            autoLayout lr
        }
        dynamic midd "FeedbackFlow" "Asking and correcting through the brain, not the database." {
            jerome -> askmidd "1. Ask a question or leave a correction"
            askmidd -> record "2. Brain reads the project records"
            askmidd -> claudeCli "3. Scoped answer (Max plan)"
            askmidd -> jerome "4. Answer + feedback logged (corrections then flow through ingestion, never direct PocketBase)"
            autoLayout lr
        }
        styles {
            element "Person" { shape Person background #1168BD color #ffffff }
            element "External" { background #888888 color #ffffff }
            element "Software System" { background #1168BD color #ffffff }
            element "Container" { background #438DD5 color #ffffff }
        }
    }
}

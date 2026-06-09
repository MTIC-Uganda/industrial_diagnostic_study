workspace "MTIC Industrial Diagnostic Study — Value Chain Intelligence System" "Automated pipeline: Jerome uploads data → agentic ingest/synthesize/review → web dashboard updated. Phase 1 (manual) is live; Phases 2–3 (automation) are in progress." {

    model {
        # People
        solomon   = person "Solomon Ariho" "Lead developer. Builds and iterates on the web dashboard. Pushes branches; main triggers prod deploy."
        hillary   = person "Hillary Arinda" "Technical advisor and pipeline engineer. Sets up infra, builds agentic chain, reviews PRs."
        jerome    = person "Jerome Nuwabaasa" "MTIC client. Uploads source data with context notes to the repo. Defines quality matrix (pass/fail criteria)."
        commissioner = person "Commissioner (MTIC)" "Final authority. Reviews the public dashboard; approves strategic outputs."
        colleagues = person "MTIC Colleagues" "Reviewers. Access the public prod URL to review value chain assessments and give feedback."

        # External systems
        github    = softwareSystem "GitHub (MTIC-Uganda org)" "Version control, CI/CD trigger, PR review gate." "External"
        itcTrade  = softwareSystem "ITC TradeMap" "International trade statistics. Automated extraction via trademap scripts." "External"
        whatsapp  = softwareSystem "WhatsApp (Hillary's Agent)" "Push notifications at each pipeline stage: upload detected, ingestion done, review passed/failed, deploy complete." "External"
        hetzner   = softwareSystem "Hetzner Server (89.167.121.193)" "Always-on server. Hosts staging and prod. Runs agentic pipeline workers (Phase 2+)."

        # The full pipeline system
        pipeline = softwareSystem "Value Chain Intelligence Pipeline" "End-to-end data-to-dashboard automation." {

            # ── DATA LAYER ──────────────────────────────────────────────────
            rawData = container "Raw Data Store" "Jerome uploads: PDFs, DOCX, XLSX, DOCX with context notes. Also TradeMap CSV exports. Path: data/ in repo." "PDF/XLSX/DOCX/Markdown"

            schema = container "Value Chain Schema" "Structured field definitions per stage per chain: production capacity, utilisation %, imports, exports (TradeMap), Tenfold 2040 targets, data gap flags. Authored by Jerome. Path: data/schema/." "Markdown/JSON"

            qualityMatrix = container "Quality Matrix" "Jerome's pass/fail criteria for each section of the diagnostic. The review agent scores against this. Path: docs/quality-matrix.md." "Markdown"

            synthesizedDB = container "Synthesized Data Store" "Structured JSON records per chain per stage. Output of the ingestion and synthesis agents. Path: data/synthesized/." "JSON"

            # ── AGENT LAYER (Phase 2+) ─────────────────────────────────────
            ingestionAgent = container "Ingestion Agent" "Triggered by GitHub push to data/. Reads the uploaded file + Jerome's context note. Maps content to schema fields. Writes JSON to synthesized store. Flags unmapped fields as data gaps. (Phase 2)" "Python/Claude Code"

            synthesisAgent = container "Synthesis Agent" "Reads all JSON for one value chain. Produces: current status assessment, gap vs Tenfold 2040, ranked bottleneck list, project profile sketches. Output: report/synthesized/<chain>/assessment.md. (Phase 2)" "Python/Claude Code"

            reviewAgent = container "Review Agent" "Validates synthesis output against Jerome's quality matrix. PASS: opens PR to main. FAIL: sends specific feedback via WhatsApp and routes back to synthesis. Self-healing loop until PASS or human override. (Phase 2)" "Python/Claude Code"

            # ── CI/CD LAYER ────────────────────────────────────────────────
            ciPipeline = container "GitHub Actions Pipeline" "Triggered on every push. Any branch → staging deploy (self-heal retry loop up to 3×). Staging pass → prod promotion + auto-merge to main. Merge conflict → warning only (prod still updated). Short URL: https://tinyurl.com/28lxntmc" "YAML"

            # ── PRESENTATION LAYER ─────────────────────────────────────────
            stagingApp = container "Staging Dashboard" "Live preview of every branch push. URL: http://89.167.121.193:8200. Reviewers check here before main." "Static HTML served by nginx"

            prodApp = container "Production Dashboard" "Public-facing value chain dashboard. URL: http://89.167.121.193:8201. Promoted from staging on main only. Jerome shares this with MTIC colleagues and Commissioner." "Static HTML served by nginx"

            # ── SCRIPTS ───────────────────────────────────────────────────
            buildScripts = container "Report Build Scripts" "Assemble markdown chapters into Word/PPTX deliverables. Separate from the dashboard pipeline. scripts/build_reports_docx.py etc." "Python"
        }

        # ── RELATIONSHIPS: people → systems ──────────────────────────────
        jerome    -> rawData   "Uploads data files with context notes (push to data/ branch → PR → main)"
        jerome    -> qualityMatrix "Authors and maintains pass/fail criteria"
        solomon   -> pipeline  "Pushes dashboard code to branches; main triggers deploy"
        hillary   -> pipeline  "Builds and maintains the agentic pipeline and CI/CD"
        colleagues -> prodApp  "Reviews value chain assessments via public URL"
        commissioner -> prodApp "Reviews strategic outputs"

        # ── DATA FLOW: ingest → synthesize → review ───────────────────────
        rawData   -> ingestionAgent  "File + context note read on push event"
        schema    -> ingestionAgent  "Field definitions guide extraction"
        ingestionAgent -> synthesizedDB "Writes structured JSON, flags data gaps"
        synthesizedDB  -> synthesisAgent "All stage JSONs for one chain"
        qualityMatrix  -> reviewAgent    "Pass/fail criteria loaded at review time"
        synthesisAgent -> reviewAgent    "Assessment markdown submitted for review"
        reviewAgent    -> ciPipeline     "PASS: triggers PR to main"
        reviewAgent    -> whatsapp       "FAIL: pushes specific gap feedback to Hillary/Solomon"
        reviewAgent    -> synthesisAgent "FAIL: feedback routed back, loop repeats"

        # ── CI/CD FLOW ────────────────────────────────────────────────────
        github    -> ciPipeline  "Push event triggers pipeline"
        ciPipeline -> stagingApp "Every push: scp dashboard HTML to staging"
        ciPipeline -> prodApp    "main only: copy staging → prod after health check"
        ciPipeline -> whatsapp   "Deploy complete notification to MTIC group (Phase 2)"

        # ── EXTERNAL DATA ─────────────────────────────────────────────────
        itcTrade  -> rawData     "TradeMap CSV exports stored in data/"

        # ── REPORT TRACK (separate from dashboard) ────────────────────────
        synthesizedDB -> buildScripts "Phase 3: synthesized data feeds report assembly"
        buildScripts -> prodApp       "Report sections rendered in dashboard"
    }

    views {
        systemContext pipeline "SystemContext" "People and external systems around the pipeline." {
            include *
            autoLayout lr
        }

        container pipeline "Containers" "Internal structure and data flow of the pipeline." {
            include *
            autoLayout tb
        }

        dynamic pipeline "DataFlow" "How a Jerome data upload flows through the full pipeline to the live dashboard." {
            jerome -> rawData "1. Jerome pushes data file + context note to data/ branch"
            rawData -> ingestionAgent "2. Push event triggers ingestion agent"
            schema -> ingestionAgent "3. Schema loaded for field mapping"
            ingestionAgent -> synthesizedDB "4. Structured JSON written; data gaps flagged"
            synthesizedDB -> synthesisAgent "5. Synthesis agent reads all stage data for one chain"
            qualityMatrix -> reviewAgent "6. Quality matrix loaded"
            synthesisAgent -> reviewAgent "7. Assessment submitted to review agent"
            reviewAgent -> ciPipeline "8a. PASS: PR opened to main, CI triggered"
            ciPipeline -> stagingApp "9a. Staging updated"
            ciPipeline -> prodApp "10a. Prod promoted (main only)"
            ciPipeline -> whatsapp "11. WhatsApp notification: prod live"
            reviewAgent -> whatsapp "8b. FAIL: specific gap feedback sent to team"
            reviewAgent -> synthesisAgent "8c. FAIL: feedback looped back for re-synthesis"
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #888888
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }
}

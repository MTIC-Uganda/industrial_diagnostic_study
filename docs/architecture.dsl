workspace "MTIC Industrial Diagnostic Study" "AI-assisted research and document generation pipeline for Uganda's 9 NDP IV priority manufacturing value chains." {

    model {
        # People
        solomon = person "Solomon Ariho" "Lead executor. Runs Claude Code sessions, ingests data, generates chapters."
        hillary  = person "Hillary Arinda" "Technical advisor. Sets up environment, reviews PRs, guides workflow."
        jerome   = person "Jerome Nuwabaasa" "MTIC client coordinator. Reviews content, provides source data, unblocks Commissioner."
        commissioner = person "Commissioner (MTIC)" "Final authority. Approved inception reports and report structure before chapter work began."

        # External systems
        github = softwareSystem "GitHub (MTIC-Uganda org)" "Version control and collaboration. All chapters, data, and scripts live here. PRs are the review gate." "External"
        itcTrademap = softwareSystem "ITC TradeMap" "International trade statistics portal. Automated extraction via trademap_fetch.py." "External"
        claudeCode = softwareSystem "Claude Code (Anthropic)" "AI engine. Primary analytical and writing tool. Ingests source data, generates chapter content, builds Word/PPTX outputs." "External"

        # The pipeline system
        pipeline = softwareSystem "Diagnostic Study Pipeline" "Local research and document generation toolchain." {

            sourceData = container "Source Data Store" "All reference documents: ToR PDFs, value chain data, NIP 2020, Tenfold Strategy, TradeMap exports. Stored in data/ and tor/." "Markdown / PDF / XLSX"

            chapterStore = container "Chapter Markdown Store" "One .md file per chapter per report. report/chapters/report1-*.md and report2-*.md. Markdown is the single source of truth; all formatted outputs are derived from these." "Markdown"

            buildScripts = container "Build Scripts" "Python scripts that assemble markdown chapters into final deliverables. Handles section order, abbreviation expansion (first-use), headers/footers, and all output formats." "Python" {
                docxBuilder  = component "build_reports_docx.py"  "Assembles chapters into Word .docx reports."
                pptxBuilder  = component "build_reports_pptx.py"  "Builds full PowerPoint slide decks."
                execBuilder  = component "build_exec_decks.py"    "Builds short Commissioner/boardroom executive decks."
                trademapClient = component "trademap_fetch.py"    "Automated ITC TradeMap data extraction."
                acronymExpander = component "expand_acronyms.py"  "First-use acronym expansion across chapters."
            }

            outputs = container "Final Deliverables" "Word documents, PowerPoint decks, and executive decks delivered to MTIC." "DOCX / PPTX" {
                report1 = component "Report 1 — Iron, Steel, Copper, Automotive" "Full diagnostic for 3 value chains."
                report2 = component "Report 2 — Textiles, Pharma, Petrochem, Sugar, Plastics, Cement" "Full diagnostic for 6 value chains."
                execDecks = component "Executive Decks (x2)" "Commissioner-level short-form presentations."
                inceptionReports = component "Inception Reports (x2)" "Pre-chapter-work approval documents. Commissioner-signed before execution."
            }
        }

        # Relationships — people to systems
        solomon -> claudeCode "Prompts chapter by chapter, ingests source data, commits output"
        solomon -> github "Opens PRs per chapter, merges on approval"
        hillary -> github "Reviews PRs, approves merges"
        jerome -> github "Provides data, reviews content"
        jerome -> commissioner "Presents inception reports and structure for approval"
        hillary -> pipeline "Sets up environment, guides workflow"

        # Relationships — pipeline internals
        solomon -> sourceData "Uploads reference docs and TradeMap exports"
        solomon -> chapterStore "Commits AI-generated chapter markdown"
        sourceData -> claudeCode "Ingested as context before synthesis"
        claudeCode -> chapterStore "Generates chapter content"
        chapterStore -> buildScripts "Input to all build scripts"
        buildScripts -> outputs "Assembles final deliverables"
        itcTrademap -> trademapClient "Data extracted via automated login + scrape"
        trademapClient -> sourceData "Exports stored in data/"

        # External deliveries
        outputs -> jerome "Final Word + PPTX reports delivered"
        outputs -> commissioner "Executive decks presented at Commissioner level"
    }

    views {
        systemContext pipeline "SystemContext" "How the pipeline sits within the broader MTIC ecosystem." {
            include *
            autoLayout lr
        }

        container pipeline "Containers" "Internal structure of the diagnostic study pipeline." {
            include *
            autoLayout tb
        }

        component buildScripts "BuildScripts" "Build script components." {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #999999
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

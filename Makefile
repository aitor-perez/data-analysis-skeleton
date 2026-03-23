# ============================================================================
# Makefile — Data Analysis Pipeline
# ============================================================================
# Usage:
#   make venv            Create virtual environment and install dependencies
#   make status          Show pipeline status and validation
#   make db              Build the DuckDB database from raw data in 1_data/
#   make analyses        Run all analysis scripts in 3_analyses/
#   make render d=<dir>  Render a specific deliverable in 4_output/<dir>
#   make outputs         Render all deliverables in 4_output/
#   make all             Run the full pipeline: db → analyses → outputs
#   make clean           Remove generated files (DuckDB, JSONs, figures, PDFs)
#   make skeleton-sync msg="..."  Commit + push skeleton improvements
# ============================================================================

# Auto-detect .venv: use it if it exists, otherwise fall back to python3
ifneq (,$(wildcard .venv/bin/python))
    PYTHON ?= .venv/bin/python
else
    PYTHON ?= python3
endif

# Create virtual environment and install dependencies
venv:
	@if [ -d ".venv" ]; then \
		echo "⚠ .venv already exists. To recreate, run: rm -rf .venv && make venv"; \
	else \
		echo "▶ Creating virtual environment..."; \
		python3 -m venv .venv; \
		.venv/bin/pip install --upgrade pip; \
		if [ -f "requirements.txt" ]; then \
			echo "▶ Installing dependencies from requirements.txt..."; \
			.venv/bin/pip install -r requirements.txt; \
		fi; \
		echo ""; \
		echo "✓ Virtual environment created at .venv/"; \
		echo ""; \
		echo "  All 'make' commands will now automatically use .venv/bin/python."; \
		echo ""; \
		echo "  To activate in your shell (optional, for interactive use):"; \
		echo "    source .venv/bin/activate"; \
		echo ""; \
	fi

# Show pipeline status and validation
status:
	@$(PYTHON) status.py

# Build the DuckDB database
db:
	$(PYTHON) 2_db/build_db.py

# Run every run.py found in 3_analyses/ subfolders
analyses:
	@for dir in 3_analyses/*/; do \
		if [ -f "$$dir/run.py" ]; then \
			echo "▶ Running $$dir"; \
			(cd "$$dir" && $(PYTHON) run.py); \
		fi; \
	done

# Render a specific deliverable: make render d=2026-02-18-short-report
# Supports both Quarto (.qmd) and data exports (export.py)
render:
	@if [ -z "$(d)" ]; then \
		echo "✗ Usage: make render d=<deliverable-folder>"; \
		echo "  Example: make render d=2026-02-18-short-report"; \
		echo "  Available:"; \
		ls -d 4_output/*/  2>/dev/null | grep -v templates | grep -v __pycache__ | sed 's|4_output/||;s|/||' | sed 's/^/    /'; \
		exit 1; \
	fi
	@if [ ! -d "4_output/$(d)" ]; then \
		echo "✗ Directory 4_output/$(d) not found."; \
		exit 1; \
	fi
	@found=0; \
	for qmd in 4_output/$(d)/*.qmd; do \
		if [ -f "$$qmd" ]; then \
			echo "▶ Rendering $$qmd"; \
			(cd "4_output/$(d)" && quarto render $$(basename "$$qmd")); \
			found=1; \
		fi; \
	done; \
	if [ -f "4_output/$(d)/export.py" ]; then \
		echo "▶ Running 4_output/$(d)/export.py"; \
		(cd "4_output/$(d)" && $(PYTHON) export.py); \
		found=1; \
	fi; \
	if [ $$found -eq 0 ]; then \
		echo "⚠ No .qmd or export.py found in 4_output/$(d)"; \
	fi

# Render all deliverables (every subfolder in 4_output/ except templates/)
# Supports both Quarto (.qmd) and data exports (export.py)
outputs:
	@for dir in 4_output/*/; do \
		case "$$dir" in \
			*templates/*|*__pycache__/*) continue ;; \
		esac; \
		for qmd in $$dir*.qmd; do \
			if [ -f "$$qmd" ]; then \
				echo "▶ Rendering $$qmd"; \
				(cd "$$dir" && quarto render $$(basename "$$qmd")); \
			fi; \
		done; \
		if [ -f "$$dir/export.py" ]; then \
			echo "▶ Running $$dir/export.py"; \
			(cd "$$dir" && $(PYTHON) export.py); \
		fi; \
	done

# Full pipeline
all: db analyses outputs

# Clean generated files
clean:
	rm -f 2_db/project.duckdb 2_db/*.wal
	find 3_analyses -name "results.json" -delete
	find 3_analyses -type d -name "figures" -exec rm -rf {} + 2>/dev/null || true
	find 4_output -name "*.pdf" -not -path "*/templates/*" -delete
	find 4_output -name "*.html" -not -path "*/templates/*" -delete
	find 4_output -name "*.tex" -not -path "*/templates/*" -not -name "titlepage.tex" -delete
	find 4_output -name "*.log" -not -path "*/templates/*" -delete
	find 4_output -type d -name "*_files" -exec rm -rf {} + 2>/dev/null || true
	@# Clean data export outputs (but not the export.py scripts or README.md)
	find 4_output -name "*.csv" -not -path "*/templates/*" -delete 2>/dev/null || true
	find 4_output -name "*.xlsx" -not -path "*/templates/*" -delete 2>/dev/null || true
	find 4_output -name "export.json" -not -path "*/templates/*" -delete 2>/dev/null || true

# Commit skeleton changes and push to the skeleton remote automatically.
# Usage: make skeleton-sync msg="improve Makefile with clean target"
# The changed files must be staged (git add) before running this.
skeleton-sync:
	@if [ -z "$(msg)" ]; then \
		echo "✗ Usage: make skeleton-sync msg=\"description of the change\""; \
		exit 1; \
	fi
	git commit -m "[skeleton] $(msg)"
	@if git remote get-url skeleton >/dev/null 2>&1; then \
		HASH=$$(git rev-parse HEAD) && \
		git fetch skeleton && \
		git checkout -b _skeleton_backport skeleton/main && \
		if git cherry-pick $$HASH; then \
			git push skeleton _skeleton_backport:main && \
			echo "✓ Pushed to skeleton remote"; \
		else \
			echo "✗ Cherry-pick conflict. Resolve manually:"; \
			echo "  git cherry-pick --abort  (to cancel)"; \
			echo "  git cherry-pick --continue  (after resolving)"; \
			git cherry-pick --abort; \
		fi; \
		git checkout - && \
		git branch -D _skeleton_backport 2>/dev/null || true; \
	else \
		echo "⚠ No 'skeleton' remote found. Committed locally with [skeleton] prefix."; \
		echo "  To set up: git remote add skeleton <skeleton-repo-url>"; \
	fi

.PHONY: venv status db analyses render outputs all clean skeleton-sync

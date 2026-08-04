---
name: data-analysis-collect
description: Use when raw data files exist in 1_data/original/ but are not yet documented in 1_data/original/sources.yaml.
---

# data-analysis-collect

Collect raw data files and document them in `1_data/original/sources.yaml`.

## Responsibility

- Ensure every file in `1_data/original/` has a matching entry in `1_data/original/sources.yaml`.
- Ensure every entry in `sources.yaml` corresponds to a file on disk.
- Help the user write accurate provenance metadata for each file.
- Flag confidential files and remind the user to add them to `.gitignore`.

## How to use

1. Run the collect script from the project root:

   ```bash
   python <path-to-skills>/data-analysis-collect/collect.py
   ```

2. Read the output. It will report:
   - Undocumented files on disk
   - Documented files missing on disk
   - Confidential files
   - Suggested `sources.yaml` entries for undocumented files
3. Ask the user for the missing metadata for each undocumented file.
4. Rewrite `1_data/original/sources.yaml` with complete entries.
5. Re-run `collect.py` to confirm all files are documented.

## `sources.yaml` schema

Use the skeleton's schema:

```yaml
- file: survey_results.csv
  origin: "EPFL internal survey platform"
  url: "https://example.com/export"
  accessed: 2026-01-15
  description: "Raw survey responses, 1200 respondents, 25 questions"
  format: CSV
  encoding: utf-8
  confidential: false
  notes: "Exported with all optional fields included"
```

Only `file:` is strictly required. All other fields are optional but encouraged.

## Rules

- Never modify files in `1_data/original/`.
- Do not fetch or download remote data unless the user explicitly asks.
- Flag confidential files in `sources.yaml` with `confidential: true`.
- Remind the user to add confidential files to `.gitignore`.
- Do not proceed to `data-analysis-build-db` until data is fully documented.

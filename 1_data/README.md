# Stage 1: Data Collection

## Goal

Gather the raw data needed for the project and document its provenance.

## What Goes Here

- Raw input files such as CSV, JSON, XLSX, and PDF
- `sources.yaml` with one entry per source
- Optional fetch or download scripts for APIs and large remote files

## Rules

- Never modify raw data after collection. All transformations happen in `2_db/`.
- Every file must be documented in `sources.yaml`.
- If data is confidential, add it to both `.gitignore` and `.cursorignore`.
- If data is too large or remote, document how to obtain it and add a download script.

## Done When

Every planned source has a file or fetch script and a matching entry in `sources.yaml`.

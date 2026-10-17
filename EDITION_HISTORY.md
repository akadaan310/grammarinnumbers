# Edition History — Grammar in Numbers

## Edition 1.0 — 2026-10-17 (first complete edition)

**Branch:** `research/the-number-edition-1-completion`, from `ccr-95868bff-zq7rqu` at `7c8dc9429ee53927a5a7b6f099665d8571253717`. Content version and print-edition hash: `book/site/downloads/pdf.json`.

- **Completed:** Chapters 33 (Euclid), 34 (exponentiation), 35 (primality), 36 (cost models), 37 (measured complexity), 38 (GiN → CGT), 39 (interfaces), 40 (SDK), 41 (findings), 42 (open problems); Appendices A (notation), B (reproducibility), C (ledger guide); website pages *status* and *edition*.
- **New ledger entries:** GIN-DEF-097; GIN-HIST-016 – 019; GIN-PROP-076; GIN-OBS-021, 022; GIN-NEG-024, 025; decisions GIN-D-016 – 019; corrections C-004, C-005 (RESULTS §L).
- **Defects fixed:** (1) INT_MIN / −1 on wrapping 32-bit machines was classified `different-selection` instead of `wrapped` (SDK and laboratory; regression test). (2) A skipped EXP-014 overwrote recorded emulation results. (3) `check_theorems_edition1.py` was not run by `run_all.sh`. (4) The print colophon implied an online edition at an address that returns 404; links to `/books/…` addresses that do not exist were replaced by the live CGT site or the repository.
- **Author name:** the public name is **Abed Kadan** (decision GIN-D-017). Alias: earlier records use *Abed Kadaan*; they are not rewritten.
- **Archived:** the milestone-0.1 PDF moved unchanged from the repository root to `archive/Grammar-in-Numbers-milestone-0.1.pdf` (sha256 `d51b3f285135b839eb70148ae3fb47df3b7f8c0d2a7475eab2800ce0eb0de20f`, 53 pages).
- **Verification:** `AUDIT_2026-10.md`, and the release record in `PUBLICATION_STATUS.md`.

## Pre-1.0 drafts — 2026-10-09 (branch `ccr-95868bff-zq7rqu`, 7 commits)

Book pipeline (`book/tools/build.mjs`, KaTeX at build time, integrity checks), SDK 1.0 with contracts and CLI, browser laboratory core with SDK fixtures, Chapters 1–32, experiments EXP-013 to EXP-015. No PDF of the chapter manuscript was produced.

## Milestone 0.1 — 2026-10-08 (branch `claude/happy-newton-r2t17c`)

Research ledger, SDK (46 tests), experiments EXP-001 to EXP-012, and a 53-page PDF compiled from the ledger documents (not the chapter manuscript).

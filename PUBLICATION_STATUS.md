# Publication Status — Grammar in Numbers, Edition 1.0

**Status:** first complete edition of a **research monograph** by Abed Kadan. **Not peer reviewed.** No institutional affiliation or endorsement is claimed. Developed with Claude (AI research assistant), who is not an author; contributions are recorded in `PROVENANCE.md`.
**Branch:** `research/the-number-edition-1-completion` (from `ccr-95868bff-zq7rqu` @ `7c8dc94`). The default branch `claude/happy-newton-r2t17c` is unchanged and awaits a reviewed pull request.
**Deployment:** none. The website builds and is tested locally; it is not deployed by this work, and no online address is claimed for it.

## Release gate (evaluated 2026-10-17)

| gate | result | evidence |
|---|---|---|
| 42 planned chapters present and substantive | **pass** — 42/42 | `book/content/chapters/01…42`; strict build |
| 3 planned appendices | **pass** — 3/3 | `a-notation`, `b-reproducibility`, `c-ledger-guide` |
| strict website build (LaTeX, references, citations, ledger ids, objectives/exercises/summaries, placeholders) | **pass** — 45 files, 154 formal items, 537 labels, 73/73 references cited | `npm run build` |
| executed examples reproduce printed output | **pass** — 121/121 | `npm run examples` |
| laboratory vs SDK fixtures; binary64 rounding vs host | **pass** — 4/4 tests | `npm test` |
| internal links | **pass** — 0 broken | `node tools/linkcheck.mjs` |
| SDK tests | **pass** — 75/75 (74 at the audit, plus the C-006 regression test) | `python3 -m unittest discover -s sdk/tests` |
| experiments EXP-001 – 015 re-run | **pass** — counted fields identical to the recorded results except the explained changes below | `sh experiments/run_all.sh`; `audit/logs/` |
| theorem checks | **pass** — 21 + 12 | `check_theorems.py`, `check_theorems_edition1.py` |
| print edition regenerated from canonical sources | **pass** — see `book/site/downloads/pdf.json` (pages, SHA-256, content version) | `npm run pdf` release checks: width, fonts embedded, chapter titles, no U+FFFD, content version |
| visual print audit | **pass, with notes** — sample pages inspected (title, contents, Ch. 2, 9, 18, 37, 39, results index, bibliography); fixed: 4 elements wider than the text block, broken ledger ids in narrow columns, 37 duplicated cross-reference words ("Proposition Proposition"), lab-box label implying an online edition | `AUDIT_2026-10.md` |
| research lane *The Number* kept separate | **pass** — own identifiers, runner, results and tests (`sh research/the-number/run_all.sh`: 10 tests, NUM-EXP-001 – 004 deterministic); not in `experiments/run_all.sh`; no chapter renumbered | `research/the-number/` |
| research-lane laboratories vs Python library | **pass** — 5/5 fixture tests | `npm test` (`tests/num.test.mjs`) |
| changelog and known issues | **pass** | `EDITION_HISTORY.md`, below |

### Explained changes in re-run results
- `exp003.json`: three cells of the meaning table (`(-2147483647 - 1) / -1` in the int32 AArch64, Java and RISC-V domains) now carry the flag `overflow` — the intended effect of correction C-004.
- `checksedition1.json`: four new checks (GIN-PROP-076, GIN-HIST-018, GIN-NEG-024, GIN-HIST-019).
- `exp014.json`: reproduced under qemu-user 8.2.2 (emulation, not hardware).

## Known issues

1. Not peer reviewed; the novelty of GIN-PROP-006 and of the pair form of GIN-THM-006 is unverified (GIN-OPEN-005).
2. Machine measurements: one x86-64 host, one version per toolchain; AArch64/RISC-V emulated only (GIN-OPEN-012).
3. The AI-only baseline of EXP-013 was not run (GIN-OPEN-013).
4. Wall-clock timings are host-specific and secondary.
5. Code lines in executed examples wrap in print (legible, not typeset).
6. The CGT publication is cited under its published byline "Abed Kadaan" (alias of the author, GIN-D-017).

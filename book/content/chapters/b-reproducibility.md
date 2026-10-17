---
title: "Reproducibility, the SDK, and the Laboratory"
status: implementation
statusnote: The commands, environments and evidence classes behind every executed example, experiment and measurement in the book, with the results of the 2026-10 reproduction audit.
description: How to reproduce every number in the book — the software requirements, the commands, what each experiment needs, the evidence classes (measured, emulated, specified), and the outcome of the clean-room re-run performed in October 2026.
---

## What can be reproduced {#sec:repro-what}

Three kinds of evidence appear in this book, and each can be regenerated from the repository without accounts, keys or paid services:

1. **Executed examples** — every `python run` block is executed at build time by `book/tools/check_examples.py`, and the build fails if the printed output differs from the real output.
2. **Experiments** — `experiments/exp001_…` to `exp015_…` write JSON results under `experiments/results/`; counted fields are deterministic given the recorded seeds, and wall-clock fields (names ending in `_s`) are not.
3. **Theorem checks** — `experiments/check_theorems.py` and `check_theorems_edition1.py` check every "proved here" statement exhaustively on small cases.

## Commands {#sec:repro-commands}

```text
# SDK tests (Python >= 3.10, standard library only)
cd sdk && PYTHONPATH=src python3 -m unittest discover -s tests -v

# every experiment, both theorem checkers, and experiments/results/SUMMARY.md
sh experiments/run_all.sh

# re-run everything into a scratch copy and compare counted fields with the committed results
python3 experiments/verify_reproduction.py

# the book: website, laboratory tests, executed examples, link check, print edition
cd book && npm ci && npm run verify && npm run pdf
```

## What each experiment needs {#sec:repro-needs}

| experiment | needs beyond Python | evidence class |
|---|---|---|
| EXP-001 – 003, 006 – 012, 015 | nothing | computation |
| EXP-004 machine division | gcc; optionally clang, javac/java, rustc, go, node | **measured** on the host |
| EXP-005 IEEE simulator vs hardware | gcc with `fenv.h` | **measured** (x86-64 SSE) |
| EXP-013 execution prediction | gcc, javac/java, rustc, go, node | **measured** |
| EXP-014 AArch64 and RISC-V | clang, lld, qemu-user (`qemu-aarch64`, `qemu-riscv64`) | **emulated**; if the tools are missing the script prints `NOT RUN` and leaves the committed results unchanged |

AArch64 and RISC-V results are emulator results: they test the SDK's models against QEMU's independent implementation of the architectures, not against physical processors (\ledger{GIN-OPEN-012}).

## The 2026-10 reproduction audit {#sec:repro-audit}

In October 2026 the repository was re-run in a clean environment (Linux 6.18 x86-64; Python 3.13.16; Node 22.22.0; gcc 13.3.0; clang 18.1.3; OpenJDK 21; rustc 1.97.0; go 1.24.7; qemu-user 8.2.2). The full record, with logs, is `AUDIT_2026-10.md`. In summary:

- all SDK tests passed;
- the counted fields of every experiment result were identical to the committed ones, including the 80,600-case IEEE comparison and, once QEMU was installed, the emulation results of EXP-014;
- every executed example of the first 32 chapters reproduced its printed output, and every lab fixture matched the browser core;
- two defects of the experiment harness were found and fixed: a skipped experiment overwrote recorded evidence, and one theorem checker was not run by `run_all.sh`;
- while the last ten chapters were written, one defect of the SDK was found and fixed — 32-bit division on wrapping machines did not flag the wraparound of $\mathrm{INT\_MIN}/-1$ (RESULTS §L, correction C-004).

## The laboratory {#sec:repro-lab}

The interactive laboratory on the website runs `book/site/assets/js/gin-core.js`, a JavaScript port of the SDK's evaluator, IEEE rounding and machine models. It is not an independent theory: `npm test` checks that it reproduces the SDK on every fixture exported by `book/tools/export_data.py` (status, layer, displayed value, IEEE flags, and the machine–mathematics relation), and that its binary64 rounding matches the host's arithmetic on 8,000 random operations (\ledger{GIN-D-015}). A disagreement fails the build.

## The print edition {#sec:repro-print}

`npm run pdf` renders the same canonical sources as the website (`dist/print.html`) to PDF with headless Chromium and refuses to publish if any element is wider than the printed text block, any chapter title is missing from the extracted text, any glyph failed to map, any font is not embedded, or the content version printed in the PDF differs from the sources'. The published file, its SHA-256 and page count are recorded in `book/site/downloads/pdf.json`.

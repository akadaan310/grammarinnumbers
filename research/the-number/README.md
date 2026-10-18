# THE NUMBER — research lane (charter)

*Working title: THE NUMBER — From Distinction to Computation.* This is a provisional reader-facing title. The repository, the SDK (`ginsdk`) and the series (*Grammar in Numbers*, in the *Computational Grammar Theory* lineage) are **not** renamed (GIN-D-018).

**Question.** What must be fixed before two numerical systems can be said to denote "the same number", and where exactly does that sameness break? This covers notations, data types, machines and evaluators.

**Scope and rules**
- The lane is separate from the edition. Its identifiers are `NUM-*`, and its results are not claims of *Grammar in Numbers* 1.0 unless they are promoted through the ledger.
- Every item carries a label: definition, classical, proved here, reinterpretation, hypothesis, observation, counterexample, or NOT RUN. "Proved here" never means "new".
- No claims of novelty, priority, uniqueness or first-ness. No claim that any script or tradition is uniquely capable of something. Comparators are mandatory.
- Python standard library only, plus optional `node` for the JavaScript probes. The CGT repository is used read-only, as a source of concepts, and no CGT code is copied.
- Results are deterministic JSON files. A run that cannot execute records `NOT RUN` and how to replicate it.

**Contents**

| file | what it holds |
|---|---|
| `FOUNDATIONS.md` | the schema 𝒩 = (D, Σ, L, ⟦·⟧, 𝒪, ℛ, C), the translation obligations O1–O5, the seven layers, and every NUM item with its evidence |
| `FALSIFICATION_MATRIX.md` | each hypothesis with its prediction, falsifier, test, result and status |
| `INTEGRATION_PLAN.md` | how the lane could enter the publication without renumbering anything (Phase 3 proposal), and the title decision |
| `numlab/` | the library: numeration systems, translation checks, converse fibers, layouts and the restricted bidi model |
| `experiments/num_exp001..004_*.py` | NUM-EXP-001 zero census · NUM-EXP-002 translation · NUM-EXP-003 spatial grammars · NUM-EXP-004 converse fibers |
| `results/` | JSON results and `run_all.log` |
| `tests/` | the unit tests for `numlab` |

**Reproduce:** `sh research/the-number/run_all.sh`

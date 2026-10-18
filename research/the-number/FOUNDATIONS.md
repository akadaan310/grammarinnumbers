# THE NUMBER — Foundations (working draft, research lane)

*From Distinction to Computation* · lane identifiers `NUM-*` · status: **research in progress, not part of the claims of the edition** (GIN-D-018)

This document defines the objects of the lane, states its hypotheses, and gives the executable examples, results and model failures that were obtained. Each item has one of these labels:

| label | meaning |
|---|---|
| **definition** (`NUM-DEF`) | a modelling choice. It cannot be true or false, only useful or not. |
| **classical** (`NUM-HIST`) | a known result, restated with a source. |
| **proved here** (`NUM-PROP`) | a proof written in this lane and checked exhaustively on small cases. This label does **not** mean the result is new. Every such item here is elementary and probably folklore. |
| **reinterpretation** (`NUM-REI`) | a reading of known material in the lane's vocabulary. |
| **hypothesis** (`NUM-HYP`) | a claim with a stated falsifier. |
| **observation** (`NUM-OBS`) | a measured software or data result, together with the environment it was measured in. |
| **counterexample** (`NUM-NEG`) | a concrete case that refutes a plausible general statement. |
| **NOT RUN** | could not be executed here. Replication steps are given. |

The lane makes no claim of novelty, priority, new theorem, new algorithm, new complexity bound, or physical-hardware confirmation. It also never says that numbers arise from "nothing". Its starting point is the act of *distinguishing*, which is a stated assumption and not a derivation (§2, layer 1).

---

## 1. The substrate schema

**NUM-DEF-001 (substrate)** — *definition.*
A numerical substrate is a tuple

  𝒩 = (D, Σ, L, ⟦·⟧, 𝒪, ℛ, C)

with these components:

- **D** — a carrier of values (for example ℕ, ℤ, ℤ/n, the binary64 data, or SQL values including NULL).
- **Σ** — an alphabet of marks (digits, signs, glyphs, or placed marks; see §5).
- **L ⊆ Σ\*** — the *admissible* words or layouts. In 2-D notations, L is a set of layouts.
- **⟦·⟧ : L ⇀ D** — a partial semantics.
- **𝒪** — partial operations on D, each with an arity.
- **ℛ** — the converse relations. For an operation ⊙, Sol(a, b) = {c : b ⊙ c = a} (GIN-DEF-015).
- **C** — a cost model on words and operations, with its unit stated (GIN-DEF-097).

This is a schema for *stating* what must be fixed before two systems are compared. It is not a theorem, and it does not claim that every numerical practice fits it. Code: `numlab/schema.py`.

**NUM-DEF-002 (numeration system)** — *definition.*
A numeration system is the part (Σ, L, ⟦·⟧) of a substrate together with an encoder enc : D ⇀ L that satisfies ⟦enc(v)⟧ = v wherever enc is defined.

Code: `numlab/systems.py` implements the following, all checked by round trips in `tests/test_numlab.py`:
- standard base b, with and without leading zeros;
- bijective base b;
- balanced ternary;
- negative base;
- sign–magnitude;
- two's complement of width w;
- factoradic;
- Zeckendorf, and unconstrained Fibonacci;
- Roman, in strict and lax forms.

**NUM-DEF-003 (representation fiber)** — *definition.*
For v ∈ D, the fiber of v is ⟦·⟧⁻¹(v) ∩ L. A system is *unique* on a length bound when every fiber of a value reached within that bound has size 1.

**NUM-DEF-004 (translation and its obligations)** — *definition.*
A translation 𝒩₁ → 𝒩₂ is a pair (t, h), where t : L₁ ⇀ L₂ rewrites words and h : D₁ → D₂ maps values. Its obligations are:

| | obligation | statement (on the stated sample) |
|---|---|---|
| O1 | value preservation | ⟦t(w)⟧₂ = h(⟦w⟧₁), and t(w) ∈ L₂ |
| O2 | commutation | h(x ⊙₁ y) = h(x) ⊙₂ h(y), wherever both sides are defined |
| O3 | converse-class preservation | class(Sol₁(a, b)) = class(Sol₂(h a, h b)), where class ∈ {none, unique, many} |
| O4 | cost class | the cost ratio C₂(t(w)) / C₁(w) is reported, and its growth is classified |
| O5 | transformation behaviour | t ∘ f₁ = f₂ ∘ t, for word transformations f such as reversal, rotation, transposition, layout change and base change |

An obligation that fails is recorded as a *model failure*, together with an example (`check_translation` in `numlab/schema.py`). The obligations are independent: NUM-PROP-001 shows O3 holding while O2 fails.

**NUM-DEF-005 (converse profile)** — *definition.*
For a finite algebra A and an operation ⊙, the converse profile is the triple

  (#none, #unique, #many)

over all pairs (a, b) ∈ A².

**NUM-DEF-006 (totalization)** — *definition.*
A totalization replaces a converse problem with a total function a ⊘ b. Where the problem has a unique solution, a ⊘ b is that solution. Elsewhere it is a selected element or a default (compare the "totalized" relation of GIN-DEF-081; code: `numlab.fibers.totalize`).

## 2. The seven substrate layers

Each layer lists its formal objects, signature, observables, allowed transformations, a counterexample, its tests, and its links to GiN and CGT.

### Layer 1 — identity and distinction

- **Objects:** a set X with a family Obs of observables f : X → Y.
- **Signature:** the relation x ≈_Obs y ⟺ ∀f ∈ Obs, f(x) = f(y).
- **Observables:** equality tests, hashing, printing, sign extraction, and type.
- **Allowed transformations:** those that preserve ≈_Obs.

**NUM-DEF-010 (distinction relative to observables)** — *definition.*
Two things are *the same number* only relative to a stated set of observables. The equality predicate a substrate provides (`==`, `===`, SQL `=`) is one observable among several.

**NUM-DEF-011 (substitutivity failure)** — *definition.*
A substitutivity failure is a pair x, y with eq(x, y) = true but f(x) ≠ f(y) for some observable f.

**Counterexample:** +0.0 == −0.0, yet atan2(+0.0, −1) = π while atan2(−0.0, −1) = −π (NUM-OBS-001).

- **Tests:** NUM-EXP-001.
- **Links:** GiN typing layer (GIN-D-006); CGT's distinction between a word and its address.

### Layer 2 — state and domain

- **Objects:** the carrier D, a definedness predicate, and the "special" data: NaN, ±∞, NULL, None, undefined.
- **Observables:** membership; whether an operation is defined at a point.
- **Allowed transformations:** extension (D ⊂ D′), quotient (D → D/~), and restriction.

**NUM-DEF-020 (zero, empty, absent)** — *definition.*
Three roles are kept apart:
- a **numeric zero**, an additive identity in D;
- an **empty structure**, the empty word, set or tuple, whose size is 0;
- an **absence marker**, a datum in D that stands for "no value": NULL, None, or JS null/undefined.

**NUM-HYP-001** treats them as observably distinct (§4).

- **Counterexample to collapsing them:** SQLite returns SUM over an empty set = NULL, while TOTAL over the same set = 0.0 (NUM-OBS-002).
- **Links:** GiN zero as the empty numeral (GIN-PROP-002) and the null pair (GIN-THM-006).

### Layer 3 — transition and operation

- **Objects:** the operations 𝒪 and the converse relations ℛ.
- **Observables:** the converse class none / unique / many, and the converse profile.
- **Allowed transformations:** homomorphisms, embeddings and quotients.
- **Counterexample:** the profile is not a complete invariant (NUM-NEG-001).
- **Tests:** NUM-EXP-004.
- **Links:** GiN converse admissibility (GIN-THM-001/007) and repairs (Chapter 18).

### Layer 4 — temporal and historical

- **Objects:** sequences of states (traces) and the order in which marks are produced or read.
- **Observables:** step counts and read order.
- **Allowed transformations:** re-association, and reordering when it is commutative.
- **Counterexample:** reversing the read order preserves value only for palindromes (NUM-PROP-002). Reversal also does not commute with base change (NUM-NEG-002).
- **Links:** GiN numerals as programs x ↦ bx + d (GIN-PROP-002); GiN re-association (GIN-CONJ-001); CGT's rewriting traces.

This lane makes no historical-chronology claims. Its "temporal" layer is read order and evaluation order only.

### Layer 5 — topology and geometry of representation

- **Objects:** layouts, meaning finite sets of placed marks (glyph, x, y, size, orientation), together with a read-order map ρ : layouts → structured words (NUM-DEF-030).
- **Observables:** spatial relations, including left/right order, baseline versus raised, vertical stacking and orientation.
- **Allowed transformations:** translation of the whole layout preserves value. Mirroring, rotation and change of reading direction may or may not preserve it.

**NUM-DEF-030 (factored semantics)** — *definition.*
The semantics factors as ⟦·⟧ = ⟦·⟧_word ∘ ρ.

**NUM-DEF-031 (channel independence)** — *definition.*
Two spatial relations R₁ and R₂ are *independent channels* of a notation when, with either one held fixed, varying the other changes the value.

- **Tests:** NUM-EXP-003.
- **Links:** CGT tree and heap addresses, the 2-D reading of a heap; GiN heap ↔ bijective binary (GIN-PROP-006).

### Layer 6 — computational and machine

- **Objects:** the GiN machine models, the IEEE simulator, and evaluators in other languages (Python, JS, SQLite).
- **Observables:** the outcome records `gin-inspect/1` and the parser results.
- **Allowed transformations:** compilation, and translation between evaluators.
- **Counterexample:** the same numeral string has a different value in each parser (NUM-OBS-004).
- **Links:** GiN Chapters 23–26 and 39 (the machine–mathematics relation, GIN-DEF-081).

### Layer 7 — meta-substrate and translation

- **Objects:** translations (t, h) and their obligations O1–O5 (NUM-DEF-004).
- **Observables:** the reports of which obligations hold or fail.
- **Allowed transformations:** composition of translations. Obligations O1 and O2 compose. O3 composes only when each step preserves classes.
- **Counterexample:** the strict Roman system has no word for 0, so decimal → Roman fails O1 at 0 (NUM-NEG-003).
- **Links:** GiN contracts (`gin-contracts/1`); CGT's translations between grammars, used read-only as a source of the concept.

## 3. Classical results used

- **NUM-HIST-001** (*classical*). Homomorphisms preserve positive existential formulas. In particular, if Sol_A(a, b) ≠ ∅ then Sol_B(h a, h b) ≠ ∅: if c is a solution, h(c) is one.
  - Source: Hodges, *Model Theory*, CUP 1993, Encyclopedia of Mathematics and its Applications 42. The bibliographic metadata was verified; the exact section and numbering were not checked.
- **NUM-HIST-002** (*classical*). Injective homomorphisms map distinct solutions to distinct solutions. Hence |Sol_B(h a, h b)| ≥ |Sol_A(a, b)|.
  - Same source.
- **NUM-HIST-003** (*classical*). The congruence b·c ≡ a (mod n) has exactly gcd(b, n) solutions when gcd(b, n) divides a, and none otherwise.
  - Checked exhaustively for n ≤ 12 in `tests/test_numlab.py`.
- **NUM-HIST-004** (*classical*). Uniqueness of representation holds for:
  - standard base b without leading zeros;
  - bijective base b;
  - balanced ternary;
  - negative base;
  - factoradic;
  - Zeckendorf representations (no two adjacent Fibonacci terms).
  - Sources: Knuth, TAOCP vol. 2, §4.1 (`knuth1997` in the edition bibliography). The Zeckendorf case is due to Lekkerkerker and to Zeckendorf; it is cited here through Knuth and was not re-verified at the primary source.
- **NUM-HIST-005** (*classical*). Radix conversion:
  - Horner's rule from base 10 to binary costs Θ(n²) word operations on n digits.
  - Divide and conquer costs O(M(n) log n), where M(n) is the cost of multiplication.
  - Conversion between bases that are powers of 2 is linear.
  - Source: Knuth, TAOCP vol. 2, §4.4.

## 4. Hypotheses, propositions and results

### NUM-HYP-001 — zero, empty and absent are observably distinct
**Prediction.** In every substrate examined, some observable separates the three roles of NUM-DEF-020.
**Falsifier.** A substrate in which no available observable separates two of the roles.

**Result (NUM-EXP-001):** *supported in 3 of 3 substrates* (Python 3.13, SQLite 3.45.1, Node 22). This is not a universal claim.

- **NUM-OBS-001 (Python).**
  - Under `==` there are 8 equality classes among 15 zero-like objects.
  - The objects 0, 0.0, −0.0, False, Fraction(0), 0j, Decimal(0) and Decimal('−0') all fall in one class.
  - Inserting the 7 numeric zeros as dict keys leaves **one** key.
  - 4 substitutivity failures were found:
    - copysign(1, x) and atan2(x, −1) differ between +0.0 and −0.0;
    - repr(0) ≠ repr(False);
    - the type of x // 1 differs between 0 and 0.0.
  - NaN ≠ NaN, yet `nan in [nan]` is True for the same object, because membership tests identity before equality.
- **NUM-OBS-002 (SQLite 3.45.1).**
  - NULL = NULL gives NULL.
  - SUM over an empty table gives NULL, while TOTAL gives 0.0 and COUNT gives 0.
  - 1/0 gives NULL.
  - CAST('abc' AS INTEGER) gives 0.
- **NUM-OBS-003 (Node 22).**
  - `null >= 0` is true, while `null == 0` and `null > 0` are both false. So `>=` is not "> or ==" on these values.
  - `[] == 0` is true.
  - `Object.is(0, −0)` is false, but a Map treats 0 and −0 as one key.

### NUM-HYP-002 — uniqueness is a property of the language L, not of the digits
**Prediction.** For the same alphabet and semantics, strict and lax languages differ in uniqueness.
**Falsifier.** A pair of systems with the same (Σ, ⟦·⟧) whose uniqueness does not depend on the choice of L.

**Result (NUM-EXP-002):** *supported*. This is essentially classical (NUM-HIST-004), restated as a measurement.

| system | words enumerated (length bound) | unique? | largest fiber / example |
|---|---|---|---|
| base 10, no leading zeros | ≤ 4 | yes | — |
| base 10, leading zeros allowed | ≤ 4 | no | value 0: ε, 0, 00, 000, 0000 |
| sign–magnitude base 2 | ≤ 9 | no | value 0: "+" and "−" |
| Zeckendorf | ≤ 14 | yes | — |
| Fibonacci, unconstrained | ≤ 14 | no | up to 26 words per value (715 has 26) |
| Roman, strict | ≤ 7 | yes | — |
| Roman, lax subtractive reading | ≤ 5 | no | 1000 = M = DD = IIM = IMI = … |
| bijective, balanced ternary, negabase, two's complement, factoradic | various | yes | — |

### NUM-HYP-003 — two spatial channels can carry independent information
**Prediction.** There are notations in which the value depends non-trivially on a horizontal relation and on a vertical or orientation relation, each with the other held fixed (NUM-DEF-031).
**Falsifier.** For every notation examined, one channel turns out to be determined by the other, or to have no effect on the value.
The hypothesis is about notations in general. **It does not claim that Arabic notation is uniquely capable of this.** The Arabic-Indic case study is placed next to non-Arabic comparators specifically to test that question.

**Result (NUM-EXP-003):** *supported for the notations examined*. The uniqueness reading was tested and rejected.

- **Constructed 2-D grammar.**
  - The marks "2" and "3" give 23 on the baseline, 2³ = 8 with the 3 raised, and "2 in base 3" = 2 with the 3 lowered.
  - Swapping the marks gives 32, 9, and undefined.
  - Both channels change the value. Together they give 5 distinct values, against 2 for the horizontal channel alone and 3 for the vertical channel alone.
- **Maya-style vertical place value** (comparator).
  - The vertical position carries the place.
  - The horizontal bars and dots inside a place carry an additive count.
  - Round trips succeed for all n < 8000 (pure base 20) and n < 7200 (calendrical variant).
- **Counting-rod-style orientation** (comparator).
  - Without a zero mark, and with all rods in one orientation, 819 of the 7,380 renderings of 1…9999 are ambiguous; the largest fiber is 6, for example 1 = 10 = 100 = 1000.
  - Alternating the orientation by place reduces this to 99 ambiguous renderings, with largest fiber 3.
  - A zero mark removes the ambiguity entirely.
  - So orientation carries place-parity information that is independent of left/right order.
- **Arabic-Indic case study** (NUM-OBS-004/005).
  - In right-to-left text, a run of digits keeps its logical, most-significant-first order and is displayed left to right. The letters around it are reversed, and two numbers in one line appear in right-to-left sequence relative to each other.
  - The same behaviour holds for **Hebrew text with European digits**. It is a property of the Unicode bidirectional algorithm, not of Arabic numerals.
  - The model in `numlab.layout.display_order` is a *restricted* re-implementation of UAX #9, checked only on hand-derived cases. It is not conformance-tested.

**Sources for the comparators:**
- Chrisomalis, *Numerical Notation: A Comparative History*, CUP 2010. Metadata verified. The book is a secondary source for the Maya and counting-rod structures; page references were not checked.
- Unicode Standard Annex #9, *Unicode Bidirectional Algorithm*. This is the standard itself; character data are from the Unicode Character Database 15.1.0 as shipped with Python.

- **NUM-OBS-004 (one numeral, five substrates).** The numeral "34" was written in five digit sets: ASCII, Arabic-Indic (U+0660…), Extended Arabic-Indic (U+06F0…), Devanagari and Fullwidth.
  - Python `int()` reads all five as 34, and also reads the **mixed-script** "٣۴" as 34.
  - JavaScript `Number()` and `parseInt()` return NaN for every non-ASCII set.
  - SQLite `CAST(… AS INTEGER)` returns **0** for every non-ASCII set. This is a silent change of value: O1 fails without any signal.
  - The GiN SDK accepted every non-ASCII set until this experiment, while the GiN laboratory core rejected them. That was a real disagreement between SDK and lab, outside the fixture set. It is now fixed so that the SDK accepts ASCII digits only, as the lab does; see correction C-006 in `RESULTS.md` §L and the regression test `test_numerals_are_ascii_digits`.
- **NUM-OBS-005 (bidi classes, UCD 15.1.0).**
  - Arabic-Indic digits have class **AN**.
  - Extended Arabic-Indic digits have class **EN**, like European digits and Fullwidth digits.
  - Devanagari digits have class **L**.
  - So "Arabic digits" is not one bidi category.

### NUM-HYP-004 — converse classes move along maps only in the directions NUM-HIST-001/002 allow
**Prediction.**
- A homomorphism never sends a solvable problem to an unsolvable one.
- An injective homomorphism never sends "many" to "unique" or "none".
- Every other change does occur somewhere.

**Falsifier.** A violation of either of the first two predictions. That would mean a bug or a mis-specified map, because the theorems themselves are classical.

**Result (NUM-EXP-004):** **0 violations** across all 20 homomorphism/operation cases examined (21 cases including one non-homomorphism), and every non-forbidden direction occurs:

- Z/12 → Z/4 (×):
  - none → unique: 16 cases (e.g. 3c = 1);
  - none → many: 6 cases;
  - many → unique: 8 cases (e.g. 3c = 3).
- Z → Z/n on a window (×): none → unique, none → many and unique → many all occur.
- Z → Q (×): 436 cases go none → unique (e.g. 2c = 1).
- Monoids sat{0..7} → sat{0..3} and max{0..7} → max{0..3}: none → many and unique → many.
- A *non*-homomorphism, x ↦ 3x from Z/4 to Z/12 under ×, sends unique → many in 8 cases. That direction is forbidden only for homomorphisms.
- Isomorphisms (the CRT map Z/6 → Z/2 × Z/3, and GF(2) ⊂ GF(4) on its image) change nothing.

*This is a confirmation of classical theory on small cases, not a new result.*

**NUM-PROP-001 (sign extension preserves converse classes of multiplication)** — *proved here, elementary, probably folklore.*
Take m < n, and let a, b be integers in [−2^{m−1}, 2^{m−1}). Then b·c ≡ a has the same class (none, unique or many) modulo 2^m as modulo 2^n.

*Proof.*
- **Case b ≠ 0.** Here |b| < 2^{m−1}, so the 2-adic valuation v of b is at most m − 2. Then gcd(b, 2^m) = gcd(b, 2^n) = 2^v. By NUM-HIST-003 the congruence is solvable in either modulus iff 2^v divides a, a condition that does not depend on the modulus. When it is solvable, the solution count is 2^v in both moduli. That count is 1 iff b is odd, in both. So the class agrees.
- **Case b = 0.** If a = 0, the solution counts are 2^m and 2^n, both > 1, so the class is "many" in both. If a ≠ 0, then 0 < |a| < 2^{m−1}, so a ≢ 0 in either modulus and there is no solution in both. ∎

- **Check:** exhaustive over all 65,536 pairs for m = 8, n = 16, with 0 class changes (NUM-EXP-002).
- **Why it matters:** the same translation fails O2 in 702 of 2,704 sampled pairs for + and 2,606 for ×. So **O3 does not require O2**, and the obligations must be checked separately (NUM-DEF-004).

**NUM-PROP-002 (reversal and palindromes)** — *proved here, trivial.*
For base-b words of a fixed length with leading zeros allowed, val(reverse w) = val(w) iff w is a palindrome.

*Proof.* val is injective on words of a fixed length (NUM-HIST-004 with padding), and reverse w has the same length as w. ∎

- **Check:** exhaustive for b ∈ {2, 3, 10} at every length up to 10⁶ words.

**NUM-NEG-001 (the profile is not a complete invariant)** — *counterexample.*
sat{0..7} (saturating +) and max{0..7} (max) have the same converse profile, (28, 29, 7). They are not isomorphic: they have 2 and 8 idempotents respectively, and an exhaustive search over bijections confirms it.

**NUM-NEG-002 (reversal does not commute with base change).**
Among n < 10⁴:
- 198 values are fixed by decimal reversal (the decimal palindromes);
- only 18 satisfy rev₁₀(n) = rev₂(n);
- decimal → binary fails O5 for reversal in 51 of 58 admissible cases.

**NUM-NEG-003 (Roman has no zero).**
Decimal → strict Roman fails O1 at exactly 0 and 4000 in the range 0…4000.

**NUM-NEG-004 (O2 failure under sign extension).**
See NUM-PROP-001. For example, h(−128 + −128) = 0 in 8 bits, but h(−128) + h(−128) = −256 in 16 bits.

**NUM-NEG-005 (the layout does not fix the value).**
The same Maya-style layout read under pure base 20 and under the calendrical weights (1, 20, 360, …) gives different values for 7,600 of the 8,000 layouts. For example, the layout of 1000 reads as 920 under the calendrical weights. The semantics ⟦·⟧ is a separate component of 𝒩 from the marks.

**NUM-OBS-006 (conversion cost, classical, reproduced).**
Counted in 32-bit word operations for 64 to 4,096 digits, with log–log slopes taken over the last three sizes:

| method | log–log slope | expected |
|---|---|---|
| Horner's rule, base 10 | 1.995 | Θ(n²) |
| divide and conquer with Karatsuba | 1.618 | about n^1.585 · log n |
| regrouping, base 16 → base 2 | 1.000 | linear |

These are reproductions of NUM-HIST-005, not new results.

**NUM-OBS-007 (totalization hides the class).**
Take the total division that returns the unique solution when there is one, the least solution when there are many, and 0 when there is none. In Z/6, Z/8 and Z/12 it answers 67%, 50% and 67% of the problems with a value that is not a unique solution. It also returns the same 0 for 1 ⊘ 0 (no solution) and for 0 ⊘ 0 (many solutions).

**NUM-OBS-008 (evaluators against exact enumeration).**
On a / b in Z/n, for n ≤ 12 and all residues (650 cases), both `ginsdk.evaluate` and the laboratory core `gin-core.js` agree with exact enumeration in **650 of 650** cases.

## 5. Working thesis (reinterpretation, not a theorem)

**NUM-REI-001.** In computation, "the number" denoted by a written or stored form is best treated as **what survives translation**. It is the class of representations across substrates that are linked by translations satisfying O1–O3, given a stated set of observables (layer 1). Where an obligation fails, the failure has a location (the layer) and a kind (the obligation).

This reinterpretation organizes known facts; it does not produce new mathematics. The lane's results so far confirm classical theory (NUM-HIST-001…005) and record software behaviour (NUM-OBS-001…008). The one structural lesson specific to the framework, that O3 is independent of O2 (NUM-PROP-001), is itself explained by classical number theory.

The falsification matrix is in `FALSIFICATION_MATRIX.md`.

## 6. Not run, and how to replicate

- **Physical hardware.** Nothing in this lane depends on a particular ISA, so there is nothing to run there. Lane results are not hardware claims.
- **A conformant bidi implementation.** NOT RUN. To cross-check `display_order`, run the UAX #9 conformance files `BidiTest.txt` and `BidiCharacterTest.txt` (unicode.org) through an established implementation (ICU, or `fribidi`) and compare on the case-study strings.
- **Other SQL engines and other JS engines.** NOT RUN. Rerun `experiments/num_exp001_zero.py` and `num_exp003_spatial.py` with the probes ported to them.
- **Primary-source checks.** The Zeckendorf/Lekkerkerker originals, page references in Chrisomalis 2010, and the section numbers in Hodges 1993 remain unverified.

## 7. Reproduce

```sh
sh research/the-number/run_all.sh     # 10 tests + NUM-EXP-001..004 (≈ 35 s; node optional)
```

The results are deterministic: two consecutive runs gave identical JSON files. They are written to `research/the-number/results/num_exp00{1..4}.json`.

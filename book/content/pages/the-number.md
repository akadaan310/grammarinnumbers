# THE NUMBER — a research lane

*Working title: THE NUMBER — From Distinction to Computation.* This page belongs to a **separate research lane**. The lane uses its own identifiers (`NUM-*`), and nothing on this page is a claim of *Grammar in Numbers*, first edition. The book's chapters are not renumbered, and the repository, the SDK and the series keep their names. The lane's foundations, its falsification matrix and its results are in the repository under `research/the-number/` ([on GitHub](https://github.com/akadaan310/grammarinnumbers/tree/HEAD/research/the-number)).

The lane asks what must be fixed before two systems — notations, data types, machines, evaluators — can be said to denote "the same number", and where exactly that sameness breaks. Its schema, 𝒩 = (D, Σ, L, ⟦·⟧, 𝒪, ℛ, C), is a modelling definition, not a theorem. Its results so far confirm classical mathematics on small cases and record measured software behaviour. **No new theorem, algorithm or complexity bound is claimed.** Every widget below computes in your browser with `num-core.js`. That file is a second implementation of the lane's Python library, and `npm test` checks it against fixtures exported from that library.

<div class="lab-section">

## Zero, empty, absent {#sec:num-zero}

::: demo num-zero
Text alternative: twenty-eight JavaScript probes about zero, emptiness and absence run in your browser and are compared with the results stored by NUM-EXP-001 under Node 22. Examples include `0 === -0` (true), `Object.is(0, -0)` (false), `null >= 0` (true) while `null == 0` and `null > 0` are both false, and `[] == 0` (true). The stored Python results show 8 equality classes under `==` among 15 zero-like objects. Seven numeric zeros inserted as dictionary keys collapse to a single key. Four cases were found where x == y but some function tells x and y apart, for example +0.0 and −0.0 under atan2. The stored SQLite results show SUM over an empty table returning NULL while TOTAL returns 0.0. Hypothesis NUM-HYP-001 — that zero, empty and absent are observably distinct — is supported in the three substrates examined. It is not claimed to hold universally.
:::

</div>
<div class="lab-section">

## One value, many words {#sec:num-translate}

::: demo num-translate
Text alternative: enter an integer to see its canonical word in fourteen numeration systems: binary, ternary, decimal, hexadecimal, bijective base 2 and base 10, balanced ternary, base −2 and base −10, sign–magnitude, 8-bit two's complement, factoradic, Zeckendorf and strict Roman. For 1994 the strict Roman word is MCMXCIV. A system with no word for the value shows a dash, for example Roman for 0 or for negative numbers. That dash is a failure of the translation obligation O1, value preservation. NUM-EXP-002 measured that uniqueness of the word depends on the language and not on the digits. Allowing leading zeros, two signs on zero, adjacent Fibonacci terms, or the lax subtractive reading of Roman numerals gives values many words; in lax Roman, 1000 = M = DD = IIM = IMI.
:::

</div>
<div class="lab-section">

## Spatial grammar: two channels {#sec:num-spatial}

::: demo num-spatial
Text alternative: two digits are placed side by side. The right digit sits on the baseline, is raised (read as an exponent), or is lowered (read as the base of the left digit). With 2 and 3 this gives 23, 2³ = 8 and "2 in base 3" = 2. Swapping the digits gives 32, 9, and undefined. Both the horizontal and the vertical relation change the value, so they are independent channels (NUM-HYP-003, supported for the notations examined). A Maya-style comparator uses the vertical position for the place and horizontal bars and dots for the count within a place. The same layout read with the calendrical place weights (1, 20, 360, …) gives a different value: 1000 reads as 920. A last panel lets your browser render a number inside Arabic, Hebrew and Latin text. In the right-to-left texts the digits still read left to right, most significant first. Hebrew with European digits behaves exactly like Arabic with Arabic-Indic digits. The behaviour comes from the Unicode Bidirectional Algorithm, not from any one script, so the reading that "only Arabic notation does this" is refuted.
:::

</div>
<div class="lab-section">

## Converse fibers under reduction {#sec:num-fibers}

::: demo num-fibers
Text alternative: choose m and a divisor k. The widget counts, for every pair (a, b) in Z/m, whether b·c = a has no solution, exactly one, or many. It then shows how these classes move under reduction modulo k. For Z/12 → Z/4, 16 problems with no solution gain a unique one (3·c = 1 has none in Z/12, and c = 3 in Z/4), and 8 problems with many solutions get a unique one (3·c = 3). A solvable problem never becomes unsolvable. That direction is forbidden by the classical theorem that homomorphisms preserve positive existential statements (NUM-HIST-001). NUM-EXP-004 checked the prediction on 20 homomorphisms and found no violations.
:::

</div>

## Status of the lane

| hypothesis | status |
|---|---|
| NUM-HYP-001 zero / empty / absent are observably distinct | supported in Python, SQLite and JavaScript (3 substrates) |
| NUM-HYP-002 uniqueness of representation belongs to the language | supported; a classical fact restated as a measurement |
| NUM-HYP-003 two spatial channels can carry independent information | supported for the notations examined |
| NUM-HYP-003u only Arabic notation separates digit order from text direction | refuted by the comparators |
| NUM-HYP-004 converse classes move only in the directions classical theory allows | supported, 0 violations |
| NUM-HYP-007 one numeral string has one value across mainstream parsers | refuted: for "٣٤", Python gives 34, JavaScript NaN and SQLite 0 |
| NUM-HYP-010 the framework predicts something classical theory does not | open, currently negative |

The lane found one real defect in the edition's software. The SDK accepted Arabic-Indic and other non-ASCII digits, while the laboratory core rejected them. It is fixed, and the correction (C-006) is recorded in the results ledger.

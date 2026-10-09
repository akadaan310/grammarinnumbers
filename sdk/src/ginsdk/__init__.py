"""ginsdk — the executable companion to *Grammar in Numbers*.

Research program of Abed Kadaan (Founding Principal Researcher). Standard library only.

Modules
-------
numerals      numerals as operation expressions; addresses; affine compilation
peano         the successor grammar, primitive recursion with rule counts, segments a{I}b
converse      inverse operations as converse relations; solution-set admissibility
expr          arithmetic as a language: parse trees, typing, layered evaluation in 20+ domains
ieee          IEEE 754 binary formats, exact-rational reference simulator with flags
machine       integer semantics of x86-64, AArch64, RISC-V, C, Java, Rust, Python, JS
circuits      gate-level adders (ripple and prefix), carry monoid, multiplier, divider
bigint        limb arithmetic with counted word operations (bit complexity)
numbertheory  Euclid, Bézout, CRT, exponentiation, primality, factorization
cost          explicit cost counters
contracts     machine-readable operation contracts; layered inspection; independent verification

Command line: ``python3 -m ginsdk inspect "1 / 0" --domain Q`` (see ``python3 -m ginsdk -h``).

Stable public API (1.x): the names in ``__all__`` below, the module functions
documented in the book's SDK reference, the ``Outcome`` record of :mod:`ginsdk.expr`,
and the JSON schemas ``gin-contracts/1`` and ``gin-inspect/1``.
"""
from . import bigint, circuits, contracts, converse, cost, expr, ieee, machine, numbertheory, numerals, peano
from .contracts import inspect, verify
from .converse import SolutionSet, divide, divide_mod, square_root, subtract
from .cost import Cost
from .expr import compare, evaluate, parse
from .numerals import BINARY, DECIMAL, UNARY, DigitGrammar, bijective, canonicalize, convert, standard

__version__ = "1.0.0"
__all__ = ["bigint", "circuits", "contracts", "converse", "cost", "expr", "ieee", "machine", "numbertheory", "numerals", "peano",
           "SolutionSet", "divide", "divide_mod", "square_root", "subtract", "Cost", "compare", "evaluate", "parse",
           "BINARY", "DECIMAL", "UNARY", "DigitGrammar", "bijective", "standard",
           "canonicalize", "convert", "inspect", "verify"]

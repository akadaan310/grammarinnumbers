---
title: "Measured Complexity: What the Experiments Show and What They Cannot"
status: empirical
statusnote: Reproducible measurements of counted operations (GIN-EXP-008, 009, 011) with least-squares fits; no measurement here is a proof, and no algorithm here is new or faster than the classical ones.
description: Reading the book's cost experiments carefully — counted limb operations against bit length on logarithmic axes, fitted exponents with their spread, the gap between counted operations and wall-clock time, how the shape of an evaluation changes depth but not necessarily work, and the limits of fitting exponents to finite ranges.
epigraph: "A slope fitted to nine points is a description of nine points."
---

::: objectives
- Read the counted-operation data of GIN-EXP-008 as the word-RAM costs of Chapter 36, and fit exponents by least squares on logarithmic axes.
- Quantify how much a fitted exponent depends on the fitting range and on the random operands.
- Explain why wall-clock time on CPython is secondary evidence, and what it does and does not confirm.
- Interpret the numeral-evaluation experiment (GIN-EXP-011) as a statement about grammar shape and cost model, without inflating it into a speedup claim.
- State what measurements cannot establish.
:::

## What was measured {#sec:what-measured}

Every cost experiment in this book counts operations rather than timing them (\ledger{GIN-D-003}). GIN-EXP-008 draws random $L$-bit operands for $L = 64, 128, \ldots, 16384$ and counts the 32-bit limb operations (add or subtract with carry, limb product, two-by-one quotient estimate, limb comparison) performed by the SDK's implementations of Chapter 15. The counts are exact and reproducible from the seed; the experiment's re-run during the 2026-10 audit reproduced every counted field (\chapref{b-reproducibility}).

```python run
import json, os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
rows = json.load(open(os.path.join(ROOT, "experiments", "results", "exp008.json")))["data"]["rows"]
print(f"{'bits':>6} {'add':>6} {'mul school':>11} {'Karatsuba':>10} {'divmod':>9} {'gcd':>9}")
for r in rows:
    print(f"{r['bits']:6d} {r['add']:6d} {r['mul_schoolbook']:11d} {r['mul_karatsuba']:10d} {r['divmod_2L_by_L']:9d} {str(r.get('gcd_euclid', '-')):>9}")
```

```output
  bits    add  mul school  Karatsuba    divmod       gcd
    64      2           8          8        16       130
   128      4          32         32        50       476
   256      8         128        128       155      1582
   512     16         512        512       568      6085
  1024     32        2048       1796      2167     22000
  2048     64        8192       5838      8399     81034
  4096    128       32768      18409     33200    326516
  8192    256      131072      56771    131928         -
 16384    512      524288     172598    526069         -
```

## Fitting exponents, and how much to trust them {#sec:fits}

If a cost is $c L^\alpha$, then $\log(\text{cost}) = \log c + \alpha \log L$, and $\alpha$ is the slope on logarithmic axes. Fitting by least squares over different ranges shows how stable the estimate is:

```python run
import json, math, os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
rows = json.load(open(os.path.join(ROOT, "experiments", "results", "exp008.json")))["data"]["rows"]

def slope(points):
    xs, ys = [math.log2(x) for x, _ in points], [math.log2(y) for _, y in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)

theory = {"add": "1", "mul_schoolbook": "2", "mul_karatsuba": "log2 3 = 1.585", "divmod_2L_by_L": "2", "gcd_euclid": "2"}
for key, th in theory.items():
    pts = [(r["bits"], r[key]) for r in rows if r.get(key)]
    print(f"{key:15s} all points {slope(pts):.3f}   last four {slope(pts[-4:]):.3f}   first four {slope(pts[:4]):.3f}   theory {th}")
```

```output
add             all points 1.000   last four 1.000   first four 1.000   theory 1
mul_schoolbook  all points 2.000   last four 2.000   first four 2.000   theory 2
mul_karatsuba   all points 1.797   last four 1.628   first four 2.000   theory log2 3 = 1.585
divmod_2L_by_L  all points 1.891   last four 1.990   first four 1.708   theory 2
gcd_euclid      all points 1.875   last four 1.912   first four 1.838   theory 2
```

::: observation {#obs:fits title="Fitted exponents depend on the range" status="empirical" ledger="GIN-OBS-022"}
Least-squares exponents fitted to the counted limb operations of GIN-EXP-008 agree with the classical exponents for addition ($1$) and schoolbook multiplication ($2$) on every range. For Karatsuba multiplication, long division and Euclid's gcd they depend on the range: small operands fall below the asymptotic regime (Karatsuba falls back to schoolbook below $16$ limbs, so its first points have slope $2$; division and gcd carry linear terms that dominate at small $L$). Only the largest-range fits approach the classical values.
:::

The observation is a reason for caution, not a refutation: a fitted exponent describes the measured range. "Karatsuba is $\Theta(L^{1.585})$" is a theorem (\ledger{GIN-PROP-063}); "the SDK's Karatsuba has slope about $1.6$ between $4096$ and $16384$ bits" is a measurement; the second supports the first and does not prove it.

## The spread over random operands {#sec:spread}

Addition and schoolbook multiplication cost the same for all operands of a given length; Euclid's algorithm does not — the number of steps depends on the quotients. Repeating the measurement over many random pairs gives the spread:

```python run
import random, statistics
from ginsdk import bigint as B
from ginsdk.cost import Cost

for L in (256, 1024):
    rng = random.Random(L)
    ops = []
    for _ in range(40):
        a, b = rng.getrandbits(L) | 1 << (L - 1), rng.getrandbits(L) | 1 << (L - 1)
        c = Cost()
        B.gcd_euclid(B.from_int(a), B.from_int(b), c)
        ops.append(B.word_ops(c))
    print(f"L = {L:5d}: 40 random pairs, limb operations min {min(ops)}, median {statistics.median(ops):.0f}, max {max(ops)}, "
          f"relative spread {(max(ops) - min(ops)) / statistics.median(ops):.1%}")
```

```output
L =   256: 40 random pairs, limb operations min 1500, median 1638, max 1844, relative spread 21.0%
L =  1024: 40 random pairs, limb operations min 20769, median 21920, max 23487, relative spread 12.4%
```

The spread (at most about a fifth of the median) is small compared with the factor of about $13$ between the two medians, so the quadratic growth is not an artefact of the particular operands drawn in GIN-EXP-008 — but a single pair per length, as in that experiment, is a sample, and is reported as one.

## Wall-clock time is secondary {#sec:wallclock}

GIN-EXP-008 also timed CPython's built-in `int` multiplication. Those numbers depend on the machine, the interpreter and its internal thresholds (CPython switches from schoolbook to Karatsuba multiplication above a fixed size), and on noise:

```python run
# wall-clock: these digits change at every re-run of GIN-EXP-008; the build checks the shape only
import json, math, os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
rows = json.load(open(os.path.join(ROOT, "experiments", "results", "exp008.json")))["data"]["rows"]
prev = None
for r in rows:
    t = r["cpython_mul_s"]
    note = f"slope from previous {math.log2(t / prev):+.2f}" if prev else ""
    print(f"{r['bits']:6d} bits: {t * 1e6:9.3f} µs   {note}")
    prev = t
```

```output
    64 bits:     0.061 µs   
   128 bits:     0.074 µs   slope from previous +0.28
   256 bits:     0.123 µs   slope from previous +0.72
   512 bits:     0.314 µs   slope from previous +1.36
  1024 bits:     1.042 µs   slope from previous +1.73
  2048 bits:     4.447 µs   slope from previous +2.09
  4096 bits:    13.425 µs   slope from previous +1.59
  8192 bits:    41.047 µs   slope from previous +1.61
 16384 bits:   124.652 µs   slope from previous +1.60
```

At small sizes the time is dominated by interpreter overhead, and the growth per doubling is far below any multiplication exponent. At large sizes it varies from one recording to the next: in the recording printed here it lies between about $1.6$ and $2.1$, and an earlier recording of the same experiment on the same host gave values between about $1.1$ and $2.2$, with a slope below zero at 128 bits. A single noisy measurement per size cannot separate the algorithm from caches, allocation and timer resolution. These numbers are rewritten at every re-run, are not reproducible to the digit — the build checks this block's shape, not its digits — and the book never uses them to support an asymptotic claim (\ledger{GIN-D-003}).

## Shape changes depth, the cost model decides work {#sec:shape}

GIN-EXP-011 converts decimal numerals of $k$ digits to binary in two shapes — Horner's right-linear evaluation and a balanced tree of compositions — with schoolbook or Karatsuba multiplication in the balanced shape:

```python run
import json, os, ginsdk

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ginsdk.__file__))))
d = json.load(open(os.path.join(ROOT, "experiments", "results", "exp011.json")))["data"]
for r in d["rows"][-4:]:
    print(f"{r['digits']:5d} digits: Horner {r['horner']:9d}   balanced+school {r['balanced_schoolbook']:8d}   "
          f"balanced+Karatsuba {r['balanced_karatsuba']:7d}   depth {r['depth_horner']} vs {r['depth_balanced']}")
print("last slopes:", {k: v[-1] for k, v in d["loglog_slopes"].items()})
```

```output
 1024 digits: Horner    159519   balanced+school    29177   balanced+Karatsuba   24659   depth 1024 vs 10
 2048 digits: Horner    633291   balanced+school   104333   balanced+Karatsuba   73694   depth 2048 vs 11
 4096 digits: Horner   2529644   balanced+school   390586   balanced+Karatsuba  221901   depth 4096 vs 12
 8192 digits: Horner  10105494   balanced+school  1507887   balanced+Karatsuba  669698   depth 8192 vs 13
last slopes: {'horner': 1.998, 'balanced_schoolbook': 1.949, 'balanced_karatsuba': 1.594}
```

The balanced shape reduces the *depth* from $k$ to $\lceil \log_2 k \rceil$ in every case. Its *work* has the same asymptotic exponent as Horner's when multiplication is schoolbook (both slopes tend to $2$; the balanced shape is cheaper by a constant factor), and a smaller exponent only when it is combined with Karatsuba multiplication (\ledger{GIN-OBS-013}). This is the precise content of the "re-association" mechanism conjectured in GIN-CONJ-001: re-association buys parallel depth unconditionally and sequential work only together with a cost model that rewards balanced operands. It is a classical radix-conversion technique \cite{knuth1997,brentzimmermann2010}, not a new algorithm.

## What measurements cannot establish {#sec:cannot}

- **Asymptotic behaviour.** Every experiment covers a finite range; fitted exponents describe that range (\ref{obs:fits}).
- **Lower bounds.** A measured cost of an implementation bounds that implementation, not the problem; the lower bounds in this book (Chapters 10 and 22) are proofs.
- **Novelty.** Agreement with classical exponents confirms the implementations; it does not suggest a new algorithm, and none is claimed.
- **Other machines.** Counted operations transfer between machines; wall-clock times do not.

::: exercise {#ex:meas-fit}
Using the table of \ref{sec:fits}, predict the number of limb operations of schoolbook multiplication at $L = 32768$ bits, and explain why the same extrapolation for Karatsuba from its first four points would be wrong.
:::

::: solution {of="ex:meas-fit"}
Slope $2$: multiply the $16384$-bit count by $4$. Karatsuba's first four points have slope $2$ because it falls back to schoolbook below the threshold; extrapolating with slope $2$ overestimates the cost by a growing factor.
:::

::: exercise {#ex:meas-wall}
Name three reasons why a wall-clock time measured in CPython could decrease when the operand length increases, and why counted operations cannot show that behaviour.
:::

::: summary
- The cost experiments count word-RAM operations; the counts are exact and reproduced by the audit.
- Fitted exponents match the classical ones for addition and schoolbook multiplication on every range; for Karatsuba, division and gcd only on the largest ranges (\ref{obs:fits}).
- The spread over random operands is small relative to the growth; wall-clock times are secondary, host-specific and non-monotone at small sizes.
- Balanced evaluation reduces depth always and work only with subquadratic multiplication — a classical technique, measured, not a speedup claim.
- Measurements describe ranges and implementations; they do not prove asymptotics, lower bounds or novelty.
:::

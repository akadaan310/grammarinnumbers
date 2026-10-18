#!/bin/sh
# THE NUMBER research lane: tests and experiments NUM-EXP-001..004.
# Separate from the edition's experiments/run_all.sh; needs Python >= 3.10, optionally node (JS probes).
set -e
cd "$(dirname "$0")"
python3 -m unittest discover -s tests
for e in experiments/num_exp00*.py; do python3 "$e"; done

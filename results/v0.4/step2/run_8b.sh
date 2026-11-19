#!/bin/bash
# step 2 test runs: arm T planning, then 8B render + frozen score for every arm. Run from the repo root.
export SECQA_DATA_DIR=C:/Users/Admin/sgqa-clean/data PYTHONPATH=src PYTHONIOENCODING=utf-8
L=results/v0.4/step2/logs
for s in t1 t2; do
  [ -f results/v0.4/step2/$s/plans_T.json ] || { echo "== $s plan T $(date +%T)"; python -m secqa.evaluation.v4.run_step2 plan8b --set $s > $L/plan8b_$s.log 2>&1; echo "rc=$? $(date +%T)"; }
done
for a in T R S B1 B0 Sfree Slong; do for s in t1 t2; do
  [ -f results/v0.4/step2/$s/run_$a.json ] && { echo "skip $s $a"; continue; }
  echo "== $s render $a $(date +%T)"
  python -m secqa.evaluation.v4.run_step2 render --set $s --plans results/v0.4/step2/$s/plans_$a.json --tag $a > $L/render_${s}_$a.log 2>&1
  echo "rc=$? $(date +%T)"
done; done
echo ALLDONE

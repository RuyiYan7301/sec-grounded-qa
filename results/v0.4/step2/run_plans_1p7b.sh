#!/bin/bash
# step 2 test runs, 1.7B arms (plan amendment 2026-11-19). Run from the repo root.
export SECQA_DATA_DIR=C:/Users/Admin/sgqa-clean/data PYTHONPATH=src PYTHONIOENCODING=utf-8
PY=C:/Users/Admin/venvs/secqa-train/Scripts/python
SFT=runs/sft_hint_r16_lr2e-4/checkpoint-480
GRPO=runs/grpo_hard_lr1e-5/checkpoint-150
declare -A DATA=([t1]=data/eval/v0.2/qa_test.json [t2]=data/eval/v0.4/qa_heldout_2611.json)
cd train
for s in t1 t2; do
  O=results/v0.4/step2/$s
  run() { tag=$1; shift; [ -f ../$O/plans_$tag.json ] && { echo "skip $s $tag"; return; }
          echo "== $s $tag $(date +%T)"; $PY eval_planner.py --data ${DATA[$s]} --out $O/plans_$tag.json "$@" \
          > ../results/v0.4/step2/logs/plans_${s}_$tag.log 2>&1; echo "rc=$? $(date +%T)"; }
  run B0 --prompt long --decoding free --batch 8
  run B1 --prompt long --decoding constrained --batch 8
  run S --adapter $SFT --prompt short --decoding constrained
  run Sfree --adapter $SFT --prompt short --decoding free
  run R --base-adapter $SFT --adapter $GRPO --prompt short --decoding constrained
  run Slong --adapter $SFT --prompt long --decoding constrained --batch 8
done
s=t2; O=results/v0.4/step2/$s
run() { tag=$1; shift; [ -f ../$O/plans_$tag.json ] && { echo "skip $s $tag"; return; }
        echo "== $s $tag $(date +%T)"; $PY eval_planner.py --data ${DATA[$s]} --out $O/plans_$tag.json "$@" \
        > ../results/v0.4/step2/logs/plans_${s}_$tag.log 2>&1; echo "rc=$? $(date +%T)"; }
run R_batch1_latency --base-adapter $SFT --adapter $GRPO --prompt short --decoding constrained --batch 1
echo ALLDONE

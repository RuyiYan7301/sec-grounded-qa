"""v0.4 step 2: company and template splits (docs/v0.4-plan.md section 3), fixed before any training data.

    python -m secqa.train.splits      # writes data/train/v0.4/splits.json

Companies: the 77 new filers, sorted, shuffled with random.Random(2609): first 15 test, next 8 validation,
the rest train; plus the v0.2 test companies (AAPL NVDA MSFT AVGO INTC AMD) in test and CSCO, ORCL in train.
Templates: within each key of the frozen generator's template table (evaluation/v2/gen_qa.T), the list is
shuffled with random.Random(2610) (keys in sorted order) and split: the first ceil(n/2) train, the rest test.
"""
import json
import math
import random

from .. import config, universe
from ..evaluation.v2 import gen_qa

OUT = config.REPO_ROOT / "data" / "train" / "v0.4" / "splits.json"
V02_TEST = ["AAPL", "NVDA", "MSFT", "AVGO", "INTC", "AMD"]
V02_DEV = ["CSCO", "ORCL"]


def build():
    new = sorted(t for t in universe.filers() if t not in universe.ORIGINAL)
    assert len(new) == 77, len(new)
    order = new[:]
    random.Random(2609).shuffle(order)
    test_new, val, train_new = order[:15], order[15:23], order[23:]
    rng = random.Random(2610)
    tpl_train, tpl_test = {}, {}
    for k in sorted(gen_qa.T):
        lst = list(gen_qa.T[k])
        rng.shuffle(lst)
        h = math.ceil(len(lst) / 2)
        tpl_train[k], tpl_test[k] = lst[:h], lst[h:]
    doc = {"plan": "docs/v0.4-plan.md section 3", "seeds": {"companies": 2609, "templates": 2610},
           "companies": {"test": sorted(V02_TEST + test_new), "test_new": sorted(test_new),
                         "validation": sorted(val), "train": sorted(train_new + V02_DEV)},
           "templates": {"train": tpl_train, "test": tpl_test}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    c = doc["companies"]
    print({k: len(v) for k, v in c.items()})
    print("test_new", c["test_new"])
    print("validation", c["validation"])


def load():
    return json.loads(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    build()

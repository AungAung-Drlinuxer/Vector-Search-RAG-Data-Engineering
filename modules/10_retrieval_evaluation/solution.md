## လေ့ကျင့်ခန်း ၁ — Golden set ဖွဲ့ပါ

Golden set ဆိုတာ query တစ်ခုအတွက် မှန်ရမယ့် chunk id တွေကို စာရင်းချထားတဲ့ အဘိဓာန်လေးပါပဲ။ အောက်မှာ query သုံးခုနဲ့ ဖွဲ့ပြထားတယ်နော်။

```python
# Build a minimal golden set: query string -> list of correct chunk ids.
golden = {
    "how do I reset my password": ["doc1#chunk3", "doc2#chunk1"],
    "what is vector search": ["doc3#chunk1"],
    "pricing for the api": ["doc4#chunk2", "doc4#chunk5", "doc1#chunk1"],
}

print(len(golden))
for q, ids in golden.items():
    print(q, "->", ids, type(ids).__name__)
# Expected output:
# 3
# how do I reset my password -> ['doc1#chunk3', 'doc2#chunk1'] list
# what is vector search -> ['doc3#chunk1'] list
# pricing for the api -> ['doc4#chunk2', 'doc4#chunk5', 'doc1#chunk1'] list
```

**အဓိကအယူဆ** — Golden set က နောက်ပိုင်း metric အားလုံးရဲ့ အခြေခံအမှန်တာ ဖြစ်လို့ query နဲ့ မှန်တဲ့ chunk id တွေကို ရိုးရိုးသလေး ဒိုင်းအထဲ သိမ်းထားရတယ်။

## လေ့ကျင့်ခန်း ၂ — recall@k တွက်ပါ

recall@k က top-k အထဲ မှန်တာ ဘယ်လောက် ပြန်ရလဲကို တိုင်တာပါပဲ၊ relevant ဘူမတည်းက ခံမထိုးရင် 0.0 ပြန်ဖို့ သတိထားပါတယ်။

```python
def recall_at_k(retrieved, relevant, k):
    # recall@k = |hits in top k| / |all relevant|
    if not relevant:
        return 0.0
    rel = set(relevant)
    hits = sum(1 for c in retrieved[:k] if c in rel)
    return hits / len(rel)

r = ["a", "b", "c", "d"]
rel = ["a", "c", "x"]
print(round(recall_at_k(r, rel, 4), 4))
print(recall_at_k(r, rel, 2))
print(recall_at_k(r, [], 4))
# Expected output:
# 0.6667
# 0.3333333333333333
# 0.0
```

**အဓိကအယူဆ** — recall@k က relevant အားလုံးထဲမှာ top-k နဲ့ ဘယ်လောက် ဖုံးလွှမ်းလဲကို ပြပေမယ့် မှားတာတွေပါလာလား ဆိုတာကိုတော့ မပြပါဘူး။

## လေ့ကျင့်ခန်း ၃ — precision@k နဲ့ MRR တွက်ပါ

precision@k က top-k ထဲမှာ မှန်တာ ဘယ်လောက် စားရှိလဲ၊ MRR က ပထမဆုံး မှန်တဲ့ result အဆင့်ရဲ့ ပြောင်းပုံကို တိုင်တာပါတယ်၊ rank က 1 ကစပါတယ်နော်။

```python
import math

def precision_at_k(retrieved, relevant, k):
    # precision@k = |hits in top k| / k
    if k <= 0:
        return 0.0
    rel = set(relevant)
    hits = sum(1 for c in retrieved[:k] if c in rel)
    return hits / k

def mrr(retrieved, relevant):
    # MRR = 1 / rank of first relevant result (0 if none)
    rel = set(relevant)
    for rank, c in enumerate(retrieved, start=1):
        if c in rel:
            return 1.0 / rank
    return 0.0

r = ["a", "b", "c"]
rel = ["b"]
print(precision_at_k(r, rel, 2))
print(mrr(r, rel))
print(mrr(["a", "c"], ["b"]))
# Expected output:
# 0.5
# 0.5
# 0.0
```

**အဓိကအယူဆ** — MRR က ပထမဆုံး hit တစ်ခုတည်းရဲ့ အဆင့်ကိုပဲ ကြည့်တာမို့ "ရှင်းနင်းတဲ့ အဖြေ နှေးသလော" ကို ဖမ်းနိုင်တယ်။

## လေ့ကျင့်ခန်း ၄ — nDCG@k တွက်ပါ

nDCG@k က တကယ့် ranking ရဲ့ DCG ကို ideal ranking ရဲ့ IDCG နဲ့ ဘေးချိတ် တိုင်းတာတာပါ၊ rank နိမ့်ရင် gain နည်းသွားအောင် log နဲ့ ချိန်ပါတယ်။

```python
import math

def _dcg(hits):
    # hits: list of 0/1, position i (0-based) has rank = i + 1
    return sum(1.0 / math.log2((i + 1) + 1) for i, h in enumerate(hits) if h)

def ndcg_at_k(retrieved, relevant, k):
    rel = set(relevant)
    top = retrieved[:k]
    actual_hits = [1 if c in rel else 0 for c in top]
    # Ideal ranking: all relevant first, limited by k.
    n_ideal = min(len(rel), k)
    ideal_hits = [1] * n_ideal
    dcg = _dcg(actual_hits)
    idcg = _dcg(ideal_hits)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

r = ["a", "b", "c", "d"]
print(ndcg_at_k(r, ["a", "b"], 4))
print(round(ndcg_at_k(r, ["d"], 4), 4))
# Expected output:
# 1.0
# 0.4307
```

**အဓိကအယူဆ** — nDCG က မှန်တာတွေ အဆင့်အလိုက် ဘယ်နေရာမှာ ပေါ်လဲ ထည့်စဉ်းစားလို့ ranking quality ကို ပိုပြီး အသိမာစား ဖမ်းနိုင်တယ်။

## လေ့ကျင့်ခန်း ၅ — document-level အကဲဖြတ်ခြင်း ပြောင်းပါ

document-level မှာ `#` ရှေ့ပိုင်းက doc id အဖြစ် ယူပြီး အဲဒီ document က top-k ထဲ ပါလာရင် relevant chunk တစ်ခုချင်းစီ ရှင်းနင်းတယ်လို့ မှတ်ပါတယ်။

```python
def recall_at_k_doc(retrieved, relevant, k):
    # A relevant chunk is "covered" if its DOCUMENT appears in top k.
    rel = set(relevant)
    retrieved_docs = set(c.split("#")[0] for c in retrieved[:k])
    covered = sum(1 for c in rel if c.split("#")[0] in retrieved_docs)
    if not rel:
        return 0.0
    return covered / len(rel)

retrieved = ["doc1#1", "doc2#1", "doc1#2"]
relevant = ["doc1#1", "doc1#2", "doc3#1"]
print(round(recall_at_k_doc(retrieved, relevant, 3), 4))
# Expected output:
# 0.6667
```

**အဓိကအယူဆ** — RAG မှာ သုံးသူက ကြည့်တာ chunk မဟုတ်ဘဲ တစ်ခုလုံးရဲ့ အဖြေဖြစ်လို့ document-level recall က စွမ်းဆောင်ရည် အမှန်တစ်ခု ပိုနီးစေတယ်။

## လေ့ကျင့်ခန်း ၆ — Regression gate နဲ့ drift စစ်ပါ

Regression gate က baseline metric တွေနဲ့ ခုံကြည့်ပြီး တစ်ခုမျှ ကျရင် တားဆီးပေးတာပါ၊ CI ထဲ ထည့် run ခြင်းက drift ကို အလိုအလျောက် ဖမ်းပေးတယ်နော်။

```python
def regression_gate(baseline, current):
    # Returns False if any current metric dropped below baseline.
    passed = True
    for metric, base_value in baseline.items():
        cur_value = current.get(metric, 0.0)
        if cur_value < base_value:
            print(f"{metric} dropped: {base_value} -> {cur_value}")
            passed = False
    return passed

baseline = {"recall@5": 0.9, "mrr": 0.8}

# A real LLM judge would live here; we use a scripted deterministic stand-in.
current_bad = {"recall@5": 0.85, "mrr": 0.82}
print(regression_gate(baseline, current_bad))

current_good = {"recall@5": 0.91, "mrr": 0.8}
print(regression_gate(baseline, current_good))
# Expected output:
# recall@5 dropped: 0.9 -> 0.85
# False
# True
```

**အဓိကအယူဆ** — Metric တွေကို baseline နဲ့ နေရာတကျ ယှဉ်ပြီး gate ချတာက data ဒါမှမဟုတ် model ပြောင်းတဲ့အခါ တိတ်တိတ် ကျသွားတဲ့ regression ကို CI မှာ ဖမ်းနိုင်ပါတယ်။

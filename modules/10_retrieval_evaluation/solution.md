## လေ့ကျင့်ခန်း ၁ — Golden set ဖွဲ့ပါ

Golden set သည် query တစ်ခုအတွက် relevant chunk id များကို စုစည်းထားသော mapping ဖြစ်သည်။ အောက်တွင် query သုံးခုဖြင့် တည်ဆောက်ပြထားသည်။

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

**အဓိကအယူဆ** — Golden set သည် နောက်ပိုင်း metric အားလုံး၏ ground truth အခြေခံဖြစ်သဖြင့် query → relevant chunk id mapping ကို structured format ဖြင့် သိမ်းဆည်းရသည်။

## လေ့ကျင့်ခန်း ၂ — recall@k တွက်ပါ

recall@k သည် relevant အားလုံးအနက် top-k အတွင်း ပြန်ရောက်လာသည့် coverage အချိုးဖြစ်ပြီး၊ relevant စာရင်း empty ဖြစ်ပါက 0.0 return ပြန်ရန် edge case ကို ကိုင်တွယ်ထားသည်။

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

**အဓိကအယူဆ** — recall@k သည် relevant set အပေါ် top-k ၏ coverage ကိုသာ တိုင်းတာပြီး irrelevant result များ ရောဝင်မှုကို တိုင်းတာခြင်း မရှိပါ။

## လေ့ကျင့်ခန်း ၃ — precision@k နဲ့ MRR တွက်ပါ

precision@k သည် top-k အတွင်း relevant အချိုးကို တိုင်းတာပြီး၊ MRR သည် ပထမဆုံး relevant result ၏ rank reciprocal ဖြစ်သည် — rank သည် 1-based ဖြစ်သည်။

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

**အဓိကအယူဆ** — MRR သည် ပထမဆုံး hit တစ်ခုတည်း၏ rank ကိုသာ အခြေခံသဖြင့် ပထမဆုံး relevant result မည်မျှနောက်ကျမှ ရောက်သည်ကို rank-sensitive အဖြစ် ဖမ်းယူနိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — nDCG@k တွက်ပါ

nDCG@k သည် actual ranking ၏ DCG ကို ideal ranking ၏ IDCG ဖြင့် normalize လုပ်သော ratio ဖြစ်ပြီး၊ rank ကျဆင်းလျှင် gain ကို log discount ဖြင့် လျှော့ချသည်။

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

**အဓိကအယူဆ** — nDCG သည် relevant hit များ၏ rank position ကို အလေးချိန်ဖြင့် ထည့်သွင်းတွက်ချက်သဖြင့် ranking quality ကို position-insensitive metric များထက် ပိုမိုတိကျစွာ ဖမ်းယူနိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — document-level အကဲဖြတ်ခြင်း ပြောင်းပါ

Document-level evaluation တွင် `#` ၏ ရှေ့အပိုင်းကို doc id အဖြစ် ယူပြီး၊ relevant chunk တစ်ခု၏ document သည် top-k အတွင်း ပါဝင်ပါက ထို chunk ကို covered အဖြစ် ရေတွက်သည်။

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

**အဓိကအယူဆ** — RAG တွင် LLM context သည် chunk တစ်ခုချင်းစီထက် document အဆင့် content ပေါ် မူတည်လေ့ရှိသဖြင့် document-level recall သည် user-facing answer quality နှင့် ပိုမိုနီးစပ်သော proxy metric ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၆ — Regression gate နဲ့ drift စစ်ပါ

Regression gate သည် current metric များကို baseline နှင့် နှိုင်းယှဉ်ပြီး metric တစ်ခုခု ကျဆင်းပါက fail ပြန်ပေးသည်။ CI pipeline အတွင်း run ခြင်းဖြင့် drift ကို အလိုအလျောက် detect လုပ်နိုင်သည်။

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

**အဓိကအယူဆ** — Metric များကို baseline နှင့် စနစ်တကျ နှိုင်းယှဉ်၍ gate ချခြင်းဖြင့် data သို့မဟုတ် model ပြောင်းလဲမှုကြောင့် တဖြည်းဖြည်း ကျဆင်းလာသော silent regression ကို CI တွင် အလိုအလျောက် ဖမ်းယူနိုင်သည်။

# M10 — Retrieval အကဲဖြတ်ခြင်း: recall@k၊ MRR၊ nDCG၊ Golden Set နှင့် Regression Gate

ဒီ module မှာ retrieval (ရှာဖွေမှု) ရဲ့ အရည်အသွေးကို တိုင်းတာတဲ့ နည်းလမ်းတွေကို လေ့လာပါမယ်။
မှတ်ချက် — ဒီ material ဟာ တရားဝင် open documentation တွေအပေါ် အခြေခံပြီး ရေးထားတဲ့ မူရင်း သင်ယူမှု material ပါ။
Official sources: https://docs.ragas.io/ , https://arxiv.org/abs/2104.08663 , https://huggingface.co/spaces/mteb/leaderboard

---

## Subtopic 1 — Golden Set ဖွဲ့ခြင်း

### ဘာကို ဆိုလိုတာလဲ
Golden set ဆိုတာ query နဲ့ မှန်တဲ့ chunk အမှတ်တွေရဲ့ စာရင်းပါ။
query တစ်ခုအတွက် လူက "ဒီ chunk က အဖြေရှိတဲ့ chunk ပါ" လို့ သတ်မှတ်ပေးထားတာပါ။
အဲဒါကို ground truth (မြေပြင်အချက်အလက်၊ အမှန်တကယ် မှန်တဲ့ အဖြေ) လို့လည်း ခေါ်ပါတယ်။

### ဘာကြောင့် လဲ
Retrieval system တစ်ခုကို ပြင်ပြီးရင် "ပိုကောင်းသွားလား" လို့ မေးစရာ ရှိပါတယ်။
သေချာတဲ့ အဖြေစာရင်း မရှိရင် ခန့်မှန်းချက်ပဲ ပြောရပါတယ်။
ခန့်မှန်းချက်က မှားလို့ရပြီး အချိန်ကုန်ပါတယ်။
Golden set ရှိရင် တူတဲ့ အချက်အလက်နဲ့ ပြန်တိုင်းလို့ ရပါတယ်။
ဒါကြောင့် အခန့်မှန်းရတဲ့ အလုပ်ကို တိုင်းတာရတဲ့ အလုပ် ဖြစ်သွားစေတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ အဖြေရှိနိုင်တဲ့ query တွေကို စုဆောင်းပါတယ်။
၂။ အဲဒီ query တစ်ခုချင်းစီအတွက် corpus ထဲကမှ မှန်တဲ့ chunk ကို လက်ညှိုးထိုးပါတယ်။
၃။ စစ်ဆေးသူ နှစ်ယောက် သုံးယောက်လောက်က သဘောတူမှုကို စစ်ပါတယ်။
၄။ သဘောမတူတဲ့ query တွေကို ဖယ်ရှားပြီး အမှတ်အသား တပ်ဆင်ပါတယ်။
၅။ JSON လို format တစ်ခုနဲ့ သိမ်းဆည်းပြီး CI မှာ အသုံးပြုပါတယ်။

### ဥပမာ

```python
# A tiny golden set: query -> list of relevant chunk ids.
# In production this would be stored as JSON and reviewed by multiple annotators.
golden_set = [
    {"query": "vector search kya ah", "relevant": ["c1", "c3"]},
    {"query": "cosine similarity hmel", "relevant": ["c2"]},
    {"query": "HNSW graph", "relevant": ["c4"]},
]

# Sanity checks every golden set should pass before use.
for item in golden_set:
    assert isinstance(item["relevant"], list) and len(item["relevant"]) > 0

print("golden set size:", len(golden_set))
print("total relevant chunks:", sum(len(i["relevant"]) for i in golden_set))
# Expected output:
# golden set size: 3
# total relevant chunks: 4
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
RAG system တစ်ခုရဲ့ အမှားတွေ အများစုဟာ generation မဟုတ်ဘဲ retrieval ကနေ လာတတ်ပါတယ်။
မှန်တဲ့ chunk ကို မရှာတွေ့ရင် LLM အကောင်းဆုံးလည်း အဖြေမှန် မထုတ်နိုင်ပါ။
ဒါကြောင့် retrieval ကို သီးသန့် အကဲဖြတ်ဖို့ golden set က ပထမဆုံး လိုအပ်တာပါ။
MTEB leaderboard မှာလည်း ဒီပုံစံအတိုင်း စံတွက်ချက်တွေ သတ်မှတ်ပြီး တိုင်းတာကြောင်း တွေ့ရပါတယ် (https://huggingface.co/spaces/mteb/leaderboard)။

---

## Subtopic 2 — recall@k နဲ့ precision@k

### ဘာကို ဆိုလိုတာလဲ
recall@k (top-k ထဲ ပြန်ရှာတွေ့နိုင်မှု) ဆိုတာ — မှန်တဲ့ chunk အားလုံးထဲက ဘယ်နှစ်ခုက k အထိ ရှာတွေ့လဲဆိုတဲ့ အချိုးပါ။
precision@k (top-k ထဲ တိကျမှု) ဆိုတာ — ပြန်လာတဲ့ k ရလဒ်ထဲက ဘယ်နှစ်ခုက တကယ်မှန်လဲဆိုတဲ့ အချိုးပါ။

### ဘာကြောင့် လဲ
RAG မှာ LLM ကို chunk အလွန်အကျွံ မကျွေးသင့်ပါ။
ဒါပေမယ့် မှန်တဲ့ chunk တစ်ခု ပျောက်သွားရင် အဖြေက လုံးဝမှားသွားနိုင်ပါတယ်။
ဒါကြောင့် နှစ်ခုလုံးကို ခွဲပြီးကြည့်ဖို့ လိုပါတယ်။
recall နိမ့်ရင် — ရှာဖွေမှုက မှန်တာတွေကို လွတ်မိနေတာပါ။
precision နိမ့်ရင် — အသုံးမဝင်တဲ့ chunk တွေက ရလဒ်ကို ညစ်နေတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
recall@k တွက်နည်း — (မှန်တာထဲက k အတွင်း ရောက်တဲ့ အရေအတွက်) ÷ (မှန်တာ စုစုပေါင်း)။
precision@k တွက်နည်း — (k ရလဒ်ထဲက မှန်တဲ့ အရေအတွက်) ÷ k။
၁။ retrieved list နဲ့ relevant set ကို ယူပါတယ်။
၂။ top-k ကို ဖြတ်ပါတယ်။
၃။ နှစ်ခုရဲ့ တွဲ့မိမှု (overlap) ကို ရှာပါတယ်။
၄။ အချိုးနှစ်ခုကို ခွဲပြီး တွက်ပါတယ်။

### ဥပမာ

```python
def recall_at_k(retrieved, relevant, k):
    """Fraction of relevant chunks found in the top-k results."""
    top_k = retrieved[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / len(relevant)

def precision_at_k(retrieved, relevant, k):
    """Fraction of top-k results that are relevant."""
    top_k = retrieved[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / k

retrieved = ["c1", "c9", "c3", "c7", "c2"]
relevant  = ["c1", "c3", "c5"]

r3 = recall_at_k(retrieved, relevant, 3)   # hits in top-3: c1, c3 -> 2 of 3
p3 = precision_at_k(retrieved, relevant, 3)
r5 = recall_at_k(retrieved, relevant, 5)   # hits in top-5: c1, c3, c2? no c5 -> 2 of 3

print("recall@3 =", r3)
print("precision@3 =", p3)
print("recall@5 =", r5)
# Expected output:
# recall@3 = 0.6666666666666666
# precision@3 = 0.6666666666666666
# recall@5 = 0.6666666666666666
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
RAG အတွက် recall@k က precision@k ထက် ပိုအရေးကြီးတတ်ပါတယ်။
ဘာကြောင့်လဲဆိုတော့ LLM က အဆိုတွေကို စစ်ပြီး စစ်ထုတ်နိုင်လို့ပါ။
ဒါပေမယ့် မရှိတဲ့ အချက်အလက်ကို LLM မထုတ်နိုင်ပါ။
ragas docs မှာလည်း retrieval တိုင်းတာမှုတွေကို သီးသန့် အဓိက နေရာပေးထားတာ တွေ့ရပါတယ် (https://docs.ragas.io/)။

---

## Subtopic 3 — MRR နဲ့ nDCG

### ဘာကို ဆိုလိုတာလဲ
MRR (Mean Reciprocal Rank၊ ပျမ်းမျှပြန်ရမှတ်) ဆိုတာ — ပထမဆုံး မှန်တဲ့ ရလဒ်ရဲ့ နေရာအရ အမှတ်ပေးတဲ့ နည်းပါ။
နေရာ ၁ မှာ ရှိရင် 1.0၊ နေရာ ၃ မှာ ရှိရင် 1/3 ပါ။
nDCG (normalized Discounted Cumulative Gain) ဆိုတာ — အပေါ်ဆုံးက မှန်တာတွေကို ပိုအမှတ်ပေးပြီး အောက်ကျသွားရင် အမှတ်လျှော့ပေးတဲ့ နည်းပါ။

### ဘာကြောင့် လဲ
recall@k က "ရောက်သလား" ပဲ ပြပါတယ်၊ "နေရာအတိုင်း မှန်လား" မပြပါ။
ပြဿနာက — မှန်တဲ့ chunk က အောက်ဆုံးမှာ ရှိနေရင် LLM context အတွင်း အရေးမကြီးတော့ပါ။
အပေါ်ဆုံးက မှန်တာနဲ့ အောက်ကျနေတာဟာ သိသိသာသာ ကွာပါတယ်။
MRR နဲ့ nDCG က ဒီနေရာအလိုက် ကွာခြားမှုကို ဖမ်းနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
MRR တွက်ဖို့ — ၁။ query တစ်ခုချင်းစီမှာ ပထမမှန်တဲ့ နေရာကို ရှာပါတယ်။
၂။ reciprocal ကို တွက်ပါတယ် (1 ÷ rank)။
၃။ query အားလုံးရဲ့ ပျမ်းမျှကို ထုတ်ပါတယ်။
nDCG တွက်ဖို့ — ၁။ rank အလိုက် relevance အမှတ်တွေကို log2(rank+1) နဲ့ စားပါတယ်။
၂။ ပေါင်းလိုက်ရင် DCG ရပါတယ်။
၃။ ideal ranking ရဲ့ DCG (IDCG) နဲ့ စားပြီး normalize လုပ်ပါတယ်။

### ဥပမာ

```python
import math

def reciprocal_rank(retrieved, relevant):
    """1/rank of the first relevant result, 0 if none found."""
    for i, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return 1.0 / i
    return 0.0

def ndcg(retrieved, relevant, k):
    """Binary-relevance nDCG@k with standard log2 discount."""
    dcg = 0.0
    for i, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(relevant)) + 1))
    return dcg / idcg

# Two queries against a tiny golden set.
cases = [
    (["c1", "c2", "c3"], ["c1"]),        # first hit at rank 1
    (["c7", "c8", "c2"], ["c2"]),       # first hit at rank 3
]
mrr = sum(reciprocal_rank(r, rel) for r, rel in cases) / len(cases)
n1 = ndcg(cases[0][0], cases[0][1], 3)
n2 = ndcg(cases[1][0], cases[1][1], 3)

print("MRR =", mrr)
print("nDCG query1 =", n1)
print("nDCG query2 =", n2)
# Expected output:
# MRR = 0.6666666666666666
# nDCG query1 = 1.0
# nDCG query2 = 0.5
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
rank-aware metrics တွေက reranker တွေရဲ့ အကျိုးသက်ရောက်မှုကို ပိုကောင်းပြပါတယ်။
reranker က retrieved order ကို ပြောင်းတာ မှာပဲ။
ဒါ့အပြင် — paper 2104.08663 မှာ retrieval evaluation အတွက် BEIR benchmark ကို မိတ်ဆက်ထားပြီး အမျိုးမျိုးသော dataset တွေမှာ ranking တိုင်းတာချက်တွေပြပါတယ် (https://arxiv.org/abs/2104.08663)။
မတူတဲ့ dataset မှာ တိုင်းတာမှုတွေ သိသိသာသာကွာတတ်တာကို ဖော်ပြထားတာ အရေးကြီးပါတယ်။

---

## Subtopic 4 — Chunk-level နဲ့ Document-level အကဲဖြတ်မှု

### ဘာကို ဆိုလိုတာလဲ
Chunk-level အကဲဖြတ်မှုက — သေချာတဲ့ chunk id တစ်ခုချင်းစီကို တိုက်စစ်တာပါ။
Document-level အကဲဖြတ်မှုက — ရလဒ်တွေက အသုံးပြုတဲ့ စာအရပ်ရပ် (document) အတွင်း ပါလားမပါလားကိုပဲ စစ်တာပါ။

### ဘာကြောင့် လဲ
Chunk id တွေက pipeline တစ်ခုနဲ့တစ်ခု ကွာသွားရင် တိုက်စစ်လို့ မရပါ။
ဥပမာ — chunk size ပြောင်းလိုက်ရင် id တွေ အားလုံး ပြောင်းသွားပါတယ်။
ဒါပေမယ့် အသုံးပြုတဲ့ document ကတော့ မပြောင်းပါ။
ဒါကြောင့် document-level အကဲဖြတ်မှုက ပိုတည်ငြိမ်တဲ့ တိုင်းတာမှု ပေးနိုင်ပါတယ်။
နောက်တစ်ချက် — chunk-level က ပိုတိကျပေမယ့် document-level က ပိုနားလည်လွယ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Chunk-level — golden set က chunk id တွေနဲ့ retrieved chunk id တွေကို တိုက်စစ်ပါတယ်။
၂။ Document-level — id တွေကို document အဖြစ် မြေပုံပြောင်းပြီး တိုက်စစ်ပါတယ်။
၃။ နှစ်မျိုးလုံးကို ချိတ်ပြီး ကြည့်ပါတယ် — ကွာခြားချက်က chunking ကို ညွှန်ပြပါတယ်။

### ဥပမာ

```python
# Mapping: chunk id -> document id (would come from the chunking pipeline).
chunk_to_doc = {"c1": "dA", "c2": "dA", "c3": "dB", "c4": "dB", "c9": "dC"}

golden_doc = ["dA", "dB"]              # correct documents
retrieved = ["c1", "c9", "c4"]          # chunk ids from the retriever

# Chunk-level: strict, exact chunk id comparison.
gold_chunks = ["c1", "c2", "c3", "c4"]
chunk_hit = len(set(retrieved) & set(gold_chunks))
print("chunk-level hits:", chunk_hit, "/", len(gold_chunks))

# Document-level: map retrieved chunks to documents, then compare.
retrieved_docs = {chunk_to_doc[c] for c in retrieved}
doc_hit = len(retrieved_docs & set(golden_doc))
print("document-level hits:", doc_hit, "/", len(golden_doc))
# Expected output:
# chunk-level hits: 2 / 4
# document-level hits: 2 / 2
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Pipeline ကို ပြင်တဲ့အခါ chunking strategy ကို မကြာခဏ ပြောင်းရပါတယ်။
Chunk id မှာ အခြေခံတဲ့ evaluation တွေက အဲဒီအခါ အလုပ်မလုပ်တော့ပါ။
Document-level တိုင်းတာမှုက ကြာရှည်လို့ သင့်တဲ့ ရွေးချယ်မှု ဖြစ်နိုင်ပါတယ်။
စျေးကွက်မှာ အလုပ်အများစုက နှစ်မျိုးလုံးကို ပေါင်းပြီး အသုံးပြုလေ့ရှိပါတယ်။

---

## Subtopic 5 — Drift ကြောင့် CI Regression Gate နဲ့ Deterministic LLM Judge

### ဘာကို ဆိုလိုတာလဲ
Regression gate ဆိုတာ — CI pipeline ထဲမှာ evaluation တွေကို အလိုအလျောက် လည်ပတ်စေပြီး အမှတ်တွေ ကျသွားရင် build ကို အောင်မြင်မှု မပေးတဲ့ စည်းမျဉ်းပါ။
Drift (မတည်ငြိမ်မှု၊ တဖြည်းဖြည်း ပြောင်းသွားမှု) ဆိုတာ — data ဒါမှမဟုတ် model ပြောင်းလဲမှုကြောင့် အရည်အသွေး တဖြည်းဖြည်း ကျသွားတာပါ။
LLM judge ဆိုတာ — ရလဒ်တွေရဲ့ အရည်အသွေးကို LLM နဲ့ အမှတ်ပေးတဲ့ နည်းပါ။ ကိုယ့် eval set မှာ rubric ရေးထားပြီး အမှတ်ပေးခိုင်းတာပါ။ ဒီသင်ခန်းစာရဲ့ lab မှာ judge ကို scripted deterministic stand-in နဲ့ အစားထိုးပြီး ရမှတ်တွက်ပုံကို ပြထားပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Retrieval ကို မတိုင်းတာဘဲ ပြောင်းလဲမှု လုပ်တာက ခန့်မှန်းချက်နဲ့ လောင်းတာပါ။ Golden set နဲ့ recall@k တို့ ရှိထားရင် chunking ဒါမှမဟုတ် embedding model ပြောင်းတိုင်း အကျိုးသက်ရောက်မှုကို ဂဏန်းနဲ့ သိနိုင်ပါတယ်။

## အနှစ်ချုပ်

- Golden set က query နှင့် မှန်တဲ့ chunk အမှတ် အတွဲပါ။
- recall@k က "အဖြေမှန် top-k ထဲ ပါလား" ကို တိုင်းပါတယ်။
- MRR က ပထမဆုံး အဖြေမှန် ဘယ်နေရာမှာ ရှိလဲ ကို တိုင်းပါတယ်။
- nDCG က အစဉ်လိုက် အရည်အသွေးကို အလေးချိန်နဲ့ တိုင်းပါတယ်။
- Eval ကို CI gate အဖြစ် ထားပြီး ကျဆင်းမှုကို အလိုအလျောက် ဖမ်းပါ။

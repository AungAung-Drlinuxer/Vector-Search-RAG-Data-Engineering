# M13 — Capstone: End-to-end ဒီဇိုင်းနှင့် Storage/Memory/QPS တွက်စက်

## Subtopic 1 — End-to-end Pipeline ကို တစ်ခုတည်း ဒီဇိုင်းအဖြစ် စုစည်းခြင်း

### ဘာကို ဆိုလိုတာလဲ

Pipeline ဆိုတာ အဆင့်တွေ ဆက်တိုက် ချိတ်တာပါ — ingest, chunk, embed, index, retrieve, rerank, evaluate ပါ။ Ingest က document တွေကို စနစ်တင်တာပါ။ Chunk က စာပိုဒ်ရှည်ကြီးကို အပိုင်းသေးသေး ဖြတ်တာပါ။ Embed က စာသားကိ vector (နံပါတ်အတန်း) အဖြစ် ပြောင်းတာပါ။ Retrieve က query နဲ့ နီးစပ်တဲ့ chunk တွေကို ရှာတာပါ။ Rerank က ရှာပြီး top results တွေကို ပြန်စစ်ပြီး အဆင့်ပြန်တာပါ။

### ဘာကြောင့် လဲ

အဆင့်တစ်ခုချင်းစီကို တစ်ခုပြီးတစ်ခု လေ့ကျင့်ရင် အဆင့်တွေကို ချိတ်ဆက်ပုံကို မမြင်ရဘူးနော်။ Chunk အရွယ်အစားပြောင်းရင် retrieve ရလဒ်လည်း ပြောင်းတယ်။ Embedding dimension ပြောင်းရင် storage လည်း ပြောင်းတယ်။ ဒါကြောင့် တစ်ခုတည်း ဒီဇိုင်းအဖြစ် မြင်ဖို့ လိုပါတယ်။ တွက်စက်လည်း pipeline တစ်ခုလုံးကို သိမ်းမှ မှန်တယ်နော်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Document တွေကို စနစ်တင်ပြီး သင့်တော်တဲ့ နည်းနဲ့ chunk လုပ်တယ်။
၂။ chunk တိုင်းကို embedding model နဲ့ vector ပြောင်းတယ်။ ဒီမှာ real model ကို မသုံးဘူး — သင်ခန်းစာက offline ဖြစ်ရလို့ fixed vector တွေကို သုံးပါမယ်။
၃။ vector တွေကို index (HNSW graph) မှာ သိမ်းတယ်။
၄။ Query လာရင် cosine similarity နဲ့ နီးစပ်တဲ့ chunk တွေကို ရှာတယ်။
၅။ ရလဒ်တွေကို rerank လုပ်ပြီး evaluate ဆိုတာ recall@k (စုစည်းတဲ့နံပါတ်၊ မှန်တဲ့အဖြေ ဘယ်နှစ်ခုပါလဲ တွက်တာ) နဲ့ တိုင်းတယ်။

### ဥပမာ

Real system မှာဆိုရင် PostgreSQL + pgvector (https://github.com/pgvector/pgvector) က index နဲ့ retrieve ကို လုပ်ပေးပါတယ်။ ဒီနမူနာက အဲဒီ mechanics တွေကို စတန်းဒတ် library နဲ့ ပြန်ဆောက်ပြထားတာပါ။

```python
import math

# A tiny "corpus": real ingest/chunk/embed steps are replaced by fixed vectors
# so the lesson runs fully offline and deterministically.
docs = ["PostgreSQL stores data", "pgvector adds vector search",
        "RAG retrieves documents", "HNSW is a graph index"]
vecs = [[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 1.0]]
query = [1.0, 0.0, 1.0, 0.0]

def cosine(a, b):
    # cosine similarity: dot(a,b) / (||a|| * ||b||)
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

# This is the "retrieve" step; pgvector's operator would do this inside SQL.
scores = sorted(((cosine(query, v), i) for i, v in enumerate(vecs)), reverse=True)
top3 = [i for _, i in scores[:3]]
# Ground truth: doc ids the evaluator (e.g. a Ragas-style checker,
# https://docs.ragas.io/) marked as relevant. Here it is a fixed list.
ground_truth = [0, 2, 3]
recall3 = len(set(top3) & set(ground_truth)) / 3

print("Retrieved top-3 doc ids:", top3)
print("recall@3 vs ground truth: {:.2f}".format(recall3))
# Expected output:
# Retrieved top-3 doc ids: [0, 3, 2]
# recall@3 vs ground truth: 1.00
```


### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Production မှာ အဆင့်တစ်ခုချင်းစီက ကွဲနေရင် debug ရခက်ပါတယ်။ ရလဒ်ဆိုးရင် chunk, embedding, rerank ထဲက ဘယ်ဟာမှားလဲ မသိရဘူးနော်။ Pipeline တစ်ခုလုံးကို သတ်မှတ်ချက် (deterministic) နဲ့ ပြန်တာကို အဆင့်တိုင်းကို ခြေရာခံနိုင်တယ်။ Ragas လို evaluation framework ကို ပေါင်းရင် ရလဒ်ကို ဂဏန်းနဲ့ တိုင်းတနိုင်ပါတယ်။

## Subtopic 2 — Storage တွက်ချက်မှု (chunks × dimension × bytes)

### ဘာကို ဆိုလိုတာလဲ

Vector storage ဆိုတာ vector အားလုံးရဲ့ byte စုစုပေါင်းပါ။ Formula က —

```
storage = chunk_count × dimension × bytes_per_value
```

fp32 (နံပါတ်တစ်လုံးကို 4 byte) က အများဆုံးပါ။ fp16 (2 byte) က တစ်ပိုင်း သက်သာတယ်။ pgvector က ဒီနှစ်မျိုးလုံးကို `vector` နဲ့ `halfvec` type နဲ့ ထောက်ပံ့ပါတယ်။

### ဘာကြောင့် လဲ

Storage ကို မခန့်မှန်းရင် server memory လို့ကို မသိရဘူးနော်။ Vector တွေက disk မှာတောင် ရှိနိုင်ပေမယ့် retrieve မြန်ဖို့အတွက် RAM (memory) ထဲ ဝင်ဖို့ လိုတတ်တယ်။ ကုန်ကျစရိတ်က ဒီဂဏန်းပေါ် မူတည်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ chunk အရေအတွက်ကို သတ်မှတ်တယ်။
၂။ embedding dimension ကို ကြည့်တယ်။
၃။ value တစ်လုံးချင်း byte အရေအတွက်ကို သတ်မှတ်တယ် (fp32 = 4)။
၄။ သုံးခုကို မြှောက်ပြီး 1024 နဲ့ သုံးခါ ပြောင်းလို့ GiB ရတယ်။

### ဥပမာ

ယူဆချက် — chunk 1,000,000 ခု၊ dimension 768၊ fp32။

```python
GIB = 1024 ** 3  # bytes in one GiB, derived here so the number is traceable

chunks = 1_000_000      # assumption: one million chunks
dim = 768               # assumption: 768-dimensional embeddings
bytes_per_value = 4     # fp32 = 4 bytes per number

vector_bytes = chunks * dim * bytes_per_value
print("fp32 vector storage: {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))

bytes_per_value = 2     # fp16 / halfvec = 2 bytes per number
vector_bytes = chunks * dim * bytes_per_value
print("fp16 vector storage: {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))
# Expected output:
# fp32 vector storage: 3072000000 bytes = 2.86 GiB
# fp16 vector storage: 1536000000 bytes = 1.43 GiB
```


### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Dimension နှစ်ဆ တင်ရင် storage လည်း နှစ်ဆ တိုးတယ်။ Chunk နှစ်ဆ တိုးရင်လည်း နှစ်ဆပါ။ pgvector မှာ column type ပြောင်းချင်ရင် migration လိုတတ်လို့ စဖို့ အရင်တွက်ဖို့ အရေးကြီးပါတယ်။ Metadata နဲ့ row overhead တွေလည်း ပိုတတ်လို့ အဲဒါကို ခန့်မှန်းခြင်းနဲ့ ထပ်ပေါင်းသင့်ပါတယ်။

## Subtopic 3 — HNSW Index Memory ခန့်မှန်းချက်

### ဘာကို ဆိုလိုတာလဲ

HNSW က multi-layer graph index ပါ — Malkov & Yashunin စာတမ်း (https://arxiv.org/abs/1603.09320) မှာ ထုတ်ပြထားတယ်။ Node တစ်ခုက layer တစ်ခုမှာ link (နောင်တစ်ခုဆီ ကြိုးဆက်) အများဆုံး M ခု ထားတယ်။ Layer 0 (အောက်ဆုံး layer) မှာတော့ 2M ခုအထိ ခွင့်ပြုပါတယ်။ Memory က vector data နဲ့ link list နှစ်မျိုးလုံးပေါ် မူတည်တယ်။

### ဘာကြောင့် လဲ

Index ကို disk မှာသာ ထားရင် graph search တစ် hop (ဆက်တံတစ်ခု ကျော်တာ) တိုင်း disk ဖတ်ရပြီး နှေးတယ်။ RAM ထဲ ဝင်ရင်မြန်ပေမယ့် RAM က ကန့်သတ်ချက်ရှိတယ်။ ဒါကြောင့် link အရေအတွက်အထိ memory တွက်ဖို့ လိုပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector bytes — chunk_count × dim × bytes_per_value။
၂။ Layer 0 link bytes — chunk_count × (2M) × link_bytes (link တစ်ခုကို int32၊ 4 byte လို့ ယူဆ)။
၃။ Upper layer တွေက အဆင့်စဉ်အလိုက် node နည်းသွားလို့ နမူနာမှာ ကျော်တယ် (စာတမ်းရဲ့ layer ခွဲခြင်းအရ)။
၄။ နှစ်မျိုးပေါင်းလို့ index တစ်ခုလုံးရဲ့ memory ရတယ်။

### ဥပမာ

ယူဆချက် — chunk 1,000,000၊ dim 768၊ fp32၊ M = 16၊ layer 0 link များ = 2M = 32၊ link တစ်ခု 4 byte။

```python
GIB = 1024 ** 3

chunks = 1_000_000
dim = 768
vector_bytes_per_chunk = dim * 4        # fp32
M = 16
layer0_links = 2 * M                    # HNSW paper: layer 0 allows up to 2M links
link_bytes = 4                          # assumption: int32 link ids

vector_bytes = chunks * vector_bytes_per_chunk
graph_bytes = chunks * layer0_links * link_bytes
total = vector_bytes + graph_bytes

print("Vector data : {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))
print("Graph links : {} bytes = {:.2f} GiB".format(graph_bytes, graph_bytes / GIB))
print("Index total : {} bytes = {:.2f} GiB".format(total, total / GIB))
# Expected output:
# Vector data : 3072000000 bytes = 2.86 GiB
# Graph links : 128000000 bytes = 0.12 GiB
# Index total : 3200000000 bytes = 2.98 GiB
```


### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

M တိုးရင် recall ကောင်းလာပေမဲ့ memory နဲ့ build time လည်း တိုးပါတယ်။ ef_construction တိုးရင် build နှေးပေမဲ့ graph အရည်အသွေး တက်ပါတယ်။ ef_search ကို query အချိန်မှာ ချိန်လို့ရတာမို့ latency နဲ့ recall ကို အလုပ်ချိန်မှာ ညှိနိုင်ပါတယ်။

Capstone ဒီဇိုင်းမှာ parameter တွေကို ကိန်းဂဏန်းနဲ့ ရှင်းပြနိုင်ရင် အဖွဲ့က ယုံကြည်ပါတယ်။ Memory တွက်ချက်မှု၊ QPS ခန့်မှန်းချက်နဲ့ eval ရလဒ် သုံးခု ကိုက်ညီနေရင် ဒီဇိုင်းက ခိုင်မာပါတယ်။

## အနှစ်ချုပ်

- Storage = chunk အရေအတွက် × dimension × bytes-per-value (+ metadata)။
- HNSW index memory ≈ vector data + graph (M နှင့် အချိုးကျ)။
- QPS ကို ef_search၊ concurrency နှင့် shard အရေအတွက်က ဆုံးဖြတ်ပါတယ်။
- Chunking နှင့် embedding ရွေးချယ်မှုကို eval နဲ့ တိုင်းပြီး ဆုံးဖြတ်ပါ။
- ဒီဇိုင်းစာတမ်းမှာ ကိန်းတိုင်းအတွက် formula ဒါမှမဟုတ် doc ညွှန်ပြပါ။

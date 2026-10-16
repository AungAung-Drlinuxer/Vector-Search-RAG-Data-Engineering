## လေ့ကျင့်ခန်း ၁ — Bi-encoder vs Cross-encoder Architectural Differences

Bi-encoder နှင့် Cross-encoder architecture နှစ်ခု၏ အခြေခံကွာခြားချက်များ၊ computation complexity၊ document vector pre-computation/caching စွမ်းရည်နှင့် multi-stage retrieval pipeline တွင် ၎င်းတို့၏ role ကို သုံးသပ်ဖော်ပြပါ။

**Hints:** SBERT documentation (https://sbert.net/) ကို ကိုးကားပါ။ Bi-encoder သည် query နှင့် document ကို သီးခြားစီ encode လုပ်သဖြင့် offline caching ဖြစ်နိုင်ပြီး Cross-encoder သည် (query, document) pair ကို joint full-attention ဖြင့် cross-examine လုပ်သဖြင့် O(N) inference cost ရှိသည်။

**Expected behavior:** Caching capability, computation cost, retrieval vs reranking stages တွင် အသုံးချပုံ ကွာခြားချက် ၃ ခုကို တိကျစွာ output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — Cosine Similarity Scoring & Top-K Manual Reranking

Query vector တစ်ခုနှင့် candidate document vectors ၅ ခုအကြား cosine similarity တွက်ချက်ပြီး score အမြင့်ဆုံး top-3 candidates ကို ascending/descending order အလိုက် deterministic rerank ပြုလုပ်ပါ။

**Hints:** Standard library `math` module နှင့် `sorted(..., key=lambda ..., reverse=True)` ကို အသုံးပြုပါ။

**Expected behavior:** Document ၅ ခုလုံး၏ cosine similarity scores များကို output ထုတ်ပြီး top-3 reranked list ကို ပြသရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Cross-encoder Reranking Latency Cost Modeling

Top-k candidate size နှင့် cross-encoder latency overhead အကြား ဆက်စပ်မှုကို ပုံဖော်ပါ။ Assumed cross-encoder inference latency (50 ms per pair) နှင့် candidate size (top-k = 20) အပေါ် အခြေခံ၍ pure retrieval သီးသန့် latency နှင့် end-to-end latency ကို နှိုင်းယှဉ်တွက်ချက်ပါ။

**Hints:** Formula: `total_rerank_ms = top_k * per_call_ms`။ Sizing decision များအတွက် assumption များကို explicit comments ဖြင့် ဖော်ပြပါ။

**Expected behavior:** Candidate size အလိုက် ကုန်ကျမည့် total latency overhead ကို ရှင်းလင်းစွာ တွက်ချက်ပြသနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — HyDE (Hypothetical Document Embeddings) Retrieval Alignment

Question-style query တစ်ခုကို deterministic hypothetical answer (stand-in representation) အဖြစ် transform လုပ်ပြီး corpus documents များနှင့် cosine similarity တွက်ချက်ကာ direct query match နှင့် နှိုင်းယှဉ်ပါ။

**Hints:** Gao et al. (arXiv:2212.10496) အရ HyDE သည် query space မှ document space သို့ semantic alignment ပြုလုပ်ပေးသည်။ Offline execution အတွက် deterministic dummy generator ကို အသုံးပြုပါ။

**Expected behavior:** Direct query scores နှင့် HyDE transformed scores နှစ်မျိုးလုံးကို output ထုတ်ပြီး semantic similarity ပြောင်းလဲမှုကို သရုပ်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၅ — Multi-Query Expansion & RRF Score Fusion

Query တစ်ခုအတွက် alternative paraphrases ၃ ခုထုတ်လုပ်ပြီး discrete ranking lists ၃ ခုကို Reciprocal Rank Fusion (RRF, k=60) ဖြင့် single robust ranking အဖြစ် ပေါင်းစပ်ပါ။

**Hints:** Formula: `RRF_score(d) = Σ [1 / (k + rank(d))]`။ Input ranking lists အသီးသီး၏ rank positions များကို aggregate ပြုလုပ်ပါ။

**Expected behavior:** Variant query တစ်ခုချင်းစီ၏ rankings များနှင့် final fused order ကို deterministic အစီအစဉ်အတိုင်း ရရှိရမည်။

---

## လေ့ကျင့်ခန်း ၆ — MMR (Maximal Marginal Relevance) Diversity Selection

Document candidate pool မှ top results များကို ရွေးချယ်ရာတွင် relevance နှင့် diversity အကြား trade-off ကို ထိန်းချုပ်သည့် MMR algorithm ကို parameter λ တန်ဖိုးနှစ်မျိုး (λ=0.9 နှင့် λ=0.3) ဖြင့် execute လုပ်ပါ။

**Hints:** MMR formulation: `argmax_{d_i ∈ R \ S} [ λ * Sim1(d_i, q) - (1 - λ) * max_{d_j ∈ S} Sim2(d_i, d_j) ]`။ λ=0.9 သည် relevance ကို ဦးစားပေးပြီး λ=0.3 သည် diversity ကို ဦးစားပေးသည်။

**Expected behavior:** λ တန်ဖိုး ကွဲပြားမှုအပေါ် မူတည်၍ ရွေးချယ်ခံရသော document subsets များ၏ structural difference ကို ရှင်းလင်းစွာ ပြသနိုင်ရမည်။

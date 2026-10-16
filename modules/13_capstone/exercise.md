## လေ့ကျင့်ခန်း ၁ — Vector Storage Footprint Capacity Estimation

1,000,000 chunks, 768 dimensions, FP32 encoding (4 bytes per floating-point value) အခြေအနေအတွက် raw vector table storage footprint ကို bytes နှင့် gigabytes (GB/GiB) ဖြင့် formula အတိုင်း တွက်ချက်ပါ။

**Hints:** Formula: `Storage_Bytes = Chunks * Dimensions * Bytes_Per_Value`။ FP32 precision သည် dimension တစ်ခုလျှင် 4 bytes သုံးစွဲပြီး FP16/Halfvec သည် 2 bytes သုံးစွဲသည်။

**Expected behavior:** 3,072,000,000 bytes (≈ 3.072 GB / 2.86 GiB) output ကို mathematical derivation နှင့်တကွ တိကျစွာ ထုတ်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — Chunk Size Granularity Trade-Off Analysis

Words ပေါင်း 100,000 ပါဝင်သော corpus တစ်ခုအတွက် (a) 200-word granular chunks နှင့် (b) 800-word macro chunks ခွဲခြမ်းမှုနှစ်ခု၏ total chunk volume ကို နှိုင်းယှဉ်တွက်ချက်ပြီး downstream retrieval precision vs context completeness trade-offs များကို သုံးသပ်ပါ။

**Hints:** `chunks = math.ceil(total_words / chunk_size)`။ 200-word chunks များသည် high precision ပေးနိုင်သော်လည်း indexing overhead 4x မြင့်တက်ပြီး 800-word chunks များသည် context completeness ကောင်းမွန်သော်လည်း semantic dilution ဖြစ်နိုင်သည်။

**Expected behavior:** (a) 500 chunks နှင့် (b) 125 chunks volume ကွာခြားချက်နှင့် semantic retrieval trade-offs များကို ရှင်းလင်းစွာ ဖော်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Single-Layer Proximity Graph Construction & Greedy Search

2D vector coordinates 100 ခုအတွက် bidirectional degree M=4 ပါဝင်သော proximity graph တစ်ခုကို တည်ဆောက်ပြီး initial entry point မှ target query သို့ greedy graph traversal algorithm ကို implement လုပ်ပါ။

**Hints:** Malkov & Yashunin (arXiv:1603.09320) HNSW Layer 0 mechanics ကို ရှင်းလင်းစွာ သရုပ်ပြရန် ဖြစ်သည်။ Local minimum သို့ ရောက်ရှိပါက traversal ရပ်တန့်ရမည်။

**Expected behavior:** Graph search result index နှင့် brute-force exact search result index တို့ကို နှိုင်းယှဉ် output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — Empirical Recall@K Metric Benchmark

Exercise ၃ တွင် တည်ဆောက်ခဲ့သော graph structure အပေါ် query distribution (100 synthetic queries) ဖြင့် graph search နှင့် brute-force search တို့၏ intersection ကို တွက်ချက်ကာ deterministic Recall@5 metric ကို တိုင်းတာပါ။

**Hints:** `Recall@K = |Retrieved_Top_K ∩ Exact_Top_K| / K`။ Reproducibility သေချာစေရန် `random.Random(42)` ဖြင့် deterministic execution ပြုလုပ်ပါ။

**Expected behavior:** 0.0 မှ 1.0 ကြားရှိ average Recall@5 တန်ဖိုး (seed 42 တွင် 0.748) ကို output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၅ — QPS Throughput နှင့် Percentile Latency (p95) Modeling

Greedy graph search တွင် query 1,000 ခုအတွက် distance evaluations count ကို profile လုပ်ပြီး assumed execution latency model (1 microsecond per evaluation) အပေါ် အခြေခံ၍ system QPS နှင့် p95 latency ကို တွက်ချက်ပါ။

**Hints:** Total latency ကို တိုင်းတာပြီး `QPS = Total_Queries / Total_Time_Seconds`။ Percentile 95th latency ကို sorted distribution ၏ index `int(0.95 * len)` ဖြင့် ရယူပါ။

**Expected behavior:** Mean evaluations per query, p95 latency (μs) နှင့် estimated QPS metrics များကို ရှင်းလင်းစွာ ဖော်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၆ — Unified End-to-End Pipeline Consolidation

Ingestion → Chunking → Stable Embedding → Proximity Graph Indexing → Retrieval (top-20) → Cosine Reranking (top-5) → Recall@5 Evaluation အဆင့် ၈ ခုလုံးကို deterministic pure Python script တစ်ခုတည်းတွင် consolidate လုပ်ပါ။

**Hints:** Embedding layer အတွက် deterministic hash function ကို stand-in အဖြစ် အသုံးပြုပါ။ First-stage candidate pool (top-20) မှ exact cosine similarity ဖြင့် top-5 သို့ rerank ပြုလုပ်ပြီး exact ground truth နှင့် နှိုင်းယှဉ်ပါ။

**Expected behavior:** Chunk count, total distance evaluations, empirical Recall@5 (seed 42 တွင် 0.912) နှင့် modeled QPS throughput တို့ကို single execution run ဖြင့် output ထုတ်ပေးရမည်။

# M7 — Reranking & Query Transformation (Cross-encoder, HyDE, Multi-query, MMR)

First-stage retrieval ၏ candidate list အား downstream LLM context အတွက် precision မြှင့်တင်ပေးသော reranking strategies များနှင့် query-document semantic gap ကို ကျဉ်းမြောင်းစေသော query transformation techniques များကို လေ့လာသည့် module ဖြစ်သည်။

## သင်ယူလေ့လာမည့် အကြောင်းအရာများ

- Bi-encoder နှင့် Cross-encoder architecture ကွာခြားချက်နှင့် computational trade-offs
- Reranking latency cost modeling နှင့် top-k candidate budget သတ်မှတ်ခြင်း
- HyDE (Hypothetical Document Embeddings) ဖြင့် zero-shot query expansion လုပ်ဆောင်ပုံ
- Multi-query expansion နှင့် Reciprocal Rank Fusion (RRF) ပေါင်းစပ်မှု
- Query decomposition ဖြင့် complex multi-part queries များကို ကိုင်တွယ်ခြင်း
- MMR (Maximal Marginal Relevance) ဖြင့် relevance နှင့် candidate diversity ချိန်ညှိခြင်း

## Module အစိတ်အပိုင်းများ

| File | အကြောင်းအရာ |
|---|---|
| `README.md` | Module scope နှင့် learning objectives |
| `explanation.md` | Subtopic ၅ ခု၏ သဘောတရားရှင်းလင်းချက်၊ formula နှင့် deterministic code example |
| `exercise.md` | ကိုယ်တိုင် implement လုပ်ရမည့် လေ့ကျင့်ခန်း ၆ ခု |
| `solution.md` | Reference implementation နှင့် ရှင်းလင်းချက် |
| `lab.py` | Standard library သာ သုံး၍ local တွင် ချက်ချင်း run နိုင်သော executable lab |

### `explanation.md` — Subtopic ဖွဲ့စည်းပုံ

1. Bi-encoder နှင့် Cross-encoder Architecture
2. Reranking Latency Cost Modeling နှင့် Top-k Budgeting
3. HyDE — Hypothetical Document Embeddings
4. Multi-Query Expansion နှင့် Reciprocal Rank Fusion (RRF)
5. MMR (Maximal Marginal Relevance) ဖြင့် Diversity Optimization

## Prerequisites

- Modules M1–M6 အခြေခံ (dense retrieval, cosine similarity, RRF mechanics)
- Python 3 standard library
- External model API မလိုအပ်ပါ — Reranking logic, math calculations နှင့် heuristics များကို pure Python ဖြင့် deterministic တည်ဆောက်ထားသည်။

## Production Use Cases

- Vector search ၏ top candidates များအတွင်း high-precision ranking ပြန်လည်စီစဉ်ခြင်း
- Short keyword queries များမှ ambiguous intent ကို disambiguate ပြုလုပ်ခြင်း
- Redundant near-duplicate passages များ context window ထဲ မပြည့်စေရန် diverse passage selection ပြုလုပ်ခြင်း

## References

- SBERT (Sentence Transformers) documentation: https://sbert.net/
- HyDE Paper (Gao et al., arXiv:2212.10496): https://arxiv.org/abs/2212.10496
- Ragas Retrieval Evaluation metrics: https://docs.ragas.io/

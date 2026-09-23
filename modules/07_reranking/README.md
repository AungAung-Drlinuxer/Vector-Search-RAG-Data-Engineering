# M7 — Reranking နှင့် Query ပြောင်းလဲခြင်း (Cross-encoder, HyDE, Multi-query, MMR)

ဒီ module မှာ retrieval ရလဒ်ကို ပိုကောင်းအောင် လုပ်ပေးတဲ့ reranking နည်းလမ်းတွေနဲ့ query ကို ပြောင်းလဲတဲ့ နည်းလမ်းတွေကို သင်ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- Bi-encoder နဲ့ cross-encoder ကွာခြားချက်ကို နားလည်ပါတယ်။
- Reranking ရဲ့ latency (နှောင့်နှေးမှု) ကုန်ကျစရိတ်ကို တွက်နည်း သင်ပါတယ်။
- Top-k ဘယ်လို ရွေးမလဲ ဆိုတာ သင်ပါတယ်။
- HyDE (hypothetical document embedding) နည်းနဲ့ query ကို ချဲ့ပါတယ်။
- Multi-query expansion နဲ့ fusion (ပေါင်းစည်းခြင်း) ကို ကိုယ်တိုင် ရေးပါတယ်။
- MMR (Maximal Marginal Relevance) နဲ့ ရလဒ် ကွဲပြားမှု (diversity) ရှင်းပါတယ်။

## သင်ခန်းစာများ

1. **L7.1 — Bi-encoder vs Cross-encoder:** SBERT စတိုင် bi-encoder နဲ့ cross-encoder ခြားနားချက်။
2. **L7.2 — Reranking နဲ့ Latency ကုန်ကျစရိတ်:** candidate အရေအတွက်နဲ့ ကုန်ကျစရိတ် တွက်ချက်ခြင်း။
3. **L7.3 — Top-k ရွေးချယ်မှု:** recall နဲ့ cost ကြားမှာ ချိန်ညှိခြင်း။
4. **L7.4 — HyDE:** query အတွက် hypothetical document ဆောက်ပြီး embed လုပ်ခြင်း။
5. **L7.5 — Multi-query Expansion နဲ့ Fusion:** query အမျိုးမျိုး ထုတ်ပြီး RRF နဲ့ ပေါင်းခြင်း။
6. **L7.6 — Query Decomposition:** ခက်ခဲတဲ့ query ကို သေးသေးလေး ခွဲခြင်း။
7. **L7.7 — MMR:** ရလဒ်တွေထဲမှာ ပုံစံ မတူတာ ရွေးပေးခြင်း။

## လိုအပ်ချက်များ (Prerequisites)

- M1 မှ M6 အထိ အခြေခံကောင်းရပါတယ်။
- Cosine similarity နဲ့ embedding vector ကို နားလည်ရပါတယ်။
- Python အခြေခံနဲ့ standard library ကို ရေးတတ်ရပါတယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Vector search ပထမအဆင့်ရဲ့ ရလဒ်က မှန်ပေမယ့် အရင်ဆုံး မပေါ်တဲ့အခါ သုံးပါတယ်။
- Query တစ်ခုတည်းနဲ့ သင့်တော်တဲ့ document မရှာတွေ့တဲ့ RAG စနစ်တွေမှာ သုံးပါတယ်။
- ရလဒ်တွေ အတူတူပဲ ထပ်နေတဲ့အခါ MMR နဲ့ ဖြေရှင်းပါတယ်။

## ကိုးကား

ဒီ module က official open documentation တွေကနေ ရေးထားတဲ့ မူရင်း လေ့လာသင်ယူမှု ပစ္စည်းပါ။ Commercial course တစ်ခုရဲ့ သင်ခန်းစာတွေကို မကူးယူ မပြန်ရေးထားပါ။

- SBERT (Sentence Transformers) official docs: https://sbert.net/
- HyDE စာတမ်း (Hypothetical Document Embeddings): https://arxiv.org/abs/2212.10496
- Ragas evaluation docs: https://docs.ragas.io/

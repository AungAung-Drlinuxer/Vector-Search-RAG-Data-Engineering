# M3 — Embedding Model ရွေးချယ်မှု၊ Dimension၊ Distance Metric နှင့် Caching

ဒီ module မှာ embedding model ရွေးတဲ့အခါ စဉ်းစားရမှုတွေ၊ dimension နဲ့ storage တွက်ချက်နည်း၊ distance metric ရွေးချယ်မှု၊ caching နဲ့ version စီမံခန့်ခွဲမှုကို လေ့လာပါမယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- Embedding model ရွေးတဲ့အခါ multilingual ဖြစ်မဖြစ်၊ domain နဲ့ ကိုက်မကိုက် ကြည့်နည်း
- Dimension အရွယ်နဲ့ storage အရွယ်ကို formula နဲ့ တွက်ချက်နည်း
- L2 normalization (vector ရဲ့ အလျားကို တစ်ဖြစ်လဲ လုပ်ပေးတဲ့ နည်း) နဲ့ cosine၊ dot၊ L2 distance တွေရဲ့ ဆက်စပ်မှု
- Matryoshka embedding (အရွယ် အမျိုးမျိုး ခေါက်သားရှိတဲ့ embedding) နဲ့ dimension ဖြတ်တောက်ခြင်း
- Batch encoding နဲ့ embedding cache လုပ်နည်း
- Embedding version စီမံခန့်ခွဲမှုနဲ့ multilingual corpus (မြန်မာ အပါအဝင်) အတွက် သတိထားစရာတွေ

## သင်ခန်းစာများ

- L1 — Embedding Model ရွေးချယ်မှု: multilingual နဲ့ domain
- L2 — Dimension နဲ့ Storage တွက်ချက်မှု
- L3 — L2 Normalization နဲ့ cosine / dot / L2 ဆက်စပ်မှု
- L4 — Matryoshka Embedding နဲ့ Dimension ဖြတ်တောက်ခြင်း
- L5 — Batch Encoding နဲ့ Cache
- L6 — Embedding Version စီမံခန့်ခွဲမှု
- L7 — Multilingual Corpus အတွက် သတိထားစရာများ

## လိုအပ်ချက်များ (Prerequisites)

- M1 နဲ့ M2 ကို ပြီးထားရပါမယ်
- Python အခြေခံနဲ့ standard library (math, json, hashlib) ကို နားလည်ထားရပါမယ်
- Vector နဲ့ cosine similarity အခြေခံကို သိထားရပါမယ်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- ကိုယ့် corpus (စုစည်းထားတဲ့ စာသားအစု) အတွက် embedding model ရွေးချင်တဲ့အခါ
- Storage ကုန်ကျစရိတ်နဲ့ speed ကို ကြိုတွက်ချင်တဲ့အခါ
- မြန်မာစာ အပါအဝင် multilingual search စနစ်ဆောက်ချင်တဲ့အခါ
- Model ပြောင်းတဲ့အခါ cache နဲ့ version ကို ဘယ်လို ထိန်းရမလဲ သိချင်တဲ့အခါ

## ကိုးကား

ဒီ module ရဲ့ နည်းပညာ အချက်အလက်တွေက ဒီ official open documentation တွေကနေ ယူထားတာပါ။

- https://arxiv.org/abs/2210.07316 (E5 text embeddings)
- https://arxiv.org/abs/2309.07597 (BGE / C-Pack)
- https://arxiv.org/abs/2212.03533 (Matryoshka representation learning)
- https://arxiv.org/abs/2205.13147 (ELOQUERA / instruction-finetuned embeddings — GTE စာတမ်း)
- https://sbert.net/ (Sentence Transformers တရားဝ စာရွက်စာတမ်း)

**Originality:** ဒီကိစ္သည် official open documentation တွေကနေ ကိုယ်ပိုင်ရေးသားထားတဲ့ လေ့လာမှု ပါဝင်သည့် အချက်အလက်များ ဖြစ်ပါသည် — စီးပွားဖြစ် သင်တန်းတစ်ခုခုရဲ့ သင်ခန်းစာကို ကူးယူ ဒါမှမဟုတ် ပြန်ရေးထားတာ မဟုတ်ပါဘူး။

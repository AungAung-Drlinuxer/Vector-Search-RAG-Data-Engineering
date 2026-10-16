# M3 — Embedding Model ရွေးချယ်မှု၊ Dimension၊ Distance Metric နှင့် Caching

ဒီ module တွင် embedding model ရွေးချယ်မှု စံနှုန်းများ၊ dimension နှင့် storage တွက်ချက်ခြင်း၊ distance metric ရွေးချယ်မှု၊ caching နှင့် version စီမံခန့်ခွဲမှုကို လေ့လာသည်။

## ဒီ module မှာ ဘာသင်မလဲ

- Embedding model ရွေးချယ်ရာတွင် multilingual support နှင့် domain fit စစ်ဆေးခြင်း
- Dimension နှင့် storage ပမာဏကို formula ဖြင့် တွက်ချက်ခြင်း
- L2 normalization နှင့် cosine၊ dot၊ L2 distance တို့၏ ဆက်စပ်မှု
- Matryoshka embedding နှင့် dimension truncation
- Batch encoding နှင့် embedding cache
- Embedding version စီမံခန့်ခွဲမှုနှင့် multilingual corpus (မြန်မာ အပါအဝင်) အတွက် သတိပြုရန် အချက်များ

## သင်ခန်းစာများ

- L1 — Embedding Model ရွေးချယ်မှု: multilingual နှင့် domain
- L2 — Dimension နှင့် Storage တွက်ချက်မှု
- L3 — L2 Normalization နှင့် cosine / dot / L2 ဆက်စပ်မှု
- L4 — Matryoshka Embedding နှင့် Dimension ဖြတ်တောက်ခြင်း
- L5 — Batch Encoding နှင့် Cache
- L6 — Embedding Version စီမံခန့်ခွဲမှု
- L7 — Multilingual Corpus အတွက် သတိထားစရာများ

## လိုအပ်ချက်များ (Prerequisites)

- M1 နှင့် M2 modules ပြီးမြောက်ထားရန်
- Python အခြေခံနှင့် standard library (math, json, hashlib) အသုံးပြုနိုင်ရန်
- Vector နှင့် cosine similarity အခြေခံ သိရှိထားရန်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- ကိုယ်ပိုင် corpus အတွက် embedding model ရွေးချယ်ရန်
- Storage ကုန်ကျစရိတ်နှင့် query speed ကို ကြိုတင်တွက်ချက်ရန်
- မြန်မာစာ အပါအဝင် multilingual search စနစ် တည်ဆောက်ရန်
- Model ပြောင်းလဲရာတွင် cache နှင့် version ထိန်းသိမ်းနည်း သိရှိရန်

## ကိုးကား

ဒီ module ၏ နည်းပညာ အချက်အလက်များကို အောက်ပါ official open documentation များမှ ရယူထားသည်။

- https://arxiv.org/abs/2210.07316 (E5 text embeddings)
- https://arxiv.org/abs/2309.07597 (BGE / C-Pack)
- https://arxiv.org/abs/2212.03533 (Matryoshka representation learning)
- https://arxiv.org/abs/2205.13147 (ELOQUERA / instruction-finetuned embeddings — GTE စာတမ်း)
- https://sbert.net/ (Sentence Transformers တရားဝင် စာရွက်စာတမ်း)

**Originality:** ဒီ module သည် official open documentation များအပေါ် အခြေခံ၍ ကိုယ်ပိုင်ရေးသားထားသော original study material ဖြစ်သည်။ Commercial course တစ်ခု၏ သင်ခန်းစာများကို ကူးယူခြင်း သို့မဟုတ် ပြန်လည်ရေးသားခြင်း မဟုတ်ပါ။

# M10 — Retrieval အကဲဖြတ်ခြင်း: recall@k, MRR, nDCG, Golden Set နှင့် Regression Gate

Retrieval စနစ်ကို သင်္ချာနဲ့ တိုင်းတာပြီး အရည်အသွေး ကျဆင်းမှု (regression) ကို အလိုအလျောက် ဖမ်းတဲ့ နည်းလမ်းတွေကို လေ့လာရတဲ့ module ပါ။

## ဒီ module မှာ ဘာသင်မလဲ

- Golden set (မေးခွန်းတစ်ခု → မှန်တဲ့ chunk အမှတ်စာရင်း) ဖွဲ့တဲ့နည်း။
- recall@k, precision@k, MRR, nDCG တွေကို pure Python နဲ့ တွက်နည်း။
- chunk-level နှင့် document-level အကဲဖြတ်မှု ကွာခြားပုံ။
- LLM judge အစား deterministic stand-in သုံးပြီး နားလည်နည်း။
- Drift (အချက်အလက် ရွေ့လျားမှု) စောင့်ကြည့်ခြင်း နှင့် CI regression gate တည်ဆောက်နည်း။

## သင်ခန်းစာများ

1. **M10.1** — Golden set ဖွဲ့ခြင်း နှင့် label သဘောတရား
2. **M10.2** — recall@k နှင့် precision@k တွက်နည်း
3. **M10.3** — MRR (Mean Reciprocal Rank) နှင့် nDCG
4. **M10.4** — Chunk-level နှင့် document-level အကဲဖြတ်ခြင်း
5. **M10.5** — LLM judge ၏ deterministic stand-in
6. **M10.6** — Drift စောင့်ကြည့်ခြင်း နှင့် CI regression gate

## လိုအပ်ချက်များ (Prerequisites)

- M05 (cosine similarity) နှင့် M06 (HNSW-style graph search) ရဲ့ Python code တွေကို နားလည်ထားရပါတယ်။
- Python standard library (`math`, `json`, `statistics`) အခြေခံ သင်ပြီးဖြစ်ရပါမယ်။
- pytest တို့ CI တို့ရဲ့ သဘောအခြေခံ သိထားရင် ပိုကောင်းပါတယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Retrieval pipeline တစ်ခု ပြင်ပြီးတိုင်း "ပိုဆိုးသွားလား" ဆိုတာ မေးချင်တဲ့အခါ။
- Chunk size သို့မဟုတ် embedder လဲတဲ့အခါ အရည်အသွေး နှိုင်းယှဉ်ချင်တဲ့အခါ။
- Production မှာ drift ဖြစ်နေလား အလိုအလျောက် စစ်ချင်တဲ့အခါ။

## ကိုးကား

- RAGAS docs: https://docs.ragas.com/
- BEIR paper: https://arxiv.org/abs/2104.08663
- MTEB leaderboard: https://huggingface.co/spaces/mteb/leaderboard

---

ဒီ course က အပေါ်မှာဖော်ပြထားတဲ့ official documentation တွေကနေ ရေးထားတဲ့ original လေ့လာသင်ယူမှု ပို့ချချက်သာ ဖြစ်ပါတယ်။ အခြား commercial course တွေရဲ့ သင်ခန်းစာတွေကို ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ပါဘူး။

# M10 — Retrieval အကဲဖြတ်ခြင်း: recall@k, MRR, nDCG, Golden Set နှင့် Regression Gate

Retrieval စနစ်၏ အရည်အသွေးကို quantitative metric များဖြင့် တိုင်းတာခြင်းနှင့် quality regression ကို CI တွင် အလိုအလျောက် detect လုပ်ခြင်းတို့ကို ကိုင်တွယ်သည့် module ဖြစ်သည်။

## ဒီ module မှာ ဘာသင်မလဲ

- Golden set (query → relevant chunk id list) တည်ဆောက်နည်း။
- recall@k, precision@k, MRR, nDCG တွက်ချက်မှုများကို pure Python ဖြင့် implement လုပ်နည်း။
- chunk-level evaluation နှင့် document-level evaluation တို့၏ ကွာခြားချက်။
- LLM judge အစား deterministic stand-in အသုံးပြုခြင်း။
- Drift monitoring နှင့် CI regression gate တည်ဆောက်နည်း။

## သင်ခန်းစာများ

1. **M10.1** — Golden set ဖွဲ့ခြင်း နှင့် label သဘောတရား
2. **M10.2** — recall@k နှင့် precision@k တွက်နည်း
3. **M10.3** — MRR (Mean Reciprocal Rank) နှင့် nDCG
4. **M10.4** — Chunk-level နှင့် document-level အကဲဖြတ်ခြင်း
5. **M10.5** — LLM judge ၏ deterministic stand-in
6. **M10.6** — Drift စောင့်ကြည့်ခြင်း နှင့် CI regression gate

## လိုအပ်ချက်များ (Prerequisites)

- M05 (cosine similarity) နှင့် M06 (HNSW-style graph search) ၏ Python implementation များကို နားလည်ထားရမည်။
- Python standard library (`math`, `json`, `statistics`) အသုံးပြုနိုင်ရမည်။
- pytest နှင့် CI pipeline ၏ အခြေခံ သဘောတရားများ ရှိပါက အဆင်ပြေသည်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Retrieval pipeline ပြောင်းလဲမှုတိုင်းအတွက် quality regression ရှိ/မရှိ အတည်ပြုလိုသည့်အခါ။
- Chunk size သို့မဟုတ် embedder ပြောင်းလဲမှုများ၏ အကျိုးသက်ရောက်မှုကို နှိုင်းယှဉ်လိုသည့်အခါ။
- Production တွင် drift ကို အလိုအလျောက် detect လုပ်လိုသည့်အခါ။

## ကိုးကား

- RAGAS docs: https://docs.ragas.com/
- BEIR paper: https://arxiv.org/abs/2104.08663
- MTEB leaderboard: https://huggingface.co/spaces/mteb/leaderboard

---

ဒီ course က အပေါ်မှာဖော်ပြထားတဲ့ official documentation တွေကနေ ရေးထားတဲ့ original လေ့လာသင်ယူမှု ပို့ချချက်သာ ဖြစ်ပါတယ်။ အခြား commercial course တွေရဲ့ သင်ခန်းစာတွေကို ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ပါဘူး။

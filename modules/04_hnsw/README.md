# M4 — HNSW Index အတွင်းပိုင်း: Parameter၊ Recall နှင့် Memory

ဤ module သည် HNSW index (graph-based ANN index) ၏ အတွင်းပိုင်း လုပ်ဆောင်ချက်ကို လေ့လာသည်။ ဤ course သည် official open documentation များအပေါ် အခြေခံ၍ ရေးသားထားသော original လေ့လာစာ ဖြစ်ပြီး commercial course များကို ကူးယူထားခြင်း မဟုတ်ပါ။

## ဒီ module မှာ ဘာသင်မလဲ

- HNSW ၏ multi-layer graph ဖွဲ့စည်းပုံ။
- Parameter သုံးခု — `M`, `ef_construction`, `ef_search` — ၏ အခန်းကဏ္ဍနှင့် သက်ရောက်မှု။
- Recall နှင့် latency ကြား trade-off ကို တွက်ချက်ခြင်း။
- Index memory နှင့် build time ခန့်မှန်းတွက်ချက်နည်း။
- Filtered search နှင့် delete/update တို့၏ index quality အပေါ် သက်ရောက်မှု။

## သင်ခန်းစာများ

| သင်ခန်းစာ | ဖော်ပြချက် |
|---|---|
| 4.1 — Multi-layer Graph သဘောတရား | HNSW paper အရ layer များ၏ အပြုအမူ |
| 4.2 — Build Parameter: M နှင့် ef_construction | Graph edge အရေအတွက် upper bound နှင့် build-time search width |
| 4.3 — Query Parameter: ef_search | Search ကုန်ကျမှုနှင့် recall ဆက်နွယ်မှု |
| 4.4 — Recall တွက်နည်း (recall@k) | Standard-library Python ဖြင့် တိုင်းတာခြင်း |
| 4.5 — Memory တွက်နည်း | 1,000,000 chunks၊ 768 dimensions၊ fp32 ယူဆချက်ဖြင့် တွက်ချက်ခြင်း |
| 4.6 — Build Time၊ Filtered Search၊ Delete/Update | Real system (pgvector, FAISS) များတွင် အပြုအမူ |

## လိုအပ်ချက်များ (Prerequisites)

- M3 (Chunking နှင့် Embedding) ပြီးမြောက်ထားရန်။
- Python standard library (`random`, `math`, `heapq`) ဖြင့် code ရေးနိုင်ရန်။
- PostgreSQL + pgvector အကြိုအတွေ့မရှိလည်း ရသည် — ဤ module က တွဲဖက် ရှင်းပြသည်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Vector data သိန်းချီအထိ ရောက်လာသောအခါ exact search latency ကို လက်မခံနိုင်တော့ခြင်း။
- pgvector တွင် `CREATE INDEX ... USING hnsw` အတွက် parameter ရွေးချယ်ရန် ဆုံးဖြတ်ရသောအခါ။
- Recall အနည်းငယ် စွန့်လှူ၍ latency လျှော့ချရမည့် design ဆုံးဖြတ်ချက် ချမှတ်ရသောအခါ။

## ကိုးကား

- HNSW paper (Malkov & Yashunin) — https://arxiv.org/abs/1603.09320
- pgvector (official GitHub) — https://github.com/pgvector/pgvector
- FAISS wiki (official GitHub wiki) — https://github.com/facebookresearch/faiss/wiki
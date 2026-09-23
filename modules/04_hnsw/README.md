# M4 — HNSW Index အတွင်းပိုင်း: Parameter၊ Recall နှင့် Memory

ဒီ module မှာ HNSW index (Approximate Nearest Neighbor ရှာဖွေမှုအတွက် graph ဖြစ်တဲ့ index တစ်မျိုး) ရဲ့ အတွင်းပိုင်းလုပ်ဆောင်ချက်ကို သင်ရပါမယ်။ ဒီ course က official open documentation တွေကနေ ရေးထားတဲ့ original လေ့လာစာဖြစ်ပြီး အခြား commercial course တွေကို ကူးယူရေးထားတာ မဟုတ်ပါဘူး။

## ဒီ module မှာ ဘာသင်မလဲ

- HNSW ရဲ့ multi-layer graph သဘောတရား (အလွှာများစွာနဲ့ ဖွဲ့စည်းထားတဲ့ graph) ကို နားလည်လာမယ်။
- Parameter သုံးခု — `M`, `ef_construction`, `ef_search` — ရဲ့ ကွာခြားချက်နဲ့ သက်ရောက်မှုကို လေ့လာမယ်။
- Recall (တကယ်နီးစွာရှိသင့်တဲ့ အဖြေတွေ ပြန်ရရခြင်း) နဲ့ latency (ဖြေပေးရန် ကုန်ချိန်) အပေးအယူကို တွက်ချက်မယ်။
- Index memory နဲ့ build time (index ဆောက်ရန် ကုန်ချိန်) တွက်နည်းကို လက်တွေ့ စမ်းကြည့်မယ်။
- Filtered search (အချက်အလက်စစ်ချိုချိုးပြီး ရှာတာ) နဲ့ delete/update ရဲ့ ဆိုးကျိုးတွေကို သိရမယ်။

## သင်ခန်းစာများ

| သင်ခန်းစာ | ဖော်ပြချက် |
|---|---|
| 4.1 — Multi-layer Graph သဘောတရား | HNSW paper အရ layer တွေက ဘယ်လို အလုပ်လုပ်လဲ |
| 4.2 — Build Parameter: M နှင့် ef_construction | Graph အဆက်အသွယ် အရေအတွက် နဲ့ ဆောက်စဉ် ရှာအကွာအတွင်း |
| 4.3 — Query Parameter: ef_search | ရှာဖွေစဉ် ကုန်ကျမှုနဲ့ recall ဆက်သွယ်မှု |
| 4.4 — Recall တွက်နည်း (recall@k) | Standard-library Python နဲ့ အရှင်းဆုံး နည်းနဲ့ တိုင်းတာခြင်း |
| 4.5 — Memory တွက်နည်း | 1,000,000 chunks၊ 768 dimensions၊ fp32 ဆိုတဲ့ သတ်မှတ်ချက်နဲ့ တွက်ပြမယ် |
| 4.6 — Build Time၊ Filtered Search၊ Delete/Update | Real system (pgvector, FAISS) တွေမှာ ဘယ်လို ခံရလဲ |

## လိုအပ်ချက်များ (Prerequisites)

- M3 (Chunking နဲ့ Embedding) ကို ပြီးထားရပါမယ်။
- Python standard library အခြေခံ (`random`, `math`, `heapq`) နဲ့ ရေးနိုင်ရပါမယ်။
- PostgreSQL + pgvector အကြောင်း ကောင်းကောင်းမွန်မွန် မသိရင်လည်း ရပါတယ်။ ဒီ module ကရော ဒါနဲ့ တွဲပြောပါမယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Vector data အရေအတွက် သိန်းနဲ့ချီလာရင် exact search က နှေးလွန်းတာကို ခံစားရတဲ့အခါ။
- pgvector မှာ `CREATE INDEX ... USING hnsw` ဆိုတဲ့ command ရေးကြည့်တဲ့အခါ၊ parameter ရွေးရမှာ ဝင်ရှုပ်တဲ့အခါ။
- Recall ကို အနည်းငယ် စတေးပြီး latency လျှော့ချင်တဲ့ ဒီဇိုင်းဆုံးဖြတ်ချက် လုပ်ရတဲ့အခါ။

## ကိုးကား

- HNSW paper (Malkov & Yashunin) — https://arxiv.org/abs/1603.09320
- pgvector (official GitHub) — https://github.com/pgvector/pgvector
- FAISS wiki (official GitHub wiki) — https://github.com/facebookresearch/faiss/wiki

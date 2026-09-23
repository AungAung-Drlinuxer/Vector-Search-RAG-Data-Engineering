# M5 — PostgreSQL + pgvector: Schema၊ Operator၊ Index နှင့် Tuning

PostgreSQL မှာ pgvector extension နဲ့ vector column တည်ဆောက်ပြီး distance operator နဲ့ index တွေကို ရွေးတဲ့ ပညာရပ်ကို သင်ပါမယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- `vector` column type နဲ့ dimension သတ်မှတ်ပုံ၊ operator class ရွေးပုံ
- Distance operator သုံးမျိုး — `<->` (L2)၊ `<=>` (cosine)၊ `<#>` (inner product) ကွာခြားချက်
- HNSW နဲ့ IVFFlat index နှစ်မျိုးကြားမှာ ဘယ်အချိန် ဘယ်ဟာ ရွေးရမလဲ
- `lists`၊ `m`၊ `ef_construction` setting တွေကို tuning လုပ်ပုံ
- `jsonb` metadata နဲ့ GIN index တွဲသုံးပုံ
- SQL-side filtering နဲ့ index အသုံးပြုမှု၊ `maintenance_work_mem`၊ parallel build
- `EXPLAIN` output ကနေ plan ဖတ်တဲ့အလေ့အကျင့်

## သင်ခန်းစာများ

- 5.1 — `vector` column၊ schema design နဲ့ embedding သိမ်းပုံ
- 5.2 — Distance operator သုံးခုနဲ့ သူတို့ရဲ့ သင်္ချာ
- 5.3 — HNSW vs IVFFlat ရွေးချယ်တဲ့ ဆုံးဖြတ်ချက်
- 5.4 — `lists`၊ `m`၊ `ef_construction` တန်ဖိုးတွေနဲ့ tuning
- 5.5 — `jsonb` metadata + GIN index တွဲဖက်ဖြတ်သန်းမှု
- 5.6 — SQL-side filtering နဲ့ index usage စစ်နည်း
- 5.7 — `maintenance_work_mem`၊ parallel build၊ `EXPLAIN` ဖတ်ခြင်း

## လိုအပ်ချက်များ (Prerequisites)

- M1 မှ M4 အထိ သင်ခန်းစာတွေ ပြီးရှိဖို့ လိုပါမယ်
- SQL အခြေခံ ရှိဖို့ လိုပါတယ် (SELECT၊ WHERE၊ index ဆိုတာ ဘာလဲ ဆိုတာ)
- Python standard library နဲ့ code ဖတ်နိုင်စွမ်း ရှိဖို့ လိုပါမယ်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Retrieval system တစ်ခုကို production မှာ PostgreSQL နဲ့ပဲ တည်ဆောက်ချင်တဲ့ အခါ
- Vector search နဲ့ metadata filter ကို query တစ်ခုတည်းမှာ တွဲချင်တဲ့ အခါ
- Index build ညောင်းခြင်း၊ query နှေးခြင်းကို ဖြေရှင်းချင်တဲ့ အခါ

## ကိုးကား

ဒီ module ရဲ့ နည်းပညာ အချက်အလက်တွေကို ဒီ official documentation တွေကနေ ယူထားပါတယ်။

- pgvector: https://github.com/pgvector/pgvector
- PostgreSQL Index Types: https://www.postgresql.org/docs/current/indexes-types.html
- PostgreSQL GIN: https://www.postgresql.org/docs/current/gin.html
- PostgreSQL Resource Configuration: https://www.postgresql.org/docs/current/runtime-config-resource.html

ဒီသင်ခန်းစာ material တွေက official open documentation ကနေ ကိုယ်တိုင်ရေးထားတဲ့ မူရင်း လေ့လာစာတွေပါ။ အခြားစီးပွားဖြစ် course တစ်ခုခုကို ကူးယူ ရေးထားတာ မဟုတ်ပါဘူး။

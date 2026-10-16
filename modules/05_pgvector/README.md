# M5 — PostgreSQL + pgvector: Schema၊ Operator၊ Index နှင့် Tuning

PostgreSQL တွင် pgvector extension ဖြင့် vector column တည်ဆောက်ခြင်း၊ distance operator နှင့် index ရွေးချယ်ခြင်း၊ tuning ပြုလုပ်ခြင်းတို့ကို လေ့လာသည်။

## ဒီ module မှာ ဘာသင်မလဲ

- `vector` column type၊ dimension သတ်မှတ်ပုံ၊ operator class ရွေးချယ်ပုံ
- Distance operator သုံးမျိုး — `<->` (L2)၊ `<=>` (cosine)၊ `<#>` (inner product) — ၏ ကွာခြားချက်
- HNSW နှင့် IVFFlat index ကြား ရွေးချယ်မှု သတ်မှတ်ချက်များ
- `lists`၊ `m`၊ `ef_construction` setting များ၏ tuning
- `jsonb` metadata နှင့် GIN index တွဲဖက်အသုံးပြုပုံ
- SQL-side filtering နှင့် index အသုံးပြုမှု၊ `maintenance_work_mem`၊ parallel build
- `EXPLAIN` output မှ plan ဖတ်ရှုခြင်း

## သင်ခန်းစာများ

- 5.1 — `vector` column၊ schema design နှင့် embedding သိမ်းဆည်းပုံ
- 5.2 — Distance operator သုံးခုနှင့် ၎င်းတို့၏ သင်္ချာအခြေခံ
- 5.3 — HNSW vs IVFFlat ရွေးချယ်မှု ဆုံးဖြတ်ချက်
- 5.4 — `lists`၊ `m`၊ `ef_construction` တန်ဖိုးများနှင့် tuning
- 5.5 — `jsonb` metadata + GIN index တွဲဖက်အသုံးပြုမှု
- 5.6 — SQL-side filtering နှင့် index usage စစ်ဆေးနည်း
- 5.7 — `maintenance_work_mem`၊ parallel build၊ `EXPLAIN` ဖတ်ရှုခြင်း

## လိုအပ်ချက်များ (Prerequisites)

- M1 မှ M4 အထိ သင်ခန်းစာများ ပြီးမြောက်ထားရန်
- SQL အခြေခံ ရှိရန် (SELECT၊ WHERE၊ index အယူအဆ)
- Python standard library code ဖတ်နိုင်စွမ်း ရှိရန်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Retrieval system တစ်ခုကို production တွင် PostgreSQL ဖြင့် တည်ဆောက်လိုသောအခါ
- Vector search နှင့် metadata filter ကို query တစ်ခုတည်းတွင် တွဲဖက်လိုသောအခါ
- Index build နှေးခြင်း၊ query latency မြင့်ခြင်းတို့ကို ဖြေရှင်းလိုသောအခါ

## ကိုးကား

ဤ module ၏ နည်းပညာ အချက်အလက်များကို အောက်ပါ official documentation များမှ ယူထားသည်။

- pgvector: https://github.com/pgvector/pgvector
- PostgreSQL Index Types: https://www.postgresql.org/docs/current/indexes-types.html
- PostgreSQL GIN: https://www.postgresql.org/docs/current/gin.html
- PostgreSQL Resource Configuration: https://www.postgresql.org/docs/current/runtime-config-resource.html

ဤသင်ခန်းစာ material များသည် official open documentation များမှ ကိုယ်တိုင် ရေးသားထားသော မူရင်း လေ့လာစာများ ဖြစ်ပြီး၊ commercial course တစ်ခုခုကို ကူးယူထားခြင်း မဟုတ်ပါ။
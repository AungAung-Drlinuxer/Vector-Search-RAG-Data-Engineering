# M9 — Data Pipeline နှင့် Orchestration

Vector search system တစ်ခုကို data pipeline နဲ့ orchestration နဲ့ စနစ်တကျ ဆောက်တဲ့ အခြေခံသဘောတရားတွေကို ဒီ module မှာ သင်ပါတယ်။

> ဒီ course ဟာ scope မှာ ဖော်ပြထားတဲ့ official open documentation တွေကနေ ရေးထားတဲ့ original သင်ရိုးညွှန်းတန်း သဘောမျိုးပါ။ အခြား commercial course သင်ခန်းစာတွေကို ပြန်မကူးရေးပါဘူး။

## ဒီ module မှာ ဘာသင်မလဲ

- Batch ingestion (အတန်းလိုက် အုပ်စုလိုက် ထည့်တဲ့နည်း) နဲ့ streaming ingestion (အချိန်နဲ့တပြေးညီ တစ်ကြိမ်ချင်း ထည့်တဲ့နည်း) ရဲ့ ကွာခြားချက်ကို သင်ပါတယ်။
- Idempotent (တစ်ခါထက်ပိုပြန်လုပ်လည်း ရလဒ် အတူတူဖြစ်နေတဲ့သဘော) pipeline ဆိုတာ ဘာကြောင့် လိုအပ်လဲ ဆိုတာကို သင်ပါတယ်။
- Backfill (အရင်ကနေ မှာယူမို့သာ နောက်ကျမှ ပြန်ဖြည့်တဲ့နည်း) နဲ့ rate limit (စနစ်ရဲ့ ကန့်သတ်နှုန်း) ကို ဘယ်လို ထိန်းညှိမလဲ ဆိုတာ လေ့လာပါတယ်။
- Dead-letter (ဖိုင်ပျက်တွေ သီးသန့်ထားတဲ့ နေရာ) နဲ့ retry (ပြန်ကြိုးစားတဲ့) စနစ်ရဲ့ အခြေခံကို နားလည်ပါတယ်။
- Change Data Capture (database အပြောင်းအလဲကို ဖမ်းယူတဲ့နည်း) အခြေခံသဘောကို သင်ပါတယ်။
- Embedding model ပြောင်းတဲ့အခါ migration (dual-write၊ shadow index၊ cut-over) လုပ်နည်းကို သင်ပါတယ်။
- Airflow နဲ့ Dagster ရဲ့ DAG (Directed Acyclic Graph — task တွေရဲ့ မှီခိုမှု ပုံသဏ္ဌာန်) design သဘောတရားကို လေ့လာပါတယ်။

## သင်ခန်းစာများ

| သင်ခန်းစာ | ခေါင်းစဉ် |
|---|---|
| M9.1 | Batch vs Streaming Ingestion — ဘာကြောင့် ကွာခြားလဲ |
| M9.2 | Idempotency နှင့် Backfill — ပြန်လုပ်လည်း ရလဒ် အတူတူ |
| M9.3 | Rate Limit၊ Retry နှင့် Dead-Letter |
| M9.4 | Change Data Capture အခြေခံ |
| M9.5 | Embedding Migration — Dual-Write၊ Shadow Index၊ Cut-over |
| M9.6 | DAG Design — Airflow/Dagster သဘောတရား |

## လိုအပ်ချက်များ (Prerequisites)

- M1 ကနေ M8 အထိ ပြီးနေရပါမယ်။ Python standard library နဲ့ ရေးတဲ့ နည်းကို သိနေရပါမယ်။
- PostgreSQL + pgvector အခြေခံကို M-series အရင် module တွေမှာ တွေ့ပြီးသားဖြစ်ပါမယ်။
- Lesson တွေက runtime မှာ database ချိတ်မပါဘူး။ Retrieval mechanics တွေကို standard-library Python နဲ့ ပြန်ရေးပြပါတယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- စာရွက်စာတမ်း သန်းနဲ့ချီပြီး embedding ထည့်ရမယ့် အခါ ဒီ module က အသုံးဝင်ပါတယ်။
- Embedding model ဟောင်းကို အသစ်ပြောင်းချင်တဲ့အခါ migration စနစ်တကျ လုပ်နိုင်ပါတယ်။
- Pipeline တစ်ခု အလယ်မှာ fail သွားရင် ဘယ်လို ပြန်ထူးမလဲ ဆိုတာ သိနေရင် အချိန်အများကြီး ချွေတာပါတယ်။
- Airflow ဒါမှမဟုတ် Dagster နဲ့ task တွေကို စနစ်တကျ စီမံခန့်ခွဲချင်တဲ့အခါ အသုံးဝင်ပါတယ်။

## ကိုးကား

ဒီ module ရဲ့ technical အချက်အလက်တွေဟာ အောက်ပါ official open documentation တွေကနေ ယူထားပါတယ်။

- Apache Airflow documentation — https://airflow.apache.org/docs/
- Dagster documentation — https://docs.dagster.io/
- pgvector (GitHub) — https://github.com/pgvector/pgvector

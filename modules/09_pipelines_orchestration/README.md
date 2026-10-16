# M9 — Data Pipeline နှင့် Orchestration

Vector search system တစ်ခုကို data pipeline နှင့် orchestration ဖြင့် စနစ်တကျ တည်ဆောက်ရာ၌ လိုအပ်သော အခြေခံသဘောတရားများကို ဤ module တွင် သင်ယူမည်ဖြစ်သည်။

> ဒီ course ဟာ scope မှာ ဖော်ပြထားတဲ့ official open documentation တွေကနေ ရေးထားတဲ့ original သင်ရိုးညွှန်းတမ်းဖြစ်ပါတယ်။ အခြား commercial course သင်ခန်းစာတွေကို ကူးယူရေးသားခြင်း မရှိပါ။

## ဒီ module မှာ ဘာသင်မလဲ

- Batch ingestion နှင့် streaming ingestion တို့၏ ကွာခြားချက်များနှင့် ရွေးချယ်မှု အခြေခံများ။
- Idempotent pipeline ဒီဇိုင်း၏ လိုအပ်ချက် — re-run ဖြစ်တိုင်း တူညီသော result ရရှိစေရန်။
- Backfill နှင့် rate limit ကို ထိန်းညှိပုံ — provider quota အတွင်း ကျစေရန်။
- Dead-letter queue နှင့် retry system အခြေခံများ။
- Change Data Capture (CDC) ၏ အခြေခံသဘောတရား။
- Embedding model ပြောင်းလဲချိန်တွင် migration ဆောင်ရွက်ပုံ — dual-write၊ shadow index၊ cut-over။
- Airflow နှင့် Dagster ၏ DAG design သဘောတရား။

## သင်ခန်းစာများ

| သင်ခန်းစာ | ခေါင်းစဉ် |
|---|---|
| M9.1 | Batch vs Streaming Ingestion — ကွာခြားချက်နှင့် ရွေးချယ်မှု |
| M9.2 | Idempotency နှင့် Backfill — re-run တိုင်း တူညီသော ရလဒ် |
| M9.3 | Rate Limit၊ Retry နှင့် Dead-Letter |
| M9.4 | Change Data Capture အခြေခံ |
| M9.5 | Embedding Migration — Dual-Write၊ Shadow Index၊ Cut-over |
| M9.6 | DAG Design — Airflow/Dagster သဘောတရား |

## လိုအပ်ချက်များ (Prerequisites)

- M1 မှ M8 အထိ module များ ပြီးစီးထားရန်။ Python standard library ဖြင့် ရေးသားနိုင်ရန် လိုအပ်သည်။
- PostgreSQL + pgvector အခြေခံကို အရင် module များတွင် မိတ်ဆက်ပြီးသား ဖြစ်သည်။
- Lesson များသည် runtime တွင် database ချိတ်ဆက်မှု မလိုအပ်ပါ။ Retrieval mechanics များကို standard-library Python ဖြင့် ပြန်လည် implement လုပ်ပြထားသည်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Document သန်းချီကို embedding လုပ်၍ index ထဲ ထည့်သွင်းရန် လိုအပ်သော အခါ။
- Embedding model အဟောင်းမှ အသစ်သို့ migration ကို စနစ်တကျ ဆောင်ရွက်လိုသော အခါ။
- Pipeline fail ဖြစ်ချိန်တွင် မည်သည့်နေရာမှ ပြန်စရမည် ဆုံးဖြတ်ရန် လိုအပ်သော အခါ။
- Airflow သို့ Dagster ဖြင့် task များကို စနစ်တကျ schedule/monitor လုပ်လိုသော အခါ။

## ကိုးကား

ဒီ module ရဲ့ technical အချက်အလက်တွေဟာ အောက်ပါ official open documentation တွေကနေ ယူထားပါတယ်။

- Apache Airflow documentation — https://airflow.apache.org/docs/
- Dagster documentation — https://docs.dagster.io/
- pgvector (GitHub) — https://github.com/pgvector/pgvector

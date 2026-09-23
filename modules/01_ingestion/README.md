# M1 — Corpus Ingestion: ရင်းမြစ်များ၊ Text ဆွဲထုတ်ခြင်း၊ Normalisation နှင့် Upsert/Delete

ဒီ module မှာ RAG စနစ်အတွက် ရင်းမြစ် document တွေကနေ သန့်သန့်ရှင်းရှင်း text ယူပြီး store ထဲ တင်နည်းကို လက်တွေ့ သင်ပါတယ်။

> ဒီသင်ရိုးညွှန်းတမ်းက စာသင်ခန်းမှ ကူးယူထားတာ မဟုတ်ပါဘူး။ ဒီ module scope မှာ ဖော်ပြထားတဲ့ official documentation တွေကို အခြေခံပြီး ကိုယ်တိုင်ရေးထားတဲ့ မူရင်း လေ့လာသင်ယူမှု material ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- ရင်းမြစ် အမျိုးအစားများ — PDF၊ HTML၊ Markdown၊ database row — ရဲ့ ခြားနားချက်တွေကို နားလည်ပါတယ်။
- Text extraction လုပ်တဲ့အခါ boilerplate (header၊ footer၊ navigation စတဲ့ မလိုအပ်တဲ့ စာသား) ဖယ်ရှားနည်း သင်ပါတယ်။
- Unicode normalization (စာလုံးတွေကို စံတစ်ခုတည်း ညီအောင် ပြောင်းခြင်း) အရေးကြီးပုံကို မြင်ပါတယ်။
- Hash နဲ့ content fingerprint (အကြောင်းအရာရဲ့ ထင်ရှားတဲ့ လက္ခဏာ) သုံးပြီး duplicate စစ်နည်း ကို Python standard library နဲ့ လက်တွေ့ ရေးပါတယ်။
- Upsert (ရှိရင် update၊ မရှိရင် insert) နဲ့ delete ရဲ့ အဓိပ္ပာယ်ကို pgvector ဆိုက်ဘက်ကနေ နားလည်ပါတယ်။
- Ingestion pipeline ကို idempotent (နှစ်ခါ run ရင် ရလဒ်တစ်ခုတည်း ရခြင်း) ဖြစ်အောင် ဖန်တီးနည်း သင်ပါတယ်။

## သင်ခန်းစာများ

1. `lessons/lesson_01_sources.md` — ရင်းမြစ် အမျိုးအစားများ နဲ့ JSON format ရဲ့ အကူးအပြောင်းနည်း
2. `lessons/lesson_02_extraction.md` — Text ဆွဲထုတ်ခြင်း နဲ့ boilerplate ဖယ်ရှားခြင်း
3. `lessons/lesson_03_normalisation.md` — Unicode normalization နဲ့ duplicate စစ်ခြင်း (hash)
4. `lessons/lesson_04_upsert_delete.md` — Incremental update၊ deletion semantics နဲ့ idempotency

## လိုအပ်ချက်များ (Prerequisites)

- Python 3 အခြေခံ ရှိဖို့ လိုပါတယ် — list၊ dict၊ function ရေးတတ်ရင် ရပါတယ်။
- Terminal မှာ Python script run တတ်ရင် လုံလောက်ပါတယ်။
- ဒီ course က runtime မှာ database ချိတ်မပါဘူးနော် — အားလုံးကို standard library Python နဲ့ ပြန်ရေးပြထားပါတယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- RAG system တစ်ခု စတည်ဆောက်ချင်တဲ့အခါ အရင်ဆုံး လိုအပ်တာက ingestion pipeline ပါ။
- ရင်းမြစ် document တွေ ပြန်လည် update ဖြစ်နေတဲ့ production စနစ်တွေမှာ duplicate နဲ့ stale data (ဟောင်းနေတဲ့ data) ပြဿနာကို ဖြေရှင်းပေးပါတယ်။
- Airflow တို့၊ batch job တို့နဲ့ pipeline schedule လုပ်ဖို့ အခြေခံ နားလည်မှု ပေးပါတယ်။

## ကိုးကား

ဒီ module ရဲ့ technical အချက်အလက်တွေကို အောက်ပါ official documentation တွေကနေ ယူထားပါတယ် —

- PostgreSQL JSON types: https://www.postgresql.org/docs/current/datatype-json.html
- Hugging Face Datasets documentation: https://huggingface.co/docs/datasets/index
- Apache Airflow documentation: https://airflow.apache.org/docs/

PostgreSQL နဲ့ pgvector ကို target လုပ်ထားပေမယ့် သင်ခန်းစာထဲမှာ SQL ကို run မပါဘူးနော် — ဖတ်ပြီး နားလည်ဖို့ပဲ ပြထားပါတယ်။

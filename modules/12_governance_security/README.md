# M12 — Governance နှင့် လုံခြုံရေး: PII၊ ACL၊ Multi-tenancy နှင့် Audit

Vector search system တစ်ခုမှာ data လုံခြုံရေး၊ ခွင့်ပြုချက် စီမံခြင်း နှင့် မှတ်တမ်းတင်ခြင်း တွေကို ဘယ်လို ဆောက်ရမလဲ ဆိုတာကို သင်ပေးပါတယ်။

> ဒီ course ရဲ့ ပါဝင်ပစ္စည်းတွေကို official open documentation တွေကနေ ကိုယ်ပိုင်ရေးသားထားတဲ့ လေ့လာသင်ယူမှု ပစ္စည်းတွေပါ။ အခြား commercial course တစ်ခုခုကို မကူးယူထားပါဘူး။

## ဒီ module မှာ ဘာသင်မလဲ

- Embedding (သတင်းအချက်အလက်ကို ဂဏန်း array အဖြစ်ပြောင်းထားတာ) ထဲမှာ PII (ကိုယ်ရေးအချက်အလက် — နာမည်၊ ဖုန်းနံပါတ်၊ မှတ်ပုံတင်) ကျန်နေတဲ့ အန္တရာယ် နဲ့ သတိပြုရမည့် အချက်တွေ
- PostgreSQL pgvector ရဲ့ row-level security (RLS) နည်းနဲ့ document-level ACL (ခွင့်ပြုချက် စာရင်း) ကို retrieval query ထဲ ထည့်တဲ့ နည်း
- Multi-tenancy (customer တစ်ယောက်ချင်းစီ အချက်အလက်တွေ ခွဲခြား သိမ်းဆည်းတဲ့ စနစ်) isolation လုပ်တဲ့ နည်းလမ်း သုံးမျိုး
- Audit log (ဘယ်သူက ဘာကို ဘယ်အချိန်မှာ ကြည့်ခဲ့လဲ ဆိုတဲ့ မှတ်တမ်း) နဲ့ access မှတ်တမ်း တင်ပုံ
- Data retention (အချက်အလက် သိမ်းဆည်းချိန်ကာလ) နဲ့ delete ပြဋ္ဌာန်းချက် ဆွဲပုံ
- Provenance (data အရင်းအမြစ်) နဲ့ license (အသုံးပြုခွင့် စာချုပ်) မှတ်တမ်း တင်ပုံ
- Ragas ရဲ့ test set နဲ့ evaluation doc တွေကို governance စစ်ဆေးရာမှာ ဘယ်လို အသုံးချမလဲ

## သင်ခန်းစာများ

1. **L01 — Embedding ထဲ ကျန်နေတဲ့ PII**: ဘာကြောင့် embedding က PII ကို ဖယ်ရှားမပေးဘူးလဲ၊ ဘယ်အချက်အလက် အမျိုးအစားတွေ အန္တရာယ်ရှိလဲ
2. **L02 — Row-Level Security နဲ့ ACL**: PostgreSQL RLS policy ကို pgvector table ပေါ်မှာ တပ်ဆင်ပုံ၊ SQL fence တွေနဲ့ ကြည့်ရှုပါမယ် (lesson တွေက SQL ကို run မချင်းပါဘူး)
3. **L03 — Multi-tenant Isolation**: tenant column၊ separate schema နဲ့ separate database — သုံးနည်းရဲ့ အားသာချက် အားနည်းချက်တွေ
4. **L04 — Audit Log နဲ့ Access မှတ်တမ်း**: ဘယ် field တွေ သိမ်းသင့်လဲ၊ retention policy နဲ့ ချိတ်ဆက်ပုံ
5. **L05 — Retention၊ Delete နှင့် Provenance**: delete pipeline၊ tombstone (ပယ်ဖျက်ပြီးကြောင်း အမှတ်အသား) အယူအဆ၊ license metadata မှတ်တမ်း
6. **L06 — Lab**: standard-library Python နဲ့ ACL-filtered cosine search (ရှာတဲ့ ရလဒ်တွေကို ခွင့်ပြုချက်အရ စစ်ပြီးမှ ပြတဲ့ နည်း) နဲ့ audit log ကို ပြန်စစ်ဆေးတဲ့ script ရေးပါမယ်

## လိုအပ်ချက်များ (Prerequisites)

- M01 (Vector search အခြေခံ) နဲ့ M06 (pgvector schema) သင်ခန်းစာတွေ ပြီးရပါမယ်
- Python အခြေခံ (function၊ list၊ dict) သိရပါမယ်
- PostgreSQL SQL ဖတ်နိုင်ရပါမယ် — database ချိတ်ဆက်စရာ တော့ မလိုပါဘူး
- Burmese နဲ့ ဖတ်ရလွယ်အောင် နားလည်နိုင်စွမ်း လိုပါတယ်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Company တစ်ခုရဲ့ document တွေက user တွေ အမျိုးမျိုး ကြည့်နိုင်ပါစေ — ဒါပေမယ့် ခွင့်ပြုချက် မတူရင် ဒီ module က စတင်ရမဲ့ အချက်ပါ
- Customer တွေ အများကြီးရှိတဲ့ SaaS product မှာ tenant data ခွဲခြားချင်ရင်
- Privacy rule တွေ (ဥပဒေ၊ စာချုပ်) အရ delete request လက်ခံရင်
- Compliance audit (စည်းမျဉ်းစစ်ဆေးမှု) အတွက် မှတ်တမ်း ပြသရင်

## ကိုးကား

- PostgreSQL Row Security Policies: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- PostgreSQL Text Search Controls (text search ထဲမှာ filter နဲ့ ranking): https://www.postgresql.org/docs/current/textsearch-controls.html
- Ragas (RAG evaluation framework): https://docs.ragas.io/

> ဒီ module မှာပြတဲ့ ဂဏန်းတွေက ကိုယ်တိုင်တွက်ပြထားတဲ့ example တွေသာ ဖြစ်ပြီး၊ real system ရဲ့ benchmark ဂဏန်းတွေ မဟုတ်ပါဘူးနော်။

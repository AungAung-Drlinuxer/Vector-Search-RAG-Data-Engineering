# M11 — Scale နှင့် Performance: Quantization၊ Sharding၊ Rebuild နှင့် Write Throughput

ဒီ module မှာ vector database ကို data အရမ်းကြီးလာတဲ့အချိန်မှာ ဘယ်လို memory ချွေတာပြီး performance ထိန်းညှိမလဲ ဆိုတာကို သင်ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- Scalar၊ binary quantization နဲ့ product quantization (PQ) ရဲ့ အခြေခံကို သင်ပါတယ်။
- Memory ချွေတာရင် recall (ရှာတွေ့မှု အရေအတွက်) ဘယ်လောက်ထိခိုက်လဲ ဆိုတဲ့ အပေးအယူကို နားလည်ပါတယ်။
- Vector ရဲ့ dimension ကို ဖြတ်ခြင်းက memory အပေါ် ဘယ်လိုသက်ရောက်လဲ ဆွေးနွေးပါတယ်။
- Sharding (data ကို အစိတ်စိတ် ခွဲသိမ်းခြင်း) နဲ့ partitioning မဟာဗျူဟာတွေကို လေ့လာပါတယ်။
- Index rebuild နဲ့ write throughput (ရေးသွင်းမှု အရေအတွက် per စက္ကန့်) အကြောင်း သင်ပါတယ်။
- Bulk load (data အများကြီးကို တစ်ပြိုင်တည်း ရေသွင်းခြင်း) ရဲ့ "build after load" နည်းလမ်းကို လက်တွေ့ လေ့ကျင့်ပါတယ်။

## သင်ခန်းစာများ

- **11.1 — Quantization ဆိုတာ ဘာလဲ:** scalar၊ binary quantization အခြေခံ၊ memory တွက်ချက်မှုတွေ ပါတယ်။
- **11.2 — Product Quantization (PQ):** Jégou et al. 2011 စာတမ်းအရ PQ ရဲ့ codebook သဘောကို standard-library Python နဲ့ ပြန်ဆောက်ပြပါမယ်။
- **11.3 — Memory နဲ့ Recall အပေးအယူ:** quantization လုပ်ပြီးရင် recall@k ဘယ်လိုကျလဲ ကို တိုင်းတာပြပါမယ်။
- **11.4 — Dimension ဖြတ်ခြင်း နှင့် Sharding:** dimension ဖြတ်တဲ့အကျိုးသွား၊ sharding နည်းလမ်းတွေကို လေ့လာပါတယ်။
- **11.5 — Rebuild၊ Write Throughput နဲ့ Bulk Load:** index rebuild အချိန်၊ bulk load ရဲ့ "load ပြီးမှ indexဆောက်" နည်းကို pgvector SQL နဲ့ ပြပါမယ်။

## လိုအပ်ချက်များ (Prerequisites)

- M1–M5 ရဲ့ cosine similarity၊ HNSW-style graph search နဲ့ recall@k အသိပညာတွေ လိုပါတယ်။
- Python standard library (math, random, struct) အသုံးပြုနိုင်ရပါမယ်။
- PostgreSQL နဲ့ pgvector SQL ဖတ်နိုင်ဖို့ M8–M9 က အခြေခံ လိုပါတယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Vector အရေအတွက် သန်းပေါင်းများစွာ ရှိလာပြီး memory ကုန်ကျစရိတ် ကြီးလာတဲ့အချိန်မှာ အသုံးဝင်ပါတယ်။
- ရှာဖွေမှု မြန်အောင် index ထပ်ဆောက်ရမယ့်အခါ၊ bulk load လုပ်ရမယ့်အခါမှာ လမ်းညွှန်ပေးပါတယ်။
- Production RAG system ရဲ့ hardware cost ကို ချွေတာချင်တဲ့ data engineer တိုင်းအတွက် အရေးကြီးပါတယ်။

## ကိုးကား

- Jégou et al., "Product Quantization for Nearest Neighbor Search" — https://arxiv.org/abs/0903.2314
- Qdrant Quantization Guide — https://qdrant.tech/documentation/guides/quantization/
- FAISS Wiki — https://github.com/facebookresearch/faiss/wiki
- pgvector Performance Notes — https://github.com/pgvector/pgvector#performance

---

**Originality:** ဒီသင်ရိုးညွှန်းတမ်းက official open documentation တွေကနေ ကိုယ်တိုင်ရေးသားတဲ့ မူရင်း သင်ခန်းစာဖြစ်ပြီး၊ အခြား commercial course တွေရဲ့ သင်ခန်းစာတွေကို ကူးယူခြင်း မပြုပါဘူး။

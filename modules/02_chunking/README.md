# M2 — Chunking မဟာဗျူဟာများနှင့် Metadata ဒီဇိုင်း

Documents တွေကို chunk အသေးအလတ်ခွဲပြီး retrieval အရည်အသွေး မြင့်အောင် လုပ်နည်း သင်ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- Fixed-size၊ recursive၊ token-based၊ semantic chunking ဆိုတဲ့ နည်းလမ်း ၄ မျိုး ကွာခြားပုံ
- Overlap (chunk တွေ ထပ်နေတဲ့ အပိုင်း) ဘာကြောင့် လိုအပ်ပြီး ဘယ်လောက် ရွေးရမလဲ
- Chunk အရွယ်နဲ့ retrieval quality ကြားမှာ အပေးအယူ (trade-off)
- Heading နှင့် document structure ကို ထိန်းသိမ်းခြင်း
- Small-to-big retrieval — chunk အသေးနဲ့ ရှာပြီး context အကြီး ပြန်ယူနည်း
- Parent-child chunking အလုပ်လုပ်ပုံ
- Chunk metadata — source၊ section၊ page၊ permission — ဒီဇိုင်းချနည်း
- Tokenization အခြေခံ (Hugging Face tokenizers docs အရ)

## သင်ခန်းစာများ

| သင်ခန်းစာ | ဖော်ပြချက် |
|---|---|
| `lessons/01_fixed_size_chunking.py` | အရွယ်အတည်တည် chunk ခွဲနည်း၊ ချို့ယွင်းချက် |
| `lessons/02_recursive_chunking.py` | Paragraph → sentence → word အဆင့်ဆင့် ခွဲနည်း |
| `lessons/03_token_based_chunking.py` | Token အရေအတွက်အလိုက် ခွဲနည်းနှင့် token counter |
| `lessons/04_semantic_chunking.py` | အဓိပ္ပာယ်အလိုက် နယ်ခြား ရှာနည်း (scripted embedder နဲ့) |
| `lessons/05_overlap_tradeoff.py` | Overlap အရွယ်နဲ့ recall@k ဆက်စပ်မှု (offline test) |
| `lessons/06_structure_aware_chunking.py` | Markdown heading တွေ မပျက်အောင် ထိန်းခြင်း |
| `lessons/07_parent_child_small_to_big.py` | Small-to-big retrieval ကို standard library နဲ့ ပြန်လုပ်ခြင်း |
| `lessons/08_metadata_design.py` | Metadata schema ဒီဇိုင်းနှင့် filtering |
| `lessons/09_lab_document_pipeline.py` | ပေါင်းစပ် lab — document တစ်ခု အပြည့် စစ်ဆေးခြင်း |

## လိုအပ်ချက်များ (Prerequisites)

- Python 3.10+ (standard library ပဲ လိုပါတယ် — external package မလိုပါဘူး)
- M1 module — embedding၊ cosine similarity အခြေခံ သိထားရပါမယ်
- Burmese ဖတ်နိုင်ဖို့ တောင်းဆိုချက် မရှိပါဘူး — ဥပမာပြကုဒ် အားလုံး English comments နဲ့ ဖြစ်ပါတယ်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- RAG pipeline စတင်တည်ဆောက်ပြီး documents တွေ ဘယ်လို ခွဲမလဲ ဆုံးဖြတ်ရတဲ့ အချိန်
- Retrieval အရည်အသွေး ကျနေတယ်၊ အဖြေတွေ ပြတ်နေတယ် ဆိုတဲ့ ပြဿနာ ဖြေရှင်းချိန်
- PDF၊ Markdown စတဲ့ structure ရှိတဲ့ documents တွေ ingest လုပ်ချင်တဲ့ အချိန်
- Chunk တွေမှာ permission filtering (ဘယ် user က ဘာကြည့်ရမလဲ) လိုအပ်တဲ့ production စနစ်များ

## ကိုးကား

ဒီ module ရဲ့ technical အချက်အလက်တွေကို အောက်ပါ official documentation တွေကနေ ယူထားပါတယ် —

- LangChain Text Splitters concepts: https://python.langchain.com/docs/concepts/text_splitters/
- LlamaIndex documentation: https://docs.llamaindex.ai/en/stable/
- Hugging Face tokenizers: https://huggingface.co/docs/tokenizers/index

Originality note — ဒီသင်ရိုးညွှန်းတမ်းက original study material ပါ။ Scope မှာ ဖော်ပြထားတဲ့ official documentation တွေကနေ ရေးထားတာပါ။ Commercial course တစ်ခုခုရဲ့ သင်ခန်းစာကို ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ပါဘူးနော်။

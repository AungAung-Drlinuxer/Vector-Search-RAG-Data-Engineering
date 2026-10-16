# M2 — Chunking မဟာဗျူဟာများနှင့် Metadata ဒီဇိုင်း

Document များကို chunk များအဖြစ် ခွဲခြမ်းခြင်းနှင့် retrieval quality မြှင့်တင်ခြင်း နည်းလမ်းများကို လေ့လာသည်။

## ဒီ module မှာ ဘာသင်မလဲ

- Chunking နည်းလမ်း ၄ မျိုး (fixed-size၊ recursive၊ token-based၊ semantic) ၏ ကွာခြားချက်များ
- Overlap ၏ လိုအပ်ချက်နှင့် သင့်လျော်သော overlap size ရွေးချယ်မှု
- Chunk size နှင့် retrieval quality ကြားရှိ trade-off
- Heading နှင့် document structure ကို ထိန်းသိမ်းခြင်း
- Small-to-big retrieval — chunk အသေးဖြင့် retrieve လုပ်ပြီး parent context ကို ပြန်လည်ရယူခြင်း
- Parent-child chunking အလုပ်လုပ်ပုံ
- Chunk metadata (source၊ section၊ page၊ permission) ဒီဇိုင်း
- Tokenization အခြေခံ (Hugging Face tokenizers docs အရ)

## သင်ခန်းစာများ

| သင်ခန်းစာ | ဖော်ပြချက် |
|---|---|
| `lessons/01_fixed_size_chunking.py` | Fixed-size chunking နှင့် ၎င်း၏ ကန့်သတ်ချက်များ |
| `lessons/02_recursive_chunking.py` | Paragraph → sentence → word အဆင့်ဆင့် ခွဲခြမ်းခြင်း |
| `lessons/03_token_based_chunking.py` | Token count အလိုက် chunking နှင့် token counter |
| `lessons/04_semantic_chunking.py` | Semantic boundary ရှာဖွေခြင်း (scripted embedder ဖြင့်) |
| `lessons/05_overlap_tradeoff.py` | Overlap size နှင့် recall@k ဆက်စပ်မှု (offline test) |
| `lessons/06_structure_aware_chunking.py` | Markdown heading structure ထိန်းသိမ်းခြင်း |
| `lessons/07_parent_child_small_to_big.py` | Small-to-big retrieval ကို standard library ဖြင့် တည်ဆောက်ခြင်း |
| `lessons/08_metadata_design.py` | Metadata schema ဒီဇိုင်းနှင့် filtering |
| `lessons/09_lab_document_pipeline.py` | ပေါင်းစပ် lab — end-to-end document pipeline |

## လိုအပ်ချက်များ (Prerequisites)

- Python 3.10+ (standard library သာ လိုအပ်သည် — external package မလိုအပ်ပါ)
- M1 module — embedding နှင့် cosine similarity အခြေခံ သိရှိထားရန်
- Burmese ဖတ်ရှုနိုင်ရန် တောင်းဆိုချက် မရှိပါ — ဥပမာ code အားလုံးတွင် English comments သာ ပါဝင်သည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- RAG pipeline တည်ဆောက်စဉင် document များ၏ chunking မဟာဗျူဟာ ဆုံးဖြတ်ရန်လိုသောအခါ
- Retrieval quality ကျဆင်းခြင်း၊ answer context ပြတ်တောက်ခြင်း စသည့် ပြဿနာများ ဖြေရှင်းရန်
- PDF၊ Markdown ကဲ့သို့ structured document များ ingest လုပ်ရန်
- Chunk အဆင့် permission filtering လိုအပ်သော production စနစ်များအတွက်

## ကိုးကား

ဒီ module ၏ technical အချက်အလက်များကို အောက်ပါ official documentation များမှ ရယူထားသည် —

- LangChain Text Splitters concepts: https://python.langchain.com/docs/concepts/text_splitters/
- LlamaIndex documentation: https://docs.llamaindex.ai/en/stable/
- Hugging Face tokenizers: https://huggingface.co/docs/tokenizers/index

Originality note — ဒီသင်ရိုးညွှန်းတမ်းသည် original study material ဖြစ်သည်။ Scope တွင် ဖော်ပြထားသော official documentation များအပေါ် အခြေခံ၍ ရေးသားထားပြီး၊ commercial course တစ်ခု၏ သင်ခန်းစာများကို ကူးယူခြင်း သို့မဟုတ် ပြန်လည်ရေးသားခြင်း မဟုတ်ပါ။

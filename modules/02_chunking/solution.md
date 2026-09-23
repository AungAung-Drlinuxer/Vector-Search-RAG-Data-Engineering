## လေ့ကျင့်ခန်း ၁ — Fixed-size chunking ကို လက်တွေ့စမ်းကြည့်ပါ

Fixed-size chunking ဆိုတာ စာသားကို စာလုံးအရေအတွက အတိအထနဲ့ ဖြတ်တာပါ။ ဒီ code မှာ ကိုယ်တိုင်ရေးထားတဲ့ စာသားကို ၅၀ စာလုံးစီနဲ့ ဖြတ်ပြထားတာပါ။ chunk တိုင်းရဲ့ အရွေအတိအထကို len() နဲ့ စစ်ကြည့်လို့ ရပါတယ်နော်။

```python
# Fixed-size chunking: split text into chunks of exactly 50 words each.
sample_text = (
    "Vector search systems need text split into chunks before embedding. "
    "Fixed-size chunking cuts text at a constant word count, which is simple and fast. "
    "The main drawback is that sentences and paragraphs can be cut in the middle. "
    "A chunk boundary may fall between related words, losing local context. "
    "This exercise demonstrates the behavior with a plain Python implementation. "
    "We count words using str.split and slice the list with fixed steps. "
    "Every chunk except possibly the last one should contain exactly fifty words. "
    "The last chunk holds whatever words remain after the final full cut."
)

words = sample_text.split()
CHUNK_SIZE = 50

chunks = []
for i in range(0, len(words), CHUNK_SIZE):
    chunks.append(" ".join(words[i:i + CHUNK_SIZE]))

for idx, chunk in enumerate(chunks):
    print(f"chunk {idx}: {len(chunk.split())} words")
    print(chunk)
    print("---")
# Expected output:
# chunk 0: 50 words
# Vector search systems need text split into chunks before embedding. Fixed-size chunking cuts text at a constant word count, which is simple and fast. The main drawback is that sentences and paragraphs can be cut in the middle. A chunk boundary may fall between related words, losing local context. This
# ---
# chunk 1: 45 words
# exercise demonstrates the behavior with a plain Python implementation. We count words using str.split and slice the list with fixed steps. Every chunk except possibly the last one should contain exactly fifty words. The last chunk holds whatever words remain after the final full cut.
# ---
```

**အဓိကအယူဆ** — Fixed-size chunking က ရိုးရိုးရှင်းရှင်း မြန်ပေမယ့် စာကြောင်းနယ်နိမိတ် မထိန်းနိုင်တဲ့အတွက် အဓိပ္ပာယ် ပျက်ကွဲမှု ခံရတတ်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Overlap ထည့်ပြီး စာကြောင်းပျက်မှု ကာကွယ်ပါ

Overlap မပါတဲ့ chunking မှာ ဝါကျတစ်ချောင်း နှစ်ပိုင်းကွဲသွားတာ မြင်ရပြီး၊ overlap ထည့်ရင် ထပ်နေတဲ့ စာလုံးများကြောင့် အဓိပ္ပာယ် ဆက်နေတာ မြင်ရပါတယ်။ step ကို `chunk_size - overlap` သုံးရတာ အရေးကြီးပါတယ်နော်။

```python
# Compare fixed-size chunking with and without overlap.
text = (
    "The deployment pipeline failed because the embedding service timed out "
    "and the retry logic was missing from the worker script."
)

words = text.split()
CHUNK_SIZE = 30
OVERLAP = 10

# No overlap: step = chunk_size (words can be cut mid-sentence across chunks)
step = CHUNK_SIZE
no_overlap = [" ".join(words[i:i + CHUNK_SIZE]) for i in range(0, len(words), step)]

# With overlap: step = chunk_size - overlap (repeated words bridge the gap)
step = CHUNK_SIZE - OVERLAP
with_overlap = []
for i in range(0, len(words), step):
    piece = words[i:i + CHUNK_SIZE]
    with_overlap.append(" ".join(piece))
    if i + CHUNK_SIZE >= len(words):
        break

print("=== No overlap (chunk size 30, overlap 0) ===")
for idx, c in enumerate(no_overlap):
    print(f"chunk {idx}: {c}")

print("\n=== With overlap (chunk size 30, overlap 10) ===")
for idx, c in enumerate(with_overlap):
    print(f"chunk {idx}: {c}")
# Expected output:
# === No overlap (chunk size 30, overlap 0) ===
# chunk 0: The deployment pipeline failed because the embedding service timed out and the retry logic was missing from the worker script.
# 
# === With overlap (chunk size 30, overlap 10) ===
# chunk 0: The deployment pipeline failed because the embedding service timed out and the retry logic was missing from the worker script.
```

**အဓိကအယူဆ** — Overlap က chunk နယ်နိမိတ်မှာ စာသား ထပ်ဆောင်းပေးခြင်းအားဖြင့် ဝါကျပျက်ကွဲမှုကို သက်သာစေပြီး retrieval အရည်အသွေး ပိုကောင်းစေပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Recursive text splitting အလုပ်လုပ်ပုံ ပြန်ရေးပါ

Recursive splitter က separator စာရင်းကို အဆင့်ဆင်းပြီး ဝါကျနယ်နိမိတ်ကို ဖြတ်တောင်း ထိန်းပေးတဲ့ နည်းပါ။ separator တစ်ခုမကျော်ရင် နောက်တစ်ခုဆီ ဆင်းသွားတဲ့ logic ကို ဒီ function မှာ မြင်နိုင်ပါတယ်နော်။

```python
# Reimplementation of recursive text splitting (LangChain-style, simplified).
import math

SEPARATORS = ["\n\n", "\n", ". ", " "]
CHUNK_SIZE = 60
log = []  # records which separator level was used for each split

def recursive_split(text, chunk_size=CHUNK_SIZE):
    if len(text) <= chunk_size:
        return [text]
    # Try each separator in priority order; use the first one that appears in text
    for level, sep in enumerate(SEPARATORS):
        if sep in text:
            parts = text.split(sep)
            log.append(f"used separator {sep!r} (level {level})")
            chunks = []
            current = ""
            for part in parts:
                candidate = (current + sep + part) if current else part
                if len(candidate) <= chunk_size:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    # Recursively split the oversized piece with lower-priority separators
                    chunks.extend(recursive_split(part, chunk_size))
                    current = ""
            if current:
                chunks.append(current)
            return [c.strip(sep) for c in chunks if c.strip(sep)]
    # No separator matched: hard cut (worst case)
    log.append("hard cut, no separator matched")
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

doc = (
    "Vector search indexes chunks for fast retrieval.\n\n"
    "Recursive splitting tries paragraph breaks first, then line breaks, then sentences, "
    "then spaces. Each chunk stays below the size limit while keeping natural boundaries. "
    "This keeps sentences intact far more often than fixed-size cutting does."
)

chunks = recursive_split(doc)
for i, c in enumerate(chunks):
    print(f"chunk {i} ({len(c)} chars): {c}")

print("\nSplit trace:")
for entry in log:
    print(entry)
# Expected output:
# chunk 0 (48 chars): Vector search indexes chunks for fast retrieval.
# chunk 1 (59 chars): Recursive splitting tries paragraph breaks first, then line
# chunk 2 (7 chars): breaks,
# chunk 3 (27 chars): then sentences, then spaces
# chunk 4 (59 chars): Each chunk stays below the size limit while keeping natural
# chunk 5 (10 chars): boundaries
# chunk 6 (58 chars): This keeps sentences intact far more often than fixed-size
# chunk 7 (7 chars): cutting
# chunk 8 (4 chars): does
# 
# Split trace:
# used separator '\n\n' (level 0)
# used separator '. ' (level 2)
# used separator ' ' (level 3)
# used separator ' ' (level 3)
# used separator ' ' (level 3)
```

**အဓိကအယူဆ** — Separator တွေကို သဘာဝအမှတ်အသား အစဉ်အလိုက် အဆင့်ဆင်းသုံးတဲ့ recursive splitting က ဝါကျပျက်မှုကို သိသိသာသာ လျှော့ပေးပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Token-based chunking နဲ့ ဂဏန်းခြင်း

Token နဲ့ စာလုံးရဲ့ ကွာခြားချက်ကို simple tokenizer တစ်ခုနဲ့ တွက်ပြပြီး၊ chunk အရေအတွကကို formula `1 + ceil((total - chunk) / (chunk - overlap))` နဲ့ တွက်ပါတယ်။ 10,000 tokens၊ chunk 512၊ overlap 64 ဆိုရင် 20 chunks ရတာကို ကိုယ်တိုင် အတည်ပြုနိုင်ပါတယ်နော်။

```python
# Token counting and chunk-count arithmetic (stdlib only, deterministic stand-in tokenizer).
import re
import math

def tokenize(text):
    # Simple deterministic stand-in for a real tokenizer (e.g. Hugging Face tokenizers)
    return re.findall(r"\w+|\S", text)

sample = "Embedding models read text as tokens, not words; e.g. 'vector-search' -> ['vector', '-', 'search']."
tokens = tokenize(sample)
print(f"token count: {len(tokens)}")
print(f"tokens: {tokens}")

# Chunk arithmetic for a 10,000-token ingestion
total_tokens = 10_000
chunk_size = 512
overlap = 64

num_chunks = 1 + math.ceil((total_tokens - chunk_size) / (chunk_size - overlap))
print(f"\ntotal tokens: {total_tokens}, chunk size: {chunk_size}, overlap: {overlap}")
print(f"number of chunks = 1 + ceil(({total_tokens} - {chunk_size}) / ({chunk_size} - {overlap})) = {num_chunks}")

# Verify by simulation: walk the token stream with the same stride
pos = 0
simulated = 0
while pos < total_tokens:
    simulated += 1
    if pos + chunk_size >= total_tokens:
        break
    pos += chunk_size - overlap
print(f"simulated chunk count: {simulated}")
# Expected output:
# token count: 35
# tokens: ['Embedding', 'models', 'read', 'text', 'as', 'tokens', ',', 'not', 'words', ';', 'e', '.', 'g', '.', "'", 'vector', '-', 'search', "'", '-', '>', '[', "'", 'vector', "'", ',', "'", '-', "'", ',', "'", 'search', "'", ']', '.']
# 
# total tokens: 10000, chunk size: 512, overlap: 64
# number of chunks = 1 + ceil((10000 - 512) / (512 - 64)) = 23
# simulated chunk count: 23
```

**အဓိကအယူဆ** — Model ရဲ့ context window နဲ့ ကိုက်အောင် chunk size ကို token အရ တွက်သင့်ပြီး၊ overlap ပါတဲ့ formula နဲ့ ကြိုတွက်လို့ ရပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Parent-child indexing နဲ့ small-to-big retrieval

Small-to-big retrieval မှာ ရှာဖွေတဲ့ချိန်မှာ သေးတဲ့ child chunk တွေနဲ့ စစ်ပြီး၊ ပြန်တင်တဲ့အခါ ကြီးတဲ့ parent paragraph အပြည့်အစုံ ထုတ်ပေးပါတယ်။ child ရလဒ်က `parent_id` နဲ့ parent ဆီ ပြန်ညွှန်တဲ့ ဆက်သွယ်မှုကို ဒီ code မှာ လက်တွေ့စစ်ကြည့်လို့ ရပါတယ်နော်။

```python
# Small-to-big retrieval simulated with plain dicts (no LLM, deterministic keyword scoring).

parents = {
    1: {"parent_id": 1,
        "parent_text": "The ingestion worker normalizes documents, extracts metadata, and writes chunks to the vector store.",
        "children": []},
    2: {"parent_id": 2,
        "parent_text": "The retrieval layer scores candidate chunks with cosine similarity and re-ranks them before generation.",
        "children": []},
}
children = []
for pid, p in parents.items():
    for sentence in p["parent_text"].split(". "):
        if sentence.strip():
            child = {"child_id": len(children) + 1, "parent_id": pid, "child_text": sentence.strip()}
            children.append(child)
            p["children"].append(child["child_id"])

def search(query, children, parents):
    # Deterministic stand-in for semantic search: exact keyword containment scoring
    keywords = query.lower().split()
    scored = []
    for c in children:
        text = c["child_text"].lower()
        score = sum(1 for k in keywords if k in text)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1]["child_id"]))
    if not scored:
        print(f"No child matched query: {query!r}")
        return None
    best_score, best_child = scored[0]
    parent = parents[best_child["parent_id"]]
    print(f"Query: {query!r}")
    print(f"Matched child (score {best_score}): {best_child['child_text']}")
    print(f"Small-to-big -> returning parent {parent['parent_id']}:")
    print(parent["parent_text"])
    return parent

search("re-ranks candidate chunks", children, parents)
# Expected output:
# Query: 're-ranks candidate chunks'
# Matched child (score 3): The retrieval layer scores candidate chunks with cosine similarity and re-ranks them before generation.
# Small-to-big -> returning parent 2:
# The retrieval layer scores candidate chunks with cosine similarity and re-ranks them before generation.
```

**အဓိကအယူဆ** — ရှာဖွေမှု precision ကို သေးတဲ့ child ကနေ ရယူပြီး ပြန်တင်တဲ့ context ကို ကြီးတဲ့ parent ကနေ ပေးတဲ့ small-to-big နည်းက နှစ်ဘက်စလုံး အားသာစေပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Chunk metadata ဒီဇိုင်းနဲ့ permission filter

Chunk metadata မှာ `source`, `section`, `page`, `permission`, `chunk_index` တွေ ပါစေရပြီး၊ retrieval မှာ permission မကိုက်တဲ့ user အတွက် secret document ကို filtered-out လုပ်ပြပါတယ်။ cosine similarity အစစ်အစား deterministic keyword score နဲ့ အစားထိုးထားပါတယ်နော်။

```python
# Chunk metadata schema + permission-filtered retrieval simulation (deterministic keyword score).

def make_chunk(chunk_id, source, section, page, permission, chunk_index, text):
    return {"id": chunk_id, "source": source, "section": section,
            "page": page, "permission": permission, "chunk_index": chunk_index, "text": text}

chunks = [
    make_chunk(1, "public_handbook.pdf", "Onboarding", 3, "public", 0,
               "New engineers follow the onboarding checklist in the public handbook."),
    make_chunk(2, "finance_secret.xlsx", "Payroll", 12, "finance", 0,
               "Payroll credentials are stored in the finance secret vault."),
    make_chunk(3, "public_handbook.pdf", "Onboarding", 4, "public", 1,
               "Access requests are filed through the standard ticketing workflow."),
]

def score(query, text):
    # Deterministic stand-in for cosine similarity: keyword overlap count
    return sum(1 for k in query.lower().split() if k in text.lower())

def filter_(allowed, chunks):
    # Pure function: keep only chunks whose permission is in the allowed set
    return [c for c in chunks if c["permission"] in allowed]

def retrieve(query, allowed, chunks, top_k=2):
    visible = filter_(allowed, chunks)
    scored = sorted(((score(query, c["text"]), c) for c in visible),
                    key=lambda x: (-x[0], x[1]["id"]))[:top_k]
    return [c for s, c in scored if s > 0]

query = "payroll credentials access"
for user, allowed in [("admin", {"public", "finance"}), ("guest", {"public"})]:
    print(f"== {user} (allowed: {sorted(allowed)}) ==")
    results = retrieve(query, allowed, chunks)
    if not results:
        print("  (no results)")
    for c in results:
        print(f"  {c['source']} p{c['page']} sec={c['section']} perm={c['permission']} "
              f"idx={c['chunk_index']} :: {c['text'][:60]}...")
# Expected output:
# == admin (allowed: ['finance', 'public']) ==
#   finance_secret.xlsx p12 sec=Payroll perm=finance idx=0 :: Payroll credentials are stored in the finance secret vault....
#   public_handbook.pdf p4 sec=Onboarding perm=public idx=1 :: Access requests are filed through the standard ticketing wor...
# == guest (allowed: ['public']) ==
#   public_handbook.pdf p4 sec=Onboarding perm=public idx=1 :: Access requests are filed through the standard ticketing wor...
```

**အဓိကအယူဆ** — Permission စတဲ့ metadata ကို index အဆင့်မှာ filter လုပ်တာဟဲ့ access control ကို retrieval ရလဒ်မှာ တိုက်ရိုက် အာမခံပေးပါတယ်။

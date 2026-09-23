## လေ့ကျင့်ခန်း ၁ — ef_search ပြောင်းပြီး recall တိုင်းချက်

Brute-force cosine search ကို gold အဖြေအဖြစ် ယူပြီး `ef_search` ကို ၁၀၊ ၂၅၊ ၅၀ လုပ်ကြည့်တဲ့အခါ recall@10 ဘယ်လိုပြောင်းလဲ ကြည့်ပါတယ်။

```python
import math

# Deterministic demo: brute-force cosine search is the gold answer,
# a graph search is simulated by only looking at the first ef_search candidates.
docs = [
    ("doc-a", [1.0, 0.0, 0.0]), ("doc-b", [0.9, 0.1, 0.0]), ("doc-c", [0.0, 1.0, 0.0]),
    ("doc-d", [0.0, 0.9, 0.1]), ("doc-e", [0.0, 0.0, 1.0]), ("doc-f", [0.8, 0.2, 0.0]),
    ("doc-g", [0.2, 0.8, 0.0]), ("doc-h", [0.0, 0.2, 0.8]), ("doc-i", [0.6, 0.0, 0.8]),
    ("doc-j", [0.1, 0.1, 0.9]), ("doc-k", [0.5, 0.5, 0.0]), ("doc-l", [0.0, 0.5, 0.5]),
]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


query = [1.0, 0.0, 0.0]
ranked = sorted(docs, key=lambda item: cosine(query, item[1]), reverse=True)
gold = [name for name, _ in ranked[:10]]
visit_order = ["doc-a", "doc-b", "doc-f", "doc-k", "doc-c", "doc-g", "doc-d", "doc-l", "doc-e", "doc-i",
               "doc-h", "doc-j"]

print("gold top-10:", gold[:5], "...")
for ef in (10, 25, 50):
    seen = visit_order[:min(ef, len(visit_order))]
    recall = len(set(seen) & set(gold)) / 10
    print(f"ef_search={ef:2d}  candidates scored={len(seen):2d}  recall@10={recall:.2f}")
# Expected output:
# gold top-10: ['doc-a', 'doc-b', 'doc-f', 'doc-k', 'doc-i'] ...
# ef_search=10  candidates scored=10  recall@10=0.90
# ef_search=25  candidates scored=12  recall@10=1.00
# ef_search=50  candidates scored=12  recall@10=1.00
```

**အဓိကအယူအဆ** — `ef_search` တက်ရင် recall တက်ပေမဲ့ score လုပ်ရတဲ့ candidate အရေအတွက်လည်း တက်တာမို့ recall နဲ့ latency က အပေးအယူ ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — M parameter ရဲ့ သက်ရောက်မှု

Node တစ်ခုချင်းစီမှာ edge အများဆုံး M ခု ထားတဲ့အခါ edge အရေအတွက်နဲ့ graph memory ဘယ်လောက်တက်လဲ တွက်ကြည့်ပါတယ်။

```python
# Edge-count model for M: each node keeps at most M neighbours, so edges ~= nodes * M.
NODES = 1000                      # assumption: 1,000 nodes
print("assumption: 1,000 nodes")
for m in (5, 15, 30):
    edges = NODES * m             # one directed edge per (node, neighbour) slot
    graph_bytes = edges * 8       # 8 bytes per neighbour id (int64)
    print(f"M={m:2d}  edges={edges:6d}  graph memory={graph_bytes / 1024 ** 2:5.2f} MiB")
# Expected output:
# assumption: 1,000 nodes
# M= 5  edges=  5000  graph memory= 0.04 MiB
# M=15  edges= 15000  graph memory= 0.11 MiB
# M=30  edges= 30000  graph memory= 0.23 MiB
```

**အဓိကအယူအဆ** — M က edge အရေအတွက်ကို တိုက်ရိုက် တိုးစေတာမို့ memory နဲ့ build time ကို ထိပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Index memory တွက်နည်း

Chunk ၁ သန်း၊ 768 dimension အတွက် vector storage နဲ့ HNSW graph memory ကို ပေါင်းတွက်ပြပါတယ်။

```python
# Index memory: vector storage plus the HNSW graph layer.
n_vectors = 1_000_000            # assumption: 1 chunk = 1 vector
dim = 768                        # assumption: 768-dimensional embedding
bytes_per_value = 4              # fp32

vectors_bytes = n_vectors * dim * bytes_per_value
for m in (16, 32):
    graph_bytes = n_vectors * m * 8      # 8 bytes per neighbour id (int64)
    total = vectors_bytes + graph_bytes
    print(f"M={m:2d}  vectors={vectors_bytes / 1024 ** 3:6.2f} GiB  graph={graph_bytes / 1024 ** 3:5.2f} GiB"
          f"  total={total / 1024 ** 3:6.2f} GiB")
# Expected output:
# M=16  vectors=  2.86 GiB  graph= 0.12 GiB  total=  2.98 GiB
# M=32  vectors=  2.86 GiB  graph= 0.24 GiB  total=  3.10 GiB
```

**အဓိကအယူအဆ** — Index memory ကို vector အပိုင်းနဲ့ graph အပိုင်း ခွဲတွက်တာက capacity planning ရဲ့ အခြေခံပါ။

## လေ့ကျင့်ခန်း ၄ — Multi-layer graph simulation

Layer နှစ်လွှာ ရှိတဲ့ graph တစ်ခုမှာ အပေါ်လွှာကနေ အောက်လွှာကို ဆင်းလာတဲ့ hop အရေအတွက် simulate လုပ်ပြပါတယ်။

```python
# Two-layer graph: greedy descent from the upper layer into the lower one (toy graph).
layer1 = {"entry": ["far"], "far": ["mid"], "mid": ["near"], "near": []}
layer0 = {"near": ["x", "y"], "x": ["target"], "y": [], "target": [], "far": [], "mid": []}


def hops(graph, start, goal):
    """Breadth-first hop count; -1 when unreachable."""
    queue, seen = [(start, 0)], {start}
    while queue:
        node, depth = queue.pop(0)
        if node == goal:
            return depth
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, depth + 1))
    return -1


print("upper layer entry -> near:", hops(layer1, "entry", "near"), "hops")
print("lower layer near -> target:", hops(layer0, "near", "target"), "hops")
print("upper layer entry -> target (wrong layer):", hops(layer1, "entry", "target"))
# Expected output:
# upper layer entry -> near: 3 hops
# lower layer near -> target: 2 hops
# upper layer entry -> target (wrong layer): -1
```

**အဓိကအယူအဆ** — Layer ခွဲထားတာက အဝေးကို ခုန်ပြီး ရောက်စေတာမို့ hop အရေအတွက် လျော့ပြီး အမြန်ဖြစ်စေပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Filtered search ရဲ့ recall ဆုံးရှုံးမှု

Tenant filter ထည့်တဲ့အခါ traversal ရောက်နိုင်တဲ့ candidate လျော့သွားပြီး recall ဘယ်လိုပြောင်းလဲ တိုင်းကြည့်ပါတယ်။

```python
# Filtered search: a tenant filter removes candidates the unfiltered traversal would have returned.
tenant_of = {f"doc-{i}": ("tenant-a" if i % 2 == 0 else "tenant-b") for i in range(1, 11)}
gold = ["doc-2", "doc-5", "doc-6", "doc-7", "doc-10"]          # true top-5 (assumed), mixed tenants
graph_order = [f"doc-{i}" for i in (2, 5, 3, 6, 8, 7, 10, 1, 4, 9)]   # traversal order (assumed)


def recall(tenant=None, k=5):
    """Recall@k of the first k reachable candidates against the global gold set."""
    pool = [n for n in graph_order if tenant is None or tenant_of[n] == tenant]
    seen = pool[:k]
    return len(set(seen) & set(gold)) / k, len(pool)


r, n = recall()
print(f"no filter       : reachable={n:2d}  recall@5={r:.2f}")
for t in ("tenant-a", "tenant-b"):
    r, n = recall(t)
    print(f"filter {t} : reachable={n:2d}  recall@5={r:.2f}")
print("note: filtering is required for permission safety; it deliberately removes candidates,")
print("      so recall must be judged against a tenant-scoped gold set, not the global one.")
# Expected output:
# no filter       : reachable=10  recall@5=0.60
# filter tenant-a : reachable= 5  recall@5=0.60
# filter tenant-b : reachable= 5  recall@5=0.40
# note: filtering is required for permission safety; it deliberately removes candidates,
#       so recall must be judged against a tenant-scoped gold set, not the global one.
```

**အဓိကအယူအဆ** — Filter က permission အတွက် မဖြစ်မနေလိုပြီး၊ recall ကို tenant-scoped gold set နဲ့ တိုင်းရပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Delete/update ရဲ့ ဆိုးကျိုးနဲ့ restore စစ်ဆေးခြင်း

Node delete လုပ်ပြီးနောက် recall ကျဆင်းတာနဲ့ rebuild လုပ်ပြီးနောက် ပြန်ကောင်းလာတာကို တိုင်းပြပါတယ်။

```python
# Delete/update: removing a node shrinks what the traversal can reach; a rebuild restores recall.
present = {f"n{i}": True for i in range(6)}
gold = {"n0", "n1", "n2", "n3", "n4"}


def graph_recall(state, k=5):
    reachable = [n for n, alive in state.items() if alive][:k]
    return len(set(reachable) & gold) / k


before = graph_recall(present)
for dead in ("n4", "n3"):
    present[dead] = False
after = graph_recall(present)
rebuilt = {f"n{i}": True for i in range(6)}                  # after a full rebuild
print(f"before delete : recall@5={before:.2f}")
print(f"after deletes : recall@5={after:.2f}")
print(f"after rebuild : recall@5={graph_recall(rebuilt):.2f}")
# Expected output:
# before delete : recall@5=1.00
# after deletes : recall@5=0.60
# after rebuild : recall@5=1.00
```

**အဓိကအယူအဆ** — Delete/update များလာရင် graph အရည်အသွေး ကျတာမို့ ပြန်ဆောက်တဲ့ (rebuild) အစီအစဉ် ထားရပါတယ်။

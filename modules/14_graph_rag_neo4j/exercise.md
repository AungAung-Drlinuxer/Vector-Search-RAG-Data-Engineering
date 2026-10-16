## လေ့ကျင့်ခန်း ၁ — Property Graph Schema ဒီဇိုင်းနှင့် Cypher Statements တည်ဆောက်ခြင်း

Entities များကို Nodes (Labels, Properties) အဖြစ်လည်းကောင်း၊ ဆက်သွယ်ချက်များကို Directed Typed Relationships (Edges, Properties) အဖြစ်လည်းကောင်း ကိုယ်စားပြုသော Property Graph data structure ကို Python ဖြင့် တည်ဆောက်ပြီး Neo4j Cypher `MERGE` statements များကို generate လုပ်ပါ။

**Hints:** Node တစ်ခုစီတွင် unique identifier, primary label နှင့် properties dict ပါဝင်ရမည်။ Relationship တွင် source node id, target node id, relationship type (ဥပမာ `CONNECTS_TO`, `MONITORS`) ပါဝင်ရမည်။ Cypher statement များသည် `MERGE (n:Label {id: $id})` format နှင့် ကိုက်ညီရမည်။

**Expected behavior:** In-memory graph structure မှ valid Neo4j Cypher DDL / DML string statements များကို generate လုပ်ပြီး nodes နှင့် edges counts ကို verify လုပ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — Text Chunks မှ Triples Extraction နှင့် Entity Resolution

Unstructured text chunk များမှ Subject-Predicate-Object (SPO) factual triples များကို extract လုပ်ပြီး near-identical entity names များကို canonical entity id တစ်ခုတည်းအဖြစ် resolve ပြုလုပ်သည့် entity resolution gate ကို implement လုပ်ပါ။

**Hints:** Real world တွင် "AWS", "Amazon Web Services", "aws" စသည့် variants များကို identical node id `"AWS"` အဖြစ် normalize ပြုလုပ်ရန် လိုအပ်သည်။ Entity resolution မပါဝင်ပါက graph တွင် duplicate disconnected nodes များ ဖြစ်ပေါ်ကာ reasoning ကျိုးပေါက်နိုင်သည်။

**Expected behavior:** Raw text မှ triples များကို extract လုပ်ပြီး alias mapping ဖြင့် deduplicate လုပ်ထားသော canonical nodes နှင့် edges များကို output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Multi-Hop Graph Traversal Engine (1-Hop & 2-Hop BFS)

သတ်မှတ်ထားသော seed entity node တစ်ခုမှစတင်၍ 1-hop နှင့် 2-hop အကွာအဝေးရှိ neighboring nodes နှင့် connecting relationships များကို Breadth-First Search (BFS) algorithm ဖြင့် traverse လုပ်ကာ factual subgraphs များကို ထုတ်ယူပါ။

**Hints:** Cypher query `MATCH (s:Entity {name: $seed})-[r1]->(n1)-[r2]->(n2) RETURN s, r1, n1, r2, n2` ၏ programmatic graph traversal logic ဖြစ်သည်။ Visited set ထားရှိခြင်းဖြင့် cycle loops (A -> B -> A) များကို ကာကွယ်ပါ။

**Expected behavior:** Seed node မှ 1-hop neighbors နှင့် 2-hop connected dependencies များကို sequence အတိုင်း path string များ (ဥပမာ `VPC --DEPLOYED_IN--> AWS_Region --MANAGED_BY--> InfraTeam`) အဖြစ် output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — Dual-Lane Hybrid Retrieval (Vector Chunks + Graph Triples Fusion)

User query တစ်ခုအတွက် (Lane 1) Dense cosine vector similarity ဖြင့် top-k text chunks ကို retrieve လုပ်ပြီး (Lane 2) Query entities များအပေါ် အခြေခံ၍ Neo4j subgraph triples များကို retrieve လုပ်ကာ contextual prompt string အဖြစ် synthesize ပြုလုပ်သည့် hybrid retrieval engine ကို တည်ဆောက်ပါ။

**Hints:** Retrieval context တွင် unstructured narrative text သာမက explicit relational facts (`[Knowledge Graph Triples]`) ပါဝင်လာသဖြင့် LLM သည် multi-hop reasoning မေးခွန်းများကို hallucination ကင်းစင်စွာ ဖြေဆိုနိုင်သည်။

**Expected behavior:** Vector score ranked passages နှင့် graph relational triples နှစ်ခုလုံး ပါဝင်သော unified context dictionary ကို generate လုပ်ပေးနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၅ — Text-to-Cypher Translation Guardrails & Validation

Natural language questions များကို Cypher queries အဖြစ် translate လုပ်ရာတွင် SQL/Cypher injection မဖြစ်စေရန်နှင့် invalid labels/relationships များ မပါဝင်စေရန် schema-constrained syntax validation engine ကို implement လုပ်ပါ။

**Hints:** Allowed node labels set နှင့် allowed relationship types set များကို whitelist အဖြစ် သတ်မှတ်ပါ။ Whitelist ပြင်ပမှ keywords များ သို့မဟုတ် destructive clauses (`DELETE`, `DROP`, `REMOVE`) ပါဝင်ပါက query execution ကို reject လုပ်ပါ။

**Expected behavior:** Valid read queries (`MATCH ... RETURN ...`) များကို parse လုပ်၍ allowlist စစ်ဆေးအတည်ပြုနိုင်ပြီး injection / destructive attempts များကို detect လုပ်ကာ block နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၆ — Graph Community Clustering & Global Summarization (Hierarchical GraphRAG)

Graph adjacency matrix အပေါ် အခြေခံ၍ connected components သို့မဟုတ် modularity-based community clustering ကို တွက်ချက်ပြီး dense entity clusters တစ်ခုချင်းစီအတွက် high-level thematic summaries များကို synthesize ပြုလုပ်ပါ။

**Hints:** Microsoft GraphRAG architecture (arXiv:2404.16130) တွင် entity communities များကို pre-generate ပြုလုပ်ထားပြီး "What are the main architectural themes across the entire infrastructure?" ကဲ့သို့သော global holistic queries များအတွက် community summaries များကို aggregate လုပ်၍ ဖြေဆိုသည်။

**Expected behavior:** Graph nodes များကို distinct clusters/communities အဖြစ် partition ခွဲခြားနိုင်ပြီး cluster တစ်ခုချင်းစီ၏ entity members များနှင့် thematic cluster title ကို output ထုတ်နိုင်ရမည်။

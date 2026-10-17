# M14 — Knowledge Graph RAG (GraphRAG) with Neo4j

Unstructured text chunk များအပေါ် အခြေခံသော vector search ၏ multi-hop reasoning အားနည်းချက်များကို ကျော်လွှားရန် Knowledge Graph (Entities, Relationships, Triples) နှင့် Vector Search ကို ပေါင်းစပ်တည်ဆောက်သော GraphRAG architecture ကို လေ့လာသည့် module ဖြစ်သည်။

## သင်ယူလေ့လာမည့် အကြောင်းအရာများ

- Property Graph Model (Nodes, Labels, Relationships, Properties) နှင့် Cypher query language fundamentals
- Unstructured text မှ Subject-Predicate-Object (SPO) triples extraction နှင့် entity resolution/normalization
- 1-hop နှင့် 2-hop graph neighborhood traversal ဖြင့် multi-hop factual reasoning ပြုလုပ်ခြင်း
- Hybrid Graph + Vector Search architecture (Dual-lane retrieval fan-out နှင့် context fusion)
- Text-to-Cypher translation vs Vector-to-Graph semantic neighborhood traversal
- Community detection algorithms (Hierarchical GraphRAG) ဖြင့် global corpus summarization ပြုလုပ်ခြင်း

## Module အစိတ်အပိုင်းများ

| File | အကြောင်းအရာ |
|---|---|
| `README.md` | Module scope နှင့် learning objectives |
| `explanation.md` | Subtopic ၆ ခု၏ သဘောတရားရှင်းလင်းချက်၊ Cypher pattern နှင့် deterministic code example |
| `exercise.md` | ကိုယ်တိုင် implement လုပ်ရမည့် လေ့ကျင့်ခန်း ၆ ခု |
| `solution.md` | Reference implementation နှင့် ရှင်းလင်းချက် |
| `lab.py` | Standard library သာ သုံး၍ local တွင် ချက်ချင်း run နိုင်သော executable lab |

### `explanation.md` — Subtopic ဖွဲ့စည်းပုံ

1. Property Graph Model နှင့် Cypher Language Fundamentals
2. Unstructured Text မှ Triples Extraction နှင့် Entity Resolution
3. Multi-Hop Graph Traversal Engine (1-Hop & 2-Hop Reasoning)
4. Dual-Lane Hybrid Retrieval (Dense Vector + Graph Triples Fusion)
5. Text-to-Cypher vs Vector-to-Graph
6. Graph Community Detection နှင့် Global Summarization (Hierarchical GraphRAG)

## Prerequisites

- Modules M00 (Architecture), M02 (Chunking), M05 (pgvector), M06 (Hybrid Search)
- Python 3 standard library
- Graph database fundamentals (Neo4j / Property Graph concepts)
- External database မလိုအပ်ပါ — Graph data structures, traversal algorithms, Cypher generator နှင့် RRF fusion များကို deterministic pure Python ဖြင့် programmatic simulation ပြုလုပ်ထားသည်။ (Optional: Docker ဖြင့် Neo4j container ထောင်၍ စမ်းသပ်နိုင်သည်)

## Production Use Cases

- Entity dependency အလွန်များပြားသော Cloud Infrastructure / DevOps architecture Q&A
- Legal contracts, compliance frameworks နှင့် biomedical literature များတွင် multi-hop deduction ပြုလုပ်ခြင်း
- Vector similarity ဖြင့် fragment ဖြစ်သွားသော global themes များကို community summary ဖြင့် ဖြေကြားခြင်း

## References

- Neo4j Official Documentation: https://neo4j.com/docs/
- Cypher Query Language Reference: https://neo4j.com/docs/cypher-manual/current/
- Microsoft GraphRAG Paper & Architecture: https://arxiv.org/abs/2404.16130
- LangChain / LlamaIndex Neo4j GraphRAG integration guides

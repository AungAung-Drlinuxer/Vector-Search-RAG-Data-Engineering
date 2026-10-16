## လေ့ကျင့်ခန်း ၁ — Pre-Embedding PII Redaction Pipeline

Text corpus အတွင်း ပါဝင်နိုင်သော Personally Identifiable Information (PII — email addresses, phone numbers) များကို regex patterns အသုံးပြု၍ detect လုပ်ပြီး vector embedding generation မပြုလုပ်မီ `[REDACTED]` ဖြင့် sanitize ပြုလုပ်ပါ။

**Hints:** Standard library `re.sub()` ကို အသုံးပြုပါ။ Ingestion stage တွင် pre-embedding redaction မပြုလုပ်ပါက sensitive PII သည် high-dimensional vector space အတွင်း persist ဖြစ်ကျန်ခဲ့ပြီး inversion attacks သို့မဟုတ် unauthorized retrieval မှတစ်ဆင့် ပေါက်ကြားနိုင်သည်။

**Expected behavior:** Input text မှ email နှင့် phone patterns များကို sanitize လုပ်ပြီး redacted text နှင့် detection audit trail ကို output ထုတ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — In-Query Document-Level ACL Enforcement

Cosine similarity ranking logic တွင် user authorization context (`allowed_doc_ids`) ကို ပေါင်းစပ်၍ unauthorized documents များကို retrieval candidate pool မှ drop လုပ်သည့် authorization gate ကို implement လုပ်ပါ။

**Hints:** Unauthorized document သည် query နှင့် mathematical similarity အမြင့်ဆုံး ဖြစ်နေသည့်တိုင် filtered candidate list တွင် လုံးဝမပါဝင်စေရပါ။

**Expected behavior:** Unfiltered ranking နှင့် ACL-enforced ranking နှစ်ခုလုံးကို output ထုတ်ပြီး permission boundary ချိုးဖောက်သော documents များ မပါဝင်ကြောင်း အတည်ပြုနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၃ — PostgreSQL Row-Level Security (RLS) DDL & Policy Design

PostgreSQL + pgvector environment အတွက် document ownership ကို enforce လုပ်မည့် Row-Level Security policy နှင့် cosine distance query DDL statements များကို ရေးသားပါ။

**Hints:** PostgreSQL official documentation (https://www.postgresql.org/docs/current/ddl-rowsecurity.html) ကို ကိုးကားပါ။ `ALTER TABLE documents ENABLE ROW LEVEL SECURITY;` နှင့် `CREATE POLICY ... USING (owner = current_user);` syntax ကို အသုံးပြုပါ။

**Expected behavior:** Valid PostgreSQL + pgvector DDL, RLS policy နှင့် cosine distance (`<=>`) SELECT query statement များကို clean formatted strings အဖြစ် ထုတ်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — Multi-Tenant Isolation Architecture နှိုင်းယှဉ်ချက်

Multi-tenant SaaS application များတွင် အသုံးပြုသော isolation models နှစ်ခု (schema-per-tenant physical isolation vs shared-table with tenant_id filter) ၏ implementation mechanics နှင့် cross-tenant leakage vulnerability ကို သရုပ်ပြပါ။

**Hints:** Shared-table model တွင် application layer filter ပျက်ကွက်ပါက (forgotten WHERE clause) tenant data leakage ဖြစ်ပေါ်ပုံကို simulate လုပ်ပြပါ။

**Expected behavior:** Model နှစ်ခုလုံး၏ query execution results များကို နှိုင်းယှဉ်ပြသပြီး leak scenario ကို explicit test case ဖြင့် သက်သေပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၅ — Append-Only Structured Audit Logging

Retrieval API requests များ (user, query text, returned document IDs, authorization result flag, deterministic ISO-8601 timestamp) ကို JSON-Lines format ဖြင့် မှတ်တမ်းတင်သော immutable audit logger ကို တည်ဆောက်ပါ။

**Hints:** Production compliance အရ audit logs များသည် append-only ဖြစ်ရမည်ဖြစ်ပြီး authorized requests သာမက permission denied ဖြစ်ရပ်များကိုပါ audit trail တွင် မှတ်တမ်းတင်ရမည်။

**Expected behavior:** Validated JSON-Lines strings များကို generate လုပ်ပြီး access grant နှင့် denial events နှစ်မျိုးလုံး ပါဝင်ရမည်။

---

## လေ့ကျင့်ခန်း ၆ — Cascade Deletion Engine နှင့် Data Provenance Tracking

Source document ဖျက်သိမ်းမှု request ရောက်ရှိလာချိန်တွင် ၎င်းနှင့် ဆက်နွှယ်နေသော downstream chunks, embedding vectors နှင့် audit references များကို cascade purge ပြုလုပ်ပြီး compliance retention အတွက် source URL နှင့် license provenance ကို deletion metadata အဖြစ် ထိန်းသိမ်းပါ။

**Hints:** Source document ဖျက်သိမ်းပြီးနောက် orphan chunks သို့မဟုတ် orphan embeddings ကျန်ရှိနေပါက GDPR compliance ချိုးဖောက်မှု ဖြစ်ပေါ်နိုင်သည်။

**Expected behavior:** Cascade delete ပြီးနောက် orphan chunks စာရင်းသည် empty ဖြစ်ရမည်ဖြစ်ပြီး deletion log တွင် provenance metadata အပြည့်အစုံ ကျန်ရှိနေရမည်။

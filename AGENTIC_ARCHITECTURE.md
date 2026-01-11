# Agentic Search Architecture

## Overview

This document explains the architectural differences between **Simple RAG Mode** and **Agentic Search Mode**.

---

## Simple RAG Mode

**Flow:**
```
User Query → RAG Engine.generate_answer() → Answer
```

**What it does:**
1. Takes user query directly
2. Calls `rag_engine.generate_answer(query)` 
3. This internally does:
   - Vector retrieval (semantic search)
   - LLM generation with retrieved context
4. Returns answer directly

**Response Format:**
```json
{
  "mode": "rag",
  "answer": "...",
  "sources": ["file1.pdf", "file2.pdf"],
  "context": ["chunk1", "chunk2", ...]
}
```

**Key Characteristics:**
- Direct retrieval + generation in one step
- No planning or reasoning
- No tool selection
- No post-processing beyond LLM generation

---

## Agentic Search Mode

**Flow:**
```
User Query 
  → Intent Detection 
  → Planning (Strategy, Queries, Tools)
  → Tool Selection (RAG retrieval)
  → Execution (rag_engine.query() as tool)
  → Post-processing (Combine, Validate, Format)
  → Final Answer with Evidence
```

**What it does:**
1. **Intent Detection**: Analyzes query to determine intent (lookup, compare, summarize, analyze)
2. **Planning**: Creates execution plan with:
   - Search strategy
   - Decomposed queries (for comparisons)
   - Required tools
   - Post-processing method
3. **Tool Selection**: Decides if RAG retrieval is needed (and which queries to search)
4. **Execution**: Uses `rag_engine.query()` directly (not `generate_answer()`) to get raw retrieval results
5. **Post-processing**: 
   - Combines results (for comparisons)
   - Formats evidence
   - Generates structured answer with custom prompts
6. **Evidence Gathering**: Extracts document excerpts and sources

**Response Format:**
```json
{
  "mode": "agentic",
  "intent": "compare",
  "agent_plan": {
    "strategy": "Split query into components, retrieve relevant sections for each, then synthesize comparison",
    "search_queries": ["refund policy", "cancellation policy"],
    "tools_used": ["rag_retrieval"],
    "post_processing_method": "combine_and_compare"
  },
  "actions_taken": [
    "Detected intent: compare",
    "Created execution plan: ...",
    "Selected RAG retrieval tool",
    "Executing RAG retrieval for: 'refund policy'",
    "Retrieved 5 relevant chunks",
    "Starting post-processing: combine_and_compare"
  ],
  "answer": "...",
  "evidence": [
    {
      "source": "refund_policy.pdf",
      "excerpt": "Refunds must be requested within 30 days..."
    }
  ],
  "sources": ["refund_policy.pdf", "cancellation_policy.pdf"],
  "confidence": 0.85
}
```

**Key Characteristics:**
- Explicit planning phase
- Tool abstraction (RAG as a tool, not direct answer generation)
- Post-processing varies by intent
- Evidence extraction and formatting
- Action tracking
- Intent-aware processing

---

## Key Architectural Differences

| Aspect | Simple RAG | Agentic Search |
|--------|-----------|----------------|
| **Orchestration** | Single function call | Multi-phase pipeline |
| **RAG Usage** | `generate_answer()` (retrieval + generation) | `query()` (retrieval only, used as tool) |
| **Planning** | None | Explicit planning phase |
| **Intent Awareness** | None | Intent detection and routing |
| **Post-processing** | LLM generation only | Intent-specific post-processing |
| **Evidence** | Raw sources list | Structured evidence with excerpts |
| **Transparency** | Opaque | Full action tracking |
| **Response Structure** | Simple (answer, sources) | Rich (plan, actions, evidence, confidence) |

---

## Code Flow Comparison

### Simple RAG
```python
# backend/app/controllers/search_controller.py
def handle_search(query, mode="rag", rag_engine):
    if mode == "rag":
        result = rag_engine.generate_answer(query)  # Direct call
        return {"mode": "rag", "answer": result["answer"], ...}
```

### Agentic Search
```python
# backend/app/services/agentic_search.py
def agentic_search(query, rag_engine):
    # STEP 1: Intent Detection
    intent = detect_intent(query)
    
    # STEP 2: Planning
    plan = create_plan(intent, query)
    
    # STEP 3: Tool Selection & Execution
    retrieval_results = []
    for search_query in plan["search_queries"]:
        result = rag_engine.query(search_query)  # Tool invocation
        retrieval_results.append(result)
    
    # STEP 4: Post-processing (varies by intent)
    if intent == "compare":
        processed = post_process_compare(retrieval_results, plan, rag_engine)
    elif intent == "summarize":
        processed = post_process_summarize(retrieval_results, plan, rag_engine)
    # ... etc
    
    # STEP 5: Build structured response
    return {
        "mode": "agentic",
        "intent": intent,
        "agent_plan": plan,
        "actions_taken": actions_taken,
        "answer": processed["answer"],
        "evidence": processed["evidence"],
        "confidence": processed["confidence"]
    }
```

---

## Why This Matters

**For Interviews/Demos:**
1. **Clear Architecture**: Shows understanding of agentic systems vs simple RAG
2. **Tool Abstraction**: RAG is treated as a tool, not the entire system
3. **Planning & Reasoning**: Demonstrates multi-step reasoning
4. **Transparency**: Full action tracking shows how decisions are made
5. **Extensibility**: Easy to add new intents, tools, or post-processing methods

**Key Insight:**
- Simple RAG: "Get me an answer" → Direct retrieval + generation
- Agentic Search: "What do I need to do? → Plan → Execute tools → Process results → Answer"

The agentic approach adds **orchestration, planning, and post-processing layers** on top of the RAG tool, making it fundamentally different from direct RAG calls.


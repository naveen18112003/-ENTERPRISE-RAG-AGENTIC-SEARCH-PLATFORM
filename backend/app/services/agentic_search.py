"""
True Agentic Search Service

This module implements a genuine agentic pipeline with:
- Intent Detection (lookup, compare, summarize, analyze)
- Planning (search strategy, query decomposition)
- Tool Selection (decide if RAG retrieval is needed)
- Execution (use RAG as a tool, not direct answer generation)
- Post-processing (combine, validate, format responses)
"""

from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path to import RAG engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.rag_engine import RagEngine


def detect_intent(query: str) -> str:
    """
    Enhanced intent detection using keyword and pattern analysis.
    
    Args:
        query: User query string
        
    Returns:
        Intent type: "lookup", "compare", "summarize", or "analyze"
    """
    query_lower = query.lower().strip()
    
    # Comparison intent
    comparison_patterns = ["compare", "comparison", "difference", "differences", 
                          "vs", "versus", "versus", "contrast", "different"]
    if any(pattern in query_lower for pattern in comparison_patterns):
        return "compare"
    
    # Check for "and" with multiple concepts (comparison)
    if " and " in query_lower:
        parts = [p.strip() for p in query_lower.split(" and ")]
        if len(parts) >= 2 and all(len(p) > 3 for p in parts):
            # Check if it's not just a conjunction in a sentence
            if not any(p in ["policy", "policies", "document", "documents"] for p in parts):
                return "compare"
    
    # Summarize intent
    summarize_patterns = ["summarize", "summary", "overview", "brief", "what are", "list all"]
    if any(pattern in query_lower for pattern in summarize_patterns):
        return "summarize"
    
    # Analyze intent
    analyze_patterns = ["analyze", "analysis", "explain", "how does", "why", "what is the impact"]
    if any(pattern in query_lower for pattern in analyze_patterns):
        return "analyze"
    
    # Default to lookup
    return "lookup"


def create_plan(intent: str, query: str) -> Dict:
    """
    Create an execution plan based on intent and query.
    
    Args:
        intent: Detected intent
        query: User query string
        
    Returns:
        Dictionary with plan details
    """
    plan = {
        "intent": intent,
        "strategy": "",
        "search_queries": [],
        "tools_needed": [],
        "post_processing": ""
    }
    
    if intent == "compare":
        # Decompose comparison query
        query_clean = query.lower().replace("compare", "").replace("comparison", "").strip()
        if " and " in query_clean:
            parts = [p.strip() for p in query_clean.split(" and ")]
            parts = [p for p in parts if p and len(p) > 2]
            plan["search_queries"] = parts if len(parts) >= 2 else [query]
        else:
            plan["search_queries"] = [query]
        
        plan["strategy"] = "Split query into components, retrieve relevant sections for each, then synthesize comparison"
        plan["tools_needed"] = ["rag_retrieval"]
        plan["post_processing"] = "combine_and_compare"
        
    elif intent == "summarize":
        plan["search_queries"] = [query]
        plan["strategy"] = "Retrieve relevant sections, then generate comprehensive summary"
        plan["tools_needed"] = ["rag_retrieval"]
        plan["post_processing"] = "summarize"
        
    elif intent == "analyze":
        plan["search_queries"] = [query]
        plan["strategy"] = "Retrieve relevant context, then perform detailed analysis"
        plan["tools_needed"] = ["rag_retrieval"]
        plan["post_processing"] = "analyze"
        
    else:  # lookup
        plan["search_queries"] = [query]
        plan["strategy"] = "Direct retrieval and answer generation"
        plan["tools_needed"] = ["rag_retrieval"]
        plan["post_processing"] = "direct_answer"
    
    return plan


def execute_rag_tool(rag_engine: RagEngine, search_query: str, n_results: int = 5) -> Dict:
    """
    Use RAG as a tool - retrieve raw documents without generation.
    This is different from generate_answer() which does retrieval + LLM generation.
    
    Args:
        rag_engine: RagEngine instance
        search_query: Query to search for
        n_results: Number of results to retrieve
        
    Returns:
        Dictionary with retrieved documents, metadatas, and raw chunks
    """
    retrieval_results = rag_engine.query(search_query, n_results=n_results)
    
    documents = retrieval_results['documents'][0] if retrieval_results['documents'] else []
    metadatas = retrieval_results['metadatas'][0] if retrieval_results['metadatas'] else []
    
    return {
        "documents": documents,
        "metadatas": metadatas,
        "query": search_query,
        "count": len(documents)
    }


def post_process_lookup(retrieval_results: Dict, query: str, rag_engine: RagEngine) -> Dict:
    """
    Post-process lookup intent: Generate answer from retrieved context.
    """
    documents = retrieval_results.get("documents", [])
    metadatas = retrieval_results.get("metadatas", [])
    
    if not documents:
        return {
            "answer": "I couldn't find any relevant information in the documents.",
            "evidence": [],
            "confidence": 0.3
        }
    
    # Use RAG's LLM to generate answer (but we control the process)
    context_str = "\n\n".join([f"--- Source: {m.get('source', 'Unknown')} ---\n{d}" 
                                for d, m in zip(documents, metadatas)])
    
    system_prompt = "You are a helpful assistant. Answer the user's question based ONLY on the provided context. Be concise and accurate."
    user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"
    
    try:
        response = rag_engine.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        # Check for rate limit errors
        if "429" in error_str or "RateLimitReached" in error_str or "rate limit" in error_str.lower():
            wait_time = None
            # Try to extract wait time from error message
            import re
            wait_match = re.search(r'wait (\d+) seconds', error_str, re.IGNORECASE)
            if wait_match:
                wait_seconds = int(wait_match.group(1))
                wait_hours = wait_seconds / 3600
                wait_time = f"{wait_hours:.1f} hours"
            answer = f"⚠️ API Rate Limit Exceeded: The GitHub Models API has a free tier limit of 50 requests per 24 hours. " \
                    f"{f'Please wait {wait_time} before trying again.' if wait_time else 'Please wait approximately 24 hours before trying again.'} " \
                    f"Alternatively, you can use an OpenAI API key by setting OPENAI_API_KEY in your .env file."
        else:
            answer = f"Error generating answer: {error_str}"
    
    # Build evidence list
    evidence = [{"source": m.get('source', 'Unknown'), 
                 "excerpt": d[:200] + "..." if len(d) > 200 else d}
                for d, m in zip(documents[:3], metadatas[:3])]
    
    confidence = min(0.95, 0.6 + (len(documents) * 0.1))
    
    return {
        "answer": answer,
        "evidence": evidence,
        "confidence": round(confidence, 2)
    }


def post_process_compare(retrieval_results_list: List[Dict], plan: Dict, rag_engine: RagEngine) -> Dict:
    """
    Post-process comparison intent: Combine multiple retrieval results and generate comparison.
    """
    if not retrieval_results_list:
        return {
            "answer": "I couldn't find information to compare.",
            "evidence": [],
            "confidence": 0.3
        }
    
    # Combine all retrieved documents
    all_documents = []
    all_metadatas = []
    all_sources = set()
    
    for result in retrieval_results_list:
        all_documents.extend(result.get("documents", []))
        all_metadatas.extend(result.get("metadatas", []))
        for m in result.get("metadatas", []):
            all_sources.add(m.get('source', 'Unknown'))
    
    if not all_documents:
        return {
            "answer": "I couldn't find relevant information for comparison.",
            "evidence": [],
            "confidence": 0.3
        }
    
    # Build comparison context
    queries = plan.get("search_queries", [])
    context_parts = []
    for i, query in enumerate(queries):
        if i < len(retrieval_results_list):
            result = retrieval_results_list[i]
            docs = result.get("documents", [])[:2]  # Top 2 for each
            metas = result.get("metadatas", [])[:2]
            context_str = "\n".join([f"--- Source: {m.get('source', 'Unknown')} ---\n{d}" 
                                     for d, m in zip(docs, metas)])
            context_parts.append(f"## {query.upper()}:\n{context_str}")
    
    combined_context = "\n\n".join(context_parts)
    
    system_prompt = "You are an expert at comparing policy documents. Create a clear, structured comparison highlighting key differences and similarities."
    user_prompt = f"Compare the following information:\n\n{combined_context}\n\nProvide a structured comparison."
    
    try:
        response = rag_engine.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RateLimitReached" in error_str or "rate limit" in error_str.lower():
            import re
            wait_match = re.search(r'wait (\d+) seconds', error_str, re.IGNORECASE)
            wait_time = f"{int(wait_match.group(1)) / 3600:.1f} hours" if wait_match else "~24 hours"
            answer = f"⚠️ API Rate Limit Exceeded: Please wait {wait_time} before trying again. " \
                    f"GitHub Models free tier allows 50 requests per 24 hours."
        else:
            answer = f"Error generating comparison: {error_str}"
    
    # Build evidence
    evidence = []
    for result in retrieval_results_list[:2]:  # Top 2 queries
        for d, m in zip(result.get("documents", [])[:1], result.get("metadatas", [])[:1]):
            evidence.append({
                "source": m.get('source', 'Unknown'),
                "excerpt": d[:200] + "..." if len(d) > 200 else d
            })
    
    confidence = min(0.95, 0.7 + (len(all_sources) * 0.05))
    
    return {
        "answer": answer,
        "evidence": evidence,
        "confidence": round(confidence, 2)
    }


def post_process_summarize(retrieval_results: Dict, query: str, rag_engine: RagEngine) -> Dict:
    """
    Post-process summarize intent: Generate comprehensive summary.
    """
    documents = retrieval_results.get("documents", [])
    metadatas = retrieval_results.get("metadatas", [])
    
    if not documents:
        return {
            "answer": "I couldn't find information to summarize.",
            "evidence": [],
            "confidence": 0.3
        }
    
    context_str = "\n\n".join([f"--- Source: {m.get('source', 'Unknown')} ---\n{d}" 
                                for d, m in zip(documents, metadatas)])
    
    system_prompt = "You are an expert at summarizing policy documents. Create a comprehensive, well-structured summary."
    user_prompt = f"Summarize the following information:\n\n{context_str}\n\nProvide a clear summary."
    
    try:
        response = rag_engine.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating summary: {e}"
    
    evidence = [{"source": m.get('source', 'Unknown'), 
                 "excerpt": d[:200] + "..." if len(d) > 200 else d}
                for d, m in zip(documents[:3], metadatas[:3])]
    
    confidence = min(0.95, 0.65 + (len(documents) * 0.08))
    
    return {
        "answer": answer,
        "evidence": evidence,
        "confidence": round(confidence, 2)
    }


def post_process_analyze(retrieval_results: Dict, query: str, rag_engine: RagEngine) -> Dict:
    """
    Post-process analyze intent: Perform detailed analysis.
    """
    documents = retrieval_results.get("documents", [])
    metadatas = retrieval_results.get("metadatas", [])
    
    if not documents:
        return {
            "answer": "I couldn't find information to analyze.",
            "evidence": [],
            "confidence": 0.3
        }
    
    context_str = "\n\n".join([f"--- Source: {m.get('source', 'Unknown')} ---\n{d}" 
                                for d, m in zip(documents, metadatas)])
    
    system_prompt = "You are an expert analyst. Provide detailed analysis, explanations, and insights based on the provided context."
    user_prompt = f"Analyze the following information:\n\n{context_str}\n\nQuestion: {query}\n\nProvide a detailed analysis."
    
    try:
        response = rag_engine.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        answer = response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RateLimitReached" in error_str or "rate limit" in error_str.lower():
            import re
            wait_match = re.search(r'wait (\d+) seconds', error_str, re.IGNORECASE)
            wait_time = f"{int(wait_match.group(1)) / 3600:.1f} hours" if wait_match else "~24 hours"
            answer = f"⚠️ API Rate Limit Exceeded: Please wait {wait_time} before trying again."
        else:
            answer = f"Error generating analysis: {error_str}"
    
    evidence = [{"source": m.get('source', 'Unknown'), 
                 "excerpt": d[:200] + "..." if len(d) > 200 else d}
                for d, m in zip(documents[:3], metadatas[:3])]
    
    confidence = min(0.95, 0.7 + (len(documents) * 0.07))
    
    return {
        "answer": answer,
        "evidence": evidence,
        "confidence": round(confidence, 2)
    }


def agentic_search(query: str, rag_engine: RagEngine) -> Dict:
    """
    True agentic search pipeline: Intent → Plan → Tool Selection → Execution → Post-processing.
    
    This is fundamentally different from Simple RAG:
    - Simple RAG: Directly calls rag_engine.generate_answer() (retrieval + generation in one step)
    - Agentic: Creates plan, uses rag_engine.query() as a tool, then does own post-processing
    
    Args:
        query: User query string
        rag_engine: Initialized RagEngine instance
        
    Returns:
        Dictionary with structured agentic response including plan, actions, evidence
    """
    actions_taken = []
    
    # STEP 1: Intent Detection
    intent = detect_intent(query)
    actions_taken.append(f"Detected intent: {intent}")
    
    # STEP 2: Planning
    plan = create_plan(intent, query)
    actions_taken.append(f"Created execution plan: {plan['strategy']}")
    
    # STEP 3: Tool Selection & Execution
    # Decide if RAG tool is needed (in this case, always yes, but structure allows for other tools)
    if "rag_retrieval" in plan["tools_needed"]:
        actions_taken.append("Selected RAG retrieval tool")
        
        retrieval_results_list = []
        for search_query in plan["search_queries"]:
            actions_taken.append(f"Executing RAG retrieval for: '{search_query}'")
            result = execute_rag_tool(rag_engine, search_query, n_results=5)
            retrieval_results_list.append(result)
            actions_taken.append(f"Retrieved {result['count']} relevant chunks")
    
    # STEP 4: Post-processing (varies by intent)
    actions_taken.append(f"Starting post-processing: {plan['post_processing']}")
    
    if intent == "compare":
        if len(retrieval_results_list) > 1:
            processed = post_process_compare(retrieval_results_list, plan, rag_engine)
        else:
            processed = post_process_compare([retrieval_results_list[0]] if retrieval_results_list else [], plan, rag_engine)
    elif intent == "summarize":
        processed = post_process_summarize(retrieval_results_list[0] if retrieval_results_list else {}, query, rag_engine)
    elif intent == "analyze":
        processed = post_process_analyze(retrieval_results_list[0] if retrieval_results_list else {}, query, rag_engine)
    else:  # lookup
        processed = post_process_lookup(retrieval_results_list[0] if retrieval_results_list else {}, query, rag_engine)
    
    # STEP 5: Build final response
    # Extract sources from evidence
    sources = list(set([e.get("source", "Unknown") for e in processed.get("evidence", [])]))
    
    return {
        "mode": "agentic",
        "intent": intent,
        "agent_plan": {
            "strategy": plan["strategy"],
            "search_queries": plan["search_queries"],
            "tools_used": plan["tools_needed"],
            "post_processing_method": plan["post_processing"]
        },
        "actions_taken": actions_taken,
        "answer": processed.get("answer", ""),
        "evidence": processed.get("evidence", []),
        "sources": sources,
        "confidence": processed.get("confidence", 0.5)
    }

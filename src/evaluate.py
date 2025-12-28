from src.rag_engine import RagEngine
from src.prompts import PromptManager
from src.llm_client import LLMClient
import time

def run_evaluation():
    print("Starting Evaluation...")
    
    # Setup
    rag = RagEngine()
    prompter = PromptManager()
    
    try:
        # Note: This will fail if no key is present, which is expected behavior for the user to fix
        llm = LLMClient() 
    except ValueError as e:
        print(f"Skipping LLM generation in evaluation due to missing key: {e}")
        llm = None

    # Evaluation Dataset
    # Format: (Question, Expected Source/Keyword, Retrieval Expected (True/False))
    test_cases = [
        # Answerable
        {
            "q": "How many days do I have to return an item?",
            "expected_keyword": "30 calendar days",
            "expect_retrieval": True
        },
        {
            "q": "What is the cost of overnight delivery?",
            "expected_keyword": "$24.95",
            "expect_retrieval": True
        },
        # Partially Answerable / Inference
        {
            "q": "Can I return a gift card?",
            "expected_keyword": "cannot be returned",
            "expect_retrieval": True
        },
        # Unanswerable / Out of Scope
        {
            "q": "Do you sell dinosaurs?",
            "expected_keyword": "cannot find", # Expect the bot to say it can't find info
            "expect_retrieval": False # Might retrieve random stuff, but content should be irrelevant
        }
    ]

    print(f"\nrunning {len(test_cases)} test cases...\n")
    
    for i, test in enumerate(test_cases):
        print(f"Test #{i+1}: {test['q']}")
        
        # 1. Test Retrieval
        retrieval_start = time.time()
        results = rag.query(test['q'], n_results=3)
        retrieval_time = time.time() - retrieval_start
        
        retrieved_docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        print(f"  Retrieval Time: {retrieval_time:.4f}s")
        print(f"  Top Source: {metadatas[0]['source'] if metadatas else 'None'}")
        
        # 2. Test Generation (if LLM is available)
        if llm:
            context = prompter.build_context_string(retrieved_docs, metadatas)
            messages = prompter.get_prompt_v2(test['q'], context)
            
            print("  Generating Answer...")
            answer = llm.generate_response(messages)
            
            # Simple keyword check evaluation
            passed = test['expected_keyword'].lower() in answer.lower()
            status = "✅ PASS" if passed else "⚠️ CHECK"
            
            print(f"  Result: {status}")
            print(f"  Answer Snippet: {answer[:100]}...")
        else:
            print("  [LLM skipped]")
            
        print("-" * 40)

if __name__ == "__main__":
    run_evaluation()

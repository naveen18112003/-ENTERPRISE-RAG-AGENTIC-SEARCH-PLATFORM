import argparse
import sys
from dotenv import load_dotenv
from src.ingest import ingest_data
from src.rag_engine import RagEngine

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="RAG Policy Assistant")
    parser.add_argument("--query", type=str, help="Ask a question to the assistant")
    parser.add_argument("--ingest", action="store_true", help="Ingest data before running")
    
    args = parser.parse_args()

    # Ingest if requested
    if args.ingest:
        ingest_data()
        # If only ingest was requested and no query, exit
        if not args.query:
            return

    # Initialize RAG Engine
    rag = RagEngine()

    def process_query(user_query):
        print(f"\nThinking about: '{user_query}'...")
        
        result = rag.generate_answer(user_query)
        
        print("\n=== ASSISTANT ANSWER ===")
        print(result["answer"])
        print("\n=== Sources ===")
        for source in set(result["sources"]):
            print(f"- {source}")
        print("\n========================\n")

    if args.query:
        process_query(args.query)
    else:
        # Loop mode
        print("Welcome to Acme Corp Policy Assistant. Type 'exit' to quit.")
        while True:
            try:
                q = input("You: ")
            except EOFError:
                break
            if q.lower() in ["exit", "quit"]:
                break
            if not q.strip():
                continue
            process_query(q)

if __name__ == "__main__":
    main()
